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
GE_Healthcare : Product
{
    private enum
    Destination_ID : uint
    {
        PACK_0,
        PACK_1,
        PACK_2,
        PACK_3
    }

    private enum
    Message_Register_ID : uint
    {
        MESSAGE_COMMAND_RESPONSE,
        MESSAGE_01,
        MESSAGE_02,
        MESSAGE_03,
        MESSAGE_04,
        MESSAGE_05,
        MESSAGE_06,
        MESSAGE_07_I,
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
        MESSAGE_1C,
        MESSAGE_1D,
        MESSAGE_07_II = 1024
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
        BOT_AFE_CB_ACTIVE_HI,
        BOT_AFE_CB_ACTIVE_LO,
        BOT_AFE_FET_STATUS,
        BOT_AFE_CONTROL_STATUS_HI,
        BOT_AFE_CONTROL_STATUS_LO,
        BOT_AFE_BATTERY_STATUS_HI,
        BOT_AFE_BATTERY_STATUS_LO,
        BOT_AFE_ALARM_STATUS_HI,
        BOT_AFE_ALARM_STATUS_LO,
        BOT_AFE_ALARM_RAW_STATUS_HI,
        BOT_AFE_ALARM_RAW_STATUS_LO,
        BOT_AFE_SAFETY_ALERT_A,
        BOT_AFE_SAFETY_ALERT_B,
        BOT_AFE_SAFETY_ALERT_C,
        BOT_AFE_SAFETY_STATUS_A,
        BOT_AFE_SAFETY_STATUS_B,
        BOT_AFE_SAFETY_STATUS_C,
        BOT_AFE_PF_ALERT_A,
        BOT_AFE_PF_ALERT_B,
        BOT_AFE_PF_ALERT_C,
        BOT_AFE_PF_ALERT_D,
        BOT_AFE_PF_STATUS_A,
        BOT_AFE_PF_STATUS_B,
        BOT_AFE_PF_STATUS_C,
        BOT_AFE_PF_STATUS_D,
    };

    private enum
    Query_ID : uint
    {
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
        MESSAGE_1C,
        MESSAGE_1D,
        ALL
    };

    private enum
    Command_ID : uint
    {
        ENTER_BOOTLOADER,
        SET_PERIODIC_TIME,
        HEATER_OFF,
        HEATER_ON,
        HEATER_AUTO,
        HEATER_LIMITS,
        SET_SERIAL_NUMBER,
        SET_ID_PREFIX,
        FG_RESET,
        FG_LIFETIME_ENABLE,
        FG_SEAL,
        FG_UNSEAL,
        FG_UNSEAL_FULL,
        FG_PROGRAM,
        FG_CAL_CC_OFFSET,
        FG_CAL_BOARD_OFFSET,
        FG_CAL_VOLTAGE,
        FG_CAL_CURRENT,
        PF_ENABLE,
        PF_DISABLE,
        PF_RESET,
        SAVE_FG_CAL_DATA,
        APPLY_SAVED_FG_CAL_DATA,
        INFLIGHT_CHARGE_ENABLE,
        INFLIGHT_CHARGE_DISABLE
    };

    private static readonly Destination s_default_dest =
    new() { id = (uint)Destination_ID.PACK_3, display_text = "Pack 3" };

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
        new() { id = (uint)Destination_ID.PACK_0, display_text = "Pack 0" },
        new() { id = (uint)Destination_ID.PACK_1, display_text = "Pack 1" },
        new() { id = (uint)Destination_ID.PACK_2, display_text = "Pack 2" },
        s_default_dest
    };

    private static readonly HashSet<Message_Register> s_message_register_set =
    new()
    {
        new() { id = (uint)Message_Register_ID.MESSAGE_COMMAND_RESPONSE, display_text = "Command Response" },
        new() { id = (uint)Message_Register_ID.MESSAGE_01, display_text = "Message 01" },
        new() { id = (uint)Message_Register_ID.MESSAGE_02, display_text = "Message 02" },
        new() { id = (uint)Message_Register_ID.MESSAGE_03, display_text = "Message 03" },
        new() { id = (uint)Message_Register_ID.MESSAGE_04, display_text = "Message 04" },
        new() { id = (uint)Message_Register_ID.MESSAGE_05, display_text = "Message 05" },
        new() { id = (uint)Message_Register_ID.MESSAGE_06, display_text = "Message 06" },
        new() { id = (uint)Message_Register_ID.MESSAGE_07_I, display_text = "Message 07 I" },
        new() { id = (uint)Message_Register_ID.MESSAGE_07_II, display_text = "Message 07 II" },
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
        //new() { id = (uint)Message_Register_ID.MESSAGE_1C, display_text = "Message 1C" },
        new() { id = (uint)Message_Register_ID.MESSAGE_1D, display_text = "Message 1D" }
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
            id = (uint)Status_Register_ID.BOT_AFE_CB_ACTIVE_HI,
            display_text = "CB Activity",
            bit7 = ("C16", true),
            bit6 = ("C15", true),
            bit5 = ("C14", true),
            bit4 = ("C13", true),
            bit3 = ("C12", false),
            bit2 = ("C11", false),
            bit1 = ("C10", false),
            bit0 = ("C9", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_CB_ACTIVE_LO,
            display_text = "CB Activity",
            bit7 = ("C8", false),
            bit6 = ("C7", false),
            bit5 = ("C6", false),
            bit4 = ("C5", false),
            bit3 = ("C4", false),
            bit2 = ("C3", false),
            bit1 = ("C2", false),
            bit0 = ("C1", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_FET_STATUS,
            display_text = "AFE FET Status",
            bit7 = ("RSVD", true),
            bit6 = ("ALRT_PIN", false),
            bit5 = ("DDSG_PIN", false),
            bit4 = ("DCHG_PIN", false),
            bit3 = ("PDSG_FET", false),
            bit2 = ("DSG_FET", false),
            bit1 = ("PCHG_FET", false),
            bit0 = ("CHG_FET", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_BATTERY_STATUS_HI,
            display_text = "AFE Battery Status Hi",
            bit7 = ("SLEEP", false),
            bit6 = ("RSVD", true),
            bit5 = ("SDM", false),
            bit4 = ("PF", false),
            bit3 = ("SS", false),
            bit2 = ("FUSE", false),
            bit1 = ("SEC1", false),
            bit0 = ("SEC0", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_BATTERY_STATUS_LO,
            display_text = "AFE Battery Status Lo",
            bit7 = ("OTPB", false),
            bit6 = ("OTPW", false),
            bit5 = ("COW_CHK", false),
            bit4 = ("WD", false),
            bit3 = ("POR", false),
            bit2 = ("SLEEP_EN", false),
            bit1 = ("PCHG_MODE", false),
            bit0 = ("CFGUPDATE", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_ALARM_STATUS_HI,
            display_text = "AFE Alarm Status Hi",
            bit7 = ("SSBC", false),
            bit6 = ("SSA", false),
            bit5 = ("PF", false),
            bit4 = ("MSK_SALRT", false),
            bit3 = ("MSK_PALRT", false),
            bit2 = ("INITSTART", false),
            bit1 = ("INITCOMP", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_ALARM_STATUS_LO,
            display_text = "AFE Alarm Status Lo",
            bit7 = ("FULLSCAN", false),
            bit6 = ("XCHG", false),
            bit5 = ("XDSG", false),
            bit4 = ("SHUTV", false),
            bit3 = ("FUSE", false),
            bit2 = ("CB", false),
            bit1 = ("ADSCAN", false),
            bit0 = ("WAKE", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_ALARM_RAW_STATUS_HI,
            display_text = "AFE Alarm Raw Status Hi",
            bit7 = ("SSBC", false),
            bit6 = ("SSA", false),
            bit5 = ("PF", false),
            bit4 = ("MSK_SALRT", false),
            bit3 = ("MSK_PALRT", false),
            bit2 = ("INITSTART", false),
            bit1 = ("INITCOMP", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_ALARM_RAW_STATUS_LO,
            display_text = "AFE Alarm Raw Status Lo",
            bit7 = ("FULLSCAN", false),
            bit6 = ("XCHG", false),
            bit5 = ("XDSG", false),
            bit4 = ("SHUTV", false),
            bit3 = ("FUSE", false),
            bit2 = ("CB", false),
            bit1 = ("ADSCAN", false),
            bit0 = ("WAKE", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_SAFETY_ALERT_A,
            display_text = "AFE Safety Alert A",
            bit7 = ("SCD", false),
            bit6 = ("OCD2", false),
            bit5 = ("OCD1", false),
            bit4 = ("OCC", false),
            bit3 = ("COV", false),
            bit2 = ("CUV", false),
            bit1 = ("RSVD", true),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_SAFETY_ALERT_B,
            display_text = "AFE Safety Alert B",
            bit7 = ("OTF", false),
            bit6 = ("OTINT", false),
            bit5 = ("OTD", false),
            bit4 = ("OTC", false),
            bit3 = ("RSVD", true),
            bit2 = ("UTINT", false),
            bit1 = ("UTD", false),
            bit0 = ("UTC", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_SAFETY_ALERT_C,
            display_text = "AFE Safety Alert C",
            bit7 = ("OCD3", false),
            bit6 = ("SCDL", false),
            bit5 = ("OCDL", false),
            bit4 = ("COVL", false),
            bit3 = ("PTOS", false),
            bit2 = ("RSVD", true),
            bit1 = ("RSVD", true),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_SAFETY_STATUS_A,
            display_text = "AFE Safety Status A",
            bit7 = ("SCD", false),
            bit6 = ("OCD2", false),
            bit5 = ("OCD1", false),
            bit4 = ("OCC", false),
            bit3 = ("COV", false),
            bit2 = ("CUV", false),
            bit1 = ("RSVD", true),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_SAFETY_STATUS_B,
            display_text = "AFE Safety Status B",
            bit7 = ("OTF", false),
            bit6 = ("OTINT", false),
            bit5 = ("OTD", false),
            bit4 = ("OTC", false),
            bit3 = ("RSVD", true),
            bit2 = ("UTINT", false),
            bit1 = ("UTD", false),
            bit0 = ("UTC", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_SAFETY_STATUS_C,
            display_text = "AFE Safety Status C",
            bit7 = ("OCD3", false),
            bit6 = ("SCDL", false),
            bit5 = ("OCDL", false),
            bit4 = ("COVL", false),
            bit3 = ("RSVD", true),
            bit2 = ("PTO", false),
            bit1 = ("HWDF", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_PF_ALERT_A,
            display_text = "AFE PF Alert A",
            bit7 = ("CUDEP", false),
            bit6 = ("SOTF", false),
            bit5 = ("RSVD", true),
            bit4 = ("SOT", false),
            bit3 = ("SOCD", false),
            bit2 = ("SOCC", false),
            bit1 = ("SOV", false),
            bit0 = ("SUV", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_PF_ALERT_B,
            display_text = "AFE PF Alert B",
            bit7 = ("SCDL", false),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("VIMA", false),
            bit3 = ("VIMR", false),
            bit2 = ("2LVL", false),
            bit1 = ("DFETF", false),
            bit0 = ("CFETF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_PF_ALERT_C,
            display_text = "AFE PF Alert C",
            bit7 = ("RSVD", true),
            bit6 = ("HWMX", false),
            bit5 = ("VSSF", false),
            bit4 = ("VREF", false),
            bit3 = ("LFOF", false),
            bit2 = ("RSVD", true),
            bit1 = ("RSVD", true),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_PF_ALERT_D,
            display_text = "AFE PF Alert D",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("RSVD", true),
            bit2 = ("RSVD", true),
            bit1 = ("RSVD", true),
            bit0 = ("TOSF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_PF_STATUS_A,
            display_text = "AFE PF Status A",
            bit7 = ("CUDEP", false),
            bit6 = ("SOTF", false),
            bit5 = ("RSVD", true),
            bit4 = ("SOT", false),
            bit3 = ("SOCD", false),
            bit2 = ("SOCC", false),
            bit1 = ("SOV", false),
            bit0 = ("SUV", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_PF_STATUS_B,
            display_text = "AFE PF Status B",
            bit7 = ("SCDL", false),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("VIMA", false),
            bit3 = ("VIMR", false),
            bit2 = ("2LVL", false),
            bit1 = ("DFETF", false),
            bit0 = ("CFETF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_PF_STATUS_C,
            display_text = "AFE PF Status C",
            bit7 = ("CMDF", false),
            bit6 = ("HWMX", false),
            bit5 = ("VSSF", false),
            bit4 = ("VREF", false),
            bit3 = ("LFOF", false),
            bit2 = ("IRMF", false),
            bit1 = ("DRMF", false),
            bit0 = ("OTPF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_PF_STATUS_D,
            display_text = "AFE PF Status D",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("RSVD", true),
            bit2 = ("RSVD", true),
            bit1 = ("RSVD", true),
            bit0 = ("TOSF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BOT_AFE_CONTROL_STATUS_HI,
            display_text = "AFE Control Status Hi",
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
            id = (uint)Status_Register_ID.BOT_AFE_CONTROL_STATUS_LO,
            display_text = "AFE Control Status Lo",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("RSVD", true),
            bit2 = ("DEEPSLP", false),
            bit1 = ("LD_TOUT", false),
            bit0 = ("LD_ON", false)
        },
    };

    private static readonly HashSet<Query> s_query_set =
    new()
    {
        new() { id = (uint)Query_ID.MESSAGE_01, display_text = "Message 01" },
        new() { id = (uint)Query_ID.MESSAGE_02, display_text = "Message 02" },
        new() { id = (uint)Query_ID.MESSAGE_03, display_text = "Message 03" },
        new() { id = (uint)Query_ID.MESSAGE_04, display_text = "Message 04" },
        new() { id = (uint)Query_ID.MESSAGE_05, display_text = "Message 05" },
        new() { id = (uint)Query_ID.MESSAGE_06, display_text = "Message 06" },
        new() { id = (uint)Query_ID.MESSAGE_07, display_text = "Message 07" },
        new() { id = (uint)Query_ID.MESSAGE_08, display_text = "Message 08" },
        new() { id = (uint)Query_ID.MESSAGE_09, display_text = "Message 09" },
        new() { id = (uint)Query_ID.MESSAGE_0A, display_text = "Message 0A" },
        new() { id = (uint)Query_ID.MESSAGE_0B, display_text = "Message 0B" },
        new() { id = (uint)Query_ID.MESSAGE_0C, display_text = "Message 0C" },
        new() { id = (uint)Query_ID.MESSAGE_0D, display_text = "Message 0D" },
        new() { id = (uint)Query_ID.MESSAGE_0E, display_text = "Message 0E" },
        new() { id = (uint)Query_ID.MESSAGE_0F, display_text = "Message 0F" },
        new() { id = (uint)Query_ID.MESSAGE_10, display_text = "Message 10" },
        new() { id = (uint)Query_ID.MESSAGE_11, display_text = "Message 11" },
        new() { id = (uint)Query_ID.MESSAGE_12, display_text = "Message 12" },
        new() { id = (uint)Query_ID.MESSAGE_13, display_text = "Message 13" },
        new() { id = (uint)Query_ID.MESSAGE_14, display_text = "Message 14" },
        new() { id = (uint)Query_ID.MESSAGE_15, display_text = "Message 15" },
        new() { id = (uint)Query_ID.MESSAGE_16, display_text = "Message 16" },
        new() { id = (uint)Query_ID.MESSAGE_17, display_text = "Message 17" },
        new() { id = (uint)Query_ID.MESSAGE_18, display_text = "Message 18" },
        new() { id = (uint)Query_ID.MESSAGE_19, display_text = "Message 19" },
        new() { id = (uint)Query_ID.MESSAGE_1A, display_text = "Message 1A" },
        new() { id = (uint)Query_ID.MESSAGE_1B, display_text = "Message 1B" },
        //new() { id = (uint)Query_ID.MESSAGE_1C, display_text = "Message 1C" },
        new() { id = (uint)Query_ID.MESSAGE_1D, display_text = "Message 1D" },
        s_default_query
    };

    private static readonly HashSet<Command> s_command_set_advanced =
    [
        new()
        {
            id = (uint)Command_ID.SET_PERIODIC_TIME,
            display_text = "Set Periodic Time",
            arguments = [("Time (ms):", "1000")],
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.SET_SERIAL_NUMBER,
            display_text = "Set Serial Number",
            arguments = [("SN:", string.Empty)],
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.SET_ID_PREFIX,
            display_text = "Set CAN ID Prefix",
            arguments = [("18-bit prefix:", "3FFFF")],
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
            id = (uint)Command_ID.FG_LIFETIME_ENABLE,
            display_text = "Lifetime Enable",
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
            id = (uint)Command_ID.FG_UNSEAL,
            display_text = "Unseal Fuel Gauge",
            arguments = [("Key:", "17916789")],
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_UNSEAL_FULL,
            display_text = "Unseal Fuel Gauge (full)",
            arguments = [("Key:", "1791AABB")],
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_PROGRAM,
            display_text = "Program Fuel Gauge",
            response_timeout = 20_000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_CC_OFFSET,
            display_text = "Calibrate FG CC Offset",
            response_timeout = 61_000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_BOARD_OFFSET,
            display_text = "Calibrate FG Board Offset",
            response_timeout = 61_000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_VOLTAGE,
            display_text = "Calibrate FG Voltage",
            arguments = [("Applied Voltage (V):", "91.2")],
            response_timeout = 12_000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_CURRENT,
            display_text = "Calibrate FG Current",
            arguments = [("Applied Current (A):", "-2.0")],
            response_timeout = 12_000
        },
        new()
        {
            id = (uint)Command_ID.PF_ENABLE,
            display_text = "PF Enable",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.PF_DISABLE,
            display_text = "PF Disable",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.PF_RESET,
            display_text = "PF Reset",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.SAVE_FG_CAL_DATA,
            display_text = "Save FG Cal Data",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.APPLY_SAVED_FG_CAL_DATA,
            display_text = "Apply Saved FG Cal Data",
            response_timeout = 1000
        },
    ];

    private static readonly HashSet<Command> s_command_set_simple =
    [
        new()
        {
            id = (uint)Command_ID.SET_PERIODIC_TIME,
            display_text = "Set Periodic Time",
            arguments = [("Time (ms):", "1000")],
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.SET_ID_PREFIX,
            display_text = "Set CAN ID Prefix",
            arguments = [("18-bit prefix:", "3FFFF")],
            response_timeout = 1000
        },
    ];

    private const uint ID_PREFIX_MASK = 0b0001_1111_1111_1111_1111_1000_0000_0000u;

    public
    GE_Healthcare
    (Config_Data a_config) :
    base()
    {
        var a_table = Toml.Parse(a_config.config_file_text).ToModel();

        var a_gehealthcare_tab = (TomlTable)a_table["gehealthcare"];

        m_advanced_mode = (bool)a_gehealthcare_tab["advanced-mode"];

        var a_prefix = ((long)a_gehealthcare_tab["default-id-prefix"]) << 11;

        m_id_prefix = checked((uint)a_prefix);

        if((m_id_prefix & (~ID_PREFIX_MASK)) is not 0)
        {
            throw new ArgumentOutOfRangeException(nameof(a_config), "invalid default-id-prefix");
        }
    }

    private readonly bool m_advanced_mode;
    private uint m_id_prefix;

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
        if(!a_id.is_ext_id || a_id.is_remote || a_id.is_can_fd)
        {
            return;
        }

        if((a_id.id & 0b100_0000_0000u) is not 0b100_0000_0000u)
        {
            return;
        }

        m_id_prefix = a_id.id & ID_PREFIX_MASK;

        var a_pck = (a_id.id & 0b000_0000_0011u) >> 0;
        var a_msg = (a_id.id & 0b011_1111_1100u) >> 2;

        if(a_msg is 0x07u)
        {
            var a_seven_data = parse_message_07(a_data);

            if(a_seven_data is null)
            {
                return;
            }

            var (a_seven_data_a, a_seven_data_b) = a_seven_data.Value;

            {
                using var a_g1 = String_Builder_Pool.acquire();

                add_mess_register_parsed
                (
                    message_register_map[(uint)Message_Register_ID.MESSAGE_07_I],
                    new(a_id, a_data)
                    {
                        id_interpreted = a_g1.value.Append($"PCK={a_pck} MSG={a_msg:X2}").ToString(),
                        data_interpreted = a_seven_data_a
                    }
                );
            }

            {
                using var a_g1 = String_Builder_Pool.acquire();

                add_mess_register_parsed
                (
                    message_register_map[(uint)Message_Register_ID.MESSAGE_07_II],
                    new(a_id, a_data)
                    {
                        id_interpreted = a_g1.value.Append($"PCK={a_pck} MSG={a_msg:X2}").ToString(),
                        data_interpreted = a_seven_data_b
                    }
                );
            }

            return;
        }

        var a_data_parsed =
        a_msg switch
        {
            0x00u => parse_command_response(a_data),
            0x01u => parse_message_01(a_data),
            0x02u => parse_message_02(a_data),
            0x03u => parse_message_03(a_data),
            0x04u => parse_message_04(a_data),
            0x05u => parse_message_05(a_data),
            0x06u => parse_message_06(a_data),
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
            //0x1Cu => parse_message_1C(a_data),
            0x1Du => parse_message_1D(a_data),
            _ => null
        };

        if(a_data_parsed is null)
        {
            return;
        }

        {
            using var a_g1 = String_Builder_Pool.acquire();

            add_mess_register_parsed
            (
                message_register_map[a_msg],
                new(a_id, a_data)
                {
                    id_interpreted = a_g1.value.Append($"PCK={a_pck} MSG={a_msg:X2}").ToString(),
                    data_interpreted = a_data_parsed
                }
            );
        }
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
                    id_interpreted = a_g1.value.Append($"PCK={a_pck} MSG={a_msg:X2}").ToString(),
                    data_interpreted = a_g2.value.Append($"Query: Message {a_msg:X2}").ToString()
                }
            );
        }

        var a_query_id = (Query_ID)a_query.id;

        switch(a_query_id)
        {
            case Query_ID.MESSAGE_01: { add_query(a_dest, 0x01u); } break;
            case Query_ID.MESSAGE_02: { add_query(a_dest, 0x02u); } break;
            case Query_ID.MESSAGE_03: { add_query(a_dest, 0x03u); } break;
            case Query_ID.MESSAGE_04: { add_query(a_dest, 0x04u); } break;
            //case Query_ID.MESSAGE_05: { add_query(a_dest, 0x05u); } break;
            //case Query_ID.MESSAGE_06: { add_query(a_dest, 0x06u); } break;
            case Query_ID.MESSAGE_07: { add_query(a_dest, 0x07u); } break;
            case Query_ID.MESSAGE_08: { add_query(a_dest, 0x08u); } break;
            case Query_ID.MESSAGE_09: { add_query(a_dest, 0x09u); } break;
            case Query_ID.MESSAGE_0A: { add_query(a_dest, 0x0Au); } break;
            case Query_ID.MESSAGE_0B: { add_query(a_dest, 0x0Bu); } break;
            case Query_ID.MESSAGE_0C: { add_query(a_dest, 0x0Cu); } break;
            case Query_ID.MESSAGE_0D: { add_query(a_dest, 0x0Du); } break;
            case Query_ID.MESSAGE_0E: { add_query(a_dest, 0x0Eu); } break;
            case Query_ID.MESSAGE_0F: { add_query(a_dest, 0x0Fu); } break;
            case Query_ID.MESSAGE_10: { add_query(a_dest, 0x10u); } break;
            case Query_ID.MESSAGE_11: { add_query(a_dest, 0x11u); } break;
            case Query_ID.MESSAGE_12: { add_query(a_dest, 0x12u); } break;
            case Query_ID.MESSAGE_13: { add_query(a_dest, 0x13u); } break;
            case Query_ID.MESSAGE_14: { add_query(a_dest, 0x14u); } break;
            case Query_ID.MESSAGE_15: { add_query(a_dest, 0x15u); } break;
            case Query_ID.MESSAGE_16: { add_query(a_dest, 0x16u); } break;
            case Query_ID.MESSAGE_17: { add_query(a_dest, 0x17u); } break;
            case Query_ID.MESSAGE_18: { add_query(a_dest, 0x18u); } break;
            case Query_ID.MESSAGE_19: { add_query(a_dest, 0x19u); } break;
            case Query_ID.MESSAGE_1A: { add_query(a_dest, 0x1Au); } break;
            case Query_ID.MESSAGE_1B: { add_query(a_dest, 0x1Bu); } break;
            //case Query_ID.MESSAGE_1C: { add_query(a_dest, 0x1Cu); } break;
            case Query_ID.MESSAGE_1D: { add_query(a_dest, 0x1Du); } break;
            case Query_ID.ALL:
            {
                const uint MSG = 0x00u;
                const ushort CMD = 0x0001;

                Span<byte> a_data = stackalloc byte[2];
                var a_index = 0;

                Misc.encode_le(CMD, a_data, ref a_index);

                using var a_g1 = String_Builder_Pool.acquire();
                using var a_g2 = String_Builder_Pool.acquire();

                add_outgoing_can_message
                (
                    new(compute_outgoing_id(a_dest, MSG, a_data.Length, out var a_pck), a_data)
                    {
                        id_interpreted = a_g1.value.Append($"PCK={a_pck} MSG={MSG:X2}").ToString(),
                        data_interpreted = a_g2.value.Append($"Command 0x{CMD:X4}: Query All").ToString()
                    }
                );
            }
            break;
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
            const uint MSG = 0x00u;

            using var a_g1 = String_Builder_Pool.acquire();
            using var a_g2 = String_Builder_Pool.acquire();

            add_outgoing_can_message
            (
                new(compute_outgoing_id(a_dest, MSG, a_data.Length, out var a_pck), a_data)
                {
                    id_interpreted = a_g1.value.Append($"PCK={a_pck} MSG={MSG:X2}").ToString(),
                    data_interpreted = a_g2.value.Append($"Command 0x{a_cmd:X4}: {a_command.display_text}").ToString()
                }
            );
        }

        var a_command_id = (Command_ID)a_command.id;

        var (a_cmd, a_data) =
            a_command_id switch
            {
                Command_ID.ENTER_BOOTLOADER => process_enter_bootloader(),
                Command_ID.SET_PERIODIC_TIME => process_set_periodic_time(a_args[0]),
                Command_ID.SET_SERIAL_NUMBER => process_set_serial_number(a_args[0]),
                Command_ID.SET_ID_PREFIX => process_set_id_prefix(a_args[0]),
                Command_ID.FG_RESET => process_fg_reset(),
                Command_ID.FG_LIFETIME_ENABLE => process_fg_lifetime_enable(),
                Command_ID.FG_SEAL => process_fg_seal(),
                Command_ID.FG_UNSEAL => process_fg_unseal(a_args[0]),
                Command_ID.FG_UNSEAL_FULL => process_fg_unseal_full(a_args[0]),
                Command_ID.FG_PROGRAM => process_fg_program(),
                Command_ID.FG_CAL_CC_OFFSET => process_fg_cal_cc_offset(),
                Command_ID.FG_CAL_BOARD_OFFSET => process_fg_cal_board_offset(),
                Command_ID.FG_CAL_VOLTAGE => process_fg_cal_voltage(a_args[0]),
                Command_ID.FG_CAL_CURRENT => process_fg_cal_current(a_args[0]),
                Command_ID.PF_ENABLE => process_pf_enable_disable(true),
                Command_ID.PF_DISABLE => process_pf_enable_disable(false),
                Command_ID.PF_RESET => process_pf_reset(),
                Command_ID.SAVE_FG_CAL_DATA => process_save_fg_cal_data(),
                Command_ID.APPLY_SAVED_FG_CAL_DATA => process_apply_saved_fg_cal_data(),
                _ => throw new ArgumentOutOfRangeException(nameof(a_command))
            };

        add_command(a_dest, a_command, a_cmd, a_data);
    }

    #region MESSAGES

    private static string?
    parse_message_01
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out short a_v1, a_data, ref a_index);
        Misc.decode_le(out short a_v2, a_data, ref a_index);
        Misc.decode_le(out short a_v3, a_data, ref a_index);
        Misc.decode_le(out short a_v4, a_data, ref a_index);

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
    parse_message_02
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out short a_v1, a_data, ref a_index);
        Misc.decode_le(out short a_v2, a_data, ref a_index);
        Misc.decode_le(out short a_v3, a_data, ref a_index);
        Misc.decode_le(out short a_v4, a_data, ref a_index);

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
    parse_message_03
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out short a_v1, a_data, ref a_index);
        Misc.decode_le(out short a_v2, a_data, ref a_index);
        Misc.decode_le(out short a_v3, a_data, ref a_index);
        Misc.decode_le(out short a_v4, a_data, ref a_index);

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
    parse_message_04
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out short a_v1, a_data, ref a_index);
        Misc.decode_le(out short a_v2, a_data, ref a_index);
        Misc.decode_le(out short a_v3, a_data, ref a_index);
        Misc.decode_le(out short a_v4, a_data, ref a_index);

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
    parse_message_05
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
            .Append($"Temp1={to_celcius(a_v1):F1}°C; ")
            .Append($"Temp2={to_celcius(a_v2):F1}°C; ")
            .Append($"Temp3={to_celcius(a_v3):F1}°C; ")
            .Append($"TempB={to_celcius(a_v4):F1}°C; ")
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

        Misc.decode_le(out int a_v1, a_data, ref a_index);
        Misc.decode_le(out int a_v2, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Pack Volt: {0.001 * a_v1:F3}V; ")
            .Append($"Charger Volt: {0.001 * a_v2:F3}V; ")
            .ToString();
        return a_result;
    }

    private static (string, string)?
    parse_message_07
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_w1, a_data, ref a_index);
        Misc.decode_le(out uint a_w2, a_data, ref a_index);

        var a_curr = unchecked((int)a_w1) >> 14;
        var a_soc_range = (a_w1 >> 12) & 0b11u;
        var a_warning_status = (a_w1 >> 7) & 0b11111u;
        var a_soc = (a_w1 >> 0) & 0b1111111u;

        var a_volt = (a_w2 >> 15) & 0b11111111111111111u;
        var a_state = (a_w2 >> 13) & 0b11u;
        var a_fault = (a_w2 >> 12) & 0b1u;
        var a_temp = (a_w2 >> 0) & 0b111111111111u;

        using var a_g1 = String_Builder_Pool.acquire();
        using var a_g2 = String_Builder_Pool.acquire();

        var a_result_a =
            a_g1.value
            .Append($"Battery Volt: {0.001 * a_volt:F3}V; ")
            .Append($"Current: {0.001 * a_curr:F3}A; ")
            .Append($"State of Charge: {a_soc}%; ")
            .Append($"Pack Temp: {to_celcius((ushort)a_temp):F1}°C; ")
            .ToString();

        var a_result_b =
            a_g2.value
            .Append($"State: 0b{Convert.ToString(a_state, 2).PadLeft(2, '0')}; ")
            .Append($"Fault: 0b{Convert.ToString(a_fault, 2).PadLeft(1, '0')}; ")
            .Append($"SoC Range: 0b{Convert.ToString(a_soc_range, 2).PadLeft(2, '0')}; ")
            .Append($"Warning status: 0b{Convert.ToString(a_warning_status, 2).PadLeft(5, '0')}; ")
            .ToString();

        return (a_result_a, a_result_b);
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

        Misc.decode_le(out ushort a_uc_version, a_data, ref a_index);
        Misc.decode_le(out ushort a_fg_version, a_data, ref a_index);
        Misc.decode_le(out ushort a_serial, a_data, ref a_index);
        Misc.decode_le(out ushort a_dfet_temp, a_data, ref a_index);

        var a_fw_vmajor = (a_uc_version & 0b1111110000000000) >> 10;
        var a_fw_vminor = (a_uc_version & 0b0000001111110000) >> 4;
        var a_fw_rev =    (a_uc_version & 0b0000000000001111) >> 0;

        var a_fg_vmajor = (a_fg_version & 0b1111110000000000) >> 10;
        var a_fg_vminor = (a_fg_version & 0b0000001111110000) >> 4;
        var a_fg_rev =    (a_fg_version & 0b0000000000001111) >> 0;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
        a_g1.value
        .Append($"µC Firmware Ver: {a_fw_vmajor}.{a_fw_vminor}.{a_fw_rev}; ")
        .Append($"FG Config Ver: {a_fg_vmajor}.{a_fg_vminor}.{a_fg_rev}; ")
        .Append($"SN: {a_serial:D5}; ")
        .Append($"DFET Temp: {to_celcius(a_dfet_temp):F1}°C; ")
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

        Misc.decode_le(out int a_afe_volt, a_data, ref a_index);
        Misc.decode_le(out int a_afe_curr, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"AFE Volt: {0.001 * a_afe_volt:F3}V; ")
            .Append($"AFE Curr: {0.001 * a_afe_curr:F3}A; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_0A
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out int a_fg_avg_curr, a_data, ref a_index);
        Misc.decode_le(out ushort a_fg_rc, a_data, ref a_index);
        Misc.decode_le(out ushort a_fg_fcc, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"FG Avg Curr: {0.001 * a_fg_avg_curr:F3}A; ")
            .Append($"Remain Cap: {0.001 * a_fg_rc:F3}Ah; ")
            .Append($"Full Charge Cap: {0.001 * a_fg_fcc:F3}Ah; ")
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

        Misc.decode_le(out ushort a_tte, a_data, ref a_index);
        Misc.decode_le(out ushort a_ttf, a_data, ref a_index);
        Misc.decode_le(out ushort a_soh, a_data, ref a_index);
        Misc.decode_le(out ushort a_cycle_count, a_data, ref a_index);

        var a_tte_str = a_tte is 0xFFFF ? "N/A" : a_tte.ToString();
        var a_ttf_str = a_ttf is 0xFFFF ? "N/A" : a_ttf.ToString();

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Time to Empty: {a_tte_str} min; ")
            .Append($"Time to Full: {a_ttf_str} min; ")
            .Append($"State of Health: {a_soh}%; ")
            .Append($"Cycle Count: {a_cycle_count}; ")
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

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_CONTROL_STATUS_HI], unchecked((byte)(a_control_status >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_CONTROL_STATUS_LO], unchecked((byte)(a_control_status >> 0)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_FLAGS_A_HI], unchecked((byte)(a_flags_a >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_FLAGS_A_LO], unchecked((byte)(a_flags_a >> 0)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_FLAGS_B_HI], unchecked((byte)(a_flags_b >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_FLAGS_B_LO], unchecked((byte)(a_flags_b >> 0)));

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

        Misc.decode_le(out ushort a_voltage_div, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_internal, a_data, ref a_index);
        Misc.decode_le(out ushort a_lt_max_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_lt_min_temp, a_data, ref a_index);
        

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Voltage Divider: {a_voltage_div}; ")
            .Append($"FG Internal Temp: {to_celcius(a_temp_internal):F1}°C; ")
            .Append($"LT Max Temp: {to_celcius(a_lt_max_temp):F1}°C; ")
            .Append($"LT Min Temp: {to_celcius(a_lt_min_temp):F1}°C; ")
            
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

        Misc.decode_le(out uint a_lt_max_volt, a_data, ref a_index);
        Misc.decode_le(out uint a_lt_min_volt, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"LT Max Volt: {0.001 * a_lt_max_volt:F3}V; ")
            .Append($"LT Min Volt: {0.001 * a_lt_min_volt:F3}V; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_0F
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_lt_max_chg_curr, a_data, ref a_index);
        Misc.decode_le(out uint a_lt_min_dsg_curr, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"LT Max Chg Curr: {0.001 * a_lt_max_chg_curr:F3}A; ")
            .Append($"LT Max Dsg Curr: {0.001 * a_lt_min_dsg_curr:F3}A; ")
            .ToString();

        return a_result;
    }

    private string?
    parse_message_10
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out short a_volt_delta, a_data, ref a_index);
        Misc.decode_le(out ushort a_cb_cells_bot, a_data, ref a_index);
        Misc.decode_le(out ushort a_cb_cells_top, a_data, ref a_index);
        Misc.decode_le(out byte a_fet_status_bot, a_data, ref a_index);
        Misc.decode_le(out byte a_fet_status_top, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Cell Volt Δ: {a_volt_delta}mV; ")
            .Append($"CB Activity Bot: 0x{a_cb_cells_bot:X4}; ")
            .Append($"FET Status Bot: 0x{a_fet_status_bot:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_CB_ACTIVE_HI], unchecked((byte)(a_cb_cells_bot >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_CB_ACTIVE_LO], unchecked((byte)(a_cb_cells_bot >> 0)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_FET_STATUS], a_fet_status_bot);

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

        Misc.decode_le(out short a_cell_min_volt, a_data, ref a_index);
        Misc.decode_le(out short a_cell_max_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_int_bot, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_int_top, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Cell Min Volt: {0.001 * a_cell_min_volt:F3}V; ")
            .Append($"Cell Max Volt: {0.001 * a_cell_max_volt:F3}V; ")
            .Append($"AFE Int Temp: {to_celcius(a_temp_int_bot):F1}°C; ")
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

        Misc.decode_le(out ushort a_bot_t1, a_data, ref a_index);
        Misc.decode_le(out ushort a_bot_t2, a_data, ref a_index);
        Misc.decode_le(out ushort a_top_t1, a_data, ref a_index);
        Misc.decode_le(out ushort a_top_t2, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"AFE Temp1: {to_celcius(a_bot_t1):F1}°C; ")
            .Append($"AFE Temp2: {to_celcius(a_bot_t2):F1}°C; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_13
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out int a_bot_volt, a_data, ref a_index);
        Misc.decode_le(out int a_top_volt, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"AFE Stack Volt: {0.001 * a_bot_volt:F3}V; ")
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

        Misc.decode_le(out int a_bot_volt, a_data, ref a_index);
        Misc.decode_le(out int a_top_volt, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"AFE Pack Volt: {0.001 * a_bot_volt:F3}V; ")
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

        Misc.decode_le(out int a_bot_volt, a_data, ref a_index);
        Misc.decode_le(out int a_top_volt, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"AFE Load Detect Volt: {0.001 * a_bot_volt:F3}V; ")
            .ToString();

        return a_result;
    }

    private string?
    parse_message_16
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_bot_control_stat, a_data, ref a_index);
        Misc.decode_le(out ushort a_top_control_stat, a_data, ref a_index);
        Misc.decode_le(out ushort a_bot_battery_stat, a_data, ref a_index);
        Misc.decode_le(out ushort a_top_battery_stat, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"AFE Control Stat: 0x{a_bot_control_stat:X4}; ")
            .Append($"AFE Battery Stat 0x{a_bot_battery_stat:X4}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_CONTROL_STATUS_HI], unchecked((byte)(a_bot_control_stat >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_CONTROL_STATUS_LO], unchecked((byte)(a_bot_control_stat >> 0)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_BATTERY_STATUS_HI], unchecked((byte)(a_bot_battery_stat >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_BATTERY_STATUS_LO], unchecked((byte)(a_bot_battery_stat >> 0)));

        return a_result;
    }

    private string?
    parse_message_17
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_bot_alarm_stat, a_data, ref a_index);
        Misc.decode_le(out ushort a_top_alarm_stat, a_data, ref a_index);
        Misc.decode_le(out ushort a_bot_alarm_raw_stat, a_data, ref a_index);
        Misc.decode_le(out ushort a_top_alarm_raw_stat, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"AFE Alarm Stat: 0x{a_bot_alarm_stat:X4}; ")
            .Append($"AFE Alarm Raw Stat 0x{a_bot_alarm_raw_stat:X4}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_ALARM_STATUS_HI], unchecked((byte)(a_bot_alarm_stat >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_ALARM_STATUS_LO], unchecked((byte)(a_bot_alarm_stat >> 0)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_ALARM_RAW_STATUS_HI], unchecked((byte)(a_bot_alarm_raw_stat >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_ALARM_RAW_STATUS_LO], unchecked((byte)(a_bot_alarm_raw_stat >> 0)));

        return a_result;
    }

    private string?
    parse_message_18
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_fg_control_status, a_data, ref a_index);
        Misc.decode_le(out byte a_bot_sft_alrt_a, a_data, ref a_index);
        Misc.decode_le(out byte a_top_sft_alrt_a, a_data, ref a_index);
        Misc.decode_le(out byte a_bot_sft_alrt_b, a_data, ref a_index);
        Misc.decode_le(out byte a_top_sft_alrt_b, a_data, ref a_index);
        Misc.decode_le(out byte a_bot_sft_alrt_c, a_data, ref a_index);
        Misc.decode_le(out byte a_top_sft_alrt_c, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"SA-A: 0x{a_bot_sft_alrt_a:X2}; ")
            .Append($"SA-B: 0x{a_bot_sft_alrt_b:X2}; ")
            .Append($"SA-C: 0x{a_bot_sft_alrt_c:X2}; ")
            .Append($"FG Ctrl Stat: 0x{a_fg_control_status:X4}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_CONTROL_STATUS_HI], unchecked((byte)(a_fg_control_status >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.FG_CONTROL_STATUS_LO], unchecked((byte)(a_fg_control_status >> 0)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_SAFETY_ALERT_A], a_bot_sft_alrt_a);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_SAFETY_ALERT_B], a_bot_sft_alrt_b);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_SAFETY_ALERT_C], a_bot_sft_alrt_c);

        return a_result;
    }

    private string?
    parse_message_19
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 7 and not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_bot_sft_stat_a, a_data, ref a_index);
        Misc.decode_le(out byte a_top_sft_stat_a, a_data, ref a_index);
        Misc.decode_le(out byte a_bot_sft_stat_b, a_data, ref a_index);
        Misc.decode_le(out byte a_top_sft_stat_b, a_data, ref a_index);
        Misc.decode_le(out byte a_bot_sft_stat_c, a_data, ref a_index);
        Misc.decode_le(out byte a_top_sft_stat_c, a_data, ref a_index);
        Misc.decode_le(out byte a_pf_enabled, a_data, ref a_index);
        

        using var a_g1 = String_Builder_Pool.acquire();

        _ =
        a_g1.value
        .Append($"SS-A: 0x{a_bot_sft_stat_a:X2}; ")
        .Append($"SS-B: 0x{a_bot_sft_stat_b:X2}; ")
        .Append($"SS-C: 0x{a_bot_sft_stat_c:X2}; ")
        .Append($"PF Enabled: {a_pf_enabled is not 0}; ");

        if(a_data.Length is 8)
        {
            Misc.decode_le(out byte a_fg_cal_data_saved, a_data, ref a_index);

            _ = a_g1.value.Append($"FG Cal Data Saved: {a_fg_cal_data_saved is not 0}; ");
        }

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_SAFETY_STATUS_A], a_bot_sft_stat_a);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_SAFETY_STATUS_B], a_bot_sft_stat_b);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_SAFETY_STATUS_C], a_bot_sft_stat_c);

        return a_g1.value.ToString();
    }

    private string?
    parse_message_1A
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_bot_pf_alrt_a, a_data, ref a_index);
        Misc.decode_le(out byte a_top_pf_alrt_a, a_data, ref a_index);
        Misc.decode_le(out byte a_bot_pf_alrt_b, a_data, ref a_index);
        Misc.decode_le(out byte a_top_pf_alrt_b, a_data, ref a_index);
        Misc.decode_le(out byte a_bot_pf_alrt_c, a_data, ref a_index);
        Misc.decode_le(out byte a_top_pf_alrt_c, a_data, ref a_index);
        Misc.decode_le(out byte a_bot_pf_alrt_d, a_data, ref a_index);
        Misc.decode_le(out byte a_top_pf_alrt_d, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PA-A: 0x{a_bot_pf_alrt_a:X2}; ")
            .Append($"PA-B: 0x{a_bot_pf_alrt_b:X2}; ")
            .Append($"PA-C: 0x{a_bot_pf_alrt_c:X2}; ")
            .Append($"PA-D: 0x{a_bot_pf_alrt_d:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_PF_ALERT_A], a_bot_pf_alrt_a);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_PF_ALERT_B], a_bot_pf_alrt_b);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_PF_ALERT_C], a_bot_pf_alrt_c);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_PF_ALERT_D], a_bot_pf_alrt_d);

        return a_result;
    }

    private string?
    parse_message_1B
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_bot_pf_stat_a, a_data, ref a_index);
        Misc.decode_le(out byte a_top_pf_stat_a, a_data, ref a_index);
        Misc.decode_le(out byte a_bot_pf_stat_b, a_data, ref a_index);
        Misc.decode_le(out byte a_top_pf_stat_b, a_data, ref a_index);
        Misc.decode_le(out byte a_bot_pf_stat_c, a_data, ref a_index);
        Misc.decode_le(out byte a_top_pf_stat_c, a_data, ref a_index);
        Misc.decode_le(out byte a_bot_pf_stat_d, a_data, ref a_index);
        Misc.decode_le(out byte a_top_pf_stat_d, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"PS-A: 0x{a_bot_pf_stat_a:X2}; ")
            .Append($"PS-B: 0x{a_bot_pf_stat_b:X2}; ")
            .Append($"PS-C: 0x{a_bot_pf_stat_c:X2}; ")
            .Append($"PS-D: 0x{a_bot_pf_stat_d:X2}; ")
            .ToString();

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_PF_STATUS_A], a_bot_pf_stat_a);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_PF_STATUS_B], a_bot_pf_stat_b);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_PF_STATUS_C], a_bot_pf_stat_c);
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BOT_AFE_PF_STATUS_D], a_bot_pf_stat_d);

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

        Misc.decode_le(out ushort a_heater_curr, a_data, ref a_index);
        Misc.decode_le(out byte a_heater_state, a_data, ref a_index);
        Misc.decode_le(out byte a_heater_mode, a_data, ref a_index);
        Misc.decode_le(out ushort a_limit_lo, a_data, ref a_index);
        Misc.decode_le(out ushort a_limit_hi, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Heater Monitor: {0.001 * a_heater_curr:F3}V; ")
            .Append($"Heater State: {(a_heater_state is 0 ? "Off" : "On")}; ")
            .Append($"Heater Mode: {(a_heater_mode is 0 ? "Manual" : "Auto")}; ")
            .Append($"Heater Lo Lim: {(double)(a_limit_lo) / 10:F1}°K; ")
            .Append($"Heater Hi Lim: {(double)(a_limit_hi) / 10:F1}°K; ")
            .ToString();

        return a_result;
    }

    private static string?
    parse_message_1D
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_serial, a_data, ref a_index);
        Misc.decode_le(out ushort a_uc_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_uc_vref, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Full SN: {a_serial:D10}; ")
            .Append($"μC Temp: {to_celcius(a_uc_temp):F1}°C; ")
            .Append($"μC ADC Vref: {0.001 * a_uc_vref:F3}V; ")
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
            a_cmd switch
            {
                0x0002 => parse_set_periodic_time(a_data, ref a_index),
                0x0003 => parse_heater_off_on_auto(a_data, ref a_index),
                0x0004 => parse_heater_limits(a_data, ref a_index),
                0x0005 => parse_set_serial_number(a_data, ref a_index),
                0x0006 => parse_set_id_prefix(a_data, ref a_index),
                0x0007 => parse_fg_reset(a_data),
                0x0008 => parse_fg_lifetime_enable(a_data),
                0x0009 => parse_fg_seal(a_data),
                0x000A => parse_fg_unseal(a_data),
                0x000B => parse_fg_unseal_full(a_data),
                0x000C => parse_fg_program(a_data, ref a_index),
                0x000D => parse_fg_cal_cc_offset(a_data, ref a_index),
                0x000E => parse_fg_cal_board_offset(a_data, ref a_index),
                0x000F => parse_fg_cal_voltage(a_data, ref a_index),
                0x0010 => parse_fg_cal_current(a_data, ref a_index),
                0x0011 => parse_pf_enable_disable(a_data, ref a_index),
                0x0012 => parse_pf_reset(a_data),
                0x0013 => parse_save_fg_cal_data(a_data),
                0x0014 => parse_apply_saved_fg_cal_data(a_data),
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
        const ushort CMD = 0x0000;

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

    private static string?
    parse_set_periodic_time
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 4)
        {
            return null;
        }

        const ushort CMD = 0x0002;

        Misc.decode_le(out ushort a_period, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: send interval set to {a_period} ms; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_heater_off_on_auto
    (byte a_code)
    {
        const ushort CMD = 0x0003;

        var a_data = new byte[3];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le(a_code, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_heater_off_on_auto
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 3)
        {
            return null;
        }

        const ushort CMD = 0x0003;

        Misc.decode_le(out byte a_code, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var sRespStr = ((a_code == 4) || (a_code == 5)) ? "Inflight charge allowed" : "heater mode";
        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: {sRespStr} set to 0x{a_code:X2}; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_heater_limits
    (string a_arg0, string a_arg1)
    {
        const ushort CMD = 0x0004;
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

    private static string?
    parse_heater_limits
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 6)
        {
            return null;
        }

        const ushort CMD = 0x0004;

        Misc.decode_le(out ushort a_lo, a_data, ref a_index);
        Misc.decode_le(out ushort a_hi, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: heater limits set to [{to_celcius(a_lo):F1}, {to_celcius(a_hi):F1}]°C; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_set_serial_number
    (string a_arg0)
    {
        const ushort CMD = 0x0005;

        var a_sn = uint.Parse(a_arg0, NumberStyles.None);
        var a_data = new byte[8];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le((ushort)0, a_data, ref a_index);
        Misc.encode_le(a_sn, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_set_serial_number
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        const ushort CMD = 0x0005;

        Misc.decode_le(out ushort _, a_data, ref a_index);
        Misc.decode_le(out uint a_serial, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: serial number set to {a_serial:D10}; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_set_id_prefix
    (string a_arg0)
    {
        const ushort CMD = 0x0006;
        const uint PREFIX_MAX = (1u << 18) - 1;
        const uint UPPER_MASK = ((1u << 13) - 1) << 5;

        var a_prefix = uint.Parse(a_arg0, NumberStyles.AllowHexSpecifier);
        var a_data = new byte[8];
        var a_index = 0;

        if(a_prefix > PREFIX_MAX)
        {
            throw new ArgumentException($"CAN ID Prefix: must be an 18-bit value (no greater than {PREFIX_MAX:X8})");
        }

        if((a_prefix & UPPER_MASK) is 0)
        {
            throw new ArgumentException($"CAN ID Prefix: upper 13 bits of 18-bit prefix must not be all 0s");
        }

        a_prefix <<= 11;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le((ushort)0, a_data, ref a_index);
        Misc.encode_le(a_prefix, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_set_id_prefix
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 8)
        {
            return null;
        }

        const ushort CMD = 0x0006;
        const uint PREFIX_MAX = (1u << 18) - 1;

        Misc.decode_le(out ushort _, a_data, ref a_index);
        Misc.decode_le(out uint a_prefix, a_data, ref a_index);

        a_prefix >>= 11;
        
        if(a_prefix is > PREFIX_MAX)
        {
            return null;
        }

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: id prefix set to 0x{a_prefix:X8}; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_reset()
    {
        const ushort CMD = 0x0007;

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

        const ushort CMD = 0x0007;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: fuel gauge reset; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_lifetime_enable()
    {
        const ushort CMD = 0x0008;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_lifetime_enable
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = 0x0008;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: fuel gauge lifetime enable; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_seal()
    {
        const ushort CMD = 0x0009;

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

        const ushort CMD = 0x0009;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: fuel gauge seal; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_unseal
    (string a_arg0)
    {
        const ushort CMD = 0x000A;

        var a_key = uint.Parse(a_arg0, NumberStyles.AllowHexSpecifier);
        var a_data = new byte[8];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le((ushort)0, a_data, ref a_index);
        Misc.encode_le(a_key, a_data, ref a_index);

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

        const ushort CMD = 0x000A;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: fuel gauge unseal; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_unseal_full
    (string a_arg0)
    {
        const ushort CMD = 0x000B;

        var a_key = uint.Parse(a_arg0, NumberStyles.AllowHexSpecifier);
        var a_data = new byte[8];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le((ushort)0, a_data, ref a_index);
        Misc.encode_le(a_key, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_unseal_full
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = 0x000B;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: fuel gauge full unseal; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_program()
    {
        const ushort CMD = 0x000C;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_program
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 3)
        {
            return null;
        }

        const ushort CMD = 0x000C;

        Misc.decode_le(out byte a_success, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Program FG: {(a_success is not 0 ? "SUCCESS" : "FAILURE")}; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_cal_cc_offset()
    {
        const ushort CMD = 0x000D;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_cal_cc_offset
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 3)
        {
            return null;
        }

        const ushort CMD = 0x000D;

        Misc.decode_le(out byte a_success, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Calibrate FG CC Offset: {(a_success is not 0 ? "SUCCESS" : "FAILURE")}; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_cal_board_offset()
    {
        const ushort CMD = 0x000E;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_cal_board_offset
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 3)
        {
            return null;
        }

        const ushort CMD = 0x000E;

        Misc.decode_le(out byte a_success, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Calibrate FG Board Offset: {(a_success is not 0 ? "SUCCESS" : "FAILURE")}; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_cal_voltage
    (string a_arg0)
    {
        const ushort CMD = 0x000F;
        const double MIN_LIMIT = 72.0;
        const double MAX_LIMIT = 100.8;

        var a_volt = double.Parse(a_arg0, NumberStyles.Float);

        if(a_volt is < MIN_LIMIT or > MAX_LIMIT)
        {
            throw new ArgumentException($"Calibrate Voltage: voltage ({a_volt:F3}V) must be >= {MIN_LIMIT:F3}V and <= {MAX_LIMIT:F3}V");
        }

        var a_data = new byte[8];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le((ushort)0, a_data, ref a_index);
        Misc.encode_le((uint)(1000.0 * a_volt), a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_cal_voltage
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 3)
        {
            return null;
        }

        const ushort CMD = 0x000F;

        Misc.decode_le(out byte a_success, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Calibrate FG Voltage: {(a_success is not 0 ? "SUCCESS" : "FAILURE")}; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_fg_cal_current
    (string a_arg0)
    {
        const ushort CMD = 0x0010;
        const double MIN_LIMIT = -10.0;
        const double MAX_LIMIT = -1.0;

        var a_curr = double.Parse(a_arg0, NumberStyles.Float);

        if(a_curr is < MIN_LIMIT or > MAX_LIMIT)
        {
            throw new ArgumentException($"Calibrate Current: current ({a_curr:F3}A) must be >= {MIN_LIMIT:F3}A and <= {MAX_LIMIT:F3}A");
        }

        var a_data = new byte[8];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le((ushort)0, a_data, ref a_index);
        Misc.encode_le((uint)(1000.0 * a_curr), a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_fg_cal_current
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 3)
        {
            return null;
        }

        const ushort CMD = 0x0010;

        Misc.decode_le(out byte a_success, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Calibrate FG Current: {(a_success is not 0 ? "SUCCESS" : "FAILURE")}; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_pf_enable_disable
    (bool a_enable)
    {
        const ushort CMD = 0x0011;

        var a_data = new byte[3];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);
        Misc.encode_le((byte)(a_enable ? 1 : 0), a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_pf_enable_disable
    (in ReadOnlySpan<byte> a_data, ref int a_index)
    {
        if(a_data.Length is not 3)
        {
            return null;
        }

        const ushort CMD = 0x0011;

        Misc.decode_le(out byte a_enabled, a_data, ref a_index);

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: PF {(a_enabled is not 0 ? "enabled" : "disabled")}; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_pf_reset()
    {
        const ushort CMD = 0x0012;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_pf_reset
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = 0x0012;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: PF reset; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_save_fg_cal_data()
    {
        const ushort CMD = 0x0013;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_save_fg_cal_data
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = 0x0013;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Save FG Calibration Data; ")
            .ToString();

        return a_result;
    }

    private static (ushort a_cmd, byte[] a_data)
    process_apply_saved_fg_cal_data()
    {
        const ushort CMD = 0x0014;

        var a_data = new byte[2];
        var a_index = 0;

        Misc.encode_le(CMD, a_data, ref a_index);

        return (CMD, a_data);
    }

    private static string?
    parse_apply_saved_fg_cal_data
    (in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 2)
        {
            return null;
        }

        const ushort CMD = 0x0014;

        using var a_g1 = String_Builder_Pool.acquire();

        var a_result =
            a_g1.value
            .Append($"Command 0x{CMD:X4} Response: Apply Saved FG Calibration Data; ")
            .ToString();

        return a_result;
    }

    #endregion

    private static double
    to_celcius
    (ushort a_raw) => 0.1 * a_raw - 273.1;

    private CAN_ID
    compute_outgoing_id
    (Destination a_destination, uint a_message_number, int a_size, out uint a_dest)
    {
        if(a_message_number is > 0xFFu)
        {
            throw new ArgumentOutOfRangeException(nameof(a_message_number));
        }

        a_dest =
            (Destination_ID)a_destination.id switch
            {
                Destination_ID.PACK_0 => 0u,
                Destination_ID.PACK_1 => 1u,
                Destination_ID.PACK_2 => 2u,
                Destination_ID.PACK_3 => 3u,
                _ => throw new ArgumentOutOfRangeException(nameof(a_destination))
            };

        return
            new()
            {
                ext_id = m_id_prefix | (a_message_number << 2) | (a_dest << 0),
                is_can_fd = false,
                is_remote = false,
                size = a_size
            };
    }
}
