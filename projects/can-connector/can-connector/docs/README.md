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