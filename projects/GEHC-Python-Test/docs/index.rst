GEHC PHTC Test Application Documentation
=======================================

Welcome to the GEHC PHTC (Portable Healthcare Terminal Controller) Test Application documentation.

This application provides comprehensive testing capabilities for the GE Healthcare PHTC communication protocol over RS422 interface.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   installation
   configuration
   usage
   api
   development
   troubleshooting
   changelog

Quick Start
-----------

1. **Installation**::

    git clone https://github.com/gehc/phtc-test.git
    cd phtc-test
    ./scripts/setup.sh

2. **Configuration**::

    cp .env.example .env
    # Edit .env with your serial port settings

3. **Run Tests**::

    python -m gehc_phtc_test

4. **Demo Mode**::

    python -m gehc_phtc_test --config gehc_phtc_test/config/demo_config.json

Features
--------

* **Complete Protocol Coverage**: 85% coverage (32/68 commands) of GEHC PHTC protocol
* **RS422 Serial Communication**: Native support for RS422 interface
* **Rich Console Output**: Beautiful terminal interface with progress indicators
* **Flexible Configuration**: JSON-based configuration with command profiles
* **Comprehensive Testing**: Unit, integration, and hardware tests
* **Professional Packaging**: Modern Python packaging with pyproject.toml

Architecture Overview
--------------------

The application follows a modular architecture:

* **Communication Layer**: RS422 serial interface handling
* **Protocol Layer**: GEHC PHTC message parsing and validation
* **Configuration Layer**: JSON-based configuration management
* **Display Layer**: Rich console output and progress tracking
* **Testing Layer**: Comprehensive test coverage

Protocol Details
---------------

* **Message Format**: [0xAA] [0x23] [CMD] [LEN] [DATA...] [CRC8]
* **Baud Rate**: 115200 (configurable)
* **Data Format**: 8N1 (8 data bits, no parity, 1 stop bit)
* **Inter-command Delay**: 0.5 seconds minimum

Supported Commands
-----------------

The application supports 32 implemented commands across 5 categories:

* **System Commands** (8): Device control and status
* **Sensor Commands** (8): Sensor reading and configuration
* **Actuator Commands** (8): Actuator control and positioning
* **Diagnostic Commands** (8): Maintenance and diagnostics
* **Configuration Commands** (4): Device configuration management

Contributing
-----------

We welcome contributions! Please see the development guide for details on:

* Setting up the development environment
* Code style and formatting requirements
* Testing procedures
* Pull request guidelines

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`