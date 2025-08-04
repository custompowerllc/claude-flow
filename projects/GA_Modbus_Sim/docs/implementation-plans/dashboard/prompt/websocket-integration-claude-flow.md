# WebSocket Integration Implementation Prompt - Claude Flow Parallel Agents

## 🚀 Implementation Overview

This prompt orchestrates the implementation of WebSocket communication between the GA Modbus Simulator's standalone logger and dashboard using Claude Flow's parallel agent coordination system.

### Project Context
- **Current State**: CSV file-based communication with polling
- **Target State**: Real-time WebSocket communication with CSV fallback
- **Key Files**:
  - `projects/GA_Modbus_Sim/src/modbus_standalone_logger.py`
  - `projects/GA_Modbus_Sim/src/modbus_dashboard.py`

## 🐝 Swarm Configuration

```bash
# Initialize swarm with 8 specialized agents for WebSocket implementation
npx claude-flow@alpha --agents 8 --topology hierarchical --strategy parallel
```

### Agent Roles & Responsibilities

1. **🏗️ Architecture Agent** (Type: `architecture`)
   - Design WebSocket server/client architecture
   - Define message protocol and data structures
   - Create integration patterns for logger and dashboard
   - Coordinate with other agents on design decisions

2. **💻 Server Implementation Agent** (Type: `coder`)
   - Implement WebSocket server in `modbus_standalone_logger.py`
   - Create WebSocketBroadcaster class
   - Integrate with existing Modbus reading logic
   - Maintain CSV logging alongside WebSocket

3. **🖥️ Client Implementation Agent** (Type: `coder`)
   - Implement WebSocket client in `modbus_dashboard.py`
   - Create WebSocketDataSource class
   - Build DataSourceManager for fallback handling
   - Update dashboard UI for connection status

4. **📡 Protocol Implementation Agent** (Type: `coder`)
   - Implement JSON message serialization/deserialization
   - Create message types (data, status, error, config)
   - Add sequence numbers and timestamps
   - Handle message compression and batching

5. **🛡️ Error Handling Agent** (Type: `perf-analyzer`)
   - Design connection failure recovery mechanisms
   - Implement automatic reconnection with exponential backoff
   - Create CSV fallback activation logic
   - Add connection quality monitoring

6. **🧪 Testing Agent** (Type: `tester`)
   - Create unit tests for WebSocket components
   - Design integration tests for end-to-end flow
   - Build performance benchmarks
   - Test fallback mechanisms

7. **⚙️ Configuration Agent** (Type: `coder`)
   - Update TOML configuration for WebSocket settings
   - Add command-line arguments for WebSocket options
   - Create deployment configurations
   - Document configuration options

8. **📊 Coordinator Agent** (Type: `task-orchestrator`)
   - Monitor implementation progress
   - Ensure component integration
   - Validate against requirements
   - Coordinate agent communications

## 📋 Implementation Tasks

### Phase 1: Foundation Setup (Parallel Execution)

**All agents work simultaneously on their domains:**

```javascript
// Coordinator initializes shared memory for agent coordination
Task("coordinator", "Initialize shared memory with WebSocket specs and coordinate all agents", "task-orchestrator")

// Architecture design in parallel with initial implementations
Task("architect", "Design WebSocket architecture and message protocol. Store decisions in memory.", "architecture")

// Server and client skeleton creation
Task("server-coder", "Create WebSocketBroadcaster class skeleton in logger", "coder")
Task("client-coder", "Create WebSocketDataSource class skeleton in dashboard", "coder")

// Protocol and configuration prep
Task("protocol-coder", "Define JSON message structures and create protocol module", "coder")
Task("config-coder", "Prepare TOML configuration schema for WebSocket settings", "coder")

// Testing and error handling frameworks
Task("tester", "Set up test framework and create test structure", "tester")
Task("analyst", "Design error handling patterns and recovery strategies", "perf-analyzer")
```

### Phase 2: Core Implementation (Coordinated Development)

```javascript
// All agents implement their components with continuous coordination
Task("server-coder", "Implement WebSocket server with broadcasting, client management, and message queuing", "coder")
Task("client-coder", "Implement WebSocket client with connection management and data callbacks", "coder")
Task("protocol-coder", "Implement message serialization, compression, and batching", "coder")
Task("config-coder", "Integrate WebSocket configuration into both logger and dashboard", "coder")
Task("analyst", "Implement reconnection logic and fallback mechanisms", "perf-analyzer")
Task("tester", "Create unit tests for all WebSocket components", "tester")
```

### Phase 3: Integration & Testing

```javascript
// Parallel integration and comprehensive testing
Task("coordinator", "Coordinate integration testing across all components", "task-orchestrator")
Task("server-coder", "Integrate WebSocket server with Modbus data flow", "coder")
Task("client-coder", "Update dashboard to use DataSourceManager with fallback", "coder")
Task("tester", "Execute integration tests and performance benchmarks", "tester")
Task("analyst", "Validate error handling and recovery mechanisms", "perf-analyzer")
```

## 📐 Technical Specifications

### WebSocket Message Protocol

```json
{
  "type": "data|status|error|config",
  "timestamp": "ISO 8601 timestamp",
  "sequence": 12345,
  "payload": {
    // Type-specific payload
  }
}
```

