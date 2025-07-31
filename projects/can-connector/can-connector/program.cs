using System;
using program_ns.gui;
using program_ns.processing;

namespace program_ns;

internal static class
Program
{
    private const string DEFAULT_CONFIG = "config-default.toml";

    [STAThread]
    private static void
    Main
    (string[] a_args)
    {
        ApplicationConfiguration.Initialize();

        var a_result = Config_Resolve.resolve(a_args.Length is 0 ? DEFAULT_CONFIG : a_args[0]);

        if(a_result is null)
        {
            return;
        }

        var (a_config, a_product) = a_result.Value;

        using var a_can = CAN_Interface.make(a_config);

        using var a_gui = new GUI_Agent(nameof(GUI_Agent), a_can, a_config, a_product);

        a_gui.main_start(a_product);
    }
}
