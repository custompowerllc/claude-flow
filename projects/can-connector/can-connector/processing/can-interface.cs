using System;
using agents;
using contracts;
using komodo_can;
using serial;
using utility.can;

namespace program_ns.processing;

internal abstract class 
CAN_Interface : IDisposable
{
    public const uint DEFAULT_POLL_INTERVAL = Komodo_CAN_Agent.DEFAULT_POLL_INTERVAL;

    public static CAN_Interface
    make
    (Config_Data a_config, uint a_poll_interval = DEFAULT_POLL_INTERVAL, bool a_is_background = false)
    {
        if(a_config.komodo is not null)
        {
            return new Komodo_CAN_Interface(nameof(Komodo_CAN_Agent), a_poll_interval, a_is_background);
        }

        if(a_config.serial is not null)
        {
            return new Serial_CAN_Interface(nameof(Serial_Agent), a_config.serial.Value.channel, a_is_background);
        }

        if(a_config.modbus is not null)
        {
            return new Modbus_CAN_Interface(nameof(Modbus_Agent), a_is_background);
        }

        throw new InvalidOperationException(nameof(a_config));
    }

    protected
    CAN_Interface(): 
    base()
    {

    }

    public void
    msg_open
    (Config_Data a_config, Action<Message_Result> a_callback) => 
        msg_open(a_config, string.Empty, 0, a_callback);

    public abstract void msg_open(Config_Data a_config, string a_port, int a_baud, Action<Message_Result> a_callback);
    public abstract void msg_close();
    public abstract void msg_set_max_error_count(uint a_count);
    public abstract void msg_error_listener_add(string a_id, Action<string, uint> a_listener);
    public abstract void msg_recv_listener_add(string a_id, Action<CAN_ID, byte[]> a_listener);
    public abstract void msg_set_poll_interval(uint a_ms);
    public abstract void msg_send_direct(CAN_ID a_id, byte[] a_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback);
    public abstract void Dispose();
}

internal sealed class
Komodo_CAN_Interface : CAN_Interface
{
    public
    Komodo_CAN_Interface
    (string a_name, uint a_poll_interval = DEFAULT_POLL_INTERVAL, bool a_is_background = false) :
    base() => 
        m_agent = new(a_name, a_poll_interval, a_is_background);

    public override void
    msg_open
    (Config_Data a_config, string a_port, int a_baud, Action<Message_Result> a_callback)
    {
        Contracts.assert(a_config.komodo is not null);

        var a_komodo = a_config.komodo.Value;

        var a_komodo_config =
            new Komodo_CAN_Device.Config()
            {
                port = a_komodo.port,
                bitrate = a_komodo.bitrate,
                timeout = a_komodo.timeout,
                latency = a_komodo.latency,
                physical_loopback = a_komodo.physical_loopback,
                info_log = null,
                ext_id_filter = a_komodo.ext_id_filter,
                std_id_filter = a_komodo.std_id_filter
            };

        m_agent.msg_open(a_komodo_config, a_callback);
    }

    public override void
    msg_close() => m_agent.msg_close();

    public override void
    msg_set_max_error_count
    (uint a_count) => m_agent.msg_set_max_error_count(a_count);

    public override void 
    msg_error_listener_add
    (string a_id, Action<string, uint> a_listener) => m_agent.msg_error_listener_add(a_id, a_listener);

    public override void
    msg_recv_listener_add
    (string a_id, Action<CAN_ID, byte[]> a_listener) => m_agent.msg_recv_listener_add(a_id, a_listener);

    public override void
    msg_set_poll_interval
    (uint a_ms) => m_agent.msg_set_poll_interval(a_ms);

    public override void
    msg_send_direct
    (CAN_ID a_id, byte[] a_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback) => m_agent.msg_send_direct(a_id, a_data, a_callback);

    public override void
    Dispose() => m_agent.Dispose();

    private readonly Komodo_CAN_Agent m_agent;
}

