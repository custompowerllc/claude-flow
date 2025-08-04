#!/usr/bin/env python3
"""
Data Logger for Runaway Detection Validation - P3E Analysis Implementation

This module provides comprehensive data logging for runaway detection algorithm
validation against P3E analysis data. It captures all detection events, thermal
data, electrical measurements, and algorithm performance metrics for analysis
and improvement.

Key Features:
1. High-frequency data capture (1Hz minimum, configurable to 10Hz)
2. CSV export in P3E-compatible format
3. Real-time validation against P3E thresholds
4. Algorithm performance metrics
5. Historical trend analysis
6. Automated report generation
7. Integration with existing logging infrastructure

Data Formats:
- CSV: Compatible with P3E analysis tools
- JSON: Real-time API and webhook integration
- SQLite: Long-term storage and analysis
- Binary: High-frequency capture with compression
"""

import sys
import os
import logging
import time
import json
import csv
import sqlite3
import threading
import queue
import gzip
import struct
from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path

# Import logging system
try:
    from ..utils.log_manager import get_logger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

# Import algorithm components
try:
    from .runaway_detection import RunawayEvent, RunawayRiskLevel, RunawayDetector
    from .thermal_propagation import ThermalPropagationEvent, ThermalState, ThermalPropagationSimulator
    from .alert_system import Alert, AlertSeverity, AlertManager
    ALGORITHMS_AVAILABLE = True
except ImportError:
    ALGORITHMS_AVAILABLE = False


class LogLevel(Enum):
    """Data logging levels"""
    MINIMAL = 1      # Critical events only
    STANDARD = 2     # Standard operational data
    DETAILED = 3     # Detailed algorithm data
    VERBOSE = 4      # Full debug data
    RAW = 5         # Raw sensor data


class DataFormat(Enum):
    """Data export formats"""
    CSV = "csv"
    JSON = "json"
    SQLITE = "sqlite"
    BINARY = "binary"
    P3E_FORMAT = "p3e_csv"  # P3E analysis compatible CSV


@dataclass
class DataPoint:
    """Individual data point for logging"""
    timestamp: datetime
    session_id: str
    cell_voltages_mv: List[int]
    temperatures_dc: List[int]  # 0.1°C units
    current_ma: int
    soc_percent: int
    pack_delta_mv: int
    max_voltage_mv: int
    min_voltage_mv: int
    max_temperature_c: float
    avg_temperature_c: float
    runaway_risk_level: str
    thermal_state: str
    alert_count: int
    event_ids: List[str]
    p3e_correlation: str
    algorithm_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationMetrics:
    """Algorithm validation metrics"""
    session_id: str
    start_time: datetime
    end_time: datetime
    total_data_points: int
    detection_events: int
    false_positives: int
    false_negatives: int
    true_positives: int
    true_negatives: int
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    accuracy: float = 0.0
    p3e_correlation_accuracy: float = 0.0
    response_time_avg_s: float = 0.0
    threshold_violations: Dict[str, int] = field(default_factory=dict)
    thermal_events: int = 0
    alert_events: int = 0


