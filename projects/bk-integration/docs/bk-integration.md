You are claude-flow, a claude code task orchestrator. 

Reference the following projects

B&K Precision BK8520 Load Tester FastAPI Controls
@projects/bk8500b_python_app_load_tester

B&K Precision 9206B Power Supply FastAPI Controls
@projects/bk9206b 

Objective: 

Create a integrated interface that can control and monitor both the BK8520 load tester and the BK9206b power supply. This way, we have a single inteface to charge and discharge battery packs. 

# Current Implementation:

## BK8520 Electronic Load Control:
  - Web Interface and REST API control is running on http://10.100.10.190:8000
  - Openapi API and schema docs avaliable at http://10.100.10.190:8000/docs
  - Server: uvicorn 
  - Reference API: @claude-flow/projects/bk-integration/docs/BK8520-API-Documentation.md


## BK9206b Power Supply Controller:
  - Web Interface and REST API control is running on http://10.100.10.190:5300
  - Openapi API and schema docs avaliable at http://10.100.10.190:5300/docs
  - Server: uvicorn 
  - Reference API: @claude-flow/projects/bk-integration/docs/BK9206b-API-Documentation.md






