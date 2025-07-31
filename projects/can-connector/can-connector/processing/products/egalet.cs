using System;
using System.Collections.Generic;
using utility.can;
using utility.misc;

namespace program_ns.processing.products;

internal sealed class
Egalet : Product
{
    private enum
    Destination_ID : uint
    {

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
        MESSAGE_14,
        MESSAGE_15,
        MESSAGE_16,
        MESSAGE_17,
        MESSAGE_18,
        MESSAGE_19,
        MESSAGE_1A,
        MESSAGE_1B,
        MESSAGE_1C
    };

    private enum
    Status_Register_ID : uint
    {
        GLOBAL_OPERATION,
        VCELL_OPERATION,
        IPACK_OPERATION,
        CELL_SELECT_HI,
        CELL_SELECT_LO,
        FAULT_DELAY,
        LOAD_CHARGE_OPERATION,
        ETAUX_OPERATION,
        GPIO_ALERT_OPERATION,
        VREG_OPERATION,
        VBAT1_OPERATION,
        POWER_FET_OPERATION,
        CB_OPERATION,
        CB_CELL_STATE_HI,
        CB_CELL_STATE_LO,
        SCAN_OPERATION,
        PRIORITY_FAULTS,
        ETAUX_FAULTS,
        OTHER_FAULTS,
        CB_STATUS,
        STATUS,
        OPEN_WIRE_STATUS_HI,
        OPEN_WIRE_STATUS_LO,
        PRIORITY_FAULTS_MASK,
        ETAUX_FAULTS_MASK,
        OTHER_FAULTS_MASK,
        CB_STATUS_MASK,
        STATUS_MASK,
        OPEN_WIRE_MASK_HI,
        OPEN_WIRE_MASK_LO
    };

    private enum
    Query_ID : uint
    {
        
    };

    private enum
    Command_ID : uint
    {
        CHARGE_FET_OFF,
        CHARGE_FET_ON,
        DISCHARGE_FET_OFF,
        DISCHARGE_FET_ON
    };

    private static readonly HashSet<Destination> s_dest_set =
    new()
    {

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
        new() { id = (uint)Message_Register_ID.MESSAGE_14, display_text = "Message 14" },
        new() { id = (uint)Message_Register_ID.MESSAGE_15, display_text = "Message 15" },
        new() { id = (uint)Message_Register_ID.MESSAGE_16, display_text = "Message 16" },
        new() { id = (uint)Message_Register_ID.MESSAGE_17, display_text = "Message 17" },
        new() { id = (uint)Message_Register_ID.MESSAGE_18, display_text = "Message 18" },
        new() { id = (uint)Message_Register_ID.MESSAGE_19, display_text = "Message 19" },
        new() { id = (uint)Message_Register_ID.MESSAGE_1A, display_text = "Message 1A" },
        new() { id = (uint)Message_Register_ID.MESSAGE_1B, display_text = "Message 1B" },
        new() { id = (uint)Message_Register_ID.MESSAGE_1C, display_text = "Message 1C" }
    };

    private static readonly HashSet<Status_Register> s_status_register_set =
    new()
    {
        new()
        {
            id = (uint)Status_Register_ID.GLOBAL_OPERATION,
            display_text = "0x01: GLOBAL OPERATION",
            bit7 = ("SFT RST", false),
            bit6 = ("RST IDLE", false),
            bit5 = ("RCAL VOS TRIG", false),
            bit4 = ("RCAL LPM EN", false),
            bit3 = ("RCAL SCAN", false),
            bit2 = ("BUSY", false),
            bit1 = ("SYS SCAN SEL", false),
            bit0 = ("SYS SCAN TRIG", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.VCELL_OPERATION,
            display_text = "0x02: VCELL OPERATION",
            bit7 = ("VCELL EN", false),
            bit6 = ("DCHRW OV", false),
            bit5 = ("CHRW UV", false),
            bit4 = ("VCELL AVG", false),
            bit3 = ("VCELL AVG", false),
            bit2 = ("VCELL AVG", false),
            bit1 = ("CLEAR", false),
            bit0 = ("VCELL TRIG", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.IPACK_OPERATION,
            display_text = "0x03: IPACK OPERATION",
            bit7 = ("IPACK EN", false),
            bit6 = ("OW UPDATE", false),
            bit5 = ("OW PDATE", false),
            bit4 = ("IPACK AVG", false),
            bit3 = ("IPACK AVG", false),
            bit2 = ("IPACK AVG", false),
            bit1 = ("IDIR DELAY", false),
            bit0 = ("IPACK TRIG", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.CELL_SELECT_HI,
            display_text = "0x04: CELL SELECT",
            bit7 = ("CELL 16", false),
            bit6 = ("CELL 15", false),
            bit5 = ("CELL 14", false),
            bit4 = ("CELL 13", false),
            bit3 = ("CELL 12", false),
            bit2 = ("CELL 11", false),
            bit1 = ("CELL 10", false),
            bit0 = ("CELL 9", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.CELL_SELECT_LO,
            display_text = "0x05: CELL SELECT",
            bit7 = ("CELL 8", false),
            bit6 = ("CELL 7", false),
            bit5 = ("CELL 6", false),
            bit4 = ("CELL 5", false),
            bit3 = ("CELL 4", false),
            bit2 = ("CELL 3", false),
            bit1 = ("CELL 2", false),
            bit0 = ("CELL 1", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.FAULT_DELAY,
            display_text = "0x09: FAULT DELAY",
            bit7 = ("AUX PULLUP", false),
            bit6 = ("CV Δ FLT DEL", false),
            bit5 = ("OTHER FLT DEL", false),
            bit4 = ("ETAUX FLT DEL", false),
            bit3 = ("VCELL FLT DEL", false),
            bit2 = ("VCELL FLT DEL", false),
            bit1 = ("VCELL FLT DEL", false),
            bit0 = ("VCELL FLT DEL", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.LOAD_CHARGE_OPERATION,
            display_text = "0x0E: LOAD/CHARGE OPERATION",
            bit7 = ("CFD", false),
            bit6 = ("ELD", false),
            bit5 = ("ELD", false),
            bit4 = ("ELR", false),
            bit3 = ("CPWR", false),
            bit2 = ("FCDC", false),
            bit1 = ("LDLP", false),
            bit0 = ("RSV", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.ETAUX_OPERATION,
            display_text = "0x11: ETAUX OPERATION",
            bit7 = ("ETAUX EN", false),
            bit6 = ("ETAUX EN", false),
            bit5 = ("RSV", true),
            bit4 = ("ETAUX AVG", false),
            bit3 = ("ETAUX AVG", false),
            bit2 = ("ETAUX AVG", false),
            bit1 = ("RSV", true),
            bit0 = ("ETAUX TRIG", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.GPIO_ALERT_OPERATION,
            display_text = "0x12: GPIO/ALERT OPERATION",
            bit7 = ("ALRT ASSERT", false),
            bit6 = ("ALRT PULSE EN", false),
            bit5 = ("GPIO CONFIG", false),
            bit4 = ("GPIO CONFIG", false),
            bit3 = ("GPIO STATUS", false),
            bit2 = ("GPIO STATUS", false),
            bit1 = ("GPIO STATUS", false),
            bit0 = ("GPIO STATUS", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.VREG_OPERATION,
            display_text = "0x1B: VREG OPERATION",
            bit7 = ("COMMS TO", false),
            bit6 = ("COMMS TO", false),
            bit5 = ("UPD OTHER", false),
            bit4 = ("UPD OTHER", false),
            bit3 = ("LD DELAY", false),
            bit2 = ("LD DELAY", false),
            bit1 = ("LP REG", false),
            bit0 = ("VREG TRIG", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.VBAT1_OPERATION,
            display_text = "0x1F: VBAT1 OPERATION",
            bit7 = ("VBAT1 EN", false),
            bit6 = ("ITEMP EN", false),
            bit5 = ("ITEMP TRIG", false),
            bit4 = ("OTHER AVG", false),
            bit3 = ("OTHER EVG", false),
            bit2 = ("OTHER AVG", false),
            bit1 = ("COMMS TO EN", false),
            bit0 = ("VBAT1 TRIG", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.POWER_FET_OPERATION,
            display_text = "0x24: POWER FET OPERATION",
            bit7 = ("CPMP EN", false),
            bit6 = ("OW EN", false),
            bit5 = ("OW TRIG", false),
            bit4 = ("CELL CON", false),
            bit3 = ("VBAT1 CON", false),
            bit2 = ("ETAUX CON", false),
            bit1 = ("DFET EN", false),
            bit0 = ("CFET EN", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.CB_OPERATION,
            display_text = "0x25: CB OPERATION",
            bit7 = ("CB EN", false),
            bit6 = ("AUTO CB EN", false),
            bit5 = ("CB CONFIG", false),
            bit4 = ("CB TRIG", false),
            bit3 = ("IEOC EN", false),
            bit2 = ("CB MASK", false),
            bit1 = ("CB EOC", false),
            bit0 = ("CB CHRG", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.CB_CELL_STATE_HI,
            display_text = "0x26: CB CELL STATE",
            bit7 = ("CELL 16", false),
            bit6 = ("CELL 15", false),
            bit5 = ("CELL 14", false),
            bit4 = ("CELL 13", false),
            bit3 = ("CELL 12", false),
            bit2 = ("CELL 11", false),
            bit1 = ("CELL 10", false),
            bit0 = ("CELL 9", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.CB_CELL_STATE_LO,
            display_text = "0x27: CB CELL STATE",
            bit7 = ("CELL 8", false),
            bit6 = ("CELL 7", false),
            bit5 = ("CELL 6", false),
            bit4 = ("CELL 5", false),
            bit3 = ("CELL 4", false),
            bit2 = ("CELL 3", false),
            bit1 = ("CELL 2", false),
            bit0 = ("CELL 1", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.SCAN_OPERATION,
            display_text = "0x2E: SCAN OPERATION",
            bit7 = ("SYS MODE", false),
            bit6 = ("SYS MODE", false),
            bit5 = ("LP TIM", false),
            bit4 = ("LP TIM", false),
            bit3 = ("LP TIM", false),
            bit2 = ("SCAN DEL", false),
            bit1 = ("SCAN DEL", false),
            bit0 = ("SCAN DEL", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PRIORITY_FAULTS,
            display_text = "0x63: PRIORITY FAULTS",
            bit7 = ("VCCF", false),
            bit6 = ("OWF", false),
            bit5 = ("IOTF", false),
            bit4 = ("COCF", false),
            bit3 = ("DOCF", false),
            bit2 = ("DSCF", false),
            bit1 = ("UVF", false),
            bit0 = ("OVF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.ETAUX_FAULTS,
            display_text = "0x64: ETAUX FAULTS",
            bit7 = ("COT1", false),
            bit6 = ("CUT1", false),
            bit5 = ("DOT1", false),
            bit4 = ("DUT1", false),
            bit3 = ("COT0", false),
            bit2 = ("CUT0", false),
            bit1 = ("DOT0", false),
            bit0 = ("DUT0", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.OTHER_FAULTS,
            display_text = "0x65: OTHER FAULTS",
            bit7 = ("VBOVF", false),
            bit6 = ("VBUVF", false),
            bit5 = ("CPMP NRDY", false),
            bit4 = ("OW XT1", false),
            bit3 = ("OW XT0", false),
            bit2 = ("OW VBAT1", false),
            bit1 = ("OW VSS", false),
            bit0 = ("CRCF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.CB_STATUS,
            display_text = "0x66: CB STATUS",
            bit7 = ("BAT FULL", false),
            bit6 = ("IOTW", false),
            bit5 = ("IEOC", false),
            bit4 = ("VEOC", false),
            bit3 = ("DVCF", false),
            bit2 = ("2HI2CB", false),
            bit1 = ("2LO2CB", false),
            bit0 = ("NEED CB", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.STATUS,
            display_text = "0x67: STATUS",
            bit7 = ("DCHRGI", false),
            bit6 = ("CHRGI", false),
            bit5 = ("CH PRESI", false),
            bit4 = ("LD PRESI", false),
            bit3 = ("OTHER FAULTS", false),
            bit2 = ("IREG1", false),
            bit1 = ("IREG2", false),
            bit0 = ("VTMPF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.OPEN_WIRE_STATUS_HI,
            display_text = "0x68: OPEN WIRE STATUS",
            bit7 = ("CELL 16", false),
            bit6 = ("CELL 15", false),
            bit5 = ("CELL 14", false),
            bit4 = ("CELL 13", false),
            bit3 = ("CELL 12", false),
            bit2 = ("CELL 11", false),
            bit1 = ("CELL 10", false),
            bit0 = ("CELL 9", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.OPEN_WIRE_STATUS_LO,
            display_text = "0x69: OPEN WIRE STATUS",
            bit7 = ("CELL 8", false),
            bit6 = ("CELL 7", false),
            bit5 = ("CELL 6", false),
            bit4 = ("CELL 5", false),
            bit3 = ("CELL 4", false),
            bit2 = ("CELL 3", false),
            bit1 = ("CELL 2", false),
            bit0 = ("CELL 1", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PRIORITY_FAULTS_MASK,
            display_text = "0x83: PRIORITY FAULTS MASK",
            bit7 = ("VCCF", false),
            bit6 = ("OWF", false),
            bit5 = ("IOTF", false),
            bit4 = ("COCF", false),
            bit3 = ("DOCF", false),
            bit2 = ("DSCF", false),
            bit1 = ("UVF", false),
            bit0 = ("OVF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.ETAUX_FAULTS_MASK,
            display_text = "0x84: ETAUX FAULTS MASK",
            bit7 = ("COT1", false),
            bit6 = ("CUT1", false),
            bit5 = ("DOT1", false),
            bit4 = ("DUT1", false),
            bit3 = ("COT0", false),
            bit2 = ("CUT0", false),
            bit1 = ("DOT0", false),
            bit0 = ("DUT0", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.OTHER_FAULTS_MASK,
            display_text = "0x85: OTHER FAULTS MASK",
            bit7 = ("VBOVF", false),
            bit6 = ("VBUVF", false),
            bit5 = ("CPMP NRDY", false),
            bit4 = ("RSV", true),
            bit3 = ("RSV", true),
            bit2 = ("RSV", true),
            bit1 = ("RSV", true),
            bit0 = ("BUSY", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.CB_STATUS_MASK,
            display_text = "0x86: CB STATUS MASK",
            bit7 = ("BAT FULL", false),
            bit6 = ("IOTW", false),
            bit5 = ("IEOC", false),
            bit4 = ("VEOC", false),
            bit3 = ("DVCF", false),
            bit2 = ("2HI2CB", false),
            bit1 = ("2LO2CB", false),
            bit0 = ("NEED CB", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.STATUS_MASK,
            display_text = "0x87: STATUS MASK",
            bit7 = ("DCHRGI", false),
            bit6 = ("CHRGI", false),
            bit5 = ("CH PRESI", false),
            bit4 = ("LD PRESI", false),
            bit3 = ("OTHER FAULTS", false),
            bit2 = ("IREG1", false),
            bit1 = ("IREG2", false),
            bit0 = ("VTMPF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.OPEN_WIRE_MASK_HI,
            display_text = "0x88: OPEN WIRE MASK",
            bit7 = ("CELL 16", false),
            bit6 = ("CELL 15", false),
            bit5 = ("CELL 14", false),
            bit4 = ("CELL 13", false),
            bit3 = ("CELL 12", false),
            bit2 = ("CELL 11", false),
            bit1 = ("CELL 10", false),
            bit0 = ("CELL 9", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.OPEN_WIRE_MASK_LO,
            display_text = "0x89: OPEN WIRE MASK",
            bit7 = ("CELL 8", false),
            bit6 = ("CELL 7", false),
            bit5 = ("CELL 6", false),
            bit4 = ("CELL 5", false),
            bit3 = ("CELL 4", false),
            bit2 = ("CELL 3", false),
            bit1 = ("CELL 2", false),
            bit0 = ("CELL 1", false)
        }
    };

    private static readonly HashSet<Query> s_query_set =
    new()
    {

    };

    private static readonly HashSet<Command> s_command_set =
    new()
    {
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
            id = (uint)Command_ID.DISCHARGE_FET_OFF,
            display_text = "Discharge FET Off",
            response_timeout = null
        },
        new()
        {
            id = (uint)Command_ID.DISCHARGE_FET_ON,
            display_text = "Discharge FET On",
            response_timeout = null
        }
    };

    public
    Egalet():
    base()
    {

    }

    public override IReadOnlySet<Destination> destination_set => s_dest_set;
    public override IReadOnlySet<Message_Register> message_register_set => s_message_register_set;
    public override IReadOnlySet<Status_Register> status_register_set => s_status_register_set;
    public override IReadOnlySet<Query> query_set => s_query_set;
    public override IReadOnlySet<Command> command_set => s_command_set;
    public override Destination? default_destination => null;
    public override Query? default_query => null;
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
            0x14u => parse_message_14(a_data),
            0x15u => parse_message_15(a_data),
            0x16u => parse_message_16(a_data),
            0x17u => parse_message_17(a_data),
            0x18u => parse_message_18(a_data),
            0x19u => parse_message_19(a_data),
            0x1Au => parse_message_1A(a_data),
            0x1Bu => parse_message_1B(a_data),
            0x1Cu => parse_message_1C(a_data),
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
                Command_ID.CHARGE_FET_OFF    => process_charge_fet_off_on(0x00),
                Command_ID.CHARGE_FET_ON     => process_charge_fet_off_on(0x01),
                Command_ID.DISCHARGE_FET_OFF => process_discharge_fet_off_on(0x00),
                Command_ID.DISCHARGE_FET_ON  => process_discharge_fet_off_on(0x01),
                _ => throw new ArgumentOutOfRangeException(nameof(a_command))
            };

        add_command(a_command, a_cmd, a_data);
    }

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
            .Append($"V01={0.001 * a_v1:F3}; ")
            .Append($"V02={0.001 * a_v2:F3}; ")
            .Append($"V03={0.001 * a_v3:F3}; ")
            .Append($"V04={0.001 * a_v4:F3}; ")
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
            .Append($"V05={0.001 * a_v1:F3}; ")
            .Append($"V06={0.001 * a_v2:F3}; ")
            .Append($"V07={0.001 * a_v3:F3}; ")
            .Append($"V08={0.001 * a_v4:F3}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_02
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
            .Append($"V09={0.001 * a_v1:F3}; ")
            .Append($"V10={0.001 * a_v2:F3}; ")
            .Append($"V11={0.001 * a_v3:F3}; ")
            .Append($"V12={0.001 * a_v4:F3}; ")
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
            .Append($"V16={0.001 * a_v4:F3}; ")
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

        Misc.decode_le(out ushort a_volt, a_data, ref a_index);
        Misc.decode_le(out short a_curr, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp0, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp1, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"Volt: {0.001 * a_volt:F3}V; ")
            .Append($"Curr: {0.004 * a_curr:F3}A; ")
            .Append($"Temp 0: {to_celcius(a_temp0):F1}°C; ")
            .Append($"Temp 1: {to_celcius(a_temp1):F1}°C; ")
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

        Misc.decode_le(out ulong a_sent_count, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"Counter: {a_sent_count}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_06
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_volt_delta, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_internal, a_data, ref a_index);
        Misc.decode_le(out ushort a_vtemp_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_vcc_volt, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"Cell Volt Δ: {0.001 * a_volt_delta:F3}V; ")
            .Append($"AFE Temp Internal: {to_celcius(a_temp_internal):F1}°C; ")
            .Append($"Vtemp Volt: {0.001 * a_vtemp_volt:F3}V; ")
            .Append($"VCC Volt: {0.001 * a_vcc_volt:F3}V; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_07
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_regulator_curr, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"AFE Regulator Curr: {0.001 * a_regulator_curr:F3}A; ")
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

        Misc.decode_le(out ushort a_adc_pack_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_adc_temp_sense, a_data, ref a_index);
        Misc.decode_le(out ushort a_adc_vref_internal, a_data, ref a_index);
        Misc.decode_le(out ushort a_adc_temp_internal, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"ADC Pack Volt: {0.001 * a_adc_pack_volt:F3}V; ")
            .Append($"ADC Temp Sense: {to_celcius(a_adc_temp_sense):F1}°C; ")
            .Append($"ADC Vref: {0.001 * a_adc_vref_internal:F3}V; ")
            .Append($"Temp μController: {to_celcius(a_adc_temp_internal):F1}°C; ")
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

        Misc.decode_le(out byte a_r1, a_data, ref a_index);
        Misc.decode_le(out byte a_r2, a_data, ref a_index);
        Misc.decode_le(out byte a_r3, a_data, ref a_index);
        Misc.decode_le(out byte a_r4, a_data, ref a_index);
        Misc.decode_le(out ushort a_r5, a_data, ref a_index);
        Misc.decode_le(out byte a_r6, a_data, ref a_index);
        Misc.decode_le(out byte a_r7, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"0x00: 0x{a_r1:X2}; ")
            .Append($"0x01: 0x{a_r2:X2}; ")
            .Append($"0x02: 0x{a_r3:X2}; ")
            .Append($"0x03: 0x{a_r4:X2}; ")
            .Append($"0x04: 0x{unchecked((byte)(a_r5 >> 8)):X2}; ")
            .Append($"0x05: 0x{unchecked((byte)(a_r5 >> 0)):X2}; ")
            .Append($"0x06: 0x{a_r6:X2}; ")
            .Append($"0x07: 0x{a_r7:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.GLOBAL_OPERATION], a_r2);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.VCELL_OPERATION], a_r3);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.IPACK_OPERATION], a_r4);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.CELL_SELECT_HI], unchecked((byte)(a_r5 >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.CELL_SELECT_LO], unchecked((byte)(a_r5 >> 0)));

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

        Misc.decode_le(out byte a_r1, a_data, ref a_index);
        Misc.decode_le(out byte a_r2, a_data, ref a_index);
        Misc.decode_le(out byte a_r3, a_data, ref a_index);
        Misc.decode_le(out byte a_r4, a_data, ref a_index);
        Misc.decode_le(out byte a_r5, a_data, ref a_index);
        Misc.decode_le(out byte a_r6, a_data, ref a_index);
        Misc.decode_le(out byte a_r7, a_data, ref a_index);
        Misc.decode_le(out byte a_r8, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"0x08: 0x{a_r1:X2}; ")
            .Append($"0x09: 0x{a_r2:X2}; ")
            .Append($"0x0A: 0x{a_r3:X2}; ")
            .Append($"0x0B: 0x{a_r4:X2}; ")
            .Append($"0x0C: 0x{a_r5:X2}; ")
            .Append($"0x0D: 0x{a_r6:X2}; ")
            .Append($"0x0E: 0x{a_r7:X2}; ")
            .Append($"0x0F: 0x{a_r8:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FAULT_DELAY], a_r2);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.LOAD_CHARGE_OPERATION], a_r7);

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

        Misc.decode_le(out byte a_r1, a_data, ref a_index);
        Misc.decode_le(out byte a_r2, a_data, ref a_index);
        Misc.decode_le(out byte a_r3, a_data, ref a_index);
        Misc.decode_le(out byte a_r4, a_data, ref a_index);
        Misc.decode_le(out byte a_r5, a_data, ref a_index);
        Misc.decode_le(out byte a_r6, a_data, ref a_index);
        Misc.decode_le(out byte a_r7, a_data, ref a_index);
        Misc.decode_le(out byte a_r8, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"0x10: 0x{a_r1:X2}; ")
            .Append($"0x11: 0x{a_r2:X2}; ")
            .Append($"0x12: 0x{a_r3:X2}; ")
            .Append($"0x13: 0x{a_r4:X2}; ")
            .Append($"0x14: 0x{a_r5:X2}; ")
            .Append($"0x15: 0x{a_r6:X2}; ")
            .Append($"0x16: 0x{a_r7:X2}; ")
            .Append($"0x17: 0x{a_r8:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.ETAUX_OPERATION], a_r2);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.GPIO_ALERT_OPERATION], a_r3);

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

        Misc.decode_le(out byte a_r1, a_data, ref a_index);
        Misc.decode_le(out byte a_r2, a_data, ref a_index);
        Misc.decode_le(out byte a_r3, a_data, ref a_index);
        Misc.decode_le(out byte a_r4, a_data, ref a_index);
        Misc.decode_le(out byte a_r5, a_data, ref a_index);
        Misc.decode_le(out byte a_r6, a_data, ref a_index);
        Misc.decode_le(out byte a_r7, a_data, ref a_index);
        Misc.decode_le(out byte a_r8, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"0x18: 0x{a_r1:X2}; ")
            .Append($"0x19: 0x{a_r2:X2}; ")
            .Append($"0x1A: 0x{a_r3:X2}; ")
            .Append($"0x1B: 0x{a_r4:X2}; ")
            .Append($"0x1C: 0x{a_r5:X2}; ")
            .Append($"0x1D: 0x{a_r6:X2}; ")
            .Append($"0x1E: 0x{a_r7:X2}; ")
            .Append($"0x1F: 0x{a_r8:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.VREG_OPERATION], a_r4);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.VBAT1_OPERATION], a_r8);

        return a_result;
    }

    private string?
    parse_message_0D
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_r1, a_data, ref a_index);
        Misc.decode_le(out byte a_r2, a_data, ref a_index);
        Misc.decode_le(out byte a_r3, a_data, ref a_index);
        Misc.decode_le(out byte a_r4, a_data, ref a_index);
        Misc.decode_le(out byte a_r5, a_data, ref a_index);
        Misc.decode_le(out byte a_r6, a_data, ref a_index);
        Misc.decode_le(out ushort a_r7, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"0x20: 0x{a_r1:X2}; ")
            .Append($"0x21: 0x{a_r2:X2}; ")
            .Append($"0x22: 0x{a_r3:X2}; ")
            .Append($"0x23: 0x{a_r4:X2}; ")
            .Append($"0x24: 0x{a_r5:X2}; ")
            .Append($"0x25: 0x{a_r6:X2}; ")
            .Append($"0x26: 0x{unchecked((byte)(a_r7 >> 8)):X2}; ")
            .Append($"0x27: 0x{unchecked((byte)(a_r7 >> 0)):X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.POWER_FET_OPERATION], a_r5);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.CB_OPERATION], a_r6);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.CB_CELL_STATE_HI], unchecked((byte)(a_r7 >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.CB_CELL_STATE_LO], unchecked((byte)(a_r7 >> 0)));

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

        Misc.decode_le(out byte a_r1, a_data, ref a_index);
        Misc.decode_le(out byte a_r2, a_data, ref a_index);
        Misc.decode_le(out byte a_r3, a_data, ref a_index);
        Misc.decode_le(out byte a_r4, a_data, ref a_index);
        Misc.decode_le(out byte a_r5, a_data, ref a_index);
        Misc.decode_le(out byte a_r6, a_data, ref a_index);
        Misc.decode_le(out byte a_r7, a_data, ref a_index);
        Misc.decode_le(out byte a_r8, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"0x28: 0x{a_r1:X2}; ")
            .Append($"0x29: 0x{a_r2:X2}; ")
            .Append($"0x2A: 0x{a_r3:X2}; ")
            .Append($"0x2B: 0x{a_r4:X2}; ")
            .Append($"0x2C: 0x{a_r5:X2}; ")
            .Append($"0x2D: 0x{a_r6:X2}; ")
            .Append($"0x2E: 0x{a_r7:X2}; ")
            .Append($"0x63: 0x{a_r8:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.SCAN_OPERATION], a_r7);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PRIORITY_FAULTS], a_r8);

        return a_result;
    }

    private string?
    parse_message_0F
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_r1, a_data, ref a_index);
        Misc.decode_le(out byte a_r2, a_data, ref a_index);
        Misc.decode_le(out byte a_r3, a_data, ref a_index);
        Misc.decode_le(out byte a_r4, a_data, ref a_index);
        Misc.decode_le(out ushort a_r5, a_data, ref a_index);
        Misc.decode_le(out byte a_r6, a_data, ref a_index);
        Misc.decode_le(out byte a_r7, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"0x64: 0x{a_r1:X2}; ")
            .Append($"0x65: 0x{a_r2:X2}; ")
            .Append($"0x66: 0x{a_r3:X2}; ")
            .Append($"0x67: 0x{a_r4:X2}; ")
            .Append($"0x68: 0x{unchecked((byte)(a_r5 >> 8)):X2}; ")
            .Append($"0x69: 0x{unchecked((byte)(a_r5 >> 0)):X2}; ")
            .Append($"0x83: 0x{a_r6:X2}; ")
            .Append($"0x84: 0x{a_r7:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.ETAUX_FAULTS], a_r1);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.OTHER_FAULTS], a_r2);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.CB_STATUS], a_r3);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.STATUS], a_r4);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.OPEN_WIRE_STATUS_HI], unchecked((byte)(a_r5 >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.OPEN_WIRE_STATUS_LO], unchecked((byte)(a_r5 >> 0)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PRIORITY_FAULTS_MASK], a_r6);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.ETAUX_FAULTS_MASK], a_r7);

        return a_result;
    }

    private string?
    parse_message_10
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 5)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_r1, a_data, ref a_index);
        Misc.decode_le(out byte a_r2, a_data, ref a_index);
        Misc.decode_le(out ushort a_r3, a_data, ref a_index);
        Misc.decode_le(out byte a_r4, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"0x85: 0x{a_r1:X2}; ")
            .Append($"0x86: 0x{a_r2:X2}; ")
            .Append($"0x87: 0x{a_r4:X2}; ")
            .Append($"0x88: 0x{unchecked((byte)(a_r3 >> 8)):X2}; ")
            .Append($"0x89: 0x{unchecked((byte)(a_r3 >> 0)):X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.OTHER_FAULTS_MASK], a_r1);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.CB_STATUS_MASK], a_r2);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.OPEN_WIRE_MASK_HI], unchecked((byte)(a_r3 >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.OPEN_WIRE_MASK_LO], unchecked((byte)(a_r3 >> 0)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.STATUS_MASK], a_r4);

        return a_result;
    }

    private static string?
    parse_message_11
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_cell_ov_thresh, a_data, ref a_index);
        Misc.decode_le(out ushort a_cell_uv_thresh, a_data, ref a_index);
        Misc.decode_le(out ushort a_cell_max_delta_thresh, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"Cell OV Thresh: {0.001 * a_cell_ov_thresh:F3}V; ")
            .Append($"Cell UV Thresh: {0.001 * a_cell_uv_thresh:F3}V; ")
            .Append($"Cell Max Δ Thresh: {0.001 * a_cell_max_delta_thresh:F3}V; ")
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

        Misc.decode_le(out uint a_dsc_thresh, a_data, ref a_index);
        Misc.decode_le(out uint a_doc_thresh, a_data, ref a_index);

        var a_dsc = 
            a_dsc_thresh is uint.MaxValue ? double.PositiveInfinity : 0.001 * a_dsc_thresh;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"DSC Thresh: {a_dsc:F3}A; ")
            .Append($"DOC Thresh: {0.001 * a_doc_thresh:F3}A; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_13
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_coc_thresh, a_data, ref a_index);
        Misc.decode_le(out ushort a_dsc_delay, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"COC Thresh: {0.001 * a_coc_thresh:F3}A; ")
            .Append($"DSC Delay: {a_dsc_delay}μs; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_14
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_dut0, a_data, ref a_index);
        Misc.decode_le(out ushort a_dot0, a_data, ref a_index);
        Misc.decode_le(out ushort a_cut0, a_data, ref a_index);
        Misc.decode_le(out ushort a_cot0, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"DUT0 Limit: {to_celcius(a_dut0):F1}°C; ")
            .Append($"DOT0 Limit: {to_celcius(a_dot0):F1}°C; ")
            .Append($"CUT0 Limit: {to_celcius(a_cut0):F1}°C; ")
            .Append($"COT0 Limit: {to_celcius(a_cot0):F1}°C; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_15
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_dut1, a_data, ref a_index);
        Misc.decode_le(out ushort a_dot1, a_data, ref a_index);
        Misc.decode_le(out ushort a_cut1, a_data, ref a_index);
        Misc.decode_le(out ushort a_cot1, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"DUT1 Limit: {to_celcius(a_dut1):F1}°C; ")
            .Append($"DOT1 Limit: {to_celcius(a_dot1):F1}°C; ")
            .Append($"CUT1 Limit: {to_celcius(a_cut1):F1}°C; ")
            .Append($"COT1 Limit: {to_celcius(a_cot1):F1}°C; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_16
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_iotw, a_data, ref a_index);
        Misc.decode_le(out ushort a_iotf, a_data, ref a_index);
        Misc.decode_le(out ushort a_vcc_min_thresh, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"IOTW Thresh: {to_celcius(a_iotw):F1}°C; ")
            .Append($"IOTF Thresh: {to_celcius(a_iotf):F1}°C; ")
            .Append($"VCC Min Thresh: {0.001 * a_vcc_min_thresh:F3}V; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_17
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_regulator_oc1, a_data, ref a_index);
        Misc.decode_le(out uint a_regulator_oc2, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"Regulator OC 1 Thresh: {0.001 * a_regulator_oc1:F3}A; ")
            .Append($"Regulator OC 2 Thresh: {0.001 * a_regulator_oc2:F3}A; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_18
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_batt_ov_thresh, a_data, ref a_index);
        Misc.decode_le(out uint a_batt_uv_thresh, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"Batt OV Thresh: {0.001 * a_batt_ov_thresh:F3}V; ")
            .Append($"Batt UV Thresh: {0.001 * a_batt_uv_thresh:F3}V; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_19
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_cb_on_time, a_data, ref a_index);
        Misc.decode_le(out uint a_cb_off_time, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"CB On Time: {a_cb_on_time}ms; ")
            .Append($"CB Off Time: {a_cb_off_time}ms; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_1A
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_cb_min_delta_thresh, a_data, ref a_index);
        Misc.decode_le(out ushort a_cb_max_volt_thresh, a_data, ref a_index);
        Misc.decode_le(out ushort a_cb_min_volt_thresh, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"CB Min Δ Thresh: {0.001 * a_cb_min_delta_thresh:F3}V; ")
            .Append($"CB Max Volt Thresh: {0.001 * a_cb_max_volt_thresh:F3}V; ")
            .Append($"CB Min Volt Thresh: {0.001 * a_cb_min_volt_thresh:F3}V; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_1B
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_eoc_curr_thresh, a_data, ref a_index);
        Misc.decode_le(out ushort a_eoc_volt_thresh, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"EOC Curr Thresh: {0.001 * a_eoc_curr_thresh:F3}A; ")
            .Append($"EOC Volt Thresh: {0.001 * a_eoc_volt_thresh:F3}V; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_1C
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ulong a_crc_error_count, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result = 
            a_g1.value
            .Append($"AFE SPI CRC Error Count: {a_crc_error_count}; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_charge_fet_off_on
    (byte a_code)
    {
        const ushort CMD = 0x0000;

        var a_data = new byte[3];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_code, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static (ushort a_cmd, byte[] a_data)
    process_discharge_fet_off_on
    (byte a_code)
    {
        const ushort CMD = 0x0001;

        var a_data = new byte[3];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_code, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static double
    to_celcius
    (ushort a_raw) => 0.1 * a_raw - 273.1;
}
