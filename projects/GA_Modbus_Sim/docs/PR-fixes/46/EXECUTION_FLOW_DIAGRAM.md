# CodeRabbit Fixes - Claude Flow Agent Execution Flow

## Overview
This diagram illustrates the parallel execution flow of Claude Flow agents implementing CodeRabbit security fixes for PR #46.

## Execution Flow Diagram

```mermaid
graph TB
    %% Define styles
    classDef critical fill:#ff6b6b,stroke:#c92a2a,color:#fff
    classDef high fill:#ff9f40,stroke:#fd7e14,color:#fff
    classDef medium fill:#4ecdc4,stroke:#22b8cf,color:#fff
    classDef agent fill:#748ffc,stroke:#5c7cfa,color:#fff
    classDef phase fill:#495057,stroke:#343a40,color:#fff
    classDef success fill:#51cf66,stroke:#37b24d,color:#fff

    %% Start
    Start([Start: CodeRabbit Fixes Implementation]):::phase
    
    %% Phase 1: Initialization
    Init[Phase 1: Swarm Initialization]:::phase
    Start --> Init
    
    Init --> SwarmInit[Initialize Hierarchical Swarm<br/>7 Agents, Parallel Mode]:::agent
    SwarmInit --> AgentSpawn{Spawn All Agents<br/>Concurrently}
    
    %% Agent Spawning (Parallel)
    AgentSpawn --> A1[Security Manager<br/>Coordination Lead]:::agent
    AgentSpawn --> A2[Vulnerability Scanner<br/>Code Analysis]:::agent
    AgentSpawn --> A3[WebSocket Expert<br/>Validation Implementation]:::agent
    AgentSpawn --> A4[Resource Manager<br/>Leak Fixes]:::agent
    AgentSpawn --> A5[Thread Safety<br/>Synchronization]:::agent
    AgentSpawn --> A6[Security Validator<br/>Testing]:::agent
    AgentSpawn --> A7[Performance Monitor<br/>Benchmarking]:::agent
    
    %% Phase 2: Analysis (30 min)
    A1 --> P2[Phase 2: Security Analysis]:::phase
    A2 --> P2
    
    P2 --> VulnScan[Scan All Vulnerabilities<br/>45+ Issues Identified]:::critical
    P2 --> PriorityMap[Priority Mapping<br/>5 CRITICAL, 8 HIGH]:::critical
    P2 --> MemStore1[Store Vulnerability Map<br/>in Shared Memory]:::medium
    
    %% Phase 3: Core Security Fixes (60 min)
    MemStore1 --> P3[Phase 3: Core Security Implementation]:::phase
    
    %% Parallel Implementation Tasks
    P3 --> WSValidation[WebSocket Validation<br/>JSON Schema]:::critical
    P3 --> PathProtection[Path Traversal<br/>Protection]:::critical
    P3 --> ResourceFix[Resource Leak<br/>Fixes]:::high
    P3 --> SerialFix[Serial Port<br/>Management]:::high
    
    %% WebSocket Implementation Details
    A3 --> WSValidation
    WSValidation --> WSSchema[Create JSON Schema<br/>Validation]:::critical
    WSValidation --> WSManager[Implement WebSocket<br/>Manager Class]:::critical
    WSValidation --> WSCleanup[Add Connection<br/>Cleanup]:::high
    
    %% Path Traversal Details
    A4 --> PathProtection
    PathProtection --> PathValid[Safe Path Join<br/>Function]:::critical
    PathProtection --> PathCheck[Validate All<br/>File Operations]:::critical
    
    %% Resource Management Details
    A4 --> ResourceFix
    ResourceFix --> ContextMgr[Add Context<br/>Managers]:::high
    ResourceFix --> ExceptionHandle[Fix Exception<br/>Handling]:::high
    
    %% Serial Port Details
    A4 --> SerialFix
    SerialFix --> PortCleanup[Port Cleanup<br/>in Finally Blocks]:::high
    SerialFix --> PortCheck[Availability Check<br/>Improvements]:::medium
    
    %% Memory Synchronization
    WSSchema --> MemStore2[Store WebSocket<br/>Implementation]:::medium
    PathValid --> MemStore2[Store Path<br/>Protection Status]:::medium
    ContextMgr --> MemStore2[Store Resource<br/>Fix Status]:::medium
    PortCleanup --> MemStore2
    
    %% Phase 4: Thread Safety (45 min)
    MemStore2 --> P4[Phase 4: Thread Safety Implementation]:::phase
    
    A5 --> P4
    P4 --> ThreadAnalysis[Analyze Shared<br/>State Access]:::high
    P4 --> LockImpl[Implement Locking<br/>Mechanisms]:::high
    P4 --> ThreadStore[Create Thread-Safe<br/>Data Store]:::high
    
    ThreadAnalysis --> RaceFixing[Fix Race<br/>Conditions]:::critical
    LockImpl --> RLockUsage[Use RLock for<br/>Reentrant Locks]:::high
    ThreadStore --> Snapshot[Implement Snapshot<br/>Methods]:::medium
    
    %% Phase 5: Testing & Validation (45 min)
    RaceFixing --> P5[Phase 5: Security Validation]:::phase
    Snapshot --> P5
    
    A6 --> P5
    P5 --> TestCreation{Create Test Suites}
    
    %% Parallel Test Creation
    TestCreation --> T1[WebSocket<br/>Injection Tests]:::critical
    TestCreation --> T2[Path Traversal<br/>Tests]:::critical
    TestCreation --> T3[Resource Leak<br/>Detection]:::high
    TestCreation --> T4[Thread Safety<br/>Stress Tests]:::high
    TestCreation --> T5[Integration<br/>Tests]:::medium
    
    %% Test Execution
    T1 --> TestRun[Run All Security Tests]:::agent
    T2 --> TestRun
    T3 --> TestRun
    T4 --> TestRun
    T5 --> TestRun
    
    %% Performance Validation
    A7 --> PerfBaseline[Establish Performance<br/>Baseline]:::medium
    PerfBaseline --> PerfMeasure[Measure Security<br/>Overhead]:::medium
    PerfMeasure --> PerfOptimize{Performance<br/>< 5% Overhead?}
    
    PerfOptimize -->|Yes| PerfPass[Performance<br/>Acceptable]:::success
    PerfOptimize -->|No| PerfTune[Optimize Critical<br/>Paths]:::high
    PerfTune --> PerfMeasure
    
    %% Final Validation
    TestRun --> FinalCheck{All Tests<br/>Passing?}
    PerfPass --> FinalCheck
    
    FinalCheck -->|Yes| SecurityAudit[Run Security<br/>Audit Tools]:::critical
    FinalCheck -->|No| FixIssues[Fix Failed<br/>Tests]:::high
    FixIssues --> TestRun
    
    SecurityAudit --> AuditPass{Audit<br/>Passed?}
    AuditPass -->|Yes| Complete[Implementation<br/>Complete]:::success
    AuditPass -->|No| SecurityFix[Fix Audit<br/>Issues]:::critical
    SecurityFix --> SecurityAudit
    
    %% Final Documentation
    Complete --> Docs[Generate Security<br/>Documentation]:::medium
    Docs --> End([End: All Vulnerabilities Fixed]):::success

    %% Coordination Arrows (dashed for memory sync)
    A1 -.->|Coordinates| A2
    A1 -.->|Coordinates| A3
    A1 -.->|Coordinates| A4
    A1 -.->|Coordinates| A5
    A1 -.->|Coordinates| A6
    A1 -.->|Coordinates| A7
    
    %% Memory Sync Points
    MemStore1 -.->|Memory Sync| A3
    MemStore1 -.->|Memory Sync| A4
    MemStore1 -.->|Memory Sync| A5
    MemStore2 -.->|Memory Sync| A5
    MemStore2 -.->|Memory Sync| A6
```

