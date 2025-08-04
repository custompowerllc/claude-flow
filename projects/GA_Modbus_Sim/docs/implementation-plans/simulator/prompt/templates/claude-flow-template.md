# [TASK_NAME] - Claude Flow Agent Swarm Template

**Target**: [SPECIFIC_IMPLEMENTATION_TARGET]
**Current State**: [CURRENT_SYSTEM_STATE]
**Success Metric**: [MEASURABLE_SUCCESS_CRITERIA]
**Complexity Level**: [1-10]/10 ([COMPLEXITY_DESCRIPTION] complexity)
**Estimated Duration**: [TIME_ESTIMATE] total implementation time

## 🚨 CRITICAL CONTEXT

[DETAILED_CONTEXT_DESCRIPTION]

We need to implement:

1. **[FEATURE_1]** - [FEATURE_1_DESCRIPTION]
2. **[FEATURE_2]** - [FEATURE_2_DESCRIPTION]
3. **[FEATURE_3]** - [FEATURE_3_DESCRIPTION]
4. **[FEATURE_4]** - [FEATURE_4_DESCRIPTION]
5. **[FEATURE_5]** - [FEATURE_5_DESCRIPTION]

## 📊 CURRENT STATUS

```
Current Implementation:
  [BASIC] [EXISTING_FEATURE_1]       ← [CURRENT_STATE_1]
  [BASIC] [EXISTING_FEATURE_2]       ← [CURRENT_STATE_2]
  [BASIC] [EXISTING_FEATURE_3]       ← [CURRENT_STATE_3]
  [MISS] [MISSING_FEATURE_1]         ← [MISSING_STATE_1]
  [MISS] [MISSING_FEATURE_2]         ← [MISSING_STATE_2]
  [MISS] [MISSING_FEATURE_3]         ← [MISSING_STATE_3]
  [MISS] [MISSING_FEATURE_4]         ← [MISSING_STATE_4]
```

## 🎯 IMPLEMENTATION STRATEGY

### Claude Flow Swarm Configuration

**Swarm Topology**: [TOPOLOGY_TYPE] ([TOPOLOGY_DESCRIPTION])
**Agent Count**: [AGENT_COUNT] specialized agents
**Execution Mode**: Parallel with shared memory coordination
**Timeline**: [TIME_ESTIMATE] maximum (accounting for complexity level [COMPLEXITY_LEVEL]/10)

### 🤖 AGENT DEPLOYMENT PLAN

```javascript
// [TASK_NAME] Swarm - Parallel Deployment
[Single Message - BatchTool]:
  - mcp__claude-flow__swarm_init { 
      topology: "[TOPOLOGY_TYPE]", 
      maxAgents: [AGENT_COUNT], 
      strategy: "parallel",
      workingDirectory: "/Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator"
    }
  
  - mcp__claude-flow__agent_spawn { 
      type: "[AGENT_TYPE_1]", 
      name: "[AGENT_NAME_1]",
      workingDirectory: "/Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator"
    }
  - mcp__claude-flow__agent_spawn { 
      type: "[AGENT_TYPE_2]", 
      name: "[AGENT_NAME_2]",
      workingDirectory: "/Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator"
    }
  - mcp__claude-flow__agent_spawn { 
      type: "[AGENT_TYPE_3]", 
      name: "[AGENT_NAME_3]",
      workingDirectory: "/Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator"
    }
  - mcp__claude-flow__agent_spawn { 
      type: "[AGENT_TYPE_4]", 
      name: "[AGENT_NAME_4]",
      workingDirectory: "/Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator"
    }
  - mcp__claude-flow__agent_spawn { 
      type: "[AGENT_TYPE_5]", 
      name: "[AGENT_NAME_5]",
      workingDirectory: "/Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator"
    }

  - TodoWrite { todos: [
      { id: "[TODO_ID_1]", content: "[TODO_DESCRIPTION_1]", status: "pending", priority: "high" },
      { id: "[TODO_ID_2]", content: "[TODO_DESCRIPTION_2]", status: "pending", priority: "high" },
      { id: "[TODO_ID_3]", content: "[TODO_DESCRIPTION_3]", status: "pending", priority: "high" },
      { id: "[TODO_ID_4]", content: "[TODO_DESCRIPTION_4]", status: "pending", priority: "high" },
      { id: "[TODO_ID_5]", content: "[TODO_DESCRIPTION_5]", status: "pending", priority: "high" },
      { id: "[TODO_ID_6]", content: "[TODO_DESCRIPTION_6]", status: "pending", priority: "high" },
      { id: "[TODO_ID_7]", content: "[TODO_DESCRIPTION_7]", status: "pending", priority: "medium" },
      { id: "[TODO_ID_8]", content: "[TODO_DESCRIPTION_8]", status: "pending", priority: "medium" },
      { id: "[TODO_ID_9]", content: "[TODO_DESCRIPTION_9]", status: "pending", priority: "medium" },
      { id: "[TODO_ID_10]", content: "[TODO_DESCRIPTION_10]", status: "pending", priority: "medium" },
      { id: "[TODO_ID_11]", content: "[TODO_DESCRIPTION_11]", status: "pending", priority: "medium" },
      { id: "[TODO_ID_12]", content: "[TODO_DESCRIPTION_12]", status: "pending", priority: "low" }
    ]}
```

