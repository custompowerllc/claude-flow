using System; // Fundamental classes and base functions
using System.Collections.Generic; // For using generic collections like List, Queue, etc.
using System.Collections.Immutable; // Immutable collection types
using System.Drawing; // For Color, Font, etc.
using System.Globalization; // For number styles, parsing cultural input, etc.
using System.Linq; // LINQ queries
using System.Windows.Forms; // Windows Forms for GUI elements
using contracts; // Custom contract definitions, assertions etc.
using program_ns.processing; // Custom processing logic
using utility.can; // Custom CAN bus utility functionality
using utility.misc; // Miscellaneous utility functions

namespace program_ns.gui; // This file is in the gui namespace of the program_ns project

using Monotonic = agents.Monotonic; // Alias for easier reference to Monotonic timing functions

internal sealed partial class Main_Form : Form, Main_Form_Agent
{
    // Define the possible states for the form
    private enum State : uint
    {
        INIT,       // Initial state before full init or after a reset
        IDLE,       // Ready for normal operations
        SENDING,    // When the GUI is sending messages
        UPGRADE_INIT, // Preparing for a firmware upgrade
        UPGRADING,    // Firmware upgrade in progress
        CAN_ERROR   // Error state from the CAN bus
    }

    // Constant definitions used for layout and logging
    private const int COMMAND_TABLE_COLS = 5;
    private const int LOG_PURGE_COUNT = 256;
    private const int LOG_LINES_LO = 1024;
    private const int LOG_LINES_HI = LOG_LINES_LO + LOG_PURGE_COUNT;
    private const string TEXT_START = "Start";
    private const string TEXT_STOP = "Stop";
    // Colors for different statuses
    private static readonly Color COLOR_START = Color.LightGreen;
    private static readonly Color COLOR_SLOW = Color.LightYellow;
    private static readonly Color COLOR_STOP = Color.Pink;
    private static readonly Color COLOR_BIT_HI = Color.Pink;
    private static readonly Color COLOR_BIT_LO = Color.LightGreen;
    private static readonly Color COLOR_BIT_RSVD = Color.LightGray;

