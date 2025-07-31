using System;
using System.Collections.Immutable;
using System.Drawing;
using System.Windows.Forms;
using program_ns.processing;

namespace program_ns.gui;

internal sealed partial class
Command_Arguments : Form
{
    public
    Command_Arguments
    (Product.Command a_command)
    {
        var a_count = a_command.arguments.Length;

        m_command = a_command;
        m_arguments = new string[a_count];
        result = DialogResult.Cancel;

        InitializeComponent();

        var a_font = new Font("Courier New", 12.0f, FontStyle.Regular, GraphicsUnit.Point);
        var a_builder = ImmutableArray.CreateBuilder<TextBox>(a_count);

        for(var a_index = 0; a_index != a_count; ++a_index)
        {
            m_arguments[a_index] = string.Empty;

            var a_txt =
                new TextBox()
                {
                    AutoSize = true,
                    Font = a_font,
                    Name = $"txt_argument_{a_index:X4}",
                    ReadOnly = false,
                    Size = new(200, 0),
                    Anchor = AnchorStyles.None,
                    TabIndex = a_index,
                    TabStop = true
                };

            a_builder.Add(a_txt);
        }

        m_argument_controls = a_builder.ToImmutable();
    }

    private readonly Product.Command m_command;
    private readonly string[] m_arguments;
    private readonly ImmutableArray<TextBox> m_argument_controls;

    public string[] arguments => m_arguments.AsSpan().ToArray();
    public DialogResult result { private set; get; }

    private void
    btn_ok_Click
    (object? a_sender, EventArgs a_args)
    {
        var a_index = 0;

        foreach(var a_txt in m_argument_controls)
        {
            m_arguments[a_index++] = a_txt.Text.Trim();
        }

        result = DialogResult.OK;

        Close();
    }

    private void
    btn_cancel_Click
    (object? a_sender, EventArgs a_args) => Close();

    private void
    Command_Arguments_Load
    (object? a_sender, EventArgs a_args)
    {
        Text = m_command.display_text;

        var a_font = new Font("Courier New", 12.0f, FontStyle.Regular, GraphicsUnit.Point);
        var a_tbl = m_tbl_arguments;
        var a_row = 0;

        a_tbl.SuspendLayout();
        a_tbl.RowStyles.Clear();
        a_tbl.RowCount = m_command.arguments.Length;

        foreach(var (a_display_text, a_default_value) in m_command.arguments)
        {
            _ = a_tbl.RowStyles.Add(new(SizeType.AutoSize));

            var a_lbl =
                new Label()
                {
                    AutoSize = true,
                    Font = a_font,
                    Name = $"lbl_argument_{a_row:X4}",
                    Text = $"{a_display_text} ".PadRight(25, '.'),
                    Anchor = AnchorStyles.None,
                    TabIndex = 0
                };

            var a_txt = m_argument_controls[a_row];

            a_txt.Text = a_default_value;
            a_tbl.Controls.Add(a_lbl, 0, a_row);
            a_tbl.Controls.Add(a_txt, 1, a_row);

            ++a_row;
        }

        a_tbl.ResumeLayout();
    }
}
