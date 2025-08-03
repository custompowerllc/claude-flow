/**
 * TypeScript interfaces for BK9206B power supply integration
 * 
 * This module provides comprehensive type definitions for all WebSocket
 * message types, device status structures, command formats, monitoring
 * events, charge controller interfaces, error responses, and configuration
 * objects used in the BK9206B power supply control system.
 */

// ========================================
// Core Enums
// ========================================

/**
 * Power supply operating modes
 */
export enum OperatingMode {
  CV = "CV",    // Constant Voltage
  CC = "CC",    // Constant Current
  OFF = "OFF"   // Output disabled
}

/**
 * Charge controller operation modes
 */
export enum ChargeOperationMode {
  MANUAL = "MANUAL",  // Standard power supply operation
  CHARGE = "CHARGE"   // Battery charging operation
}

/**
 * Charge controller states
 */
export enum ChargeState {
  IDLE = "IDLE",
  CC_CHARGING = "CC_CHARGING",
  CV_CHARGING = "CV_CHARGING", 
  TERMINATED = "TERMINATED",
  ERROR = "ERROR",
  PAUSED = "PAUSED"
}

/**
 * WebSocket message types from server
 */
export enum WebSocketMessageType {
  // Connection management
  CONNECTION = "connection",
  PONG = "pong",
  ERROR = "error",
  
  // Status and data
  STATUS = "status",
  CONFIG = "config",
  CHARGE_STATUS = "charge_status",
  
  // Events
  MONITORING_EVENT = "monitoring_event",
  TAPER_EVENT = "taper_event",
  CHARGE_EVENT = "charge_event",
  
  // Responses
  CHARGE_RESPONSE = "charge_response",
  OPERATION_MODE_RESPONSE = "operation_mode_response",
  
  // Subscriptions
  SUBSCRIBED = "subscribed",
  UNSUBSCRIBED = "unsubscribed",
  
  // Broadcasting
  BROADCAST = "broadcast"
}

/**
 * WebSocket message types for client requests
 */
export enum WebSocketRequestType {
  PING = "ping",
  GET_STATUS = "get_status",
  GET_CONFIG = "get_config",
  SUBSCRIBE = "subscribe",
  UNSUBSCRIBE = "unsubscribe",
  START_CHARGE = "start_charge",
  STOP_CHARGE = "stop_charge",
  PAUSE_CHARGE = "pause_charge",
  RESUME_CHARGE = "resume_charge",
  GET_CHARGE_STATUS = "get_charge_status",
  SET_OPERATION_MODE = "set_operation_mode"
}

// ========================================
// Base Interfaces
// ========================================

/**
 * Base timestamp interface for all time-related data
 */
export interface TimestampedData {
  timestamp: string; // ISO datetime string
}

/**
 * Base WebSocket message structure
 */
export interface BaseWebSocketMessage extends TimestampedData {
  type: string;
  data: Record<string, any>;
}

// ========================================
// Device Status Interfaces
// ========================================

/**
 * Complete device status response structure
 */
export interface DeviceStatusResponse extends TimestampedData {
  voltage_set: number;        // Set voltage in volts
  current_set: number;        // Set current limit in amperes
  voltage_actual: number;     // Measured voltage in volts
  current_actual: number;     // Measured current in amperes
  power_actual: number;       // Measured power in watts
  output_enabled: boolean;    // Output state
  operating_mode: OperatingMode; // Current operating mode
  device_id: string;          // Device identification string
}

/**
 * Taper current configuration response
 */
export interface TaperConfigResponse {
  threshold: number;          // Current taper threshold in amperes
  duration: number;           // Taper duration in seconds
  enabled: boolean;           // Whether taper current detection is enabled
  last_triggered?: string;    // Last time taper was triggered (ISO datetime)
}

/**
 * Server health response structure
 */
export interface HealthResponse {
  server_status: string;              // Server health status
  device_connected: boolean;          // Device connection status
  device_ready: boolean;              // Device ready status
  uptime_seconds: number;             // Server uptime in seconds
  monitoring_active: boolean;         // Whether monitoring loop is active
  last_device_communication?: string; // Last successful device communication (ISO datetime)
}