    // Constructor for the main form. It takes a master GUI agent and a product definition.
    public Main_Form(GUI_Agent a_master, Product a_product)
    {
        m_master = a_master; // Save the master agent for later messaging
        m_dialog_queue = new(); // Queue for dialog messages to be processed serially
        m_destination_set = a_product.destination_set; // Available destinations from the product configuration
        m_message_register_set = a_product.message_register_set; // Message registers available for display
        m_status_register_set = a_product.status_register_set; // Status registers for bit displays
        m_query_set = a_product.query_set; // Query set for sending out data
        m_command_set = a_product.command_set; // Command set for additional functionalities
        m_activity_timer = new() { Interval = 100, Enabled = false }; // Timer to update the UI based on recent activity
        m_recv_log = new(LOG_LINES_HI); // Log queue for received messages
        m_send_log = new(LOG_LINES_HI); // Log queue for sent messages
        m_state = State.INIT; // Start in INIT state
        m_processing_dialog = false; // No dialog is being processed at the start
        m_recv_count = 0; // Count of received messages
        m_send_count = 0; // Count of sent messages
        m_firmware_upgrade_mark = 0; // Timestamp marker for firmware upgrade start
        m_activity_mark = Monotonic.current_tick - 4000; // Set an initial activity timestamp

        InitializeComponent(); // Windows Form designer initialization

        // Set up the activity timer tick event
        m_activity_timer.Tick += (object? a_sender, EventArgs a_args) =>
        {
            // Calculate elapsed time from last activity
            var a_elapsed = Monotonic.current_tick - m_activity_mark;

            // Determine color based on elapsed time
            var a_color =
                a_elapsed switch
                {
                    >= 4000 => COLOR_STOP,   // Too slow? Show as stop color.
                    >= 2000 => COLOR_SLOW,   // Getting a little sluggish.
                    _ => COLOR_START         // Default fast state.
                };

            // Update the background color only if it has changed
            if (m_btn_activity.BackColor != a_color)
            {
                m_btn_activity.BackColor = a_color;
            }
        };

        // Create immutable arrays of controls for receive and send sections
        m_recv_controls = ImmutableArray.Create<Control>
        (
            m_txt_recv_int,
            m_btn_recv_int_apply,
            m_btn_recv_stop_start
        );

        m_send_controls = ImmutableArray.Create<Control>
        (
            m_cmb_send_dest,
            m_txt_send_int,
            m_txt_send_count,
            m_cmb_send_query,
            m_btn_send_start_stop,
            m_btn_send_once
        );

        m_firmware_controls = ImmutableArray.Create<Control>
        (
            m_btn_upgrade_firmware,
            m_btn_enter_bootloader,
            m_btn_exit_bootloader
        );

        // Populate the send destination combo box
        {
            foreach (var a_dest in m_destination_set)
            {
                _ = m_cmb_send_dest.Items.Add(a_dest);
            }

            // If default destination exists and is valid, select it.
            if (a_product.default_destination is not null && m_destination_set.Contains(a_product.default_destination))
            {
                m_cmb_send_dest.SelectedItem = a_product.default_destination;
            }
        }

        // Populate the query combo box similarly
        {
            foreach (var a_query in m_query_set)
            {
                _ = m_cmb_send_query.Items.Add(a_query);
            }

            if (a_product.default_query is not null && m_query_set.Contains(a_product.default_query))
            {
                m_cmb_send_query.SelectedItem = a_product.default_query;
            }
        }

        // Create text boxes for each message register and store them in an immutable dictionary
        {
            var a_font = new Font("Courier New", 12.0f, FontStyle.Regular, GraphicsUnit.Point);
            var a_builder = ImmutableDictionary.CreateBuilder<Product.Message_Register, TextBox>();
            var a_number = 0u;

            foreach (var a_reg in m_message_register_set)
            {
                var a_txt =
                    new TextBox()
                    {
                        AutoSize = true,
                        Font = a_font,
                        Name = $"txt_message_register_{a_number:X4}",
                        ReadOnly = true,
                        Size = new(1400, 0),
                        Anchor = AnchorStyles.None,
                        TabIndex = 0,
                        TabStop = false
                    };

                a_builder.Add(a_reg, a_txt);

                ++a_number;
            }

            m_message_register_control_map = a_builder.ToImmutable();
        }

        // Create buttons for each status register with bits displayed
        {
            var a_font = new Font("Courier New", 12.0f, FontStyle.Bold, GraphicsUnit.Point);
            var a_builder = ImmutableDictionary.CreateBuilder<Product.Status_Register, ImmutableArray<Button>>();
            var a_number = 0u;

            // Local function to create an individual bit button
            Button make_button(string a_text, uint a_number) =>
                new()
                {
                    AutoSize = true,
                    Font = a_font,
                    Name = $"btn_status_register_bit{a_number:X4}",
                    Text = a_text,
                    BackColor = COLOR_BIT_RSVD,
                    Enabled = false,
                    Size = new(150, 0),
                    Anchor = AnchorStyles.None,
                    TabIndex = 0,
                    TabStop = false
                };

            foreach (var a_reg in m_status_register_set)
            {
                // Create an array of buttons for each bit in the register
                var a_bits =
                    ImmutableArray.Create
                    (
                        make_button(a_reg.bit7.display_text, a_number + 0u),
                        make_button(a_reg.bit6.display_text, a_number + 1u),
                        make_button(a_reg.bit5.display_text, a_number + 2u),
                        make_button(a_reg.bit4.display_text, a_number + 3u),
                        make_button(a_reg.bit3.display_text, a_number + 4u),
                        make_button(a_reg.bit2.display_text, a_number + 5u),
                        make_button(a_reg.bit1.display_text, a_number + 6u),
                        make_button(a_reg.bit0.display_text, a_number + 7u)
                    );

                a_builder.Add(a_reg, a_bits);

                a_number += 16u; // Increase the global bit counter (fancy way to keep unique names)
            }

            m_status_register_control_map = a_builder.ToImmutable();
        }

        // Create buttons for each command available in the product
        {
            var a_font = new Font("Courier New", 12.0f, FontStyle.Regular, GraphicsUnit.Point);
            var a_builder = ImmutableDictionary.CreateBuilder<Product.Command, Button>();
            var a_number = 0u;

            foreach (var a_cmd in m_command_set)
            {
                var a_command = a_cmd; // Capture for closure use

                var a_button =
                    new Button()
                    {
                        AutoSize = true,
                        Font = a_font,
                        Name = $"btn_command_{a_number:X4}",
                        Text = a_cmd.display_text,
                        BackColor = Color.LightGray,
                        Enabled = false,
                        Size = new(285, 0),
                        Anchor = AnchorStyles.None,
                        TabIndex = 0,
                        TabStop = false
                    };

                // Wire up the click event to the command handler
                a_button.Click += (object? a_sender, EventArgs a_args) => command_button_clicked(a_command);

                a_builder.Add(a_command, a_button);

                ++a_number;
            }

            m_command_control_map = a_builder.ToImmutable();
        }
    }

    // Member variables
    private readonly GUI_Agent m_master; // The master agent handling interactions
    private readonly Queue<Action> m_dialog_queue; // Queue for handling GUI dialog actions sequentially
    private readonly IReadOnlySet<Product.Destination> m_destination_set; // Product's destination set
    private readonly IReadOnlySet<Product.Message_Register> m_message_register_set; // Message registers
    private readonly IReadOnlySet<Product.Status_Register> m_status_register_set; // Status registers
    private readonly IReadOnlySet<Product.Query> m_query_set; // Set of available queries
    private readonly IReadOnlySet<Product.Command> m_command_set; // Set of commands
    private readonly ImmutableArray<Control> m_recv_controls; // Immutable list of receive-related controls
    private readonly ImmutableArray<Control> m_send_controls; // Immutable list of send-related controls
    private readonly ImmutableArray<Control> m_firmware_controls; // Immutable list of firmware upgrade controls
    private readonly ImmutableDictionary<Product.Message_Register, TextBox> m_message_register_control_map; // Map of message registers to their UI text boxes
    private readonly ImmutableDictionary<Product.Status_Register, ImmutableArray<Button>> m_status_register_control_map; // Map of status registers to their bit buttons
    private readonly ImmutableDictionary<Product.Command, Button> m_command_control_map; // Map of commands to their UI buttons
    private readonly Timer m_activity_timer; // Timer to monitor and indicate bus activity
    private readonly Queue<string> m_recv_log; // Log for received messages
    private readonly Queue<string> m_send_log; // Log for sent messages
    private State m_state; // Current state of the form
    private bool m_processing_dialog; // Whether a dialog is currently being processed
    private bool processing_dialog => m_processing_dialog; // Shortcut getter for readability
    private uint m_recv_count; // Number of received messages processed
    private uint m_send_count; // Number of sent messages processed
    private long m_firmware_upgrade_mark; // Timestamp when firmware upgrade initiated
    private long m_activity_mark; // Timestamp for last activity update

