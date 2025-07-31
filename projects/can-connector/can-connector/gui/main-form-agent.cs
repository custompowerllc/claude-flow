using program_ns.processing;
using utility.can;

namespace program_ns.gui;

internal interface
Main_Form_Agent
{
    void
    msg_enable_features
    (Config_Data a_config);

    void
    msg_available_ports
    (string[] a_ports);

    void
    msg_enter_ready_state();

    void
    msg_can_error
    (string a_message);

    void
    msg_can_open_failed
    (string a_message);

    void
    msg_can_reopened();

    void
    msg_bus_activity();

    void
    msg_firmware_parse_fail
    (string a_message);

    void
    msg_firmware_upgrade_confirm
    (CAN_Bootloader a_firmware_upgrader);

    void 
    msg_firmware_upgrade_initiated
    (bool a_success);

    void
    msg_firmware_upgrade_progress
    (int a_bytes_sent, string a_status);

    void
    msg_firmware_upgrade_fail
    (string a_message);

    void
    msg_firmware_upgrade_success();

    void
    msg_bootloader_exited();

    void
    msg_update_send_count
    (uint a_count);

    void
    msg_send_stop_finished();

    void
    msg_send_once_finished();

    void
    msg_command_invalid
    (string a_message);

    void
    msg_command_finished
    (Product.Command a_command);

    void
    msg_new_can_message_received
    (Product.Message_Register a_register, CAN_Message_Parsed a_message);

    void
    msg_new_status_register_received
    (Product.Status_Register a_register, byte a_status);

    void
    msg_new_can_message_sent
    (CAN_Message_Parsed a_message);

    void
    msg_new_can_message_received_bootloader
    (CAN_Message_Parsed a_message);

    void
    msg_new_can_message_sent_bootloader
    (CAN_Message_Parsed a_message);
}
