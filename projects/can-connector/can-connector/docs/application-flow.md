# Application Flow Diagram

This diagram illustrates the sequence of events and interactions between the major components of the `can-connector` application.

```mermaid
sequenceDiagram
    participant User
    participant Program.Main
    participant Config_Resolve
    participant CAN_Interface
    participant GUI_Agent
    participant Main_Form
    participant Backend_Agents

    Program.Main->>Config_Resolve: Parse .toml config
    Config_Resolve-->>Program.Main: Return Config_Data & Product objects
    Program.Main->>CAN_Interface: Instantiate
    Program.Main->>GUI_Agent: Instantiate
    GUI_Agent->>Main_Form: Create and Show
    Main_Form->>Main_Form: Build UI from Product object

    User->>Main_Form: Click Connect
    Main_Form->>GUI_Agent: Notify Connect
    GUI_Agent->>CAN_Interface: Establish Connection
    CAN_Interface-->>GUI_Agent: Connection Success
    GUI_Agent->>Main_Form: Set State to IDLE

    loop Event-Driven Operation
        CAN_Interface->>GUI_Agent: Incoming Data
        GUI_Agent->>Main_Form: Update UI

        User->>Main_Form: Perform Action (e.g., Send)
        Main_Form->>GUI_Agent: Notify Action
        GUI_Agent->>Backend_Agents: Execute Action
        Backend_Agents->>CAN_Interface: Send Data
    end
```

## Flow Description

1.  **Startup:** The application starts at `Program.Main`.
2.  **Configuration Loading:** It parses the specified `.toml` configuration file to create `Config_Data` and `Product` objects. These objects define the application's behavior and the target device's properties.
3.  **Initialization:** The core `CAN_Interface` and `GUI_Agent` components are instantiated.
4.  **UI Construction:** The `GUI_Agent` creates the `Main_Form`, which then dynamically builds its user interface based on the loaded `Product` profile.
5.  **Connection:** The user initiates a connection via the UI. The request flows from the `Main_Form` to the `GUI_Agent`, which then instructs the `CAN_Interface` to connect to the hardware.
6.  **Ready State:** Upon a successful connection, the `GUI_Agent` updates the `Main_Form`'s state to `IDLE`, enabling the main controls.
7.  **Event-Driven Operation:** The application enters its main loop:
    -   **Incoming Data:** Data received by the `CAN_Interface` is processed and forwarded to the `GUI_Agent`, which then updates the `Main_Form` to display the new information.
    -   **User Actions:** User interactions with the `Main_Form` are sent to the `GUI_Agent`, which delegates the tasks to the appropriate backend agents (e.g., `Send_Agent`, `Upgrade_Agent`). These agents then use the `CAN_Interface` to communicate with the device.