## 📋 AGENT TASK SPECIFICATIONS

### Agent 1: `[AGENT_TYPE_1]` - [AGENT_NAME_1]
**Primary Objective**: [AGENT_1_OBJECTIVE]

**MANDATORY COORDINATION PROTOCOL**:
```bash
# START - CRITICAL: Set working directory to simulator subdirectory
cd /Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator
npx claude-flow@alpha hooks pre-task --description "[AGENT_1_TASK_DESCRIPTION]" --working-dir "$(pwd)"

# DURING (after each major operation)
npx claude-flow@alpha hooks post-edit --memory-key "[AGENT_1_MEMORY_KEY]" --working-dir "$(pwd)"
npx claude-flow@alpha memory store "swarm/[AGENT_1_ID]/findings" "[AGENT_1_FINDINGS]" --namespace "GA_Modbus_Python_App_Simulator"

# END  
npx claude-flow@alpha hooks post-task --task-id "[AGENT_1_TASK_ID]" --working-dir "$(pwd)"
```

**TASKS**:
1. [AGENT_1_TASK_1]
2. [AGENT_1_TASK_2]
3. [AGENT_1_TASK_3]
4. [AGENT_1_TASK_4]
5. [AGENT_1_TASK_5]
6. [AGENT_1_TASK_6]

### Agent 2: `[AGENT_TYPE_2]` - [AGENT_NAME_2]
**Primary Objective**: [AGENT_2_OBJECTIVE]

**MANDATORY COORDINATION PROTOCOL**:
```bash
# START - CRITICAL: Set working directory to simulator subdirectory
cd /Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator
npx claude-flow@alpha hooks pre-task --description "[AGENT_2_TASK_DESCRIPTION]" --working-dir "$(pwd)"
npx claude-flow@alpha memory query "swarm/[AGENT_1_ID]/findings" --namespace "GA_Modbus_Python_App_Simulator"

# DURING  
npx claude-flow@alpha hooks post-edit --file "[AGENT_2_FILE]" --working-dir "$(pwd)"
npx claude-flow@alpha memory store "swarm/[AGENT_2_ID]/design" "[AGENT_2_DESIGN]" --namespace "GA_Modbus_Python_App_Simulator"

# END
npx claude-flow@alpha hooks post-task --task-id "[AGENT_2_TASK_ID]" --working-dir "$(pwd)"
```

**TASKS**:
1. [AGENT_2_TASK_1]
2. [AGENT_2_TASK_2]
3. [AGENT_2_TASK_3]
4. [AGENT_2_TASK_4]
5. [AGENT_2_TASK_5]
6. [AGENT_2_TASK_6]
7. [AGENT_2_TASK_7]

### Agent 3: `[AGENT_TYPE_3]` - [AGENT_NAME_3]  
**Primary Objective**: [AGENT_3_OBJECTIVE]

**MANDATORY COORDINATION PROTOCOL**:
```bash
# START - CRITICAL: Set working directory to simulator subdirectory
cd /Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator
npx claude-flow@alpha hooks pre-task --description "[AGENT_3_TASK_DESCRIPTION]" --working-dir "$(pwd)"
npx claude-flow@alpha memory query "swarm/[AGENT_2_ID]/design" --namespace "GA_Modbus_Python_App_Simulator"

# DURING
npx claude-flow@alpha hooks post-edit --file "[AGENT_3_FILE]" --working-dir "$(pwd)"
npx claude-flow@alpha memory store "swarm/[AGENT_3_ID]/implementations" "[AGENT_3_CHANGES]" --namespace "GA_Modbus_Python_App_Simulator"

# END
npx claude-flow@alpha hooks post-task --task-id "[AGENT_3_TASK_ID]" --working-dir "$(pwd)"
```

