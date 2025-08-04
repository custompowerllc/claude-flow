Create a prompt to implement integration of websocket communication between the modbus standalone logger and the modbus_dashboard.py

Files:

-   claude-flow\projects\GA_Modbus_Sim\src\modbus_standalone_logger.py
-   claude-flow\projects\GA_Modbus_Sim\src\modbus_dashboard.py

Websocket


For real-time monitoring, replace the current implementation which continuously reads from the csv file that the modbus standalone logger is writing to. 

Instead of the dashboard reading from the csv file during real time monitoring, the logger and dashboard will use websocket communications. So that data is sent to the dashboard during real time monitoring. 