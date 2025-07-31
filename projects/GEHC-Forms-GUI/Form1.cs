using System;
using System.Data;
using System.IO;
using System.IO.Ports;
using System.Windows.Forms;

namespace GEHC_Forms_GUI
{
    public partial class Form1 : Form
    {
        private DataTable dataTable;
        private SerialPort serialPort;

        public Form1()
        {
            InitializeComponent();
            LoadSerialPorts();
            LoadCSVData();
            LoadConfigSettings();
        }

        private void LoadSerialPorts()
        {
            comboBoxPorts.Items.Clear();
            string[] ports = SerialPort.GetPortNames();
            foreach (string port in ports)
            {
                comboBoxPorts.Items.Add(port);
            }

            if (comboBoxPorts.Items.Count > 0)
            {
                comboBoxPorts.SelectedIndex = 0; // Select the first available port
            }
        }

        private void LoadConfigSettings()
        {
            // Load saved COM port and baud rate from config file
            var config = AppConfig.Instance;

            // Set the saved COM port if available
            if (!string.IsNullOrEmpty(config.ComPort))
            {
                for (int i = 0; i < comboBoxPorts.Items.Count; i++)
                {
                    if (comboBoxPorts.Items[i].ToString() == config.ComPort)
                    {
                        comboBoxPorts.SelectedIndex = i;
                        break;
                    }
                }
            }

            // Set the saved baud rate if available
            for (int i = 0; i < comboBoxBaudRate.Items.Count; i++)
            {
                if (int.Parse(comboBoxBaudRate.Items[i].ToString()) == config.BaudRate)
                {
                    comboBoxBaudRate.SelectedIndex = i;
                    break;
                }
            }

            // Setup event handlers for saving config when settings change
            comboBoxPorts.SelectedIndexChanged += (s, e) => SaveConfigSettings();
            comboBoxBaudRate.SelectedIndexChanged += (s, e) => SaveConfigSettings();
        }

        private void SaveConfigSettings()
        {
            if (comboBoxPorts.SelectedItem != null && comboBoxBaudRate.SelectedItem != null)
            {
                var config = AppConfig.Instance;
                config.ComPort = comboBoxPorts.SelectedItem.ToString();
                config.BaudRate = int.Parse(comboBoxBaudRate.SelectedItem.ToString());
                config.Save();
            }
        }

