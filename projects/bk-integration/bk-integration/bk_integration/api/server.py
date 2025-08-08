"""FastAPI server for BK-Integration external API access."""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import json

from ..workflows.battery_test import BatteryTestOrchestrator, TestPhase

logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class HealthResponse(BaseModel):
    """API health check response."""
    success: bool = True
    message: str = "BK-Integration API is running"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)


class DeviceStatusResponse(BaseModel):
    """Device status response."""
    load_connected: bool
    power_connected: bool
    load_status: Dict[str, Any]
    power_status: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class TestProfileRequest(BaseModel):
    """Battery test profile request."""
    profile: str = "default"
    cycles: int = Field(default=1, ge=1, le=10)
    export_results: bool = False


class CustomTestRequest(BaseModel):
    """Custom battery test request."""
    charge_voltage: float = Field(ge=0.0, le=60.0)
    charge_current: float = Field(ge=0.0, le=5.0)
    discharge_current: float = Field(ge=0.0, le=60.0)
    cutoff_voltage: float = Field(ge=0.0, le=120.0)
    cycles: int = Field(default=1, ge=1, le=10)
    rest_time: int = Field(default=60, ge=0, le=3600)
    taper_threshold: Optional[float] = Field(None, ge=0.01, le=5.0)
    taper_duration: Optional[int] = Field(None, ge=1, le=3600)


class DeviceControlRequest(BaseModel):
    """Device control request."""
    voltage: Optional[float] = None
    current: Optional[float] = None
    enabled: Optional[bool] = None


class TestStatusResponse(BaseModel):
    """Test status response."""
    test_active: bool
    phase: str
    test_id: Optional[str] = None
    cycles_completed: int = 0
    total_cycles: int = 1
    elapsed_time: float = 0
    current_capacity_ah: float = 0
    current_energy_wh: float = 0
    efficiency_percent: float = 0
    timestamp: datetime = Field(default_factory=datetime.now)


