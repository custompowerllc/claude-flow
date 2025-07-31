using System;
using System.Windows.Forms;
using program_ns.processing;

namespace program_ns.gui;

internal sealed partial class
Config_Resolve : Form
{
    public static (Config_Data, Product)?
    resolve
    (string a_file_name)
    {
        string a_error;

        try
        {
            var a_config = new Config_Data(a_file_name);

            return (a_config, Product.make(a_config));
        }
        catch(Exception a_except)
        {
            a_error = a_except.Message;
        }

        var a_form = new Config_Resolve(a_error);

        Application.Run(a_form);

        return a_form.result;
    }

    private
    Config_Resolve
    (string a_initial_error)
    {
        m_initial_error = a_initial_error;

        result = null;

        InitializeComponent();
    }

    private readonly string m_initial_error;

    private (Config_Data, Product)? result { set; get; }

    private void
    Config_Resolve_Load
    (object? a_sender, EventArgs a_args) =>
        MessageBox.Show
        (
            this,
            $"Error loading configuration file:{Environment.NewLine}{m_initial_error}",
            "ERROR",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error
        );

    private void
    btn_browse_Click
    (object? a_sender, EventArgs a_args)
    {
        using var a_dialog = new OpenFileDialog() { Filter = "TOML Files (*.toml)|*.toml" };

        _ = a_dialog.ShowDialog(this);

        m_txt_path.Text = a_dialog.FileName;
    }

    private void
    txt_path_TextChanged
    (object? a_sender, EventArgs a_args) => m_btn_ok.Enabled = m_txt_path.Text.Trim().Length is not 0;

    private void
    btn_ok_Click
    (object? a_sender, EventArgs a_args)
    {
        var a_file_name = m_txt_path.Text.Trim();

        try
        {
            var a_config = new Config_Data(a_file_name);

            result = (a_config, Product.make(a_config));
        }
        catch(Exception a_except)
        {
            _ =
            MessageBox.Show
            (
                this,
                $"Error loading configuration file:{Environment.NewLine}{a_except.Message}",
                "ERROR",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );

            _ = m_txt_path.Focus();

            m_txt_path.SelectAll();

            return;
        }

        Close();
    }

    private void
    btn_exit_Click
    (object? a_sender, EventArgs a_args) => Close();
}