        private void btnConnect_Click(object sender, EventArgs e)
        {
            if (serialPort == null || !serialPort.IsOpen)
            {
                try
                {
                    int baudRate = int.Parse(comboBoxBaudRate.SelectedItem.ToString());
                    serialPort = new SerialPort(comboBoxPorts.SelectedItem.ToString(), baudRate, Parity.None, 8,
                        StopBits.One);
                    serialPort.Open();
                    btnConnect.Text = "Disconnect";
                    AppendToConsole($"Connected to {comboBoxPorts.SelectedItem} at {baudRate} baud.");
                }
                catch (Exception ex)
                {
                    AppendToConsole($"Failed to connect: {ex.Message}");
                    MessageBox.Show($"Failed to connect to the serial port:\n{ex.Message}", "Error",
                        MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
            else
            {
                serialPort.Close();
                btnConnect.Text = "Connect";
                AppendToConsole("Disconnected from serial port.");
            }
        }

        private void LoadCSVData()
        {
            string filePath = "Battery_Info.csv";

            if (!File.Exists(filePath))
            {
                MessageBox.Show("The file 'Battery_Info.csv' was not found!", "Error", MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
                return;
            }

            try
            {
                dataTable = new DataTable();

                // Read all lines from the CSV file
                string[] lines = File.ReadAllLines(filePath);

                if (lines.Length == 0)
                {
                    MessageBox.Show("The CSV file is empty.", "Error", MessageBoxButtons.OK,
                        MessageBoxIcon.Warning);
                    return;
                }

                // Split the header line into columns
                string[] headers = lines[0].Split(',');
                foreach (string header in headers)
                {
                    dataTable.Columns.Add(header.Trim());
                }

                // Add data rows
                for (int i = 1; i < lines.Length; i++)
                {
                    string[] fields = lines[i].Split(',');

                    // Skip rows that do not match the header column count
                    if (fields.Length != headers.Length)
                    {
                        MessageBox.Show($"Skipping malformed row at line {i + 1}.", "Warning", MessageBoxButtons.OK,
                            MessageBoxIcon.Warning);
                        continue;
                    }

                    dataTable.Rows.Add(fields);
                }

                // Bind the DataTable to the DataGridView
                dataGridView.DataSource = dataTable;
                dataGridView.Columns["Description"].AutoSizeMode = DataGridViewAutoSizeColumnMode.AllCells;

                // Add the "Value" column
                if (!dataGridView.Columns.Contains("Value"))
                {
                    dataGridView.Columns.Add("Value", "Value");
                }

                // Add the "Read" column with buttons
                if (!dataGridView.Columns.Contains("Read"))
                {
                    DataGridViewButtonColumn readColumn = new DataGridViewButtonColumn
                    {
                        Name = "Read",
                        HeaderText = "Read",
                        Text = "Read",
                        UseColumnTextForButtonValue = true
                    };
                    dataGridView.Columns.Add(readColumn);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"An error occurred while reading the CSV file:\n{ex.Message}", "Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private byte CalculateCRC8(byte[] data, int len)
        {
            byte crc = 0;
            for (int i = 0; i < len; i++)
            {
                crc ^= data[i];
                for (int j = 0; j < 8; j++)
                {
                    if ((crc & 0x80) != 0)
                    {
                        crc = (byte)((crc << 1) ^ 0x07); // Polynomial for SMBus CRC
                    }
                    else
                    {
                        crc <<= 1;
                    }
                }
            }

            return crc;
        }


        private void dataGridView_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {
            // Check if the "Read" column was clicked
            if (e.ColumnIndex == dataGridView.Columns["Read"].Index && e.RowIndex >= 0)
            {
                // Get the Command and Description of the clicked row
                string commandHex = dataGridView.Rows[e.RowIndex].Cells["Code"].Value?.ToString();
                string description = dataGridView.Rows[e.RowIndex].Cells["Description"].Value?.ToString();

                if (string.IsNullOrWhiteSpace(commandHex))
                {
                    AppendToConsole("Command is missing for the selected row.");
                    return;
                }

                try
                {
                    // Parse the command code
                    byte command = Convert.ToByte(commandHex, 16);


                    // Construct PHTC request message
                    byte[] requestMessage = new byte[4];
                    requestMessage[0] = 0x23; // SYNC_HEADER_HOST_TO_BATTERY
                    requestMessage[1] = command; // Command code
                    requestMessage[2] = 0x00; // No additional data
                    requestMessage[3] = CalculateCRC8(requestMessage, 3); // CRC-8
                    // Log the request message
                    AppendToConsole(
                        $"Sending request: {BitConverter.ToString(requestMessage)} (Command: {description})");

                    // Send the request to the serial device
                    serialPort.Write(requestMessage, 0, requestMessage.Length);

                    // Read the response from the serial device
                    serialPort.ReadTimeout = 5000; // Set timeout
                    byte[] responseBuffer = new byte[256];
                    int bytesRead = serialPort.Read(responseBuffer, 0, responseBuffer.Length);

                    // Validate the response
                    if (bytesRead < 3 || responseBuffer[0] != 0x40) // SYNC_HEADER_BATTERY_TO_HOST
                    {
                        AppendToConsole("Invalid response received.");
                        return;
                    }

                    // Validate CRC
                    if (CalculateCRC8(responseBuffer, bytesRead - 1) != responseBuffer[bytesRead - 1])
                    {
                        AppendToConsole("CRC validation failed for the response.");
                        return;
                    }

                    // Extract the data length and value
                    int dataLength = responseBuffer[2];
                    if (bytesRead != 3 + dataLength + 1) // SYNC_HEADER + Command + Length + Data + CRC
                    {
                        AppendToConsole("Malformed response received.");
                        return;
                    }

                    // Extract the response data based on the command
                    string responseMessage = ParseResponse(command, responseBuffer, dataLength);
                    AppendToConsole(responseMessage);

                    // Update the Value column for the row
                    dataGridView.Rows[e.RowIndex].Cells["Value"].Value = responseMessage;
                }
                catch (TimeoutException)
                {
                    AppendToConsole("Timeout: No response received within 5 seconds.");
                }
                catch (Exception ex)
                {
                    AppendToConsole($"Error during serial communication: {ex.Message}");
                }
            }
        }

        private string ParseResponse(byte command, byte[] response, int dataLength)
        {
            switch (command)
            {
                case 0x00: return "Manufacturer Access: Manufacturer-specific information";

                case 0x01: return $"Remaining Capacity Alarm: {BitConverter.ToUInt16(response, 3)} mAh/10mWh";

                case 0x02: return $"Remaining Time Alarm: {BitConverter.ToUInt16(response, 3)} minutes";

                case 0x03: return $"Battery Mode: 0x{response[3]:X2}";

                case 0x04: return $"AtRate: {BitConverter.ToInt16(response, 3)} mA/10mW";

                case 0x05: return $"AtRate Time To Full: {BitConverter.ToUInt16(response, 3)} minutes";

                case 0x06: return $"AtRate Time To Empty: {BitConverter.ToUInt16(response, 3)} minutes";

                case 0x07: return $"AtRate OK: {response[3] != 0}";

                case 0x08: return $"Temperature: {BitConverter.ToUInt16(response, 3)} °C";

                case 0x09: return $"Voltage: {BitConverter.ToUInt16(response, 3)} mV";

                case 0x0A: return $"Current: {BitConverter.ToInt16(response, 3)} mA";

                case 0x0B: return $"Average Current: {BitConverter.ToInt16(response, 3)} mA";

                case 0x0C: return $"Max Error: {response[3]}%";

                case 0x0D: return $"Relative State of Charge: {response[3]}%";

                case 0x0E: return $"Absolute State of Charge: {response[3]}%";

                case 0x0F: return $"Remaining Capacity: {BitConverter.ToUInt16(response, 3)} mAh/10mWh";

                case 0x10: return $"Full Charge Capacity: {BitConverter.ToUInt16(response, 3)} mAh";

                case 0x11: return $"Run Time to Empty: {BitConverter.ToUInt16(response, 3)} minutes";

                case 0x12: return $"Average Time to Empty: {BitConverter.ToUInt16(response, 3)} minutes";

                case 0x13: return $"Average Time to Full: {BitConverter.ToUInt16(response, 3)} minutes";

                case 0x14: return $"Charging Current: {BitConverter.ToUInt16(response, 3)} mA";

                case 0x15: return $"Charging Voltage: {BitConverter.ToUInt16(response, 3)} mV";

                case 0x17: return $"Cycle Count: {BitConverter.ToUInt16(response, 3)} cycles";

                case 0x18: return $"Design Capacity: {BitConverter.ToUInt16(response, 3)} mAh";

                case 0x19: return $"Design Voltage: {BitConverter.ToUInt16(response, 3)} mV";

                case 0x1A: return $"Specification Info: SMBus version 0x{response[3]:X2}";

                case 0x2C: return $"Temperature 6: {BitConverter.ToUInt16(response, 3)} °C";

                case 0x2D: return $"Temperature 7: {BitConverter.ToUInt16(response, 3)} °C";

                case 0x2E: return $"Temperature 8: {BitConverter.ToUInt16(response, 3)} °C";

                case 0x33: case 0x34: case 0x35: case 0x36: case 0x37:
                case 0x38: case 0x39: case 0x3A: case 0x3B: case 0x3C:
                case 0x3D: case 0x3E: case 0x3F:
                    int cellNumber = command - 0x33 + 13;
                    return $"Cell {cellNumber} Voltage: {BitConverter.ToUInt16(response, 3)} mV";

                case 0x40: return $"Battery Pack PS Nr: {BitConverter.ToUInt16(response, 3)}";

                case 0x41: return $"Cell Cp 0: {BitConverter.ToUInt16(response, 3)} mAh";

                case 0x42: return $"Discharge End Cell Voltage: {BitConverter.ToUInt16(response, 3)} mV";

                case 0x43: return $"Current State: 0x{response[3]:X2}";

                case 0x45: return $"Current Status Allowed Max Discharge Power: {BitConverter.ToUInt16(response, 3)} mW";

                case 0x46: return $"Fault: 0x{response[3]:X2}";

                case 0x4B: return $"Warning: 0x{response[3]:X2}";

                case 0x4C: return $"History Record: {response[3]} record(s)";

                case 0x4F: return $"Battery SOH: {response[3]}%";

                default: return $"Unsupported or unknown command (0x{command:X2})";
            }
        }


        private void AppendToConsole(string message)
        {
            if (textBoxConsole.InvokeRequired)
            {
                textBoxConsole.Invoke(new Action(() => AppendToConsole(message)));
                return;
            }

            textBoxConsole.AppendText($"{DateTime.Now:HH:mm:ss} - {message}{Environment.NewLine}");
            textBoxConsole.ScrollToCaret();
        }

        private string SendPHTCRequest(string code)
        {
            try
            {
                if (serialPort == null || !serialPort.IsOpen)
                {
                    AppendToConsole("Attempted to send data while serial port is not connected.");
                    MessageBox.Show("Serial port is not connected.", "Error", MessageBoxButtons.OK,
                        MessageBoxIcon.Error);
                    return null;
                }

                string requestMessage = $"PHTC_REQUEST_{code}";
                AppendToConsole($"Sending: {requestMessage}");
                serialPort.WriteLine(requestMessage);

                string response = serialPort.ReadLine();
                AppendToConsole($"Received: {response}");

                if (response.StartsWith("PHTC_RESPONSE"))
                {
                    return response.Replace("PHTC_RESPONSE_", "").Trim();
                }

                AppendToConsole($"Invalid response: {response}");
                return null;
            }
            catch (Exception ex)
            {
                AppendToConsole($"Communication error: {ex.Message}");
                return null;
            }
        }
    }
}