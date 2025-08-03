https://github.com/ruvnet/claude-flow/tree/main

# Deploy intelligent swarm coordination
npx claude-flow@alpha swarm "Build a full-stack application" --strategy development --claude

# Launch hive-mind with specific specializations
npx claude-flow@alpha hive-mind spawn "Create microservices architecture" --agents 8 --claude


# Deploy complete development swarm
npx claude-flow@alpha hive-mind spawn "Build e-commerce platform with React, Node.js, and PostgreSQL" \
  --agents 10 \
  --strategy parallel \
  --memory-namespace ecommerce \
  --claude

# Monitor progress in real-time
npx claude-flow@alpha swarm monitor --dashboard --real-time

# Deploy research swarm with neural enhancement
npx claude-flow@alpha swarm "Research AI safety in autonomous systems" \
  --strategy research \
  --neural-patterns enabled \
  --memory-compression high \
  --claude

# Analyze results with cognitive computing
npx claude-flow@alpha cognitive analyze --target research-results

# Automated security analysis with AI coordination
npx claude-flow@alpha github gh-coordinator analyze --analysis-type security --target ./src
npx claude-flow@alpha github repo-architect optimize --security-focused --compliance SOC2
npx claude-flow@alpha hive-mind spawn "security audit and compliance review" --claude


npx claude-flow@alpha --help          # Main help
npx claude-flow@alpha help <command>  # Detailed command help

# Test available GitHub modes
npx claude-flow@alpha github gh-coordinator --help
npx claude-flow@alpha github pr-manager --help  
npx claude-flow@alpha github issue-tracker --help
npx claude-flow@alpha github release-manager --help
npx claude-flow@alpha github repo-architect --help
npx claude-flow@alpha github sync-coordinator --help

# Test memory functionality
npx claude-flow@alpha memory stats
npx claude-flow@alpha memory store "test" "alpha testing data"
npx claude-flow@alpha memory query "test"

# Test workflow execution
npx claude-flow@alpha workflow create --name "Test Pipeline" --parallel

# GE Healthcare
https://github.com/custompowerllc/GEHealthcare.git