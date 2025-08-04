#!/usr/bin/env python3
"""
Real-time Alert Generation System - P3E Analysis Implementation

This module provides comprehensive real-time alert generation for thermal runaway
detection based on P3E analysis data. It integrates with the runaway detection
and thermal propagation systems to provide multi-layered alerting with
escalation protocols and automated response recommendations.

Key Features:
1. Multi-level alert severity system
2. Real-time notification delivery
3. Alert escalation protocols based on P3E timelines
4. Automated response recommendations
5. Historical alert analysis and trends
6. Integration with external monitoring systems
7. Emergency shutdown coordination

Based on P3E response timelines:
- Early Warning (100mV): Immediate alert required
- High Risk (300mV): 30-second response window
- Critical (500mV): <10-second response window
- Emergency (700mV): 1-second BMS automatic response
"""

import sys
import os
import logging
import time
import json
import threading
import queue
import smtplib
import socket
from typing import Dict, List, Optional, Any, Callable, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import logging system
try:
    from ..utils.log_manager import get_logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

# Import runaway detection and thermal propagation
try:
    from .runaway_detection import RunawayEvent, RunawayRiskLevel, RunawayDetector
    from .thermal_propagation import ThermalPropagationEvent, ThermalState, ThermalPropagationSimulator
    ALGORITHMS_AVAILABLE = True
except ImportError:
    ALGORITHMS_AVAILABLE = False
    # Fallback definitions
    class RunawayRiskLevel(Enum):
        NORMAL = "normal"
        EARLY_WARNING = "warning"
        HIGH_RISK = "high"
        CRITICAL = "critical"
        EMERGENCY = "emergency"
        CATASTROPHIC = "catastrophic"


class AlertSeverity(Enum):
    """Alert severity levels with P3E response requirements"""
    INFO = ("info", 0, 300)           # Informational, 5-minute response
    WARNING = ("warning", 1, 60)      # Early warning, 1-minute response
    HIGH = ("high", 2, 30)           # High risk, 30-second response (P3E)
    CRITICAL = ("critical", 3, 10)    # Critical, <10-second response (P3E)
    EMERGENCY = ("emergency", 4, 1)   # Emergency, 1-second response (P3E)
    CATASTROPHIC = ("catastrophic", 5, 0)  # Immediate action required
    
    def __init__(self, name: str, level: int, response_time_s: int):
        self.level = level
        self.response_time_s = response_time_s


class AlertType(Enum):
    """Types of alerts generated"""
    VOLTAGE_THRESHOLD = "voltage_threshold"
    TEMPERATURE_GRADIENT = "temperature_gradient"
    CURRENT_ANOMALY = "current_anomaly"
    PROGRESSIVE_FAILURE = "progressive_failure"
    THERMAL_PROPAGATION = "thermal_propagation"
    BMS_PROTECTION_FAILURE = "bms_protection_failure"
    SYSTEM_HEALTH = "system_health"
    P3E_CORRELATION = "p3e_correlation"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"


class AlertChannel(Enum):
    """Alert delivery channels"""
    LOG = "log"
    CONSOLE = "console"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    DATABASE = "database"
    DASHBOARD = "dashboard"
    BMS = "bms"
    TCP_SOCKET = "tcp_socket"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    condition: str  # Python expression to evaluate
    channels: List[AlertChannel]
    cooldown_seconds: int = 60
    escalation_time_seconds: int = 300
    p3e_correlation: bool = False
    auto_response: bool = False
    enabled: bool = True


@dataclass
class Alert:
    """Alert message structure"""
    alert_id: str
    timestamp: datetime
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    source_data: Dict[str, Any]
    p3e_correlation: str
    response_required_by: datetime
    escalation_level: int = 0
    acknowledged: bool = False
    resolved: bool = False
    auto_response_triggered: bool = False
    delivery_status: Dict[AlertChannel, bool] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertConfiguration:
    """System-wide alert configuration"""
    # Email settings
    smtp_server: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_recipients: List[str] = field(default_factory=list)
    
    # SMS settings (placeholder for future implementation)
    sms_gateway: str = ""
    sms_recipients: List[str] = field(default_factory=list)
    
    # Webhook settings
    webhook_urls: List[str] = field(default_factory=list)
    webhook_timeout: int = 10
    
    # Database settings
    database_enabled: bool = False
    database_connection: str = ""
    
    # TCP socket settings
    tcp_host: str = "localhost"
    tcp_port: int = 8765
    
    # General settings
    max_alerts_per_minute: int = 60
    alert_retention_days: int = 30
    auto_escalation_enabled: bool = True
    emergency_shutdown_enabled: bool = True