    // Helper property for posting messages to the UI thread asynchronously
    private Action send_message
    {
        set => BeginInvoke(value);
    }

    // Similar helper that is aware of dialogs (to maintain order)
    private Action send_message_dialog_aware
    {
        set => BeginInvoke(() => enqueue_message_dialog_aware = value);
    }

    // Enqueues messages to be processed later, ensuring only one dialog processes at a time.
    private Action enqueue_message_dialog_aware
    {
        set
        {
            m_dialog_queue.Enqueue(value);

            // If a dialog is already processing, don't try to process more.
            if (processing_dialog)
            {
                return;
            }

            // Process queued dialogs one-by-one
            while (m_dialog_queue.TryDequeue(out var a_message))
            {
                m_processing_dialog = true;

                try
                {
                    a_message();
                }
                finally
                {
                    m_processing_dialog = false;
                }
            }
        }
    }

    // Message from the master telling the form to enable features based on the config data
    void Main_Form_Agent.msg_enable_features(Config_Data a_config) =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.INIT);

            Text = a_config.general.title; // Update window title

            // Enable the relevant UI group based on what configuration is available
            do
            {
                if (a_config.komodo is not null)
                {
                    m_btn_init_can.Visible = true;
                    break;
                }

                if (a_config.serial is not null)
                {
                    m_grp_serial.Visible = true;
                    m_txt_baud.Text = a_config.serial.Value.default_baud_rate.ToString();
                    break;
                }

                if (a_config.modbus is not null)
                {
                    m_grp_serial.Visible = true;
                    m_txt_baud.Text = a_config.modbus.Value.default_baud_rate.ToString();
                    break;
                }
            }
            while (false);

            // Show sending group if queries are available, and firmware group if bootloader config exists.
            m_grp_send.Visible = m_query_set.Count is not 0;
            m_grp_firmware.Visible = a_config.bootloader is not null;
        };

    // Show available serial ports in the combo box
    void Main_Form_Agent.msg_available_ports(string[] a_ports) =>
        send_message =
        () =>
        {
            Contracts.assert(m_state is State.INIT);

            if (a_ports.Length is 0)
            {
                return;
            }

            foreach (var a_port in a_ports)
            {
                _ = m_cmb_port.Items.Add(a_port);
            }

            m_cmb_port.SelectedIndex = 0; // Select first port as default
            m_btn_serial_open.Enabled = true;
        };

    // Enter the "ready" state – enabling controls and starting timers
    void Main_Form_Agent.msg_enter_ready_state() =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.INIT);

            m_state = State.IDLE;

            m_activity_timer.Enabled = true;

            if (m_btn_init_can.Visible)
            {
                m_btn_init_can.Enabled = false;
            }
            else
            {
                m_cmb_port.Enabled = m_txt_baud.Enabled = m_btn_serial_open.Enabled = false;
            }

            enable_recv_controls(true);
            enable_send_controls(true);
            enable_firmware_controls(true);
            enable_command_controls(true);
        };

    // Signal a CAN error by changing state and notifying the user via a message box.
    void Main_Form_Agent.msg_can_error(string a_message) =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is not State.INIT);

            m_state = State.CAN_ERROR;

            _ = MessageBox.Show
            (
                this,
                $"Too many errors!{Environment.NewLine}Last error: {a_message}",
                "ERROR",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );

            if (m_btn_init_can.Visible)
            {
                m_btn_init_can.Enabled = true;
            }
            else
            {
                m_cmb_port.Enabled = m_txt_baud.Enabled = m_btn_serial_open.Enabled = true;
            }

            // Hide firmware upgrade progress UI elements
            m_lbl_upgrade_progress.Visible = false;
            m_prg_upgrade_progress.Visible = false;
            m_lbl_upgrade_status.Visible = false;

            enable_recv_controls(false);
            enable_send_controls(false);
            enable_firmware_controls(false);
            enable_command_controls(false);
        };

    // Handle failure in opening the CAN bus 
    void Main_Form_Agent.msg_can_open_failed(string a_message) =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.INIT or State.CAN_ERROR);

            _ = MessageBox.Show
            (
                this,
                $"Init failed: {a_message}",
                "ERROR",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        };

    // Reopen CAN bus and return to idle state
    void Main_Form_Agent.msg_can_reopened() =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.CAN_ERROR);

            m_state = State.IDLE;

            if (m_btn_init_can.Visible)
            {
                m_btn_init_can.Enabled = false;
            }
            else
            {
                m_cmb_port.Enabled = m_txt_baud.Enabled = m_btn_serial_open.Enabled = false;
            }

            enable_recv_controls(true);
            enable_send_controls(true);
            enable_firmware_controls(true);
            enable_command_controls(true);
        };

    // Update the UI to indicate bus activity (reset inactivity timer)
    void Main_Form_Agent.msg_bus_activity() =>
        send_message =
        () =>
        {
            m_activity_mark = Monotonic.current_tick;

            if (m_btn_activity.BackColor != COLOR_START)
            {
                m_btn_activity.BackColor = COLOR_START;
            }
        };

    // Notify user that firmware parsing failed and revert to normal operations.
    void Main_Form_Agent.msg_firmware_parse_fail(string a_message) =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.UPGRADE_INIT or State.CAN_ERROR);

            if (m_state is State.CAN_ERROR)
            {
                return;
            }

            m_state = State.IDLE;

            _ = MessageBox.Show
            (
                this,
                $"Firmware Load Failed: {a_message}",
                "ERROR",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );

            enable_recv_controls(true);
            enable_send_controls(true);
            enable_firmware_controls(true);
            enable_command_controls(true);
        };

    // Ask the user to confirm a firmware upgrade including the size in bytes.
    void Main_Form_Agent.msg_firmware_upgrade_confirm(CAN_Bootloader a_firmware_upgrader) =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.UPGRADE_INIT or State.CAN_ERROR);

            if (m_state is State.CAN_ERROR)
            {
                return;
            }

            var a_result =
            MessageBox.Show
            (
                this,
                $"Confirm Firmware Upgrade: {Environment.NewLine}size: {a_firmware_upgrader.app_size} bytes",
                "CONFIRM",
                MessageBoxButtons.OKCancel,
                MessageBoxIcon.Question
            );

            // If user cancels, revert to IDLE state and re-enable controls.
            if (a_result is not DialogResult.OK)
            {
                m_state = State.IDLE;

                enable_recv_controls(true);
                enable_send_controls(true);
                enable_firmware_controls(true);
                enable_command_controls(true);

                return;
            }

            // Record upgrade start time and trigger upgrade in the master.
            m_firmware_upgrade_mark = Monotonic.current_tick;

            m_master.msg_upgrade_firmware(a_firmware_upgrader);

            // Initialize upgrade progress bar parameters.
            m_prg_upgrade_progress.Minimum = 0;
            m_prg_upgrade_progress.Maximum = a_firmware_upgrader.total_transfer_size;
            m_prg_upgrade_progress.Value = 0;
            m_lbl_upgrade_status.Text = string.Empty;
        };

    // Inform the UI whether the firmware upgrade initiation succeeded, and adjust UI elements.
    void Main_Form_Agent.msg_firmware_upgrade_initiated(bool a_success) =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.UPGRADE_INIT or State.CAN_ERROR);

            if (m_state is State.CAN_ERROR)
            {
                return;
            }

            if (a_success)
            {
                m_state = State.UPGRADING;

                m_lbl_upgrade_progress.Visible = true;
                m_prg_upgrade_progress.Visible = true;
                m_lbl_upgrade_status.Visible = true;

                return;
            }

            m_state = State.IDLE;

            var a_elapsed = (Monotonic.current_tick - m_firmware_upgrade_mark) * 0.001;

            _ = MessageBox.Show
            (
                this,
                $"Firmware Upgrade Failed: failed to enter bootloader{Environment.NewLine}{Environment.NewLine}Elapsed: {a_elapsed:F3}s",
                "ERROR",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );

            enable_recv_controls(true);
            enable_send_controls(true);
            enable_firmware_controls(true);
            enable_command_controls(true);
        };

    // Update the firmware upgrade progress bar and status text
    void Main_Form_Agent.msg_firmware_upgrade_progress(int a_bytes_sent, string a_status) =>
        send_message =
        () =>
        {
            if (a_bytes_sent > m_prg_upgrade_progress.Value)
            {
                m_prg_upgrade_progress.Value = a_bytes_sent;
            }

            m_lbl_upgrade_status.Text = a_status;
        };

    // Called when firmware upgrade fails – notifies the user and resets UI elements.
    void Main_Form_Agent.msg_firmware_upgrade_fail(string a_message) =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.UPGRADING or State.CAN_ERROR);

            if (m_state is State.CAN_ERROR)
            {
                return;
            }

            m_state = State.IDLE;

            var a_elapsed = (Monotonic.current_tick - m_firmware_upgrade_mark) * 0.001;

            _ = MessageBox.Show
            (
                this,
                $"Firmware Upgrade Failed: {a_message}{Environment.NewLine}{Environment.NewLine}Elapsed: {a_elapsed:F3}s",
                "ERROR",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );

            // Hide firmware upgrade UI elements on failure.
            m_lbl_upgrade_progress.Visible = false;
            m_prg_upgrade_progress.Visible = false;
            m_lbl_upgrade_status.Visible = false;

            enable_recv_controls(true);
            enable_send_controls(true);
            enable_firmware_controls(true);
            enable_command_controls(true);
        };

    // Notify the user of successful firmware upgrade and reset UI accordingly.
    void Main_Form_Agent.msg_firmware_upgrade_success() =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.UPGRADING or State.CAN_ERROR);

            if (m_state is State.CAN_ERROR)
            {
                return;
            }

            m_state = State.IDLE;

            var a_elapsed = (Monotonic.current_tick - m_firmware_upgrade_mark) * 0.001;

            m_prg_upgrade_progress.Value = m_prg_upgrade_progress.Maximum;

            _ = MessageBox.Show
            (
                this,
                $"Firmware Upgrade Success!{Environment.NewLine}{Environment.NewLine}Elapsed: {a_elapsed:F3}s",
                "SUCCESS",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );

            m_lbl_upgrade_progress.Visible = false;
            m_prg_upgrade_progress.Visible = false;
            m_lbl_upgrade_status.Visible = false;

            enable_recv_controls(true);
            enable_send_controls(true);
            enable_firmware_controls(true);
            enable_command_controls(true);
        };

    // Called after bootloader exit – re-enable UI controls.
    void Main_Form_Agent.msg_bootloader_exited() =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.IDLE or State.CAN_ERROR);

            if (m_state is State.CAN_ERROR)
            {
                return;
            }

            enable_recv_controls(true);
            enable_send_controls(true);
            enable_firmware_controls(true);
            enable_command_controls(true);
        };

    // Update the send count text box on the UI.
    void Main_Form_Agent.msg_update_send_count(uint a_count) =>
        send_message =
        () => m_txt_send_count.Text = a_count.ToString();

    // Signal that sending has finished and update the UI accordingly.
    void Main_Form_Agent.msg_send_stop_finished() =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.SENDING or State.CAN_ERROR);

            if (m_state is State.CAN_ERROR)
            {
                return;
            }

            m_state = State.IDLE;

            m_btn_send_start_stop.BackColor = COLOR_START;
            m_btn_send_start_stop.Text = TEXT_START;

            enable_recv_controls(true);
            enable_send_controls(true);
            enable_firmware_controls(true);
            enable_command_controls(true);
        };

    // Signal that a one-time send is finished.
    void Main_Form_Agent.msg_send_once_finished() =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.IDLE or State.CAN_ERROR);

            if (m_state is State.CAN_ERROR)
            {
                return;
            }

            enable_recv_controls(true);
            enable_send_controls(true);
            enable_firmware_controls(true);
            enable_command_controls(true);
        };

    // Inform the user that the command is invalid.
    void Main_Form_Agent.msg_command_invalid(string a_message) =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.IDLE or State.SENDING or State.CAN_ERROR);

            if (m_state is State.CAN_ERROR)
            {
                return;
            }

            _ = MessageBox.Show
            (
                this,
                $"Command Failed: {a_message}",
                "ERROR",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );

            enable_recv_controls(true);
            enable_send_controls(true);
            enable_firmware_controls(true);
            enable_command_controls(true);
        };

    // After a command has finished processing, re-enable controls.
    void Main_Form_Agent.msg_command_finished(Product.Command a_command) =>
        send_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.IDLE or State.SENDING or State.CAN_ERROR);

            if (m_state is State.CAN_ERROR)
            {
                return;
            }

            enable_recv_controls(true);
            enable_send_controls(true);
            enable_firmware_controls(true);
            enable_command_controls(true);
        };

    // Local helper method to log CAN messages (both send and receive)
    private static void log_message(
        uint a_count,
        CAN_Message_Parsed a_m,
        Queue<string> a_log_queue,
        TextBox a_log_text_box
    )
    {
        // Acquire a string builder from the pool
        using var a_g1 = String_Builder_Pool.acquire();

        // Format the message with message count and details
        var a_text =
            a_g1.value
            .Append($"{a_count:D8}: FRAME={{{a_m.id_parsed}, [{a_m.data_parsed}]}}; MESSAGE: {{{a_m.id_interpreted}}}; {a_m.data_interpreted}")
            .ToString();

        // If log is not full, append the line
        if (a_log_queue.Count is < LOG_LINES_HI)
        {
            a_log_queue.Enqueue(a_text);

            a_log_text_box.AppendText(a_text);
            a_log_text_box.AppendText(Environment.NewLine);

            return;
        }

        // Purge oldest entries if log is full
        for (var a_remove = LOG_PURGE_COUNT; a_remove is not 0; --a_remove)
        {
            _ = a_log_queue.Dequeue();
        }

        a_log_queue.Enqueue(a_text);
        a_log_text_box.Lines = a_log_queue.ToArray();
        a_log_text_box.AppendText(Environment.NewLine);
    }

    // When a new CAN message is received on a message register, update the register display and log
    void Main_Form_Agent.msg_new_can_message_received(Product.Message_Register a_register, CAN_Message_Parsed a_message) =>
        send_message =
        () =>
        {
            using (var a_g1 = String_Builder_Pool.acquire())
            {
                m_message_register_control_map[a_register].Text =
                    a_g1.value.Append($"{{{a_message.id_interpreted}}}; {a_message.data_interpreted}").ToString();
            }

            // Log the received message
            log_message
            (
                ++m_recv_count,
                a_message,
                m_recv_log,
                m_txt_recv_log
            );
        };

    // Update the UI for a new status register value
    void Main_Form_Agent.msg_new_status_register_received(Product.Status_Register a_register, byte a_status) =>
        send_message =
        () =>
        {
            // Local helper to determine color for each bit
            Color bit_color(int a_shift) =>
                (a_status & (1 << a_shift)) is 0 ? COLOR_BIT_LO : COLOR_BIT_HI;

            var a_bits = m_status_register_control_map[a_register];

            if (!a_register.bit7.always_reserved)
            {
                a_bits[0].BackColor = bit_color(7);
            }

            if (!a_register.bit6.always_reserved)
            {
                a_bits[1].BackColor = bit_color(6);
            }

            if (!a_register.bit5.always_reserved)
            {
                a_bits[2].BackColor = bit_color(5);
            }

            if (!a_register.bit4.always_reserved)
            {
                a_bits[3].BackColor = bit_color(4);
            }

            if (!a_register.bit3.always_reserved)
            {
                a_bits[4].BackColor = bit_color(3);
            }

            if (!a_register.bit2.always_reserved)
            {
                a_bits[5].BackColor = bit_color(2);
            }

            if (!a_register.bit1.always_reserved)
            {
                a_bits[6].BackColor = bit_color(1);
            }

            if (!a_register.bit0.always_reserved)
            {
                a_bits[7].BackColor = bit_color(0);
            }
        };

    // Log a new CAN message that has been sent
    void Main_Form_Agent.msg_new_can_message_sent(CAN_Message_Parsed a_message) =>
        send_message =
        () =>
            log_message
            (
                ++m_send_count,
                a_message,
                m_send_log,
                m_txt_send_log
            );

    // Log messages received in bootloader mode (similar to normal receive)
    void Main_Form_Agent.msg_new_can_message_received_bootloader(CAN_Message_Parsed a_message) =>
        send_message =
        () =>
            log_message
            (
                ++m_recv_count,
                a_message,
                m_recv_log,
                m_txt_recv_log
            );

    // Log messages sent in bootloader mode
    void Main_Form_Agent.msg_new_can_message_sent_bootloader(CAN_Message_Parsed a_message) =>
        send_message =
        () =>
            log_message
            (
                ++m_send_count,
                a_message,
                m_send_log,
                m_txt_send_log
            );

    // Enable or disable controls related to receive messages.
    private void enable_recv_controls(bool a_enable)
    {
        foreach (var a_control in m_recv_controls)
        {
            a_control.Enabled = a_enable;
        }
    }

    // Enable or disable send controls, with optional exclusions.
    private void enable_send_controls(bool a_enable, params Control[] a_exclude)
    {
        foreach (var a_control in m_send_controls)
        {
            if (a_exclude.Contains(a_control))
            {
                continue;
            }

            if (a_control == m_btn_send_start_stop)
            {
                a_control.Enabled =
                    a_enable && m_state is State.IDLE or State.SENDING;
                continue;
            }

            if (a_control == m_cmb_send_dest)
            {
                a_control.Enabled =
                    a_enable && m_state is State.IDLE && m_destination_set.Count is not 0;
                continue;
            }

            a_control.Enabled =
                a_enable && m_state is State.IDLE;
        }
    }

    // Enable or disable firmware-related controls.
    private void enable_firmware_controls(bool a_enable)
    {
        foreach (var a_control in m_firmware_controls)
        {
            a_control.Enabled =
                a_enable && m_state is State.IDLE;
        }
    }

    // Enable or disable command buttons.
    private void enable_command_controls(bool a_enable)
    {
        foreach (var a_control in m_command_control_map.Values)
        {
            a_control.Enabled =
                a_enable && m_state is State.IDLE or State.SENDING;
        }
    }

    // Helper method to parse numeric input from a textbox with error handling.
    private long? parse_text_integer(
        string a_text,
        long a_min_val,
        long a_max_val,
        bool a_allow_empty = false,
        NumberStyles a_style = NumberStyles.Integer
    )
    {
        if (a_allow_empty && a_text.Length is 0)
        {
            return null;
        }

        long a_val;

        try
        {
            a_val = long.Parse(a_text, a_style);
        }
        catch (FormatException a_except)
        {
            _ = MessageBox.Show
            (
                this,
                $"Invalid Input: \"{a_text}\": {a_except.Message}",
                "ERROR",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );

            return null;
        }

        // Check if the parsed value is within allowed range.
        if (a_val < a_min_val || a_val > a_max_val)
        {
            _ = MessageBox.Show
            (
                this,
                $"Input Out of Range: \"{a_text}\": min={a_min_val} max={a_max_val}",
                "ERROR",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );

            return null;
        }

        return a_val;
    }

    // Form closing event: ensure proper cleanup. Prevent closing if upgrading.
    private void Main_Form_FormClosing(object? a_sender, FormClosingEventArgs a_args)
    {
        if (m_state is State.UPGRADING)
        {
            a_args.Cancel = true;
            return;
        }

        m_activity_timer.Enabled = false;
        m_activity_timer.Dispose();
        m_master.Dispose();
    }

    // Form load event: initializes default values and creates dynamic UI layouts for registers and commands.
    private void Main_Form_Load(object? a_sender, EventArgs a_args)
    {
        m_txt_recv_int.Text = GUI_Agent.DEFAULT_RECV_INTERVAL.ToString();
        m_txt_send_int.Text = GUI_Agent.DEFAULT_SEND_INTERVAL.ToString();
        m_txt_send_count.Text = string.Empty;

        m_btn_recv_stop_start.BackColor = COLOR_STOP;
        m_btn_recv_stop_start.Text = TEXT_STOP;
        m_btn_send_start_stop.BackColor = COLOR_START;
        m_btn_send_start_stop.Text = TEXT_START;

        // Set up the message registers table dynamically.
        {
            var a_font = new Font("Courier New", 12.0f, FontStyle.Regular, GraphicsUnit.Point);
            var a_tbl = m_tbl_message_registers;
            var a_row = 0;

            a_tbl.SuspendLayout();
            a_tbl.RowStyles.Clear();
            a_tbl.RowCount = m_message_register_set.Count;

            foreach (var a_reg in m_message_register_set)
            {
                _ = a_tbl.RowStyles.Add(new(SizeType.AutoSize));

                var a_lbl =
                    new Label()
                    {
                        AutoSize = true,
                        Font = a_font,
                        Name = $"lbl_message_register_{a_row:X4}",
                        Text = $"{a_reg.display_text} ".PadRight(25, '.'),
                        Anchor = AnchorStyles.None,
                        TabIndex = 0
                    };

                var a_txt = m_message_register_control_map[a_reg];

                a_tbl.Controls.Add(a_lbl, 0, a_row);
                a_tbl.Controls.Add(a_txt, 1, a_row);

                ++a_row;
            }

            a_tbl.ResumeLayout();
        }

        // Set up the status registers table dynamically.
        {
            var a_font = new Font("Courier New", 12.0f, FontStyle.Regular, GraphicsUnit.Point);
            var a_tbl = m_tbl_status_registers;
            var a_row = 0;

            a_tbl.SuspendLayout();
            a_tbl.RowStyles.Clear();
            a_tbl.RowCount = m_status_register_set.Count;

            foreach (var a_reg in m_status_register_set)
            {
                _ = a_tbl.RowStyles.Add(new(SizeType.AutoSize));

                var a_lbl =
                    new Label()
                    {
                        AutoSize = true,
                        Font = a_font,
                        Name = $"lbl_status_register{a_row:X4}",
                        Text = $"{a_reg.display_text} ".PadRight(40, '.'),
                        Anchor = AnchorStyles.None,
                        TabIndex = 0
                    };

                var a_bits = m_status_register_control_map[a_reg];

                a_tbl.Controls.Add(a_lbl, 0, a_row);

                for (var a_i = 0; a_i != a_bits.Length; ++a_i)
                {
                    a_tbl.Controls.Add(a_bits[a_i], a_i + 1, a_row);
                }

                ++a_row;
            }

            a_tbl.ResumeLayout();
        }

        // Set up the commands table dynamically, arranging buttons into a grid.
        {
            var a_tbl = m_tbl_commands;

            a_tbl.SuspendLayout();
            a_tbl.RowStyles.Clear();

            {
                var a_div = m_command_set.Count / COMMAND_TABLE_COLS;
                var a_mod = m_command_set.Count % COMMAND_TABLE_COLS;

                a_tbl.RowCount = a_div + (a_mod is 0 ? 0 : 1);
            }

            var a_row = 0;
            var a_col = 0;

            foreach (var a_reg in m_command_set)
            {
                if (a_col is 0)
                {
                    _ = a_tbl.RowStyles.Add(new(SizeType.AutoSize));
                }

                a_tbl.Controls.Add(m_command_control_map[a_reg], a_col, a_row);

                if (++a_col is not COMMAND_TABLE_COLS)
                {
                    continue;
                }

                ++a_row;
                a_col = 0;
            }

            a_tbl.ResumeLayout();
        }
    }

    // Button click event for initializing CAN bus.
    private void btn_init_can_Click(object? a_sender, EventArgs a_args)
    {
        Contracts.assert(m_state is State.INIT or State.CAN_ERROR);
        m_master.msg_open_can(m_state is State.CAN_ERROR);
    }

    // Button click event for opening the serial port.
    private void btn_serial_open_Click(object? a_sender, EventArgs a_args) =>
        enqueue_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.INIT or State.CAN_ERROR);

            m_txt_baud.Text = m_txt_baud.Text.Trim();

            if (m_cmb_port.SelectedItem is not string a_port)
            {
                _ = MessageBox.Show
                (
                    this,
                    "No port selected",
                    "ERROR",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );

                return;
            }

            if (!int.TryParse(m_txt_baud.Text, NumberStyles.None, null, out var a_baud))
            {
                _ = MessageBox.Show
                (
                    this,
                    "Invalid baud-rate",
                    "ERROR",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );

                return;
            }

            if (a_baud is <= 0)
            {
                _ = MessageBox.Show
                (
                    this,
                    "Baud-rate out of range",
                    "ERROR",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );

                return;
            }

            m_master.msg_open_serial(m_state is State.CAN_ERROR, a_port, a_baud);
        };

    // Exit button click event, simply closes the form.
    private void btn_exit_Click(object? a_sender, EventArgs a_args) => Close();

    // Button click event for firmware upgrade initiation.
    private void btn_upgrade_firmware_Click(object? a_sender, EventArgs a_args) =>
        enqueue_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.IDLE);

            using var a_dialog = new OpenFileDialog() { Filter = "HEX Files (*.hex)|*.hex" };

            _ = a_dialog.ShowDialog(this);

            var a_file_name = a_dialog.FileName;

            if (a_file_name.Length is 0)
            {
                return;
            }

            m_master.msg_parse_firmware(a_file_name);

            m_state = State.UPGRADE_INIT;

            enable_recv_controls(false);
            enable_send_controls(false);
            enable_firmware_controls(false);
            enable_command_controls(false);
        };

    // Button click event to apply received interval changes.
    private void btn_recv_int_apply_Click(object? a_sender, EventArgs a_args)
    {
        Contracts.assert(m_state is not State.INIT);

        var a_interval = parse_text_integer(m_txt_recv_int.Text.Trim(), 0, 1000);

        if (a_interval is null)
        {
            return;
        }

        m_master.msg_set_recv_interval((uint)a_interval.Value);
    }

    // Toggle button click for starting/stopping reception of messages.
    private void btn_recv_int_stop_start_Click(object? a_sender, EventArgs a_args)
    {
        Contracts.assert(m_state is not State.INIT);

        var a_btn = m_btn_recv_stop_start;
        Contracts.assert(a_btn.BackColor == COLOR_STOP || a_btn.BackColor == COLOR_START);

        if (a_btn.BackColor == COLOR_STOP)
        {
            m_master.msg_ignore_recv(true);
            a_btn.BackColor = COLOR_START;
            a_btn.Text = TEXT_START;
            return;
        }

        m_master.msg_ignore_recv(false);
        a_btn.BackColor = COLOR_STOP;
        a_btn.Text = TEXT_STOP;
    }

    // Button click event to start or stop sending messages continuously.
    private void btn_send_start_stop_Click(object? a_sender, EventArgs a_args)
    {
        Contracts.assert(m_state is State.IDLE or State.SENDING);

        var a_btn = m_btn_send_start_stop;

        if (m_state is State.SENDING)
        {
            m_master.msg_stop_sending();

            enable_recv_controls(false);
            enable_send_controls(false);
            enable_firmware_controls(false);
            enable_command_controls(false);

            return;
        }

        var a_interval = parse_text_integer(m_txt_send_int.Text.Trim(), 10, 1000 * 60 * 60);

        if (a_interval is null)
        {
            return;
        }

        var a_count_text = m_txt_send_count.Text.Trim();
        var a_count = parse_text_integer(a_count_text, 1, uint.MaxValue, true);

        if (a_count is null && a_count_text.Length is not 0)
        {
            return;
        }

        Contracts.assert(m_cmb_send_query.SelectedItem is not null);

        m_master.msg_start_sending((uint)a_interval.Value, (uint?)a_count, (Product.Query)m_cmb_send_query.SelectedItem);

        a_btn.BackColor = COLOR_STOP;
        a_btn.Text = TEXT_STOP;

        m_state = State.SENDING;

        enable_send_controls(false, m_btn_send_start_stop);
        enable_firmware_controls(false);
    }

    // Button click event for sending a one-time query.
    private void btn_send_once_Click(object? a_sender, EventArgs a_args)
    {
        Contracts.assert(m_state is State.IDLE);

        m_master.msg_send_once((Product.Query)m_cmb_send_query.SelectedItem);

        enable_recv_controls(false);
        enable_send_controls(false);
        enable_firmware_controls(false);
        enable_command_controls(false);
    }

    // Button click event to enter bootloader mode.
    private void btn_enter_bootloader_Click(object? a_sender, EventArgs a_args)
    {
        Contracts.assert(m_state is State.IDLE);

        m_master.msg_enter_bootloader();

        enable_recv_controls(false);
        enable_send_controls(false);
        enable_firmware_controls(false);
        enable_command_controls(false);
    }

    // Button click event to exit bootloader mode.
    private void btn_exit_bootloader_Click(object? a_sender, EventArgs a_args)
    {
        Contracts.assert(m_state is State.IDLE);

        m_master.msg_exit_bootloader();

        enable_recv_controls(false);
        enable_send_controls(false);
        enable_firmware_controls(false);
        enable_command_controls(false);
    }

    // Event handler when the send destination changes.
    private void cmb_send_dest_SelectedIndexChanged(object? a_sender, EventArgs a_args)
    {
        if (m_state is State.INIT)
        {
            return;
        }

        Contracts.assert(m_cmb_send_dest.SelectedItem is not null);

        m_master.msg_set_send_dest((Product.Destination)m_cmb_send_dest.SelectedItem);
    }

    // Handler for when a command button is clicked
    private void command_button_clicked(Product.Command a_command) =>
        enqueue_message_dialog_aware =
        () =>
        {
            Contracts.assert(m_state is State.IDLE or State.SENDING);

            if (a_command.arguments.IsEmpty)
            {
                m_master.msg_command(a_command, Array.Empty<string>());
                enable_recv_controls(false);
                enable_send_controls(false);
                enable_firmware_controls(false);
                enable_command_controls(false);
                return;
            }

            // Pop up dialog for command arguments if needed
            using var a_arguments_dialog = new Command_Arguments(a_command);
            _ = a_arguments_dialog.ShowDialog(this);

            if (a_arguments_dialog.result is not DialogResult.OK)
            {
                return;
            }

            m_master.msg_command(a_command, a_arguments_dialog.arguments);

            enable_recv_controls(false);
            enable_send_controls(false);
            enable_firmware_controls(false);
            enable_command_controls(false);
        };

    // Button click event to clear all message registers
    private void btn_clear_message_registers_Click(object? a_sender, EventArgs a_args)
    {
        foreach (var a_txt in m_message_register_control_map.Values)
        {
            a_txt.Clear();
        }
    }

    // Button click event to clear status register colors
    private void btn_clear_status_registers_Click(object? a_sender, EventArgs a_args)
    {
        foreach (var a_bits in m_status_register_control_map.Values)
        {
            foreach (var a_btn in a_bits)
            {
                a_btn.BackColor = COLOR_BIT_RSVD;
            }
        }
    }

    // Button click event to clear the received log
    private void btn_clear_recv_log_Click(object? a_sender, EventArgs a_args)
    {
        m_recv_log.Clear();
        m_txt_recv_log.Clear();
    }

    // Button click event to clear the sent log
    private void btn_clear_send_log_Click(object? a_sender, EventArgs a_args)
    {
        m_send_log.Clear();
        m_txt_send_log.Clear();
    }
}