## Execution Timeline

```mermaid
gantt
    title CodeRabbit Fixes Implementation Timeline (180 minutes)
    dateFormat HH:mm
    axisFormat %H:%M
    
    section Initialization
    Swarm Setup           :active, init1, 00:00, 5m
    Agent Spawning        :active, init2, after init1, 5m
    
    section Phase 1 Analysis
    Vulnerability Scan    :crit, p1a, after init2, 10m
    Priority Mapping      :crit, p1b, after init2, 10m
    Memory Storage        :p1c, after p1a, 5m
    Coordination          :p1d, after init2, 20m
    
    section Phase 2 Security
    WebSocket Valid       :crit, p2a, after p1c, 20m
    Path Traversal        :crit, p2b, after p1c, 15m
    Resource Fixes        :crit, p2c, after p1c, 15m
    Serial Port           :p2d, after p1c, 10m
    
    section Phase 3 Threading
    Thread Analysis       :crit, p3a, after p2a, 15m
    Lock Implementation   :crit, p3b, after p3a, 15m
    Race Condition Fix    :crit, p3c, after p3b, 10m
    Testing              :p3d, after p3c, 5m
    
    section Phase 4 Testing
    Test Creation        :crit, p4a, after p3c, 15m
    Test Execution       :crit, p4b, after p4a, 15m
    Performance Check    :p4c, after p2a, 10m
    Integration Tests    :p4d, after p4b, 5m
    
    section Validation
    Security Audit       :crit, p5a, after p4d, 5m
    Documentation        :p5b, after p5a, 5m
```