**TASKS**:
1. [AGENT_3_TASK_1]
2. [AGENT_3_TASK_2]
3. [AGENT_3_TASK_3]
4. [AGENT_3_TASK_4]
5. [AGENT_3_TASK_5]
6. [AGENT_3_TASK_6]
7. [AGENT_3_TASK_7]
8. [AGENT_3_TASK_8]

### Agent 4: `[AGENT_TYPE_4]` - [AGENT_NAME_4]
**Primary Objective**: [AGENT_4_OBJECTIVE]

**MANDATORY COORDINATION PROTOCOL**:
```bash
# START - CRITICAL: Set working directory to simulator subdirectory
cd /Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator
npx claude-flow@alpha hooks pre-task --description "[AGENT_4_TASK_DESCRIPTION]" --working-dir "$(pwd)"
npx claude-flow@alpha memory query "swarm/*" --namespace "GA_Modbus_Python_App_Simulator"

# DURING
npx claude-flow@alpha hooks notification --message "[AGENT_4_RESULTS]" --working-dir "$(pwd)"
npx claude-flow@alpha memory store "swarm/[AGENT_4_ID]/results" "[AGENT_4_STATUS]" --namespace "GA_Modbus_Python_App_Simulator"

# END
npx claude-flow@alpha hooks post-task --analyze-performance true --working-dir "$(pwd)"
```

**TASKS**:
1. [AGENT_4_TASK_1]
2. [AGENT_4_TASK_2]
3. [AGENT_4_TASK_3]
4. [AGENT_4_TASK_4]
5. [AGENT_4_TASK_5]
6. [AGENT_4_TASK_6]
7. [AGENT_4_TASK_7]

### Agent 5: `[AGENT_TYPE_5]` - [AGENT_NAME_5]
**Primary Objective**: [AGENT_5_OBJECTIVE]

**MANDATORY COORDINATION PROTOCOL**:
```bash
# START - CRITICAL: Set working directory to simulator subdirectory
cd /Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator
npx claude-flow@alpha hooks pre-task --description "[AGENT_5_TASK_DESCRIPTION]" --working-dir "$(pwd)"

# DURING  
npx claude-flow@alpha hooks post-edit --file "[AGENT_5_FILE]" --working-dir "$(pwd)"
npx claude-flow@alpha memory store "swarm/[AGENT_5_ID]/updates" "[AGENT_5_CHANGES]" --namespace "GA_Modbus_Python_App_Simulator"

# END
npx claude-flow@alpha hooks post-task --task-id "[AGENT_5_TASK_ID]" --working-dir "$(pwd)"
```

**TASKS**:
1. [AGENT_5_TASK_1]
2. [AGENT_5_TASK_2]
3. [AGENT_5_TASK_3]
4. [AGENT_5_TASK_4]
5. [AGENT_5_TASK_5]
6. [AGENT_5_TASK_6]

## 🎯 TECHNICAL SPECIFICATIONS

### [MAIN_CLASS_NAME] Class Design
```python
[CLASS_IMPORTS]

class [MAIN_CLASS_NAME]:
    """[CLASS_DESCRIPTION]"""
    
    def __init__(self, 
                 [INIT_PARAM_1]: [PARAM_1_TYPE] = [DEFAULT_1],
                 [INIT_PARAM_2]: [PARAM_2_TYPE] = [DEFAULT_2],
                 [INIT_PARAM_3]: [PARAM_3_TYPE] = [DEFAULT_3],
                 [INIT_PARAM_4]: [PARAM_4_TYPE] = [DEFAULT_4]):
        pass
    
    def [METHOD_1](self, [METHOD_1_PARAMS]) -> [METHOD_1_RETURN]:
        """[METHOD_1_DESCRIPTION]"""
        pass
    
    def [METHOD_2](self, [METHOD_2_PARAMS]) -> [METHOD_2_RETURN]:
        """[METHOD_2_DESCRIPTION]"""
        pass
    
    def [METHOD_3](self, [METHOD_3_PARAMS]) -> [METHOD_3_RETURN]:
        """[METHOD_3_DESCRIPTION]"""
        pass
    
    def [METHOD_4](self, [METHOD_4_PARAMS]) -> [METHOD_4_RETURN]:
        """[METHOD_4_DESCRIPTION]"""
        pass
```