// ========================================
// Command Request/Response Interfaces
// ========================================

/**
 * Voltage setting request
 */
export interface VoltageRequest {
  voltage: number; // Output voltage in volts (0-60V)
}

/**
 * Current setting request
 */
export interface CurrentRequest {
  current: number; // Current limit in amperes (0-5A)
}

/**
 * Taper threshold setting request
 */
export interface TaperThresholdRequest {
  threshold: number; // Taper current threshold in amperes
}

/**
 * Taper duration setting request
 */
export interface TaperDurationRequest {
  duration: number; // Taper duration in seconds (1-3600s)
}

/**
 * Operation mode setting request
 */
export interface OperationModeRequest {
  mode: ChargeOperationMode;
}

/**
 * Charge start parameters
 */
export interface ChargeStartParams {
  charge_current: number;       // Charging current in amperes
  charge_voltage: number;       // Target charge voltage in volts
  taper_threshold: number;      // Current taper threshold in amperes
  max_charge_time?: number;     // Maximum charge time in minutes (default: 180)
}

/**
 * Generic success response
 */
export interface SuccessResponse extends TimestampedData {
  success: boolean;
  message: string;
}

/**
 * Charge operation response
 */
export interface ChargeResponse {
  success: boolean;
  error?: string;
}

/**
 * Operation mode change response
 */
export interface OperationModeResponse {
  success: boolean;
  mode: ChargeOperationMode;
  message: string;
}

// ========================================
// Error Response Interfaces
// ========================================

/**
 * Standard error response format
 */
export interface ErrorResponse extends TimestampedData {
  error: string;        // Error message
  detail?: string;      // Detailed error information
}

/**
 * WebSocket error message data
 */
export interface WebSocketErrorData {
  message: string;
}

// ========================================
// Monitoring Event Interfaces
// ========================================

/**
 * Monitoring event data structure
 */
export interface MonitoringEvent extends TimestampedData {
  event_type: string;                    // Type of monitoring event
  voltage: number;                       // Voltage at time of event
  current: number;                       // Current at time of event
  power: number;                         // Power at time of event
  operating_mode: OperatingMode;         // Operating mode at time of event
  details?: Record<string, any>;        // Additional event details
}

/**
 * Taper current event data
 */
export interface TaperEvent extends TimestampedData {
  triggered: boolean;       // Whether taper was triggered
  threshold: number;        // Taper threshold that was checked
  current_value: number;    // Current value when checked
  duration_met: boolean;    // Whether duration requirement was met
  output_disabled: boolean; // Whether output was automatically disabled
}

// ========================================
// Charge Controller Interfaces
// ========================================

/**
 * Charge controller status
 */
export interface ChargeControllerStatus {
  operation_mode: ChargeOperationMode;
  state: ChargeState;
  charge_params: ChargeStartParams;
  elapsed_time: string;             // Duration string (HH:MM:SS)
  energy_delivered: number;         // Energy delivered in Wh
  start_time?: string;              // Charge start time (ISO datetime)
  can_use_manual_controls: boolean;
  is_charge_mode_active: boolean;
}

/**
 * Charge event data
 */
export interface ChargeEventData extends TimestampedData {
  event_type: string;               // Type of charge event
  data: Record<string, any>;        // Event-specific data
}

/**
 * Charge progress data
 */
export interface ChargeProgressData {
  state: ChargeState;
  elapsed_time: string;             // Duration string (HH:MM:SS)
  energy_delivered: number;         // Energy delivered in Wh
  charge_params: ChargeStartParams;
}

/**
 * Charge termination summary
 */
export interface ChargeTerminationSummary {
  reason: string;                   // Termination reason
  duration: string;                 // Total charge duration (HH:MM:SS)
  energy_delivered: number;         // Total energy delivered in Wh
}

/**
 * Phase transition data
 */
export interface PhaseTransitionData {
  from: string;                     // Previous charge phase
  to: string;                       // New charge phase
}

