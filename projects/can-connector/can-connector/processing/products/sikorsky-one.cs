using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Globalization;
using contracts;
using utility.can;
using utility.misc;

namespace program_ns.processing.products;

using Translator = translators.Sikorsky_One_Modbus;

internal sealed class
Sikorsky_One : Product
{
    private enum
    Destination_ID : uint
    {
        SLAVE_1
    }

    private enum
    Message_Register_ID : uint
    {
        MESSAGE_00,
        MESSAGE_01,
        MESSAGE_02,
        MESSAGE_03,
        MESSAGE_04,
        MESSAGE_05,
        MESSAGE_06,
        MESSAGE_07,
        MESSAGE_08,
        MESSAGE_09,
        MESSAGE_0A,
        MESSAGE_0B,
        MESSAGE_0C,
        MESSAGE_0D,
        MESSAGE_0E,
        MESSAGE_0F,
        MESSAGE_10,
        MESSAGE_11,
        MESSAGE_12,
        MESSAGE_COMMAND_RESPONSE = 0xFFu
    };

    private enum
    Status_Register_ID :
    uint
    {
        COILS_A,
        COILS_B,
        FG_CONTROL_STATUS_HI,
        FG_CONTROL_STATUS_LO,
        FG_FLAGS_A_HI,
        FG_FLAGS_A_LO,
        FG_FLAGS_B_HI,
        FG_FLAGS_B_LO,
        FG_PACK_CONFIG_HI,
        FG_PACK_CONFIG_LO,
        FG_LEARNED_STATUS,
        AFE_STATUS0,
        AFE_STATUS1,
        AFE_STATUS2,
        AFE_STATUS3,
        AFE_CONTROL0,
        AFE_CONTROL1,
        AFE_CONTROL2,
        AFE_CONTROL3
    };

    private enum
    Query_ID :
    uint
    {
        COILS,
        DISCRETES,
        HOLDINGS,
        INPUTS,
        ALL
    };

    private enum
    Command_ID :
    uint
    {
        ENTER_BOOTLOADER,
        FETS_OFF,
        FETS_ON,
        RESET_MICRO,
        FG_RESET,
        FG_IT_ENABLE,
        FG_SEAL,
        FG_UNSEAL_KEY,
        FG_UNSEAL,
        FG_FULL_UNSEAL_KEY,
        FG_FULL_UNSEAL,
        AFE_PROGRAM,
        FG_PROGRAM,
        FG_CAL_CC_OFFSET,
        FG_CAL_BOARD_OFFSET,
        FG_CAL_APPLIED_VOLTAGE,
        FG_CAL_VOLTAGE,
        FG_CAL_APPLIED_CURRENT,
        FG_CAL_CURRENT,
        SERIAL_NUMBER_SET,
        SERIAL_NUMBER_STORE,
        BLINK_DISABLE,
        BLINK_ENABLE
    };

    private static readonly Destination s_default_dest =
        new() { id = (uint)Destination_ID.SLAVE_1, display_text = "Slave 1" };

    private static readonly Query s_default_query =
        new() { id = (uint)Query_ID.ALL, display_text = "All" };

    private static readonly HashSet<Destination> s_dest_set =
    new()
    {
        s_default_dest
    };

    private static readonly HashSet<Message_Register> s_message_register_set =
    new()
    {
        new() { id = (uint)Message_Register_ID.MESSAGE_00, display_text = "Message 00" },
        new() { id = (uint)Message_Register_ID.MESSAGE_01, display_text = "Message 01" },
        new() { id = (uint)Message_Register_ID.MESSAGE_02, display_text = "Message 02" },
        new() { id = (uint)Message_Register_ID.MESSAGE_03, display_text = "Message 03" },
        new() { id = (uint)Message_Register_ID.MESSAGE_04, display_text = "Message 04" },
        new() { id = (uint)Message_Register_ID.MESSAGE_05, display_text = "Message 05" },
        new() { id = (uint)Message_Register_ID.MESSAGE_06, display_text = "Message 06" },
        new() { id = (uint)Message_Register_ID.MESSAGE_07, display_text = "Message 07" },
        new() { id = (uint)Message_Register_ID.MESSAGE_08, display_text = "Message 08" },
        new() { id = (uint)Message_Register_ID.MESSAGE_09, display_text = "Message 09" },
        new() { id = (uint)Message_Register_ID.MESSAGE_0A, display_text = "Message 0A" },
        new() { id = (uint)Message_Register_ID.MESSAGE_0B, display_text = "Message 0B" },
        new() { id = (uint)Message_Register_ID.MESSAGE_0C, display_text = "Message 0C" },
        new() { id = (uint)Message_Register_ID.MESSAGE_0D, display_text = "Message 0D" },
        new() { id = (uint)Message_Register_ID.MESSAGE_0E, display_text = "Message 0E" },
        new() { id = (uint)Message_Register_ID.MESSAGE_0F, display_text = "Message 0F" },
        new() { id = (uint)Message_Register_ID.MESSAGE_10, display_text = "Message 10" },
        new() { id = (uint)Message_Register_ID.MESSAGE_11, display_text = "Message 11" },
        new() { id = (uint)Message_Register_ID.MESSAGE_12, display_text = "Message 12" },
        new() { id = (uint)Message_Register_ID.MESSAGE_COMMAND_RESPONSE, display_text = "Last Command Response" }
    };

    private static readonly HashSet<Status_Register> s_status_register_set =
    new()
    {
        new()
        {
            id = (uint)Status_Register_ID.COILS_A,
            display_text = "Coils A",
            bit7 = ("RSVD", true),
            bit6 = ("BLINK_EN", false),
            bit5 = ("STORE_SN", false),
            bit4 = ("CAL_CURR", false),
            bit3 = ("CAL_VOLT", false),
            bit2 = ("CAL_BOARD", false),
            bit1 = ("CAL_CC", false),
            bit0 = ("PROG_FG", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.COILS_B,
            display_text = "Coils B",
            bit7 = ("PROG_AFE", false),
            bit6 = ("FG_FAS", false),
            bit5 = ("FG_SS", false),
            bit4 = ("FG_IT_EN", false),
            bit3 = ("FG_RESET", false),
            bit2 = ("μC_RESET", false),
            bit1 = ("FETS", false),
            bit0 = ("ENTER_BOOT", false)
        },
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
            id = (uint)Status_Register_ID.FG_PACK_CONFIG_HI,
            display_text = "Fuel Gauge Pack Config Hi",
            bit7 = ("RESCAP", false),
            bit6 = ("CAL_EN", false),
            bit5 = ("SCALED", false),
            bit4 = ("RSVD", true),
            bit3 = ("VOLTSEL", false),
            bit2 = ("IWAKE", false),
            bit1 = ("RSNS1", false),
            bit0 = ("RSNS0", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_PACK_CONFIG_LO,
            display_text = "Fuel Gauge Pack Config Lo",
            bit7 = ("RFACTSTEP", false),
            bit6 = ("SLEEP", false),
            bit5 = ("RMFCC", false),
            bit4 = ("NiDT", false),
            bit3 = ("NiDV", false),
            bit2 = ("PB_RSTRT", false),
            bit1 = ("GNDSEL", false),
            bit0 = ("TEMPS", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_LEARNED_STATUS,
            display_text = "Fuel Gauge Learned Status",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("Qmax", false),
            bit2 = ("ITEN", false),
            bit1 = ("CF1", false),
            bit0 = ("CF0", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_STATUS0,
            display_text = "AFE Status 0",
            bit7 = ("CUTF", false),
            bit6 = ("COTF", false),
            bit5 = ("DUTF", false),
            bit4 = ("DOTF", false),
            bit3 = ("UVLOF", false),
            bit2 = ("UVF", false),
            bit1 = ("OVLOF", false),
            bit0 = ("OVF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_STATUS1,
            display_text = "AFE Status 1",
            bit7 = ("VEOC", false),
            bit6 = ("RSVD", true),
            bit5 = ("OPENF", false),
            bit4 = ("CELLF", false),
            bit3 = ("DSCF", false),
            bit2 = ("DOCF", false),
            bit1 = ("COCF", false),
            bit0 = ("IOTF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_STATUS2,
            display_text = "AFE Status 2",
            bit7 = ("LVCHG", false),
            bit6 = ("INT_SCAN", false),
            bit5 = ("ECC_FAIL", false),
            bit4 = ("ECC_USED", false),
            bit3 = ("DCHING", false),
            bit2 = ("CHING", false),
            bit1 = ("CH_PRSNT", false),
            bit0 = ("LD_PRSNT", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_STATUS3,
            display_text = "AFE Status 3",
            bit7 = ("RSVD", true),
            bit6 = ("SLEEP", false),
            bit5 = ("DOZE", false),
            bit4 = ("IDLE", false),
            bit3 = ("CBUV", false),
            bit2 = ("CBOV", false),
            bit1 = ("CBUT", false),
            bit0 = ("CBOT", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_CONTROL0,
            display_text = "AFE Control 0",
            bit7 = ("RSVD", true),
            bit6 = ("ADC STRT", false),
            bit5 = ("CG1", false),
            bit4 = ("CG0", false),
            bit3 = ("AMO3", false),
            bit2 = ("AMO2", false),
            bit1 = ("AMO1", false),
            bit0 = ("AMO0", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_CONTROL1,
            display_text = "AFE Control 1",
            bit7 = ("CLR_LERR", false),
            bit6 = ("LMON_EN", false),
            bit5 = ("CLR_CERR", false),
            bit4 = ("CMON_EN", false),
            bit3 = ("PSD", false),
            bit2 = ("PCFET", false),
            bit1 = ("CFET", false),
            bit0 = ("DFET", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_CONTROL2,
            display_text = "AFE Control 2",
            bit7 = ("RSVD", true),
            bit6 = ("µC FET", false),
            bit5 = ("µC CBAL", false),
            bit4 = ("µC LMON", false),
            bit3 = ("µC CMON", false),
            bit2 = ("µC SCAN", false),
            bit1 = ("OW_STRT", false),
            bit0 = ("CBAL_ON", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_CONTROL3,
            display_text = "AFE Control 3",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("PDWN", false),
            bit2 = ("SLEEP", false),
            bit1 = ("DOZE", false),
            bit0 = ("IDLE", false)
        }
    };

    private static readonly HashSet<Query> s_query_set =
    new()
    {
        new() { id = (uint)Query_ID.COILS, display_text = "Coils" },
        new() { id = (uint)Query_ID.DISCRETES, display_text = "Discretes" },
        new() { id = (uint)Query_ID.HOLDINGS, display_text = "Holdings" },
        new() { id = (uint)Query_ID.INPUTS, display_text = "Inputs" },
        s_default_query
    };

    private static readonly HashSet<Command> s_command_set =
    new()
    {
        new()
        {
            id = (uint)Command_ID.FETS_OFF,
            display_text = "FETs Off",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FETS_ON,
            display_text = "FETs On",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.RESET_MICRO,
            display_text = "Reset Microcontroller",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_RESET,
            display_text = "Reset Fuel Gauge",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_IT_ENABLE,
            display_text = "Fuel Gauge IT Enable",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_SEAL,
            display_text = "Seal Fuel Gauge",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_UNSEAL_KEY,
            display_text = "Set FG Unseal Key",
            arguments = ImmutableArray.Create(("Key:", "17176789")),
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_UNSEAL,
            display_text = "Unseal Fuel Gauge",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_FULL_UNSEAL_KEY,
            display_text = "Set FG Full Unseal Key",
            arguments = ImmutableArray.Create(("Key:", "1717AABB")),
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_FULL_UNSEAL,
            display_text = "Full Unseal Fuel Gauge",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.AFE_PROGRAM,
            display_text = "Program AFE",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_PROGRAM,
            display_text = "Program Fuel Gauge",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_CC_OFFSET,
            display_text = "Calibrate FG CC Offset",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_BOARD_OFFSET,
            display_text = "Calibrate FG Board Offset",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_APPLIED_VOLTAGE,
            display_text = "Set FG Applied Voltage",
            arguments = ImmutableArray.Create(("Applied Voltage (V):", "26.6")),
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_VOLTAGE,
            display_text = "Calibrate FG Voltage",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_APPLIED_CURRENT,
            display_text = "Set FG Applied Current",
            arguments = ImmutableArray.Create(("Applied Current (A):", "-2.0")),
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_CURRENT,
            display_text = "Calibrate FG Current",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.SERIAL_NUMBER_SET,
            display_text = "Set Serial Number",
            arguments = ImmutableArray.Create(("SN:", string.Empty)),
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.SERIAL_NUMBER_STORE,
            display_text = "Store Serial Number",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.BLINK_DISABLE,
            display_text = "Blink Disable",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.BLINK_ENABLE,
            display_text = "Blink Enable",
            response_timeout = 1000
        }
    };

    public
    Sikorsky_One
    (Config_Data a_config) :
    base()
    {
        if(a_config.bootloader is not null)
        {
            m_enter_bootloader =
                new()
                {
                    id = (uint)Command_ID.ENTER_BOOTLOADER,
                    display_text = "Enter Bootloader",
                    response_timeout = null
                };

            m_dest_set = new HashSet<Destination>();
            m_message_register_set = new HashSet<Message_Register>();
            m_status_register_set = new HashSet<Status_Register>();
            m_query_set = new HashSet<Query>();
            m_command_set = new HashSet<Command>();

            return;
        }

        m_enter_bootloader =
            new()
            {
                id = (uint)Command_ID.ENTER_BOOTLOADER,
                display_text = "Enter Bootloader",
                response_timeout = 1000
            };

        m_dest_set = s_dest_set;
        m_message_register_set = s_message_register_set;
        m_status_register_set = s_status_register_set;
        m_query_set = s_query_set;

        var a_command_set = new HashSet<Command>() { m_enter_bootloader };

        a_command_set.UnionWith(s_command_set);

        m_command_set = a_command_set;
    }

    private readonly Command m_enter_bootloader;
    private readonly IReadOnlySet<Destination> m_dest_set;
    private readonly IReadOnlySet<Message_Register> m_message_register_set;
    private readonly IReadOnlySet<Status_Register> m_status_register_set;
    private readonly IReadOnlySet<Query> m_query_set;
    private readonly IReadOnlySet<Command> m_command_set;

    public override IReadOnlySet<Destination> destination_set => m_dest_set;
    public override IReadOnlySet<Message_Register> message_register_set => m_message_register_set;
    public override IReadOnlySet<Status_Register> status_register_set => m_status_register_set;
    public override IReadOnlySet<Query> query_set => m_query_set;
    public override IReadOnlySet<Command> command_set => m_command_set;
    public override Destination? default_destination => s_default_dest;
    public override Query? default_query => s_default_query;
    public override Command? enter_bootloader_command => m_command_set.Contains(m_enter_bootloader) ? null : m_enter_bootloader;

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
        a_msg switch
        {
            0x00u => parse_message_00(a_data),
            0x01u => parse_message_01(a_data),
            0x02u => parse_message_02(a_data),
            0x03u => parse_message_03(a_data),
            0x04u => parse_message_04(a_data),
            0x05u => parse_message_05(a_data),
            0x06u => parse_message_06(a_data),
            0x07u => parse_message_07(a_data),
            0x08u => parse_message_08(a_data),
            0x09u => parse_message_09(a_data),
            0x0Au => parse_message_0A(a_data),
            0x0Bu => parse_message_0B(a_data),
            0x0Cu => parse_message_0C(a_data),
            0x0Du => parse_message_0D(a_data),
            0x0Eu => parse_message_0E(a_data),
            0x0Fu => parse_message_0F(a_data),
            0x10u => parse_message_10(a_data),
            0x11u => parse_message_11(a_data),
            0x12u => parse_message_12(a_data),
            0xFFu => parse_command_response(a_data),
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
                id_interpreted = a_g1.value.Append($"MSG={a_msg:X2}").ToString(),
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
        (Query a_query, ushort a_cmd, byte[] a_data)
        {
            const uint MSG = 0xFFu;

            using var a_g1 = String_Builder_Pool.acquire();
            using var a_g2 = String_Builder_Pool.acquire();

            add_outgoing_can_message
            (
                new
                (
                    new()
                    {
                        ext_id = MSG,
                        is_can_fd = false,
                        is_remote = false,
                        size = a_data.Length
                    },
                    a_data
                )
                {
                    id_interpreted = a_g1.value.Append($"MSG={MSG:X2}").ToString(),
                    data_interpreted = a_g2.value.Append($"Command 0x{a_cmd:X4}: {a_query.display_text}").ToString()
                }
            );
        }

        var a_query_id = (Query_ID)a_query.id;

        if(a_query_id is Query_ID.ALL)
        {

            var (a_cmd, a_data) = process_query_coils();

            add_query(query_map[(uint)Query_ID.COILS], a_cmd, a_data);

            (a_cmd, a_data) = process_query_discretes();

            add_query(query_map[(uint)Query_ID.DISCRETES], a_cmd, a_data);

            (a_cmd, a_data) = process_query_holdings();

            add_query(query_map[(uint)Query_ID.HOLDINGS], a_cmd, a_data);

            (a_cmd, a_data) = process_query_inputs();

            add_query(query_map[(uint)Query_ID.INPUTS], a_cmd, a_data);

            return;
        }

        {
            var (a_cmd, a_data) =
                a_query_id switch
                {
                    Query_ID.COILS => process_query_coils(),
                    Query_ID.DISCRETES => process_query_discretes(),
                    Query_ID.HOLDINGS => process_query_holdings(),
                    Query_ID.INPUTS => process_query_inputs(),
                    _ => throw new ArgumentOutOfRangeException(nameof(a_query))
                };

            add_query(a_query, a_cmd, a_data);
        }
    }

    protected override void
    new_command
    (Destination? a_dest, Command a_command, in ReadOnlySpan<string> a_args)
    {
        void
        add_command
        (Command a_command, ushort a_cmd, byte[] a_data)
        {
            const uint MSG = 0xFFu;

            using var a_g1 = String_Builder_Pool.acquire();
            using var a_g2 = String_Builder_Pool.acquire();

            add_outgoing_can_message
            (
                new
                (
                    new()
                    {
                        ext_id = MSG,
                        is_can_fd = false,
                        is_remote = false,
                        size = a_data.Length
                    },
                    a_data
                )
                {
                    id_interpreted = a_g1.value.Append($"MSG={MSG:X2}").ToString(),
                    data_interpreted = a_g2.value.Append($"Command 0x{a_cmd:X4}: {a_command.display_text}").ToString()
                }
            );
        }

        var a_command_id = (Command_ID)a_command.id;

        var (a_cmd, a_data) =
            a_command_id switch
            {
                Command_ID.ENTER_BOOTLOADER => process_enter_bootloader(),
                Command_ID.FETS_OFF => process_fet(0x00),
                Command_ID.FETS_ON => process_fet(0x01),
                Command_ID.RESET_MICRO => process_reset_micro(),
                Command_ID.FG_RESET => process_fg_reset(),
                Command_ID.FG_IT_ENABLE => process_fg_it_enable(),
                Command_ID.FG_SEAL => process_fg_seal(),
                Command_ID.FG_UNSEAL_KEY => process_fg_unseal_key(a_args[0]),
                Command_ID.FG_UNSEAL => process_fg_unseal(),
                Command_ID.FG_FULL_UNSEAL_KEY => process_fg_full_unseal_key(a_args[0]),
                Command_ID.FG_FULL_UNSEAL => process_fg_full_unseal(),
                Command_ID.AFE_PROGRAM => process_afe_program(),
                Command_ID.FG_PROGRAM => process_fg_program(),
                Command_ID.FG_CAL_CC_OFFSET => process_fg_cal_cc_offset(),
                Command_ID.FG_CAL_BOARD_OFFSET => process_fg_cal_board_offset(),
                Command_ID.FG_CAL_APPLIED_VOLTAGE => process_fg_cal_applied_voltage(a_args[0]),
                Command_ID.FG_CAL_VOLTAGE => process_fg_cal_voltage(),
                Command_ID.FG_CAL_APPLIED_CURRENT => process_fg_cal_applied_current(a_args[0]),
                Command_ID.FG_CAL_CURRENT => process_fg_cal_current(),
                Command_ID.SERIAL_NUMBER_SET => process_serial_number_set(a_args[0]),
                Command_ID.SERIAL_NUMBER_STORE => process_serial_number_store(),
                Command_ID.BLINK_DISABLE => process_blink(0x00),
                Command_ID.BLINK_ENABLE => process_blink(0x01),
                _ => throw new ArgumentOutOfRangeException(nameof(a_command))
            };

        add_command(a_command, a_cmd, a_data);
    }

    #region MESSAGES

    private static string?
    parse_message_00
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
    parse_message_01
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
    parse_message_02
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_pack_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_volt_delta, a_data, ref a_index);
        Misc.decode_le(out short a_current, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"AFE Volt: {0.001 * a_pack_volt:F3}V; ")
            .Append($"Cell Volt Δ: {a_volt_delta}mV; ")
            .Append($"AFE Curr: {0.001 * a_current:F3}A; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_03
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_fg_volt, a_data, ref a_index);
        Misc.decode_le(out short a_fg_curr, a_data, ref a_index);
        Misc.decode_le(out short a_fg_avg_curr, a_data, ref a_index);
        Misc.decode_le(out ushort a_state_of_charge, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"FG Volt: {0.001 * a_fg_volt:F3}V; ")
            .Append($"FG Curr: {0.001 * a_fg_curr:F3}A; ")
            .Append($"FG Avg Curr: {0.001 * a_fg_avg_curr:F3}A; ")
            .Append($"State of Charge: {a_state_of_charge}%; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_04
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_afe_temp1, a_data, ref a_index);
        Misc.decode_le(out ushort a_afe_temp2, a_data, ref a_index);
        Misc.decode_le(out ushort a_fg_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_fg_temp_internal, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"AFE Temp1: {to_celcius(a_afe_temp1):F1}°C; ")
            .Append($"AFE Temp2: {to_celcius(a_afe_temp2):F1}°C; ")
            .Append($"FG Temp: {to_celcius(a_fg_temp):F1}°C; ")
            .Append($"FG Internal Temp: {to_celcius(a_fg_temp_internal):F1}°C; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_05
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_fcc, a_data, ref a_index);
        Misc.decode_le(out ushort a_rc, a_data, ref a_index);
        Misc.decode_le(out ushort a_dc, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Full Charge Capacity: {a_fcc}mAh; ")
            .Append($"Remaining Capacity: {a_rc}mAh; ")
            .Append($"Design Capacity: {a_dc}mAh; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_06
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 4)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_tte, a_data, ref a_index);
        Misc.decode_le(out ushort a_ttf, a_data, ref a_index);

        var a_tte_str = a_tte is 0xFFFF ? "N/A" : a_tte.ToString();
        var a_ttf_str = a_ttf is 0xFFFF ? "N/A" : a_ttf.ToString();

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Time to Empty: {a_tte_str} min; ")
            .Append($"Time to Full: {a_ttf_str} min; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_07
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 4)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_soh, a_data, ref a_index);
        Misc.decode_le(out ushort a_cycle_count, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"State of Health: {a_soh}%; ")
            .Append($"Cycle Count: {a_cycle_count}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_08
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_lt_max_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_lt_min_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_voltage_div, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"LT Max Temp: {to_celcius(a_lt_max_temp):F1}°C; ")
            .Append($"LT Min Temp: {to_celcius(a_lt_min_temp):F1}°C; ")
            .Append($"Voltage Divider: {a_voltage_div}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_09
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_lt_max_chg_curr, a_data, ref a_index);
        Misc.decode_le(out ushort a_lt_min_dsg_curr, a_data, ref a_index);
        Misc.decode_le(out ushort a_lt_max_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_lt_min_volt, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"LT Max Chg Curr: {0.001 * a_lt_max_chg_curr:F3}A; ")
            .Append($"LT Max Dsg Curr: {0.001 * a_lt_min_dsg_curr:F3}A; ")
            .Append($"LT Max Volt: {0.001 * a_lt_max_volt:F3}V; ")
            .Append($"LT Min Volt: {0.001 * a_lt_min_volt:F3}V; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_0A
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_adc_vref, a_data, ref a_index);
        Misc.decode_le(out ushort a_micro_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_ts_temp, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"ADC Vref: {0.001 * a_adc_vref:F3}V; ")
            .Append($"µController Temp: {to_celcius(a_micro_temp):F1}°C; ")
            .Append($"LM73 Temp: {to_celcius(a_ts_temp):F1}°C; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_0B
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_uc_version, a_data, ref a_index);
        Misc.decode_le(out ushort a_fg_version, a_data, ref a_index);
        Misc.decode_le(out uint a_serial, a_data, ref a_index);

        var a_fw_vmajor = (a_uc_version & 0b1111110000000000) >> 10;
        var a_fw_vminor = (a_uc_version & 0b0000001111110000) >> 4;
        var a_fw_rev =    (a_uc_version & 0b0000000000001111) >> 0;

        var a_fg_vmajor = (a_fg_version & 0b1111110000000000) >> 10;
        var a_fg_vminor = (a_fg_version & 0b0000001111110000) >> 4;
        var a_fg_rev =    (a_fg_version & 0b0000000000001111) >> 0;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"µController Firmware Ver: {a_fw_vmajor}.{a_fw_vminor}.{a_fw_rev}; ")
            .Append($"Fuel Gauge Firmware Ver: {a_fg_vmajor}.{a_fg_vminor}.{a_fg_rev}; ")
            .Append($"Serial Number: {a_serial:D10}; ")
            .ToString();

        return a_result;
    }

    private string?
    parse_message_0C
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_fg_control_status, a_data, ref a_index);
        Misc.decode_le(out ushort a_fg_flags_a, a_data, ref a_index);
        Misc.decode_le(out ushort a_fg_flags_b, a_data, ref a_index);
        Misc.decode_le(out ushort a_fg_pack_config, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"FG Control Status: 0x{a_fg_control_status:X4}; ")
            .Append($"FG Flags A: 0x{a_fg_flags_a:X4}; ")
            .Append($"FG Flags B: 0x{a_fg_flags_b:X4}; ")
            .Append($"FG Pack Config: 0x{a_fg_pack_config:X4}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_CONTROL_STATUS_HI], unchecked((byte)(a_fg_control_status >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_CONTROL_STATUS_LO], unchecked((byte)(a_fg_control_status >> 0)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_FLAGS_A_HI], unchecked((byte)(a_fg_flags_a >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_FLAGS_A_LO], unchecked((byte)(a_fg_flags_a >> 0)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_FLAGS_B_HI], unchecked((byte)(a_fg_flags_b >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_FLAGS_B_LO], unchecked((byte)(a_fg_flags_b >> 0)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_PACK_CONFIG_HI], unchecked((byte)(a_fg_pack_config >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_PACK_CONFIG_LO], unchecked((byte)(a_fg_pack_config >> 0)));

        return a_result;
    }

    private string?
    parse_message_0D
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 1)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_fg_learned_status, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"FG Learned Status: 0x{a_fg_learned_status:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_LEARNED_STATUS], a_fg_learned_status);

        return a_result;
    }

    private string?
    parse_message_0E
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_status0, a_data, ref a_index);
        Misc.decode_le(out byte a_status1, a_data, ref a_index);
        Misc.decode_le(out byte a_status2, a_data, ref a_index);
        Misc.decode_le(out byte a_status3, a_data, ref a_index);
        Misc.decode_le(out byte a_control0, a_data, ref a_index);
        Misc.decode_le(out byte a_control1, a_data, ref a_index);
        Misc.decode_le(out byte a_control2, a_data, ref a_index);
        Misc.decode_le(out byte a_control3, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"status0: 0x{a_status0:X2}; ")
            .Append($"status1: 0x{a_status1:X2}; ")
            .Append($"status2: 0x{a_status2:X2}; ")
            .Append($"status3: 0x{a_status3:X2}; ")
            .Append($"control0: 0x{a_control0:X2}; ")
            .Append($"control1: 0x{a_control1:X2}; ")
            .Append($"control2: 0x{a_control2:X2}; ")
            .Append($"control3: 0x{a_control3:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_STATUS0], a_status0);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_STATUS1], a_status1);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_STATUS2], a_status2);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_STATUS3], a_status3);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_CONTROL0], a_control0);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_CONTROL1], a_control1);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_CONTROL2], a_control2);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_CONTROL3], a_control3);

        return a_result;
    }

    private string?
    parse_message_0F
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_coils_a, a_data, ref a_index);
        Misc.decode_le(out byte a_coils_b, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Coils A: 0x{a_coils_a:X2}; ")
            .Append($"Coils b: 0x{a_coils_b:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.COILS_A], a_coils_a);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.COILS_B], a_coils_b);

        return a_result;
    }

    private static string?
    parse_message_10
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 4)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_serial, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Holding Serial Number: {a_serial:D10}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_11
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_unseal_key, a_data, ref a_index);
        Misc.decode_le(out uint a_full_unseal_key, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Holding Unseal Key: 0x{a_unseal_key:X8}; ")
            .Append($"Holding Full Unseal Key: 0x{a_full_unseal_key:X8}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_12
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 4)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_volt, a_data, ref a_index);
        Misc.decode_le(out short a_curr, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Holding Applied Voltage: {0.001 * a_volt:F3}V; ")
            .Append($"Holding Applied Current: {0.001 * a_curr:F3}A; ")
            .ToString();

        return a_result;
    }

    #endregion

    #region COMMANDS

    private string?
    parse_command_response
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is < 2)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_cmd, a_data, ref a_index);

        var a_result =
            (Translator.Command_Number)a_cmd switch
            {
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_ENTER_BOOT => parse_enter_bootloader(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FET => parse_fet(a_data, ref a_index),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_RESET_MICRO => parse_reset_micro(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_RESET => parse_fg_reset(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_IT_EN => parse_fg_it_enable(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_SEAL => parse_fg_seal(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_UNSEAL_KEY => parse_fg_unseal_key(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_UNSEAL => parse_fg_unseal(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_FULL_UNSEAL_KEY => parse_fg_full_unseal_key(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_FULL_UNSEAL => parse_fg_full_unseal(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_PROG_AFE => parse_afe_program(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_PROG_FG => parse_fg_program(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CAL_CC => parse_fg_cal_cc_offset(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CAL_BOARD => parse_fg_cal_board_offset(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CAL_APPLIED_VOLT => parse_fg_cal_applied_voltage(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CAL_VOLT => parse_fg_cal_voltage(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CAL_APPLIED_CURR => parse_fg_cal_applied_current(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CAL_CURR => parse_fg_cal_current(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_SERIAL_NUMBER => parse_serial_number_set(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_SERIAL_NUMBER_STORE => parse_serial_number_store(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_BLINK_EN => parse_blink(a_data, ref a_index),
                _ => null
            };

        if(a_result is not null)
        {
            set_pending_command_completed();
        }

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_enter_bootloader()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_ENTER_BOOT;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_enter_bootloader
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_ENTER_BOOT;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: enter bootloader; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fet
    (byte a_code)
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_FET;

        var a_data = new byte[3];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_code, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fet
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 3)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_FET;

        Misc.decode_le(out byte a_state, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: FETs {(a_state is not 0 ? "ON" : "OFF")}; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_reset_micro()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_RESET_MICRO;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_reset_micro
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_RESET_MICRO;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: pack microcontroller will reset; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_reset()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_RESET;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_reset
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_RESET;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge reset; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_it_enable()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_IT_EN;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_it_enable
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_IT_EN;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge IT enable; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_seal()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_SEAL;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_seal
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_SEAL;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge seal; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_unseal_key
    (string a_arg0)
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_UNSEAL_KEY;

        var a_key = uint.Parse(a_arg0, NumberStyles.AllowHexSpecifier);

        var a_data = new byte[6];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_key, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_unseal_key
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_UNSEAL_KEY;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge unseal key set; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_unseal()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_UNSEAL;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_unseal
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_UNSEAL;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge unseal; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_full_unseal_key
    (string a_arg0)
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_FULL_UNSEAL_KEY;

        var a_key = uint.Parse(a_arg0, NumberStyles.AllowHexSpecifier);

        var a_data = new byte[6];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_key, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_full_unseal_key
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_FULL_UNSEAL_KEY;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge full unseal key set; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_full_unseal()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_FULL_UNSEAL;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_full_unseal
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_FULL_UNSEAL;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge full unseal; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_afe_program()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_PROG_AFE;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_afe_program
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_PROG_AFE;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: program AFE; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_program()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_PROG_FG;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_program
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_PROG_FG;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: program Fuel Gauge; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_cal_cc_offset()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_CAL_CC;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_cal_cc_offset
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_CAL_CC;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge calibrate CC offset; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_cal_board_offset()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_CAL_BOARD;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_cal_board_offset
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_CAL_BOARD;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge calibrate board offset; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_cal_applied_voltage
    (string a_arg0)
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_CAL_APPLIED_VOLT;
        const double MIN_LIMIT = 15.0;
        const double MAX_LIMIT = 29.4;

        var a_volt = double.Parse(a_arg0, NumberStyles.Float);

        if(a_volt is < MIN_LIMIT or > MAX_LIMIT)
        {
            throw new ArgumentException($"Calibrate Voltage: voltage ({a_volt:F3}V) must be >= {MIN_LIMIT:F3}V and <= {MAX_LIMIT:F3}V");
        }

        var a_data = new byte[4];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le((ushort)(1000.0 * a_volt), a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_cal_applied_voltage
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_CAL_APPLIED_VOLT;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge applied voltage set; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_cal_voltage()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_CAL_VOLT;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_cal_voltage
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_CAL_VOLT;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge calibrate voltage; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_cal_applied_current
    (string a_arg0)
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_CAL_APPLIED_CURR;
        const double MIN_LIMIT = -10.0;
        const double MAX_LIMIT = -1.0;

        var a_curr = double.Parse(a_arg0, NumberStyles.Float);

        if(a_curr is < MIN_LIMIT or > MAX_LIMIT)
        {
            throw new ArgumentException($"Calibrate Current: current ({a_curr:F3}A) must be >= {MIN_LIMIT:F3}A and <= {MAX_LIMIT:F3}A");
        }

        var a_data = new byte[4];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le((short)(1000.0 * a_curr), a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_cal_applied_current
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_CAL_APPLIED_CURR;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge applied current set; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_cal_current()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_CAL_CURR;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_cal_current
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_CAL_CURR;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge calibrate current; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_serial_number_set
    (string a_arg0)
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_SERIAL_NUMBER;

        var a_sn = uint.Parse(a_arg0, NumberStyles.None);

        var a_data = new byte[6];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_sn, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_serial_number_set
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_SERIAL_NUMBER;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: desired serial number set; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_serial_number_store()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_SERIAL_NUMBER_STORE;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_serial_number_store
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_SERIAL_NUMBER_STORE;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: serial number store; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_blink
    (byte a_code)
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_BLINK_EN;

        var a_data = new byte[3];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_code, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_blink
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 3)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_BLINK_EN;

        Misc.decode_le(out byte a_state, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: LED Blink {(a_state is not 0 ? "Enabled" : "Disabled")}; ")
            .ToString();

        return a_result;
    }

    #endregion

    #region QUERIES

    private static (ushort a_cmd, byte[] a_data)
    process_query_coils()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_QUERY_COIL;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_query_discretes()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_QUERY_DISCRETE;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_query_holdings()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_QUERY_HOLDING;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_query_inputs()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_QUERY_INPUT;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    #endregion

    private static double
    to_celcius
    (ushort a_raw) => 0.1 * a_raw - 273.1;
}
