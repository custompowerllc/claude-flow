using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Globalization;
using contracts;
using utility.can;
using utility.misc;

namespace program_ns.processing.products;

using Translator = translators.GA_LiFePO4_Next_Modbus;

internal sealed class
GA_LiFePO4_Next : Product
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
        MESSAGE_13,
        MESSAGE_COMMAND_RESPONSE = 0xFFu
    };

    private enum
    Status_Register_ID:
    uint
    {
        COILS_A,
        COILS_B,
        FG_CONTROL_STATUS_HI,
        FG_CONTROL_STATUS_LO,
        FG_BATTERY_STATUS_HI,
        FG_BATTERY_STATUS_LO,
        FG_OPERATION_STATUS_HI,
        FG_OPERATION_STATUS_LO,
        FG_GAUGING_STATUS_HI,
        FG_GAUGING_STATUS_LO,
        FG_MANU_STATUS_HI,
        FG_MANU_STATUS_LO,
        AFE_SYS_STAT,
        AFE_CELLBAL1,
        AFE_CELLBAL2,
        AFE_CELLBAL3,
        AFE_SYS_CTRL1,
        AFE_SYS_CTRL2
    };

    private enum
    Query_ID:
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
        CHARGE_FET_OFF,
        CHARGE_FET_ON,
        DISCHARGE_FET_OFF,
        DISCHARGE_FET_ON,
        RESET_MICRO,
        FG_RESET,
        FG_LT_ENABLE,
        FG_SEAL,
        FG_UNSEAL_KEY,
        FG_UNSEAL,
        FG_FULL_UNSEAL_KEY,
        FG_FULL_UNSEAL,
        FG_PROGRAM,
        FG_CAL_CC_OFFSET,
        FG_CAL_BOARD_OFFSET,
        FG_CAL_APPLIED_VOLTAGE,
        FG_CAL_VOLTAGE,
        FG_CAL_APPLIED_CURRENT,
        FG_CAL_CURRENT,
        SERIAL_NUMBER_SET,
        SERIAL_NUMBER_STORE,
        REBALANCE_MODE_ENTER,
        REBALANCE_MODE_EXIT
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
        new() { id = (uint)Message_Register_ID.MESSAGE_13, display_text = "Message 13" },
        new() { id = (uint)Message_Register_ID.MESSAGE_COMMAND_RESPONSE, display_text = "Last Command Response" }
    };

    private static readonly HashSet<Status_Register> s_status_register_set =
    new()
    {
        new()
        {
            id = (uint)Status_Register_ID.COILS_A,
            display_text = "Coils A",
            bit7 = ("ENTER_BOOT", false),
            bit6 = ("STORE_SN", false),
            bit5 = ("CAL_CURR", false),
            bit4 = ("CAL_VOLT", false),
            bit3 = ("CAL_BOARD", false),
            bit2 = ("CAL_CC", false),
            bit1 = ("PROG_FG", false),
            bit0 = ("FG_LT_EN", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.COILS_B,
            display_text = "Coils B",
            bit7 = ("RSVD", true),
            bit6 = ("REBAL_MODE", false),
            bit5 = ("FG_FAS", false),
            bit4 = ("FG_SS", false),
            bit3 = ("FG_RESET", false),
            bit2 = ("μC_RESET", false),
            bit1 = ("DFET", false),
            bit0 = ("CFET", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_CONTROL_STATUS_HI,
            display_text = "Fuel Gauge Control Status Hi",
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
            id = (uint)Status_Register_ID.FG_CONTROL_STATUS_LO,
            display_text = "Fuel Gauge Control Status Lo",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("CCA", false),
            bit4 = ("BCA", false),
            bit3 = ("SNOOZE", false),
            bit2 = ("RSVD", true),
            bit1 = ("RSVD", true),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_BATTERY_STATUS_HI,
            display_text = "Fuel Battery Status Hi",
            bit7 = ("RSVD", true),
            bit6 = ("SOCLOW", false),
            bit5 = ("UTC", false),
            bit4 = ("UTD", false),
            bit3 = ("OTC", false),
            bit2 = ("OTD", false),
            bit1 = ("BATHIGH", false),
            bit0 = ("BATLOW", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_BATTERY_STATUS_LO,
            display_text = "Fuel Battery Status Lo",
            bit7 = ("SLEEP", false),
            bit6 = ("CHGINH", false),
            bit5 = ("FD", false),
            bit4 = ("FC", false),
            bit3 = ("TCA", false),
            bit2 = ("TDA", false),
            bit1 = ("CHG", false),
            bit0 = ("DSG", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_OPERATION_STATUS_HI,
            display_text = "Fuel Gauge Operation Status Hi",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("RSVD", true),
            bit2 = ("RSVD", true),
            bit1 = ("INITCOMP", false),
            bit0 = ("AUTH", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_OPERATION_STATUS_LO,
            display_text = "Fuel Gauge Operation Status Lo",
            bit7 = ("BLT", false),
            bit6 = ("SMTH", false),
            bit5 = ("ACTHR", false),
            bit4 = ("VDQ", false),
            bit3 = ("EDV2", false),
            bit2 = ("SEC1", false),
            bit1 = ("SEC0", false),
            bit0 = ("CALMD", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_GAUGING_STATUS_HI,
            display_text = "Fuel Gauge Gauging Status Hi",
            bit7 = ("VDQ", false),
            bit6 = ("EDV2", false),
            bit5 = ("EDV1", false),
            bit4 = ("RSVD", true),
            bit3 = ("RSVD", true),
            bit2 = ("FCCX", false),
            bit1 = ("RSVD", true),
            bit0 = ("REST", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_GAUGING_STATUS_LO,
            display_text = "Fuel Gauge Gauging Status Lo",
            bit7 = ("CF", false),
            bit6 = ("DSG", false),
            bit5 = ("EDV", false),
            bit4 = ("RSVD", true),
            bit3 = ("TC", false),
            bit2 = ("TD", false),
            bit1 = ("FC", false),
            bit0 = ("FD", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FG_MANU_STATUS_HI,
            display_text = "Fuel Gauge Manuf Status Hi",
            bit7 = ("CAL_EN", false),
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
            id = (uint)Status_Register_ID.FG_MANU_STATUS_LO,
            display_text = "Fuel Gauge Manuf Status Lo",
            bit7 = ("RSVD", true),
            bit6 = ("WHR_EN", false),
            bit5 = ("LF_EN", false),
            bit4 = ("PCTL_EN", false),
            bit3 = ("EOS_EN", false),
            bit2 = ("IGN_SD_EN", false),
            bit1 = ("ACCHG_EN", false),
            bit0 = ("ACDSG_EN", false)
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
            bit4 = ("C5 (CELL4)", false),
            bit3 = ("C4", true),
            bit2 = ("C3 (CELL3)", false),
            bit1 = ("C2 (CELL2)", false),
            bit0 = ("C1 (CELL1)", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_CELLBAL2,
            display_text = "AFE CELLBAL2",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("C10(CELL8)", false),
            bit3 = ("C9", true),
            bit2 = ("C8 (CELL7)", false),
            bit1 = ("C7 (CELL6)", false),
            bit0 = ("C6 (CELL5)", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.AFE_CELLBAL3,
            display_text = "AFE CELLBAL3",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("C15", true),
            bit3 = ("C14", true),
            bit2 = ("C13", true),
            bit1 = ("C12", true),
            bit0 = ("C11", true)
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
            id = (uint)Command_ID.CHARGE_FET_OFF,
            display_text = "Charge FET Off",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.CHARGE_FET_ON,
            display_text = "Charge FET On",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.DISCHARGE_FET_OFF,
            display_text = "Discharge FET Off",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.DISCHARGE_FET_ON,
            display_text = "Discharge FET On",
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
            id = (uint)Command_ID.FG_LT_ENABLE,
            display_text = "Fuel Gauge LT Enable",
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
            arguments = ImmutableArray.Create(("Key:", "15038901")),
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
            arguments = ImmutableArray.Create(("Key:", "1503ABCD")),
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_FULL_UNSEAL,
            display_text = "Unseal Fuel Gauge (full)",
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
            arguments = ImmutableArray.Create(("Applied Voltage (V):", "26.4")),
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
            arguments = ImmutableArray.Create(("Applied Current (A):", "-4.0")),
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
            id = (uint)Command_ID.REBALANCE_MODE_ENTER,
            display_text = "Enter Rebalance Mode",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.REBALANCE_MODE_EXIT,
            display_text = "Exit Rebalance Mode",
            response_timeout = 1000
        }
    };

    public
    GA_LiFePO4_Next
    (Config_Data a_config):
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
            0x13u => parse_message_13(a_data),
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
                Command_ID.CHARGE_FET_OFF => process_charge_fet(0x00),
                Command_ID.CHARGE_FET_ON => process_charge_fet(0x01),
                Command_ID.DISCHARGE_FET_OFF => process_discharge_fet(0x00),
                Command_ID.DISCHARGE_FET_ON => process_discharge_fet(0x01),
                Command_ID.RESET_MICRO => process_reset_micro(),
                Command_ID.FG_RESET => process_fg_reset(),
                Command_ID.FG_LT_ENABLE => process_fg_lt_enable(),
                Command_ID.FG_SEAL => process_fg_seal(),
                Command_ID.FG_UNSEAL_KEY => process_fg_unseal_key(a_args[0]),
                Command_ID.FG_UNSEAL => process_fg_unseal(),
                Command_ID.FG_FULL_UNSEAL_KEY => process_fg_full_unseal_key(a_args[0]),
                Command_ID.FG_FULL_UNSEAL => process_fg_full_unseal(),
                Command_ID.FG_PROGRAM => process_fg_program(),
                Command_ID.FG_CAL_CC_OFFSET => process_fg_cal_cc_offset(),
                Command_ID.FG_CAL_BOARD_OFFSET => process_fg_cal_board_offset(),
                Command_ID.FG_CAL_APPLIED_VOLTAGE => process_fg_cal_applied_voltage(a_args[0]),
                Command_ID.FG_CAL_VOLTAGE => process_fg_cal_voltage(),
                Command_ID.FG_CAL_APPLIED_CURRENT => process_fg_cal_applied_current(a_args[0]),
                Command_ID.FG_CAL_CURRENT => process_fg_cal_current(),
                Command_ID.SERIAL_NUMBER_SET => process_serial_number_set(a_args[0]),
                Command_ID.SERIAL_NUMBER_STORE => process_serial_number_store(),
                Command_ID.REBALANCE_MODE_ENTER => process_rebalance_mode(0x01),
                Command_ID.REBALANCE_MODE_EXIT => process_rebalance_mode(0x00),
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
            .Append($"AFE Curr: {0.002 * a_current:F3}A; ")
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

        Misc.decode_le(out ushort a_adc_gain, a_data, ref a_index);
        Misc.decode_le(out short a_adc_offset, a_data, ref a_index);
        Misc.decode_le(out ushort a_ov_limit, a_data, ref a_index);
        Misc.decode_le(out ushort a_uv_limit, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"AFE ADC Gain: {a_adc_gain}μV/LSB; ")
            .Append($"AFE ADC Offset: {a_adc_offset}mV; ")
            .Append($"AFE OV Limit: {0.001 * a_ov_limit:F3}V; ")
            .Append($"AFE UV Limit: {0.001 * a_uv_limit:F3}V; ")
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

        Misc.decode_le(out ushort a_fg_volt, a_data, ref a_index);
        Misc.decode_le(out short a_fg_curr, a_data, ref a_index);
        Misc.decode_le(out short a_fg_avg_curr, a_data, ref a_index);
        Misc.decode_le(out ushort a_state_of_charge, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"FG Volt: {0.001 * a_fg_volt:F3}V; ")
            .Append($"FG Curr: {0.002 * a_fg_curr:F3}A; ")
            .Append($"FG Avg Curr: {0.002 * a_fg_avg_curr:F3}A; ")
            .Append($"State of Charge: {a_state_of_charge}%; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_05
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
    parse_message_06
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
            .Append($"Full Charge Capacity: {2 * a_fcc}mAh; ")
            .Append($"Remaining Capacity: {2 * a_rc}mAh; ")
            .Append($"Design Capacity: {2 * a_dc}mAh; ")
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
    parse_message_08
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_soh, a_data, ref a_index);
        Misc.decode_le(out ushort a_cycle_count, a_data, ref a_index);
        Misc.decode_le(out ushort a_chg_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_chg_curr, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"State of Health: {a_soh}%; ")
            .Append($"Cycle Count: {a_cycle_count}; ")
            .Append($"Charging Volt: {0.001 * a_chg_volt:F3}V; ")
            .Append($"Charging Curr: {0.002 * a_chg_curr:F3}A; ")
            .ToString();

        return a_result;
    }

    private string?
    parse_message_09
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_sys_stat, a_data, ref a_index);
        Misc.decode_le(out byte a_cellbal1, a_data, ref a_index);
        Misc.decode_le(out byte a_cellbal2, a_data, ref a_index);
        Misc.decode_le(out byte a_cellbal3, a_data, ref a_index);
        Misc.decode_le(out byte a_sys_ctl1, a_data, ref a_index);
        Misc.decode_le(out byte a_sys_ctl2, a_data, ref a_index);
        Misc.decode_le(out byte a_ov_trip, a_data, ref a_index);
        Misc.decode_le(out byte a_uv_trip, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"sys_stat: 0x{a_sys_stat:X2}; ")
            .Append($"sys_ctl1: 0x{a_sys_ctl1:X2}; ")
            .Append($"sys_ctl2: 0x{a_sys_ctl2:X2}; ")
            .Append($"cellbal1: 0x{a_cellbal1:X2}; ")
            .Append($"cellbal2: 0x{a_cellbal2:X2}; ")
            .Append($"cellbal3: 0x{a_cellbal3:X2}; ")
            .Append($"ov_trip:  0x{a_ov_trip:X2}; ")
            .Append($"uv_trip:  0x{a_uv_trip:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_SYS_STAT], a_sys_stat);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_CELLBAL1], a_cellbal1);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_CELLBAL2], a_cellbal2);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_CELLBAL3], a_cellbal3);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_SYS_CTRL1], a_sys_ctl1);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.AFE_SYS_CTRL2], a_sys_ctl2);

        return a_result;
    }

    private string?
    parse_message_0A
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
        Misc.decode_le(out byte a_cc_cfg, a_data, ref a_index);
        Misc.decode_le(out byte a_uc_rev, a_data, ref a_index);
        Misc.decode_le(out byte a_fg_rev, a_data, ref a_index);
        Misc.decode_le(out ushort a_control_status, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"protect1: 0x{a_protect1:X2}; ")
            .Append($"protect2: 0x{a_protect2:X2}; ")
            .Append($"protect3: 0x{a_protect3:X2}; ")
            .Append($"cc_cfg:   0x{a_cc_cfg:X2}; ")
            .Append($"μC Rev:   {a_uc_rev}; ")
            .Append($"FG Rev:   {a_fg_rev}; ")
            .Append($"FG Control Status: 0x{a_control_status:X4}; ")
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

        return a_result;
    }

    private string?
    parse_message_0B
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_battery_status, a_data, ref a_index);
        Misc.decode_le(out ushort a_operation_status, a_data, ref a_index);
        Misc.decode_le(out ushort a_gauging_status, a_data, ref a_index);
        Misc.decode_le(out ushort a_manu_status, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"FG Batt Status: 0x{a_battery_status:X4}; ")
            .Append($"FG Oper Status: 0x{a_operation_status:X4}; ")
            .Append($"FG Gauging Status: 0x{a_gauging_status:X4}; ")
            .Append($"FG Man Status: 0x{a_manu_status:X4}; ")
            .ToString();

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_BATTERY_STATUS_HI],
            (byte)((a_battery_status & 0xFF00u) >> 8)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_BATTERY_STATUS_LO],
            (byte)((a_battery_status & 0x00FFu) >> 0)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_OPERATION_STATUS_HI],
            (byte)((a_operation_status & 0xFF00u) >> 8)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_OPERATION_STATUS_LO],
            (byte)((a_operation_status & 0x00FFu) >> 0)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_GAUGING_STATUS_HI],
            (byte)((a_gauging_status & 0xFF00u) >> 8)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_GAUGING_STATUS_LO],
            (byte)((a_gauging_status & 0x00FFu) >> 0)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_MANU_STATUS_HI],
            (byte)((a_manu_status & 0xFF00u) >> 8)
        );

        add_stat_register_parsed
        (
            status_register_map[(uint)Status_Register_ID.FG_MANU_STATUS_LO],
            (byte)((a_manu_status & 0x00FFu) >> 0)
        );

        return a_result;
    }

    private static string?
    parse_message_0C
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
    parse_message_0D
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
            .Append($"LT Max Chg Curr: {0.002 * a_lt_max_chg_curr:F3}A; ")
            .Append($"LT Max Dsg Curr: {0.002 * a_lt_min_dsg_curr:F3}A; ")
            .Append($"LT Max Volt: {0.001 * a_lt_max_volt:F3}V; ")
            .Append($"LT Min Volt: {0.001 * a_lt_min_volt:F3}V; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_0E
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_adc_pack_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_adc_vref, a_data, ref a_index);
        Misc.decode_le(out ushort a_micro_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_ts_temp, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"ADC Pack Volt: {0.001 * a_adc_pack_volt:F3}V; ")
            .Append($"ADC Vref: {0.001 * a_adc_vref:F3}V; ")
            .Append($"µController Temp: {to_celcius(a_micro_temp):F1}°C; ")
            .Append($"LM73 Temp: {to_celcius(a_ts_temp):F1}°C; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_0F
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
            .Append($"Serial Number: {a_serial:D10}; ")
            .ToString();

        return a_result;
    }

    private string?
    parse_message_10
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
    parse_message_11
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
    parse_message_12
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
    parse_message_13
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
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CHARGE_FET => parse_charge_fet(a_data, ref a_index),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_DISCHARGE_FET => parse_discharge_fet(a_data, ref a_index),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_RESET_MICRO => parse_reset_micro(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_RESET => parse_fg_reset(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_LT_EN => parse_fg_lt_enable(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_SEAL => parse_fg_seal(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_UNSEAL_KEY => parse_fg_unseal_key(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_UNSEAL => parse_fg_unseal(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_FULL_UNSEAL_KEY => parse_fg_full_unseal_key(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_FG_FULL_UNSEAL => parse_fg_full_unseal(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_PROG_FG => parse_fg_program(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CAL_CC => parse_fg_cal_cc_offset(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CAL_BOARD => parse_fg_cal_board_offset(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CAL_APPLIED_VOLT => parse_fg_cal_applied_voltage(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CAL_VOLT => parse_fg_cal_voltage(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CAL_APPLIED_CURR => parse_fg_cal_applied_current(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_CAL_CURR => parse_fg_cal_current(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_SERIAL_NUMBER => parse_serial_number_set(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_SERIAL_NUMBER_STORE => parse_serial_number_store(a_data),
                Translator.Command_Number.CMD_RESPONSE | Translator.Command_Number.CMD_REBALANCE_MODE => parse_rebalance_mode(a_data, ref a_index),
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
    process_charge_fet
    (byte a_code)
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_CHARGE_FET;

        var a_data = new byte[3];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_code, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_charge_fet
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 3)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_CHARGE_FET;

        Misc.decode_le(out byte a_state, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: charge FET {(a_state is not 0 ? "ON" : "OFF")}; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_discharge_fet
    (byte a_code)
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_DISCHARGE_FET;

        var a_data = new byte[3];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_code, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_discharge_fet
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 3)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_DISCHARGE_FET;

        Misc.decode_le(out byte a_state, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: discharge FET {(a_state is not 0 ? "ON" : "OFF")}; ")
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
    process_fg_lt_enable()
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_LT_EN;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_lt_enable
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_FG_LT_EN;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Fuel Gauge lifetime enable; ")
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
    process_rebalance_mode
    (byte a_code)
    {
        const ushort CMD = (ushort)Translator.Command_Number.CMD_REBALANCE_MODE;

        var a_data = new byte[3];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_code, a_data, ref a_index);

        return (CMD, a_data);
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
        const double MIN_LIMIT = 24.0;
        const double MAX_LIMIT = 28.4;

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

    private static string?
    parse_rebalance_mode
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 3)
        {
            return null;
        }

        const ushort CMD = (ushort)Translator.Command_Number.CMD_REBALANCE_MODE;

        Misc.decode_le(out byte a_state, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: rebalance Mode {(a_state is not 0 ? "ON" : "OFF")}; ")
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