internal sealed class
Serial_CAN_Interface : CAN_Interface
{
    public
    Serial_CAN_Interface
    (string a_name, uint a_channel, bool a_is_background = false) :
    base()
    {
        m_channel = a_channel;
        m_agent = new(a_name, a_is_background);
    }

    public override void
    msg_open
    (Config_Data a_config, string a_port, int a_baud, Action<Message_Result> a_callback)
    {
        Contracts.assert(a_config.serial is not null);

        var a_serial = a_config.serial.Value;

        static Serial_Device.Match_Result
        serial_match_func
        (ReadOnlyMemory<byte> a_memory)
        {
            if(CAN_Over_UART.parse(a_memory.Span, out var _, out var _, out var _) is int a_size)
            {
                return new() { is_match = true, consumed = a_size };
            }

            return new() { is_match = false, consumed = 1 };
        }

        m_agent.msg_open
        (
            new()
            {
                port = a_port,
                send_timeout = 500,
                baud_bate = a_baud,
                data_bits = a_serial.data_bits,
                parity_type = a_serial.parity_type,
                stop_bits = a_serial.stop_bits,
                hand_shake = a_serial.hand_shake
            },
            CAN_Over_UART.MIN_TOTAL_SIZE,
            CAN_Over_UART.MAX_TOTAL_SIZE_FD,
            serial_match_func,
            a_callback
        );
    }

    public override void
    msg_close() => m_agent.msg_close();

    public override void
    msg_set_max_error_count
    (uint a_count)
    {
        
    }

    public override void
    msg_error_listener_add
    (string a_id, Action<string, uint> a_listener)
    {

    }

    public override void
    msg_recv_listener_add
    (string a_id, Action<CAN_ID, byte[]> a_listener)
    {
        var a_target_chan = m_channel;

        m_agent.msg_recv_listener_add
        (
            a_id,
            (byte[] a_serial) =>
            {
                if(CAN_Over_UART.parse(new ReadOnlySpan<byte>(a_serial), out var a_id, out var a_channel, out var a_recv_data) is null)
                {
                    return;
                }

                if(a_channel != a_target_chan)
                {
                    return;
                }

                a_listener(a_id, a_recv_data.ToArray());
            }
        );
    }

    public override void
    msg_set_poll_interval
    (uint a_ms)
    {

    }

    public override void
    msg_send_direct
    (CAN_ID a_id, byte[] a_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        var a_send_data = CAN_Over_UART.generate(a_id, m_channel, a_data);

        m_agent.msg_send_direct
        (
            a_send_data,
            a_sent =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                if(a_sent.error is Exception a_error)
                {
                    Message_Result.make_error(out a_result, a_error);
                }
                else
                {
                    Message_Result.make_value(out a_result, (a_id, a_data));
                }

                a_callback(a_result);
            }
        );
    }

    public override void
    Dispose() => m_agent.Dispose();

    private readonly uint m_channel;
    private readonly Serial_Agent m_agent;
}

internal sealed class
Modbus_CAN_Interface : CAN_Interface
{
    public
    Modbus_CAN_Interface
    (string a_name, bool a_is_background = false) :
    base() =>
        m_agent = new(a_name, a_is_background);

    public override void
    msg_open
    (Config_Data a_config, string a_port, int a_baud, Action<Message_Result> a_callback)
    {
        Contracts.assert(a_config.modbus is not null);

        var a_modbus = a_config.modbus.Value;

        Translator a_translator;

        try
        {
            a_translator = Translator.make(a_modbus);
        }
        catch(Exception a_except)
        {
            Message_Result.make_error(out var a_result, a_except);

            a_callback(a_result);

            return;
        }

        m_agent.msg_open
        (
            new()
            {
                port = a_port,
                send_timeout = 500,
                baud_bate = a_baud,
                data_bits = a_modbus.data_bits,
                parity_type = a_modbus.parity_type,
                stop_bits = a_modbus.stop_bits,
                hand_shake = a_modbus.hand_shake
            },
            a_translator, 
            a_callback
        );
    }

    public override void
    msg_close() => m_agent.msg_close();

    public override void
    msg_set_max_error_count
    (uint a_count) => m_agent.msg_set_max_error_count(a_count);

    public override void
    msg_error_listener_add
    (string a_id, Action<string, uint> a_listener) => m_agent.msg_error_listener_add(a_id, a_listener);

    public override void
    msg_recv_listener_add
    (string a_id, Action<CAN_ID, byte[]> a_listener) => m_agent.msg_recv_listener_add(a_id, a_listener);

    public override void
    msg_set_poll_interval
    (uint a_ms)
    {

    }

    public override void
    msg_send_direct
    (CAN_ID a_id, byte[] a_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback) => m_agent.msg_send_direct(a_id, a_data, a_callback);

    public override void
    Dispose() => m_agent.Dispose();

    private readonly Modbus_Agent m_agent;
}