### Data Message Example
```json
{
  "type": "data",
  "timestamp": "2025-08-03T20:42:55.123456",
  "sequence": 12345,
  "payload": {
    "afe_cell_volt1": 3245,
    "afe_cell_volt2": 3248,
    "afe_pack_volt": 25984,
    "afe_current": -1250,
    "fg_current": -1248,
    "fg_state_of_charge": 87,
    "afe_temp1": 3030
  }
}
```

### Connection Management
- WebSocket server on port 8765 (configurable)
- Automatic reconnection with exponential backoff
- Maximum 30 reconnection attempts
- CSV fallback on connection failure
- Message history buffer for reconnecting clients

## 🔄 Agent Coordination Protocol

### Memory Keys for Coordination
```javascript
// Architecture decisions
"websocket/architecture/server-design"
"websocket/architecture/client-design"
"websocket/architecture/protocol-spec"

// Implementation progress
"websocket/implementation/server-status"
"websocket/implementation/client-status"
"websocket/implementation/protocol-status"

// Testing results
"websocket/testing/unit-test-results"
"websocket/testing/integration-results"
"websocket/testing/performance-metrics"

// Issues and resolutions
"websocket/issues/blockers"
"websocket/issues/resolved"
```

### Coordination Hooks
```bash
# Before starting any implementation
npx claude-flow@alpha hooks pre-task --description "WebSocket [component]" --auto-spawn-agents false

# After completing each major step
npx claude-flow@alpha hooks post-edit --file "[file]" --memory-key "websocket/[agent]/[step]"

# For cross-agent coordination
npx claude-flow@alpha hooks notify --message "[decision/update]" --telemetry true

# After completing agent task
npx claude-flow@alpha hooks post-task --task-id "websocket-[component]" --analyze-performance true
```

## 🎯 Success Criteria

### Performance Metrics
- Data transmission latency < 10ms
- Support for 5+ concurrent dashboard connections
- CPU usage reduction > 20% compared to CSV polling
- Memory usage increase < 50MB
- Zero data loss during normal operation

### Functionality Requirements
- ✅ Real-time data transmission via WebSocket
- ✅ Automatic fallback to CSV on connection failure
- ✅ Multiple dashboard support
- ✅ Connection status visualization
- ✅ Backward compatibility with CSV-only mode
- ✅ Configurable WebSocket settings
- ✅ Comprehensive error handling

### Code Quality Standards
- Unit test coverage > 80%
- Integration tests for all scenarios
- Performance benchmarks documented
- Configuration examples provided
- User documentation complete

## 📝 Implementation Execution

### Starting the Implementation

```bash
# 1. Initialize Claude Flow swarm
npx claude-flow@alpha sparc run swarm-init "WebSocket integration for GA Modbus Simulator"

# 2. Execute this prompt with parallel agents
npx claude-flow@alpha sparc batch "architecture,coder,tester,perf-analyzer,task-orchestrator" "Implement WebSocket integration as specified"

# 3. Monitor progress
npx claude-flow@alpha swarm status
npx claude-flow@alpha task status
```

### Agent Spawn Instructions

When spawning agents, each MUST include:

```
You are the [Role] agent for WebSocket integration implementation.

MANDATORY COORDINATION:
1. START: Run `npx claude-flow@alpha hooks pre-task --description "WebSocket [your component]"`
2. DURING: After EVERY file operation, run `npx claude-flow@alpha hooks post-edit --file "[file]" --memory-key "websocket/[role]/[step]"`
3. DECISIONS: Store ALL decisions using `npx claude-flow@alpha hooks notify --message "[decision]"`
4. COORDINATION: Check memory for other agents' work before making decisions
5. END: Run `npx claude-flow@alpha hooks post-task --task-id "websocket-[component]" --analyze-performance true`

Your specific responsibilities:
[Detailed role-specific tasks]

Remember: Coordinate with other agents through shared memory!
```

## 🚨 Critical Implementation Notes

### Backward Compatibility
- CSV logging MUST continue alongside WebSocket
- Dashboard MUST support both WebSocket and CSV modes
- Configuration changes MUST be backward compatible
- Existing workflows MUST NOT break

### Error Handling
- WebSocket failures MUST NOT crash the logger
- Dashboard MUST gracefully fall back to CSV
- Connection issues MUST be clearly communicated
- Data integrity MUST be maintained

### Performance Considerations
- Message batching for high-frequency data
- Optional compression for large payloads
- Connection pooling for multiple clients
- Memory-efficient message queuing

## 📊 Progress Tracking

```
📊 WebSocket Integration Progress
├── Total Tasks: 8 major components
├── ✅ Completed: Track via TodoWrite
├── 🔄 In Progress: Monitor with swarm status
├── ⭕ Todo: Update as agents progress
└── ❌ Blocked: Coordinate resolution

Key Milestones:
├── 🎯 Architecture Complete
├── 🎯 Server Implementation
├── 🎯 Client Implementation
├── 🎯 Protocol Implementation
├── 🎯 Error Handling
├── 🎯 Configuration Integration
├── 🎯 Testing Complete
└── 🎯 Documentation Ready
```

## 🏁 Completion Checklist

- [ ] WebSocket server integrated in logger
- [ ] WebSocket client integrated in dashboard
- [ ] Message protocol fully implemented
- [ ] Error handling and fallback working
- [ ] Configuration options documented
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Performance benchmarks met
- [ ] User documentation complete
- [ ] Deployment tested

---

**Ready for parallel implementation with Claude Flow agents!**