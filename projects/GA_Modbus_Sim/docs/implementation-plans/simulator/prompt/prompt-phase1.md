# Phase 1 Implementation Prompt

You will be helping me implement and develop an application. Read this document throughly as implementation guide, then afterwards only proceed in implementing the software and that you have enough information, and resources prior to proceeding with implementation, only if you are confident in doing so. Give me a confidence score from 0-100, 100 being absolutely confident. Proceed only if you are 90% confident. Otherwise list needed information or resources that you would require, if you are not absolutely confident.

# Reference 

## implementation plan
PATH: @projects/GA_Modbus_Python_App/docs/implementation-plans/simulator/CORRECTED_IMPLEMENTATION_PLAN.md

## Simulator directory structure
PATH: @projects/GA_Modbus_Python_App/simulator


## Modbus Register Mapping
PATH: @projects/GA_Modbus_Python_App/docs/implementation-plans/simulator/FINAL_REGISTER_MAPPING_ANALYSIS.md

## Standalone Python GA logger
This is the standalone logger in which the simulator will be interacting and communicating with

PATH: @projects/GA_Modbus_Python_App/src/modbus_standalone_logger.py

## Implementation Phases Workflow

PATH: @projects/GA_Modbus_Python_App/docs/implementation-plans/simulator/Gdocs/diagrams/implementation-phases-workflow.md

## Phase 1 Diagram


PATH: @projects/GA_Modbus_Python_App/docs/implementation-plans/simulator/Gdocs/diagrams/phase1-dry-run.md

## Confidence Assessment

PATH: @projects/GA_Modbus_Python_App/docs/implementation-plans/simulator/docs/confidence-assessment.md

# Implementation Guidelines

## Python Version Requirements

### **CRITICAL: Python 3.6+ Required for Phase 1**
Phase 1 requires Python 3.6+ for modern features and improved performance.

**✅ ENCOURAGED Modern Python Features:**
- **f-strings**: `f"Cell voltage: {voltage:.3f}V"` for clean string formatting
- **Type hints**: `def calculate_voltage(self, soc: float) -> float:` for better code clarity
- **Pathlib**: `from pathlib import Path` for modern path handling
- **subprocess.run()**: Use modern subprocess interface
- **dataclasses**: `@dataclass` for configuration structures

**✅ RECOMMENDED Syntax for Phase 1:**
```python
# Use f-strings for clean formatting
print(f"Value: {variable}")
print(f"Port {port} status: {status}")

# Use pathlib for modern path handling
from pathlib import Path
file_path = Path(directory) / filename
if file_path.exists():

# Use modern subprocess interface
result = subprocess.run([cmd], capture_output=True, text=True)
```

**Version Checking:**
- Add Python version check: `sys.version_info >= (3, 6)`
- Graceful failure with informative error messages
- Clear upgrade instructions for users

### **Python 3 Validation Protocol**
Before implementation completion, run these validation tests:

1. **Version Check Implementation**:
   ```python
   import sys
   if sys.version_info < (3, 6):
       print("ERROR: Phase 1 requires Python 3.6 or higher")
       print(f"Current version: {sys.version}")
       print("Please upgrade Python to continue")
       sys.exit(1)
   ```

2. **Modern Feature Testing**:
   ```bash
   # Test f-string support
   python3 -c "name='test'; print(f'Hello {name}')"
   
   # Test type hints
   python3 -c "def func(x: int) -> str: return str(x); print(func.__annotations__)"
   
   # Test pathlib
   python3 -c "from pathlib import Path; print(Path.cwd())"
   ```

3. **Execution Validation**:
   ```bash
   # Test demo execution
   python3 simulator/demo_phase1.py
   
   # Test core modules
   python3 -c "import sys; sys.path.append('simulator'); import src.core.modbus_server"
   ```

### **Modern Python Best Practices**
- **f-strings**: Preferred over `.format()` for readability
- **Type hints**: Document function signatures for better maintenance
- **Pathlib**: More robust than `os.path` for file operations
- **Context managers**: Use `with` statements for resource management
- **List comprehensions**: Cleaner than explicit loops where appropriate

## Sub-agents guidelines

@CLAUDE.md  Use claude-flow agents working in parallel for efficiency sub agents.

    Only create sub agents that actually exist.

    For example, agent type: analyst and architect do not exist. Use code-analyzer or system-architect instead

    
### Avoid previous run errors
previous run errors:

coordinator(Coordinate overall project planning)
  ⎿  Initializing…
  ⎿  Error: Agent type 'coordinator' not found. Available agents: general-purpose, code-refactoring-specialist, refinement, pseudocode, architecture, specification, ml-developer, base-template-generator, swarm-init, smart-agent, sparc-coord, pr-manager, perf-analyzer, task-orchestrator, sparc-coder, memory-coordinator, migration-planner, swarm-memory-manager,
      collective-intelligence-coordinator, consensus-builder, repo-architect, issue-tracker, project-board-sync, github-modes, code-review-swarm, workflow-automation, multi-repo-swarm, sync-coordinator, release-swarm, release-manager, swarm-pr, swarm-issue, system-architect, production-validator, tdd-london-swarm, mobile-dev, backend-dev, cicd-engineer, 
     code-analyzer, coder, planner, tester, researcher, reviewer, mesh-coordinator, adaptive-coordinator, hierarchical-coordinator, api-docs, byzantine-coordinator, quorum-manager, security-manager, gossip-coordinator, performance-benchmarker, raft-manager, crdt-synchronizer


# documentation

As you develop the software, write documentation in this directory. Documentation can be technical documention on how the software works, or how to use the software.
- @projects/GA_Modbus_Python_App/docs/implementation-plans/simulator/docs

As you develop the software, write any visualization, diagrams, drawings to this directory. Diagrams can be in plantuml, mermaid, svg, html, or md
- @projects/GA_Modbus_Python_App/docs/implementation-plans/simulator/docs/diagrams

# logging

As you develop the software write development logs here. Development logs can be tasks messages, communication, or debug messages from sub agents. You can also log statistics, such as completed tasks, task duration, any development or debug logs.

- @projects/GA_Modbus_Python_App/docs/implementation-plans/simulator/dev-logs
- 

# 🔧 **Implementation Phases**

You will implement this software in phases. 

### **Phase 1: Virtual COM Port + Exact Modbus Protocol (Week 1)**


### **Phase 2: Complete BMS Simulation (Week 2)**


### **Phase 3: Rich CLI Interface (Week 3)**

### **Phase 4: Scenario System (Week 4)**

### **Phase 5: Testing & Integration (Week 5)**

Current task implement {Phase}.

{Phase} = {Phase 2}

{Status} = Pre-planning 