### CLI Integration
```python
# New CLI options for run_simulator.py
parser.add_argument('[CLI_OPTION_1]', 
                   help='[CLI_HELP_1]')
parser.add_argument('[CLI_OPTION_2]', 
                   help='[CLI_HELP_2]')
parser.add_argument('[CLI_OPTION_3]', default='[DEFAULT_3]',
                   help='[CLI_HELP_3] (default: [DEFAULT_3])')
parser.add_argument('[CLI_OPTION_4]', choices=['[CHOICE_1]', '[CHOICE_2]', '[CHOICE_3]'], 
                   default='[DEFAULT_4]', help='[CLI_HELP_4] (default: [DEFAULT_4])')
parser.add_argument('[CLI_OPTION_5]', type=int, default=[DEFAULT_5],
                   help='[CLI_HELP_5] (default: [DEFAULT_5])')
parser.add_argument('[CLI_OPTION_6]', action='store_true',
                   help='[CLI_HELP_6]')
```

### File Structure
```
simulator/
├── [NEW_DIRECTORY_1]/             # [DIRECTORY_1_DESCRIPTION]
│   ├── [NEW_FILE_1]               # [FILE_1_DESCRIPTION]
│   ├── [NEW_FILE_2]               # [FILE_2_DESCRIPTION]
│   └── [NEW_FILE_3]               # [FILE_3_DESCRIPTION]
├── config/
│   ├── register_mapping.json     # Existing register configuration
│   └── [NEW_CONFIG_FILE]         # NEW: [CONFIG_DESCRIPTION]
```

### Configuration File Format
```json
{
  "version": 1,
  "[CONFIG_KEY_1]": "[CONFIG_VALUE_1]",
  "[CONFIG_KEY_2]": "[CONFIG_VALUE_2]",
  "[CONFIG_SECTION_1]": {
    "[SUB_KEY_1]": {
      "[PARAM_1]": "[VALUE_1]"
    },
    "[SUB_KEY_2]": {
      "[PARAM_2]": "[VALUE_2]"
    }
  },
  "[CONFIG_SECTION_2]": {
    "[SUB_KEY_3]": {
      "[PARAM_3]": "[VALUE_3]",
      "[PARAM_4]": "[VALUE_4]"
    }
  }
}
```

## 🎯 SUCCESS CRITERIA

### Primary Goals
1. **[GOAL_1]**: [GOAL_1_DESCRIPTION]
2. **[GOAL_2]**: [GOAL_2_DESCRIPTION]
3. **[GOAL_3]**: [GOAL_3_DESCRIPTION]
4. **[GOAL_4]**: [GOAL_4_DESCRIPTION]
5. **[GOAL_5]**: [GOAL_5_DESCRIPTION]
6. **[GOAL_6]**: [GOAL_6_DESCRIPTION]

### Validation Sequence
```bash
# After implementation complete - CRITICAL: Set correct working directory to simulator
cd /Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator

# 1. Test [VALIDATION_TEST_1]
[VALIDATION_COMMAND_1]

# 2. Verify [VALIDATION_TEST_2]
[VALIDATION_COMMAND_2]

# 3. Test [VALIDATION_TEST_3]
[VALIDATION_COMMAND_3]

# 4. Test [VALIDATION_TEST_4]  
[VALIDATION_COMMAND_4]

# 5. Test [VALIDATION_TEST_5]
[VALIDATION_COMMAND_5]

# 6. Check [VALIDATION_TEST_6]
[VALIDATION_COMMAND_6]

# 7. Test [VALIDATION_TEST_7]
[VALIDATION_COMMAND_7]

# 8. Validate [VALIDATION_TEST_8]
[VALIDATION_COMMAND_8]
```

## ⚡ EXECUTION TIMELINE

### 📊 COMPLEXITY BREAKDOWN ([COMPLEXITY_LEVEL]/10 - [COMPLEXITY_DESCRIPTION])