class DataLogger:
    """
    Comprehensive data logger for runaway detection validation
    
    Captures all algorithm outputs, system states, and validation metrics
    for comparison against P3E analysis data and continuous improvement.
    """
    
    def __init__(self, log_directory: str = "data_logs", log_level: LogLevel = LogLevel.STANDARD):
        """Initialize data logger"""
        # Setup logging
        if LOGGING_AVAILABLE:
            self.logger = get_logger(__name__, 'data_logger')
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
        
        self.log_directory = Path(log_directory)
        self.log_level = log_level
        self.session_id = f"session_{int(time.time())}"
        
        # Create log directory
        self.log_directory.mkdir(exist_ok=True)
        
        # Data storage
        self.data_queue = queue.Queue()
        self.current_session_data: List[DataPoint] = []
        self.validation_metrics = ValidationMetrics(
            session_id=self.session_id,
            start_time=datetime.now(),
            end_time=datetime.now(),
            total_data_points=0,
            detection_events=0,
            false_positives=0,
            false_negatives=0,
            true_positives=0,
            true_negatives=0
        )
        
        # Algorithm references (set via integration)
        self.runaway_detector: Optional[RunawayDetector] = None
        self.thermal_simulator: Optional[ThermalPropagationSimulator] = None
        self.alert_manager: Optional[AlertManager] = None
        
        # Logging state
        self.logging_active = False
        self.sample_rate_hz = 1.0  # Default 1Hz
        self.csv_writer = None
        self.sqlite_connection = None
        
        # P3E validation thresholds
        self.p3e_thresholds = {
            'early_warning_mv': 100,
            'high_risk_mv': 300,
            'critical_mv': 500,
            'emergency_mv': 700,
            'catastrophic_mv': 1000,
            'thermal_warning_c': 35.0,
            'thermal_critical_c': 45.0,
            'thermal_runaway_c': 60.0
        }
        
        # Statistics
        self.stats = {
            'total_data_points': 0,
            'csv_records_written': 0,
            'json_records_written': 0,
            'sqlite_records_written': 0,
            'validation_sessions': 0,
            'p3e_correlations_found': 0,
            'algorithm_accuracy': 0.0
        }
        
        self.logger.info(f"DataLogger initialized: {self.log_directory}")
        self.logger.info(f"Session ID: {self.session_id}")
    
    def set_algorithm_references(self, runaway_detector: Optional[RunawayDetector] = None,
                                thermal_simulator: Optional[ThermalPropagationSimulator] = None,
                                alert_manager: Optional[AlertManager] = None) -> None:
        """Set references to algorithm components for integrated logging"""
        self.runaway_detector = runaway_detector
        self.thermal_simulator = thermal_simulator
        self.alert_manager = alert_manager
        
        self.logger.info("Algorithm references set for integrated logging")
    
    def start_logging(self, sample_rate_hz: float = 1.0, formats: List[DataFormat] = None) -> None:
        """Start data logging"""
        self.sample_rate_hz = sample_rate_hz
        self.logging_active = True
        self.validation_metrics.start_time = datetime.now()
        
        # Default formats
        if formats is None:
            formats = [DataFormat.CSV, DataFormat.JSON, DataFormat.SQLITE]
        
        # Initialize output formats
        for fmt in formats:
            self._initialize_format(fmt)
        
        # Start logging thread
        self._logging_thread = threading.Thread(target=self._logging_loop)
        self._logging_thread.daemon = True
        self._logging_thread.start()
        
        self.logger.info(f"Data logging started at {sample_rate_hz}Hz")
        self.logger.info(f"Formats: {[fmt.value for fmt in formats]}")
    
    def stop_logging(self) -> str:
        """Stop data logging and return session summary file"""
        self.logging_active = False
        self.validation_metrics.end_time = datetime.now()
        
        # Process remaining data
        self._process_remaining_data()
        
        # Finalize outputs
        self._finalize_formats()
        
        # Generate session summary
        summary_file = self._generate_session_summary()
        
        # Calculate final metrics
        self._calculate_validation_metrics()
        
        self.logger.info(f"Data logging stopped. Session: {self.session_id}")
        self.logger.info(f"Summary: {summary_file}")
        
        return summary_file
    
    def log_data_point(self, cell_voltages_mv: List[int], temperatures_dc: List[int],
                      current_ma: int, soc_percent: int, metadata: Dict[str, Any] = None) -> None:
        """Log a single data point"""
        if not self.logging_active:
            return
        
        # Calculate derived values
        pack_delta_mv = max(cell_voltages_mv) - min(cell_voltages_mv) if cell_voltages_mv else 0
        max_voltage_mv = max(cell_voltages_mv) if cell_voltages_mv else 0
        min_voltage_mv = min(cell_voltages_mv) if cell_voltages_mv else 0
        temperatures_c = [t / 10.0 for t in temperatures_dc]
        max_temp_c = max(temperatures_c) if temperatures_c else 25.0
        avg_temp_c = sum(temperatures_c) / len(temperatures_c) if temperatures_c else 25.0
        
        # Get algorithm states
        runaway_risk = "normal"
        thermal_state = "normal"
        alert_count = 0
        event_ids = []
        p3e_correlation = ""
        algorithm_metrics = {}
        
        if self.runaway_detector:
            status = self.runaway_detector.get_current_status()
            runaway_risk = status.get('current_risk_level', 'normal')
            alert_count += status.get('active_events', 0)
            algorithm_metrics.update({
                'runaway_detector': {
                    'total_events': status.get('total_events', 0),
                    'pack_delta_mv': status.get('pack_delta_mv', 0),
                    'shutdown_requested': status.get('shutdown_requested', False)
                }
            })
        
        if self.thermal_simulator:
            thermal_status = self.thermal_simulator.get_propagation_status()
            thermal_state = "normal"
            if max_temp_c >= 60.0:
                thermal_state = "runaway"
            elif max_temp_c >= 45.0:
                thermal_state = "critical"
            elif max_temp_c >= 35.0:
                thermal_state = "elevated"
            
            alert_count += thermal_status.get('recent_events', 0)
            algorithm_metrics.update({
                'thermal_simulator': {
                    'total_events': thermal_status.get('total_events', 0),
                    'max_temperature_c': thermal_status['current_status']['max_temperature_c'],
                    'runaway_cells': thermal_status['current_status']['runaway_cells']
                }
            })
        
        if self.alert_manager:
            alert_stats = self.alert_manager.get_alert_statistics()
            alert_count += alert_stats.get('active_alerts', 0)
            algorithm_metrics.update({
                'alert_manager': {
                    'total_alerts': alert_stats.get('total_alerts', 0),
                    'p3e_correlations': alert_stats.get('p3e_correlations', 0),
                    'auto_responses': alert_stats.get('auto_responses_triggered', 0)
                }
            })
        
        # Determine P3E correlation
        p3e_correlation = self._determine_p3e_correlation(pack_delta_mv, max_temp_c, current_ma)
        
        # Create data point
        data_point = DataPoint(
            timestamp=datetime.now(),
            session_id=self.session_id,
            cell_voltages_mv=cell_voltages_mv.copy(),
            temperatures_dc=temperatures_dc.copy(),
            current_ma=current_ma,
            soc_percent=soc_percent,
            pack_delta_mv=pack_delta_mv,
            max_voltage_mv=max_voltage_mv,
            min_voltage_mv=min_voltage_mv,
            max_temperature_c=max_temp_c,
            avg_temperature_c=avg_temp_c,
            runaway_risk_level=runaway_risk,
            thermal_state=thermal_state,
            alert_count=alert_count,
            event_ids=event_ids,
            p3e_correlation=p3e_correlation,
            algorithm_metrics=algorithm_metrics,
            metadata=metadata or {}
        )
        
        # Add to queue
        self.data_queue.put(data_point)
        self.stats['total_data_points'] += 1
        
        if p3e_correlation != "Normal operation":
            self.stats['p3e_correlations_found'] += 1
    
    def _determine_p3e_correlation(self, pack_delta_mv: int, max_temp_c: float, current_ma: int) -> str:
        """Determine P3E correlation based on current conditions"""
        correlations = []
        
        # Voltage-based correlations
        if pack_delta_mv >= 1000:
            correlations.append("Pack 0535: 1048mV catastrophic level")
        elif pack_delta_mv >= 700:
            correlations.append("Pack 0533: 702mV emergency level")
        elif pack_delta_mv >= 500:
            correlations.append("P3E critical threshold (500mV)")
        elif pack_delta_mv >= 300:
            correlations.append("Pack 0533: 300mV escalation point")
        elif pack_delta_mv >= 100:
            correlations.append("P3E early warning (100mV)")
        
        # Thermal correlations
        if max_temp_c >= 65.0:
            correlations.append("Pack 0535: 65°C thermal runaway")
        elif max_temp_c >= 60.0:
            correlations.append("P3E thermal runaway threshold")
        elif max_temp_c >= 45.0:
            correlations.append("P3E thermal critical zone")
        elif max_temp_c >= 35.0:
            correlations.append("P3E thermal elevated zone")
        
        # Current correlations
        if current_ma <= -5000:
            correlations.append("Pack 0533: -5.3A discharge pattern")
        
        return "; ".join(correlations) if correlations else "Normal operation"
    
    def _logging_loop(self) -> None:
        """Main logging loop"""
        sample_interval = 1.0 / self.sample_rate_hz
        
        while self.logging_active:
            loop_start = time.time()
            
            try:
                # Process queued data points
                self._process_data_queue()
                
                # Sleep for remaining interval
                elapsed = time.time() - loop_start
                sleep_time = max(0, sample_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Error in logging loop: {e}")
                time.sleep(1.0)
    
    def _process_data_queue(self) -> None:
        """Process all queued data points"""
        processed_count = 0
        
        while not self.data_queue.empty() and processed_count < 100:  # Batch processing
            try:
                data_point = self.data_queue.get_nowait()
                self._write_data_point(data_point)
                self.current_session_data.append(data_point)
                processed_count += 1
                
            except queue.Empty:
                break
            except Exception as e:
                self.logger.error(f"Error processing data point: {e}")
    
    def _write_data_point(self, data_point: DataPoint) -> None:
        """Write data point to all active formats"""
        try:
            # CSV format
            if self.csv_writer:
                self._write_csv_record(data_point)
            
            # JSON format
            self._write_json_record(data_point)
            
            # SQLite format
            if self.sqlite_connection:
                self._write_sqlite_record(data_point)
            
        except Exception as e:
            self.logger.error(f"Error writing data point: {e}")
    
    def _write_csv_record(self, data_point: DataPoint) -> None:
        """Write data point to CSV file"""
        if not self.csv_writer:
            return
        
        # Convert to P3E-compatible format
        row = {
            'timestamp': data_point.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'session_id': data_point.session_id,
            'pack_delta_mv': data_point.pack_delta_mv,
            'max_voltage_mv': data_point.max_voltage_mv,
            'min_voltage_mv': data_point.min_voltage_mv,
            'current_ma': data_point.current_ma,
            'soc_percent': data_point.soc_percent,
            'max_temperature_c': f"{data_point.max_temperature_c:.1f}",
            'avg_temperature_c': f"{data_point.avg_temperature_c:.1f}",
            'runaway_risk_level': data_point.runaway_risk_level,
            'thermal_state': data_point.thermal_state,
            'alert_count': data_point.alert_count,
            'p3e_correlation': data_point.p3e_correlation
        }
        
        # Add individual cell voltages
        for i, voltage in enumerate(data_point.cell_voltages_mv, 1):
            row[f'cell_{i}_voltage_mv'] = voltage
        
        # Add individual temperatures
        for i, temp in enumerate(data_point.temperatures_dc, 1):
            row[f'temp_{i}_dc'] = temp
        
        self.csv_writer.writerow(row)
        self.stats['csv_records_written'] += 1
    
    def _write_json_record(self, data_point: DataPoint) -> None:
        """Write data point to JSON file"""
        json_file = self.log_directory / f"{self.session_id}.json"
        
        with open(json_file, 'a') as f:
            json_data = asdict(data_point)
            json_data['timestamp'] = data_point.timestamp.isoformat()
            f.write(json.dumps(json_data) + '\n')
        
        self.stats['json_records_written'] += 1
    
    def _write_sqlite_record(self, data_point: DataPoint) -> None:
        """Write data point to SQLite database"""
        if not self.sqlite_connection:
            return
        
        cursor = self.sqlite_connection.cursor()
        
        # Insert main record
        cursor.execute("""
            INSERT INTO data_points (
                timestamp, session_id, pack_delta_mv, max_voltage_mv, min_voltage_mv,
                current_ma, soc_percent, max_temperature_c, avg_temperature_c,
                runaway_risk_level, thermal_state, alert_count, p3e_correlation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data_point.timestamp.isoformat(),
            data_point.session_id,
            data_point.pack_delta_mv,
            data_point.max_voltage_mv,
            data_point.min_voltage_mv,
            data_point.current_ma,
            data_point.soc_percent,
            data_point.max_temperature_c,
            data_point.avg_temperature_c,
            data_point.runaway_risk_level,
            data_point.thermal_state,
            data_point.alert_count,
            data_point.p3e_correlation
        ))
        
        record_id = cursor.lastrowid
        
        # Insert cell voltages
        for i, voltage in enumerate(data_point.cell_voltages_mv, 1):
            cursor.execute("""
                INSERT INTO cell_voltages (record_id, cell_id, voltage_mv)
                VALUES (?, ?, ?)
            """, (record_id, i, voltage))
        
        # Insert temperatures
        for i, temp in enumerate(data_point.temperatures_dc, 1):
            cursor.execute("""
                INSERT INTO temperatures (record_id, sensor_id, temperature_dc)
                VALUES (?, ?, ?)
            """, (record_id, i, temp))
        
        self.sqlite_connection.commit()
        self.stats['sqlite_records_written'] += 1
    
    def _initialize_format(self, fmt: DataFormat) -> None:
        """Initialize specific output format"""
        if fmt == DataFormat.CSV or fmt == DataFormat.P3E_FORMAT:
            self._initialize_csv_format()
        elif fmt == DataFormat.SQLITE:
            self._initialize_sqlite_format()
    
    def _initialize_csv_format(self) -> None:
        """Initialize CSV output format"""
        csv_file = self.log_directory / f"{self.session_id}_p3e_format.csv"
        
        # Define CSV headers based on P3E format
        headers = [
            'timestamp', 'session_id', 'pack_delta_mv', 'max_voltage_mv', 'min_voltage_mv',
            'current_ma', 'soc_percent', 'max_temperature_c', 'avg_temperature_c',
            'runaway_risk_level', 'thermal_state', 'alert_count', 'p3e_correlation'
        ]
        
        # Add cell voltage headers
        for i in range(1, 9):  # Assume 8 cells
            headers.append(f'cell_{i}_voltage_mv')
        
        # Add temperature headers
        for i in range(1, 9):  # Assume 8 temperature sensors
            headers.append(f'temp_{i}_dc')
        
        self.csv_file = open(csv_file, 'w', newline='')
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=headers)
        self.csv_writer.writeheader()
        
        self.logger.info(f"CSV format initialized: {csv_file}")
    
    def _initialize_sqlite_format(self) -> None:
        """Initialize SQLite database format"""
        db_file = self.log_directory / f"{self.session_id}.db"
        self.sqlite_connection = sqlite3.connect(str(db_file), check_same_thread=False)
        
        cursor = self.sqlite_connection.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE data_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                pack_delta_mv INTEGER,
                max_voltage_mv INTEGER,
                min_voltage_mv INTEGER,
                current_ma INTEGER,
                soc_percent INTEGER,
                max_temperature_c REAL,
                avg_temperature_c REAL,
                runaway_risk_level TEXT,
                thermal_state TEXT,
                alert_count INTEGER,
                p3e_correlation TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE cell_voltages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER,
                cell_id INTEGER,
                voltage_mv INTEGER,
                FOREIGN KEY (record_id) REFERENCES data_points (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE temperatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER,
                sensor_id INTEGER,
                temperature_dc INTEGER,
                FOREIGN KEY (record_id) REFERENCES data_points (id)
            )
        """)
        
        self.sqlite_connection.commit()
        
        self.logger.info(f"SQLite format initialized: {db_file}")
    
    def _process_remaining_data(self) -> None:
        """Process any remaining data in queue"""
        while not self.data_queue.empty():
            try:
                data_point = self.data_queue.get_nowait()
                self._write_data_point(data_point)
                self.current_session_data.append(data_point)
            except queue.Empty:
                break
    
    def _finalize_formats(self) -> None:
        """Finalize all output formats"""
        if self.csv_writer:
            self.csv_file.close()
            self.csv_writer = None
        
        if self.sqlite_connection:
            self.sqlite_connection.close()
            self.sqlite_connection = None
    
    def _generate_session_summary(self) -> str:
        """Generate session summary report"""
        summary_file = self.log_directory / f"{self.session_id}_summary.json"
        
        # Calculate session statistics
        session_duration = (self.validation_metrics.end_time - self.validation_metrics.start_time).total_seconds()
        
        # Analyze P3E correlations
        p3e_events = [dp for dp in self.current_session_data if dp.p3e_correlation != "Normal operation"]
        
        # Threshold violations
        threshold_violations = {}
        for threshold, value in self.p3e_thresholds.items():
            violations = 0
            for dp in self.current_session_data:
                if 'mv' in threshold and dp.pack_delta_mv >= value:
                    violations += 1
                elif 'c' in threshold and dp.max_temperature_c >= value:
                    violations += 1
            threshold_violations[threshold] = violations
        
        # Risk level distribution
        risk_distribution = {}
        for dp in self.current_session_data:
            risk = dp.runaway_risk_level
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
        
        summary = {
            'session_info': {
                'session_id': self.session_id,
                'start_time': self.validation_metrics.start_time.isoformat(),
                'end_time': self.validation_metrics.end_time.isoformat(),
                'duration_seconds': session_duration,
                'sample_rate_hz': self.sample_rate_hz
            },
            'data_statistics': {
                'total_data_points': len(self.current_session_data),
                'csv_records': self.stats['csv_records_written'],
                'json_records': self.stats['json_records_written'],
                'sqlite_records': self.stats['sqlite_records_written']
            },
            'p3e_analysis': {
                'total_correlations': len(p3e_events),
                'correlation_rate': len(p3e_events) / max(len(self.current_session_data), 1) * 100,
                'threshold_violations': threshold_violations,
                'unique_correlations': list(set([dp.p3e_correlation for dp in p3e_events]))
            },
            'algorithm_performance': {
                'risk_distribution': risk_distribution,
                'max_delta_detected': max([dp.pack_delta_mv for dp in self.current_session_data], default=0),
                'max_temperature_detected': max([dp.max_temperature_c for dp in self.current_session_data], default=0),
                'total_alerts': sum([dp.alert_count for dp in self.current_session_data])
            },
            'validation_metrics': asdict(self.validation_metrics),
            'recommendations': self._generate_recommendations()
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Session summary generated: {summary_file}")
        return str(summary_file)
    
    def _calculate_validation_metrics(self) -> None:
        """Calculate detailed validation metrics"""
        if not self.current_session_data:
            return
        
        # Update basic counts
        self.validation_metrics.total_data_points = len(self.current_session_data)
        
        # P3E correlation accuracy
        p3e_events = [dp for dp in self.current_session_data if dp.p3e_correlation != "Normal operation"]
        self.validation_metrics.p3e_correlation_accuracy = len(p3e_events) / len(self.current_session_data) * 100
        
        # Threshold violations
        violations = {}
        for threshold, value in self.p3e_thresholds.items():
            count = 0
            for dp in self.current_session_data:
                if 'mv' in threshold and dp.pack_delta_mv >= value:
                    count += 1
                elif 'c' in threshold and dp.max_temperature_c >= value:
                    count += 1
            violations[threshold] = count
        
        self.validation_metrics.threshold_violations = violations
        
        # Calculate response times (placeholder - would need actual response data)
        response_times = []  # Would be populated from actual response data
        self.validation_metrics.response_time_avg_s = sum(response_times) / len(response_times) if response_times else 0.0
        
        # Count events
        self.validation_metrics.detection_events = sum([dp.alert_count for dp in self.current_session_data])
        self.validation_metrics.thermal_events = len([dp for dp in self.current_session_data if dp.thermal_state != "normal"])
        self.validation_metrics.alert_events = len([dp for dp in self.current_session_data if dp.alert_count > 0])
        
        self.logger.info("Validation metrics calculated")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on logged data"""
        recommendations = []
        
        if not self.current_session_data:
            return ["No data available for analysis"]
        
        # Analyze maximum values
        max_delta = max([dp.pack_delta_mv for dp in self.current_session_data])
        max_temp = max([dp.max_temperature_c for dp in self.current_session_data])
        
        # Delta-based recommendations
        if max_delta >= 1000:
            recommendations.append("CRITICAL: Pack 0535 level delta detected - implement emergency protocols")
        elif max_delta >= 700:
            recommendations.append("EMERGENCY: Pack 0533 level delta detected - review emergency response")
        elif max_delta >= 500:
            recommendations.append("HIGH RISK: Critical threshold exceeded - enhance monitoring")
        elif max_delta >= 300:
            recommendations.append("MODERATE RISK: High-risk threshold exceeded - implement preventive measures")
        elif max_delta >= 100:
            recommendations.append("LOW RISK: Early warning threshold exceeded - increase monitoring frequency")
        
        # Temperature-based recommendations
        if max_temp >= 65.0:
            recommendations.append("THERMAL CRITICAL: Pack 0535 thermal level - emergency cooling required")
        elif max_temp >= 60.0:
            recommendations.append("THERMAL RUNAWAY: Implement thermal emergency protocols")
        elif max_temp >= 45.0:
            recommendations.append("THERMAL HIGH: Activate enhanced cooling systems")
        elif max_temp >= 35.0:
            recommendations.append("THERMAL ELEVATED: Monitor thermal trends closely")
        
        # P3E correlation recommendations
        p3e_events = len([dp for dp in self.current_session_data if dp.p3e_correlation != "Normal operation"])
        if p3e_events > len(self.current_session_data) * 0.1:  # >10% P3E correlations
            recommendations.append("HIGH P3E CORRELATION: Implement proven P3E mitigation strategies")
        
        # Algorithm performance
        if self.stats['p3e_correlations_found'] > 0:
            recommendations.append("P3E patterns detected - validate against historical P3E data")
        
        if not recommendations:
            recommendations.append("Normal operation detected - continue standard monitoring")
        
        return recommendations
    
    def export_p3e_compatible_data(self, output_file: str = None) -> str:
        """Export data in P3E analysis compatible format"""
        if output_file is None:
            output_file = str(self.log_directory / f"{self.session_id}_p3e_export.csv")
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # P3E-compatible headers
            headers = [
                'timestamp', 'elapsed_time_s', 'pack_delta_mv', 'current_ma', 'soc_percent',
                'max_temperature_c', 'cell_1_mv', 'cell_2_mv', 'cell_3_mv', 'cell_4_mv',
                'cell_5_mv', 'cell_6_mv', 'cell_7_mv', 'cell_8_mv', 'event_type',
                'p3e_correlation', 'risk_level'
            ]
            writer.writerow(headers)
            
            # Data rows
            start_time = self.current_session_data[0].timestamp if self.current_session_data else datetime.now()
            
            for dp in self.current_session_data:
                elapsed_time = (dp.timestamp - start_time).total_seconds()
                
                row = [
                    dp.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                    f"{elapsed_time:.3f}",
                    dp.pack_delta_mv,
                    dp.current_ma,
                    dp.soc_percent,
                    f"{dp.max_temperature_c:.1f}"
                ]
                
                # Add cell voltages (pad to 8 cells)
                cell_voltages = dp.cell_voltages_mv + [0] * (8 - len(dp.cell_voltages_mv))
                row.extend(cell_voltages[:8])
                
                # Add event information
                if dp.pack_delta_mv >= 700:
                    event_type = "emergency"
                elif dp.pack_delta_mv >= 500:
                    event_type = "critical"
                elif dp.pack_delta_mv >= 300:
                    event_type = "high_risk"
                elif dp.pack_delta_mv >= 100:
                    event_type = "warning"
                else:
                    event_type = "normal"
                
                row.extend([event_type, dp.p3e_correlation, dp.runaway_risk_level])
                
                writer.writerow(row)
        
        self.logger.info(f"P3E compatible export created: {output_file}")
        return output_file
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return {
            'session_id': self.session_id,
            'logging_active': self.logging_active,
            'sample_rate_hz': self.sample_rate_hz,
            'data_points_logged': len(self.current_session_data),
            'queue_size': self.data_queue.qsize(),
            'statistics': self.stats.copy(),
            'validation_metrics': asdict(self.validation_metrics),
            'p3e_thresholds': self.p3e_thresholds.copy(),
            'log_directory': str(self.log_directory)
        }


def main():
    """Test function for data logger"""
    # Setup logging
    if LOGGING_AVAILABLE:
        from ..utils.log_manager import setup_logging
        setup_logging(level='INFO')
        logger = get_logger(__name__, 'data_logger')
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
    
    print("=== P3E Data Logger Test ===")
    
    # Create data logger
    data_logger = DataLogger(log_directory="test_logs", log_level=LogLevel.DETAILED)
    
    # Start logging
    formats = [DataFormat.CSV, DataFormat.JSON, DataFormat.SQLITE]
    data_logger.start_logging(sample_rate_hz=2.0, formats=formats)
    
    print(f"Data logging started at 2Hz")
    print(f"Session ID: {data_logger.session_id}")
    
    # Simulate P3E test scenarios
    test_scenarios = [
        {
            'name': 'Normal Operation',
            'duration': 5.0,
            'cell_voltages': [3700, 3705, 3698, 3702, 3701, 3699, 3703, 3697],
            'temperatures': [250, 252, 251, 249, 253, 250, 251, 252],
            'current': 0,
            'soc': 50
        },
        {
            'name': 'P3E Early Warning (120mV)',
            'duration': 3.0,
            'cell_voltages': [3700, 3705, 3698, 3702, 3701, 3580, 3703, 3697],  # 125mV delta
            'temperatures': [280, 285, 283, 281, 287, 280, 284, 282],
            'current': -1000,
            'soc': 65
        },
        {
            'name': 'P3E Pack 0533 Pattern (350mV)',
            'duration': 4.0,
            'cell_voltages': [3700, 3705, 3698, 3702, 3701, 3350, 3703, 3697],  # 355mV delta
            'temperatures': [305, 310, 308, 306, 312, 305, 309, 307],
            'current': -5300,
            'soc': 45
        },
        {
            'name': 'P3E Critical (550mV)',
            'duration': 2.0,
            'cell_voltages': [3700, 3705, 3698, 3702, 3701, 3150, 3703, 3697],  # 555mV delta
            'temperatures': [350, 355, 353, 351, 357, 350, 354, 352],
            'current': -5300,
            'soc': 35
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n--- Scenario {i+1}: {scenario['name']} ---")
        
        start_time = time.time()
        while (time.time() - start_time) < scenario['duration']:
            # Add some variation to the data
            variation = (time.time() - start_time) / scenario['duration'] * 0.1
            
            cell_voltages = [int(v + v * variation * 0.001) for v in scenario['cell_voltages']]
            temperatures = [int(t + t * variation * 0.002) for t in scenario['temperatures']]
            current = int(scenario['current'] + scenario['current'] * variation * 0.05)
            soc = max(0, int(scenario['soc'] - variation * 10))
            
            # Log data point
            data_logger.log_data_point(
                cell_voltages_mv=cell_voltages,
                temperatures_dc=temperatures,
                current_ma=current,
                soc_percent=soc,
                metadata={'scenario': scenario['name'], 'test_phase': i+1}
            )
            
            time.sleep(0.3)  # ~3Hz data rate
        
        # Show current statistics
        stats = data_logger.get_session_statistics()
        print(f"Data points logged: {stats['data_points_logged']}")
        print(f"P3E correlations found: {stats['statistics']['p3e_correlations_found']}")
    
    # Stop logging and generate summary
    print("\n=== Stopping Data Logger ===")
    summary_file = data_logger.stop_logging()
    
    # Export P3E compatible data
    p3e_export = data_logger.export_p3e_compatible_data()
    
    print(f"Session summary: {summary_file}")
    print(f"P3E export: {p3e_export}")
    
    # Show final statistics
    final_stats = data_logger.get_session_statistics()
    print(f"\nFinal Statistics:")
    print(f"  Total data points: {final_stats['data_points_logged']}")
    print(f"  CSV records: {final_stats['statistics']['csv_records_written']}")
    print(f"  JSON records: {final_stats['statistics']['json_records_written']}")
    print(f"  SQLite records: {final_stats['statistics']['sqlite_records_written']}")
    print(f"  P3E correlations: {final_stats['statistics']['p3e_correlations_found']}")


if __name__ == "__main__":
    main()