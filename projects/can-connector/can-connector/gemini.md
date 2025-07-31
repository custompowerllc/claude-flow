# CAN Connector Project Overview

This document provides an overview of the `can-connector` application, its architecture, features, and development guidelines.

## 1. Project Overview

`can-connector` is a Windows desktop utility designed for testing, diagnostics, and firmware management of various hardware products, primarily battery systems. It acts as a bridge between a host computer and a target device, communicating over CAN bus, Serial, or Modbus protocols.

The application is highly configurable and data-driven. It loads product-specific profiles from `.toml` files, which define the communication protocols, available commands, data registers, and other parameters for a specific piece of hardware. This allows the same application to be used for a wide range of different products without code changes.

## 2. Features

- **Multi-Protocol Support:** Connects to target devices via:
  - **CAN bus:** Primarily using Total Phase Komodo CAN interfaces.
  - **Serial Port:** Standard serial communication.
  - **Modbus:** Serial-based Modbus communication.
- **Product Profiles:** Loads device-specific configurations from TOML files. This makes the UI and functionality adapt to the selected product.
- **Real-time Data Monitoring:**
  - **Message Registers:** Displays real-time values from the device, translated into human-readable format.
  - **Status Registers:** Shows the state of individual bits in status bytes, with color-coding for high/low states.
- **Data Logging:** Logs all sent and received messages in separate, clear, time-stamped formats.
- **Interactive Sending:**
  - **Queries:** Send predefined queries to the device.
  - **One-Shot & Periodic Sending:** Send a query once or repeatedly at a configurable interval, for a specific or infinite count.
- **Command Execution:** Execute product-specific commands (e.g., "reset device", "run diagnostics"). The application can prompt the user for arguments if a command requires them.
- **Firmware Upgrades:**
  - Supports firmware upgrades by loading `.hex` files.
  - Manages the process of entering/exiting the device's bootloader.
  - Provides a progress bar and status updates during the upgrade.
- **Dynamic UI:** The user interface is built dynamically based on the loaded product profile, showing only the relevant registers, commands, and settings.

## 3. Architecture

The application follows a decoupled, agent-based architecture that separates the UI, business logic, and hardware communication.

- **Entry Point (`Program.cs`):**
  - The `Main` method is the application entry point.
  - It resolves the configuration file specified by command-line arguments (or a default).
  - It instantiates the core components: `CAN_Interface` and `GUI_Agent`.

- **Configuration (`.toml` files & `processing/config-data.cs`):**
  - The application's behavior is defined by `.toml` configuration files.
  - `Config_Resolve.cs` parses these files into a `Config_Data` object (for general settings) and a `Product` object (for device-specific definitions).
  - The `Product` class (`processing/product.cs`) defines the structure for message/status registers, commands, queries, etc.
  - Specific product implementations are located in `processing/products/`.

- **GUI Layer (`gui/`):**
  - Built with C# Windows Forms.
  - **`Main_Form.cs`:** The main window. It is responsible for rendering the UI and capturing user input. It operates as a "view" and is kept simple. It implements the `Main_Form_Agent` interface to receive messages from the `GUI_Agent`.
  - **`GUI_Agent.cs`:** The controller/presenter for the GUI. It mediates all communication between the `Main_Form` and the backend processing agents. It translates user actions into calls to the backend and formats data from the backend for display on the form.
  - The UI uses a state machine (`Main_Form.State`) to manage control availability (e.g., disabling buttons during a firmware upgrade).

- **Processing Layer (`processing/`):**
  - Contains the core application logic.
  - **`CAN_Interface.cs`:** An abstraction layer for communicating with the hardware. It provides a common interface whether the underlying protocol is CAN, Serial, or Modbus.
  - **Agents (`*-agent.cs`):** Specialized agents handle specific tasks:
    - `Send_Agent`: Manages the logic for sending messages.
    - `Upgrade_Agent`: Orchestrates the firmware upgrade process.
    - `Modbus_Agent`: Handles the Modbus protocol specifics.
  - **`Translator.cs`:** Translates raw data from the bus (e.g., a CAN frame) into the parsed and interpreted formats defined by the `Product` profile.

## 4. Application Flow

1.  **Startup:** `Program.Main` parses the command-line arguments to find the path to a `.toml` config file.
2.  **Configuration Loading:** `Config_Resolve` reads and parses the `.toml` file, creating the `Config_Data` and `Product` objects.
3.  **Initialization:** The `CAN_Interface` and `GUI_Agent` are created with the loaded configuration. The `GUI_Agent` then creates and shows the `Main_Form`.
4.  **UI Construction:** `Main_Form` dynamically builds its UI components (register tables, command buttons) based on the information in the `Product` object it receives from the `GUI_Agent`.
5.  **Connection:** The user clicks a button (e.g., "Initialize CAN") on the UI. The `Main_Form` notifies the `GUI_Agent`, which calls the `CAN_Interface` to establish a connection.
6.  **Ready State:** Upon a successful connection, the `GUI_Agent` messages the `Main_Form` to enter the `IDLE` state, which enables the main application controls.
7.  **Event-Driven Operation:** The application now runs in an event loop:
    - **Incoming Data:** `CAN_Interface` receives raw data, the `Translator` parses it, and the `GUI_Agent` is notified. The `GUI_Agent` then sends formatted data to the `Main_Form` to update the display.
    - **User Actions:** The user interacts with the UI (e.g., clicks "Send Once"). The `Main_Form` sends a message to the `GUI_Agent`, which invokes the appropriate backend agent (`Send_Agent`, `Upgrade_Agent`, etc.) to perform the action. The UI is temporarily disabled until the action is complete.
