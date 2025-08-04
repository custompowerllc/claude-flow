#!/usr/bin/env python3
"""
Thermal Runaway Propagation Simulator - P3E Analysis Implementation

This module simulates thermal runaway propagation patterns based on P3E 
analysis data, including geographic clustering, cell-to-cell heat transfer,
and progressive failure cascades.

Based on P3E thermal analysis findings:
- Pack 0535: 65°C thermal hotspot with 1048mV electrical runaway (Cell #6)
- Geographic clustering: Thermal and electrical issues in same locations
- Cell #6 shows highest thermal correlation across multiple packs
- Thermal propagation follows physical cell layout patterns

Key Features:
1. Cell-to-cell thermal conductivity modeling
2. Heat generation from electrical resistance
3. Progressive failure cascade simulation
4. Cooling system effectiveness modeling
5. Geographic clustering validation
6. Real-time thermal map generation
"""

import sys
import os
import logging
import time
import math
import threading
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

# Import logging system
try:
    from ..utils.log_manager import get_logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False


class ThermalState(Enum):
    """Thermal states for cells"""
    NORMAL = "normal"           # <35°C
    ELEVATED = "elevated"       # 35-40°C
    HIGH = "high"               # 40-45°C
    CRITICAL = "critical"       # 45-60°C
    RUNAWAY = "runaway"         # >60°C
    CATASTROPHIC = "catastrophic"  # >80°C


class CoolingEffectiveness(Enum):
    """Cooling system effectiveness levels"""
    NONE = 0.0
    POOR = 0.3
    MODERATE = 0.6
    GOOD = 0.8
    EXCELLENT = 1.0


@dataclass
class CellThermalData:
    """Thermal data for individual cells"""
    cell_id: int
    position_x: float
    position_y: float
    temperature_c: float
    target_temp_c: float = 25.0
    heat_generation_w: float = 0.0
    heat_capacity_j_k: float = 50.0  # Joules per Kelvin
    thermal_mass_kg: float = 0.1     # kg
    surface_area_m2: float = 0.01    # m²
    thermal_conductivity: float = 200.0  # W/(m·K)
    last_updated: datetime = field(default_factory=datetime.now)
    thermal_history: List[float] = field(default_factory=list)
    runaway_probability: float = 0.0
    neighboring_cells: List[int] = field(default_factory=list)


@dataclass
class ThermalPropagationEvent:
    """Thermal propagation event data"""
    event_id: str
    timestamp: datetime
    source_cell: int
    affected_cells: List[int]
    propagation_rate_c_per_s: float
    max_temperature_c: float
    heat_generation_total_w: float
    cooling_effectiveness: float
    geographic_cluster: bool
    p3e_correlation: str
    severity_level: ThermalState
    estimated_spread_time_s: float
    mitigation_actions: List[str]


