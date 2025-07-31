using agents;
using utility.can;

namespace program_ns.processing;

internal sealed partial class
Send_Agent : Agent_Extern<Send_Agent.Intern>
{
    public abstract class
    Event_Adapter
    {
        public Event_Adapter() { }
        public abstract void send_stop_finished();
        public abstract void send_once_finished();
        public abstract void command_finished(Product.Command a_command);
        public abstract void command_failed(Product.Command a_command, string a_message);
        public abstract void new_send_count(uint a_count);
        public abstract void new_message_register_parsed(Product.Message_Register a_register, CAN_Message_Parsed a_message);
        public abstract void new_status_register_parsed(Product.Status_Register a_register, byte a_status);
        public abstract void new_can_message_sent(CAN_Message_Parsed a_message);
        public abstract void can_error(string a_message);
    }

    public const uint DEFAULT_SEND_INTERVAL = 1000;

    public
    Send_Agent
    (string a_name, CAN_Interface a_can_agent, Config_Data a_config, Product a_product) :
    base(() => new(a_name, a_can_agent, a_config, a_product), a_name, false)
    {

    }

    public void
    msg_set_event_adapter
    (Event_Adapter a_adapter) =>
        send_message(a_agent => a_agent.msg_set_event_adapter(a_adapter));

    public void
    msg_set_send_dest
    (Product.Destination a_dest) =>
        send_message(a_agent => a_agent.msg_set_send_dest(a_dest));

    public void
    msg_enter_bootloader() =>
        send_message(a_agent => a_agent.msg_enter_bootloader(this));

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
        send_message(a_agent => a_agent.msg_send_once(this, a_query));

    public void
    msg_command
    (Product.Command a_command, string[] a_args) =>
        send_message(a_agent => a_agent.msg_command(this, a_command, a_args));

    public void
    msg_can_message_received
    (CAN_ID a_id, byte[] a_data) =>
        send_message(a_agent => a_agent.msg_can_message_received(a_id, a_data));

    public void
    msg_can_error
    (string a_message) =>
        try_send_message(a_agent => a_agent.msg_can_error(a_message));

    public void
    msg_can_error_clear() =>
        send_message(static a_agent => a_agent.msg_can_error_clear());
}
