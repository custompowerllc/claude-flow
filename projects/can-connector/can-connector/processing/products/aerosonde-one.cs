using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Globalization;
using contracts;
using Tomlyn;
using Tomlyn.Model;
using utility.can;
using utility.misc;

namespace program_ns.processing.products;

internal sealed class
Aerosonde_One : Product
{
    private enum
    Destination_ID : uint
    {
        PACK_1,
        PACK_2,
        PACK_3,
        PACK_4
    }

    private enum
    Message_Register_ID : uint
    {
        MESSAGE_0,
        MESSAGE_1,
        MESSAGE_2,
        MESSAGE_3,
        MESSAGE_4,
        MESSAGE_5,
        MESSAGE_6,
        MESSAGE_7,
        MESSAGE_8,
        MESSAGE_9,
        MESSAGE_A,
        MESSAGE_B,
        MESSAGE_C,
        MESSAGE_D,
        MESSAGE_E
    };

    private enum
    Status_Register_ID : uint
    {
        FG_CONTROL_STATUS_HI,
        FG_CONTROL_STATUS_LO,
        FG_FLAGS_A_HI,
        FG_FLAGS_A_LO,
        FG_FLAGS_B_HI,
        FG_FLAGS_B_LO,
        AFE_SYS_STAT,
        AFE_CELLBAL1,
        AFE_CELLBAL2,
        AFE_CELLBAL3,
        AFE_SYS_CTRL1,
        AFE_SYS_CTRL2
    };

    private enum
    Query_ID : uint
    {
        MESSAGE_0,
        MESSAGE_1,
        MESSAGE_2,
        MESSAGE_3,
        MESSAGE_4,
        MESSAGE_5,
        MESSAGE_6,
        MESSAGE_7,
        MESSAGE_8,
        MESSAGE_9,
        MESSAGE_A,
        MESSAGE_B,
        MESSAGE_C,
        MESSAGE_D,
        MESSAGE_E,
        ALL
    };

    private enum
    Command_ID : uint
    {
        ENTER_SHIP_MODE,
        SET_PERIODIC_TIME,
        CLEAR_ERROR,
        HEATER_OFF,
        HEATER_ON,
        HEATER_AUTO,
        HEATER_LIMITS,
        CHARGE_FET_OFF,
        CHARGE_FET_ON,
        SET_SERIAL_NUMBER,
        RESET_MICRO,
        FG_IT_ENABLE,
        FG_RESET,
        FG_SEAL,
        FG_UNSEAL,
        FG_UNSEAL_FULL,
        ENTER_BOOTLOADER
    };

    private static readonly Destination s_default_dest =
        new() { id = (uint)Destination_ID.PACK_4, display_text = "Pack 4" };

    private static readonly Query s_default_query =
        new() { id = (uint)Query_ID.ALL, display_text = "All" };

    private static readonly Command s_enter_bootloader =
        new()
        {
            id = (uint)Command_ID.ENTER_BOOTLOADER,
            display_text = "Enter Bootloader",
            arguments = ImmutableArray.Create<(string, string)>(),
            response_timeout = null
        };

    private static readonly HashSet<Destination> s_dest_set =
    new()
    {
        new() { id = (uint)Destination_ID.PACK_1, display_text = "Pack 1" },
        new() { id = (uint)Destination_ID.PACK_2, display_text = "Pack 2" },
        new() { id = (uint)Destination_ID.PACK_3, display_text = "Pack 3" },
        s_default_dest
    };

    private static readonly HashSet<Message_Register> s_message_register_set =
    new()
    {
        new() { id = (uint)Message_Register_ID.MESSAGE_0, display_text = "Message 0" },
        new() { id = (uint)Message_Register_ID.MESSAGE_1, display_text = "Message 1" },
        new() { id = (uint)Message_Register_ID.MESSAGE_2, display_text = "Message 2" },
        new() { id = (uint)Message_Register_ID.MESSAGE_3, display_text = "Message 3" },
        new() { id = (uint)Message_Register_ID.MESSAGE_4, display_text = "Message 4" },
        new() { id = (uint)Message_Register_ID.MESSAGE_5, display_text = "Message 5" },
        new() { id = (uint)Message_Register_ID.MESSAGE_6, display_text = "Message 6" },
        new() { id = (uint)Message_Register_ID.MESSAGE_7, display_text = "Message 7" },
        new() { id = (uint)Message_Register_ID.MESSAGE_8, display_text = "Message 8" },
        new() { id = (uint)Message_Register_ID.MESSAGE_9, display_text = "Message 9" },
        new() { id = (uint)Message_Register_ID.MESSAGE_A, display_text = "Message A" },
        new() { id = (uint)Message_Register_ID.MESSAGE_B, display_text = "Message B" },
        new() { id = (uint)Message_Register_ID.MESSAGE_C, display_text = "Message C" },
        new() { id = (uint)Message_Register_ID.MESSAGE_D, display_text = "Message D" },
        new() { id = (uint)Message_Register_ID.MESSAGE_E, display_text = "Message E" }
    };

    private static readonly HashSet<Status_Register> s_status_register_set =
    new()
    {
        new()
        {
            id = (uint)Status_Register_ID.FG_CONTROL_STATUS_HI,
            display_text = "Fuel Gauge Control Status Hi",
            bit7 = ("RSVD", true),
            bit6 = ("FAS", false),
            bit5 = ("SS", false),
            bit4 = ("CALEN", false),
            bit3 = ("CCA", false),
            bit2 = ("BCA", false),
            bit1 = ("CSV", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_CONTROL_STATUS_LO,
            display_text = "Fuel Gauge Control Status Lo",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("FULLSLEEP", false),
            bit4 = ("SLEEP", false),
            bit3 = ("LDMD", false),
            bit2 = ("RUP_DIS", false),
            bit1 = ("VOK", false),
            bit0 = ("QEN", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_FLAGS_A_HI,
            display_text = "Fuel Gauge Flags A Hi",
            bit7 = ("OTC", false),
            bit6 = ("OTD", false),
            bit5 = ("BATHI", false),
            bit4 = ("BATLOW", false),
            bit3 = ("CHG_INH", false),
            bit2 = ("XCHG", false),
            bit1 = ("FC", false),
            bit0 = ("CHG", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_FLAGS_A_LO,
            display_text = "Fuel Gauge Flags A Lo",
            bit7 = ("OCVTAKEN", false),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("CF", false),
            bit3 = ("RSVD", true),
            bit2 = ("SOC1", false),
            bit1 = ("SOCF", false),
            bit0 = ("DSG", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_FLAGS_B_HI,
            display_text = "Fuel Gauge Flags B Hi",
            bit7 = ("SOH", false),
            bit6 = ("LIFE", false),
            bit5 = ("FIRSTDOD", false),
            bit4 = ("RSVD", true),
            bit3 = ("RSVD", true),
            bit2 = ("DODEOC", false),
            bit1 = ("DTRC", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_FLAGS_B_LO,
            display_text = "Fuel Gauge Flags B Lo",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("RSVD", true),
            bit2 = ("RSVD", true),
            bit1 = ("RSVD", true),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_SYS_STAT,
            display_text = "AFE SYS_STAT",
            bit7 = ("CC_READY", false),
            bit6 = ("RSVD", true),
            bit5 = ("DEV_XRDY", false),
            bit4 = ("OVRD_ALERT", false),
            bit3 = ("UV", false),
            bit2 = ("OV", false),
            bit1 = ("SCD", false),
            bit0 = ("OCD", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_CELLBAL1,
            display_text = "AFE CELLBAL1",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("C5", false),
            bit3 = ("C4", false),
            bit2 = ("C3", false),
            bit1 = ("C2", false),
            bit0 = ("C1", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_CELLBAL2,
            display_text = "AFE CELLBAL2",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("C10", false),
            bit3 = ("C9", false),
            bit2 = ("C8", false),
            bit1 = ("C7", false),
            bit0 = ("C6", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_CELLBAL3,
            display_text = "AFE CELLBAL1",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("C15", false),
            bit3 = ("C14", false),
            bit2 = ("C13", false),
            bit1 = ("C12", false),
            bit0 = ("C11", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_SYS_CTRL1,
            display_text = "AFE SYS_CTRL1",
            bit7 = ("LOAD_PRSNT", false),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("ADC_EN", false),
            bit3 = ("TEMP_SEL", false),
            bit2 = ("RSVD", true),
            bit1 = ("SHUT_A", false),
            bit0 = ("SHUT_B", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_SYS_CTRL2,
            display_text = "AFE SYS_CTRL2",
            bit7 = ("DELAY_DIS", false),
            bit6 = ("CC_EN", false),
            bit5 = ("CC_ONESHOT", false),
            bit4 = ("RSVD", true),
            bit3 = ("RSVD", true),
            bit2 = ("RSVD", true),
            bit1 = ("DSG_ON", false),
            bit0 = ("CHG_ON", false)
        }
    };

    private static readonly HashSet<Query> s_query_set =
    new()
    {
        new() { id = (uint)Query_ID.MESSAGE_0, display_text = "Message 0" },
        new() { id = (uint)Query_ID.MESSAGE_1, display_text = "Message 1" },
        new() { id = (uint)Query_ID.MESSAGE_2, display_text = "Message 2" },
        new() { id = (uint)Query_ID.MESSAGE_3, display_text = "Message 3" },
        new() { id = (uint)Query_ID.MESSAGE_4, display_text = "Message 4" },
        new() { id = (uint)Query_ID.MESSAGE_5, display_text = "Message 5" },
        new() { id = (uint)Query_ID.MESSAGE_6, display_text = "Message 6" },
        new() { id = (uint)Query_ID.MESSAGE_7, display_text = "Message 7" },
        new() { id = (uint)Query_ID.MESSAGE_8, display_text = "Message 8" },
        new() { id = (uint)Query_ID.MESSAGE_9, display_text = "Message 9" },
        new() { id = (uint)Query_ID.MESSAGE_A, display_text = "Message A" },
        new() { id = (uint)Query_ID.MESSAGE_B, display_text = "Message B" },
        new() { id = (uint)Query_ID.MESSAGE_C, display_text = "Message C" },
        new() { id = (uint)Query_ID.MESSAGE_D, display_text = "Message D" },
        new() { id = (uint)Query_ID.MESSAGE_E, display_text = "Message E" },
        s_default_query
    };

    private static readonly HashSet<Command> s_command_set_advanced =
    new()
    {
        new()
        {
            id = (uint)Command_ID.ENTER_SHIP_MODE,
            display_text = "Enter Ship Mode",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.SET_PERIODIC_TIME,
            display_text = "Set Periodic Time",
            arguments = ImmutableArray.Create(("Time (ms):", "1000")),
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.CLEAR_ERROR,
            display_text = "Clear Error",
            arguments = ImmutableArray.Create(("Bits (hex):", "FF")),
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.HEATER_OFF,
            display_text = "Heater Off",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.HEATER_ON,
            display_text = "Heater On",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.HEATER_AUTO,
            display_text = "Heater Auto",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.HEATER_LIMITS,
            display_text = "Heater Limits",
            arguments =
            ImmutableArray.Create(("Low Limit (°C):", string.Empty), ("High Limit (°C):", string.Empty)),
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.CHARGE_FET_OFF,
            display_text = "Charge FET Off",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.CHARGE_FET_ON,
            display_text = "Charge FET On",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.SET_SERIAL_NUMBER,
            display_text = "Set Serial Number",
            arguments = ImmutableArray.Create(("SN:", string.Empty)),
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.RESET_MICRO,
            display_text = "Reset Microcontroller",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.FG_IT_ENABLE,
            display_text = "IT Enable",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.FG_RESET,
            display_text = "Reset Fuel Gauge",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.FG_SEAL,
            display_text = "Seal Fuel Gauge",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.FG_UNSEAL,
            display_text = "Unseal Fuel Gauge",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.FG_UNSEAL_FULL,
            display_text = "Unseal Fuel Gauge (full)",
            response_timeout = null
        }
    };

    private static readonly HashSet<Command> s_command_set_simple =
    new()
    {

        new()
        {
            id = (uint)Command_ID.ENTER_SHIP_MODE,
            display_text = "Enter Ship Mode",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.SET_PERIODIC_TIME,
            display_text = "Set Periodic Time",
            arguments = ImmutableArray.Create(("Time (ms):", "1000")),
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.CLEAR_ERROR,
            display_text = "Clear Error",
            arguments = ImmutableArray.Create(("Bits (hex):", "FF")),
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.HEATER_OFF,
            display_text = "Heater Off",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.HEATER_ON,
            display_text = "Heater On",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.HEATER_AUTO,
            display_text = "Heater Auto",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.HEATER_LIMITS,
            display_text = "Heater Limits",
            arguments =
            ImmutableArray.Create(("Low Limit (°C):", string.Empty), ("High Limit (°C):", string.Empty)),
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.CHARGE_FET_OFF,
            display_text = "Charge Fet Off",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.CHARGE_FET_ON,
            display_text = "Charge Fet On",
            response_timeout = null
        }
    };

    public
    Aerosonde_One
    (Config_Data a_config):
    base()
    {
        var a_table = Toml.Parse(a_config.config_file_text).ToModel();

        m_advanced_mode = (bool)((TomlTable)a_table["aerosonde"])["advanced-mode"];
    }

    private readonly bool m_advanced_mode;

    public override IReadOnlySet<Destination> destination_set => s_dest_set;
    public override IReadOnlySet<Message_Register> message_register_set => s_message_register_set;
    public override IReadOnlySet<Status_Register> status_register_set => s_status_register_set;
    public override IReadOnlySet<Query> query_set => s_query_set;
    public override IReadOnlySet<Command> command_set => m_advanced_mode ? s_command_set_advanced : s_command_set_simple;
    public override Destination? default_destination => s_default_dest;
    public override Query? default_query => s_default_query;
    public override Command? enter_bootloader_command => s_enter_bootloader;

    protected override void
    new_can_message
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if((a_id.id & 0x1FFFF000u) is not 0x10005000u)
        {
            return;
        }

        var a_pck = (a_id.id & 0x000000F0u) >> 4;
        var a_msg = (a_id.id & 0x0000000Fu) >> 0;

        var a_data_parsed =
        a_msg switch
        {
            0x0u => parse_message_0(a_data),
            0x1u => parse_message_1(a_data),
            0x2u => parse_message_2(a_data),
            0x3u => parse_message_3(a_data),
            0x4u => parse_message_4(a_data),
            0x5u => parse_message_5(a_data),
            0x6u => parse_message_6(a_data),
            0x7u => parse_message_7(a_data),
            0x8u => parse_message_8(a_data),
            0x9u => parse_message_9(a_data),
            0xAu => parse_message_a(a_data),
            0xBu => parse_message_b(a_data),
            0xCu => parse_message_c(a_data),
            0xDu => parse_message_d(a_data),
            0xEu => parse_message_e(a_data),
            _ => null
        };

        if(a_data_parsed is null)
        {
            return;
        }

        using var a_g1 = String_Builder_Pool.acquire();

        add_mess_register_parsed
        (
            message_register_map[a_msg],
            new(a_id, a_data)
            {
                id_interpreted = a_g1.value.Append($"PCK={a_pck} MSG={a_msg:X1}").ToString(),
                data_interpreted = a_data_parsed
            }
        );
    }

    protected override void
    new_query
    (Destination? a_dest, Query a_query)
    {
        Contracts.assert(a_dest is not null);

        void
        add_query
        (Destination a_dest, uint a_msg)
        {
            var a_empty = Array.Empty<byte>();

            using var a_g1 = String_Builder_Pool.acquire();
            using var a_g2 = String_Builder_Pool.acquire();

            add_outgoing_can_message
            (
                new(compute_outgoing_id(a_dest, a_msg, a_empty.Length, out var a_pck), a_empty)
                {
                    id_interpreted = a_g1.value.Append($"PCK={a_pck} MSG={a_msg:X1}").ToString(),
                    data_interpreted = a_g2.value.Append($"Query: Message {a_msg:X1}").ToString()
                }
            );
        }

        var a_query_id = (Query_ID)a_query.id;

        switch(a_query_id)
        {
            case Query_ID.MESSAGE_0: { add_query(a_dest, 0x0u); } break;
            case Query_ID.MESSAGE_1: { add_query(a_dest, 0x1u); } break;
            case Query_ID.MESSAGE_2: { add_query(a_dest, 0x2u); } break;
            case Query_ID.MESSAGE_3: { add_query(a_dest, 0x3u); } break;
            case Query_ID.MESSAGE_4: { add_query(a_dest, 0x4u); } break;
            case Query_ID.MESSAGE_5: { add_query(a_dest, 0x5u); } break;
            case Query_ID.MESSAGE_6: { add_query(a_dest, 0x6u); } break;
            case Query_ID.MESSAGE_7: { add_query(a_dest, 0x7u); } break;
            case Query_ID.MESSAGE_8: { add_query(a_dest, 0x8u); } break;
            case Query_ID.MESSAGE_9: { add_query(a_dest, 0x9u); } break;
            case Query_ID.MESSAGE_A: { add_query(a_dest, 0xAu); } break;
            case Query_ID.MESSAGE_B: { add_query(a_dest, 0xBu); } break;
            case Query_ID.MESSAGE_C: { add_query(a_dest, 0xCu); } break;
            case Query_ID.MESSAGE_D: { add_query(a_dest, 0xDu); } break;
            case Query_ID.MESSAGE_E: { add_query(a_dest, 0xEu); } break;
            case Query_ID.ALL:
            {
                const uint MSG = 0xFu;
                const ushort CMD = 0x0003;

                var a_data = new byte[2];
                var a_index = 0;

                Misc.encode_le(CMD, a_data, ref a_index);

                using var a_g1 = String_Builder_Pool.acquire();
                using var a_g2 = String_Builder_Pool.acquire();

                add_outgoing_can_message
                (
                    new(compute_outgoing_id(a_dest, MSG, a_data.Length, out var a_pck), a_data)
                    {
                        id_interpreted = a_g1.value.Append($"PCK={a_pck} MSG={MSG:X1}").ToString(),
                        data_interpreted = a_g2.value.Append($"Command 0x{CMD:X4}: Query All").ToString()
                    }
                );
            } break;
            default: throw new ArgumentOutOfRangeException(nameof(a_query));
        }
    }

    protected override void
    new_command
    (Destination? a_dest, Command a_command, in ReadOnlySpan<string> a_args)
    {
        Contracts.assert(a_dest is not null);

        void
        add_command
        (Destination a_dest, Command a_command, ushort a_cmd, byte[] a_data)
        {
            const uint MSG = 0xFu;

            using var a_g1 = String_Builder_Pool.acquire();
            using var a_g2 = String_Builder_Pool.acquire();

            add_outgoing_can_message
            (
                new(compute_outgoing_id(a_dest, MSG, a_data.Length, out var a_pck), a_data)
                {
                    id_interpreted = a_g1.value.Append($"PCK={a_pck} MSG={MSG:X1}").ToString(),
                    data_interpreted = a_g2.value.Append($"Command 0x{a_cmd:X4}: {a_command.display_text}").ToString()
                }
            );
        }

        var a_command_id = (Command_ID)a_command.id;

        var (a_cmd, a_data) =
            a_command_id switch
            {
                Command_ID.ENTER_SHIP_MODE   => process_enter_ship_mode(),
                Command_ID.SET_PERIODIC_TIME => process_set_periodic_time(a_args[0]),
                Command_ID.CLEAR_ERROR       => process_clear_error(a_args[0]),
                Command_ID.HEATER_OFF        => process_heater_off_on_auto(0x0000),
                Command_ID.HEATER_ON         => process_heater_off_on_auto(0x0001),
                Command_ID.HEATER_AUTO       => process_heater_off_on_auto(0x0002),
                Command_ID.HEATER_LIMITS     => process_heater_limits(a_args[0], a_args[1]),
                Command_ID.CHARGE_FET_OFF    => process_charge_fet_off_on(0x0000),
                Command_ID.CHARGE_FET_ON     => process_charge_fet_off_on(0x0001),
                Command_ID.SET_SERIAL_NUMBER => process_set_serial_number(a_args[0]),
                Command_ID.RESET_MICRO       => process_reset_micro(),
                Command_ID.FG_IT_ENABLE      => process_fg_it_enable(),
                Command_ID.FG_RESET          => process_fg_reset(),
                Command_ID.FG_SEAL           => process_fg_seal(),
                Command_ID.FG_UNSEAL         => process_fg_unseal(),
                Command_ID.FG_UNSEAL_FULL    => process_fg_unseal_full(),
                Command_ID.ENTER_BOOTLOADER  => process_enter_bootloader(),
                _ => throw new ArgumentOutOfRangeException(nameof(a_command))
            };

        add_command(a_dest, a_command, a_cmd, a_data);
    }

    private static string?
    parse_message_0
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_v1, a_data, ref a_index);
        Misc.decode_le(out ushort a_v2, a_data, ref a_index);
        Misc.decode_le(out ushort a_v3, a_data, ref a_index);
        Misc.decode_le(out ushort a_v4, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"V1={0.001 * a_v1:F3}; ")
            .Append($"V2={0.001 * a_v2:F3}; ")
            .Append($"V3={0.001 * a_v3:F3}; ")
            .Append($"V4={0.001 * a_v4:F3}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_1
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_v1, a_data, ref a_index);
        Misc.decode_le(out ushort a_v2, a_data, ref a_index);
        Misc.decode_le(out ushort a_v3, a_data, ref a_index);
        Misc.decode_le(out ushort a_v4, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"V5={0.001 * a_v1:F3}; ")
            .Append($"V6={0.001 * a_v2:F3}; ")
            .Append($"V7={0.001 * a_v3:F3}; ")
            .Append($"V8={0.001 * a_v4:F3}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_2
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_v1, a_data, ref a_index);
        Misc.decode_le(out ushort a_v2, a_data, ref a_index);
        Misc.decode_le(out ushort a_v3, a_data, ref a_index);
        Misc.decode_le(out ushort a_v4, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"V9={0.001 * a_v1:F3}; ")
            .Append($"V10={0.001 * a_v2:F3}; ")
            .Append($"V11={0.001 * a_v3:F3}; ")
            .Append($"V12={0.001 * a_v4:F3}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_3
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_v1, a_data, ref a_index);
        Misc.decode_le(out ushort a_v2, a_data, ref a_index);
        Misc.decode_le(out ushort a_v3, a_data, ref a_index);
        Misc.decode_le(out ushort a_v4, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"V13={0.001 * a_v1:F3}; ")
            .Append($"V14={0.001 * a_v2:F3}; ")
            .Append($"V15={0.001 * a_v3:F3}; ")
            .Append($"VBAT={0.001 * a_v4:F3}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_4
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_volt, a_data, ref a_index);
        Misc.decode_le(out short a_curr, a_data, ref a_index);
        Misc.decode_le(out ushort a_soc, a_data, ref a_index);
        Misc.decode_le(out short a_temp, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Battery Volt: {0.001 * a_volt:F3}V; ")
            .Append($"Current: {0.006 * a_curr:F3}A; ")
            .Append($"State of Charge: {a_soc}%; ")
            .Append($"Pack Temp: {0.1 * a_temp:F1}°C; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_5
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_error, a_data, ref a_index);
        Misc.decode_le(out byte a_state, a_data, ref a_index);
        Misc.decode_le(out ushort a_max_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_chg_cycles, a_data, ref a_index);
        Misc.decode_le(out ushort a_serial_number, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Error: 0x{a_error:X2}; ")
            .Append($"State: 0x{a_state:X2}; ")
            .Append($"Max Temp: {to_celcius(a_max_temp):F1}°C; ")
            .Append($"Charge Cycles: {a_chg_cycles}; ")
            .Append($"Serial Number: {a_serial_number:D5}; ")
            .ToString();

        return a_result;
    }

    private string?
    parse_message_6
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_control_status, a_data, ref a_index);
        Misc.decode_le(out ushort a_pack_config, a_data, ref a_index);
        Misc.decode_le(out ushort a_flags_a, a_data, ref a_index);
        Misc.decode_le(out ushort a_flags_b, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Control Status: 0x{a_control_status:X4}; ")
            .Append($"Pack Config: 0x{a_pack_config:X4}; ")
            .Append($"Flags A: 0x{a_flags_a:X4}; ")
            .Append($"Flags B: 0x{a_flags_b:X4}; ")
            .ToString();

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_CONTROL_STATUS_HI],
            (byte)((a_control_status & 0xFF00u) >> 8)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_CONTROL_STATUS_LO],
            (byte)((a_control_status & 0x00FFu) >> 0)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_FLAGS_A_HI],
            (byte)((a_flags_a & 0xFF00u) >> 8)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_FLAGS_A_LO],
            (byte)((a_flags_a & 0x00FFu) >> 0)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_FLAGS_B_HI],
            (byte)((a_flags_b & 0xFF00u) >> 8)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_FLAGS_B_LO],
            (byte)((a_flags_b & 0x00FFu) >> 0)
        );

        return a_result;
    }

    private static string?
    parse_message_7
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_itcc, a_data, ref a_index);
        Misc.decode_le(out byte a_learned_status, a_data, ref a_index);
        Misc.decode_le(out byte a_max_error, a_data, ref a_index);
        Misc.decode_le(out ushort a_fcc, a_data, ref a_index);
        Misc.decode_le(out ushort a_rc, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"IT Cycle Count: {a_itcc}; ")
            .Append($"Learned Status: 0x{a_learned_status:X2}; ")
            .Append($"Max Error: {a_max_error}; ")
            .Append($"FCC: {6 * a_fcc}mAh; ")
            .Append($"RC: {6 * a_rc}mAh; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_8
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_lt_max_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_lt_min_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_lt_max_chg_curr, a_data, ref a_index);
        Misc.decode_le(out ushort a_lt_max_dsg_curr, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"LT Max Temp: {to_celcius(a_lt_max_temp):F1}°C; ")
            .Append($"LT Min Temp: {to_celcius(a_lt_min_temp):F1}°C; ")
            .Append($"LT Max Chg Curr: {0.006 * a_lt_max_chg_curr:F3}A; ")
            .Append($"LT Max Dsg Curr: {0.006 * a_lt_max_dsg_curr:F3}A; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_9
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_lt_max_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_lt_min_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_micro_firmware, a_data, ref a_index);
        Misc.decode_le(out ushort a_fg_firmware, a_data, ref a_index);

        var a_vmajor = (a_micro_firmware & 0b1111110000000000) >> 10;
        var a_vminor = (a_micro_firmware & 0b0000001111110000) >> 4;
        var a_rev    = (a_micro_firmware & 0b0000000000001111) >> 0;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"LT Max Volt: {0.001 * a_lt_max_volt:F3}V; ")
            .Append($"LT Min Volt: {0.001 * a_lt_min_volt:F3}V; ")
            .Append($"µController Firmware Ver: {a_vmajor}.{a_vminor}.{a_rev}; ")
            .Append($"Fuel Gauge Firmware Ver: 0x{a_fg_firmware:X4}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_a
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_volt_divider, a_data, ref a_index);
        Misc.decode_le(out ushort a_fg_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_soh, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Voltage divider: {a_volt_divider}; ")
            .Append($"Fuel Gauge Temp: {to_celcius(a_fg_temp):F1}°C; ")
            .Append($"State of Health {a_soh}%; ")
            .ToString();

        return a_result;
    }

    private string?
    parse_message_b
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_sys_stat, a_data, ref a_index);
        Misc.decode_le(out byte a_sys_ctl1, a_data, ref a_index);
        Misc.decode_le(out byte a_sys_ctl2, a_data, ref a_index);
        Misc.decode_le(out byte a_cellbal1, a_data, ref a_index);
        Misc.decode_le(out byte a_cellbal2, a_data, ref a_index);
        Misc.decode_le(out byte a_cellbal3, a_data, ref a_index);
        Misc.decode_le(out ushort a_volt_delta, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"sys_stat: 0x{a_sys_stat:X2}; ")
            .Append($"sys_ctl1: 0x{a_sys_ctl1:X2}; ")
            .Append($"sys_ctl2: 0x{a_sys_ctl2:X2}; ")
            .Append($"cellbal1: 0x{a_cellbal1:X2}; ")
            .Append($"cellbal2: 0x{a_cellbal2:X2}; ")
            .Append($"cellbal3: 0x{a_cellbal3:X2}; ")
            .Append($"Cell VΔ: {a_volt_delta}mV; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_SYS_STAT], a_sys_stat);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_CELLBAL1], a_cellbal1);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_CELLBAL2], a_cellbal2);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_CELLBAL3], a_cellbal3);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_SYS_CTRL1], a_sys_ctl1);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_SYS_CTRL2], a_sys_ctl2);

        return a_result;
    }

    private static string?
    parse_message_c
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_protect1, a_data, ref a_index);
        Misc.decode_le(out byte a_protect2, a_data, ref a_index);
        Misc.decode_le(out byte a_protect3, a_data, ref a_index);
        Misc.decode_le(out byte a_ov_trip, a_data, ref a_index);
        Misc.decode_le(out byte a_uv_trip, a_data, ref a_index);
        Misc.decode_le(out byte a_cc_cfg, a_data, ref a_index);
        Misc.decode_le(out ushort a_volt_delta_alert, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"protect1: 0x{a_protect1:X2}; ")
            .Append($"protect2: 0x{a_protect2:X2}; ")
            .Append($"protect3: 0x{a_protect3:X2}; ")
            .Append($"ov_trip:  0x{a_ov_trip:X2}; ")
            .Append($"uv_trip:  0x{a_uv_trip:X2}; ")
            .Append($"cc_cfg:   0x{a_cc_cfg:X2}; ")
            .Append($"Cell VΔ Alert: {a_volt_delta_alert is not 0}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_d
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_temp_ts1, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_ts2, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_ts3, a_data, ref a_index);
        Misc.decode_le(out short a_afe_curr, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Temp TS1(PT): {to_celcius(a_temp_ts1):F1}°C; ")
            .Append($"Temp TS2(RT2): {to_celcius(a_temp_ts2):F1}°C; ")
            .Append($"Temp TS3(RT1): {to_celcius(a_temp_ts3):F1}°C; ")
            .Append($"AFE Current: {0.006 * a_afe_curr:F3}A; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_e
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_temp_micro, a_data, ref a_index);
        Misc.decode_le(out byte a_heater_state, a_data, ref a_index);
        Misc.decode_le(out byte a_heater_mode, a_data, ref a_index);
        Misc.decode_le(out ushort a_limit_lo, a_data, ref a_index);
        Misc.decode_le(out ushort a_limit_hi, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Temp µController: {to_celcius(a_temp_micro):F1}°C; ")
            .Append($"Heater State: {(a_heater_state is 0 ? "Off" : "On")}; ")
            .Append($"Heater Mode: {(a_heater_mode is 0 ? "Manual" : "Auto")}; ")
            .Append($"Heater Lo Lim: {to_celcius(a_limit_lo):F1}°C; ")
            .Append($"Heater Hi Lim: {to_celcius(a_limit_hi):F1}°C; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_enter_ship_mode()
    {
        const ushort CMD = 0x0001;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_set_periodic_time
    (string a_arg0)
    {
        const ushort CMD = 0x0002;
        const int MIN_PERIOD = 10;

        var a_interval = ushort.Parse(a_arg0, NumberStyles.None);

        if(a_interval is < MIN_PERIOD)
        {
            throw new ArgumentException($"Periodic Time: time ({a_interval} ms) must be >= {MIN_PERIOD} ms");
        }

        var a_data = new byte[4];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_interval, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_clear_error
    (string a_arg0)
    {
        const ushort CMD = 0x0004;

        var a_bits = byte.Parse(a_arg0, NumberStyles.AllowHexSpecifier);

        var a_data = new byte[4];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le((ushort)a_bits, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_heater_off_on_auto
    (ushort a_code)
    {
        const ushort CMD = 0x0005;

        var a_data = new byte[4];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_code, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_heater_limits
    (string a_arg0, string a_arg1)
    {
        const ushort CMD = 0x0007;
        const double MIN_LIMIT = -273.1;
        const double MAX_LIMIT = 1000.0;

        var a_lo = double.Parse(a_arg0, NumberStyles.Float);
        var a_hi = double.Parse(a_arg1, NumberStyles.Float);

        if(a_lo is < MIN_LIMIT or > MAX_LIMIT)
        {
            throw new ArgumentException($"Heater Limits: low limit ({a_lo:F1}°C) must be >= {MIN_LIMIT:F1}°C and <= {MAX_LIMIT:F1}°C");
        }

        if(a_hi is < MIN_LIMIT or > MAX_LIMIT)
        {
            throw new ArgumentException($"Heater Limits: high limit ({a_hi:F1}°C) must be >= {MIN_LIMIT:F1}°C and <= {MAX_LIMIT:F1}°C");
        }

        if(a_lo > a_hi)
        {
            throw new ArgumentException($"Heater Limits: low limit ({a_lo:F1}°C) must be <= high limit ({a_hi:F1}°C)");
        }

        var a_data = new byte[6];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le((ushort)(10.0 * (a_lo + 273.1)), a_data, ref a_index);
        Misc.encode_le((ushort)(10.0 * (a_hi + 273.1)), a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_charge_fet_off_on
    (ushort a_code)
    {
        const ushort CMD = 0x0008;

        var a_data = new byte[4];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_code, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_set_serial_number
    (string a_arg0)
    {
        const ushort CMD = 0x0009;

        var a_sn = ushort.Parse(a_arg0, NumberStyles.None);
        var a_data = new byte[4];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_sn, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_reset_micro()
    {
        const ushort CMD = 0x0006;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_it_enable()
    {
        const ushort CMD = 0x000A;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_reset()
    {
        const ushort CMD = 0x000B;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_seal()
    {
        const ushort CMD = 0x000C;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_unseal()
    {
        const ushort CMD = 0x000D;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_unseal_full()
    {
        const ushort CMD = 0x000E;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_enter_bootloader()
    {
        const ushort CMD = 0x000F;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static double
    to_celcius
    (ushort a_raw) => 0.1 * a_raw - 273.1;

    private static CAN_ID
    compute_outgoing_id
    (Destination a_destination, uint a_message_number, int a_size, out uint a_dest)
    {
        if(a_message_number is > 0xFu)
        {
            throw new ArgumentOutOfRangeException(nameof(a_message_number));
        }

        a_dest =
            (Destination_ID)a_destination.id switch
            {
                Destination_ID.PACK_1 => 1u,
                Destination_ID.PACK_2 => 2u,
                Destination_ID.PACK_3 => 3u,
                Destination_ID.PACK_4 => 4u,
                _ => throw new ArgumentOutOfRangeException(nameof(a_destination))
            };

        return
            new()
            {
                ext_id = 0x10005100u | (a_dest << 4) | a_message_number,
                is_can_fd = false,
                is_remote = false,
                size = a_size
            };
    }
}
