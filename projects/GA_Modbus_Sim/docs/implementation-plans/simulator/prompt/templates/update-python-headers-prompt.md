# Claude Flow Agent Template: Update Python File Headers

## Task Description
Update all Python source files in the GA_Modbus_Sim project to include standardized header comments with author information, similar to the format used in `modbus_standalone_logger.py`.

## Header Template
```python
"""
[Module/File Description]

Author: Alan Hu
Title: Firmware Engineer
Company: Custom Power LLC
Date: August 3, 2025

[Detailed description of the module/file functionality]
"""
```

## Target Directories (Dry Run)

### Source Files to Update:
1. **Main Project Root**
   - `/projects/GA_Modbus_Sim/*.py` (excluding venv)
   - Files: `check_csv_format.py`, `test_*.py`

2. **Source Directory**
   - `/projects/GA_Modbus_Sim/src/*.py`
   - Primary source files including `modbus_query_test.py`

3. **Simulator Module**
   - `/projects/GA_Modbus_Sim/simulator/*.py`
   - `/projects/GA_Modbus_Sim/simulator/src/core/*.py`
   - `/projects/GA_Modbus_Sim/simulator/src/utils/*.py`
   - `/projects/GA_Modbus_Sim/simulator/config/logging/*.py`

4. **Test Files**
   - `/projects/GA_Modbus_Sim/tests/unit/*.py`
   - `/projects/GA_Modbus_Sim/tests/cli/*.py`
   - `/projects/GA_Modbus_Sim/simulator/tests/unit/*.py`
   - `/projects/GA_Modbus_Sim/simulator/tests/integration/*.py`
   - `/projects/GA_Modbus_Sim/simulator/tests/performance/*.py`

5. **P3E Report Module**
   - `/projects/GA_Modbus_Sim/P3E-Report/*.py`

### Files to Exclude:
- All files in `/venv/` directory
- `__init__.py` files (typically empty or minimal)
- Any generated or third-party files

## Implementation Strategy

### Phase 1: Analysis (Dry Run)
1. Scan all Python files in the project
2. Identify files that need header updates
3. Check existing headers to avoid duplicating author information
4. Generate report of files to be modified

### Phase 2: Header Detection
1. Check if file already has author information
2. Preserve existing module descriptions
3. Identify files with missing or incomplete headers

### Phase 3: Update Process
1. For files with existing docstrings:
   - Insert author information after module description
   - Preserve existing functionality descriptions
2. For files without docstrings:
   - Add complete header template with placeholder description
3. Maintain proper Python docstring formatting

## Dry Run Output Format

```
=== Python Header Update Dry Run ===
Total Python files found: XX
Files to update: XX
Files already have headers: XX
Files to skip (__init__.py, venv): XX

Files to Update:
1. /projects/GA_Modbus_Sim/src/modbus_query_test.py
   - Current: Has docstring but missing author info
   - Action: Insert author block after description

2. /projects/GA_Modbus_Sim/simulator/src/core/modbus_server.py
   - Current: No docstring
   - Action: Add complete header template

[... additional files ...]

Excluded Files:
- /venv/* (third-party packages)
- __init__.py files (typically empty)
```

## Claude Flow Agent Configuration

```yaml
agent_type: code-analyzer
task: Update Python file headers with author information
parallel_operations: true
batch_size: 10
validation: 
  - Check for existing author information
  - Preserve module functionality descriptions
  - Ensure proper Python docstring format
```

## Example Transformations

### Before:
```python
#!/usr/bin/env python3
"""Simple module for testing Modbus functionality."""

import sys
```

### After:
```python
#!/usr/bin/env python3
"""
Simple module for testing Modbus functionality.

Author: Alan Hu
Title: Firmware Engineer
Company: Custom Power LLC
Date: August 3, 2025

[Preserved existing description]
"""

import sys
```

## Validation Steps
1. Ensure all updated files maintain valid Python syntax
2. Verify docstrings are properly formatted
3. Check that existing functionality descriptions are preserved
4. Confirm author information is consistently formatted
5. Test that updated files can still be imported/executed

## Notes
- Preserve shebang lines (`#!/usr/bin/env python3`) if present
- Maintain existing encoding declarations if present
- Keep module-level docstrings at the top of the file
- Don't modify copyright notices if they exist
- Use consistent date format across all files