## Agent Orchestration & Task Allocation

```mermaid
graph TB
    %% Define styles
    classDef orchestrator fill:#e74c3c,stroke:#c0392b,color:#fff
    classDef security fill:#e67e22,stroke:#d35400,color:#fff
    classDef analyzer fill:#3498db,stroke:#2980b9,color:#fff
    classDef implementer fill:#27ae60,stroke:#229954,color:#fff
    classDef validator fill:#9b59b6,stroke:#8e44ad,color:#fff
    classDef monitor fill:#f39c12,stroke:#e67e22,color:#fff
    classDef memory fill:#2c3e50,stroke:#34495e,color:#fff
    classDef hook fill:#7f8c8d,stroke:#95a5a6,color:#fff
    classDef task fill:#ecf0f1,stroke:#bdc3c7,color:#2c3e50

    %% Central Orchestrator
    SWARM[🐝 Claude Flow Swarm<br/>Hierarchical Topology<br/>7 Agents, Parallel Mode]:::orchestrator
    
    %% Agent 1: Security Manager
    A1[Agent 1: security-manager<br/>🛡️ Security Lead<br/>Coordination & Strategy]:::security
    A1_TASKS[📋 Tasks:<br/>• Review vulnerability report<br/>• Create implementation plan<br/>• Coordinate agent activities<br/>• Validate security fixes<br/>• Generate audit checklist<br/>• Document improvements]:::task
    
    %% Agent 2: Code Analyzer
    A2[Agent 2: code-analyzer<br/>🔍 Vulnerability Scanner<br/>Pattern Detection & Analysis]:::analyzer
    A2_TASKS[📋 Tasks:<br/>• Scan Python files for vulns<br/>• Map file path operations<br/>• Find WebSocket handlers<br/>• Locate shared state access<br/>• Identify resource patterns<br/>• Generate vuln report]:::task
    
    %% Agent 3: Backend Developer
    A3[Agent 3: backend-dev<br/>🌐 WebSocket Expert<br/>API Security & Validation]:::implementer
    A3_TASKS[📋 Tasks:<br/>• Implement JSON schema validation<br/>• Create WebSocketManager class<br/>• Add connection tracking<br/>• Implement graceful shutdown<br/>• Create security utilities<br/>• Update message handlers]:::task
    
    %% Agent 4: Resource Coder
    A4[Agent 4: coder<br/>🔧 Resource Manager<br/>Leak Prevention & Cleanup]:::implementer
    A4_TASKS[📋 Tasks:<br/>• Fix serial port cleanup<br/>• Add context managers<br/>• Implement exception handling<br/>• Create resource tracking<br/>• Fix thread cleanup<br/>• Add connection pooling]:::task
    
    %% Agent 5: Thread Safety Coder
    A5[Agent 5: coder<br/>⚡ Thread Safety Implementer<br/>Synchronization & Locking]:::implementer
    A5_TASKS[📋 Tasks:<br/>• Create ThreadSafeDataStore<br/>• Identify shared state<br/>• Add locking mechanisms<br/>• Implement thread-safe collections<br/>• Fix race conditions<br/>• Add sync utilities]:::task
    
    %% Agent 6: Security Tester
    A6[Agent 6: tester<br/>🧪 Security Validator<br/>Testing & Verification]:::validator
    A6_TASKS[📋 Tasks:<br/>• Create injection test cases<br/>• Develop path traversal tests<br/>• Write leak detection tests<br/>• Create stress tests<br/>• Implement regression tests<br/>• Automate security testing]:::task
    
    %% Agent 7: Performance Monitor
    A7[Agent 7: performance-benchmarker<br/>📊 Performance Monitor<br/>Impact Analysis & Optimization]:::monitor
    A7_TASKS[📋 Tasks:<br/>• Establish performance baseline<br/>• Measure validation overhead<br/>• Profile resource changes<br/>• Test thread safety impact<br/>• Optimize critical paths<br/>• Generate performance report]:::task
    
    %% Memory System
    MEMORY[(🧠 Shared Memory System<br/>Namespace: GA_Modbus_Sim_Security<br/>Cross-Agent Coordination)]:::memory
    
    %% Hook System
    HOOKS[🪝 Claude Flow Hooks<br/>Pre/Post/Notify<br/>Automated Coordination]:::hook
    
    %% Connections - Orchestration
    SWARM --> A1
    SWARM --> A2
    SWARM --> A3
    SWARM --> A4
    SWARM --> A5
    SWARM --> A6
    SWARM --> A7
    
    %% Task Assignments
    A1 --> A1_TASKS
    A2 --> A2_TASKS
    A3 --> A3_TASKS
    A4 --> A4_TASKS
    A5 --> A5_TASKS
    A6 --> A6_TASKS
    A7 --> A7_TASKS
    
    %% Memory Interactions
    A1 -.->|Stores Strategy| MEMORY
    A2 -.->|Stores Findings| MEMORY
    A3 -.->|Stores Implementations| MEMORY
    A4 -.->|Stores Fixes| MEMORY
    A5 -.->|Stores Safe Classes| MEMORY
    A6 -.->|Stores Test Results| MEMORY
    A7 -.->|Stores Metrics| MEMORY
    
    MEMORY -.->|Queries Data| A3
    MEMORY -.->|Queries Data| A4
    MEMORY -.->|Queries Data| A5
    MEMORY -.->|Queries Data| A6
    MEMORY -.->|Queries Data| A7
    
    %% Hook Coordination
    A1 --> HOOKS
    A2 --> HOOKS
    A3 --> HOOKS
    A4 --> HOOKS
    A5 --> HOOKS
    A6 --> HOOKS
    A7 --> HOOKS
    
    HOOKS -.->|Synchronizes| A1
    HOOKS -.->|Synchronizes| A2
    HOOKS -.->|Synchronizes| A3
    HOOKS -.->|Synchronizes| A4
    HOOKS -.->|Synchronizes| A5
    HOOKS -.->|Synchronizes| A6
    HOOKS -.->|Synchronizes| A7
```

