using System;
using agents;
using program_ns.processing.translators;
using utility.can;

namespace program_ns.processing;

internal abstract class
Translator
{
    public interface
    Protocol
    {
        void received_message(CAN_ID a_id, byte[] a_data);
        void received_error(string a_message);
        void send_data(byte[] a_data, Action<Message_Result<byte[]>> a_callback);
        void send_recv_data(byte[] a_data, Action<Message_Result<byte[]>> a_callback, int a_timeout);
    }

    public static Translator
    make
    (in Config_Data.Modbus_Table a_config) =>
        a_config.translator switch
        {
            nameof(GA_LiFePO4_Modbus) => new GA_LiFePO4_Modbus(),
            nameof(GA_LiFePO4_Next_Modbus) => new GA_LiFePO4_Next_Modbus(),
            nameof(Sikorsky_One_Modbus) => new Sikorsky_One_Modbus(),
            _ => throw new ArgumentException($"unrecognized translator \"{a_config.translator}\"", nameof(a_config))
        };

    protected
    Translator()
    {

    }

    public abstract void
    sent_message
    (CAN_ID a_id, byte[] a_data, Protocol a_receiver, Action<Message_Result<(CAN_ID, byte[])>> a_callback);
}
