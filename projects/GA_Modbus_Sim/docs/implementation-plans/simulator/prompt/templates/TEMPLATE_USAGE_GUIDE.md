# Claude Flow Template Usage Guide

## 🚀 Quick Start

The `claude-flow-template.md` provides a comprehensive template for creating Claude Flow agent swarm prompts with enhanced working directory enforcement and coordination patterns.

## 📋 Essential Replacements Checklist

### ✅ **Basic Task Information**
```
[TASK_NAME] → "Database Migration" 
[SPECIFIC_IMPLEMENTATION_TARGET] → "Migrate SQLite to PostgreSQL with data preservation"
[CURRENT_SYSTEM_STATE] → "Using SQLite with basic queries"
[MEASURABLE_SUCCESS_CRITERIA] → "All data migrated, tests pass, performance improved"
[COMPLEXITY_LEVEL] → "7"
[TIME_ESTIMATE] → "4-6 hours"
```

### ✅ **Agent Configuration** 
```
[AGENT_COUNT] → "5"
[TOPOLOGY_TYPE] → "hierarchical"
[AGENT_TYPE_1] → "code-analyzer"
[AGENT_NAME_1] → "Database Analyzer"
[AGENT_TYPE_2] → "backend-dev"
[AGENT_NAME_2] → "Migration Architect"
```

### ✅ **Task Management**
```
[TODO_ID_1] → "analyze-schema"
[TODO_DESCRIPTION_1] → "Analyze current SQLite schema structure"
[AGENT_1_OBJECTIVE] → "Comprehensive analysis of current database structure"
[AGENT_1_TASK_1] → "Map all table structures and relationships"
```

## 🎯 Agent Selection Guide

### **Task Type → Recommended Agents**

#### **Code Implementation Tasks**
- Primary: `coder` (Implementation Specialist)
- Support: `code-analyzer` (Code Analysis), `tester` (Validation)

#### **System Architecture Tasks**
- Primary: `system-architect` (System Designer)
- Support: `backend-dev` (Architecture Specialist), `researcher` (Tech Research)

#### **Performance Optimization**
- Primary: `performance-benchmarker` (Performance Specialist)
- Support: `code-analyzer` (Code Analysis), `tester` (Performance Testing)

#### **API Development**
- Primary: `backend-dev` (API Architect)
- Support: `coder` (Implementation), `api-docs` (Documentation), `tester` (API Testing)

#### **Database Operations**
- Primary: `backend-dev` (Database Architect)
- Support: `code-analyzer` (Schema Analysis), `coder` (Migration Scripts), `tester` (Data Validation)

## 📊 Complexity Level Guidelines

### **Complexity Rating Scale:**

| Level | Description | Examples | Agent Count |
|-------|-------------|----------|-------------|
| 1-2 | **Simple** | Basic config changes, simple scripts | 3 agents |
| 3-4 | **Low-Medium** | Feature additions, basic integrations | 3-4 agents |
| 5-6 | **Medium** | Complex features, API integrations | 4-5 agents |
| 7-8 | **High** | System architecture changes, migrations | 5-6 agents |
| 9-10 | **Critical** | Core system overhauls, complex algorithms | 6-8 agents |

### **Complexity Factors:**
- **Threading/Concurrency**: +2-3 levels
- **External APIs**: +1-2 levels
- **Database Changes**: +1-2 levels
- **Performance Requirements**: +1-2 levels
- **Legacy Code Integration**: +1-3 levels

## 🏗️ Topology Selection

### **Hierarchical** (Recommended for most tasks)
- **Best for**: Complex coordinated tasks, clear dependencies
- **Pros**: Clear command structure, efficient coordination
- **Agent Count**: 4-8 agents

### **Mesh** 
- **Best for**: Collaborative analysis, research tasks
- **Pros**: Peer-to-peer coordination, flexible communication
- **Agent Count**: 3-6 agents

### **Star**
- **Best for**: Simple tasks with central coordination
- **Pros**: Simple structure, fast coordination
- **Agent Count**: 3-5 agents