## Detailed Agent Specializations

```mermaid
graph LR
    %% Define styles for agent types
    classDef security fill:#e74c3c,stroke:#c0392b,color:#fff,font-weight:bold
    classDef analyzer fill:#3498db,stroke:#2980b9,color:#fff,font-weight:bold
    classDef backend fill:#27ae60,stroke:#229954,color:#fff,font-weight:bold
    classDef coder fill:#f39c12,stroke:#e67e22,color:#fff,font-weight:bold
    classDef tester fill:#9b59b6,stroke:#8e44ad,color:#fff,font-weight:bold
    classDef monitor fill:#e67e22,stroke:#d35400,color:#fff,font-weight:bold
    classDef file fill:#ecf0f1,stroke:#95a5a6,color:#2c3e50
    classDef critical fill:#c0392b,stroke:#a93226,color:#fff

    %% Agent Types and File Assignments
    subgraph "🛡️ Security Manager (security-manager)"
        SM[Security Lead]:::security
        SM_FILES[Files:<br/>• CODERABBIT_FIXES.md (read)<br/>• security_plan.md (create)<br/>• audit_checklist.md (create)]:::file
    end
    
    subgraph "🔍 Vulnerability Scanner (code-analyzer)"
        VS[Pattern Detection]:::analyzer
        VS_FILES[Files:<br/>• All .py files (scan)<br/>• vulnerability_map.json (create)<br/>• security_report.md (create)]:::file
    end
    
    subgraph "🌐 WebSocket Expert (backend-dev)"
        WE[API Security]:::backend
        WE_FILES[Files:<br/>• modbus_dashboard.py (modify)<br/>• validation.py (create)<br/>• websocket_manager.py (create)]:::file
    end
    
    subgraph "🔧 Resource Manager (coder)"
        RM[Leak Prevention]:::coder
        RM_FILES[Files:<br/>• modbus_server.py (modify)<br/>• modbus_standalone_logger.py (modify)<br/>• resources.py (create)]:::file
    end
    
    subgraph "⚡ Thread Safety (coder)"
        TS[Synchronization]:::coder
        TS_FILES[Files:<br/>• data_manager.py (modify)<br/>• threading.py (create)<br/>• thread_safe_store.py (create)]:::file
    end
    
    subgraph "🧪 Security Validator (tester)"
        SV[Testing]:::tester
        SV_FILES[Files:<br/>• test_validation.py (create)<br/>• test_security.py (create)<br/>• test_threading.py (create)]:::file
    end
    
    subgraph "📊 Performance Monitor (performance-benchmarker)"
        PM[Impact Analysis]:::monitor
        PM_FILES[Files:<br/>• benchmark_security.py (create)<br/>• performance_report.json (create)<br/>• optimization_log.md (create)]:::file
    end
    
    %% Critical Fixes Assignment
    CRITICAL_FIXES[🚨 CRITICAL FIXES<br/>WebSocket Injection<br/>Path Traversal<br/>Resource Leaks<br/>Thread Safety<br/>Serial Port Cleanup]:::critical
    
    %% Agent to Critical Fix Mapping
    VS --> CRITICAL_FIXES
    WE --> CRITICAL_FIXES
    RM --> CRITICAL_FIXES
    TS --> CRITICAL_FIXES
```