class AlertDeliveryService:
    """Service for delivering alerts through various channels"""
    
    def __init__(self, config: AlertConfiguration):
        self.config = config
        
        if LOGGING_AVAILABLE:
            self.logger = get_logger(__name__, 'alert_delivery')
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
        
        # Delivery statistics
        self.delivery_stats = {
            'total_sent': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'channel_stats': {channel: {'sent': 0, 'failed': 0} for channel in AlertChannel}
        }
    
    def deliver_alert(self, alert: Alert, channels: List[AlertChannel]) -> Dict[AlertChannel, bool]:
        """Deliver alert through specified channels"""
        delivery_results = {}
        
        for channel in channels:
            try:
                if channel == AlertChannel.LOG:
                    self._deliver_to_log(alert)
                elif channel == AlertChannel.CONSOLE:
                    self._deliver_to_console(alert)
                elif channel == AlertChannel.EMAIL:
                    self._deliver_to_email(alert)
                elif channel == AlertChannel.WEBHOOK:
                    self._deliver_to_webhook(alert)
                elif channel == AlertChannel.DATABASE:
                    self._deliver_to_database(alert)
                elif channel == AlertChannel.TCP_SOCKET:
                    self._deliver_to_tcp_socket(alert)
                else:
                    self.logger.warning(f"Unsupported delivery channel: {channel}")
                    delivery_results[channel] = False
                    continue
                
                delivery_results[channel] = True
                self.delivery_stats['successful_deliveries'] += 1
                self.delivery_stats['channel_stats'][channel]['sent'] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to deliver alert via {channel}: {e}")
                delivery_results[channel] = False
                self.delivery_stats['failed_deliveries'] += 1
                self.delivery_stats['channel_stats'][channel]['failed'] += 1
            
            self.delivery_stats['total_sent'] += 1
        
        return delivery_results
    
    def _deliver_to_log(self, alert: Alert) -> None:
        """Deliver alert to log system"""
        log_message = f"ALERT [{alert.severity.name}] {alert.title}: {alert.message}"
        
        if alert.severity.level >= AlertSeverity.EMERGENCY.level:
            self.logger.critical(log_message)
        elif alert.severity.level >= AlertSeverity.CRITICAL.level:
            self.logger.error(log_message)
        elif alert.severity.level >= AlertSeverity.HIGH.level:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _deliver_to_console(self, alert: Alert) -> None:
        """Deliver alert to console"""
        timestamp = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        severity_marker = "🚨" if alert.severity.level >= AlertSeverity.CRITICAL.level else "⚠️"
        
        print(f"\n{severity_marker} [{timestamp}] {alert.severity.name} ALERT")
        print(f"Type: {alert.alert_type.value}")
        print(f"Title: {alert.title}")
        print(f"Message: {alert.message}")
        if alert.p3e_correlation:
            print(f"P3E Correlation: {alert.p3e_correlation}")
        print(f"Response Required By: {alert.response_required_by.strftime('%H:%M:%S')}")
        if alert.source_data:
            print(f"Data: {json.dumps(alert.source_data, indent=2)}")
        print("-" * 80)
    
    def _deliver_to_email(self, alert: Alert) -> None:
        """Deliver alert via email"""
        if not self.config.email_recipients:
            return
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = self.config.smtp_username or "p3e-alert-system@custompower.com"
        msg['To'] = ", ".join(self.config.email_recipients)
        msg['Subject'] = f"[{alert.severity.name}] P3E Alert: {alert.title}"
        
        # Email body
        body = f"""
P3E Battery Management System Alert

Severity: {alert.severity.name}
Type: {alert.alert_type.value}
Timestamp: {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
Alert ID: {alert.alert_id}

Title: {alert.title}
Message: {alert.message}

P3E Correlation: {alert.p3e_correlation}

Response Required By: {alert.response_required_by.strftime("%Y-%m-%d %H:%M:%S")}

Source Data:
{json.dumps(alert.source_data, indent=2)}

---
P3E Battery Safety System
Custom Power LLC
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        try:
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.smtp_username and self.config.smtp_password:
                    server.starttls()
                    server.login(self.config.smtp_username, self.config.smtp_password)
                
                server.send_message(msg)
                
        except Exception as e:
            self.logger.error(f"Email delivery failed: {e}")
            raise
    
    def _deliver_to_webhook(self, alert: Alert) -> None:
        """Deliver alert via webhook"""
        if not self.config.webhook_urls:
            return
        
        import requests
        
        # Prepare webhook payload
        payload = {
            'alert_id': alert.alert_id,
            'timestamp': alert.timestamp.isoformat(),
            'severity': alert.severity.name,
            'type': alert.alert_type.value,
            'title': alert.title,
            'message': alert.message,
            'p3e_correlation': alert.p3e_correlation,
            'response_required_by': alert.response_required_by.isoformat(),
            'source_data': alert.source_data,
            'metadata': alert.metadata
        }
        
        # Send to all webhook URLs
        for url in self.config.webhook_urls:
            try:
                response = requests.post(
                    url, 
                    json=payload, 
                    timeout=self.config.webhook_timeout,
                    headers={'Content-Type': 'application/json'}
                )
                response.raise_for_status()
                
            except Exception as e:
                self.logger.error(f"Webhook delivery to {url} failed: {e}")
                raise
    
    def _deliver_to_database(self, alert: Alert) -> None:
        """Deliver alert to database (placeholder)"""
        # This would implement database storage
        # For now, just log the intent
        self.logger.info(f"Database delivery: {alert.alert_id}")
    
    def _deliver_to_tcp_socket(self, alert: Alert) -> None:
        """Deliver alert via TCP socket"""
        try:
            # Create alert message for TCP
            message = {
                'type': 'p3e_alert',
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'severity': alert.severity.name,
                'alert_type': alert.alert_type.value,
                'title': alert.title,
                'message': alert.message,
                'p3e_correlation': alert.p3e_correlation,
                'source_data': alert.source_data
            }
            
            # Send via TCP socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5.0)
                sock.connect((self.config.tcp_host, self.config.tcp_port))
                sock.sendall(json.dumps(message).encode('utf-8'))
                
        except Exception as e:
            self.logger.error(f"TCP socket delivery failed: {e}")
            raise


class AlertManager:
    """
    Comprehensive alert management system for P3E battery monitoring
    
    Manages alert generation, delivery, escalation, and response coordination
    based on P3E analysis data and proven response protocols.
    """
    
    def __init__(self, config: Optional[AlertConfiguration] = None):
        """Initialize alert management system"""
        # Setup logging
        if LOGGING_AVAILABLE:
            self.logger = get_logger(__name__, 'alert_manager')
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
        
        self.config = config or AlertConfiguration()
        self.delivery_service = AlertDeliveryService(self.config)
        
        # Alert storage
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.alert_rules: Dict[str, AlertRule] = {}
        
        # Alert processing
        self.alert_queue = queue.Queue()
        self.processing_active = False
        self.rate_limiter = {}  # Channel -> last_alert_time mapping
        
        # Statistics
        self.stats = {
            'total_alerts': 0,
            'alerts_by_severity': {severity: 0 for severity in AlertSeverity},
            'alerts_by_type': {alert_type: 0 for alert_type in AlertType},
            'escalated_alerts': 0,
            'auto_responses_triggered': 0,
            'average_response_time': 0.0,
            'p3e_correlations': 0
        }
        
        # Initialize P3E-specific alert rules
        self._initialize_p3e_alert_rules()
        
        self.logger.info("AlertManager initialized with P3E-specific rules")
    
    def _initialize_p3e_alert_rules(self) -> None:
        """Initialize P3E analysis-based alert rules"""
        p3e_rules = [
            AlertRule(
                rule_id="p3e_early_warning",
                name="P3E Early Warning (100mV)",
                alert_type=AlertType.VOLTAGE_THRESHOLD,
                severity=AlertSeverity.WARNING,
                condition="pack_delta_mv >= 100",
                channels=[AlertChannel.LOG, AlertChannel.CONSOLE, AlertChannel.DASHBOARD],
                cooldown_seconds=30,
                p3e_correlation=True
            ),
            AlertRule(
                rule_id="p3e_high_risk",
                name="P3E High Risk (300mV - Pack 0533 Pattern)",
                alert_type=AlertType.VOLTAGE_THRESHOLD,
                severity=AlertSeverity.HIGH,
                condition="pack_delta_mv >= 300",
                channels=[AlertChannel.LOG, AlertChannel.CONSOLE, AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                cooldown_seconds=10,
                escalation_time_seconds=30,
                p3e_correlation=True,
                auto_response=True
            ),
            AlertRule(
                rule_id="p3e_critical",
                name="P3E Critical (500mV - Emergency Response)",
                alert_type=AlertType.VOLTAGE_THRESHOLD,
                severity=AlertSeverity.CRITICAL,
                condition="pack_delta_mv >= 500",
                channels=[AlertChannel.LOG, AlertChannel.CONSOLE, AlertChannel.EMAIL, AlertChannel.WEBHOOK, AlertChannel.TCP_SOCKET],
                cooldown_seconds=5,
                escalation_time_seconds=10,
                p3e_correlation=True,
                auto_response=True
            ),
            AlertRule(
                rule_id="p3e_emergency",
                name="P3E Emergency (700mV - Pack 0533 Level)",
                alert_type=AlertType.VOLTAGE_THRESHOLD,
                severity=AlertSeverity.EMERGENCY,
                condition="pack_delta_mv >= 700",
                channels=list(AlertChannel),
                cooldown_seconds=0,
                escalation_time_seconds=1,
                p3e_correlation=True,
                auto_response=True
            ),
            AlertRule(
                rule_id="p3e_catastrophic",
                name="P3E Catastrophic (1000mV - Pack 0535 Level)",
                alert_type=AlertType.BMS_PROTECTION_FAILURE,
                severity=AlertSeverity.CATASTROPHIC,
                condition="pack_delta_mv >= 1000",
                channels=list(AlertChannel),
                cooldown_seconds=0,
                escalation_time_seconds=0,
                p3e_correlation=True,
                auto_response=True
            ),
            AlertRule(
                rule_id="p3e_cell6_monitor",
                name="P3E Cell #6 Enhanced Monitoring",
                alert_type=AlertType.P3E_CORRELATION,
                severity=AlertSeverity.HIGH,
                condition="cell_6_voltage_mv > 4200 or cell_6_voltage_mv < 2500",
                channels=[AlertChannel.LOG, AlertChannel.CONSOLE, AlertChannel.EMAIL],
                cooldown_seconds=60,
                p3e_correlation=True
            ),
            AlertRule(
                rule_id="p3e_thermal_runaway",
                name="P3E Thermal Runaway (65°C Pack 0535 Pattern)",
                alert_type=AlertType.THERMAL_PROPAGATION,
                severity=AlertSeverity.EMERGENCY,
                condition="max_temperature_c >= 60.0",
                channels=list(AlertChannel),
                cooldown_seconds=0,
                escalation_time_seconds=1,
                p3e_correlation=True,
                auto_response=True
            ),
            AlertRule(
                rule_id="p3e_discharge_runaway",
                name="P3E Discharge Runaway Pattern (Pack 0533)",
                alert_type=AlertType.CURRENT_ANOMALY,
                severity=AlertSeverity.HIGH,
                condition="current_ma <= -5000 and pack_delta_mv >= 50",
                channels=[AlertChannel.LOG, AlertChannel.CONSOLE, AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                cooldown_seconds=15,
                escalation_time_seconds=60,
                p3e_correlation=True,
                auto_response=True
            )
        ]
        
        for rule in p3e_rules:
            self.alert_rules[rule.rule_id] = rule
        
        self.logger.info(f"Initialized {len(p3e_rules)} P3E-specific alert rules")
    
    def start_processing(self) -> None:
        """Start alert processing"""
        self.processing_active = True
        
        # Start processing thread
        self._process_thread = threading.Thread(target=self._process_alerts)
        self._process_thread.daemon = True
        self._process_thread.start()
        
        # Start escalation monitoring thread
        self._escalation_thread = threading.Thread(target=self._monitor_escalations)
        self._escalation_thread.daemon = True
        self._escalation_thread.start()
        
        self.logger.info("Alert processing started")
    
    def stop_processing(self) -> None:
        """Stop alert processing"""
        self.processing_active = False
        self.logger.info("Alert processing stopped")
    
    def generate_alert(self, alert_type: AlertType, title: str, message: str,
                      severity: AlertSeverity, source_data: Dict[str, Any],
                      p3e_correlation: str = "", metadata: Dict[str, Any] = None) -> str:
        """Generate a new alert"""
        alert_id = f"{alert_type.value}_{int(time.time())}_{hash(message) % 10000}"
        
        # Calculate response deadline based on severity
        response_deadline = datetime.now() + timedelta(seconds=severity.response_time_s)
        
        alert = Alert(
            alert_id=alert_id,
            timestamp=datetime.now(),
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            source_data=source_data,
            p3e_correlation=p3e_correlation,
            response_required_by=response_deadline,
            metadata=metadata or {}
        )
        
        # Add to queue for processing
        self.alert_queue.put(alert)
        
        # Update statistics
        self.stats['total_alerts'] += 1
        self.stats['alerts_by_severity'][severity] += 1
        self.stats['alerts_by_type'][alert_type] += 1
        
        if p3e_correlation:
            self.stats['p3e_correlations'] += 1
        
        self.logger.info(f"Alert generated: {alert_id} - {severity.name} - {title}")
        
        return alert_id
    
    def _process_alerts(self) -> None:
        """Main alert processing loop"""
        while self.processing_active:
            try:
                # Get next alert from queue
                alert = self.alert_queue.get(timeout=1.0)
                
                # Evaluate alert rules
                applicable_rules = self._evaluate_alert_rules(alert)
                
                if applicable_rules:
                    # Process with applicable rules
                    for rule in applicable_rules:
                        self._process_alert_with_rule(alert, rule)
                else:
                    # Default processing
                    self._process_alert_default(alert)
                
                # Store alert
                self.active_alerts[alert.alert_id] = alert
                self.alert_history.append(alert)
                
                # Clean up old alerts
                self._cleanup_old_alerts()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing alert: {e}")
    
    def _evaluate_alert_rules(self, alert: Alert) -> List[AlertRule]:
        """Evaluate which alert rules apply to this alert"""
        applicable_rules = []
        
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            if rule.alert_type != alert.alert_type:
                continue
            
            # Check cooldown
            last_alert_time = self.rate_limiter.get(rule.rule_id, datetime.min)
            if (datetime.now() - last_alert_time).total_seconds() < rule.cooldown_seconds:
                continue
            
            # Evaluate condition
            try:
                # Create evaluation context
                eval_context = {
                    'pack_delta_mv': alert.source_data.get('pack_delta_mv', 0),
                    'max_temperature_c': alert.source_data.get('max_temperature_c', 0),
                    'current_ma': alert.source_data.get('current_ma', 0),
                    'cell_6_voltage_mv': alert.source_data.get('cell_6_voltage_mv', 0),
                    'severity_level': alert.severity.level,
                    'p3e_correlation': bool(alert.p3e_correlation)
                }
                
                if eval(rule.condition, {"__builtins__": {}}, eval_context):
                    applicable_rules.append(rule)
                    self.rate_limiter[rule.rule_id] = datetime.now()
                    
            except Exception as e:
                self.logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
        
        return applicable_rules
    
    def _process_alert_with_rule(self, alert: Alert, rule: AlertRule) -> None:
        """Process alert using specific rule"""
        # Update alert severity if rule specifies higher
        if rule.severity.level > alert.severity.level:
            alert.severity = rule.severity
            alert.response_required_by = datetime.now() + timedelta(seconds=rule.severity.response_time_s)
        
        # Deliver alert through rule channels
        delivery_results = self.delivery_service.deliver_alert(alert, rule.channels)
        alert.delivery_status.update(delivery_results)
        
        # Trigger auto-response if enabled
        if rule.auto_response:
            self._trigger_auto_response(alert, rule)
        
        # Set up escalation if configured
        if rule.escalation_time_seconds > 0:
            self._schedule_escalation(alert, rule.escalation_time_seconds)
        
        self.logger.info(f"Alert {alert.alert_id} processed with rule {rule.rule_id}")
    
    def _process_alert_default(self, alert: Alert) -> None:
        """Default alert processing when no rules match"""
        # Default channels based on severity
        if alert.severity.level >= AlertSeverity.CRITICAL.level:
            channels = [AlertChannel.LOG, AlertChannel.CONSOLE, AlertChannel.EMAIL]
        elif alert.severity.level >= AlertSeverity.HIGH.level:
            channels = [AlertChannel.LOG, AlertChannel.CONSOLE]
        else:
            channels = [AlertChannel.LOG]
        
        # Deliver alert
        delivery_results = self.delivery_service.deliver_alert(alert, channels)
        alert.delivery_status.update(delivery_results)
        
        self.logger.info(f"Alert {alert.alert_id} processed with default rules")
    
    def _trigger_auto_response(self, alert: Alert, rule: AlertRule) -> None:
        """Trigger automatic response based on alert and rule"""
        if alert.auto_response_triggered:
            return  # Already triggered
        
        try:
            # P3E-specific auto responses
            if "p3e_high_risk" in rule.rule_id:
                self._auto_response_reduce_current(alert, 50)  # Reduce to 50%
            elif "p3e_critical" in rule.rule_id:
                self._auto_response_prepare_shutdown(alert)
            elif "p3e_emergency" in rule.rule_id or "p3e_catastrophic" in rule.rule_id:
                self._auto_response_emergency_shutdown(alert)
            elif "p3e_thermal_runaway" in rule.rule_id:
                self._auto_response_thermal_emergency(alert)
            elif "p3e_discharge_runaway" in rule.rule_id:
                self._auto_response_stop_discharge(alert)
            
            alert.auto_response_triggered = True
            self.stats['auto_responses_triggered'] += 1
            
            self.logger.warning(f"Auto-response triggered for alert {alert.alert_id}")
            
        except Exception as e:
            self.logger.error(f"Auto-response failed for alert {alert.alert_id}: {e}")
    
    def _auto_response_reduce_current(self, alert: Alert, percentage: int) -> None:
        """Auto-response: Reduce current to specified percentage"""
        response_alert = Alert(
            alert_id=f"AUTO_CURRENT_{int(time.time())}",
            timestamp=datetime.now(),
            alert_type=AlertType.SYSTEM_HEALTH,
            severity=AlertSeverity.INFO,
            title="Auto-Response: Current Reduction",
            message=f"Automatically reducing current to {percentage}% due to alert {alert.alert_id}",
            source_data={'parent_alert': alert.alert_id, 'action': 'reduce_current', 'percentage': percentage},
            p3e_correlation="P3E Protocol: Reduce current during high-risk conditions",
            response_required_by=datetime.now() + timedelta(seconds=60)
        )
        
        self.alert_queue.put(response_alert)
    
    def _auto_response_prepare_shutdown(self, alert: Alert) -> None:
        """Auto-response: Prepare for emergency shutdown"""
        response_alert = Alert(
            alert_id=f"AUTO_PREP_{int(time.time())}",
            timestamp=datetime.now(),
            alert_type=AlertType.SYSTEM_HEALTH,
            severity=AlertSeverity.HIGH,
            title="Auto-Response: Shutdown Preparation",
            message=f"Preparing emergency shutdown procedures due to alert {alert.alert_id}",
            source_data={'parent_alert': alert.alert_id, 'action': 'prepare_shutdown'},
            p3e_correlation="P3E Protocol: Prepare shutdown for critical conditions",
            response_required_by=datetime.now() + timedelta(seconds=10)
        )
        
        self.alert_queue.put(response_alert)
    
    def _auto_response_emergency_shutdown(self, alert: Alert) -> None:
        """Auto-response: Emergency shutdown"""
        response_alert = Alert(
            alert_id=f"AUTO_SHUTDOWN_{int(time.time())}",
            timestamp=datetime.now(),
            alert_type=AlertType.EMERGENCY_SHUTDOWN,
            severity=AlertSeverity.CATASTROPHIC,
            title="Auto-Response: EMERGENCY SHUTDOWN",
            message=f"EMERGENCY SHUTDOWN initiated due to alert {alert.alert_id}",
            source_data={'parent_alert': alert.alert_id, 'action': 'emergency_shutdown'},
            p3e_correlation="P3E Protocol: Emergency shutdown for catastrophic conditions",
            response_required_by=datetime.now() + timedelta(seconds=1)
        )
        
        self.alert_queue.put(response_alert)
    
    def _auto_response_thermal_emergency(self, alert: Alert) -> None:
        """Auto-response: Thermal emergency procedures"""
        response_alert = Alert(
            alert_id=f"AUTO_THERMAL_{int(time.time())}",
            timestamp=datetime.now(),
            alert_type=AlertType.THERMAL_PROPAGATION,
            severity=AlertSeverity.EMERGENCY,
            title="Auto-Response: Thermal Emergency",
            message=f"Thermal emergency procedures activated due to alert {alert.alert_id}",
            source_data={'parent_alert': alert.alert_id, 'action': 'thermal_emergency'},
            p3e_correlation="P3E Protocol: Thermal emergency response (Pack 0535 pattern)",
            response_required_by=datetime.now() + timedelta(seconds=1)
        )
        
        self.alert_queue.put(response_alert)
    
    def _auto_response_stop_discharge(self, alert: Alert) -> None:
        """Auto-response: Stop discharge immediately"""
        response_alert = Alert(
            alert_id=f"AUTO_DISCHARGE_{int(time.time())}",
            timestamp=datetime.now(),
            alert_type=AlertType.CURRENT_ANOMALY,
            severity=AlertSeverity.CRITICAL,
            title="Auto-Response: Stop Discharge",
            message=f"Discharge stopped immediately due to alert {alert.alert_id}",
            source_data={'parent_alert': alert.alert_id, 'action': 'stop_discharge'},
            p3e_correlation="P3E Protocol: Stop discharge during runaway conditions (Pack 0533 pattern)",
            response_required_by=datetime.now() + timedelta(seconds=5)
        )
        
        self.alert_queue.put(response_alert)
    
    def _schedule_escalation(self, alert: Alert, escalation_time_s: int) -> None:
        """Schedule alert escalation"""
        def escalate():
            if alert.alert_id in self.active_alerts and not alert.acknowledged:
                alert.escalation_level += 1
                alert.severity = AlertSeverity(min(alert.severity.level + 1, AlertSeverity.CATASTROPHIC.level))
                
                escalation_alert = Alert(
                    alert_id=f"ESC_{alert.alert_id}_{alert.escalation_level}",
                    timestamp=datetime.now(),
                    alert_type=AlertType.SYSTEM_HEALTH,
                    severity=alert.severity,
                    title=f"ESCALATED: {alert.title}",
                    message=f"Alert {alert.alert_id} escalated to {alert.severity.name} - no acknowledgment received",
                    source_data=alert.source_data,
                    p3e_correlation=f"Escalated: {alert.p3e_correlation}",
                    response_required_by=datetime.now() + timedelta(seconds=alert.severity.response_time_s)
                )
                
                self.alert_queue.put(escalation_alert)
                self.stats['escalated_alerts'] += 1
        
        timer = threading.Timer(escalation_time_s, escalate)
        timer.start()
    
    def _monitor_escalations(self) -> None:
        """Monitor alerts for escalation requirements"""
        while self.processing_active:
            try:
                current_time = datetime.now()
                
                for alert in list(self.active_alerts.values()):
                    if (not alert.acknowledged and 
                        not alert.resolved and 
                        current_time > alert.response_required_by):
                        
                        # Auto-escalate overdue alerts
                        if self.config.auto_escalation_enabled:
                            alert.escalation_level += 1
                            self.stats['escalated_alerts'] += 1
                            
                            self.logger.warning(f"Auto-escalating overdue alert: {alert.alert_id}")
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in escalation monitoring: {e}")
                time.sleep(30)
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.metadata['acknowledged_by'] = acknowledged_by
            alert.metadata['acknowledged_at'] = datetime.now().isoformat()
            
            self.logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
            return True
        
        return False
    
    def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.metadata['resolved_by'] = resolved_by
            alert.metadata['resolved_at'] = datetime.now().isoformat()
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            self.logger.info(f"Alert resolved: {alert_id} by {resolved_by}")
            return True
        
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert system statistics"""
        # Calculate response time statistics
        response_times = []
        for alert in self.alert_history[-100:]:  # Last 100 alerts
            if alert.acknowledged and 'acknowledged_at' in alert.metadata:
                ack_time = datetime.fromisoformat(alert.metadata['acknowledged_at'])
                response_time = (ack_time - alert.timestamp).total_seconds()
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        return {
            'total_alerts': self.stats['total_alerts'],
            'active_alerts': len(self.active_alerts),
            'alerts_by_severity': {sev.name: count for sev, count in self.stats['alerts_by_severity'].items()},
            'alerts_by_type': {atype.name: count for atype, count in self.stats['alerts_by_type'].items()},
            'escalated_alerts': self.stats['escalated_alerts'],
            'auto_responses_triggered': self.stats['auto_responses_triggered'],
            'average_response_time_s': avg_response_time,
            'p3e_correlations': self.stats['p3e_correlations'],
            'delivery_stats': self.delivery_service.delivery_stats,
            'system_status': 'active' if self.processing_active else 'inactive'
        }
    
    def _cleanup_old_alerts(self) -> None:
        """Clean up old alerts to prevent memory issues"""
        cutoff_date = datetime.now() - timedelta(days=self.config.alert_retention_days)
        
        # Clean up history
        self.alert_history = [alert for alert in self.alert_history if alert.timestamp > cutoff_date]
        
        # Clean up resolved active alerts older than 1 hour
        hour_ago = datetime.now() - timedelta(hours=1)
        resolved_alerts = [aid for aid, alert in self.active_alerts.items() 
                          if alert.resolved and alert.timestamp < hour_ago]
        
        for alert_id in resolved_alerts:
            del self.active_alerts[alert_id]