## 🔧 Common Template Patterns

### **Analysis → Design → Implementation → Test → Document**
```javascript
Agent 1: code-analyzer (Analysis)
Agent 2: system-architect (Design) 
Agent 3: coder (Implementation)
Agent 4: tester (Testing)
Agent 5: api-docs (Documentation)
```

### **Research → Architecture → Implementation → Validation**
```javascript
Agent 1: researcher (Research)
Agent 2: backend-dev (Architecture)
Agent 3: coder (Implementation) 
Agent 4: tester (Validation)
```

### **Analyze → Optimize → Test → Monitor**
```javascript
Agent 1: code-analyzer (Analysis)
Agent 2: performance-benchmarker (Optimization)
Agent 3: tester (Testing)
Agent 4: researcher (Monitoring Setup)
```

## 📝 Memory Namespace Patterns

### **Project-Specific Namespaces:**
```bash
# Simulator-specific tasks
--namespace "GA_Modbus_Python_App_Simulator"

# Main app tasks  
--namespace "GA_Modbus_Python_App_Main"

# Tool-specific tasks
--namespace "GA_Modbus_Python_App_Tools"
```

### **Task-Specific Memory Keys:**
```bash
# Analysis results
"swarm/analyzer/findings"
"swarm/analyzer/schema_analysis" 
"swarm/analyzer/performance_metrics"

# Design decisions
"swarm/architect/system_design"
"swarm/architect/api_specification"
"swarm/architect/data_model"

# Implementation progress
"swarm/coder/implementations"
"swarm/coder/code_changes"
"swarm/coder/integration_status"
```

## ⚠️ Common Pitfalls

### **❌ Wrong Working Directory**
```bash
# WRONG - too generic
cd /Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App

# CORRECT - specific to simulator
cd /Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator
```

### **❌ Generic Memory Namespaces**
```bash
# WRONG - causes cross-project contamination
--namespace "coordination"

# CORRECT - project-specific
--namespace "GA_Modbus_Python_App_Simulator"
```

### **❌ Insufficient Agent Coordination**
```bash
# WRONG - missing coordination
npx claude-flow@alpha hooks pre-task

# CORRECT - full coordination
cd /Users/alanhu/development/claude-flow-agents/projects/GA_Modbus_Python_App/simulator
npx claude-flow@alpha hooks pre-task --description "task" --working-dir "$(pwd)"
```

## 🎯 Template Validation Checklist

Before using your customized template:

- [ ] All `[PLACEHOLDER]` values replaced
- [ ] Working directory paths are simulator-specific
- [ ] Memory namespace is project-specific
- [ ] Agent count matches task complexity
- [ ] Agent types appropriate for task requirements
- [ ] All coordination protocols include working directory
- [ ] Success criteria are measurable and testable
- [ ] Validation sequence includes all critical tests
- [ ] Technical specifications are detailed and accurate
- [ ] File paths are relative to simulator root

## 📚 Examples

### **Simple Configuration Task (Complexity 3/10)**
```
[TASK_NAME] → "Add CLI Logging Options"
[AGENT_COUNT] → "3"
[AGENT_TYPE_1] → "code-analyzer"
[AGENT_TYPE_2] → "coder"
[AGENT_TYPE_3] → "tester"
[TOPOLOGY_TYPE] → "star"
```

### **Complex Migration Task (Complexity 7/10)**
```
[TASK_NAME] → "Database Schema Migration"
[AGENT_COUNT] → "6"
[AGENT_TYPE_1] → "code-analyzer"
[AGENT_TYPE_2] → "backend-dev"
[AGENT_TYPE_3] → "coder"
[AGENT_TYPE_4] → "tester"
[AGENT_TYPE_5] → "performance-benchmarker"
[AGENT_TYPE_6] → "api-docs"
[TOPOLOGY_TYPE] → "hierarchical"
```

This guide ensures you can quickly and correctly customize the Claude Flow template for any simulator-related task while maintaining proper working directory enforcement and coordination patterns.