## Task Execution Matrix

```mermaid
graph TB
    %% Define styles
    classDef phase1 fill:#ff6b6b,stroke:#c92a2a,color:#fff
    classDef phase2 fill:#4ecdc4,stroke:#22b8cf,color:#fff
    classDef phase3 fill:#45b7d1,stroke:#3498db,color:#fff
    classDef phase4 fill:#96ceb4,stroke:#74b9ff,color:#fff
    classDef sync fill:#fdcb6e,stroke:#e17055,color:#fff

    %% Phase Headers
    P1[Phase 1: Analysis & Planning]:::phase1
    P2[Phase 2: Core Security Implementation]:::phase2
    P3[Phase 3: Thread Safety & Resources]:::phase3
    P4[Phase 4: Testing & Validation]:::phase4
    
    %% Phase 1 Tasks (30 min)
    P1 --> T1_1[Agent 1: Review CodeRabbit report<br/>Create security strategy]
    P1 --> T1_2[Agent 2: Scan all Python files<br/>Map vulnerabilities]
    P1 --> T1_SYNC[Memory Sync: Store findings]:::sync
    
    %% Phase 2 Tasks (60 min)
    P2 --> T2_1[Agent 3: Implement WebSocket validation<br/>Create JSON schema]
    P2 --> T2_2[Agent 4: Fix resource leaks<br/>Add context managers]
    P2 --> T2_3[Agent 7: Establish baseline<br/>Monitor performance]
    P2 --> T2_SYNC[Memory Sync: Store implementations]:::sync
    
    %% Phase 3 Tasks (45 min)
    P3 --> T3_1[Agent 5: Create ThreadSafeDataStore<br/>Add locking mechanisms]
    P3 --> T3_2[Agent 4: Fix serial port cleanup<br/>Exception handling]
    P3 --> T3_3[Agent 1: Coordinate fixes<br/>Validate completeness]
    P3 --> T3_SYNC[Memory Sync: Store thread fixes]:::sync
    
    %% Phase 4 Tasks (45 min)
    P4 --> T4_1[Agent 6: Create security tests<br/>Run validation suite]
    P4 --> T4_2[Agent 7: Performance validation<br/>Optimize if needed]
    P4 --> T4_3[Agent 1: Final security audit<br/>Generate report]
    P4 --> T4_SYNC[Memory Sync: Store results]:::sync
    
    %% Sequential Flow
    T1_SYNC --> P2
    T2_SYNC --> P3
    T3_SYNC --> P4
    
    %% Parallel Execution within Phases
    T1_1 -.->|Parallel| T1_2
    T2_1 -.->|Parallel| T2_2
    T2_2 -.->|Parallel| T2_3
    T3_1 -.->|Parallel| T3_2
    T3_2 -.->|Parallel| T3_3
    T4_1 -.->|Parallel| T4_2
    T4_2 -.->|Parallel| T4_3
```

## Critical Path Analysis