class ThermalPropagationSimulator:
    """
    Advanced thermal runaway propagation simulator based on P3E analysis
    
    Models thermal propagation using:
    1. Physical cell layout and distances
    2. Thermal conductivity between cells
    3. Heat generation from electrical resistance
    4. Environmental cooling effects
    5. P3E geographic clustering patterns
    6. Progressive cascade failure modes
    """
    
    def __init__(self, cell_count: int = 8, pack_layout: str = "linear"):
        """Initialize thermal propagation simulator"""
        # Setup logging
        if LOGGING_AVAILABLE:
            self.logger = get_logger(__name__, 'thermal_propagation')
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
        
        self.cell_count = cell_count
        self.pack_layout = pack_layout
        
        # Initialize cells with P3E layout (Cell #6 high-risk position)
        self.cells: Dict[int, CellThermalData] = {}
        self._initialize_cell_layout()
        
        # Thermal propagation parameters
        self.ambient_temp_c = 25.0
        self.cooling_effectiveness = CoolingEffectiveness.MODERATE
        self.thermal_time_constant = 30.0  # seconds
        self.heat_transfer_coefficient = 10.0  # W/(m²·K)
        
        # P3E analysis parameters
        self.p3e_hotspot_cells = [6]  # Cell #6 based on Pack 0535 analysis
        self.geographic_clustering_enabled = True
        self.runaway_threshold_c = 60.0  # Based on Pack 0535: 65°C
        
        # Simulation state
        self.simulation_active = False
        self.propagation_events: List[ThermalPropagationEvent] = []
        self.thermal_map_history: List[Dict[int, float]] = []
        
        # Statistics
        self.stats = {
            'total_events': 0,
            'runaway_events': 0,
            'cells_affected': 0,
            'max_temperature_reached': 25.0,
            'average_propagation_rate': 0.0,
            'cooling_system_activations': 0,
            'p3e_correlations': 0
        }
        
        self.logger.info(f"ThermalPropagationSimulator initialized for {cell_count} cells")
        self.logger.info(f"Layout: {pack_layout}, High-risk cells: {self.p3e_hotspot_cells}")
    
    def _initialize_cell_layout(self) -> None:
        """Initialize cell positions based on pack layout"""
        if self.pack_layout == "linear":
            # Linear arrangement (typical for P3E packs)
            spacing = 0.02  # 2cm between cells
            for i in range(1, self.cell_count + 1):
                x_pos = (i - 1) * spacing
                y_pos = 0.0
                
                self.cells[i] = CellThermalData(
                    cell_id=i,
                    position_x=x_pos,
                    position_y=y_pos,
                    temperature_c=self.ambient_temp_c
                )
        
        elif self.pack_layout == "2x4_grid":
            # 2x4 grid layout
            for i in range(1, self.cell_count + 1):
                row = (i - 1) // 4
                col = (i - 1) % 4
                x_pos = col * 0.025  # 2.5cm spacing
                y_pos = row * 0.025
                
                self.cells[i] = CellThermalData(
                    cell_id=i,
                    position_x=x_pos,
                    position_y=y_pos,
                    temperature_c=self.ambient_temp_c
                )
        
        # Calculate neighboring cells based on distance
        self._calculate_neighbors()
        
        # Set P3E-specific parameters for high-risk cells
        for cell_id in self.p3e_hotspot_cells:
            if cell_id in self.cells:
                cell = self.cells[cell_id]
                cell.thermal_conductivity *= 1.2  # Higher conductivity (defect)
                cell.runaway_probability = 0.15   # 15% higher probability
    
    def _calculate_neighbors(self) -> None:
        """Calculate neighboring cells based on physical distance"""
        max_neighbor_distance = 0.035  # 3.5cm maximum for thermal coupling
        
        for cell_id, cell in self.cells.items():
            neighbors = []
            
            for other_id, other_cell in self.cells.items():
                if cell_id != other_id:
                    distance = math.sqrt(
                        (cell.position_x - other_cell.position_x) ** 2 +
                        (cell.position_y - other_cell.position_y) ** 2
                    )
                    
                    if distance <= max_neighbor_distance:
                        neighbors.append(other_id)
            
            cell.neighboring_cells = neighbors
            self.logger.debug(f"Cell {cell_id} neighbors: {neighbors}")
    
    def start_simulation(self, time_step: float = 1.0) -> None:
        """Start thermal propagation simulation"""
        self.simulation_active = True
        self.time_step = time_step
        
        # Start simulation thread
        self._sim_thread = threading.Thread(target=self._simulation_loop)
        self._sim_thread.daemon = True
        self._sim_thread.start()
        
        self.logger.info(f"Thermal propagation simulation started (dt={time_step}s)")
    
    def stop_simulation(self) -> None:
        """Stop thermal propagation simulation"""
        self.simulation_active = False
        self.logger.info("Thermal propagation simulation stopped")
    
    def _simulation_loop(self) -> None:
        """Main simulation loop"""
        while self.simulation_active:
            try:
                # Update thermal state for all cells
                self._update_thermal_dynamics()
                
                # Check for propagation events
                self._detect_thermal_propagation()
                
                # Apply cooling effects
                self._apply_cooling_effects()
                
                # Update thermal history
                self._update_thermal_history()
                
                # Check for runaway conditions
                self._check_runaway_conditions()
                
                time.sleep(self.time_step)
                
            except Exception as e:
                self.logger.error(f"Error in thermal simulation loop: {e}")
                time.sleep(5.0)
    
    def set_cell_temperature(self, cell_id: int, temperature_c: float, 
                           heat_generation_w: float = 0.0) -> None:
        """Set cell temperature and heat generation"""
        if cell_id not in self.cells:
            self.logger.warning(f"Unknown cell ID: {cell_id}")
            return
        
        cell = self.cells[cell_id]
        cell.temperature_c = temperature_c
        cell.heat_generation_w = heat_generation_w
        cell.last_updated = datetime.now()
        
        # Update statistics
        if temperature_c > self.stats['max_temperature_reached']:
            self.stats['max_temperature_reached'] = temperature_c
        
        self.logger.debug(f"Cell {cell_id}: {temperature_c:.1f}°C, {heat_generation_w:.2f}W")
    
    def simulate_p3e_pack_0535_event(self) -> None:
        """Simulate the Pack 0535 thermal runaway event from P3E analysis"""
        self.logger.info("Simulating P3E Pack 0535 thermal runaway event")
        
        # Pack 0535: Cell #6 reached 65°C with 1048mV electrical runaway
        # Progressive heating over 3+ hour timeframe
        
        # Initial heating (start of runaway)
        self.set_cell_temperature(6, 35.0, 2.0)  # Cell #6 starts heating
        
        # Simulate progressive heating over time
        def progressive_heating():
            heating_phases = [
                (0, 35.0, 2.0),      # T+0: Initial heating
                (300, 45.0, 5.0),    # T+5min: Moderate heating
                (900, 55.0, 10.0),   # T+15min: High heating
                (1800, 65.0, 20.0),  # T+30min: Critical heating (P3E level)
                (3600, 75.0, 30.0),  # T+1hr: Catastrophic heating
            ]
            
            for delay, temp, power in heating_phases:
                threading.Timer(delay, lambda t=temp, p=power: self.set_cell_temperature(6, t, p)).start()
        
        progressive_heating()
        
        # Create propagation event
        event = ThermalPropagationEvent(
            event_id=f"P3E_0535_{int(time.time())}",
            timestamp=datetime.now(),
            source_cell=6,
            affected_cells=[6],
            propagation_rate_c_per_s=0.01,  # Gradual heating
            max_temperature_c=65.0,
            heat_generation_total_w=20.0,
            cooling_effectiveness=float(self.cooling_effectiveness.value),
            geographic_cluster=True,
            p3e_correlation="Pack 0535: Cell #6 thermal runaway with 1048mV electrical correlation",
            severity_level=ThermalState.RUNAWAY,
            estimated_spread_time_s=3600.0,
            mitigation_actions=[
                "Immediate cooling activation",
                "Electrical current reduction",
                "Enhanced cell #6 monitoring",
                "Prepare for emergency shutdown"
            ]
        )
        
        self.propagation_events.append(event)
        self.stats['p3e_correlations'] += 1
        
        self.logger.warning("P3E Pack 0535 simulation initiated - Cell #6 thermal runaway")
    
    def simulate_p3e_pack_0533_thermal_correlation(self) -> None:
        """Simulate Pack 0533 thermal correlation during discharge"""
        self.logger.info("Simulating P3E Pack 0533 thermal correlation during discharge")
        
        # Pack 0533: 305°C temperature during 702mV electrical runaway
        # Rapid escalation during -5.3A discharge
        
        # Set initial thermal state during discharge
        for cell_id in self.cells:
            base_temp = 30.5  # 305°C in P3E data (likely 30.5°C)
            self.set_cell_temperature(cell_id, base_temp, 1.0)
        
        # Cell #6 progressive failure
        def discharge_thermal_correlation():
            correlation_phases = [
                (0, 30.5, 1.0),      # Normal discharge temperature
                (960, 32.0, 3.0),    # T+16min: Start of escalation
                (1020, 35.0, 8.0),   # T+17min: Thermal rise
                (1080, 40.0, 15.0),  # T+18min: Critical thermal
            ]
            
            for delay, temp, power in correlation_phases:
                threading.Timer(delay, lambda t=temp, p=power: self.set_cell_temperature(6, t, p)).start()
        
        discharge_thermal_correlation()
        
        # Create correlation event
        event = ThermalPropagationEvent(
            event_id=f"P3E_0533_{int(time.time())}",
            timestamp=datetime.now(),
            source_cell=6,
            affected_cells=[6],
            propagation_rate_c_per_s=0.15,  # Rapid heating during discharge
            max_temperature_c=40.0,
            heat_generation_total_w=15.0,
            cooling_effectiveness=float(self.cooling_effectiveness.value),
            geographic_cluster=True,
            p3e_correlation="Pack 0533: Cell #6 thermal correlation with 702mV electrical runaway during -5.3A discharge",
            severity_level=ThermalState.HIGH,
            estimated_spread_time_s=120.0,  # 2-minute escalation
            mitigation_actions=[
                "Stop discharge immediately",
                "Activate cooling systems",
                "Monitor electrical parameters",
                "Prepare for BMS shutdown"
            ]
        )
        
        self.propagation_events.append(event)
        self.stats['p3e_correlations'] += 1
        
        self.logger.warning("P3E Pack 0533 thermal correlation initiated")
    
    def _update_thermal_dynamics(self) -> None:
        """Update thermal dynamics for all cells"""
        # Calculate heat transfer between cells
        heat_transfer_matrix = self._calculate_heat_transfer_matrix()
        
        # Update each cell's temperature
        for cell_id, cell in self.cells.items():
            # Heat generation (electrical resistance, defects)
            heat_generated = cell.heat_generation_w * self.time_step
            
            # Heat transfer from neighbors
            heat_from_neighbors = sum(heat_transfer_matrix.get((neighbor_id, cell_id), 0.0) 
                                    for neighbor_id in cell.neighboring_cells)
            
            # Heat transfer to neighbors
            heat_to_neighbors = sum(heat_transfer_matrix.get((cell_id, neighbor_id), 0.0) 
                                  for neighbor_id in cell.neighboring_cells)
            
            # Heat loss to environment
            heat_to_environment = (cell.temperature_c - self.ambient_temp_c) * \
                                cell.surface_area_m2 * self.heat_transfer_coefficient * self.time_step
            
            # Net heat change
            net_heat_j = heat_generated + heat_from_neighbors - heat_to_neighbors - heat_to_environment
            
            # Temperature change
            temp_change = net_heat_j / cell.heat_capacity_j_k
            cell.temperature_c += temp_change
            
            # Apply thermal time constant (thermal inertia)
            cell.temperature_c = cell.temperature_c * (1 - self.time_step / self.thermal_time_constant) + \
                               cell.target_temp_c * (self.time_step / self.thermal_time_constant)
            
            # Ensure physical limits
            cell.temperature_c = max(cell.temperature_c, self.ambient_temp_c)
            
            cell.last_updated = datetime.now()
    
    def _calculate_heat_transfer_matrix(self) -> Dict[Tuple[int, int], float]:
        """Calculate heat transfer between all cell pairs"""
        heat_transfer = {}
        
        for cell_id, cell in self.cells.items():
            for neighbor_id in cell.neighboring_cells:
                if neighbor_id in self.cells:
                    neighbor = self.cells[neighbor_id]
                    
                    # Distance between cells
                    distance = math.sqrt(
                        (cell.position_x - neighbor.position_x) ** 2 +
                        (cell.position_y - neighbor.position_y) ** 2
                    )
                    
                    # Temperature difference
                    temp_diff = cell.temperature_c - neighbor.temperature_c
                    
                    # Heat transfer rate (Fourier's law)
                    if distance > 0:
                        thermal_resistance = distance / (cell.thermal_conductivity * cell.surface_area_m2)
                        heat_transfer_rate = temp_diff / thermal_resistance
                        heat_transfer[(cell_id, neighbor_id)] = heat_transfer_rate * self.time_step
        
        return heat_transfer
    
    def _detect_thermal_propagation(self) -> None:
        """Detect thermal propagation events"""
        for cell_id, cell in self.cells.items():
            if cell.temperature_c > 40.0:  # Threshold for propagation concern
                
                # Check if heat is spreading to neighbors
                affected_neighbors = []
                for neighbor_id in cell.neighboring_cells:
                    neighbor = self.cells[neighbor_id]
                    if neighbor.temperature_c > self.ambient_temp_c + 5.0:  # >5°C above ambient
                        affected_neighbors.append(neighbor_id)
                
                if affected_neighbors:
                    # Calculate propagation rate
                    if len(cell.thermal_history) >= 2:
                        temp_rise_rate = (cell.thermal_history[-1] - cell.thermal_history[-2]) / self.time_step
                    else:
                        temp_rise_rate = 0.0
                    
                    # Check for geographic clustering (P3E pattern)
                    geographic_cluster = self._check_geographic_clustering([cell_id] + affected_neighbors)
                    
                    # Create propagation event
                    event = ThermalPropagationEvent(
                        event_id=f"PROP_{int(time.time())}_{cell_id}",
                        timestamp=datetime.now(),
                        source_cell=cell_id,
                        affected_cells=affected_neighbors,
                        propagation_rate_c_per_s=temp_rise_rate,
                        max_temperature_c=max(cell.temperature_c, 
                                            max([self.cells[nid].temperature_c for nid in affected_neighbors], default=0)),
                        heat_generation_total_w=cell.heat_generation_w + 
                                              sum([self.cells[nid].heat_generation_w for nid in affected_neighbors]),
                        cooling_effectiveness=float(self.cooling_effectiveness.value),
                        geographic_cluster=geographic_cluster,
                        p3e_correlation=self._get_p3e_thermal_correlation(cell_id, cell.temperature_c),
                        severity_level=self._get_thermal_state(cell.temperature_c),
                        estimated_spread_time_s=self._estimate_spread_time(temp_rise_rate, cell.temperature_c),
                        mitigation_actions=self._get_thermal_mitigation_actions(cell.temperature_c)
                    )
                    
                    # Only add if it's a new event (avoid duplicates)
                    if not any(e.source_cell == cell_id and 
                             (datetime.now() - e.timestamp).total_seconds() < 30 
                             for e in self.propagation_events[-5:]):
                        self.propagation_events.append(event)
                        self.stats['total_events'] += 1
                        self.stats['cells_affected'] = len(set([cell_id] + affected_neighbors))
                        
                        self.logger.warning(f"Thermal propagation detected: Cell {cell_id} -> {affected_neighbors}")
    
    def _check_geographic_clustering(self, cell_ids: List[int]) -> bool:
        """Check if thermal events show geographic clustering (P3E pattern)"""
        if not self.geographic_clustering_enabled or len(cell_ids) < 2:
            return False
        
        # Calculate average position of affected cells
        positions = [(self.cells[cid].position_x, self.cells[cid].position_y) for cid in cell_ids if cid in self.cells]
        
        if len(positions) < 2:
            return False
        
        # Calculate clustering metric (variance in positions)
        avg_x = sum(pos[0] for pos in positions) / len(positions)
        avg_y = sum(pos[1] for pos in positions) / len(positions)
        
        variance = sum((pos[0] - avg_x) ** 2 + (pos[1] - avg_y) ** 2 for pos in positions) / len(positions)
        
        # If variance is low, cells are clustered
        clustering_threshold = 0.001  # 1mm² threshold
        return variance < clustering_threshold
    
    def _get_p3e_thermal_correlation(self, cell_id: int, temperature_c: float) -> str:
        """Get P3E thermal correlation information"""
        correlations = []
        
        if cell_id == 6:
            if temperature_c >= 65.0:
                correlations.append("Pack 0535: Cell #6 catastrophic thermal runaway (65°C with 1048mV)")
            elif temperature_c >= 40.0:
                correlations.append("Pack 0533: Cell #6 thermal correlation during discharge")
            elif temperature_c >= 35.0:
                correlations.append("Cell #6 elevated temperature - high-risk cell per P3E analysis")
        
        if temperature_c >= 60.0:
            correlations.append("Thermal runaway threshold exceeded (P3E analysis)")
        elif temperature_c >= 45.0:
            correlations.append("Critical thermal zone - emergency response required")
        elif temperature_c >= 35.0:
            correlations.append("Elevated thermal zone - enhanced monitoring required")
        
        return "; ".join(correlations) if correlations else "Normal thermal operation"
    
    def _get_thermal_state(self, temperature_c: float) -> ThermalState:
        """Get thermal state based on temperature"""
        if temperature_c >= 80.0:
            return ThermalState.CATASTROPHIC
        elif temperature_c >= 60.0:
            return ThermalState.RUNAWAY
        elif temperature_c >= 45.0:
            return ThermalState.CRITICAL
        elif temperature_c >= 40.0:
            return ThermalState.HIGH
        elif temperature_c >= 35.0:
            return ThermalState.ELEVATED
        else:
            return ThermalState.NORMAL
    
    def _estimate_spread_time(self, propagation_rate_c_per_s: float, current_temp_c: float) -> float:
        """Estimate time for thermal spread to reach critical levels"""
        if propagation_rate_c_per_s <= 0:
            return float('inf')
        
        temp_to_critical = max(0, 60.0 - current_temp_c)  # Time to reach runaway
        return temp_to_critical / propagation_rate_c_per_s
    
    def _get_thermal_mitigation_actions(self, temperature_c: float) -> List[str]:
        """Get thermal mitigation actions based on temperature"""
        actions = []
        
        if temperature_c >= 80.0:
            actions.extend([
                "CATASTROPHIC: Immediate evacuation",
                "Emergency services activation",
                "Complete system isolation",
                "Fireproof containment activation"
            ])
        elif temperature_c >= 60.0:
            actions.extend([
                "RUNAWAY: Emergency shutdown",
                "Maximum cooling activation",
                "Personnel evacuation from area",
                "Thermal monitoring intensification"
            ])
        elif temperature_c >= 45.0:
            actions.extend([
                "CRITICAL: Immediate current reduction",
                "Active cooling system activation",
                "Prepare emergency shutdown",
                "Thermal imaging activation"
            ])
        elif temperature_c >= 40.0:
            actions.extend([
                "HIGH: Reduce operating current",
                "Increase cooling system effectiveness",
                "Enhanced temperature monitoring",
                "Check thermal management system"
            ])
        elif temperature_c >= 35.0:
            actions.extend([
                "ELEVATED: Monitor thermal trends",
                "Verify cooling system operation",
                "Check for thermal obstructions",
                "Increase monitoring frequency"
            ])
        
        return actions
    
    def _apply_cooling_effects(self) -> None:
        """Apply cooling system effects"""
        cooling_power = float(self.cooling_effectiveness.value)
        
        if cooling_power > 0:
            for cell in self.cells.values():
                # Enhanced cooling for overheated cells
                if cell.temperature_c > 35.0:
                    cooling_factor = cooling_power * (cell.temperature_c - self.ambient_temp_c) / 20.0
                    cell.temperature_c -= cooling_factor * self.time_step
                    cell.temperature_c = max(cell.temperature_c, self.ambient_temp_c)
    
    def _update_thermal_history(self) -> None:
        """Update thermal history for all cells"""
        current_thermal_map = {}
        
        for cell_id, cell in self.cells.items():
            # Update individual cell history
            cell.thermal_history.append(cell.temperature_c)
            if len(cell.thermal_history) > 100:  # Keep last 100 readings
                cell.thermal_history.pop(0)
            
            # Update thermal map
            current_thermal_map[cell_id] = cell.temperature_c
        
        # Add to thermal map history
        self.thermal_map_history.append(current_thermal_map)
        if len(self.thermal_map_history) > 1000:  # Keep last 1000 maps
            self.thermal_map_history.pop(0)
    
    def _check_runaway_conditions(self) -> None:
        """Check for thermal runaway conditions"""
        for cell_id, cell in self.cells.items():
            if cell.temperature_c >= self.runaway_threshold_c:
                if not any(e.source_cell == cell_id and e.severity_level == ThermalState.RUNAWAY 
                          for e in self.propagation_events[-5:]):
                    
                    # Create runaway event
                    event = ThermalPropagationEvent(
                        event_id=f"RUNAWAY_{int(time.time())}_{cell_id}",
                        timestamp=datetime.now(),
                        source_cell=cell_id,
                        affected_cells=[cell_id],
                        propagation_rate_c_per_s=0.0,
                        max_temperature_c=cell.temperature_c,
                        heat_generation_total_w=cell.heat_generation_w,
                        cooling_effectiveness=float(self.cooling_effectiveness.value),
                        geographic_cluster=cell_id in self.p3e_hotspot_cells,
                        p3e_correlation=self._get_p3e_thermal_correlation(cell_id, cell.temperature_c),
                        severity_level=ThermalState.RUNAWAY,
                        estimated_spread_time_s=0.0,
                        mitigation_actions=self._get_thermal_mitigation_actions(cell.temperature_c)
                    )
                    
                    self.propagation_events.append(event)
                    self.stats['runaway_events'] += 1
                    
                    self.logger.critical(f"THERMAL RUNAWAY DETECTED: Cell {cell_id} at {cell.temperature_c:.1f}°C")
    
    def set_cooling_effectiveness(self, effectiveness: CoolingEffectiveness) -> None:
        """Set cooling system effectiveness"""
        self.cooling_effectiveness = effectiveness
        self.stats['cooling_system_activations'] += 1
        self.logger.info(f"Cooling effectiveness set to: {effectiveness.name}")
    
    def get_thermal_map(self) -> Dict[int, Dict[str, Any]]:
        """Get current thermal map with detailed information"""
        thermal_map = {}
        
        for cell_id, cell in self.cells.items():
            thermal_map[cell_id] = {
                'temperature_c': cell.temperature_c,
                'heat_generation_w': cell.heat_generation_w,
                'thermal_state': self._get_thermal_state(cell.temperature_c).value,
                'position': {'x': cell.position_x, 'y': cell.position_y},
                'neighbors': cell.neighboring_cells,
                'runaway_probability': cell.runaway_probability,
                'p3e_hotspot': cell_id in self.p3e_hotspot_cells,
                'last_updated': cell.last_updated.isoformat()
            }
        
        return thermal_map
    
    def get_propagation_status(self) -> Dict[str, Any]:
        """Get thermal propagation status"""
        # Calculate current statistics
        temperatures = [cell.temperature_c for cell in self.cells.values()]
        max_temp = max(temperatures) if temperatures else 25.0
        avg_temp = sum(temperatures) / len(temperatures) if temperatures else 25.0
        
        # Recent events
        recent_events = [event for event in self.propagation_events 
                        if (datetime.now() - event.timestamp).total_seconds() < 300]  # Last 5 minutes
        
        # Risk assessment
        risk_levels = [self._get_thermal_state(temp) for temp in temperatures]
        risk_distribution = {}
        for risk in risk_levels:
            risk_distribution[risk.value] = risk_distribution.get(risk.value, 0) + 1
        
        return {
            'simulation_active': self.simulation_active,
            'cell_count': self.cell_count,
            'pack_layout': self.pack_layout,
            'current_status': {
                'max_temperature_c': max_temp,
                'average_temperature_c': avg_temp,
                'ambient_temperature_c': self.ambient_temp_c,
                'cooling_effectiveness': self.cooling_effectiveness.name,
                'runaway_cells': [cid for cid, cell in self.cells.items() 
                                if cell.temperature_c >= self.runaway_threshold_c]
            },
            'recent_events': len(recent_events),
            'total_events': len(self.propagation_events),
            'risk_distribution': risk_distribution,
            'p3e_hotspot_cells': self.p3e_hotspot_cells,
            'geographic_clustering_active': self.geographic_clustering_enabled,
            'statistics': self.stats.copy()
        }
    
    def get_propagation_report(self) -> Dict[str, Any]:
        """Generate comprehensive thermal propagation report"""
        status = self.get_propagation_status()
        thermal_map = self.get_thermal_map()
        
        # Recent significant events
        significant_events = [
            {
                'timestamp': event.timestamp.isoformat(),
                'source_cell': event.source_cell,
                'affected_cells': event.affected_cells,
                'max_temperature_c': event.max_temperature_c,
                'severity': event.severity_level.value,
                'p3e_correlation': event.p3e_correlation,
                'mitigation_actions': event.mitigation_actions
            }
            for event in self.propagation_events[-10:]  # Last 10 events
        ]
        
        # P3E correlation analysis
        p3e_events = [event for event in self.propagation_events if "Pack 0" in event.p3e_correlation]
        
        return {
            'status': status,
            'thermal_map': thermal_map,
            'recent_events': significant_events,
            'p3e_correlations': {
                'total_events': len(p3e_events),
                'pack_0535_correlations': len([e for e in p3e_events if "0535" in e.p3e_correlation]),
                'pack_0533_correlations': len([e for e in p3e_events if "0533" in e.p3e_correlation]),
                'cell_6_events': len([e for e in self.propagation_events if e.source_cell == 6]),
                'geographic_clustering_detected': len([e for e in self.propagation_events if e.geographic_cluster])
            },
            'thermal_trends': {
                'peak_temperature_reached': self.stats['max_temperature_reached'],
                'average_propagation_rate': self.stats.get('average_propagation_rate', 0.0),
                'runaway_events': self.stats['runaway_events'],
                'cooling_activations': self.stats['cooling_system_activations']
            },
            'recommendations': self._generate_thermal_recommendations()
        }
    
    def _generate_thermal_recommendations(self) -> List[str]:
        """Generate thermal management recommendations"""
        recommendations = []
        
        max_temp = max([cell.temperature_c for cell in self.cells.values()])
        
        if max_temp >= 60.0:
            recommendations.extend([
                "CRITICAL: Thermal runaway in progress - emergency shutdown required",
                "Activate maximum cooling immediately",
                "Prepare for evacuation procedures",
                "Contact emergency services"
            ])
        elif max_temp >= 45.0:
            recommendations.extend([
                "HIGH RISK: Reduce all currents immediately",
                "Activate enhanced cooling systems",
                "Monitor thermal propagation closely",
                "Prepare emergency shutdown procedures"
            ])
        elif max_temp >= 35.0:
            recommendations.extend([
                "ELEVATED: Increase thermal monitoring frequency",
                "Verify cooling system operation",
                "Reduce operating current by 25%",
                "Check for thermal obstructions"
            ])
        
        # P3E-specific recommendations
        if 6 in self.cells and self.cells[6].temperature_c > 30.0:
            recommendations.append("Enhanced Cell #6 monitoring required (P3E high-risk correlation)")
        
        if self.stats['p3e_correlations'] > 0:
            recommendations.append("P3E thermal patterns detected - implement proven mitigation strategies")
        
        if not recommendations:
            recommendations.append("Continue normal thermal monitoring")
        
        return recommendations


