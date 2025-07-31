using System.Windows.Forms;
using agents;
using program_ns.processing;
using utility.can;

namespace program_ns.gui;

internal sealed partial class
GUI_Agent : Agent_Extern<GUI_Agent.Intern>
{
    public const uint DEFAULT_RECV_INTERVAL = CAN_Interface.DEFAULT_POLL_INTERVAL;
    public const uint DEFAULT_SEND_INTERVAL = Send_Agent.DEFAULT_SEND_INTERVAL;
    public const uint MAX_CAN_ERRORS = 15;
    public const uint MAX_MODBUS_ERRORS = 0;

    public
    GUI_Agent
    (string a_name, CAN_Interface a_can_agent, Config_Data a_config, Product a_product) :
    base(() => new(a_name, a_can_agent, a_config, a_product), a_name, false)
    {

    }

    public void
    main_start
    (Product a_product)
    {
        var a_form = new Main_Form(this, a_product);

        msg_init(a_form);

        Application.Run(a_form);
    }

    public void
    msg_open_can
    (bool a_is_reopen) =>
        send_message(a_agent => a_agent.msg_open_can(this, a_is_reopen));

    public void
    msg_open_serial
    (bool a_is_reopen, string a_port, int a_baud) =>
        send_message(a_agent => a_agent.msg_open_serial(this, a_is_reopen, a_port, a_baud));

    public void
    msg_set_send_dest
    (Product.Destination a_dest) =>
        send_message(a_agent => a_agent.msg_set_send_dest(a_dest));

    public void
    msg_parse_firmware
    (string a_file_name) =>
        send_message(a_agent => a_agent.msg_parse_firmware(a_file_name));

    public void
    msg_upgrade_firmware
    (CAN_Bootloader a_firmware_upgrader) =>
        send_message(a_agent => a_agent.msg_upgrade_firmware(a_firmware_upgrader));

    public void
    msg_enter_bootloader() =>
        send_message(a_agent => a_agent.msg_enter_bootloader());

    public void
    msg_exit_bootloader() =>
        send_message(a_agent => a_agent.msg_exit_bootloader());

    public void
    msg_set_recv_interval
    (uint a_ms) =>
        send_message(a_agent => a_agent.msg_set_recv_interval(a_ms));

    public void
    msg_ignore_recv
    (bool a_ignore) =>
        send_message(a_agent => a_agent.msg_ignore_recv(a_ignore));

    public void
    msg_start_sending
    (uint a_ms, uint? a_count, Product.Query a_query) =>
        send_message(a_agent => a_agent.msg_start_sending(a_ms, a_count, a_query));

    public void
    msg_stop_sending() =>
        send_message(static a_agent => a_agent.msg_stop_sending());

    public void
    msg_send_once
    (Product.Query a_query) =>
        send_message(a_agent => a_agent.msg_send_once(a_query));

    public void
    msg_command
    (Product.Command a_command, string[] a_args) =>
        send_message(a_agent => a_agent.msg_command(a_command, a_args));
}