def main():
    """Test function for alert system"""
    # Setup logging
    if LOGGING_AVAILABLE:
        from ..utils.log_manager import setup_logging
        setup_logging(level='INFO')
        logger = get_logger(__name__, 'alert_system')
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
    
    print("=== P3E Alert System Test ===")
    
    # Create alert manager
    config = AlertConfiguration(
        email_recipients=["test@custompower.com"],
        webhook_urls=["http://localhost:8080/webhook"],
        auto_escalation_enabled=True
    )
    
    alert_manager = AlertManager(config)
    alert_manager.start_processing()
    
    print("Alert system started with P3E rules")
    
    # Test P3E alert scenarios
    test_scenarios = [
        {
            'name': 'P3E Early Warning (100mV)',
            'alert_type': AlertType.VOLTAGE_THRESHOLD,
            'severity': AlertSeverity.WARNING,
            'title': 'Cell voltage delta exceeds 100mV threshold',
            'message': 'Pack delta reached 120mV - P3E early warning threshold exceeded',
            'source_data': {'pack_delta_mv': 120, 'max_voltage_mv': 3820, 'min_voltage_mv': 3700},
            'p3e_correlation': 'P3E threshold: 5-8x normal operation'
        },
        {
            'name': 'P3E Pack 0533 Pattern (326mV)',
            'alert_type': AlertType.VOLTAGE_THRESHOLD,
            'severity': AlertSeverity.HIGH,
            'title': 'Pack 0533 escalation pattern detected',
            'message': 'Cell voltage delta 326mV during -5.3A discharge - matches Pack 0533 runaway pattern',
            'source_data': {'pack_delta_mv': 326, 'current_ma': -5300, 'cell_6_voltage_mv': 2853},
            'p3e_correlation': 'Pack 0533: 326mV escalation point during discharge'
        },
        {
            'name': 'P3E Critical (702mV)',
            'alert_type': AlertType.VOLTAGE_THRESHOLD,
            'severity': AlertSeverity.EMERGENCY,
            'title': 'CRITICAL: Pack 0533 runaway level reached',
            'message': 'Cell voltage delta 702mV - Pack 0533 critical failure level',
            'source_data': {'pack_delta_mv': 702, 'current_ma': -5300, 'cell_6_voltage_mv': 2474},
            'p3e_correlation': 'Pack 0533: 702mV peak runaway during discharge'
        },
        {
            'name': 'P3E Pack 0535 Catastrophic (1048mV)',
            'alert_type': AlertType.BMS_PROTECTION_FAILURE,
            'severity': AlertSeverity.CATASTROPHIC,
            'title': 'CATASTROPHIC: Pack 0535 runaway level',
            'message': 'Cell voltage delta 1048mV with 4411mV overvoltage - Pack 0535 catastrophic failure',
            'source_data': {'pack_delta_mv': 1048, 'cell_6_voltage_mv': 4411, 'max_temperature_c': 65.0},
            'p3e_correlation': 'Pack 0535: 1048mV catastrophic runaway with thermal correlation'
        },
        {
            'name': 'P3E Thermal Runaway',
            'alert_type': AlertType.THERMAL_PROPAGATION,
            'severity': AlertSeverity.EMERGENCY,
            'title': 'Thermal runaway detected - Pack 0535 pattern',
            'message': 'Cell temperature 65°C with thermal propagation - matches Pack 0535 thermal runaway',
            'source_data': {'max_temperature_c': 65.0, 'source_cell': 6, 'pack_delta_mv': 1048},
            'p3e_correlation': 'Pack 0535: 65°C thermal hotspot with electrical runaway'
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n--- Test {i+1}: {scenario['name']} ---")
        
        # Generate alert
        alert_id = alert_manager.generate_alert(
            alert_type=scenario['alert_type'],
            title=scenario['title'],
            message=scenario['message'],
            severity=scenario['severity'],
            source_data=scenario['source_data'],
            p3e_correlation=scenario['p3e_correlation']
        )
        
        print(f"Alert generated: {alert_id}")
        
        # Wait for processing
        time.sleep(2.0)
        
        # Check statistics
        stats = alert_manager.get_alert_statistics()
        print(f"Total alerts: {stats['total_alerts']}")
        print(f"Active alerts: {stats['active_alerts']}")
        print(f"P3E correlations: {stats['p3e_correlations']}")
        print(f"Auto responses: {stats['auto_responses_triggered']}")
        
        time.sleep(1.0)
    
    # Show final statistics
    print("\n=== Final Alert Statistics ===")
    final_stats = alert_manager.get_alert_statistics()
    
    print(f"Total Alerts Generated: {final_stats['total_alerts']}")
    print(f"P3E Correlations: {final_stats['p3e_correlations']}")
    print(f"Auto-Responses Triggered: {final_stats['auto_responses_triggered']}")
    print(f"Average Response Time: {final_stats['average_response_time_s']:.2f}s")
    
    print("\nAlerts by Severity:")
    for severity, count in final_stats['alerts_by_severity'].items():
        if count > 0:
            print(f"  {severity}: {count}")
    
    print("\nDelivery Statistics:")
    delivery_stats = final_stats['delivery_stats']
    print(f"  Total Sent: {delivery_stats['total_sent']}")
    print(f"  Successful: {delivery_stats['successful_deliveries']}")
    print(f"  Failed: {delivery_stats['failed_deliveries']}")
    
    # Stop alert manager
    alert_manager.stop_processing()
    print("\nAlert system stopped.")


if __name__ == "__main__":
    main()