def main():
    """Test function for thermal propagation simulator"""
    # Setup logging
    if LOGGING_AVAILABLE:
        from ..utils.log_manager import setup_logging
        setup_logging(level='INFO')
        logger = get_logger(__name__, 'thermal_propagation')
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
    
    print("=== P3E Thermal Propagation Simulator Test ===")
    
    # Create simulator
    simulator = ThermalPropagationSimulator(cell_count=8, pack_layout="linear")
    simulator.start_simulation(time_step=0.5)
    
    print(f"Thermal simulation started")
    print(f"High-risk cells (P3E analysis): {simulator.p3e_hotspot_cells}")
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'Normal Operation',
            'description': 'All cells at normal temperature',
            'action': lambda: [simulator.set_cell_temperature(i, 25.0, 0.1) for i in range(1, 9)]
        },
        {
            'name': 'P3E Pack 0535 Simulation',
            'description': 'Simulate Pack 0535 Cell #6 thermal runaway',
            'action': lambda: simulator.simulate_p3e_pack_0535_event()
        },
        {
            'name': 'P3E Pack 0533 Correlation',
            'description': 'Simulate Pack 0533 thermal correlation',
            'action': lambda: simulator.simulate_p3e_pack_0533_thermal_correlation()
        },
        {
            'name': 'Progressive Heating',
            'description': 'Progressive heating simulation',
            'action': lambda: [simulator.set_cell_temperature(3, 45.0, 8.0),
                             simulator.set_cell_temperature(4, 42.0, 5.0)]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n--- Test {i+1}: {scenario['name']} ---")
        print(f"Description: {scenario['description']}")
        
        # Execute scenario
        scenario['action']()
        
        # Wait for propagation
        time.sleep(2.0)
        
        # Check status
        status = simulator.get_propagation_status()
        thermal_map = simulator.get_thermal_map()
        
        print(f"Max Temperature: {status['current_status']['max_temperature_c']:.1f}°C")
        print(f"Recent Events: {status['recent_events']}")
        print(f"Runaway Cells: {status['current_status']['runaway_cells']}")
        
        # Show hottest cells
        hot_cells = [(cid, data['temperature_c']) for cid, data in thermal_map.items() 
                    if data['temperature_c'] > 30.0]
        if hot_cells:
            hot_cells_sorted = sorted(hot_cells, key=lambda x: x[1], reverse=True)
            print(f"Hot Cells: {[(f'Cell {cid}', f'{temp:.1f}°C') for cid, temp in hot_cells_sorted[:3]]}")
        
        time.sleep(3.0)
    
    # Generate final report
    print("\n=== Thermal Propagation Report ===")
    report = simulator.get_propagation_report()
    
    print(f"Total Events: {report['status']['total_events']}")
    print(f"P3E Correlations: {report['p3e_correlations']['total_events']}")
    print(f"Pack 0535 Events: {report['p3e_correlations']['pack_0535_correlations']}")
    print(f"Cell #6 Events: {report['p3e_correlations']['cell_6_events']}")
    print(f"Peak Temperature: {report['thermal_trends']['peak_temperature_reached']:.1f}°C")
    
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
    
    # Stop simulation
    simulator.stop_simulation()
    print("\nThermal simulation stopped.")


if __name__ == "__main__":
    main()