```mermaid
graph TD
    %% Define styles
    classDef critical fill:#ff6b6b,stroke:#c92a2a,color:#fff
    classDef parallel fill:#4ecdc4,stroke:#22b8cf,color:#fff
    classDef optional fill:#868e96,stroke:#495057,color:#fff

    %% Critical Path
    Start([Start]):::critical
    Start --> VulnAnalysis[Vulnerability<br/>Analysis]:::critical
    VulnAnalysis --> WSValid[WebSocket<br/>Validation]:::critical
    VulnAnalysis --> PathTrav[Path Traversal<br/>Protection]:::critical
    
    WSValid --> ThreadSafe[Thread Safety<br/>Implementation]:::critical
    PathTrav --> ThreadSafe
    
    ThreadSafe --> SecTests[Security<br/>Testing]:::critical
    SecTests --> Audit[Security<br/>Audit]:::critical
    Audit --> End([Complete]):::critical
    
    %% Parallel Paths
    VulnAnalysis --> ResFix[Resource<br/>Fixes]:::parallel
    VulnAnalysis --> SerFix[Serial Port<br/>Fixes]:::parallel
    ResFix --> SecTests
    SerFix --> SecTests
    
    %% Optional Optimizations
    VulnAnalysis --> ErrHandle[Error<br/>Handling]:::optional
    VulnAnalysis --> CSVOpt[CSV<br/>Optimization]:::optional
    VulnAnalysis --> ConfigMgmt[Config<br/>Management]:::optional
    
    ErrHandle --> SecTests
    CSVOpt --> SecTests
    ConfigMgmt --> SecTests
    
    %% Performance Path
    WSValid --> PerfBase[Performance<br/>Baseline]:::parallel
    PerfBase --> PerfCheck{< 5%<br/>Overhead?}:::parallel
    PerfCheck -->|Yes| SecTests
    PerfCheck -->|No| Optimize[Optimize]:::parallel
    Optimize --> PerfCheck
```

## Key Execution Principles

### 1. **Parallel Execution**
- All 7 agents spawn simultaneously
- Independent tasks execute in parallel
- Shared memory enables coordination without blocking

### 2. **Priority-Based Implementation**
- CRITICAL vulnerabilities (WebSocket, Path Traversal) first
- HIGH priority issues (Resource leaks, Thread safety) second
- MEDIUM priority optimizations last

### 3. **Continuous Validation**
- Each implementation immediately tested
- Performance monitored throughout
- Security audit as final gate

### 4. **Memory-Based Coordination**
- Agents share findings via memory store
- No direct agent-to-agent communication
- Security Manager orchestrates via memory queries

### 5. **Hook-Driven Synchronization**
- Pre-task hooks for context loading
- Post-edit hooks for progress tracking
- Notification hooks for milestone updates

This execution flow ensures all 45+ CodeRabbit issues are systematically addressed with proper prioritization and validation.

## Agent Type Specifications & Capabilities

| Agent # | Agent Type | Specialization | Primary Files | Key Capabilities |
|---------|------------|----------------|---------------|------------------|
| **1** | `security-manager` | 🛡️ **Security Lead** | CODERABBIT_FIXES.md, security_plan.md | Strategic coordination, vulnerability prioritization, audit validation |
| **2** | `code-analyzer` | 🔍 **Vulnerability Scanner** | All Python files, vulnerability_map.json | Pattern detection, static analysis, security scanning |
| **3** | `backend-dev` | 🌐 **WebSocket Expert** | modbus_dashboard.py, validation.py | API security, message validation, connection management |
| **4** | `coder` | 🔧 **Resource Manager** | modbus_server.py, resources.py | Resource leak prevention, context management, cleanup |
| **5** | `coder` | ⚡ **Thread Safety** | data_manager.py, threading.py | Synchronization, locking, race condition prevention |  
| **6** | `tester` | 🧪 **Security Validator** | test_*.py files | Security testing, injection tests, validation suites |
| **7** | `performance-benchmarker` | 📊 **Performance Monitor** | benchmark_security.py | Performance analysis, overhead measurement, optimization |

## Agent Coordination Patterns

### **Hierarchical Leadership**
- **Security Manager** (Agent 1) acts as the orchestrating leader
- All other agents report findings and progress to shared memory
- Coordination happens through memory queries, not direct communication

### **Parallel Execution Phases**
1. **Phase 1** (30 min): Agents 1 & 2 analyze vulnerabilities in parallel
2. **Phase 2** (60 min): Agents 3, 4 & 7 implement core fixes simultaneously  
3. **Phase 3** (45 min): Agents 4, 5 & 1 handle threading and resource cleanup
4. **Phase 4** (45 min): Agents 6, 7 & 1 validate and audit in parallel

### **Memory-Based Synchronization**
- **Namespace**: `GA_Modbus_Sim_Security` prevents cross-project contamination
- **Key Pattern**: `swarm/{agent_id}/{task_type}` for organized storage
- **Query Pattern**: Agents query previous findings before starting work

### **Hook-Driven Automation**
- **Pre-task**: Context loading and dependency checking
- **Post-edit**: Progress tracking and memory updates  
- **Notification**: Milestone completion and status updates

This orchestration reduces the estimated 40-50 hour manual implementation to 180 minutes through intelligent parallel coordination.