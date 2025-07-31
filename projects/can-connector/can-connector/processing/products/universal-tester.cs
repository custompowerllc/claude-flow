using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using contracts;
using utility.can;
using utility.misc;

namespace program_ns.processing.products;

internal sealed class
Universal_Tester : Product
{
    private enum
    CAN_Command : uint
    {
        ECHO_S,
        ECHO_R,
        GET_STATUS_S,
        GET_STATUS_R,
        SIGNAL_SELECT_S,
        SIGNAL_SELECT_R,
        PS_SELECT_S,
        PS_SELECT_R,
        LOAD_SELECT_S,
        LOAD_SELECT_R,
        BYPASS_SELECT_S,
        BYPASS_SELECT_R,
        RESET_ALL_S,
        RESET_ALL_R,
        BUTTON_EVENT = 240,
        INVALID = 256
    }

    private enum
    Signal_Code : byte
    {
        OFF,
        THERMISTOR,
        ID_RESISTOR,
        PACK_VOLT,
        BATT_VOLT,
        INVALID
    }

    private enum
    PS_Code : byte
    {
        OFF,
        PACK,
        BATT,
        INVALID
    }

    private enum
    Load_Code : byte
    {
        OFF,
        NORMAL,
        LIGHT,
        INVALID
    }

    private enum
    Bypass_Code : byte
    {
        OFF,
        POSITIVE,
        NEGATIVE,
        INVALID
    }

    private enum
    Destination_ID : uint
    {

    }

    private enum
    Message_Register_ID : uint
    {
        ECHO = CAN_Command.ECHO_R,
        GET_STATUS = CAN_Command.GET_STATUS_R,
        SIGNAL_SELECT = CAN_Command.SIGNAL_SELECT_R,
        PS_SELECT = CAN_Command.PS_SELECT_R,
        LOAD_SELECT = CAN_Command.LOAD_SELECT_R,
        BYPASS_SELECT = CAN_Command.BYPASS_SELECT_R,
        RESET_ALL = CAN_Command.RESET_ALL_R,
        BUTTON_EVENT = CAN_Command.BUTTON_EVENT
    };

    private enum
    Status_Register_ID : uint
    {
        IO_STATE_HI,
        IO_STATE_LO
    };

    private enum
    Query_ID : uint
    {
        GET_STATUS
    };

    private enum
    Command_ID : uint
    {
        ECHO,
        SIGNAL_SELECT_OFF,
        SIGNAL_SELECT_THERMISTOR,
        SIGNAL_SELECT_ID_RESISTOR,
        SIGNAL_SELECT_PACK_VOLT,
        SIGNAL_SELECT_BATT_VOLT,
        PS_SELECT_OFF,
        PS_SELECT_PACK,
        PS_SELECT_BATT,
        LOAD_SELECT_OFF,
        LOAD_SELECT_NORMAL,
        LOAD_SELECT_LIGHT,
        BYPASS_SELECT_OFF,
        BYPASS_SELECT_POSITIVE,
        BYPASS_SELECT_NEGATIVE,
        RESET_ALL
    };

    private static readonly Query s_default_query =
        new() { id = (uint)Query_ID.GET_STATUS, display_text = "Status" };

    private static readonly HashSet<Destination> s_dest_set =
    new()
    {

    };

    private static readonly HashSet<Message_Register> s_message_register_set =
    new()
    {
        new() { id = (uint)Message_Register_ID.ECHO, display_text = "Echo Response" },
        new() { id = (uint)Message_Register_ID.GET_STATUS, display_text = "Status" },
        new() { id = (uint)Message_Register_ID.SIGNAL_SELECT, display_text = "Signal Select Respnse" },
        new() { id = (uint)Message_Register_ID.PS_SELECT, display_text = "PS Select Response" },
        new() { id = (uint)Message_Register_ID.LOAD_SELECT, display_text = "Load Select Response" },
        new() { id = (uint)Message_Register_ID.BYPASS_SELECT, display_text = "Bypass Select Response" },
        new() { id = (uint)Message_Register_ID.RESET_ALL, display_text = "Reset All Response" },
        new() { id = (uint)Message_Register_ID.BUTTON_EVENT, display_text = "Button Event" }
    };

    private static readonly HashSet<Status_Register> s_status_register_set =
    new()
    {
        new()
        {
            id = (uint)Status_Register_ID.IO_STATE_HI,
            display_text = "IO State Hi",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("START", false),
            bit2 = ("BYP_POS", false),
            bit1 = ("BYP_NEG", false),
            bit0 = ("R_THERM", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.IO_STATE_LO,
            display_text = "IO State Lo",
            bit7 = ("R_IDRES", false),
            bit6 = ("R_PACKV", false),
            bit5 = ("R_BATTV", false),
            bit4 = ("LOAD_EN", false),
            bit3 = ("LED", false),
            bit2 = ("LLOAD_EN", false),
            bit1 = ("PS_SEL", false),
            bit0 = ("PS_EN", false)
        }
    };

    private static readonly HashSet<Query> s_query_set =
    new()
    {
        s_default_query
    };

    private static readonly HashSet<Command> s_command_set =
    new()
    {
        new()
        {
            id = (uint)Command_ID.ECHO,
            display_text = "Echo",
            arguments = ImmutableArray.Create(("Data:", "DEADBEEF")),
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.SIGNAL_SELECT_OFF,
            display_text = "Measurement Off",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.SIGNAL_SELECT_THERMISTOR,
            display_text = "Measure Thermistor",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.SIGNAL_SELECT_ID_RESISTOR,
            display_text = "Measure ID Resistor",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.SIGNAL_SELECT_PACK_VOLT,
            display_text = "Measure Pack Volt",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.SIGNAL_SELECT_BATT_VOLT,
            display_text = "Measure Batt Volt",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.PS_SELECT_OFF,
            display_text = "PS Off",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.PS_SELECT_PACK,
            display_text = "PS Pack",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.PS_SELECT_BATT,
            display_text = "PS Batt",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.LOAD_SELECT_OFF,
            display_text = "Load Off",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.LOAD_SELECT_NORMAL,
            display_text = "Normal Load",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.LOAD_SELECT_LIGHT,
            display_text = "Light Load",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.BYPASS_SELECT_OFF,
            display_text = "Bypass Off",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.BYPASS_SELECT_POSITIVE,
            display_text = "Positive Bypass",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.BYPASS_SELECT_NEGATIVE,
            display_text = "Negative Bypass",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.RESET_ALL,
            display_text = "Reset All",
            response_timeout = 1000
        }
    };

    public
    Universal_Tester() :
    base()
    {

    }

    public override IReadOnlySet<Destination> destination_set => s_dest_set;
    public override IReadOnlySet<Message_Register> message_register_set => s_message_register_set;
    public override IReadOnlySet<Status_Register> status_register_set => s_status_register_set;
    public override IReadOnlySet<Query> query_set => s_query_set;
    public override IReadOnlySet<Command> command_set => s_command_set;
    public override Destination? default_destination => null;
    public override Query? default_query => s_default_query;
    public override Command? enter_bootloader_command => null;

    protected override void
    new_can_message
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if((a_id.id & 0xFFFFFF00u) is not 0x00000000u)
        {
            return;
        }

        var a_msg = a_id.id;

        var a_data_parsed =
        (Message_Register_ID)a_msg switch
        {
            Message_Register_ID.ECHO          => parse_echo(a_data),
            Message_Register_ID.GET_STATUS    => parse_status(a_data),
            Message_Register_ID.SIGNAL_SELECT => parse_signal_select(a_data),
            Message_Register_ID.PS_SELECT     => parse_ps_select(a_data),
            Message_Register_ID.LOAD_SELECT   => parse_load_select(a_data),
            Message_Register_ID.BYPASS_SELECT => parse_bypass_select(a_data),
            Message_Register_ID.RESET_ALL     => parse_reset_all(a_data),
            Message_Register_ID.BUTTON_EVENT  => parse_button_event(a_data),
            _ => null
        };

        if(a_data_parsed is null)
        {
            return;
        }

        if((Message_Register_ID)a_msg is not Message_Register_ID.GET_STATUS and not Message_Register_ID.BUTTON_EVENT)
        {
            set_pending_command_completed();
        }

        using var a_g1 = String_Builder_Pool.acquire();

        add_mess_register_parsed
        (
            message_register_map[a_msg],
            new(a_id, a_data)
            {
                id_interpreted = a_g1.value.Append($"MSG={a_msg:X2}").ToString(),
                data_interpreted = a_data_parsed
            }
        );
    }

    protected override void
    new_query
    (Destination? a_dest, Query a_query)
    {
        Contracts.assert(a_dest is null);

        void
        add_query
        (Query a_query, CAN_Command a_id, byte[] a_data)
        {
            var a_message = (uint)a_id;

            using var a_g1 = String_Builder_Pool.acquire();
            using var a_g2 = String_Builder_Pool.acquire();

            add_outgoing_can_message
            (
                new
                (
                    new()
                    {
                        ext_id = a_message,
                        is_can_fd = false,
                        is_remote = false,
                        size = a_data.Length
                    },
                    a_data
                )
                {
                    id_interpreted = a_g1.value.Append($"MSG={a_message:X2}").ToString(),
                    data_interpreted = a_g2.value.Append($"{a_query.display_text}").ToString()
                }
            );
        }

        var a_query_id = (Query_ID)a_query.id;

        if(a_query_id is Query_ID.GET_STATUS)
        {
            add_query(a_query, CAN_Command.GET_STATUS_S, Array.Empty<byte>());
        }
    }

    protected override void
    new_command
    (Destination? a_dest, Command a_command, in ReadOnlySpan<string> a_args)
    {
        void
        add_command
        (Command a_command, CAN_Command a_id, byte[] a_data)
        {
            var a_message = (uint)a_id;

            using var a_g1 = String_Builder_Pool.acquire();
            using var a_g2 = String_Builder_Pool.acquire();

            add_outgoing_can_message
            (
                new
                (
                    new()
                    {
                        ext_id = a_message,
                        is_can_fd = false,
                        is_remote = false,
                        size = a_data.Length
                    },
                    a_data
                )
                {
                    id_interpreted = a_g1.value.Append($"MSG={a_message:X2}").ToString(),
                    data_interpreted = a_g2.value.Append($"{a_command.display_text}").ToString()
                }
            );
        }

        var a_command_id = (Command_ID)a_command.id;

        var (a_cmd, a_data) =
            a_command_id switch
            {
                Command_ID.ECHO => process_echo(a_args[0]),
                Command_ID.SIGNAL_SELECT_OFF => process_signal_select(Signal_Code.OFF),
                Command_ID.SIGNAL_SELECT_THERMISTOR => process_signal_select(Signal_Code.THERMISTOR),
                Command_ID.SIGNAL_SELECT_ID_RESISTOR => process_signal_select(Signal_Code.ID_RESISTOR),
                Command_ID.SIGNAL_SELECT_PACK_VOLT => process_signal_select(Signal_Code.PACK_VOLT),
                Command_ID.SIGNAL_SELECT_BATT_VOLT => process_signal_select(Signal_Code.BATT_VOLT),
                Command_ID.PS_SELECT_OFF => process_ps_select(PS_Code.OFF),
                Command_ID.PS_SELECT_PACK => process_ps_select(PS_Code.PACK),
                Command_ID.PS_SELECT_BATT => process_ps_select(PS_Code.BATT),
                Command_ID.LOAD_SELECT_OFF => process_load_select(Load_Code.OFF),
                Command_ID.LOAD_SELECT_NORMAL => process_load_select(Load_Code.NORMAL),
                Command_ID.LOAD_SELECT_LIGHT => process_load_select(Load_Code.LIGHT),
                Command_ID.BYPASS_SELECT_OFF => process_bypass_select(Bypass_Code.OFF),
                Command_ID.BYPASS_SELECT_POSITIVE => process_bypass_select(Bypass_Code.POSITIVE),
                Command_ID.BYPASS_SELECT_NEGATIVE => process_bypass_select(Bypass_Code.NEGATIVE),
                Command_ID.RESET_ALL => process_reset_all(),
                _ => throw new ArgumentOutOfRangeException(nameof(a_command))
            };

        add_command(a_command, a_cmd, a_data);
    }

    private static string?
    parse_echo
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_be(out ulong a_number, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        return a_g1.value.Append($"{a_number:X16}; ").ToString();
    }

    private string?
    parse_status
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_io_state, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp1, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp2, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"IO State: 0x{a_io_state:X4}; ")
            .Append($"Temp1: {to_celcius(a_temp1):F1}°C; ")
            .Append($"Temp2: {to_celcius(a_temp2):F1}°C; ")
            .ToString();

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.IO_STATE_HI],
            (byte)((a_io_state & 0xFF00u) >> 8)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.IO_STATE_LO],
            (byte)((a_io_state & 0x00FFu) >> 0)
        );

        return a_result;
    }

    private static string?
    parse_signal_select
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 1)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_code, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Measure Mode: {(Signal_Code)a_code}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_ps_select
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 1)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_code, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS Mode: {(PS_Code)a_code}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_load_select
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 1)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_code, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Load Mode: {(Load_Code)a_code}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_bypass_select
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 1)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_code, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Bypass Mode: {(Bypass_Code)a_code}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_reset_all
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 0)
        {
            return null;
        }

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Reset All Completed; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_button_event
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 0)
        {
            return null;
        }

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Start Pressed; ")
            .ToString();

        return a_result;
    }

    private static (CAN_Command a_cmd, byte[] a_data)
    process_echo
    (string a_arg)
    {
        var a_number = ulong.Parse(a_arg, System.Globalization.NumberStyles.HexNumber);

        var a_data = new byte[8];
        var a_index = 0;

        Misc.encode_be(a_number, a_data, ref a_index);

        return (CAN_Command.ECHO_S, a_data);
    }

    private static (CAN_Command a_cmd, byte[] a_data)
    process_signal_select
    (Signal_Code a_code)
    {
        var a_data = new byte[1];
        var a_index = 0;

        Misc.encode_be((byte)a_code, a_data, ref a_index);

        return (CAN_Command.SIGNAL_SELECT_S, a_data);
    }

    private static (CAN_Command a_cmd, byte[] a_data)
    process_ps_select
    (PS_Code a_code)
    {
        var a_data = new byte[1];
        var a_index = 0;

        Misc.encode_le((byte)a_code, a_data, ref a_index);

        return (CAN_Command.PS_SELECT_S, a_data);
    }

    private static (CAN_Command a_cmd, byte[] a_data)
    process_load_select
    (Load_Code a_code)
    {
        var a_data = new byte[1];
        var a_index = 0;

        Misc.encode_le((byte)a_code, a_data, ref a_index);

        return (CAN_Command.LOAD_SELECT_S, a_data);
    }

    private static (CAN_Command a_cmd, byte[] a_data)
    process_bypass_select
    (Bypass_Code a_code)
    {
        var a_data = new byte[1];
        var a_index = 0;

        Misc.encode_le((byte)a_code, a_data, ref a_index);

        return (CAN_Command.BYPASS_SELECT_S, a_data);
    }

    private static (CAN_Command a_cmd, byte[] a_data)
    process_reset_all() =>
        (CAN_Command.RESET_ALL_S, Array.Empty<byte>());

    private static double
    to_celcius
    (ushort a_raw) => 0.1 * a_raw - 273.1;
}

