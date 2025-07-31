using agents;
using utility.can;

namespace program_ns.processing;

internal sealed partial class
Upgrade_Agent : Agent_Extern<Upgrade_Agent.Intern>
{
    public abstract class
    Event_Adapter
    {
        public Event_Adapter() { }
        public abstract void bootloader_exited();
        public abstract void firmware_parse_success(CAN_Bootloader a_upgrader);
        public abstract void firmware_parse_fail(string a_message);
        public abstract void firmware_upgrade_success();
        public abstract void firmware_upgrade_fail(string a_message);
        public abstract void firmware_upgrade_progress(int a_bytes_transferred, string a_status);
        public abstract void new_message_register_parsed(CAN_Message_Parsed a_message);
        public abstract void new_can_message_sent(CAN_Message_Parsed a_message);
        public abstract void can_error(string a_message);
    }

    public
    Upgrade_Agent
    (string a_name, CAN_Interface a_can_agent, Config_Data a_config) :
    base(() => new(a_name, a_can_agent, a_config), a_name, false)
    {

    }

    public void
    msg_set_event_adapter
    (Event_Adapter a_adapter) =>
        send_message(a_agent => a_agent.msg_set_event_adapter(a_adapter));

    public void
    msg_parse_firmware
    (string a_file_name) =>
        send_message(a_agent => a_agent.msg_parse_firmware(a_file_name));

    public void
    msg_firmware_upgrade_initiate
    (CAN_Bootloader a_upgrader) =>
        send_message(a_agent => a_agent.msg_firmware_upgrade_initiate(this, a_upgrader));

    public void
    msg_exit_bootloader() =>
        send_message(a_agent => a_agent.msg_exit_bootloader(this));

    public void
    msg_can_message_received
    (CAN_ID a_id, byte[] a_data) =>
        try_send_message(a_agent => a_agent.msg_can_message_received(a_id, a_data));

    public void
    msg_can_error
    (string a_message) =>
        try_send_message(a_agent => a_agent.msg_can_error(a_message));

    public void
    msg_can_error_clear() =>
        try_send_message(static a_agent => a_agent.msg_can_error_clear());
}
