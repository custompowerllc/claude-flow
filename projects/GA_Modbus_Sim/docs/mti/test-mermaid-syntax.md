# Test Mermaid Syntax

This is a simple test to validate the Mermaid diagrams are properly formatted.

## Simple Test Diagram

```mermaid
flowchart TD
    A[Start] --> B[Process]
    B --> C{Decision}
    C -->|Yes| D[Success]
    C -->|No| E[Retry]
    E --> B
    D --> F[End]
```

## Test Equipment Diagram

```mermaid
graph TB
    subgraph "Equipment"
        PS[Power Supply]
        EL[Electronic Load]
    end
    
    PS --> DUT[Device Under Test]
    EL --> DUT
```

If these render correctly, the syntax issues in MTI-102284-05 should be resolved.