// ========================================
// WebSocket Message Interfaces
// ========================================

/**
 * Generic WebSocket message from server
 */
export interface WebSocketMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType;
}

/**
 * WebSocket connection message
 */
export interface ConnectionMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.CONNECTION;
  data: {
    status: string;
    connection_id: number;
    server_time: string;
  };
}

/**
 * WebSocket pong response
 */
export interface PongMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.PONG;
  data: {
    timestamp: string;
  };
}

/**
 * WebSocket status message
 */
export interface StatusMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.STATUS;
  data: DeviceStatusResponse;
}

/**
 * WebSocket config message
 */
export interface ConfigMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.CONFIG;
  data: TaperConfigResponse;
}

/**
 * WebSocket charge status message
 */
export interface ChargeStatusMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.CHARGE_STATUS;
  data: {
    status: ChargeControllerStatus;
  };
}

/**
 * WebSocket monitoring event message
 */
export interface MonitoringEventMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.MONITORING_EVENT;
  data: MonitoringEvent;
}

/**
 * WebSocket taper event message
 */
export interface TaperEventMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.TAPER_EVENT;
  data: TaperEvent;
}

/**
 * WebSocket charge event message
 */
export interface ChargeEventMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.CHARGE_EVENT;
  data: ChargeEventData;
}

/**
 * WebSocket error message
 */
export interface ErrorMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.ERROR;
  data: WebSocketErrorData;
}

/**
 * WebSocket charge response message
 */
export interface ChargeResponseMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.CHARGE_RESPONSE;
  data: ChargeResponse;
}

/**
 * WebSocket operation mode response message
 */
export interface OperationModeResponseMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.OPERATION_MODE_RESPONSE;
  data: OperationModeResponse;
}

/**
 * WebSocket subscription confirmation message
 */
export interface SubscriptionMessage extends BaseWebSocketMessage {
  type: WebSocketMessageType.SUBSCRIBED | WebSocketMessageType.UNSUBSCRIBED;
  data: {
    events: string[];
    message: string;
  };
}

// ========================================
// Client Request Interfaces
// ========================================

/**
 * Client WebSocket request message
 */
export interface ClientWebSocketMessage {
  type: WebSocketRequestType;
  [key: string]: any;
}

/**
 * Ping request
 */
export interface PingRequest extends ClientWebSocketMessage {
  type: WebSocketRequestType.PING;
}

/**
 * Status request
 */
export interface StatusRequest extends ClientWebSocketMessage {
  type: WebSocketRequestType.GET_STATUS;
}

/**
 * Config request
 */
export interface ConfigRequest extends ClientWebSocketMessage {
  type: WebSocketRequestType.GET_CONFIG;
}

/**
 * Subscription request
 */
export interface SubscribeRequest extends ClientWebSocketMessage {
  type: WebSocketRequestType.SUBSCRIBE;
  events: string[];
}

/**
 * Unsubscription request
 */
export interface UnsubscribeRequest extends ClientWebSocketMessage {
  type: WebSocketRequestType.UNSUBSCRIBE;
  events: string[];
}

/**
 * Start charge request
 */
export interface StartChargeRequest extends ClientWebSocketMessage {
  type: WebSocketRequestType.START_CHARGE;
  params: ChargeStartParams;
}

/**
 * Stop charge request
 */
export interface StopChargeRequest extends ClientWebSocketMessage {
  type: WebSocketRequestType.STOP_CHARGE;
}

/**
 * Pause charge request
 */
export interface PauseChargeRequest extends ClientWebSocketMessage {
  type: WebSocketRequestType.PAUSE_CHARGE;
}

/**
 * Resume charge request
 */
export interface ResumeChargeRequest extends ClientWebSocketMessage {
  type: WebSocketRequestType.RESUME_CHARGE;
}

/**
 * Get charge status request
 */
export interface GetChargeStatusRequest extends ClientWebSocketMessage {
  type: WebSocketRequestType.GET_CHARGE_STATUS;
}

/**
 * Set operation mode request
 */