**Complexity Factors:**
- **[COMPLEXITY_FACTOR_1]** ([FACTOR_1_LEVEL]/10): [FACTOR_1_DESCRIPTION]
- **[COMPLEXITY_FACTOR_2]** ([FACTOR_2_LEVEL]/10): [FACTOR_2_DESCRIPTION]
- **[COMPLEXITY_FACTOR_3]** ([FACTOR_3_LEVEL]/10): [FACTOR_3_DESCRIPTION]
- **[COMPLEXITY_FACTOR_4]** ([FACTOR_4_LEVEL]/10): [FACTOR_4_DESCRIPTION]
- **[COMPLEXITY_FACTOR_5]** ([FACTOR_5_LEVEL]/10): [FACTOR_5_DESCRIPTION]
- **[COMPLEXITY_FACTOR_6]** ([FACTOR_6_LEVEL]/10): [FACTOR_6_DESCRIPTION]

**Overall Complexity**: [COMPLEXITY_LEVEL]/10 ([COMPLEXITY_DESCRIPTION])
- [COMPLEXITY_REASON_1]
- [COMPLEXITY_REASON_2]
- [COMPLEXITY_REASON_3]
- [COMPLEXITY_REASON_4]
- [COMPLEXITY_REASON_5]

### Phase 1: [PHASE_1_NAME] ([PHASE_1_MINUTES] minutes - Complexity [PHASE_1_COMPLEXITY]/10)
- [PHASE_1_TASK_1] ([TASK_1_MINUTES] min)
- [PHASE_1_TASK_2] ([TASK_2_MINUTES] min)
- [PHASE_1_TASK_3] ([TASK_3_MINUTES] min)
- [PHASE_1_COORDINATION]

### Phase 2: [PHASE_2_NAME] ([PHASE_2_MINUTES] minutes - Complexity [PHASE_2_COMPLEXITY]/10)
- [PHASE_2_TASK_1] ([TASK_1_MINUTES] min)
- [PHASE_2_TASK_2] ([TASK_2_MINUTES] min)
- [PHASE_2_TASK_3] ([TASK_3_MINUTES] min)
- [PHASE_2_TASK_4] ([TASK_4_MINUTES] min)

### Phase 3: [PHASE_3_NAME] ([PHASE_3_MINUTES] minutes - Complexity [PHASE_3_COMPLEXITY]/10)
- [PHASE_3_TASK_1] ([TASK_1_MINUTES] min)
- [PHASE_3_TASK_2] ([TASK_2_MINUTES] min)
- [PHASE_3_TASK_3] ([TASK_3_MINUTES] min)
- [PHASE_3_TASK_4] ([TASK_4_MINUTES] min)

### Phase 4: [PHASE_4_NAME] ([PHASE_4_MINUTES] minutes - Complexity [PHASE_4_COMPLEXITY]/10)
- [PHASE_4_TASK_1]
- [PHASE_4_TASK_2]
- [PHASE_4_TASK_3]

**Total Estimated Duration**: [TOTAL_TIME] ([TOTAL_MINUTES] minutes base + 20% buffer for complexity)

## 🔧 EXPECTED FILE MODIFICATIONS

### New Files
- `simulator/[NEW_FILE_PATH_1]` - NEW [NEW_FILE_DESCRIPTION_1]
- `simulator/[NEW_FILE_PATH_2]` - NEW [NEW_FILE_DESCRIPTION_2]
- `simulator/[NEW_FILE_PATH_3]` - NEW [NEW_FILE_DESCRIPTION_3]

### Modified Files
- `simulator/[MODIFIED_FILE_1]` - [MODIFICATION_DESCRIPTION_1]
- `simulator/[MODIFIED_FILE_2]` - [MODIFICATION_DESCRIPTION_2]
- `simulator/[MODIFIED_FILE_3]` - [MODIFICATION_DESCRIPTION_3]
- `simulator/[MODIFIED_FILE_4]` - [MODIFICATION_DESCRIPTION_4]
- `simulator/[MODIFIED_FILE_5]` - [MODIFICATION_DESCRIPTION_5]
- `simulator/[MODIFIED_FILE_6]` - [MODIFICATION_DESCRIPTION_6]

## 📊 PROGRESS TRACKING FORMAT

