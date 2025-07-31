using System;
using System.Diagnostics;
using agents;
using contracts;
using utility.can;
using utility.misc;
using utility.modbus;

namespace program_ns.processing.translators;

internal sealed class
GA_LiFePO4_Next_Modbus : Translator
{
    public enum
    Command_Number : ushort
    {
        CMD_ENTER_BOOT,
        CMD_CHARGE_FET,
        CMD_DISCHARGE_FET,
        CMD_RESET_MICRO,
        CMD_FG_RESET,
        CMD_FG_LT_EN,
        CMD_FG_SEAL,
        CMD_FG_UNSEAL_KEY,
        CMD_FG_UNSEAL,
        CMD_FG_FULL_UNSEAL_KEY,
        CMD_FG_FULL_UNSEAL,
        CMD_PROG_FG,
        CMD_CAL_CC,
        CMD_CAL_BOARD,
        CMD_CAL_APPLIED_VOLT,
        CMD_CAL_VOLT,
        CMD_CAL_APPLIED_CURR,
        CMD_CAL_CURR,
        CMD_SERIAL_NUMBER,
        CMD_SERIAL_NUMBER_STORE,
        CMD_REBALANCE_MODE,
        CMD_QUERY_COIL,
        CMD_QUERY_DISCRETE,
        CMD_QUERY_HOLDING,
        CMD_QUERY_INPUT,
        CMD_RESPONSE = 0x8000
    }

    private const uint SLAVE_ADDR = 1;

    public
    GA_LiFePO4_Next_Modbus() :
    base()
    {

    }

    public override void
    sent_message
    (CAN_ID a_can_id, byte[] a_can_data, Protocol a_protocol, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        try
        {
            if(a_can_id.id is not 0xFF)
            {
                throw new UnreachableException();
            }

            var a_data = new ReadOnlySpan<byte>(a_can_data);

            var a_index = 0;

            Misc.decode_le(out ushort a_cmd, a_data, ref a_index);

            _ =
            (Command_Number)a_cmd switch
            {
                Command_Number.CMD_ENTER_BOOT => process_enter_boot(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_CHARGE_FET => process_charge_fet(a_data, ref a_index, a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_DISCHARGE_FET => process_discharge_fet(a_data, ref a_index, a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_RESET_MICRO => process_reset_micro(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_FG_RESET => process_fg_reset(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_FG_LT_EN => process_fg_lt_en(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_FG_SEAL => process_fg_seal_unseal(a_protocol, a_can_id, a_can_data, a_callback, true),
                Command_Number.CMD_FG_UNSEAL_KEY => process_fg_unseal_key(a_data, ref a_index, a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_FG_UNSEAL => process_fg_seal_unseal(a_protocol, a_can_id, a_can_data, a_callback, false),
                Command_Number.CMD_FG_FULL_UNSEAL_KEY => process_fg_full_unseal_key(a_data, ref a_index, a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_FG_FULL_UNSEAL => process_fg_full_unseal(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_PROG_FG => process_prog_fg(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_CAL_CC => process_cal_cc(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_CAL_BOARD => process_cal_board(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_CAL_APPLIED_VOLT => process_cal_applied_volt(a_data, ref a_index, a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_CAL_VOLT => process_cal_volt(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_CAL_APPLIED_CURR => process_cal_applied_curr(a_data, ref a_index, a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_CAL_CURR => process_cal_curr(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_SERIAL_NUMBER => process_serial_number(a_data, ref a_index, a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_SERIAL_NUMBER_STORE => process_serial_number_store(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_REBALANCE_MODE => process_rebalance_mode(a_data, ref a_index, a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_QUERY_COIL => process_query_coil(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_QUERY_DISCRETE => process_query_discrete(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_QUERY_HOLDING => process_query_holding(a_protocol, a_can_id, a_can_data, a_callback),
                Command_Number.CMD_QUERY_INPUT => process_query_input(a_protocol, a_can_id, a_can_data, a_callback),
                _ => false
            };
        }
        catch(Exception a_except)
        {
            Message_Result.make_error(out Message_Result<(CAN_ID, byte[])> a_result, a_except);

            a_callback(a_result);
        }
    }

    private static bool
    process_enter_boot
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 24u, true);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_ENTER_BOOT);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return false;
    }

    private static bool
    process_charge_fet
    (in ReadOnlySpan<byte> a_data, ref int a_index, Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        Misc.decode_le(out byte a_state, a_data, ref a_index);

        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 10u, a_state is not 0);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_CHARGE_FET);

                    var a_send_data = new byte[3];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);
                    Misc.encode_le((byte)(a_data_slice[0] & 0x01), a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_discharge_fet
    (in ReadOnlySpan<byte> a_data, ref int a_index, Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        Misc.decode_le(out byte a_state, a_data, ref a_index);

        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 11u, a_state is not 0);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_DISCHARGE_FET);

                    var a_send_data = new byte[3];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);
                    Misc.encode_le((byte)(a_data_slice[0] & 0x01), a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_reset_micro
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 12u, true);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_RESET_MICRO);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_fg_reset
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 13u, true);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_FG_RESET);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_fg_lt_en
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 17u, true);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_FG_LT_EN);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_fg_unseal_key
    (in ReadOnlySpan<byte> a_data, ref int a_index, Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        Misc.decode_le(out uint a_key, a_data, ref a_index);

        var a_key_hi = unchecked((ushort)(a_key >> 16));
        var a_key_lo = unchecked((ushort)(a_key >> 0));

        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_HOLDNGS, 1002u, stackalloc ushort[] { a_key_hi, a_key_lo });

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_HOLDNGS,
                        0,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_FG_UNSEAL_KEY);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_fg_seal_unseal
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback, bool a_seal)
    {
        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 14u, a_seal);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    var a_cmd = (ushort)Command_Number.CMD_RESPONSE;

                    a_cmd |= (ushort)(a_seal ? Command_Number.CMD_FG_SEAL : Command_Number.CMD_FG_UNSEAL);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(a_cmd, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_fg_full_unseal_key
    (in ReadOnlySpan<byte> a_data, ref int a_index, Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        Misc.decode_le(out uint a_key, a_data, ref a_index);

        var a_key_hi = unchecked((ushort)(a_key >> 16));
        var a_key_lo = unchecked((ushort)(a_key >> 0));

        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_HOLDNGS, 1004u, stackalloc ushort[] { a_key_hi, a_key_lo });

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_HOLDNGS,
                        0,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_FG_FULL_UNSEAL_KEY);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_fg_full_unseal
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 15u, false);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_FG_FULL_UNSEAL);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_prog_fg
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 18u, true);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_PROG_FG);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_cal_cc
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 19u, true);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_CAL_CC);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_cal_board
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 20u, true);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_CAL_BOARD);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_cal_applied_volt
    (in ReadOnlySpan<byte> a_data, ref int a_index, Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        Misc.decode_le(out ushort a_applied_volt, a_data, ref a_index);

        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_HOLDING, 1006u, a_applied_volt);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_HOLDING,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_CAL_APPLIED_VOLT);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_cal_volt
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 21u, true);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_CAL_VOLT);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_cal_applied_curr
    (in ReadOnlySpan<byte> a_data, ref int a_index, Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        Misc.decode_le(out ushort a_applied_curr, a_data, ref a_index);

        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_HOLDING, 1007u, a_applied_curr);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_HOLDING,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_CAL_APPLIED_CURR);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_cal_curr
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 22u, true);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_CAL_CURR);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_serial_number
    (in ReadOnlySpan<byte> a_data, ref int a_index, Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        Misc.decode_le(out uint a_sn, a_data, ref a_index);

        var a_sn_hi = unchecked((ushort)(a_sn >> 16));
        var a_sn_lo = unchecked((ushort)(a_sn >> 0));

        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_HOLDNGS, 1000u, stackalloc ushort[] { a_sn_hi, a_sn_lo });

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_HOLDNGS,
                        0,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_SERIAL_NUMBER);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_serial_number_store
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 23u, true);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_SERIAL_NUMBER_STORE);

                    var a_send_data = new byte[2];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_rebalance_mode
    (in ReadOnlySpan<byte> a_data, ref int a_index, Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        Misc.decode_le(out byte a_state, a_data, ref a_index);

        var a_send_data = Modbus_Master.generate_write(SLAVE_ADDR, Modbus_Master.Func_Code.WRITE_SINGLE_COIL, 16u, a_state is not 0);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.WRITE_SINGLE_COIL,
                        2,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    const ushort CMD = (ushort)(Command_Number.CMD_RESPONSE | Command_Number.CMD_REBALANCE_MODE);

                    var a_send_data = new byte[3];

                    var a_index = 0;

                    Misc.encode_le(CMD, a_send_data, ref a_index);
                    Misc.encode_le((byte)(a_data_slice[0] & 0x01), a_send_data, ref a_index);

                    received_command_response(a_protocol, a_send_data);

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_query_coil
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        const int BYTES = 2;

        var a_send_data = Modbus_Master.generate_read(SLAVE_ADDR, Modbus_Master.Func_Code.READ_COILS, 10u, 16);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.READ_COILS,
                        BYTES,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    var a_packet_data = new Coil_Data();

                    {
                        var a_index = 0;

                        Misc.decode_be(out a_packet_data.coils_lo, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.coils_hi, a_data_slice, ref a_index);

                        Contracts.assert(a_index is BYTES);
                    }

                    Span<byte> a_send_data = stackalloc byte[8];

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.coils_hi, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.coils_lo, a_send_data, ref a_index);

                        received_message(a_protocol, 0x10u, a_send_data[..a_index].ToArray());
                    }

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_query_discrete
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        const int BYTES = 24;

        var a_send_data = Modbus_Master.generate_read(SLAVE_ADDR, Modbus_Master.Func_Code.READ_DISCRETES, 8u, 8 * BYTES);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.READ_DISCRETES,
                        BYTES,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    var a_packet_data = new Discrete_Data();

                    {
                        var a_index = 0;

                        Misc.decode_be(out a_packet_data.afe_sys_stat, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_cellbal1, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_cellbal2, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_cellbal3, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_sys_ctrl1, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_sys_ctrl2, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_protect1, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_protect2, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_protect3, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_ov_trip, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_uv_trip, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_cc_cfg, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_control_status, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_battery_status, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_operation_status, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_gauging_status, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_manufacturing_status, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.uc_rev, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_rev, a_data_slice, ref a_index);

                        Contracts.assert(a_index is BYTES);
                    }

                    var a_send_data = new byte[8].AsSpan();

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.afe_sys_stat, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_cellbal1, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_cellbal2, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_cellbal3, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_sys_ctrl1, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_sys_ctrl2, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_ov_trip, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_uv_trip, a_send_data, ref a_index);

                        received_message(a_protocol, 0x09u, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.afe_protect1, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_protect2, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_protect3, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_cc_cfg, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.uc_rev, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_rev, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_control_status, a_send_data, ref a_index);

                        received_message(a_protocol, 0x0Au, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.fg_battery_status, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_operation_status, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_gauging_status, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_manufacturing_status, a_send_data, ref a_index);

                        received_message(a_protocol, 0x0Bu, a_send_data[..a_index].ToArray());
                    }

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return true;
    }

    private static bool
    process_query_holding
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        const int BYTES = 8 * 2;

        var a_send_data = Modbus_Master.generate_read(SLAVE_ADDR, Modbus_Master.Func_Code.READ_HOLDINGS, 1000u, BYTES / 2);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.READ_HOLDINGS,
                        BYTES,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    var a_packet_data = new Holding_Data();

                    {
                        var a_index = 0;

                        Misc.decode_be(out a_packet_data.serial_number, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_unseal_key, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_full_unseal_key, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_applied_voltage, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_applied_current, a_data_slice, ref a_index);

                        Contracts.assert(a_index is BYTES);
                    }

                    Span<byte> a_send_data = stackalloc byte[8];

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.serial_number, a_send_data, ref a_index);

                        received_message(a_protocol, 0x11u, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.fg_unseal_key, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_full_unseal_key, a_send_data, ref a_index);

                        received_message(a_protocol, 0x12u, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.fg_applied_voltage, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_applied_current, a_send_data, ref a_index);

                        received_message(a_protocol, 0x13u, a_send_data[..a_index].ToArray());
                    }

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return false;
    }

    private static bool
    process_query_input
    (Protocol a_protocol, CAN_ID a_can_id, byte[] a_can_data, Action<Message_Result<(CAN_ID, byte[])>> a_callback)
    {
        const int BYTES = 45 * 2;

        var a_send_data = Modbus_Master.generate_read(SLAVE_ADDR, Modbus_Master.Func_Code.READ_INPUTS, 10u, BYTES / 2);

        a_protocol.send_recv_data
        (
            a_send_data,
            a_recv_data =>
            {
                Message_Result<(CAN_ID, byte[])> a_result;

                try
                {
                    response_verify
                    (
                        a_recv_data,
                        SLAVE_ADDR,
                        Modbus_Master.Func_Code.READ_INPUTS,
                        BYTES,
                        out var a_parse_result,
                        out var a_data_slice
                    );

                    var a_packet_data = new Input_Data();

                    {
                        var a_index = 0;

                        Misc.decode_be(out a_packet_data.afe_cell_volt1, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_cell_volt2, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_cell_volt3, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_cell_volt4, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_cell_volt5, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_cell_volt6, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_cell_volt7, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_cell_volt8, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_pack_volt, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_cell_volt_delta, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_temp1, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_temp2, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_current, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_adc_gain, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_adc_offset, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_ov_limit, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.afe_uv_limit, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_state_of_charge, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_voltage, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_current, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_temperature, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_remaining_capacity, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_full_charge_capacity, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_design_capacity, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_average_current, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_time_to_empty, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_time_to_full, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_internal_temp, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_cycle_count, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_state_of_health, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_charging_voltage, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_charging_current, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_lifetime_max_temp, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_lifetime_min_temp, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_lifetime_max_chg_curr, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_lifetime_max_dsg_curr, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_lifetime_max_volt, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_lifetime_min_volt, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.fg_voltage_divider, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.adc_pack_volt, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.adc_vref, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.micro_temp, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.ts_temp, a_data_slice, ref a_index);
                        Misc.decode_be(out a_packet_data.serial_number, a_data_slice, ref a_index);

                        Contracts.assert(a_index is BYTES);
                    }

                    var a_send_data = new byte[8].AsSpan();

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.afe_cell_volt1, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_cell_volt2, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_cell_volt3, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_cell_volt4, a_send_data, ref a_index);

                        received_message(a_protocol, 0x00u, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.afe_cell_volt5, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_cell_volt6, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_cell_volt7, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_cell_volt8, a_send_data, ref a_index);

                        received_message(a_protocol, 0x01u, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.afe_pack_volt, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_cell_volt_delta, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_current, a_send_data, ref a_index);

                        received_message(a_protocol, 0x02u, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.afe_adc_gain, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_adc_offset, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_ov_limit, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_uv_limit, a_send_data, ref a_index);

                        received_message(a_protocol, 0x03u, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.fg_voltage, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_current, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_average_current, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_state_of_charge, a_send_data, ref a_index);

                        received_message(a_protocol, 0x04u, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.afe_temp1, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.afe_temp2, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_temperature, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_internal_temp, a_send_data, ref a_index);

                        received_message(a_protocol, 0x05u, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.fg_full_charge_capacity, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_remaining_capacity, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_design_capacity, a_send_data, ref a_index);

                        received_message(a_protocol, 0x06u, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.fg_time_to_empty, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_time_to_full, a_send_data, ref a_index);

                        received_message(a_protocol, 0x07u, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.fg_state_of_health, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_cycle_count, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_charging_voltage, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_charging_current, a_send_data, ref a_index);

                        received_message(a_protocol, 0x08u, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.fg_lifetime_max_temp, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_lifetime_min_temp, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_voltage_divider, a_send_data, ref a_index);

                        received_message(a_protocol, 0x0Cu, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.fg_lifetime_max_chg_curr, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_lifetime_max_dsg_curr, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_lifetime_max_volt, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.fg_lifetime_min_volt, a_send_data, ref a_index);

                        received_message(a_protocol, 0x0Du, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.adc_pack_volt, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.adc_vref, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.micro_temp, a_send_data, ref a_index);
                        Misc.encode_le(a_packet_data.ts_temp, a_send_data, ref a_index);

                        received_message(a_protocol, 0x0Eu, a_send_data[..a_index].ToArray());
                    }

                    {
                        var a_index = 0;

                        Misc.encode_le(a_packet_data.serial_number, a_send_data, ref a_index);

                        received_message(a_protocol, 0x0Fu, a_send_data[..a_index].ToArray());
                    }

                    Message_Result.make_value(out a_result, (a_can_id, a_can_data));
                }
                catch(Exception a_except)
                {
                    a_protocol.received_error(a_except.Message);

                    Message_Result.make_error(out a_result, a_except);
                }

                a_callback(a_result);
            },
            500
        );

        return false;
    }

    private static void
    response_verify
    (
        Message_Result<byte[]> a_recv_data,
        uint a_slave_addr,
        Modbus_Master.Func_Code a_func_code,
        int a_byte_count,
        out Modbus_Master.Parse_Result a_parse_result,
        out ReadOnlySpan<byte> a_data_slice
    )
    {
        if(a_recv_data.error is Exception a_error)
        {
            a_parse_result = new();
            a_data_slice = new();

            throw new Exception($"send failed: {a_error.Message}");
        }

        if(Modbus_Master.parse(a_recv_data.value, out a_parse_result, out a_data_slice) is null)
        {
            _ = Modbus_Master.parse_error(a_recv_data.value, out var a_parse_error_result);

            throw new Exception($"error code: 0x{a_parse_error_result.error_code:X2}");
        }

        if(a_parse_result.slave_addr != a_slave_addr)
        {
            throw new Exception($"unexpected slave address: {a_parse_result.slave_addr}, expected 0x{a_slave_addr:X2}");
        }

        if(a_parse_result.func_code != (byte)a_func_code)
        {
            throw new Exception($"unexpected function code: 0x{a_parse_result.func_code:X2}: expected 0x{(byte)a_func_code:X2}");
        }

        if(a_data_slice.Length != a_byte_count)
        {
            throw new Exception($"unexpected byte count: {a_data_slice.Length}: expected {a_byte_count}");
        }
    }

    private static void
    received_command_response
    (Protocol a_protocol, byte[] a_data) =>
        received_message(a_protocol, 0xFFu, a_data);

    private static void
    received_message
    (Protocol a_protocol, uint a_message_number, byte[] a_data)
    {
        var a_id =
            new CAN_ID()
            {
                ext_id = a_message_number,
                is_can_fd = false,
                is_remote = false,
                size = a_data.Length
            };

        a_protocol.received_message(a_id, a_data);
    }

    private struct
    Coil_Data
    {
        public byte coils_lo;
        public byte coils_hi;
    }

    private struct
    Discrete_Data
    {
        public byte afe_sys_stat;
        public byte afe_cellbal1;
        public byte afe_cellbal2;
        public byte afe_cellbal3;
        public byte afe_sys_ctrl1;
        public byte afe_sys_ctrl2;
        public byte afe_protect1;
        public byte afe_protect2;
        public byte afe_protect3;
        public byte afe_ov_trip;
        public byte afe_uv_trip;
        public byte afe_cc_cfg;
        public ushort fg_control_status;
        public ushort fg_battery_status;
        public ushort fg_operation_status;
        public ushort fg_gauging_status;
        public ushort fg_manufacturing_status;
        public byte uc_rev;
        public byte fg_rev;
    }

    private struct
    Holding_Data
    {
        public uint serial_number;
        public uint fg_unseal_key;
        public uint fg_full_unseal_key;
        public ushort fg_applied_voltage;
        public short fg_applied_current;
    }

    private struct
    Input_Data
    {
        public ushort afe_cell_volt1;
        public ushort afe_cell_volt2;
        public ushort afe_cell_volt3;
        public ushort afe_cell_volt4;
        public ushort afe_cell_volt5;
        public ushort afe_cell_volt6;
        public ushort afe_cell_volt7;
        public ushort afe_cell_volt8;
        public ushort afe_pack_volt;
        public ushort afe_cell_volt_delta;
        public ushort afe_temp1;
        public ushort afe_temp2;
        public short afe_current;
        public ushort afe_adc_gain;
        public short afe_adc_offset;
        public ushort afe_ov_limit;
        public ushort afe_uv_limit;
        public ushort fg_state_of_charge;
        public ushort fg_voltage;
        public short fg_current;
        public ushort fg_temperature;
        public ushort fg_remaining_capacity;
        public ushort fg_full_charge_capacity;
        public ushort fg_design_capacity;
        public short fg_average_current;
        public ushort fg_time_to_empty;
        public ushort fg_time_to_full;
        public ushort fg_internal_temp;
        public ushort fg_cycle_count;
        public ushort fg_state_of_health;
        public ushort fg_charging_voltage;
        public ushort fg_charging_current;
        public ushort fg_lifetime_max_temp;
        public ushort fg_lifetime_min_temp;
        public ushort fg_lifetime_max_chg_curr;
        public ushort fg_lifetime_max_dsg_curr;
        public ushort fg_lifetime_max_volt;
        public ushort fg_lifetime_min_volt;
        public ushort fg_voltage_divider;
        public ushort adc_pack_volt;
        public ushort adc_vref;
        public ushort micro_temp;
        public ushort ts_temp;
        public uint serial_number;
    }
}