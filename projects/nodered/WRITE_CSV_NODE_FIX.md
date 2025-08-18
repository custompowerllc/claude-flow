# Fix for Write to CSV Node "zero-length" Error

## Error: "Invalid property expression: zero-length"

This error occurs when the Write to CSV node is misconfigured. Here's the exact fix:

## Step-by-Step Fix for Write to CSV Node

### 1. Open the Write to CSV Node
- **Double-click** the "Write to CSV" node in your Node-RED flow
- This should open the "Edit write file node" dialog

### 2. Configure the Filename Setting
**CRITICAL**: The filename dropdown and field must be configured exactly as follows:

- **Filename dropdown**: Click and change from "path" to **"msg"**
- **Filename text field**: **DELETE everything and leave completely EMPTY**

### 3. Other Settings (should already be correct)
- **Action**: "append to file" 
- **Add newline**: ✅ Checked
- **Create directory**: ✅ Checked  
- **Encoding**: "default"
- **Name**: "Write to CSV" (or whatever you prefer)

### 4. Save and Deploy
- Click **"Done"** to close the dialog
- Click the red **"Deploy"** button in the top right
- Wait for the deploy to complete

## Why This Configuration Works

When set to **"msg"**, the file node will:
- Look for `msg.filename` property in the incoming message
- Use the dynamic filename created by the "Start Logger" function
- Create files like: `20250818_111213-0000-NONE.csv`
- Save to the `./logs/` directory as configured

## Visual Confirmation

After configuring correctly, you should see:
- Filename dropdown shows: **"msg"**
- Filename field is: **completely empty**
- No red triangle or error indicators on the node

## Test the Fix

1. **Initialize Configuration** (click the inject node)
2. **Start Logging** (click the inject node)  
3. **Check Debug Panel** for:
   - "CSV formatter config check" warnings
   - "Logged record #1", "Logged record #2", etc.
   - NO "zero-length" errors

## If Still Getting Errors

If you still see the zero-length error:

1. **Delete the Write to CSV node completely**:
   - Select the node and press Delete
   - Deploy the flow

2. **Add a new file node**:
   - Drag a new "file" node from the storage category
   - Connect it to the "Format CSV Data" node output
   - Configure as described above

3. **Alternative**: Set a static filename temporarily:
   - Filename dropdown: "string"
   - Filename field: `./logs/test_output.csv`
   - This bypasses the dynamic filename to test if the rest works

## Expected Result

Once fixed, you should see:
- No more "zero-length" errors
- CSV files created in `./logs/` directory
- Debug messages showing successful logging
- Data flowing through the entire pipeline

The key is ensuring the dropdown says **"msg"** and the field is **empty**!