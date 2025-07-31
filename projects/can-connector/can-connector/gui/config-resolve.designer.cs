namespace program_ns.gui;

sealed partial class
Config_Resolve
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
        System.Windows.Forms.GroupBox a_grp_selected;
        var resources = new System.ComponentModel.ComponentResourceManager(typeof(Config_Resolve));
        m_txt_path = new System.Windows.Forms.TextBox();
        m_btn_browse = new System.Windows.Forms.Button();
        m_btn_ok = new System.Windows.Forms.Button();
        m_btn_exit = new System.Windows.Forms.Button();
        a_grp_selected = new System.Windows.Forms.GroupBox();
        a_grp_selected.SuspendLayout();
        SuspendLayout();
        // 
        // a_grp_selected
        // 
        a_grp_selected.Controls.Add(m_txt_path);
        a_grp_selected.Controls.Add(m_btn_browse);
        a_grp_selected.Font = new System.Drawing.Font("Courier New", 9.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point);
        a_grp_selected.Location = new System.Drawing.Point(12, 12);
        a_grp_selected.Name = "a_grp_selected";
        a_grp_selected.Size = new System.Drawing.Size(506, 84);
        a_grp_selected.TabIndex = 0;
        a_grp_selected.TabStop = false;
        a_grp_selected.Text = "Selected:";
        // 
        // m_txt_path
        // 
        m_txt_path.Font = new System.Drawing.Font("Courier New", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
        m_txt_path.Location = new System.Drawing.Point(6, 21);
        m_txt_path.Name = "m_txt_path";
        m_txt_path.Size = new System.Drawing.Size(494, 26);
        m_txt_path.TabIndex = 1;
        m_txt_path.TextChanged += txt_path_TextChanged;
        // 
        // m_btn_browse
        // 
        m_btn_browse.Font = new System.Drawing.Font("Courier New", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
        m_btn_browse.Location = new System.Drawing.Point(425, 53);
        m_btn_browse.Name = "m_btn_browse";
        m_btn_browse.Size = new System.Drawing.Size(75, 23);
        m_btn_browse.TabIndex = 0;
        m_btn_browse.TabStop = false;
        m_btn_browse.Text = "Browse";
        m_btn_browse.UseVisualStyleBackColor = true;
        m_btn_browse.Click += btn_browse_Click;
        // 
        // m_btn_ok
        // 
        m_btn_ok.Enabled = false;
        m_btn_ok.Font = new System.Drawing.Font("Courier New", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point);
        m_btn_ok.Location = new System.Drawing.Point(12, 102);
        m_btn_ok.Name = "m_btn_ok";
        m_btn_ok.Size = new System.Drawing.Size(250, 40);
        m_btn_ok.TabIndex = 0;
        m_btn_ok.TabStop = false;
        m_btn_ok.Text = "OK";
        m_btn_ok.UseVisualStyleBackColor = true;
        m_btn_ok.Click += btn_ok_Click;
        // 
        // m_btn_exit
        // 
        m_btn_exit.Font = new System.Drawing.Font("Courier New", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point);
        m_btn_exit.Location = new System.Drawing.Point(268, 102);
        m_btn_exit.Name = "m_btn_exit";
        m_btn_exit.Size = new System.Drawing.Size(250, 40);
        m_btn_exit.TabIndex = 0;
        m_btn_exit.TabStop = false;
        m_btn_exit.Text = "Exit";
        m_btn_exit.UseVisualStyleBackColor = true;
        m_btn_exit.Click += btn_exit_Click;
        // 
        // config_resolve
        // 
        AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
        AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
        BackColor = System.Drawing.Color.LightSteelBlue;
        ClientSize = new System.Drawing.Size(530, 151);
        Controls.Add(a_grp_selected);
        Controls.Add(m_btn_exit);
        Controls.Add(m_btn_ok);
        Font = new System.Drawing.Font("Courier New", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
        Icon = (System.Drawing.Icon)resources.GetObject("$this.Icon");
        MaximizeBox = false;
        MaximumSize = new System.Drawing.Size(546, 190);
        MinimizeBox = false;
        MinimumSize = new System.Drawing.Size(546, 190);
        Name = "config_resolve";
        ShowIcon = false;
        ShowInTaskbar = false;
        StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
        Text = "Select Configuration File";
        TopMost = true;
        Load += Config_Resolve_Load;
        a_grp_selected.ResumeLayout(false);
        a_grp_selected.PerformLayout();
        ResumeLayout(false);
    }

    #endregion

    private System.Windows.Forms.Button m_btn_ok;
    private System.Windows.Forms.Button m_btn_exit;
    private System.Windows.Forms.TextBox m_txt_path;
    private System.Windows.Forms.Button m_btn_browse;
}