class WebSocketManager:
    """WebSocket connection manager for real-time monitoring."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected, total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected, total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


def create_app(config=None, load_client=None, power_client=None, safety_monitor=None) -> FastAPI:
    """Create FastAPI application with dependency injection.
    
    Args:
        config: Configuration manager
        load_client: BK8520 client
        power_client: BK9206b client
        safety_monitor: Safety monitor
        
    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="BK-Integration API",
        description="REST API for unified control of BK8520 and BK9206b devices",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # WebSocket manager
    websocket_manager = WebSocketManager()
    
    # Global state
    current_orchestrator: Optional[BatteryTestOrchestrator] = None
    
    # Dependency functions
    def get_config():
        if not config:
            raise HTTPException(status_code=503, detail="Configuration not available")
        return config
    
    def get_load_client():
        if not load_client:
            raise HTTPException(status_code=503, detail="BK8520 client not available")
        return load_client
    
    def get_power_client():
        if not power_client:
            raise HTTPException(status_code=503, detail="BK9206b client not available")
        return power_client
    
    def get_safety_monitor():
        if not safety_monitor:
            raise HTTPException(status_code=503, detail="Safety monitor not available")
        return safety_monitor
    
    # HTML interface
    @app.get("/", response_class=HTMLResponse)
    async def get_web_interface():
        """Simple web interface for API testing."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>BK-Integration API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .endpoint { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
                .method { font-weight: bold; color: #007acc; }
                .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
                .success { background-color: #d4edda; color: #155724; }
                .error { background-color: #f8d7da; color: #721c24; }
                button { margin: 5px; padding: 8px 15px; cursor: pointer; }
                #output { background: #f8f9fa; padding: 10px; margin: 10px 0; min-height: 200px; }
            </style>
        </head>
        <body>
            <h1>BK-Integration API Interface</h1>
            <p>Interactive testing interface for BK-Integration REST API</p>
            
            <div class="endpoint">
                <div class="method">GET /api/health</div>
                <button onclick="testEndpoint('/api/health')">Test Health</button>
            </div>
            
            <div class="endpoint">
                <div class="method">GET /api/devices/status</div>
                <button onclick="testEndpoint('/api/devices/status')">Test Device Status</button>
            </div>
            
            <div class="endpoint">
                <div class="method">POST /api/devices/connect</div>
                <button onclick="testEndpoint('/api/devices/connect', 'POST')">Test Connect</button>
            </div>
            
            <div class="endpoint">
                <div class="method">GET /api/test/status</div>
                <button onclick="testEndpoint('/api/test/status')">Test Status</button>
            </div>
            
            <div class="endpoint">
                <div class="method">WebSocket /ws/monitor</div>
                <button onclick="connectWebSocket()">Connect WebSocket</button>
                <button onclick="disconnectWebSocket()">Disconnect</button>
            </div>
            
            <h3>Output:</h3>
            <div id="output"></div>
            
            <script>
                let ws = null;
                
                async function testEndpoint(url, method = 'GET') {
                    const output = document.getElementById('output');
                    try {
                        const response = await fetch(url, { method: method });
                        const data = await response.json();
                        output.innerHTML += `<div class="success">${method} ${url}: ${JSON.stringify(data, null, 2)}</div>`;
                    } catch (error) {
                        output.innerHTML += `<div class="error">${method} ${url}: ${error.message}</div>`;
                    }
                }
                
                function connectWebSocket() {
                    const output = document.getElementById('output');
                    ws = new WebSocket(`ws://${window.location.host}/ws/monitor`);
                    
                    ws.onopen = function() {
                        output.innerHTML += '<div class="success">WebSocket connected</div>';
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        output.innerHTML += `<div>WS: ${JSON.stringify(data, null, 2)}</div>`;
                    };
                    
                    ws.onclose = function() {
                        output.innerHTML += '<div class="error">WebSocket disconnected</div>';
                    };
                }
                
                function disconnectWebSocket() {
                    if (ws) {
                        ws.close();
                        ws = null;
                    }
                }
            </script>
        </body>
        </html>
        """
        return html_content
    
    # API endpoints
    @app.get("/api/health", response_model=HealthResponse)
    async def health_check():
        """API health check endpoint."""
        return HealthResponse()
    
    @app.get("/api/devices/status", response_model=DeviceStatusResponse)
    async def get_devices_status(
        load_client=Depends(get_load_client),
        power_client=Depends(get_power_client)
    ):
        """Get status of both devices."""
        try:
            load_status = load_client.get_status()
            power_status = power_client.get_status()
            
            return DeviceStatusResponse(
                load_connected=load_status.get('success', False) and 
                              load_status.get('data', {}).get('connected', False),
                power_connected=isinstance(power_status, dict),
                load_status=load_status,
                power_status=power_status
            )
        except Exception as e:
            logger.error(f"Error getting device status: {e}")
            raise HTTPException(status_code=500, detail=f"Device status error: {e}")
    
    @app.post("/api/devices/connect")
    async def connect_devices(
        load_client=Depends(get_load_client),
        power_client=Depends(get_power_client),
        config=Depends(get_config)
    ):
        """Connect to both devices."""
        try:
            # Connect BK8520
            load_config = config.get_load_config()
            load_result = load_client.connect(
                port=load_config.get('serial_port', '/dev/ttyUSB0')
            )
            
            # Check BK9206b
            power_result = power_client.health_check()
            
            success = load_result.get('success', False) and (
                power_result.get('success', False) or 
                power_result.get('server_status') == 'healthy'
            )
            
            return {
                "success": success,
                "message": "Device connection completed",
                "load_result": load_result,
                "power_result": power_result,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error connecting devices: {e}")
            raise HTTPException(status_code=500, detail=f"Connection error: {e}")
    
    @app.post("/api/test/battery")
    async def start_battery_test(
        request: TestProfileRequest,
        config=Depends(get_config),
        load_client=Depends(get_load_client),
        power_client=Depends(get_power_client),
        safety_monitor=Depends(get_safety_monitor)
    ):
        """Start battery test with specified profile."""
        nonlocal current_orchestrator
        
        # Check if test is already running
        if current_orchestrator and current_orchestrator.test_active:
            raise HTTPException(status_code=409, detail="Test already running")
        
        try:
            # Get test profile
            test_profile = config.get_test_profile(request.profile)
            
            # Validate profile
            if not config.validate_test_profile(test_profile):
                raise HTTPException(status_code=400, detail="Invalid test profile")
            
            # Create orchestrator
            current_orchestrator = BatteryTestOrchestrator(
                power_client, load_client, safety_monitor
            )
            
            # Start test in background task
            async def run_test():
                try:
                    results = current_orchestrator.run_battery_test(test_profile, request.cycles)
                    
                    # Broadcast completion
                    await websocket_manager.broadcast(json.dumps({
                        "type": "test_complete",
                        "data": results.to_dict(),
                        "timestamp": datetime.now().isoformat()
                    }))
                    
                    # Export results if requested
                    if request.export_results:
                        filename = f"battery_test_{results.test_id}.json"
                        current_orchestrator.export_results(filename, 'json')
                    
                except Exception as e:
                    logger.error(f"Background test failed: {e}")
                    await websocket_manager.broadcast(json.dumps({
                        "type": "test_error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }))
            
            # Schedule background task
            asyncio.create_task(run_test())
            
            return {
                "success": True,
                "message": "Battery test started",
                "test_id": current_orchestrator.current_results.test_id,
                "profile": request.profile,
                "cycles": request.cycles,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error starting battery test: {e}")
            raise HTTPException(status_code=500, detail=f"Test start error: {e}")
    
    @app.post("/api/test/battery/custom")
    async def start_custom_battery_test(
        request: CustomTestRequest,
        load_client=Depends(get_load_client),
        power_client=Depends(get_power_client),
        safety_monitor=Depends(get_safety_monitor),
        config=Depends(get_config)
    ):
        """Start battery test with custom parameters."""
        nonlocal current_orchestrator
        
        # Check if test is already running
        if current_orchestrator and current_orchestrator.test_active:
            raise HTTPException(status_code=409, detail="Test already running")
        
        try:
            # Create custom profile
            custom_profile = {
                'name': 'custom',
                'description': f'Custom test: {request.charge_voltage}V @ {request.charge_current}A',
                'charge_voltage': request.charge_voltage,
                'charge_current': request.charge_current,
                'discharge_current': request.discharge_current,
                'cutoff_voltage': request.cutoff_voltage,
                'rest_time': request.rest_time,
                'taper_threshold': request.taper_threshold or 0.1,
                'taper_duration': request.taper_duration or 60
            }
            
            # Validate custom profile
            if not config.validate_test_profile(custom_profile):
                raise HTTPException(status_code=400, detail="Invalid custom test parameters")
            
            # Create orchestrator and start test
            current_orchestrator = BatteryTestOrchestrator(
                power_client, load_client, safety_monitor
            )
            
            # Background task for test execution
            async def run_custom_test():
                try:
                    results = current_orchestrator.run_battery_test(custom_profile, request.cycles)
                    await websocket_manager.broadcast(json.dumps({
                        "type": "test_complete",
                        "data": results.to_dict(),
                        "timestamp": datetime.now().isoformat()
                    }))
                except Exception as e:
                    logger.error(f"Custom test failed: {e}")
                    await websocket_manager.broadcast(json.dumps({
                        "type": "test_error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }))
            
            asyncio.create_task(run_custom_test())
            
            return {
                "success": True,
                "message": "Custom battery test started",
                "test_id": current_orchestrator.current_results.test_id,
                "parameters": custom_profile,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error starting custom test: {e}")
            raise HTTPException(status_code=500, detail=f"Custom test error: {e}")
    
    @app.post("/api/test/stop")
    async def stop_battery_test():
        """Stop currently running battery test."""
        nonlocal current_orchestrator
        
        if not current_orchestrator or not current_orchestrator.test_active:
            raise HTTPException(status_code=404, detail="No active test to stop")
        
        try:
            current_orchestrator.emergency_stop()
            
            # Broadcast stop event
            await websocket_manager.broadcast(json.dumps({
                "type": "test_stopped",
                "timestamp": datetime.now().isoformat()
            }))
            
            return {
                "success": True,
                "message": "Battery test stopped",
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error stopping test: {e}")
            raise HTTPException(status_code=500, detail=f"Test stop error: {e}")
    
    @app.get("/api/test/status", response_model=TestStatusResponse)
    async def get_test_status():
        """Get current battery test status."""
        if not current_orchestrator:
            return TestStatusResponse(test_active=False, phase=TestPhase.IDLE.value)
        
        status = current_orchestrator.get_current_status()
        return TestStatusResponse(**status)
    
    @app.get("/api/test/results")
    async def get_test_results(test_id: Optional[str] = None):
        """Get battery test results."""
        if not current_orchestrator or not current_orchestrator.current_results:
            raise HTTPException(status_code=404, detail="No test results available")
        
        results = current_orchestrator.current_results
        
        # Check test_id if provided
        if test_id and results.test_id != test_id:
            raise HTTPException(status_code=404, detail=f"Test ID {test_id} not found")
        
        return {
            "success": True,
            "results": results.to_dict(),
            "timestamp": datetime.now()
        }
    
    @app.post("/api/power/voltage")
    async def set_power_voltage(
        request: DeviceControlRequest,
        power_client=Depends(get_power_client)
    ):
        """Set power supply voltage."""
        if request.voltage is None:
            raise HTTPException(status_code=400, detail="Voltage parameter required")
        
        try:
            result = power_client.set_voltage(request.voltage)
            if not result.get('success'):
                raise HTTPException(status_code=400, detail=result.get('message'))
            
            return result
        except Exception as e:
            logger.error(f"Error setting voltage: {e}")
            raise HTTPException(status_code=500, detail=f"Voltage control error: {e}")
    
    @app.post("/api/power/current")
    async def set_power_current(
        request: DeviceControlRequest,
        power_client=Depends(get_power_client)
    ):
        """Set power supply current limit."""
        if request.current is None:
            raise HTTPException(status_code=400, detail="Current parameter required")
        
        try:
            result = power_client.set_current(request.current)
            if not result.get('success'):
                raise HTTPException(status_code=400, detail=result.get('message'))
            
            return result
        except Exception as e:
            logger.error(f"Error setting current: {e}")
            raise HTTPException(status_code=500, detail=f"Current control error: {e}")
    
    @app.post("/api/power/output/{action}")
    async def control_power_output(
        action: str,
        power_client=Depends(get_power_client)
    ):
        """Enable or disable power supply output."""
        if action not in ['enable', 'disable']:
            raise HTTPException(status_code=400, detail="Action must be 'enable' or 'disable'")
        
        try:
            if action == 'enable':
                result = power_client.enable_output()
            else:
                result = power_client.disable_output()
            
            if not result.get('success'):
                raise HTTPException(status_code=400, detail=result.get('message'))
            
            return result
        except Exception as e:
            logger.error(f"Error controlling output: {e}")
            raise HTTPException(status_code=500, detail=f"Output control error: {e}")
    
    @app.post("/api/load/current")
    async def set_load_current(
        request: DeviceControlRequest,
        load_client=Depends(get_load_client)
    ):
        """Set load tester discharge current."""
        if request.current is None:
            raise HTTPException(status_code=400, detail="Current parameter required")
        
        try:
            result = load_client.set_current(request.current)
            if not result.get('success'):
                raise HTTPException(status_code=400, detail=result.get('message'))
            
            return result
        except Exception as e:
            logger.error(f"Error setting load current: {e}")
            raise HTTPException(status_code=500, detail=f"Load current error: {e}")
    
    @app.post("/api/load/input/{action}")
    async def control_load_input(
        action: str,
        load_client=Depends(get_load_client)
    ):
        """Enable or disable load tester input."""
        if action not in ['enable', 'disable']:
            raise HTTPException(status_code=400, detail="Action must be 'enable' or 'disable'")
        
        try:
            if action == 'enable':
                result = load_client.enable_input()
            else:
                result = load_client.disable_input()
            
            if not result.get('success'):
                raise HTTPException(status_code=400, detail=result.get('message'))
            
            return result
        except Exception as e:
            logger.error(f"Error controlling load input: {e}")
            raise HTTPException(status_code=500, detail=f"Load input error: {e}")
    
    @app.websocket("/ws/monitor")
    async def websocket_monitor(websocket: WebSocket):
        """WebSocket endpoint for real-time device monitoring."""
        await websocket_manager.connect(websocket)
        
        try:
            while True:
                # Send periodic status updates
                if load_client and power_client:
                    try:
                        load_data = load_client.get_readings()
                        power_data = power_client.get_status()
                        
                        message = {
                            "type": "status_update",
                            "data": {
                                "load": load_data,
                                "power": power_data
                            },
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        await websocket.send_text(json.dumps(message))
                        
                    except Exception as e:
                        logger.error(f"Error in WebSocket monitoring: {e}")
                
                # Send test status if available
                if current_orchestrator:
                    test_status = current_orchestrator.get_current_status()
                    if test_status['test_active']:
                        message = {
                            "type": "test_status",
                            "data": test_status,
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send_text(json.dumps(message))
                
                # Wait before next update
                await asyncio.sleep(1.0)
                
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            websocket_manager.disconnect(websocket)
    
    return app