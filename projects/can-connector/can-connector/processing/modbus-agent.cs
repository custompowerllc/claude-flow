using System;
using agents;
using serial;
using utility.can;

namespace program_ns.processing;

using Error_Listener = Action<string, uint>;
using Recv_Listener = Action<CAN_ID, byte[]>;

internal sealed partial class
Modbus_Agent : Agent_Extern<Modbus_Agent.Intern>, Translator.Protocol
{
    public
    Modbus_Agent
    (string a_name, bool a_is_background = false) :
    base(() => new(a_name), a_name, a_is_background)
    {

    }

    public void
    msg_open
    (Serial_Device.Config a_config, Translator a_translator, Action<Message_Result> a_callback) =>
        send_message(a_agent => a_agent.msg_open(this, a_config, a_translator, a_callback));

    public void
    msg_close() =>
        send_message(static a_agent => a_agent.msg_close());

    public void
    msg_recv_listener_add
    (string a_id, Recv_Listener a_listener) =>
        send_message(a_agent => a_agent.msg_recv_listener_add(a_id, a_listener));

    public void
    msg_recv_listener_remove
    (string a_id) =>
        send_message(a_agent => a_agent.msg_recv_listener_remove(a_id));

    public void
    msg_error_listener_add
    (string a_id, Error_Listener a_listener) =>
        send_message(a_agent => a_agent.msg_error_listener_add(a_id, a_listener));

    public void
    msg_error_listener_remove
    (string a_id) =>
        send_message(a_agent => a_agent.msg_error_listener_remove(a_id));

    public void
    msg_set_max_error_count
    (uint a_count) =>
        send_message(a_agent => a_agent.msg_set_max_error_count(a_count));

    public void
    msg_send
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        if(a_id.data_size != a_data.Length)
        {
            throw new ArgumentException("id-data length mismatch", nameof(a_data));
        }

        var a_copy = a_data.Length is 0 ? Array.Empty<byte>() : a_data.ToArray();

        send_message(a_agent => a_agent.msg_send(this, a_id, a_copy, a_callback));
    }

    public void
    msg_send
    (CAN_ID a_id, byte[] a_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        if(a_id.data_size != a_data.Length)
        {
            throw new ArgumentException("id-data length mismatch", nameof(a_data));
        }

        var a_copy = a_data.Length is 0 ? a_data : a_data.AsSpan().ToArray();

        send_message(a_agent => a_agent.msg_send(this, a_id, a_copy, a_callback));
    }

    public void
    msg_send_direct
    (CAN_ID a_id, byte[] a_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        if(a_id.data_size != a_data.Length)
        {
            throw new ArgumentException("id-data length mismatch", nameof(a_data));
        }

        send_message(a_agent => a_agent.msg_send(this, a_id, a_data, a_callback));
    }

    void
    Translator.Protocol.received_message
    (CAN_ID a_id, byte[] a_data) =>
        msg_received_message(a_id, a_data);

    void
    Translator.Protocol.received_error
    (string a_message) =>
        msg_received_error(a_message);

    void
    Translator.Protocol.send_data
    (byte[] a_data, Action<Message_Result<byte[]>> a_callback) =>
        msg_send_data(a_data, a_callback);

    void
    Translator.Protocol.send_recv_data
    (byte[] a_data, Action<Message_Result<byte[]>> a_callback, int a_timeout) =>
        msg_send_recv_data(a_data, a_callback, a_timeout);
}
