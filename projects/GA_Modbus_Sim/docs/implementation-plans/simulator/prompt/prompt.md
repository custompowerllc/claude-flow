@projects/GA_Modbus_Python_App/ can you create a simulator that the standalone modbus logger can communicate with for testing and development. The simulator should provide a virtual com port, simulate modbus registers, send and recieve modbus communications data. Simulate the battery bms modbus registers. The simulator should be a CLI with pythob RICH 
    library. The simuaator should be configuraable to simulate different scenarios. @projects/GA_Modbus_Python_App/docs/implementation-plans/simulator Create the implementation plan first, don't write any code yet. @CLAUDE.md  Use claude-flow agents working in parallel for efficiency sub agents.

    Only create sub agents that actually exist.

    For example, agent type: analyst and architect do not exist. Use code-analyzer or system-architect instead

    I'll create a comprehensive implementation plan for the Modbus simulator using claude-flow agents working in parallel. Let me set up the coordination and create the plan.

previous run errors:

coordinator(Coordinate overall project planning)
  ⎿  Initializing…
  ⎿  Error: Agent type 'coordinator' not found. Available agents: general-purpose, code-refactoring-specialist, refinement, pseudocode, architecture, specification, ml-developer, base-template-generator, swarm-init, smart-agent, sparc-coord, pr-manager, perf-analyzer, task-orchestrator, sparc-coder, memory-coordinator, migration-planner, swarm-memory-manager,
      collective-intelligence-coordinator, consensus-builder, repo-architect, issue-tracker, project-board-sync, github-modes, code-review-swarm, workflow-automation, multi-repo-swarm, sync-coordinator, release-swarm, release-manager, swarm-pr, swarm-issue, system-architect, production-validator, tdd-london-swarm, mobile-dev, backend-dev, cicd-engineer, 
     code-analyzer, coder, planner, tester, researcher, reviewer, mesh-coordinator, adaptive-coordinator, hierarchical-coordinator, api-docs, byzantine-coordinator, quorum-manager, security-manager, gossip-coordinator, performance-benchmarker, raft-manager, crdt-synchronizer


The implementation plan should include a rapid prototype that tests the proof of concept including virtual com port. Working communications via modbus and serial communication implementation. The CLI should print to the console useful information for debugging. The CLI should also be interactive, allowing inputs from the user. For the initial prototype, the simulator should be able to set battery voltage, which should simulate a 8S LIFEPO4 battery pack, simulate modbus registers such as pack voltage, afe cell voltage 1-8, etc.
Include unit testing