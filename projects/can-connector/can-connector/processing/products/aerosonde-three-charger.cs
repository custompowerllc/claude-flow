using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Formats.Asn1;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using utility.can;
using utility.misc;

namespace program_ns.processing.products;

internal sealed class
Aerosonde_Three_Charger : Product
{
    static long curTimeStamp;
    static long logTimeStamp;
    static int[] instrumentData = new int[32];
    StreamWriter writer;
    static int instrumentDataCounter = 0xFF;
    static string instrumentFormat = "{0,8}, {1,8}, {2,8}, {3,8}, {4,8}, {5,8}, {6,8}, {7,8}, {8,8}, {9,8}, {10,8}, {11,8}, {12,8}, {13,8}, {14,8}, {15,8}, {16}, {17}, {18}, {19}";

    protected void InitInstrumentData()
    {
        curTimeStamp = 0;
        logTimeStamp = 0;
        instrumentDataCounter = 0;
        writer = new StreamWriter("output.csv");
        string outputline = "P1-State, P2-State, P3-State, P4-State, P1-Volt, P2-Volt, P3-Volt, P4-Volt, P1-Curr, P2-Curr, P3-Curr, P4-Curr, P1-SOC, P2-SOC, P3-SOC, P4-SOC, P1-DisT, P2-DisT, P3-DisT, P4-DisT";
        writer.WriteLine(outputline);
    }

    protected void CloseInstrumentData()
    {
        writer.Close();
        instrumentDataCounter = 0xFFFF;
    }
    protected void CheckInstrumentData()
    {
        if (instrumentDataCounter == 0xFFFF)
        {
            return;
        }
        if (logTimeStamp == curTimeStamp)
        {
            return;
        }
        long diff = curTimeStamp - logTimeStamp;
        logTimeStamp = curTimeStamp;
        if (instrumentDataCounter >= 10)
            instrumentDataCounter = 0;
        instrumentDataCounter += (int) diff;
        if (instrumentDataCounter >= 10)
        {
            string outputline = String.Format(instrumentFormat, instrumentData[0], instrumentData[1], instrumentData[2], instrumentData[3],
                instrumentData[6], instrumentData[7], instrumentData[4], instrumentData[5],
                instrumentData[8], instrumentData[9], instrumentData[10], instrumentData[11],
                instrumentData[12], instrumentData[13], instrumentData[14], instrumentData[15],
                to_celcius((ushort)instrumentData[16]), to_celcius((ushort)instrumentData[17]), to_celcius((ushort)instrumentData[18]), to_celcius((ushort)instrumentData[19]));
            writer.WriteLine(outputline);
        }
    }

    enum
    Charger_State : byte
    {
        INITIALIZING,
        PS_SETUP,
        IDLE,
        BUSY,
        EMERGENCY,
        BOOTLOADER,
        INVALID
    };

    enum
    NVM_Lock_Owner : byte
    {
        NONE,
        CHANNEL_1,
        CHANNEL_2,
        CHANNEL_3,
        CHANNEL_4,
        GUI,
        CHARGER,
        INVALID
    };

    enum
    Pack_State : byte
    {
        DISCONNECTED,
        CONNECTED,
        CHARGE_ONGOING,
        CHARGE_PAUSED,
        CHARGE_COMPLETE,
        DISCHG_ONGOING,
        DISCHG_PAUSED,
        DISCHG_COMPLETE,
        INVALID
    };

    private enum
    Destination_ID : uint
    {

    }

    private enum
    Message_Register_ID : uint
    {
        CMD_ENTER_BOOTLOADER,
        CMD_SET_SERIAL_S,
        CMD_SET_SERIAL_R,
        CMD_CALIBRATE_ADC_OFFSETS_S,
        CMD_CALIBRATE_ADC_OFFSETS_R,
        CMD_CALIBRATE_ADC_VOLT_S,
        CMD_CALIBRATE_ADC_VOLT_R,
        CMD_CALIBRATE_ADC_CURR_S,
        CMD_CALIBRATE_ADC_CURR_R,
        CMD_CHARGE_CURR_INCREMENT,
        CMD_CHARGE_TARGET_SOC_INCREMENT,
        CMD_CHARGE_SETTINGS_CANCEL,
        CMD_CHARGE_SETTINGS_STORE_S,
        CMD_CHARGE_SETTINGS_STORE_R,
        CMD_DISCHG_TARGET_SOC_INCREMENT,
        CMD_DISCHG_SETTINGS_CANCEL,
        CMD_DISCHG_SETTINGS_STORE_S,
        CMD_DISCHG_SETTINGS_STORE_R,
        CMD_BRIGHTNESS_MODE_INCREMENT,
        CMD_BRIGHTNESS_MIN_INCREMENT,
        CMD_BRIGHTNESS_MAX_INCREMENT,
        CMD_BRIGHTNESS_SETTINGS_STORE_S,
        CMD_BRIGHTNESS_SETTINGS_STORE_R,
        CMD_STANDARD_CHARGE_S,
        CMD_STANDARD_CHARGE_R,
        CMD_STANDARD_DISCHG_S,
        CMD_STANDARD_DISCHG_R,
        CMD_CUSTOM_CHARGE_S,
        CMD_CUSTOM_CHARGE_R,
        CMD_CUSTOM_DISCHG_S,
        CMD_CUSTOM_DISCHG_R,
        CMD_CANCEL_OPERATION_S,
        CMD_CANCEL_OPERATION_R,
        CMD_CANCEL_OPERATION_ALL_S,
        CMD_CANCEL_OPERATION_ALL_R,
        CMD_FACTORY_DEFAULTS_S,
        CMD_FACTORY_DEFAULTS_R,
        GUI_CHARGER_STATE = 64,
        GUI_PACK_VOLT_A,
        GUI_PACK_VOLT_B,
        GUI_PACK_CURR,
        GUI_PACK_TEMP,
        GUI_PACK_SOC,
        GUI_ADC_VOLT_A,
        GUI_ADC_VOLT_B,
        GUI_ADC_CURR,
        GUI_PS_CHARGE_STATUS,
        GUI_PS_SYSTEM_STATUS,
        GUI_PS_AC_VOLT_A,
        GUI_PS_AC_VOLT_B,
        GUI_PS_VOLT_A,
        GUI_PS_VOLT_B,
        GUI_PS_CURR,
        GUI_PS_TEMP,
        GUI_PS_CHARGE_VOLT_A,
        GUI_PS_CHARGE_VOLT_B,
        GUI_PS_CHARGE_CURR,
        GUI_PS_FLOAT_VOLT_A,
        GUI_PS_FLOAT_VOLT_B,
        GUI_PS_TAPER_CURR,
        GUI_RESISTOR_TEMP,
        GUI_BOARD_TEMP,
        GUI_SYS_INFO,
        GUI_TIME_STAMP,
        GUI_DISPLAY_ADC,
        BROADCAST_CHARGER_STATE = 192,
        BROADCAST_PACK_VOLT_A,
        BROADCAST_PACK_VOLT_B,
        BROADCAST_PACK_CURR,
        BROADCAST_PACK_TEMP,
        BROADCAST_PACK_SOC,
        BROADCAST_PS_CHARGE_STATUS,
        BROADCAST_CHARGE_CURR_SETTING,
        BROADCAST_CHARGE_DISCHG_TARGET_SOC_SETTING,
        BROADCAST_BRIGHTNESS_SETTINGS,
        BROADCAST_CHARGE_CURR_SETTING_NVM,
        BROADCAST_CHARGE_DISCHG_TARGET_SOC_SETTING_NVM,
        BROADCAST_BRIGHTNESS_SETTINGS_NVM,
        BROADCAST_SYS_INFO,
        BROADCAST_TIME_STAMP = 255,
        INVALID,
        DISPLAY1_ADC,
        DISPLAY2_ADC
    };

    private enum
    Status_Register_ID : uint
    {
        PS1_CHARGE_STATUS_HI,
        PS1_CHARGE_STATUS_LO,
        PS1_FAULT_STATUS,
        PS1_SYSTEM_STATUS,
        PS2_CHARGE_STATUS_HI,
        PS2_CHARGE_STATUS_LO,
        PS2_FAULT_STATUS,
        PS2_SYSTEM_STATUS,
        PS3_CHARGE_STATUS_HI,
        PS3_CHARGE_STATUS_LO,
        PS3_FAULT_STATUS,
        PS3_SYSTEM_STATUS,
        PS4_CHARGE_STATUS_HI,
        PS4_CHARGE_STATUS_LO,
        PS4_FAULT_STATUS,
        PS4_SYSTEM_STATUS
    };

    private enum
    Query_ID : uint
    {

    };

    private enum
    Command_ID : uint
    {
        ENTER_BOOTLOADER,
        SET_SERIAL_NUMBER,
        CALIBRATE_ADC_OFFSETS,
        CALIBRATE_VOLT,
        CALIBRATE_CURR
    };

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

    };

    private static readonly HashSet<Message_Register> s_message_register_set =
    new()
    {
        new() { id = (uint)Message_Register_ID.GUI_CHARGER_STATE,    display_text = "Message 00" },
        new() { id = (uint)Message_Register_ID.GUI_PACK_VOLT_A,      display_text = "Message 01" },
        new() { id = (uint)Message_Register_ID.GUI_PACK_VOLT_B,      display_text = "Message 02" },
        new() { id = (uint)Message_Register_ID.GUI_PACK_CURR,        display_text = "Message 03" },
        new() { id = (uint)Message_Register_ID.GUI_PACK_TEMP,        display_text = "Message 04" },
        new() { id = (uint)Message_Register_ID.GUI_PACK_SOC,         display_text = "Message 05" },
        new() { id = (uint)Message_Register_ID.GUI_ADC_VOLT_A,       display_text = "Message 06" },
        new() { id = (uint)Message_Register_ID.GUI_ADC_VOLT_B,       display_text = "Message 07" },
        new() { id = (uint)Message_Register_ID.GUI_ADC_CURR,         display_text = "Message 08" },
        new() { id = (uint)Message_Register_ID.GUI_PS_CHARGE_STATUS, display_text = "Message 09" },
        new() { id = (uint)Message_Register_ID.GUI_PS_SYSTEM_STATUS, display_text = "Message 0A" },
        new() { id = (uint)Message_Register_ID.GUI_PS_AC_VOLT_A,     display_text = "Message 0B" },
        new() { id = (uint)Message_Register_ID.GUI_PS_AC_VOLT_B,     display_text = "Message 0C" },
        new() { id = (uint)Message_Register_ID.GUI_PS_VOLT_A,        display_text = "Message 0D" },
        new() { id = (uint)Message_Register_ID.GUI_PS_VOLT_B,        display_text = "Message 0E" },
        new() { id = (uint)Message_Register_ID.GUI_PS_CURR,          display_text = "Message 0F" },
        new() { id = (uint)Message_Register_ID.GUI_PS_TEMP,          display_text = "Message 10" },
        new() { id = (uint)Message_Register_ID.GUI_PS_CHARGE_VOLT_A, display_text = "Message 11" },
        new() { id = (uint)Message_Register_ID.GUI_PS_CHARGE_VOLT_B, display_text = "Message 12" },
        new() { id = (uint)Message_Register_ID.GUI_PS_CHARGE_CURR,   display_text = "Message 13" },
        new() { id = (uint)Message_Register_ID.GUI_PS_FLOAT_VOLT_A,  display_text = "Message 14" },
        new() { id = (uint)Message_Register_ID.GUI_PS_FLOAT_VOLT_B,  display_text = "Message 15" },
        new() { id = (uint)Message_Register_ID.GUI_PS_TAPER_CURR,    display_text = "Message 16" },
        new() { id = (uint)Message_Register_ID.GUI_RESISTOR_TEMP,    display_text = "Message 17" },
        new() { id = (uint)Message_Register_ID.GUI_BOARD_TEMP,       display_text = "Message 18" },
        new() { id = (uint)Message_Register_ID.GUI_SYS_INFO,         display_text = "Message 19" },
        new() { id = (uint)Message_Register_ID.GUI_TIME_STAMP,       display_text = "Message 1A" },
        new() { id = (uint)Message_Register_ID.DISPLAY1_ADC,         display_text = "Message 1B" },
        new() { id = (uint)Message_Register_ID.DISPLAY2_ADC,         display_text = "Message 1C" },
        new() { id = (uint)Message_Register_ID.CMD_SET_SERIAL_R, display_text = "Set Serial Number" },
        new() { id = (uint)Message_Register_ID.CMD_CALIBRATE_ADC_OFFSETS_R, display_text = "Calibrate ADC Offsets" },
        new() { id = (uint)Message_Register_ID.CMD_CALIBRATE_ADC_VOLT_R, display_text = "Calibrate Voltage" },
        new() { id = (uint)Message_Register_ID.CMD_CALIBRATE_ADC_CURR_R, display_text = "Calibrate Current" }
    };

    private static readonly HashSet<Status_Register> s_status_register_set =
    new()
    {
        new()
        {
            id = (uint)Status_Register_ID.PS1_CHARGE_STATUS_HI,
            display_text = "PS1 Charge Status Hi",
            bit7 = ("FVTOF", false),
            bit6 = ("CVTOF", false),
            bit5 = ("CCTOF", false),
            bit4 = ("RSVD", true),
            bit3 = ("BTNC", false),
            bit2 = ("NTCER", false),
            bit1 = ("RSVD", true),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS1_CHARGE_STATUS_LO,
            display_text = "PS1 Charge Status Lo",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("FVM", false),
            bit2 = ("CVM", false),
            bit1 = ("CCM", false),
            bit0 = ("FULLM", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS1_FAULT_STATUS,
            display_text = "PS1 Fault Status",
            bit7 = ("HI_TEMP", false),
            bit6 = ("OP_OFF", false),
            bit5 = ("AC_FAIL", false),
            bit4 = ("SHORT", false),
            bit3 = ("OLP", false),
            bit2 = ("OVP", false),
            bit1 = ("OTP", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS1_SYSTEM_STATUS,
            display_text = "PS1 System Status",
            bit7 = ("RSVD", true),
            bit6 = ("EEPER", false),
            bit5 = ("INIT_STATE", false),
            bit4 = ("RSVD", true),
            bit3 = ("RSVD", true),
            bit2 = ("RSVD", true),
            bit1 = ("DC_OK", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS2_CHARGE_STATUS_HI,
            display_text = "PS2 Charge Status Hi",
            bit7 = ("FVTOF", false),
            bit6 = ("CVTOF", false),
            bit5 = ("CCTOF", false),
            bit4 = ("RSVD", true),
            bit3 = ("BTNC", false),
            bit2 = ("NTCER", false),
            bit1 = ("RSVD", true),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS2_CHARGE_STATUS_LO,
            display_text = "PS2 Charge Status Lo",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("FVM", false),
            bit2 = ("CVM", false),
            bit1 = ("CCM", false),
            bit0 = ("FULLM", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS2_FAULT_STATUS,
            display_text = "PS2 Fault Status",
            bit7 = ("HI_TEMP", false),
            bit6 = ("OP_OFF", false),
            bit5 = ("AC_FAIL", false),
            bit4 = ("SHORT", false),
            bit3 = ("OLP", false),
            bit2 = ("OVP", false),
            bit1 = ("OTP", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS2_SYSTEM_STATUS,
            display_text = "PS2 System Status",
            bit7 = ("RSVD", true),
            bit6 = ("EEPER", false),
            bit5 = ("INIT_STATE", false),
            bit4 = ("ADL_ON", false),
            bit3 = ("RSVD", true),
            bit2 = ("RSVD", true),
            bit1 = ("DC_OK", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS3_CHARGE_STATUS_HI,
            display_text = "PS3 Charge Status Hi",
            bit7 = ("FVTOF", false),
            bit6 = ("CVTOF", false),
            bit5 = ("CCTOF", false),
            bit4 = ("RSVD", true),
            bit3 = ("BTNC", false),
            bit2 = ("NTCER", false),
            bit1 = ("RSVD", true),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS3_CHARGE_STATUS_LO,
            display_text = "PS3 Charge Status Lo",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("FVM", false),
            bit2 = ("CVM", false),
            bit1 = ("CCM", false),
            bit0 = ("FULLM", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS3_FAULT_STATUS,
            display_text = "PS3 Fault Status",
            bit7 = ("HI_TEMP", false),
            bit6 = ("OP_OFF", false),
            bit5 = ("AC_FAIL", false),
            bit4 = ("SHORT", false),
            bit3 = ("OLP", false),
            bit2 = ("OVP", false),
            bit1 = ("OTP", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS3_SYSTEM_STATUS,
            display_text = "PS3 System Status",
            bit7 = ("RSVD", true),
            bit6 = ("EEPER", false),
            bit5 = ("INIT_STATE", false),
            bit4 = ("ADL_ON", false),
            bit3 = ("RSVD", true),
            bit2 = ("RSVD", true),
            bit1 = ("DC_OK", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS4_CHARGE_STATUS_HI,
            display_text = "PS4 Charge Status Hi",
            bit7 = ("FVTOF", false),
            bit6 = ("CVTOF", false),
            bit5 = ("CCTOF", false),
            bit4 = ("RSVD", true),
            bit3 = ("BTNC", false),
            bit2 = ("NTCER", false),
            bit1 = ("RSVD", true),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS4_CHARGE_STATUS_LO,
            display_text = "PS4 Charge Status Lo",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("FVM", false),
            bit2 = ("CVM", false),
            bit1 = ("CCM", false),
            bit0 = ("FULLM", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS4_FAULT_STATUS,
            display_text = "PS4 Fault Status",
            bit7 = ("HI_TEMP", false),
            bit6 = ("OP_OFF", false),
            bit5 = ("AC_FAIL", false),
            bit4 = ("SHORT", false),
            bit3 = ("OLP", false),
            bit2 = ("OVP", false),
            bit1 = ("OTP", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.PS4_SYSTEM_STATUS,
            display_text = "PS4 System Status",
            bit7 = ("RSVD", true),
            bit6 = ("EEPER", false),
            bit5 = ("INIT_STATE", false),
            bit4 = ("ADL_ON", false),
            bit3 = ("RSVD", true),
            bit2 = ("RSVD", true),
            bit1 = ("DC_OK", false),
            bit0 = ("RSVD", true)
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
            id = (uint)Command_ID.SET_SERIAL_NUMBER,
            display_text = "Set Serial Number",
            arguments = ImmutableArray.Create(("SN:", "0")),
            response_timeout = 1_000
        },
        new()
        {
            id = (uint)Command_ID.CALIBRATE_ADC_OFFSETS,
            display_text = "Calibrate ADC Offsets",
            arguments = ImmutableArray.Create<(string, string)>(),
            response_timeout = 1_000
        },
        new()
        {
            id = (uint)Command_ID.CALIBRATE_VOLT,
            display_text = "Calibrate Voltage",
            arguments = ImmutableArray.Create
            (
                ("Channel Number:", "1"),
                ("Measured Voltage (V):", "50.0")
            ),
            response_timeout = 1_000
        },
        new()
        {
            id = (uint)Command_ID.CALIBRATE_CURR,
            display_text = "Calibrate Current",
            arguments = ImmutableArray.Create
            (
                ("Channel Number:", "1"),
                ("Applied Current (A):", "2.0")
            ),
            response_timeout = 1000
        }
    };

    public
    Aerosonde_Three_Charger() :
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
    public override Command? enter_bootloader_command => s_enter_bootloader;

    protected override void
    new_can_message
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if (instrumentDataCounter == 0xFF)
        {
            InitInstrumentData();
        }

        if((a_id.id & 0x1FFF0000u) is not 0x13370000u)
        {
            return;
        }

        var a_mesg = (a_id.id & 0x0000FF00u) >> 8;
        var a_addr = (a_id.id & 0x000000F0u) >> 4;
        var a_chan = (a_id.id & 0x0000000Fu) >> 0;

        var a_message = (Message_Register_ID)a_mesg;

        var a_data_parsed =
        a_message switch
        {
            Message_Register_ID.GUI_CHARGER_STATE =>    parse_message_00(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PACK_VOLT_A =>      parse_message_01(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PACK_VOLT_B =>      parse_message_02(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PACK_CURR =>        parse_message_03(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PACK_TEMP =>        parse_message_04(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PACK_SOC =>         parse_message_05(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_ADC_VOLT_A =>       parse_message_06(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_ADC_VOLT_B =>       parse_message_07(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_ADC_CURR =>         parse_message_08(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_CHARGE_STATUS => parse_message_09(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_SYSTEM_STATUS => parse_message_0A(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_AC_VOLT_A =>     parse_message_0B(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_AC_VOLT_B =>     parse_message_0C(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_VOLT_A =>        parse_message_0D(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_VOLT_B =>        parse_message_0E(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_CURR =>          parse_message_0F(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_TEMP =>          parse_message_10(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_CHARGE_VOLT_A => parse_message_11(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_CHARGE_VOLT_B => parse_message_12(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_CHARGE_CURR =>   parse_message_13(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_FLOAT_VOLT_A =>  parse_message_14(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_FLOAT_VOLT_B =>  parse_message_15(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_PS_TAPER_CURR =>    parse_message_16(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_RESISTOR_TEMP =>    parse_message_17(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_BOARD_TEMP =>       parse_message_18(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_SYS_INFO =>         parse_message_19(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_TIME_STAMP =>       parse_message_1A(a_addr, a_chan, a_data),
            Message_Register_ID.GUI_DISPLAY_ADC =>      parse_message_1B_1C(a_addr, a_chan, a_data),
            Message_Register_ID.CMD_SET_SERIAL_R => parse_set_serial_response(a_addr, a_chan, a_data),
            Message_Register_ID.CMD_CALIBRATE_ADC_OFFSETS_R => parse_cal_offsets_response(a_addr, a_chan, a_data),
            Message_Register_ID.CMD_CALIBRATE_ADC_VOLT_R => parse_cal_volt_response(a_addr, a_chan, a_data),
            Message_Register_ID.CMD_CALIBRATE_ADC_CURR_R => parse_cal_curr_response(a_addr, a_chan, a_data),
            _ => null
        };


        if (a_message == Message_Register_ID.GUI_PS_CHARGE_STATUS)
        {
            CheckInstrumentData();
        }

        if (a_data_parsed is null)
        {
            return;
        }

        if(a_message is Message_Register_ID.GUI_DISPLAY_ADC)
        {
            if(a_addr is 2)
            {
                a_message = Message_Register_ID.DISPLAY1_ADC;
            }

            if(a_addr is 3)
            {
                a_message = Message_Register_ID.DISPLAY2_ADC;
            }
        }

        using var a_g1 = String_Builder_Pool.acquire();

        add_mess_register_parsed
        (
            message_register_map[(uint)a_message],
            new(a_id, a_data)
            {
                id_interpreted = a_g1.value.Append($"MS={a_mesg:X2} AD={a_addr:X1} CH={a_chan:X1}").ToString(),
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
        (Command a_command, uint a_mesg, uint a_chan, byte[] a_data)
        {
            using var a_g1 = String_Builder_Pool.acquire();
            using var a_g2 = String_Builder_Pool.acquire();

            add_outgoing_can_message
            (
                new
                (
                    new()
                    {
                        ext_id = 0x13370000u | ((a_mesg & 0xFFu) << 8) | (a_chan & 0xF),
                        is_can_fd = false,
                        is_remote = false,
                        size = a_data.Length
                    },
                    a_data
                )
                {
                    id_interpreted = a_g1.value.Append($"MS={a_mesg:X2} AD=0 CH={a_chan:X1}").ToString(),
                    data_interpreted = a_g2.value.Append($"Command: {a_command.display_text}").ToString()
                }
            );
        }

        var a_command_id = (Command_ID)a_command.id;

        if (a_command_id == Command_ID.ENTER_BOOTLOADER)
        {
            CloseInstrumentData();
            return;
        }

        var (a_mesg, a_chan, a_data) =
            a_command_id switch
            {
                Command_ID.ENTER_BOOTLOADER => process_enter_bootloader(),
                Command_ID.SET_SERIAL_NUMBER => process_set_serial_number(a_args[0]),
                Command_ID.CALIBRATE_ADC_OFFSETS => process_calibrate_adc_offsets(),
                Command_ID.CALIBRATE_VOLT => process_calibrate_volt(a_args[0], a_args[1]),
                Command_ID.CALIBRATE_CURR => process_calibrate_curr(a_args[0], a_args[1]),
                _ => throw new ArgumentOutOfRangeException(nameof(a_command))
            };

        add_command(a_command, a_mesg, a_chan, a_data);
    }

    private static string?
    parse_message_00
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_charger_state, a_data, ref a_index);
        Misc.decode_le(out byte a_nvm_lock_owner, a_data, ref a_index);
        Misc.decode_le(out byte a_pack4_state, a_data, ref a_index);
        Misc.decode_le(out byte a_pack3_state, a_data, ref a_index);
        Misc.decode_le(out byte a_pack2_state, a_data, ref a_index);
        Misc.decode_le(out byte a_pack1_state, a_data, ref a_index);

        instrumentData[0] = a_pack1_state;
        instrumentData[1] = a_pack2_state;
        instrumentData[2] = a_pack3_state;
        instrumentData[3] = a_pack4_state;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Charger State: {parse_charger_state(a_charger_state)}")
            .Append($"NVM Lock: {parse_lock_owner(a_nvm_lock_owner)}")
            .Append($"PK1: {parse_pack_state(a_pack1_state)}")
            .Append($"PK2: {parse_pack_state(a_pack2_state)}")
            .Append($"PK3: {parse_pack_state(a_pack3_state)}")
            .Append($"PK4: {parse_pack_state(a_pack4_state)}")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_01
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_v2, a_data, ref a_index);
        Misc.decode_le(out uint a_v1, a_data, ref a_index);

        instrumentData[4] = (int) a_v1;
        instrumentData[5] = (int) a_v2;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PK3 Volt: {to_volts(a_v1)}; ")
            .Append($"PK4 Volt: {to_volts(a_v2)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_02
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_v2, a_data, ref a_index);
        Misc.decode_le(out uint a_v1, a_data, ref a_index);

        instrumentData[6] = (int)a_v1;
        instrumentData[7] = (int)a_v2;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PK1 Volt: {to_volts(a_v1)}; ")
            .Append($"PK2 Volt: {to_volts(a_v2)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_03
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out short a_c4, a_data, ref a_index);
        Misc.decode_le(out short a_c3, a_data, ref a_index);
        Misc.decode_le(out short a_c2, a_data, ref a_index);
        Misc.decode_le(out short a_c1, a_data, ref a_index);

        instrumentData[8] = (int)  a_c1;
        instrumentData[9] = (int)  a_c2;
        instrumentData[10] = (int) a_c3;
        instrumentData[11] = (int) a_c4;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PK1 Curr: {to_amps(a_c1)}; ")
            .Append($"PK2 Curr: {to_amps(a_c2)}; ")
            .Append($"PK3 Curr: {to_amps(a_c3)}; ")
            .Append($"PK4 Curr: {to_amps(a_c4)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_04
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_t4, a_data, ref a_index);
        Misc.decode_le(out ushort a_t3, a_data, ref a_index);
        Misc.decode_le(out ushort a_t2, a_data, ref a_index);
        Misc.decode_le(out ushort a_t1, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PK1 Temp: {to_celcius(a_t1)}; ")
            .Append($"PK2 Temp: {to_celcius(a_t2)}; ")
            .Append($"PK3 Temp: {to_celcius(a_t3)}; ")
            .Append($"PK4 Temp: {to_celcius(a_t4)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_05
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 4)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_soc4, a_data, ref a_index);
        Misc.decode_le(out byte a_soc3, a_data, ref a_index);
        Misc.decode_le(out byte a_soc2, a_data, ref a_index);
        Misc.decode_le(out byte a_soc1, a_data, ref a_index);

        instrumentData[12] = (int)a_soc1;
        instrumentData[13] = (int)a_soc2;
        instrumentData[14] = (int)a_soc3;
        instrumentData[15] = (int)a_soc4;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PK1 SoC: {to_percent(a_soc1)}; ")
            .Append($"PK2 SoC: {to_percent(a_soc2)}; ")
            .Append($"PK3 SoC: {to_percent(a_soc3)}; ")
            .Append($"PK4 SoC: {to_percent(a_soc4)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_06
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out int a_v2, a_data, ref a_index);
        Misc.decode_le(out int a_v1, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"ADC3 Volt: {to_volts(a_v1)}; ")
            .Append($"ADC4 Volt: {to_volts(a_v2)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_07
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out int a_v2, a_data, ref a_index);
        Misc.decode_le(out int a_v1, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"ADC1 Volt: {to_volts(a_v1)}; ")
            .Append($"ADC2 Volt: {to_volts(a_v2)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_08
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out short a_c4, a_data, ref a_index);
        Misc.decode_le(out short a_c3, a_data, ref a_index);
        Misc.decode_le(out short a_c2, a_data, ref a_index);
        Misc.decode_le(out short a_c1, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"ADC1 Curr: {to_amps(a_c1)}; ")
            .Append($"ADC2 Curr: {to_amps(a_c2)}; ")
            .Append($"ADC3 Curr: {to_amps(a_c3)}; ")
            .Append($"ADC4 Curr: {to_amps(a_c4)}; ")
            .ToString();

        return a_result;
    }

    private string?
    parse_message_09
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_s1, a_data, ref a_index);
        Misc.decode_le(out ushort a_s2, a_data, ref a_index);
        Misc.decode_le(out ushort a_s3, a_data, ref a_index);
        Misc.decode_le(out ushort a_s4, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS1 Charge Status: 0x{a_s1:X4}; ")
            .Append($"PS2 Charge Status: 0x{a_s2:X4}; ")
            .Append($"PS3 Charge Status: 0x{a_s3:X4}; ")
            .Append($"PS4 Charge Status: 0x{a_s4:X4}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS1_CHARGE_STATUS_HI], (byte)((a_s1 & 0xFF00u) >> 8));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS1_CHARGE_STATUS_LO], (byte)((a_s1 & 0x00FFu) >> 0));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS2_CHARGE_STATUS_HI], (byte)((a_s2 & 0xFF00u) >> 8));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS2_CHARGE_STATUS_LO], (byte)((a_s3 & 0x00FFu) >> 0));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS3_CHARGE_STATUS_HI], (byte)((a_s3 & 0xFF00u) >> 8));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS3_CHARGE_STATUS_LO], (byte)((a_s3 & 0x00FFu) >> 0));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS4_CHARGE_STATUS_HI], (byte)((a_s4 & 0xFF00u) >> 8));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS4_CHARGE_STATUS_LO], (byte)((a_s4 & 0x00FFu) >> 0));

        return a_result;
    }

    private string?
    parse_message_0A
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_f1, a_data, ref a_index);
        Misc.decode_le(out byte a_f2, a_data, ref a_index);
        Misc.decode_le(out byte a_f3, a_data, ref a_index);
        Misc.decode_le(out byte a_f4, a_data, ref a_index);
        Misc.decode_le(out byte a_s1, a_data, ref a_index);
        Misc.decode_le(out byte a_s2, a_data, ref a_index);
        Misc.decode_le(out byte a_s3, a_data, ref a_index);
        Misc.decode_le(out byte a_s4, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS1 Fault Stat: 0x{a_f1:X2}; ")
            .Append($"PS2 Fault Stat: 0x{a_f2:X2}; ")
            .Append($"PS3 Fault Stat: 0x{a_f3:X2}; ")
            .Append($"PS4 Fault Stat: 0x{a_f4:X2}; ")
            .Append($"PS1 Sys Stat: 0x{a_s1:X2}; ")
            .Append($"PS2 Sys Stat: 0x{a_s2:X2}; ")
            .Append($"PS3 Sys Stat: 0x{a_s3:X2}; ")
            .Append($"PS4 Sys Stat: 0x{a_s4:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS1_FAULT_STATUS], a_f1);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS2_FAULT_STATUS], a_f2);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS3_FAULT_STATUS], a_f3);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS4_FAULT_STATUS], a_f4);

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS1_SYSTEM_STATUS], a_s1);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS2_SYSTEM_STATUS], a_s2);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS3_SYSTEM_STATUS], a_s3);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PS4_SYSTEM_STATUS], a_s4);

        return a_result;
    }

    private static string?
    parse_message_0B
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_v1, a_data, ref a_index);
        Misc.decode_le(out uint a_v2, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS1 AC Volt: {to_volts(a_v1)}; ")
            .Append($"PS2 AC Volt: {to_volts(a_v2)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_0C
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_v1, a_data, ref a_index);
        Misc.decode_le(out uint a_v2, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS3 AC Volt: {to_volts(a_v1)}; ")
            .Append($"PS4 AC Volt: {to_volts(a_v2)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_0D
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_v1, a_data, ref a_index);
        Misc.decode_le(out uint a_v2, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS1 Volt: {to_volts(a_v1)}; ")
            .Append($"PS2 Volt: {to_volts(a_v2)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_0E
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_v1, a_data, ref a_index);
        Misc.decode_le(out uint a_v2, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS3 Volt: {to_volts(a_v1)}; ")
            .Append($"PS4 Volt: {to_volts(a_v2)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_0F
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_c4, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS1 Curr: {to_amps(a_c1)}; ")
            .Append($"PS2 Curr: {to_amps(a_c2)}; ")
            .Append($"PS3 Curr: {to_amps(a_c3)}; ")
            .Append($"PS4 Curr: {to_amps(a_c4)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_10
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_t1, a_data, ref a_index);
        Misc.decode_le(out ushort a_t2, a_data, ref a_index);
        Misc.decode_le(out ushort a_t3, a_data, ref a_index);
        Misc.decode_le(out ushort a_t4, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS1 Temp: {to_celcius(a_t1)}; ")
            .Append($"PS2 Temp: {to_celcius(a_t2)}; ")
            .Append($"PS3 Temp: {to_celcius(a_t3)}; ")
            .Append($"PS4 Temp: {to_celcius(a_t4)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_11
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_v1, a_data, ref a_index);
        Misc.decode_le(out uint a_v2, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS1 Charge Volt: {to_volts(a_v1)}; ")
            .Append($"PS2 Charge Volt: {to_volts(a_v2)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_12
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_v1, a_data, ref a_index);
        Misc.decode_le(out uint a_v2, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS3 Charge Volt: {to_volts(a_v1)}; ")
            .Append($"PS4 Charge Volt: {to_volts(a_v2)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_13
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_c4, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS1 Charge Curr: {to_amps(a_c1)}; ")
            .Append($"PS2 Charge Curr: {to_amps(a_c2)}; ")
            .Append($"PS3 Charge Curr: {to_amps(a_c3)}; ")
            .Append($"PS4 Charge Curr: {to_amps(a_c4)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_14
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_v1, a_data, ref a_index);
        Misc.decode_le(out uint a_v2, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS1 Float Volt: {to_volts(a_v1)}; ")
            .Append($"PS2 Float Volt: {to_volts(a_v2)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_15
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_v1, a_data, ref a_index);
        Misc.decode_le(out uint a_v2, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS3 Float Volt: {to_volts(a_v1)}; ")
            .Append($"PS4 Float Volt: {to_volts(a_v2)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_16
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_c4, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS1 Taper Curr: {to_amps(a_c1)}; ")
            .Append($"PS2 Taper Curr: {to_amps(a_c2)}; ")
            .Append($"PS3 Taper Curr: {to_amps(a_c3)}; ")
            .Append($"PS4 Taper Curr: {to_amps(a_c4)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_17
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_t4, a_data, ref a_index);
        Misc.decode_le(out ushort a_t3, a_data, ref a_index);
        Misc.decode_le(out ushort a_t2, a_data, ref a_index);
        Misc.decode_le(out ushort a_t1, a_data, ref a_index);

        instrumentData[16] = (int)a_t1;
        instrumentData[17] = (int)a_t2;
        instrumentData[18] = (int)a_t3;
        instrumentData[19] = (int)a_t4;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"RES1 Temp: {to_celcius(a_t1)}; ")
            .Append($"RES2 Temp: {to_celcius(a_t2)}; ")
            .Append($"RES3 Temp: {to_celcius(a_t3)}; ")
            .Append($"RES4 Temp: {to_celcius(a_t4)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_18
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_case_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_board_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_utemp, a_data, ref a_index);
        Misc.decode_le(out ushort a_vref, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Case Temp: {to_celcius(a_case_temp)}; ")
            .Append($"Board Temp: {to_celcius(a_board_temp)}; ")
            .Append($"μC Internal Temp: {to_celcius(a_utemp)}; ")
            .Append($"μC Vref Internal: {to_volts(a_vref)}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_19
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_serial_number, a_data, ref a_index);
        Misc.decode_le(out ushort a_micro_firmware, a_data, ref a_index);

        var a_vmajor = (a_micro_firmware & 0b1111110000000000) >> 10;
        var a_vminor = (a_micro_firmware & 0b0000001111110000) >> 4;
        var a_rev =    (a_micro_firmware & 0b0000000000001111) >> 0;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Serial Number: {a_serial_number:D10}; ")
            .Append($"µC Firmware Ver: {a_vmajor}.{a_vminor}.{a_rev}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_1A
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out long a_timestamp, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        curTimeStamp = a_timestamp / 1000;

        var a_result =
            a_g1.value
            .Append($"Time Stamp: {a_timestamp}; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_1B_1C
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 2 and not 3 || a_chan is not 0 || a_data.Length is not 6)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_ls_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_utemp, a_data, ref a_index);
        Misc.decode_le(out ushort a_vref, a_data, ref a_index);

        var a_disp = a_addr is 2 ? "DISP1" : "DISP2";

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"{a_disp} LS Volt: {to_volts(a_ls_volt)}; ")
            .Append($"{a_disp} μC Internal Temp: {to_celcius(a_utemp)}; ")
            .Append($"{a_disp} μC Vref Internal: {to_volts(a_vref)}; ")
            .ToString();

        return a_result;
    }

    private string?
    parse_set_serial_response
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 1)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_success, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Set Serial Number: {(a_success is not 0 ? "SUCCESS" : "FAILURE")}; ")
            .ToString();

        set_pending_command_completed();

        return a_result;
    }

    private string?
    parse_cal_offsets_response
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_chan is not 0 || a_data.Length is not 1)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_success, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Calibrate ADC Offsets: {(a_success is not 0 ? "SUCCESS" : "FAILURE")}; ")
            .ToString();

        set_pending_command_completed();

        return a_result;
    }

    private string?
    parse_cal_volt_response
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_data.Length is not 1)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_success, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Calibrate Voltage Channel {a_chan}: {(a_success is not 0 ? "SUCCESS" : "FAILURE")}; ")
            .ToString();

        set_pending_command_completed();

        return a_result;
    }

    private string?
    parse_cal_curr_response
    (uint a_addr, uint a_chan, in ReadOnlySpan<byte> a_data)
    {
        if(a_addr is not 1 || a_data.Length is not 1)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_success, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Calibrate Current Channel {a_chan}: {(a_success is not 0 ? "SUCCESS" : "FAILURE")}; ")
            .ToString();

        set_pending_command_completed();

        return a_result;
    }

    private static (uint a_mesg, uint a_chan, byte[] a_data)
    process_enter_bootloader() =>
        ((uint)Message_Register_ID.CMD_ENTER_BOOTLOADER, 0u, Array.Empty<byte>());

    private static (uint a_mesg, uint a_chan, byte[] a_data)
    process_set_serial_number
    (string a_serial_arg)
    {
        var a_serial = uint.Parse(a_serial_arg);

        var a_data = new byte[4];
        var a_index = 0;

        Misc.encode_le(a_serial, a_data, ref a_index);

        return ((uint)Message_Register_ID.CMD_SET_SERIAL_S, 0u, a_data);
    }

    private static (uint a_mesg, uint a_chan, byte[] a_data)
    process_calibrate_adc_offsets() =>
        ((uint)Message_Register_ID.CMD_CALIBRATE_ADC_OFFSETS_S, 0u, Array.Empty<byte>());

    private static (uint a_mesg, uint a_chan, byte[] a_data)
    process_calibrate_volt
    (string a_chan_arg, string a_volt_arg)
    {
        const double MIN_LIMIT = 25.0;
        const double MAX_LIMIT = 105.0;

        var a_volt = double.Parse(a_volt_arg, NumberStyles.Float);

        if(a_volt is < MIN_LIMIT or > MAX_LIMIT)
        {
            throw new ArgumentException($"Calibrate Voltage: voltage ({a_volt:F3}V) must be >= {MIN_LIMIT:F3}V and <= {MAX_LIMIT:F3}V");
        }

        var a_chan = uint.Parse(a_chan_arg);

        if(a_chan is not 1 and not 2 and not 3 and not 4)
        {
            throw new ArgumentException($"Invalid Channel: channel ({a_chan}) must be 1, 2, 3, or 4");
        }

        var a_data = new byte[4];
        var a_index = 0;

        Misc.encode_le((uint)(1000.0 * a_volt), a_data, ref a_index);

        return ((uint)Message_Register_ID.CMD_CALIBRATE_ADC_VOLT_S, a_chan, a_data);
    }

    private static (uint a_mesg, uint a_chan, byte[] a_data)
    process_calibrate_curr
    (string a_chan_arg, string a_curr_arg)
    {
        const double MIN_LIMIT = 1.0;
        const double MAX_LIMIT = 4.0;

        var a_curr = double.Parse(a_curr_arg, NumberStyles.Float);

        if(a_curr is < MIN_LIMIT or > MAX_LIMIT)
        {
            throw new ArgumentException($"Calibrate Current: current ({a_curr:F3}A) must be >= {MIN_LIMIT:F3}A and <= {MAX_LIMIT:F3}A");
        }

        var a_chan = uint.Parse(a_chan_arg);

        if(a_chan is not 1 and not 2 and not 3 and not 4)
        {
            throw new ArgumentException($"Invalid Channel: channel ({a_chan}) must be 1, 2, 3, or 4");
        }

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le((ushort)(1000.0 * a_curr), a_data, ref a_index);

        return ((uint)Message_Register_ID.CMD_CALIBRATE_ADC_CURR_S, a_chan, a_data);
    }

    private static string
    to_volts
    (uint a_raw)
    {
        if(a_raw is uint.MaxValue)
        {
            return "N/A";
        }

        return $"{0.001 * a_raw:F3}V";
    }

    private static string
    to_volts
    (int a_raw)
    {
        if(a_raw is int.MinValue)
        {
            return "N/A";
        }

        return $"{0.001 * a_raw:F3}V";
    }

    private static string
    to_volts
    (ushort a_raw)
    {
        if(a_raw is ushort.MaxValue)
        {
            return "N/A";
        }

        return $"{0.001 * a_raw:F3}V";
    }

    private static string
    to_volts
    (short a_raw)
    {
        if(a_raw is short.MinValue)
        {
            return "N/A";
        }

        return $"{0.001 * a_raw:F3}V";
    }

    private static string
    to_amps
    (ushort a_raw)
    {
        if(a_raw is ushort.MaxValue)
        {
            return "N/A";
        }

        return $"{0.001 * a_raw:F3}A";
    }

    private static string
    to_amps
    (short a_raw)
    {
        if(a_raw is short.MinValue)
        {
            return "N/A";
        }

        return $"{0.001 * a_raw:F3}A";
    }

    private static string
    to_celcius
    (ushort a_raw)
    {
        if(a_raw is ushort.MaxValue)
        {
            return "N/A";
        }

        return $"{0.1 * a_raw - 273.1:F1}°C";
    }

    private static string
    to_percent
    (byte a_raw)
    {
        if(a_raw is byte.MaxValue)
        {
            return "N/A";
        }

        return $"{a_raw}%";
    }

    private static string
    parse_charger_state
    (byte a_state) =>
        (Charger_State)a_state switch
        {
            Charger_State.INITIALIZING => "Init;      ",
            Charger_State.PS_SETUP     => "PS Setup;  ",
            Charger_State.IDLE         => "Idle;      ",
            Charger_State.BUSY         => "Busy;      ",
            Charger_State.EMERGENCY    => "Emergency; ",
            Charger_State.BOOTLOADER   => "Boot;      ",
            _                          => "Invalid;   "
        };

    private static string
    parse_lock_owner
    (byte a_state) =>
        (NVM_Lock_Owner)a_state switch
        {
            NVM_Lock_Owner.NONE      => "None;    ",
            NVM_Lock_Owner.CHANNEL_1 => "Ch1;     ",
            NVM_Lock_Owner.CHANNEL_2 => "Ch2;     ",
            NVM_Lock_Owner.CHANNEL_3 => "Ch3;     ",
            NVM_Lock_Owner.CHANNEL_4 => "Ch4;     ",
            NVM_Lock_Owner.GUI       => "GUI;     ",
            NVM_Lock_Owner.CHARGER   => "Charger; ",
            _                        => "Invalid; "
        };

    private static string
    parse_pack_state
    (byte a_state)
    {
        var a_spc = "; ";
        var a_end = (a_state & 0x80u) is 0 ? "*;" : a_spc;

        var a_result =
        (Pack_State)(a_state & 0x7Fu) switch
        {
            Pack_State.DISCONNECTED    => $"Disconnected{a_spc}",
            Pack_State.CONNECTED       => $"Connected{a_end}   ",
            Pack_State.CHARGE_ONGOING  => $"Charging{a_end}    ",
            Pack_State.CHARGE_PAUSED   => $"Chg Paused{a_end}  ",
            Pack_State.CHARGE_COMPLETE => $"Chg Complete{a_end}",
            Pack_State.DISCHG_ONGOING  => $"Discharging{a_end} ",
            Pack_State.DISCHG_PAUSED   => $"Dsg Paused{a_end}  ",
            Pack_State.DISCHG_COMPLETE => $"Dsg Complete{a_end}",
            _                          => $"Invalid{a_spc}     "
        };

        return a_result;
    }
}