```
🐝 [TASK_NAME] Swarm Status: ACTIVE
├── 🏗️ Topology: [TOPOLOGY_TYPE]
├── 👥 Agents: [AGENT_COUNT]/[AGENT_COUNT] active
├── ⚡ Mode: parallel execution
├── 📊 Tasks: [TOTAL_TASKS] total ([COMPLETED] complete, [IN_PROGRESS] in-progress, [PENDING] pending)
└── 🧠 Memory: [MEMORY_POINTS] coordination points stored

Implementation Progress:
├── ✅ [COMPLETED_TASK_1] complete
├── ✅ [COMPLETED_TASK_2] finalized
├── ✅ [COMPLETED_TASK_3] implemented
├── 🔄 [IN_PROGRESS_TASK_1] [PROGRESS_PERCENT]% complete...
├── 🔄 [IN_PROGRESS_TASK_2] in progress...
├── 🔄 [IN_PROGRESS_TASK_3] [PROGRESS_PERCENT]% complete...
├── ⏳ [PENDING_TASK_1] pending
├── ⏳ [PENDING_TASK_2] pending
├── ⏳ [PENDING_TASK_3] pending
└── ⏳ [PENDING_TASK_4] pending

Current Status: [CURRENT_STATUS]
Target: [TARGET_STATUS]
```

## 🚨 CRITICAL NOTES

### **WORKING DIRECTORY ENFORCEMENT**:
All agents MUST work in `/Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator`
- Never default to `bk9206b` or any other project directory
- Never work in the parent GA_Modbus_Python_App directory - work specifically in the simulator subdirectory
- All file operations must be relative to the simulator root
- Memory namespace MUST be "GA_Modbus_Python_App_Simulator" to avoid cross-project contamination

### **Complexity Challenges ([COMPLEXITY_LEVEL]/10 Rating Justification):**

1. **[CHALLENGE_1_NAME]** ([CHALLENGE_1_LEVEL]/10): 
   - [CHALLENGE_1_DETAIL_1]
   - [CHALLENGE_1_DETAIL_2]
   - [CHALLENGE_1_DETAIL_3]

2. **[CHALLENGE_2_NAME]** ([CHALLENGE_2_LEVEL]/10):
   - [CHALLENGE_2_DETAIL_1]
   - [CHALLENGE_2_DETAIL_2]
   - [CHALLENGE_2_DETAIL_3]

3. **[CHALLENGE_3_NAME]** ([CHALLENGE_3_LEVEL]/10):
   - [CHALLENGE_3_DETAIL_1]
   - [CHALLENGE_3_DETAIL_2]
   - [CHALLENGE_3_DETAIL_3]

4. **[CHALLENGE_4_NAME]** ([CHALLENGE_4_LEVEL]/10):
   - [CHALLENGE_4_DETAIL_1]
   - [CHALLENGE_4_DETAIL_2]
   - [CHALLENGE_4_DETAIL_3]

5. **[CHALLENGE_5_NAME]** ([CHALLENGE_5_LEVEL]/10):
   - [CHALLENGE_5_DETAIL_1]
   - [CHALLENGE_5_DETAIL_2]
   - [CHALLENGE_5_DETAIL_3]

### **Risk Mitigation:**
- **High Risk**: [HIGH_RISK_ITEM] → [HIGH_RISK_MITIGATION]
- **Medium Risk**: [MEDIUM_RISK_ITEM] → [MEDIUM_RISK_MITIGATION]
- **Low Risk**: [LOW_RISK_ITEM] → [LOW_RISK_MITIGATION]

## 🎯 FINAL DELIVERABLES

1. **[DELIVERABLE_1]**: [DELIVERABLE_1_DESCRIPTION]
2. **[DELIVERABLE_2]**: [DELIVERABLE_2_DESCRIPTION]
3. **[DELIVERABLE_3]**: [DELIVERABLE_3_DESCRIPTION]
4. **[DELIVERABLE_4]**: [DELIVERABLE_4_DESCRIPTION]
5. **[DELIVERABLE_5]**: [DELIVERABLE_5_DESCRIPTION]
6. **[DELIVERABLE_6]**: [DELIVERABLE_6_DESCRIPTION]
7. **[DELIVERABLE_7]**: [DELIVERABLE_7_DESCRIPTION]

---

## 📈 COMPLEXITY ASSESSMENT SUMMARY

