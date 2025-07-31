namespace program_ns.gui;

sealed partial class
Command_Arguments
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

    private void
    InitializeComponent()
    {
        System.Windows.Forms.GroupBox a_grp_arguments;
        System.Windows.Forms.Panel a_pan_arguments;
        var resources = new System.ComponentModel.ComponentResourceManager(typeof(Command_Arguments));
        m_tbl_arguments = new System.Windows.Forms.TableLayoutPanel();
        m_btn_ok = new System.Windows.Forms.Button();
        m_btn_cancel = new System.Windows.Forms.Button();
        a_grp_arguments = new System.Windows.Forms.GroupBox();
        a_pan_arguments = new System.Windows.Forms.Panel();
        a_grp_arguments.SuspendLayout();
        a_pan_arguments.SuspendLayout();
        SuspendLayout();
        // 
        // a_grp_arguments
        // 
        a_grp_arguments.Controls.Add(a_pan_arguments);
        a_grp_arguments.Font = new System.Drawing.Font("Courier New", 9.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point);
        a_grp_arguments.Location = new System.Drawing.Point(12, 12);
        a_grp_arguments.Name = "a_grp_arguments";
        a_grp_arguments.Size = new System.Drawing.Size(506, 230);
        a_grp_arguments.TabIndex = 0;
        a_grp_arguments.TabStop = false;
        a_grp_arguments.Text = "Arguments:";
        // 
        // a_pan_arguments
        // 
        a_pan_arguments.AutoScroll = true;
        a_pan_arguments.Controls.Add(m_tbl_arguments);
        a_pan_arguments.Location = new System.Drawing.Point(6, 21);
        a_pan_arguments.Name = "a_pan_arguments";
        a_pan_arguments.Size = new System.Drawing.Size(494, 203);
        a_pan_arguments.TabIndex = 0;
        // 
        // m_tbl_arguments
        // 
        m_tbl_arguments.AutoScroll = true;
        m_tbl_arguments.AutoSize = true;
        m_tbl_arguments.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
        m_tbl_arguments.ColumnCount = 2;
        m_tbl_arguments.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_arguments.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle());
        m_tbl_arguments.Location = new System.Drawing.Point(3, 3);
        m_tbl_arguments.Name = "m_tbl_arguments";
        m_tbl_arguments.RowCount = 1;
        m_tbl_arguments.RowStyles.Add(new System.Windows.Forms.RowStyle());
        m_tbl_arguments.Size = new System.Drawing.Size(0, 0);
        m_tbl_arguments.TabIndex = 0;
        // 
        // m_btn_ok
        // 
        m_btn_ok.Font = new System.Drawing.Font("Courier New", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point);
        m_btn_ok.Location = new System.Drawing.Point(12, 248);
        m_btn_ok.Name = "m_btn_ok";
        m_btn_ok.Size = new System.Drawing.Size(250, 40);
        m_btn_ok.TabIndex = 0;
        m_btn_ok.TabStop = false;
        m_btn_ok.Text = "OK";
        m_btn_ok.UseVisualStyleBackColor = true;
        m_btn_ok.Click += btn_ok_Click;
        // 
        // m_btn_cancel
        // 
        m_btn_cancel.Font = new System.Drawing.Font("Courier New", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point);
        m_btn_cancel.Location = new System.Drawing.Point(268, 248);
        m_btn_cancel.Name = "m_btn_cancel";
        m_btn_cancel.Size = new System.Drawing.Size(250, 40);
        m_btn_cancel.TabIndex = 0;
        m_btn_cancel.TabStop = false;
        m_btn_cancel.Text = "Cancel";
        m_btn_cancel.UseVisualStyleBackColor = true;
        m_btn_cancel.Click += btn_cancel_Click;
        // 
        // command_arguments
        // 
        AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
        AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
        BackColor = System.Drawing.Color.LightSteelBlue;
        ClientSize = new System.Drawing.Size(530, 300);
        Controls.Add(m_btn_cancel);
        Controls.Add(m_btn_ok);
        Controls.Add(a_grp_arguments);
        Font = new System.Drawing.Font("Courier New", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
        Icon = (System.Drawing.Icon)resources.GetObject("$this.Icon");
        MaximizeBox = false;
        MaximumSize = new System.Drawing.Size(546, 339);
        MinimizeBox = false;
        MinimumSize = new System.Drawing.Size(546, 339);
        Name = "command_arguments";
        ShowIcon = false;
        ShowInTaskbar = false;
        StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
        Text = "Command Arguments";
        TopMost = true;
        Load += Command_Arguments_Load;
        a_grp_arguments.ResumeLayout(false);
        a_pan_arguments.ResumeLayout(false);
        a_pan_arguments.PerformLayout();
        ResumeLayout(false);
    }

    #endregion

    private System.Windows.Forms.Button m_btn_ok;
    private System.Windows.Forms.Button m_btn_cancel;
    private System.Windows.Forms.TableLayoutPanel m_tbl_arguments;
}