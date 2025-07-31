@claude.md 
use claude-flow parallel agents and follow execution guidelines defined in @claude.md 
For smaller tasks no need to use swarm or hivemind

Pre-agent-spawning:

Make sure that an agent actually exists before using executing spawn. To avoid Error: Agent Type not found, otherwise the task execution will fail. 



After executing claude-flow parallel agents and when agents have completed all of their tasks. Create a after action report in @docs/custom-reports. Include performance overview and metrics, including the agents involved and their performance statistics, tasks, token usage, task duration, efficiency and responsibilities. 