| Component | Complexity | Duration | Risk Level |
|-----------|------------|----------|------------|
| [COMPONENT_1] | [COMP_1_COMPLEXITY]/10 | [COMP_1_DURATION] min | [COMP_1_RISK] |
| [COMPONENT_2] | [COMP_2_COMPLEXITY]/10 | [COMP_2_DURATION] min | [COMP_2_RISK] |
| [COMPONENT_3] | [COMP_3_COMPLEXITY]/10 | [COMP_3_DURATION] min | [COMP_3_RISK] |
| [COMPONENT_4] | [COMP_4_COMPLEXITY]/10 | [COMP_4_DURATION] min | [COMP_4_RISK] |
| [COMPONENT_5] | [COMP_5_COMPLEXITY]/10 | [COMP_5_DURATION] min | [COMP_5_RISK] |
| [COMPONENT_6] | [COMP_6_COMPLEXITY]/10 | [COMP_6_DURATION] min | [COMP_6_RISK] |
| [COMPONENT_7] | [COMP_7_COMPLEXITY]/10 | [COMP_7_DURATION] min | [COMP_7_RISK] |
| [COMPONENT_8] | [COMP_8_COMPLEXITY]/10 | [COMP_8_DURATION] min | [COMP_8_RISK] |

**OVERALL COMPLEXITY**: [COMPLEXITY_LEVEL]/10 ([COMPLEXITY_DESCRIPTION])
**TOTAL DURATION**: [TOTAL_TIME] ([TOTAL_MINUTES] minutes + 20% complexity buffer)

**PROCEED WITH CONFIDENCE**: Despite the [COMPLEXITY_DESCRIPTION] complexity ([COMPLEXITY_LEVEL]/10), the swarm approach with [AGENT_COUNT] specialized agents working in parallel significantly reduces implementation time. The main complexity drivers ([MAIN_COMPLEXITY_DRIVERS]) are well-understood problems with established solutions. All agents work in parallel with shared memory coordination for optimal efficiency.

---

## 📝 TEMPLATE USAGE INSTRUCTIONS

### How to Use This Template

1. **Replace Placeholders**: Search and replace all `[PLACEHOLDER]` values with your specific implementation details
2. **Adjust Agent Count**: Modify the number of agents based on task complexity (3-8 recommended)
3. **Update Working Directory**: Ensure all paths point to your specific project subdirectory
4. **Customize Agent Types**: Choose appropriate agent types from the available Claude Flow agents
5. **Set Complexity Level**: Assess and set realistic complexity ratings (1-10 scale)
6. **Define Success Criteria**: Create measurable and testable success metrics

### Required Replacements

**Basic Information:**
- `[TASK_NAME]` - Short descriptive name for the task
- `[SPECIFIC_IMPLEMENTATION_TARGET]` - What exactly you're building
- `[CURRENT_SYSTEM_STATE]` - Current state of the system
- `[MEASURABLE_SUCCESS_CRITERIA]` - How success will be measured
- `[COMPLEXITY_LEVEL]` - Complexity rating 1-10
- `[TIME_ESTIMATE]` - Realistic time estimate

**Agent Configuration:**
- `[AGENT_COUNT]` - Number of agents (3-8 recommended)
- `[AGENT_TYPE_N]` - Type of each agent (code-analyzer, backend-dev, coder, tester, api-docs, etc.)
- `[AGENT_NAME_N]` - Descriptive name for each agent
- `[TOPOLOGY_TYPE]` - Swarm topology (hierarchical, mesh, star, ring)

**Task Details:**
- `[TODO_ID_N]` - Unique identifier for each todo item
- `[TODO_DESCRIPTION_N]` - Description of each todo task
- `[AGENT_N_OBJECTIVE]` - Primary objective for each agent
- `[AGENT_N_TASK_N]` - Specific tasks for each agent

### Agent Type Reference

**Common Agent Types:**
- `code-analyzer` - Code analysis and pattern detection
- `backend-dev` - Backend architecture and API design
- `coder` - Implementation and coding tasks
- `tester` - Testing and validation
- `api-docs` - Documentation creation
- `system-architect` - High-level system design
- `performance-benchmarker` - Performance testing
- `researcher` - Research and information gathering

### Best Practices

1. **Start with 5 agents** for most tasks
2. **Use hierarchical topology** for complex coordination
3. **Set realistic complexity levels** based on actual technical challenges
4. **Include all working directory enforcement** to prevent directory issues
5. **Use project-specific memory namespaces** to avoid contamination
6. **Create comprehensive validation sequences** for testing
7. **Include detailed technical specifications** for implementation guidance

This template ensures consistent Claude Flow prompt structure with proper working directory enforcement and coordination patterns.