namespace program_ns.gui;

sealed partial class
Main_Form
{
    private System.ComponentModel.IContainer components = null;

    protected override void
    Dispose
    (bool disposing)
    {
        if(disposing && (components != null))
        {
            components.Dispose();
        }

        base.Dispose(disposing);
    }

    #region Windows Form Designer generated code

    private void InitializeComponent()
    {
        System.Windows.Forms.Label a_lbl_pack_id;
        System.Windows.Forms.Label a_lbl_send_query;
        System.Windows.Forms.TabPage a_tbpg_message_registers;
        System.Windows.Forms.TabControl a_tbctl_main;
        System.Windows.Forms.TabPage a_tbpg_status_registers;
        System.Windows.Forms.TabPage a_tbpg_recv_log;
        System.Windows.Forms.TabPage a_tbpg_send_log;
        System.Windows.Forms.Label a_lbl_recv_int;
        System.Windows.Forms.Label a_lbl_send_int;
        System.Windows.Forms.Label a_lbl_send_count;
        System.Windows.Forms.Panel a_pan_commands;
        System.Windows.Forms.GroupBox a_grp_recv;
        System.Windows.Forms.GroupBox a_grp_commands;
        System.Windows.Forms.Label a_lbl_port;
        System.Windows.Forms.Label a_lbl_baud;
        System.Windows.Forms.PictureBox a_pic_logo;
        System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Main_Form));
        m_tbl_message_registers = new System.Windows.Forms.TableLayoutPanel();
        m_tbl_status_registers = new System.Windows.Forms.TableLayoutPanel();
        m_txt_recv_log = new System.Windows.Forms.TextBox();
        m_txt_send_log = new System.Windows.Forms.TextBox();
        m_tbl_commands = new System.Windows.Forms.TableLayoutPanel();
        m_txt_recv_int = new System.Windows.Forms.TextBox();
        m_btn_recv_int_apply = new System.Windows.Forms.Button();
        m_btn_recv_stop_start = new System.Windows.Forms.Button();
        m_btn_activity = new System.Windows.Forms.Button();
        m_grp_send = new System.Windows.Forms.GroupBox();
        m_cmb_send_dest = new System.Windows.Forms.ComboBox();
        m_txt_send_int = new System.Windows.Forms.TextBox();
        m_txt_send_count = new System.Windows.Forms.TextBox();
        m_cmb_send_query = new System.Windows.Forms.ComboBox();
        m_btn_send_once = new System.Windows.Forms.Button();
        m_btn_send_start_stop = new System.Windows.Forms.Button();
        m_btn_init_can = new System.Windows.Forms.Button();
        m_btn_exit = new System.Windows.Forms.Button();
        m_btn_upgrade_firmware = new System.Windows.Forms.Button();
        m_prg_upgrade_progress = new System.Windows.Forms.ProgressBar();
        m_lbl_upgrade_progress = new System.Windows.Forms.Label();
        m_btn_enter_bootloader = new System.Windows.Forms.Button();
        m_btn_exit_bootloader = new System.Windows.Forms.Button();
        m_grp_firmware = new System.Windows.Forms.GroupBox();
        m_lbl_upgrade_status = new System.Windows.Forms.Label();
        m_btn_clear_message_registers = new System.Windows.Forms.Button();
        m_btn_clear_status_registers = new System.Windows.Forms.Button();
        m_btn_clear_recv_log = new System.Windows.Forms.Button();
        m_btn_clear_send_log = new System.Windows.Forms.Button();
        m_grp_serial = new System.Windows.Forms.GroupBox();
        m_btn_serial_open = new System.Windows.Forms.Button();
        m_txt_baud = new System.Windows.Forms.TextBox();
        m_cmb_port = new System.Windows.Forms.ComboBox();
        a_tbpg_data_logger = new System.Windows.Forms.TabPage();
        a_lbl_pack_id = new System.Windows.Forms.Label();
        a_lbl_send_query = new System.Windows.Forms.Label();
        a_tbpg_message_registers = new System.Windows.Forms.TabPage();
        a_tbctl_main = new System.Windows.Forms.TabControl();
        a_tbpg_status_registers = new System.Windows.Forms.TabPage();
        a_tbpg_recv_log = new System.Windows.Forms.TabPage();
        a_tbpg_send_log = new System.Windows.Forms.TabPage();
        a_lbl_recv_int = new System.Windows.Forms.Label();
        a_lbl_send_int = new System.Windows.Forms.Label();
        a_lbl_send_count = new System.Windows.Forms.Label();
        a_pan_commands = new System.Windows.Forms.Panel();
        a_grp_recv = new System.Windows.Forms.GroupBox();
        a_grp_commands = new System.Windows.Forms.GroupBox();
        a_lbl_port = new System.Windows.Forms.Label();
        a_lbl_baud = new System.Windows.Forms.Label();
        a_pic_logo = new System.Windows.Forms.PictureBox();

        a_tbpg_data_logger = new System.Windows.Forms.TabPage();
        m_dgv_data_logger = new System.Windows.Forms.DataGridView();
        m_btn_save_to_csv = new System.Windows.Forms.Button();

        a_tbpg_message_registers.SuspendLayout();
        a_tbctl_main.SuspendLayout();
        a_tbpg_status_registers.SuspendLayout();
        a_tbpg_recv_log.SuspendLayout();
        a_tbpg_send_log.SuspendLayout();
        a_pan_commands.SuspendLayout();
        a_grp_recv.SuspendLayout();
        a_grp_commands.SuspendLayout();
        ((System.ComponentModel.ISupportInitialize)a_pic_logo).BeginInit();
        m_grp_send.SuspendLayout();
        m_grp_firmware.SuspendLayout();
        m_grp_serial.SuspendLayout();
        SuspendLayout();
        // 
        // a_lbl_pack_id
        // 
        a_lbl_pack_id.AutoSize = true;
        a_lbl_pack_id.Font = new System.Drawing.Font("Courier New", 8.25F);
        a_lbl_pack_id.Location = new System.Drawing.Point(34, 25);
        a_lbl_pack_id.Name = "a_lbl_pack_id";
        a_lbl_pack_id.Size = new System.Drawing.Size(42, 14);
        a_lbl_pack_id.TabIndex = 7;
        a_lbl_pack_id.Text = "Dest:";
        // 
        // a_lbl_send_query
        // 
        a_lbl_send_query.AutoSize = true;
        a_lbl_send_query.Font = new System.Drawing.Font("Courier New", 8.25F);
        a_lbl_send_query.Location = new System.Drawing.Point(27, 108);
        a_lbl_send_query.Name = "a_lbl_send_query";
        a_lbl_send_query.Size = new System.Drawing.Size(49, 14);
        a_lbl_send_query.TabIndex = 17;
        a_lbl_send_query.Text = "Query:";
        // 
        // a_tbpg_message_registers
        // 
        a_tbpg_message_registers.AutoScroll = true;
        a_tbpg_message_registers.Controls.Add(m_tbl_message_registers);
        a_tbpg_message_registers.Location = new System.Drawing.Point(4, 25);
        a_tbpg_message_registers.Name = "a_tbpg_message_registers";
        a_tbpg_message_registers.Padding = new System.Windows.Forms.Padding(3);
        a_tbpg_message_registers.Size = new System.Drawing.Size(1690, 608);
        a_tbpg_message_registers.TabIndex = 0;
        a_tbpg_message_registers.Text = "Message Registers";
        a_tbpg_message_registers.UseVisualStyleBackColor = true;
        // 
        // m_tbl_message_registers
        // 
        m_tbl_message_registers.AutoScroll = true;
        m_tbl_message_registers.AutoSize = true;
        m_tbl_message_registers.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
        m_tbl_message_registers.ColumnCount = 2;
        m_tbl_message_registers.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_message_registers.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_message_registers.Location = new System.Drawing.Point(3, 3);
        m_tbl_message_registers.Name = "m_tbl_message_registers";
        m_tbl_message_registers.RowCount = 1;
        m_tbl_message_registers.RowStyles.Add(new System.Windows.Forms.RowStyle());
        m_tbl_message_registers.Size = new System.Drawing.Size(0, 0);
        m_tbl_message_registers.TabIndex = 0;
        // 
        // a_tbctl_main
        // 
        a_tbctl_main.Controls.Add(a_tbpg_message_registers);
        a_tbctl_main.Controls.Add(a_tbpg_status_registers);
        a_tbctl_main.Controls.Add(a_tbpg_recv_log);
        a_tbctl_main.Controls.Add(a_tbpg_send_log);
        a_tbctl_main.Controls.Add(a_tbpg_data_logger);
        a_tbctl_main.Font = new System.Drawing.Font("Courier New", 9.75F);
        a_tbctl_main.Location = new System.Drawing.Point(192, 12);
        a_tbctl_main.Name = "a_tbctl_main";
        a_tbctl_main.SelectedIndex = 0;
        a_tbctl_main.Size = new System.Drawing.Size(1698, 637);
        a_tbctl_main.TabIndex = 0;
        a_tbctl_main.TabStop = false;
        // 
        // a_tbpg_status_registers
        // 
        a_tbpg_status_registers.AutoScroll = true;
        a_tbpg_status_registers.Controls.Add(m_tbl_status_registers);
        a_tbpg_status_registers.Location = new System.Drawing.Point(4, 25);
        a_tbpg_status_registers.Name = "a_tbpg_status_registers";
        a_tbpg_status_registers.Padding = new System.Windows.Forms.Padding(3);
        a_tbpg_status_registers.Size = new System.Drawing.Size(1690, 608);
        a_tbpg_status_registers.TabIndex = 5;
        a_tbpg_status_registers.Text = "Status Registers";
        a_tbpg_status_registers.UseVisualStyleBackColor = true;
        // 
        // m_tbl_status_registers
        // 
        m_tbl_status_registers.AutoScroll = true;
        m_tbl_status_registers.AutoSize = true;
        m_tbl_status_registers.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
        m_tbl_status_registers.ColumnCount = 9;
        m_tbl_status_registers.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_status_registers.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_status_registers.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_status_registers.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_status_registers.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_status_registers.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_status_registers.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_status_registers.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_status_registers.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_status_registers.Location = new System.Drawing.Point(0, 0);
        m_tbl_status_registers.Name = "m_tbl_status_registers";
        m_tbl_status_registers.RowCount = 1;
        m_tbl_status_registers.RowStyles.Add(new System.Windows.Forms.RowStyle());
        m_tbl_status_registers.Size = new System.Drawing.Size(0, 0);
        m_tbl_status_registers.TabIndex = 0;
        // 
        // a_tbpg_recv_log
        // 
        a_tbpg_recv_log.Controls.Add(m_txt_recv_log);
        a_tbpg_recv_log.Location = new System.Drawing.Point(4, 25);
        a_tbpg_recv_log.Name = "a_tbpg_recv_log";
        a_tbpg_recv_log.Padding = new System.Windows.Forms.Padding(3);
        a_tbpg_recv_log.Size = new System.Drawing.Size(1690, 608);
        a_tbpg_recv_log.TabIndex = 6;
        a_tbpg_recv_log.Text = "Recv Log";
        a_tbpg_recv_log.UseVisualStyleBackColor = true;



        // 
        // m_txt_recv_log
        // 
        m_txt_recv_log.Font = new System.Drawing.Font("Courier New", 9F);
        m_txt_recv_log.Location = new System.Drawing.Point(6, 6);
        m_txt_recv_log.MaxLength = 0;
        m_txt_recv_log.Multiline = true;
        m_txt_recv_log.Name = "m_txt_recv_log";
        m_txt_recv_log.ReadOnly = true;
        m_txt_recv_log.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
        m_txt_recv_log.Size = new System.Drawing.Size(1678, 596);
        m_txt_recv_log.TabIndex = 0;
        m_txt_recv_log.TabStop = false;
        // 
        // a_tbpg_send_log
        // 
        a_tbpg_send_log.Controls.Add(m_txt_send_log);
        a_tbpg_send_log.Location = new System.Drawing.Point(4, 25);
        a_tbpg_send_log.Name = "a_tbpg_send_log";
        a_tbpg_send_log.Padding = new System.Windows.Forms.Padding(3);
        a_tbpg_send_log.Size = new System.Drawing.Size(1690, 608);
        a_tbpg_send_log.TabIndex = 7;
        a_tbpg_send_log.Text = "Send Log";
        a_tbpg_send_log.UseVisualStyleBackColor = true;
        // 
        // m_txt_send_log
        // 
        m_txt_send_log.Font = new System.Drawing.Font("Courier New", 9F);
        m_txt_send_log.Location = new System.Drawing.Point(6, 6);
        m_txt_send_log.MaxLength = 0;
        m_txt_send_log.Multiline = true;
        m_txt_send_log.Name = "m_txt_send_log";
        m_txt_send_log.ReadOnly = true;
        m_txt_send_log.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
        m_txt_send_log.Size = new System.Drawing.Size(1678, 596);
        m_txt_send_log.TabIndex = 0;
        m_txt_send_log.TabStop = false;
        // 
        // a_lbl_recv_int
        // 
        a_lbl_recv_int.AutoSize = true;
        a_lbl_recv_int.Font = new System.Drawing.Font("Courier New", 8.25F);
        a_lbl_recv_int.Location = new System.Drawing.Point(6, 24);
        a_lbl_recv_int.Name = "a_lbl_recv_int";
        a_lbl_recv_int.Size = new System.Drawing.Size(70, 14);
        a_lbl_recv_int.TabIndex = 20;
        a_lbl_recv_int.Text = "Interval:";
        // 
        // a_lbl_send_int
        // 
        a_lbl_send_int.AutoSize = true;
        a_lbl_send_int.Font = new System.Drawing.Font("Courier New", 8.25F);
        a_lbl_send_int.Location = new System.Drawing.Point(6, 54);
        a_lbl_send_int.Name = "a_lbl_send_int";
        a_lbl_send_int.Size = new System.Drawing.Size(70, 14);
        a_lbl_send_int.TabIndex = 21;
        a_lbl_send_int.Text = "Interval:";
        // 
        // a_lbl_send_count
        // 
        a_lbl_send_count.AutoSize = true;
        a_lbl_send_count.Font = new System.Drawing.Font("Courier New", 8.25F);
        a_lbl_send_count.Location = new System.Drawing.Point(27, 81);
        a_lbl_send_count.Name = "a_lbl_send_count";
        a_lbl_send_count.Size = new System.Drawing.Size(49, 14);
        a_lbl_send_count.TabIndex = 22;
        a_lbl_send_count.Text = "Count:";
        // 
        // a_pan_commands
        // 
        a_pan_commands.AutoScroll = true;
        a_pan_commands.Controls.Add(m_tbl_commands);
        a_pan_commands.Location = new System.Drawing.Point(6, 21);
        a_pan_commands.Name = "a_pan_commands";
        a_pan_commands.Size = new System.Drawing.Size(1479, 128);
        a_pan_commands.TabIndex = 0;
        // 
        // m_tbl_commands
        // 
        m_tbl_commands.AutoScroll = true;
        m_tbl_commands.AutoSize = true;
        m_tbl_commands.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
        m_tbl_commands.ColumnCount = 5;
        m_tbl_commands.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_commands.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_commands.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_commands.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_commands.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_commands.Location = new System.Drawing.Point(0, 0);
        m_tbl_commands.Name = "m_tbl_commands";
        m_tbl_commands.RowCount = 1;
        m_tbl_commands.RowStyles.Add(new System.Windows.Forms.RowStyle());
        m_tbl_commands.Size = new System.Drawing.Size(0, 0);
        m_tbl_commands.TabIndex = 0;
        // 
        // a_grp_recv
        // 
        a_grp_recv.Controls.Add(a_lbl_recv_int);
        a_grp_recv.Controls.Add(m_txt_recv_int);
        a_grp_recv.Controls.Add(m_btn_recv_int_apply);
        a_grp_recv.Controls.Add(m_btn_recv_stop_start);
        a_grp_recv.Controls.Add(m_btn_activity);
        a_grp_recv.Font = new System.Drawing.Font("Courier New", 9.75F, System.Drawing.FontStyle.Bold);
        a_grp_recv.Location = new System.Drawing.Point(4, 163);
        a_grp_recv.Name = "a_grp_recv";
        a_grp_recv.Size = new System.Drawing.Size(182, 140);
        a_grp_recv.TabIndex = 0;
        a_grp_recv.TabStop = false;
        a_grp_recv.Text = "Recv:";
        // 
        // m_txt_recv_int
        // 
        m_txt_recv_int.Enabled = false;
        m_txt_recv_int.Font = new System.Drawing.Font("Courier New", 9F);
        m_txt_recv_int.Location = new System.Drawing.Point(82, 20);
        m_txt_recv_int.MaxLength = 4;
        m_txt_recv_int.Name = "m_txt_recv_int";
        m_txt_recv_int.Size = new System.Drawing.Size(94, 21);
        m_txt_recv_int.TabIndex = 1;
        // 
        // m_btn_recv_int_apply
        // 
        m_btn_recv_int_apply.Enabled = false;
        m_btn_recv_int_apply.Font = new System.Drawing.Font("Courier New", 9F);
        m_btn_recv_int_apply.Location = new System.Drawing.Point(82, 47);
        m_btn_recv_int_apply.Name = "m_btn_recv_int_apply";
        m_btn_recv_int_apply.Size = new System.Drawing.Size(94, 23);
        m_btn_recv_int_apply.TabIndex = 0;
        m_btn_recv_int_apply.TabStop = false;
        m_btn_recv_int_apply.Text = "Apply";
        m_btn_recv_int_apply.UseVisualStyleBackColor = true;
        m_btn_recv_int_apply.Click += btn_recv_int_apply_Click;
        // 
        // m_btn_recv_stop_start
        // 
        m_btn_recv_stop_start.BackColor = System.Drawing.Color.Pink;
        m_btn_recv_stop_start.Enabled = false;
        m_btn_recv_stop_start.Font = new System.Drawing.Font("Courier New", 9F);
        m_btn_recv_stop_start.Location = new System.Drawing.Point(6, 76);
        m_btn_recv_stop_start.Name = "m_btn_recv_stop_start";
        m_btn_recv_stop_start.Size = new System.Drawing.Size(170, 23);
        m_btn_recv_stop_start.TabIndex = 0;
        m_btn_recv_stop_start.TabStop = false;
        m_btn_recv_stop_start.Text = "Stop";
        m_btn_recv_stop_start.UseVisualStyleBackColor = false;
        m_btn_recv_stop_start.Click += btn_recv_int_stop_start_Click;
        // 
        // m_btn_activity
        // 
        m_btn_activity.BackColor = System.Drawing.Color.Pink;
        m_btn_activity.Enabled = false;
        m_btn_activity.Font = new System.Drawing.Font("Courier New", 9F, System.Drawing.FontStyle.Bold);
        m_btn_activity.Location = new System.Drawing.Point(6, 105);
        m_btn_activity.Name = "m_btn_activity";
        m_btn_activity.Size = new System.Drawing.Size(170, 23);
        m_btn_activity.TabIndex = 0;
        m_btn_activity.TabStop = false;
        m_btn_activity.Text = "Bus Activity";
        m_btn_activity.UseVisualStyleBackColor = false;
        // 
        // a_grp_commands
        // 
        a_grp_commands.Controls.Add(a_pan_commands);
        a_grp_commands.Font = new System.Drawing.Font("Courier New", 9.75F, System.Drawing.FontStyle.Bold);
        a_grp_commands.Location = new System.Drawing.Point(4, 696);
        a_grp_commands.Name = "a_grp_commands";
        a_grp_commands.Size = new System.Drawing.Size(1491, 155);
        a_grp_commands.TabIndex = 0;
        a_grp_commands.TabStop = false;
        a_grp_commands.Text = "Commands:";
        // 
        // a_lbl_port
        // 
        a_lbl_port.AutoSize = true;
        a_lbl_port.Font = new System.Drawing.Font("Courier New", 9F);
        a_lbl_port.Location = new System.Drawing.Point(6, 22);
        a_lbl_port.Name = "a_lbl_port";
        a_lbl_port.Size = new System.Drawing.Size(42, 15);
        a_lbl_port.TabIndex = 2;
        a_lbl_port.Text = "Port:";
        // 
        // a_lbl_baud
        // 
        a_lbl_baud.AutoSize = true;
        a_lbl_baud.Font = new System.Drawing.Font("Courier New", 9F);
        a_lbl_baud.Location = new System.Drawing.Point(6, 50);
        a_lbl_baud.Name = "a_lbl_baud";
        a_lbl_baud.Size = new System.Drawing.Size(42, 15);
        a_lbl_baud.TabIndex = 3;
        a_lbl_baud.Text = "Baud:";
        // 
        // a_pic_logo
        // 
        a_pic_logo.Image = (System.Drawing.Image)resources.GetObject("a_pic_logo.Image");
        a_pic_logo.Location = new System.Drawing.Point(1587, 655);
        a_pic_logo.MaximumSize = new System.Drawing.Size(305, 88);
        a_pic_logo.MinimumSize = new System.Drawing.Size(305, 88);
        a_pic_logo.Name = "a_pic_logo";
        a_pic_logo.Size = new System.Drawing.Size(305, 88);
        a_pic_logo.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage;
        a_pic_logo.TabIndex = 7;
        a_pic_logo.TabStop = false;
        // 
        // m_grp_send
        // 
        m_grp_send.Controls.Add(m_cmb_send_dest);
        m_grp_send.Controls.Add(a_lbl_send_count);
        m_grp_send.Controls.Add(a_lbl_send_int);
        m_grp_send.Controls.Add(m_txt_send_int);
        m_grp_send.Controls.Add(m_txt_send_count);
        m_grp_send.Controls.Add(m_cmb_send_query);
        m_grp_send.Controls.Add(a_lbl_send_query);
        m_grp_send.Controls.Add(m_btn_send_once);
        m_grp_send.Controls.Add(a_lbl_pack_id);
        m_grp_send.Controls.Add(m_btn_send_start_stop);
        m_grp_send.Font = new System.Drawing.Font("Courier New", 9.75F, System.Drawing.FontStyle.Bold);
        m_grp_send.Location = new System.Drawing.Point(4, 309);
        m_grp_send.Name = "m_grp_send";
        m_grp_send.Size = new System.Drawing.Size(182, 196);
        m_grp_send.TabIndex = 0;
        m_grp_send.TabStop = false;
        m_grp_send.Text = "Send:";
        m_grp_send.Visible = false;
        // 
        // m_cmb_send_dest
        // 
        m_cmb_send_dest.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
        m_cmb_send_dest.Enabled = false;
        m_cmb_send_dest.Font = new System.Drawing.Font("Courier New", 9F);
        m_cmb_send_dest.FormattingEnabled = true;
        m_cmb_send_dest.Location = new System.Drawing.Point(82, 21);
        m_cmb_send_dest.Name = "m_cmb_send_dest";
        m_cmb_send_dest.Size = new System.Drawing.Size(94, 23);
        m_cmb_send_dest.TabIndex = 0;
        m_cmb_send_dest.TabStop = false;
        m_cmb_send_dest.SelectedIndexChanged += cmb_send_dest_SelectedIndexChanged;
        // 
        // m_txt_send_int
        // 
        m_txt_send_int.Enabled = false;
        m_txt_send_int.Font = new System.Drawing.Font("Courier New", 9F);
        m_txt_send_int.Location = new System.Drawing.Point(82, 50);
        m_txt_send_int.MaxLength = 8;
        m_txt_send_int.Name = "m_txt_send_int";
        m_txt_send_int.Size = new System.Drawing.Size(94, 21);
        m_txt_send_int.TabIndex = 2;
        // 
        // m_txt_send_count
        // 
        m_txt_send_count.Enabled = false;
        m_txt_send_count.Font = new System.Drawing.Font("Courier New", 9F);
        m_txt_send_count.Location = new System.Drawing.Point(82, 77);
        m_txt_send_count.MaxLength = 12;
        m_txt_send_count.Name = "m_txt_send_count";
        m_txt_send_count.Size = new System.Drawing.Size(94, 21);
        m_txt_send_count.TabIndex = 3;
        // 
        // m_cmb_send_query
        // 
        m_cmb_send_query.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
        m_cmb_send_query.Enabled = false;
        m_cmb_send_query.Font = new System.Drawing.Font("Courier New", 9F);
        m_cmb_send_query.FormattingEnabled = true;
        m_cmb_send_query.Location = new System.Drawing.Point(82, 104);
        m_cmb_send_query.Name = "m_cmb_send_query";
        m_cmb_send_query.Size = new System.Drawing.Size(94, 23);
        m_cmb_send_query.TabIndex = 0;
        m_cmb_send_query.TabStop = false;
        // 
        // m_btn_send_once
        // 
        m_btn_send_once.Enabled = false;
        m_btn_send_once.Font = new System.Drawing.Font("Courier New", 9F);
        m_btn_send_once.Location = new System.Drawing.Point(6, 162);
        m_btn_send_once.Name = "m_btn_send_once";
        m_btn_send_once.Size = new System.Drawing.Size(170, 23);
        m_btn_send_once.TabIndex = 0;
        m_btn_send_once.TabStop = false;
        m_btn_send_once.Text = "Send Once";
        m_btn_send_once.UseVisualStyleBackColor = true;
        m_btn_send_once.Click += btn_send_once_Click;
        // 
        // m_btn_send_start_stop
        // 
        m_btn_send_start_stop.BackColor = System.Drawing.Color.LightGreen;
        m_btn_send_start_stop.Enabled = false;
        m_btn_send_start_stop.Font = new System.Drawing.Font("Courier New", 9F);
        m_btn_send_start_stop.Location = new System.Drawing.Point(6, 133);
        m_btn_send_start_stop.Name = "m_btn_send_start_stop";
        m_btn_send_start_stop.Size = new System.Drawing.Size(170, 23);
        m_btn_send_start_stop.TabIndex = 0;
        m_btn_send_start_stop.TabStop = false;
        m_btn_send_start_stop.Text = "Start";
        m_btn_send_start_stop.UseVisualStyleBackColor = false;
        m_btn_send_start_stop.Click += btn_send_start_stop_Click;
        // 
        // m_btn_init_can
        // 
        m_btn_init_can.Font = new System.Drawing.Font("Courier New", 12F, System.Drawing.FontStyle.Bold);
        m_btn_init_can.Location = new System.Drawing.Point(4, 11);
        m_btn_init_can.Name = "m_btn_init_can";
        m_btn_init_can.Size = new System.Drawing.Size(182, 70);
        m_btn_init_can.TabIndex = 0;
        m_btn_init_can.TabStop = false;
        m_btn_init_can.Text = "Init CAN";
        m_btn_init_can.UseVisualStyleBackColor = true;
        m_btn_init_can.Visible = false;
        m_btn_init_can.Click += btn_init_can_Click;
        // 
        // m_btn_exit
        // 
        m_btn_exit.Font = new System.Drawing.Font("Courier New", 12F, System.Drawing.FontStyle.Bold);
        m_btn_exit.Location = new System.Drawing.Point(4, 87);
        m_btn_exit.Name = "m_btn_exit";
        m_btn_exit.Size = new System.Drawing.Size(182, 70);
        m_btn_exit.TabIndex = 0;
        m_btn_exit.TabStop = false;
        m_btn_exit.Text = "Exit";
        m_btn_exit.UseVisualStyleBackColor = true;
        m_btn_exit.Click += btn_exit_Click;
        // 
        // m_btn_upgrade_firmware
        // 
        m_btn_upgrade_firmware.Enabled = false;
        m_btn_upgrade_firmware.Font = new System.Drawing.Font("Courier New", 9F);
        m_btn_upgrade_firmware.Location = new System.Drawing.Point(6, 20);
        m_btn_upgrade_firmware.Name = "m_btn_upgrade_firmware";
        m_btn_upgrade_firmware.Size = new System.Drawing.Size(170, 23);
        m_btn_upgrade_firmware.TabIndex = 0;
        m_btn_upgrade_firmware.TabStop = false;
        m_btn_upgrade_firmware.Text = "Upgrade";
        m_btn_upgrade_firmware.UseVisualStyleBackColor = true;
        m_btn_upgrade_firmware.Click += btn_upgrade_firmware_Click;
        // 
        // m_prg_upgrade_progress
        // 
        m_prg_upgrade_progress.Location = new System.Drawing.Point(192, 655);
        m_prg_upgrade_progress.Name = "m_prg_upgrade_progress";
        m_prg_upgrade_progress.Size = new System.Drawing.Size(889, 35);
        m_prg_upgrade_progress.TabIndex = 0;
        m_prg_upgrade_progress.Visible = false;
        // 
        // m_lbl_upgrade_progress
        // 
        m_lbl_upgrade_progress.AutoSize = true;
        m_lbl_upgrade_progress.Font = new System.Drawing.Font("Courier New", 12F);
        m_lbl_upgrade_progress.Location = new System.Drawing.Point(8, 655);
        m_lbl_upgrade_progress.Name = "m_lbl_upgrade_progress";
        m_lbl_upgrade_progress.Size = new System.Drawing.Size(178, 18);
        m_lbl_upgrade_progress.TabIndex = 0;
        m_lbl_upgrade_progress.Text = "Upgrade Progress:";
        m_lbl_upgrade_progress.Visible = false;
        // 
        // m_btn_enter_bootloader
        // 
        m_btn_enter_bootloader.Enabled = false;
        m_btn_enter_bootloader.Font = new System.Drawing.Font("Courier New", 9F);
        m_btn_enter_bootloader.Location = new System.Drawing.Point(6, 49);
        m_btn_enter_bootloader.Name = "m_btn_enter_bootloader";
        m_btn_enter_bootloader.Size = new System.Drawing.Size(170, 23);
        m_btn_enter_bootloader.TabIndex = 0;
        m_btn_enter_bootloader.TabStop = false;
        m_btn_enter_bootloader.Text = "Enter Bootloader";
        m_btn_enter_bootloader.UseVisualStyleBackColor = true;
        m_btn_enter_bootloader.Click += btn_enter_bootloader_Click;
        // 
        // m_btn_exit_bootloader
        // 
        m_btn_exit_bootloader.Enabled = false;
        m_btn_exit_bootloader.Font = new System.Drawing.Font("Courier New", 9F);
        m_btn_exit_bootloader.Location = new System.Drawing.Point(6, 78);
        m_btn_exit_bootloader.Name = "m_btn_exit_bootloader";
        m_btn_exit_bootloader.Size = new System.Drawing.Size(170, 23);
        m_btn_exit_bootloader.TabIndex = 0;
        m_btn_exit_bootloader.TabStop = false;
        m_btn_exit_bootloader.Text = "Exit Bootloader";
        m_btn_exit_bootloader.UseVisualStyleBackColor = true;
        m_btn_exit_bootloader.Click += btn_exit_bootloader_Click;
        // 
        // m_grp_firmware
        // 
        m_grp_firmware.Controls.Add(m_btn_upgrade_firmware);
        m_grp_firmware.Controls.Add(m_btn_enter_bootloader);
        m_grp_firmware.Controls.Add(m_btn_exit_bootloader);
        m_grp_firmware.Font = new System.Drawing.Font("Courier New", 9.75F, System.Drawing.FontStyle.Bold);
        m_grp_firmware.Location = new System.Drawing.Point(4, 539);
        m_grp_firmware.Name = "m_grp_firmware";
        m_grp_firmware.Size = new System.Drawing.Size(182, 110);
        m_grp_firmware.TabIndex = 0;
        m_grp_firmware.TabStop = false;
        m_grp_firmware.Text = "Firmware:";
        m_grp_firmware.Visible = false;
        // 
        // m_lbl_upgrade_status
        // 
        m_lbl_upgrade_status.AutoSize = true;
        m_lbl_upgrade_status.Font = new System.Drawing.Font("Courier New", 12F);
        m_lbl_upgrade_status.Location = new System.Drawing.Point(1087, 655);
        m_lbl_upgrade_status.Name = "m_lbl_upgrade_status";
        m_lbl_upgrade_status.Size = new System.Drawing.Size(408, 18);
        m_lbl_upgrade_status.TabIndex = 0;
        m_lbl_upgrade_status.Text = "UPGRADE-STATUS-MESSAGE------------------";
        m_lbl_upgrade_status.Visible = false;
        // 
        // m_btn_clear_message_registers
        // 
        m_btn_clear_message_registers.Font = new System.Drawing.Font("Courier New", 12F);
        m_btn_clear_message_registers.Location = new System.Drawing.Point(1503, 749);
        m_btn_clear_message_registers.Name = "m_btn_clear_message_registers";
        m_btn_clear_message_registers.Size = new System.Drawing.Size(389, 30);
        m_btn_clear_message_registers.TabIndex = 0;
        m_btn_clear_message_registers.TabStop = false;
        m_btn_clear_message_registers.Text = "Clear Message Registers";
        m_btn_clear_message_registers.UseVisualStyleBackColor = true;
        m_btn_clear_message_registers.Click += btn_clear_message_registers_Click;
        // 
        // m_btn_clear_status_registers
        // 
        m_btn_clear_status_registers.Font = new System.Drawing.Font("Courier New", 12F);
        m_btn_clear_status_registers.Location = new System.Drawing.Point(1503, 785);
        m_btn_clear_status_registers.Name = "m_btn_clear_status_registers";
        m_btn_clear_status_registers.Size = new System.Drawing.Size(389, 30);
        m_btn_clear_status_registers.TabIndex = 0;
        m_btn_clear_status_registers.TabStop = false;
        m_btn_clear_status_registers.Text = "Clear Status Registers";
        m_btn_clear_status_registers.UseVisualStyleBackColor = true;
        m_btn_clear_status_registers.Click += btn_clear_status_registers_Click;
        // 
        // m_btn_clear_recv_log
        // 
        m_btn_clear_recv_log.Font = new System.Drawing.Font("Courier New", 12F);
        m_btn_clear_recv_log.Location = new System.Drawing.Point(1503, 821);
        m_btn_clear_recv_log.Name = "m_btn_clear_recv_log";
        m_btn_clear_recv_log.Size = new System.Drawing.Size(190, 30);
        m_btn_clear_recv_log.TabIndex = 0;
        m_btn_clear_recv_log.TabStop = false;
        m_btn_clear_recv_log.Text = "Clear Recv Log";
        m_btn_clear_recv_log.UseVisualStyleBackColor = true;
        m_btn_clear_recv_log.Click += btn_clear_recv_log_Click;
        // 
        // m_btn_clear_send_log
        // 
        m_btn_clear_send_log.Font = new System.Drawing.Font("Courier New", 12F);
        m_btn_clear_send_log.Location = new System.Drawing.Point(1702, 821);
        m_btn_clear_send_log.Name = "m_btn_clear_send_log";
        m_btn_clear_send_log.Size = new System.Drawing.Size(190, 30);
        m_btn_clear_send_log.TabIndex = 0;
        m_btn_clear_send_log.TabStop = false;
        m_btn_clear_send_log.Text = "Clear Send Log";
        m_btn_clear_send_log.UseVisualStyleBackColor = true;
        m_btn_clear_send_log.Click += btn_clear_send_log_Click;
        // 
        // m_grp_serial
        // 
        m_grp_serial.Controls.Add(m_btn_serial_open);
        m_grp_serial.Controls.Add(a_lbl_baud);
        m_grp_serial.Controls.Add(a_lbl_port);
        m_grp_serial.Controls.Add(m_txt_baud);
        m_grp_serial.Controls.Add(m_cmb_port);
        m_grp_serial.Font = new System.Drawing.Font("Courier New", 9F, System.Drawing.FontStyle.Bold);
        m_grp_serial.Location = new System.Drawing.Point(4, 5);
        m_grp_serial.Name = "m_grp_serial";
        m_grp_serial.Size = new System.Drawing.Size(182, 76);
        m_grp_serial.TabIndex = 0;
        m_grp_serial.TabStop = false;
        m_grp_serial.Text = "Serial:";
        m_grp_serial.Visible = false;
        // 
        // m_btn_serial_open
        // 
        m_btn_serial_open.Enabled = false;
        m_btn_serial_open.Font = new System.Drawing.Font("Courier New", 9F);
        m_btn_serial_open.Location = new System.Drawing.Point(133, 20);
        m_btn_serial_open.Name = "m_btn_serial_open";
        m_btn_serial_open.Size = new System.Drawing.Size(43, 48);
        m_btn_serial_open.TabIndex = 0;
        m_btn_serial_open.TabStop = false;
        m_btn_serial_open.Text = "Open";
        m_btn_serial_open.UseVisualStyleBackColor = true;
        m_btn_serial_open.Click += btn_serial_open_Click;
        // 
        // m_txt_baud
        // 
        m_txt_baud.Font = new System.Drawing.Font("Courier New", 8.25F);
        m_txt_baud.Location = new System.Drawing.Point(54, 48);
        m_txt_baud.MaxLength = 9;
        m_txt_baud.Name = "m_txt_baud";
        m_txt_baud.Size = new System.Drawing.Size(73, 20);
        m_txt_baud.TabIndex = 0;
        m_txt_baud.TabStop = false;
        // 
        // m_cmb_port
        // 
        m_cmb_port.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
        m_cmb_port.Font = new System.Drawing.Font("Courier New", 8.25F);
        m_cmb_port.FormattingEnabled = true;
        m_cmb_port.Location = new System.Drawing.Point(54, 20);
        m_cmb_port.Name = "m_cmb_port";
        m_cmb_port.Size = new System.Drawing.Size(73, 22);
        m_cmb_port.TabIndex = 0;
        m_cmb_port.TabStop = false;
        // 
        // a_tbpg_data_logger
        // 
        a_tbpg_data_logger.Location = new System.Drawing.Point(4, 25);
        a_tbpg_data_logger.Name = "a_tbpg_data_logger";
        a_tbpg_data_logger.Padding = new System.Windows.Forms.Padding(3);
        a_tbpg_data_logger.Size = new System.Drawing.Size(1690, 608);
        a_tbpg_data_logger.TabIndex = 8;
        a_tbpg_data_logger.Text = "Datalog";
        a_tbpg_data_logger.UseVisualStyleBackColor = true;

        // 
        // m_dgv_data_logger
        // 
        m_dgv_data_logger.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
        m_dgv_data_logger.Location = new System.Drawing.Point(6, 6);
        m_dgv_data_logger.Name = "m_dgv_data_logger";
        m_dgv_data_logger.Size = new System.Drawing.Size(1678, 550);
        m_dgv_data_logger.TabIndex = 0;
        // 
        // m_btn_save_to_csv
        // 
        m_btn_save_to_csv.Font = new System.Drawing.Font("Courier New", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
        m_btn_save_to_csv.Location = new System.Drawing.Point(6, 565);
        m_btn_save_to_csv.Name = "m_btn_save_to_csv";
        m_btn_save_to_csv.Size = new System.Drawing.Size(170, 30);
        m_btn_save_to_csv.TabIndex = 1;
        m_btn_save_to_csv.Text = "Save to CSV";
        m_btn_save_to_csv.UseVisualStyleBackColor = true;
        //m_btn_save_to_csv.Click += m_btn_save_to_csv_click;
        // 
        // Main_Form
        // 
        AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
        AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
        BackColor = System.Drawing.Color.LightSteelBlue;
        ClientSize = new System.Drawing.Size(1904, 861);
        Controls.Add(a_pic_logo);
        Controls.Add(m_grp_serial);
        Controls.Add(m_btn_init_can);
        Controls.Add(m_btn_clear_send_log);
        Controls.Add(m_btn_clear_recv_log);
        Controls.Add(m_btn_clear_status_registers);
        Controls.Add(m_btn_clear_message_registers);
        Controls.Add(m_grp_firmware);
        Controls.Add(a_grp_commands);
        Controls.Add(m_lbl_upgrade_status);
        Controls.Add(m_grp_send);
        Controls.Add(a_grp_recv);
        Controls.Add(m_lbl_upgrade_progress);
        Controls.Add(m_prg_upgrade_progress);
        Controls.Add(a_tbctl_main);
        Controls.Add(m_btn_exit);
        Font = new System.Drawing.Font("Courier New", 9F);
        Icon = (System.Drawing.Icon)resources.GetObject("$this.Icon");
        Margin = new System.Windows.Forms.Padding(2, 1, 2, 1);
        MaximizeBox = false;
        MaximumSize = new System.Drawing.Size(1920, 900);
        MinimumSize = new System.Drawing.Size(1920, 900);
        Name = "Main_Form";
        Text = "Connector";
        FormClosing += Main_Form_FormClosing;
        Load += Main_Form_Load;
        a_tbpg_message_registers.ResumeLayout(false);
        a_tbpg_message_registers.PerformLayout();
        a_tbctl_main.ResumeLayout(false);
        a_tbpg_status_registers.ResumeLayout(false);
        a_tbpg_status_registers.PerformLayout();
        a_tbpg_recv_log.ResumeLayout(false);
        a_tbpg_recv_log.PerformLayout();
        a_tbpg_send_log.ResumeLayout(false);
        a_tbpg_send_log.PerformLayout();
        a_pan_commands.ResumeLayout(false);
        a_pan_commands.PerformLayout();
        a_grp_recv.ResumeLayout(false);
        a_grp_recv.PerformLayout();
        a_grp_commands.ResumeLayout(false);
        ((System.ComponentModel.ISupportInitialize)a_pic_logo).EndInit();
        m_grp_send.ResumeLayout(false);
        m_grp_send.PerformLayout();
        m_grp_firmware.ResumeLayout(false);
        m_grp_serial.ResumeLayout(false);
        m_grp_serial.PerformLayout();
        ResumeLayout(false);
        PerformLayout();
    }

    #endregion
    private System.Windows.Forms.TextBox m_txt_recv_int;
    private System.Windows.Forms.Button m_btn_recv_int_apply;
    private System.Windows.Forms.TextBox m_txt_send_int;
    private System.Windows.Forms.TextBox m_txt_send_count;
    private System.Windows.Forms.ComboBox m_cmb_send_query;
    private System.Windows.Forms.Button m_btn_send_start_stop;
    private System.Windows.Forms.Button m_btn_send_once;
    private System.Windows.Forms.Button m_btn_recv_stop_start;
    private System.Windows.Forms.Button m_btn_upgrade_firmware;
    private System.Windows.Forms.Button m_btn_init_can;
    private System.Windows.Forms.Button m_btn_exit;
    private System.Windows.Forms.ProgressBar m_prg_upgrade_progress;
    private System.Windows.Forms.Label m_lbl_upgrade_progress;
    private System.Windows.Forms.Button m_btn_activity;
    private System.Windows.Forms.Button m_btn_enter_bootloader;
    private System.Windows.Forms.Button m_btn_exit_bootloader;
    private System.Windows.Forms.GroupBox m_grp_firmware;
    private System.Windows.Forms.ComboBox m_cmb_send_dest;
    private System.Windows.Forms.Label m_lbl_upgrade_status;
    private System.Windows.Forms.TextBox m_txt_recv_log;
    private System.Windows.Forms.TextBox m_txt_send_log;
    private System.Windows.Forms.TableLayoutPanel m_tbl_message_registers;
    private System.Windows.Forms.TableLayoutPanel m_tbl_status_registers;
    private System.Windows.Forms.TableLayoutPanel m_tbl_commands;
    private System.Windows.Forms.Button m_btn_clear_message_registers;
    private System.Windows.Forms.Button m_btn_clear_status_registers;
    private System.Windows.Forms.Button m_btn_clear_recv_log;
    private System.Windows.Forms.Button m_btn_clear_send_log;
    private System.Windows.Forms.GroupBox m_grp_send;
    private System.Windows.Forms.GroupBox m_grp_serial;
    private System.Windows.Forms.ComboBox m_cmb_port;
    private System.Windows.Forms.TextBox m_txt_baud;
    private System.Windows.Forms.Button m_btn_serial_open;
    private System.Windows.Forms.TabPage a_tbpg_data_logger;
    private System.Windows.Forms.DataGridView m_dgv_data_logger;
    private System.Windows.Forms.Button m_btn_save_to_csv;
}