export interface SetOperationModeRequest extends ClientWebSocketMessage {
  type: WebSocketRequestType.SET_OPERATION_MODE;
  mode: ChargeOperationMode;
}

// ========================================
// Configuration Interfaces
// ========================================

/**
 * Device configuration object
 */
export interface DeviceConfig {
  voltage_min: number;              // Minimum voltage (V)
  voltage_max: number;              // Maximum voltage (V)
  current_min: number;              // Minimum current (A)
  current_max: number;              // Maximum current (A)
  voltage_precision: number;        // Voltage precision (decimal places)
  current_precision: number;        // Current precision (decimal places)
  monitoring_interval: number;      // Monitoring interval (seconds)
}

/**
 * Server configuration object
 */
export interface ServerConfig {
  host: string;                     // Server host address
  port: number;                     // Server port
  websocket_path: string;           // WebSocket endpoint path
  api_prefix: string;               // REST API prefix
  cors_enabled: boolean;            // CORS support enabled
  debug_mode: boolean;              // Debug logging enabled
}

/**
 * Application configuration object
 */
export interface AppConfig {
  device: DeviceConfig;
  server: ServerConfig;
  taper_config: TaperConfigResponse;
}

// ========================================
// Connection Statistics
// ========================================

/**
 * WebSocket connection statistics
 */
export interface ConnectionStats {
  active_connections: number;
  total_connections: number;
  connection_ids: number[];
  subscriptions: Record<number, string[]>;
}

// ========================================
// Union Types for Type Guards
// ========================================

/**
 * All possible server WebSocket message types
 */
export type ServerWebSocketMessage = 
  | ConnectionMessage
  | PongMessage
  | StatusMessage
  | ConfigMessage
  | ChargeStatusMessage
  | MonitoringEventMessage
  | TaperEventMessage
  | ChargeEventMessage
  | ErrorMessage
  | ChargeResponseMessage
  | OperationModeResponseMessage
  | SubscriptionMessage;

/**
 * All possible client WebSocket request types
 */
export type ClientWebSocketRequest =
  | PingRequest
  | StatusRequest
  | ConfigRequest
  | SubscribeRequest
  | UnsubscribeRequest
  | StartChargeRequest
  | StopChargeRequest
  | PauseChargeRequest
  | ResumeChargeRequest
  | GetChargeStatusRequest
  | SetOperationModeRequest;

// ========================================
// Type Guards
// ========================================

/**
 * Type guard for server WebSocket messages
 */
export function isServerWebSocketMessage(msg: any): msg is ServerWebSocketMessage {
  return msg && typeof msg === 'object' && 'type' in msg && 'data' in msg && 'timestamp' in msg;
}

/**
 * Type guard for client WebSocket requests
 */
export function isClientWebSocketRequest(msg: any): msg is ClientWebSocketRequest {
  return msg && typeof msg === 'object' && 'type' in msg && Object.values(WebSocketRequestType).includes(msg.type);
}

/**
 * Type guard for error messages
 */
export function isErrorMessage(msg: ServerWebSocketMessage): msg is ErrorMessage {
  return msg.type === WebSocketMessageType.ERROR;
}

/**
 * Type guard for status messages
 */
export function isStatusMessage(msg: ServerWebSocketMessage): msg is StatusMessage {
  return msg.type === WebSocketMessageType.STATUS;
}

/**
 * Type guard for charge event messages
 */
export function isChargeEventMessage(msg: ServerWebSocketMessage): msg is ChargeEventMessage {
  return msg.type === WebSocketMessageType.CHARGE_EVENT;
}

/**
 * Type guard for monitoring event messages
 */
export function isMonitoringEventMessage(msg: ServerWebSocketMessage): msg is MonitoringEventMessage {
  return msg.type === WebSocketMessageType.MONITORING_EVENT;
}

/**
 * Type guard for taper event messages
 */
export function isTaperEventMessage(msg: ServerWebSocketMessage): msg is TaperEventMessage {
  return msg.type === WebSocketMessageType.TAPER_EVENT;
}