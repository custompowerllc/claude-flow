using System;
using System.Collections.Generic;
using agents;
using serial;
using utility.can;
using utility.modbus;

namespace program_ns.processing;

using error_listener = Action<string, uint>;
using recv_listener = Action<CAN_ID, byte[]>;

internal sealed partial class
Modbus_Agent
{
    private void
    msg_port_opened
    (Message_Result a_opened, Action<Message_Result> a_callback) =>
        try_send_message(a_agent => a_agent.msg_port_opened(a_opened, a_callback));

    private void
    msg_received_message
    (CAN_ID a_id, byte[] a_data)
    {
        if(a_id.data_size != a_data.Length)
        {
            throw new ArgumentException("id-data length mismatch", nameof(a_data));
        }

        _ = try_send_message(a_agent => a_agent.msg_received_message(a_id, a_data));
    }

    private void
    msg_received_error
    (string a_message) =>
        try_send_message(a_agent => a_agent.msg_received_error(a_message));

    private void
    msg_send_data
    (byte[] a_data, Action<Message_Result<byte[]>> a_callback) =>
        try_send_message(a_agent => a_agent.msg_send_data(a_data, a_callback));

    private void
    msg_send_recv_data
    (byte[] a_data, Action<Message_Result<byte[]>> a_callback, int a_timeout) =>
        try_send_message(a_agent => a_agent.msg_send_recv_data(a_data, a_callback, a_timeout));
}

internal sealed partial class
Modbus_Agent
{
    public sealed class
    Intern : Agent_Intern<Intern>
    {
        public
        Intern
        (string a_name) :
        base(a_name)
        {
            m_serial = new($"{a_name}::{nameof(Serial_Agent)}");
            m_translator = null;
            m_error_count = 0;
            m_max_error_count = uint.MaxValue;
            m_recv_listeners = new();
            m_error_listeners = new();
        }

        private readonly Serial_Agent m_serial;
        private Translator? m_translator;
        private uint m_error_count;
        private uint m_max_error_count;
        private readonly Dictionary<string, recv_listener> m_recv_listeners;
        private readonly Dictionary<string, error_listener> m_error_listeners;

        public void
        msg_open
        (Modbus_Agent a_extern, Serial_Device.Config a_config, Translator a_translator, Action<Message_Result> a_callback)
        {
            if(m_translator is not null)
            {
                Message_Result.make_error(out var a_result, new Exception("already opened"));

                a_callback(a_result);

                return;
            }

            m_serial.msg_open
            (
                a_config,
                Modbus_Master.MIN_MATCH_SIZE,
                Modbus_Master.MAX_MATCH_SIZE,
                static (ReadOnlyMemory<byte> a_serial) =>
                {
                    if(Modbus_Master.parse(a_serial.Span, out var _, out var a_data) is int a_size)
                    {
                        return new() { is_match = true, consumed = a_size };
                    }

                    if(Modbus_Master.parse_error(a_serial.Span, out var _) is int a_error_size)
                    {
                        return new() { is_match = true, consumed = a_error_size };
                    }

                    return new() { is_match = false, consumed = 1 };
                },
                a_opened => a_extern.msg_port_opened(a_opened, a_callback)
            );

            m_translator = a_translator;
        }

        public void
        msg_port_opened
        (Message_Result a_opened, Action<Message_Result> a_callback)
        {
            if(a_opened.is_error)
            {
                m_translator = null;
            }

            a_callback(a_opened);
        }

        public void
        msg_close()
        {
            if(m_translator is null)
            {
                log_info_line("already closed");

                return;
            }

            m_translator = null;

            m_error_count = 0;

            m_serial.msg_close();
        }

        public void
        msg_recv_listener_add
        (string a_id, recv_listener a_listener) => m_recv_listeners[a_id] = a_listener;

        public void
        msg_recv_listener_remove
        (string a_id)
        {
            if(!m_recv_listeners.Remove(a_id))
            {
                log_info_line($"Failed to remove recv listener \"{a_id}\" (does not exist)");
            }
        }

        public void
        msg_error_listener_add
        (string a_id, error_listener a_listener) => m_error_listeners[a_id] = a_listener;

        public void
        msg_error_listener_remove
        (string a_id)
        {
            if(!m_error_listeners.Remove(a_id))
            {
                log_info_line($"Failed to remove error listener \"{a_id}\" (does not exist)");
            }
        }

        public void
        msg_set_max_error_count
        (uint a_count) => m_max_error_count = a_count;

        public void
        msg_send
        (
            Translator.Protocol a_extern,
            CAN_ID a_id,
            byte[] a_data,
            Action<Message_Result<(CAN_ID, byte[])>> a_callback
        )
        {
            if(m_translator is null)
            {
                Message_Result.make_error(out Message_Result<(CAN_ID, byte[])> a_result, new Exception("failed to send message (no port open)"));

                a_callback(a_result);

                return;
            }

            m_translator.sent_message(a_id, a_data, a_extern, a_callback);
        }

        public void
        msg_received_message
        (CAN_ID a_id, byte[] a_data)
        {
            foreach(var a_callback  in m_recv_listeners.Values)
            {
                a_callback(a_id, a_data.AsSpan().ToArray());
            }
        }

        public void
        msg_received_error
        (string a_message)
        {
            _ = unchecked(++m_error_count);

            foreach(var a_callback in m_error_listeners.Values)
            {
                a_callback(a_message, m_error_count);
            }

            if(m_error_count > m_max_error_count)
            {
                msg_close();
            }
        }

        public void
        msg_send_data
        (byte[] a_data, Action<Message_Result<byte[]>> a_callback) =>
            m_serial.msg_send_direct(a_data, a_callback);

        public void
        msg_send_recv_data
        (byte[] a_data, Action<Message_Result<byte[]>> a_callback, int a_timeout) =>
            m_serial.msg_send_recv_direct(a_data, a_callback, a_timeout);

        public override void
        Dispose() => m_serial.Dispose();
    }
}

