using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Globalization;
using System.Text;
using contracts;
using Tomlyn;
using Tomlyn.Model;
using utility.can;
using utility.misc;

namespace program_ns.processing.products;

internal sealed class
Avd_One : Product
{
    private enum
    Message_Number : uint
    {
        WAKE_S,
        WAKE_R,
        COMMAND_S,
        COMMAND_R,
        CORE_STATS_S,
        CORE_STATS_R,
        VOLTAGE_S,
        VOLTAGE_R,
        CURRENT_S,
        CURRENT_R,
        DESIGN_S,
        DESIGN_R,
        STATUS_A_S,
        STATUS_A_R,
        STATUS_B_S,
        STATUS_B_R,
        DA_STATUS_S,
        DA_STATUS_R,
        GAUGE_STATUS_A_S,
        GAUGE_STATUS_A_R,
        GAUGE_STATUS_B_S,
        GAUGE_STATUS_B_R,
        CB_STATUS_S,
        CB_STATUS_R,
        AFE_REGISTER_S,
        AFE_REGISTER_R,
        LIFETIME_DATA_A_S,
        LIFETIME_DATA_A_R,
        LIFETIME_DATA_B_S,
        LIFETIME_DATA_B_R,
        MISC_DATA_S,
        MISC_DATA_R,
        SERIAL_NUMBER_S,
        SERIAL_NUMBER_R,
        PART_NUMBER_S,
        PART_NUMBER_R,
        INVALID = 256
    }

    private enum
    Command_Number : ushort
    {
        FETS_OFF,
        FETS_ON,
        SET_SERIAL_NUMBER,
        SET_BUILD_DATE,
        FG_RESET,
        FG_SEAL,
        FG_UNSEAL,
        FG_UNSEAL_FULL,
        FG_GAUGING_ENABLE,
        FG_LIFETIME_ENABLE,
        FG_PF_ENABLE,
        FG_BBR_ENABLE,
        FORCE_LED,
        RDP_ENABLE,
        RESET_REQUEST = 1024,
        JTAG_CONNECT,
        ISQC_CONNECT,
        DISCONNECT_IDLE,
        FG_PROGRAM,
        FG_CAL_CC_OFFSET,
        FG_CAL_BOARD_OFFSET,
        FG_CAL_VOLTAGE,
        FG_CAL_CURRENT
    }

    private enum
    Command_Error : ushort
    {
        NONE,
        INVALID_OPERATION,
        FUEL_GAUGE_SEALED,
        INVALID_UNSEAL_KEY,
        INVALID_SERIAL_NUMBER,
        INVALID_BUILD_DATE,
        EEPROM_WRITE_FAILED,
        RDP_ENABLE_FAILED,
        PROGCAL_ERROR = 1024,
        INVALID_STATE
    }

    private enum
    Destination_ID : uint
    {

    }

    private enum
    Message_Register_ID : uint
    {
        WAKE,
        COMMAND,
        CORE_STATS_I,
        CORE_STATS_II,
        VOLTAGE,
        CURRENT_I,
        CURRENT_II,
        DESIGN,
        STATUS_A,
        STATUS_B,
        DA_STATUS_I,
        DA_STATUS_II,
        DA_STATUS_III,
        DA_STATUS_IV,
        DA_STATUS_V,
        DA_STATUS_VI,
        DA_STATUS_VII,
        GAUGE_STATUS_A_I,
        GAUGE_STATUS_A_II,
        GAUGE_STATUS_A_III,
        GAUGE_STATUS_A_IV,
        GAUGE_STATUS_A_V,
        GAUGE_STATUS_A_VI,
        GAUGE_STATUS_A_VII,
        GAUGE_STATUS_A_VIII,
        GAUGE_STATUS_A_IX,
        GAUGE_STATUS_B_I,
        GAUGE_STATUS_B_II,
        GAUGE_STATUS_B_III,
        CB_STATUS_I,
        CB_STATUS_II,
        AFE_REGISTER_I,
        AFE_REGISTER_II,
        AFE_REGISTER_III,
        AFE_REGISTER_IV,
        AFE_REGISTER_V,
        LIFETIME_DATA_A_I,
        LIFETIME_DATA_A_II,
        LIFETIME_DATA_A_III,
        LIFETIME_DATA_A_IV,
        LIFETIME_DATA_A_V,
        LIFETIME_DATA_A_VI,
        LIFETIME_DATA_A_VII,
        LIFETIME_DATA_A_VIII,
        LIFETIME_DATA_A_IX,
        LIFETIME_DATA_B_I,
        LIFETIME_DATA_B_II,
        LIFETIME_DATA_B_III,
        LIFETIME_DATA_B_IV,
        LIFETIME_DATA_B_V,
        LIFETIME_DATA_B_VI,
        LIFETIME_DATA_B_VII,
        LIFETIME_DATA_B_VIII,
        MISC_DATA_I,
        MISC_DATA_II,
        MISC_DATA_III,
        MISC_DATA_IV,
        MISC_DATA_V,
        SERIAL_NUMBER,
        PART_NUMBER
    };

    private enum
    Status_Register_ID : uint
    {
        BATTERY_STATUS_HI,
        BATTERY_STATUS_LO,
        MANUFACTURING_STATUS_HI,
        MANUFACTURING_STATUS_LO,
        OPERATION_STATUS_HI_HI,
        OPERATION_STATUS_HI_LO,
        OPERATION_STATUS_LO_HI,
        OPERATION_STATUS_LO_LO,
        CHARGING_STATUS_HI_HI,
        CHARGING_STATUS_HI_LO,
        CHARGING_STATUS_LO_HI,
        CHARGING_STATUS_LO_LO,
        GAUGING_STATUS_HI_HI,
        GAUGING_STATUS_HI_LO,
        GAUGING_STATUS_LO_HI,
        GAUGING_STATUS_LO_LO,
        SAFETY_ALERT_HI_HI,
        SAFETY_ALERT_HI_LO,
        SAFETY_ALERT_LO_HI,
        SAFETY_ALERT_LO_LO,
        SAFETY_STATUS_HI_HI,
        SAFETY_STATUS_HI_LO,
        SAFETY_STATUS_LO_HI,
        SAFETY_STATUS_LO_LO,
        PF_ALERT_HI_HI,
        PF_ALERT_HI_LO,
        PF_ALERT_LO_HI,
        PF_ALERT_LO_LO,
        PF_STATUS_HI_HI,
        PF_STATUS_HI_LO,
        PF_STATUS_LO_HI,
        PF_STATUS_LO_LO
    };

    private enum
    Query_ID : uint
    {
        WAKE,
        CORE_STATS,
        VOLTAGE,
        CURRENT,
        DESIGN,
        STATUS_A,
        STATUS_B,
        DA_STATUS,
        GAUGE_STATUS_A,
        GAUGE_STATUS_B,
        CB_STATUS,
        AFE_REGISTER,
        LIFETIME_DATA_A,
        LIFETIME_DATA_B,
        MISC_DATA,
        SERIAL_NUMBER,
        PART_NUMBER,
        ALL
    };

    private enum
    Command_ID : uint
    {
        FETS_OFF,
        FETS_ON,
        SET_SERIAL_NUMBER,
        SET_BUILD_DATE,
        FG_UNSEAL,
        FG_UNSEAL_FULL,
        FG_RESET,
        FG_GAUGING_ENABLE,
        FG_LIFETIME_ENABLE,
        FG_PF_ENABLE,
        FG_BBR_ENABLE,
        FG_SEAL,
        FORCE_LED_OFF,
        FORCE_LED_GREEN,
        FORCE_LED_RED,
        FORCE_LED_ORANGE,
        RDP_ENABLE,
        RESET_REQUEST,
        JTAG_CONNECT,
        ISQC_CONNECT,
        DISCONNECT_IDLE,
        FG_PROGRAM,
        FG_CAL_CC_OFFSET,
        FG_CAL_BOARD_OFFSET,
        FG_CAL_VOLTAGE,
        FG_CAL_CURRENT
    };

    private static readonly Query s_default_query =
        new() { id = (uint)Query_ID.ALL, display_text = "All" };

    private static readonly HashSet<Destination> s_dest_set =
    new()
    {

    };

    private static readonly HashSet<Message_Register> s_message_register_set =
    new()
    {
        new() { id = (uint)Message_Register_ID.WAKE, display_text = "Wake Response" },
        new() { id = (uint)Message_Register_ID.COMMAND, display_text = "Command Response" },
        new() { id = (uint)Message_Register_ID.CORE_STATS_I,  display_text = "Core Stats I" },
        new() { id = (uint)Message_Register_ID.CORE_STATS_II, display_text = "Core Stats II" },
        new() { id = (uint)Message_Register_ID.VOLTAGE, display_text = "Voltage" },
        new() { id = (uint)Message_Register_ID.CURRENT_I,  display_text = "Current I" },
        new() { id = (uint)Message_Register_ID.CURRENT_II, display_text = "Current II" },
        new() { id = (uint)Message_Register_ID.DESIGN, display_text = "Design" },
        new() { id = (uint)Message_Register_ID.STATUS_A, display_text = "Status A" },
        new() { id = (uint)Message_Register_ID.STATUS_B, display_text = "Status B" },
        new() { id = (uint)Message_Register_ID.DA_STATUS_I,   display_text = "DA Status I" },
        new() { id = (uint)Message_Register_ID.DA_STATUS_II,  display_text = "DA Status II" },
        new() { id = (uint)Message_Register_ID.DA_STATUS_III, display_text = "DA Status III" },
        new() { id = (uint)Message_Register_ID.DA_STATUS_IV,  display_text = "DA Status IV" },
        new() { id = (uint)Message_Register_ID.DA_STATUS_V,   display_text = "DA Status V" },
        new() { id = (uint)Message_Register_ID.DA_STATUS_VI,  display_text = "DA Status VI" },
        new() { id = (uint)Message_Register_ID.DA_STATUS_VII, display_text = "DA Status VII" },
        new() { id = (uint)Message_Register_ID.GAUGE_STATUS_A_I,    display_text = "Gauge Status A I" },
        new() { id = (uint)Message_Register_ID.GAUGE_STATUS_A_II,   display_text = "Gauge Status A II" },
        new() { id = (uint)Message_Register_ID.GAUGE_STATUS_A_III,  display_text = "Gauge Status A III" },
        new() { id = (uint)Message_Register_ID.GAUGE_STATUS_A_IV,   display_text = "Gauge Status A IV" },
        new() { id = (uint)Message_Register_ID.GAUGE_STATUS_A_V,    display_text = "Gauge Status A V" },
        new() { id = (uint)Message_Register_ID.GAUGE_STATUS_A_VI,   display_text = "Gauge Status A VI" },
        new() { id = (uint)Message_Register_ID.GAUGE_STATUS_A_VII,  display_text = "Gauge Status A VII" },
        new() { id = (uint)Message_Register_ID.GAUGE_STATUS_A_VIII, display_text = "Gauge Status A VIII" },
        new() { id = (uint)Message_Register_ID.GAUGE_STATUS_A_IX,   display_text = "Gauge Status A IX" },
        new() { id = (uint)Message_Register_ID.GAUGE_STATUS_B_I,    display_text = "Gauge Status B I" },
        new() { id = (uint)Message_Register_ID.GAUGE_STATUS_B_II,   display_text = "Gauge Status B II" },
        new() { id = (uint)Message_Register_ID.GAUGE_STATUS_B_III,  display_text = "Gauge Status B III" },
        new() { id = (uint)Message_Register_ID.CB_STATUS_I,  display_text = "CB Status I" },
        new() { id = (uint)Message_Register_ID.CB_STATUS_II, display_text = "CB Status II" },
        new() { id = (uint)Message_Register_ID.AFE_REGISTER_I,   display_text = "AFE Register I" },
        new() { id = (uint)Message_Register_ID.AFE_REGISTER_II,  display_text = "AFE Register II" },
        new() { id = (uint)Message_Register_ID.AFE_REGISTER_III, display_text = "AFE Register III" },
        new() { id = (uint)Message_Register_ID.AFE_REGISTER_IV,  display_text = "AFE Register IV" },
        new() { id = (uint)Message_Register_ID.AFE_REGISTER_V,   display_text = "AFE Register V" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_A_I,    display_text = "Lifetime Data A I" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_A_II,   display_text = "Lifetime Data A II" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_A_III,  display_text = "Lifetime Data A III" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_A_IV,   display_text = "Lifetime Data A IV" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_A_V,    display_text = "Lifetime Data A V" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_A_VI,   display_text = "Lifetime Data A VI" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_A_VII,  display_text = "Lifetime Data A VII" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_A_VIII, display_text = "Lifetime Data A VIII" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_A_IX,   display_text = "Lifetime Data A IX" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_B_I,    display_text = "Lifetime Data B I" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_B_II,   display_text = "Lifetime Data B II" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_B_III,  display_text = "Lifetime Data B III" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_B_IV,   display_text = "Lifetime Data B IV" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_B_V,    display_text = "Lifetime Data B V" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_B_VI,   display_text = "Lifetime Data B VI" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_B_VII,  display_text = "Lifetime Data B VII" },
        new() { id = (uint)Message_Register_ID.LIFETIME_DATA_B_VIII, display_text = "Lifetime Data B VIII" },
        new() { id = (uint)Message_Register_ID.MISC_DATA_I,   display_text = "Misc Data I" },
        new() { id = (uint)Message_Register_ID.MISC_DATA_II,  display_text = "Misc Data II" },
        new() { id = (uint)Message_Register_ID.MISC_DATA_III, display_text = "Misc Data III" },
        new() { id = (uint)Message_Register_ID.MISC_DATA_IV,  display_text = "Misc Data IV" },
        new() { id = (uint)Message_Register_ID.MISC_DATA_V,   display_text = "Misc Data V" },
        new() { id = (uint)Message_Register_ID.SERIAL_NUMBER, display_text = "Serial Number" },
        new() { id = (uint)Message_Register_ID.PART_NUMBER, display_text = "Part Number" }
    };

    private static readonly HashSet<Status_Register> s_status_register_set =
    new()
    {
        new()
        {
            id = (uint)Status_Register_ID.BATTERY_STATUS_HI,
            display_text = "Battery Status Hi",
            bit7 = ("OCA", false),
            bit6 = ("TCA", false),
            bit5 = ("RSVD", true),
            bit4 = ("OTA", false),
            bit3 = ("TDA", false),
            bit2 = ("RSVD", true),
            bit1 = ("RCA", false),
            bit0 = ("RTA", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.BATTERY_STATUS_LO,
            display_text = "Battery Status Lo",
            bit7 = ("INIT", false),
            bit6 = ("DSG", false),
            bit5 = ("FC", false),
            bit4 = ("FD", false),
            bit3 = ("EC3", false),
            bit2 = ("EC2", false),
            bit1 = ("EC1", false),
            bit0 = ("EC0", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.MANUFACTURING_STATUS_HI,
            display_text = "Manufacturing Status Hi",
            bit7 = ("CAL_TEST", false),
            bit6 = ("LT_TEST", false),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("RSVD", true),
            bit2 = ("RSVD", true),
            bit1 = ("LED_EN", false),
            bit0 = ("FUSE_EN", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.MANUFACTURING_STATUS_LO,
            display_text = "Manufacturing Status Lo",
            bit7 = ("BBR_EN", false),
            bit6 = ("PF_EN", false),
            bit5 = ("LF_EN", false),
            bit4 = ("FET_EN", false),
            bit3 = ("GAUGE_EN", false),
            bit2 = ("DSG_EN", false),
            bit1 = ("CHG_EN", false),
            bit0 = ("PCHG_EN", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.OPERATION_STATUS_HI_HI,
            display_text = "Operation Status Hi Hi",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("EMSHUT", false),
            bit4 = ("CB", false),
            bit3 = ("SLPCC", false),
            bit2 = ("SLPAD", false),
            bit1 = ("SMBLCAL", false),
            bit0 = ("INIT", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.OPERATION_STATUS_HI_LO,
            display_text = "Operation Status Hi Lo",
            bit7 = ("SLEEPM", false),
            bit6 = ("XL", false),
            bit5 = ("CAL_OFFST", false),
            bit4 = ("CAL", false),
            bit3 = ("AUTOCALM", false),
            bit2 = ("AUTH", false),
            bit1 = ("LED", false),
            bit0 = ("SDM", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.OPERATION_STATUS_LO_HI,
            display_text = "Operation Status Lo Hi",
            bit7 = ("SLEEP", false),
            bit6 = ("XCHG", false),
            bit5 = ("XDSG", false),
            bit4 = ("PF", false),
            bit3 = ("SS", false),
            bit2 = ("SDV", false),
            bit1 = ("SEC1", false),
            bit0 = ("SEC0", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.OPERATION_STATUS_LO_LO,
            display_text = "Operation Status Lo Lo",
            bit7 = ("BTP_INT", false),
            bit6 = ("RSVD", true),
            bit5 = ("FUSE", false),
            bit4 = ("RSVD", true),
            bit3 = ("PCHG", false),
            bit2 = ("CHG", false),
            bit1 = ("DSG", false),
            bit0 = ("PRES", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.CHARGING_STATUS_HI_HI,
            display_text = "Charging Status Hi Hi",
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
            id = (uint)Status_Register_ID.CHARGING_STATUS_HI_LO,
            display_text = "Charging Status Hi Lo",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("RSVD", true),
            bit3 = ("NCT", false),
            bit2 = ("CCC", false),
            bit1 = ("CVR", false),
            bit0 = ("CCR", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.CHARGING_STATUS_LO_HI,
            display_text = "Charging Status Lo Hi",
            bit7 = ("VCT", false),
            bit6 = ("MCHG", false),
            bit5 = ("SU", false),
            bit4 = ("IN", false),
            bit3 = ("HV", false),
            bit2 = ("MV", false),
            bit1 = ("LV", false),
            bit0 = ("PV", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.CHARGING_STATUS_LO_LO,
            display_text = "Charging Status Lo Lo",
            bit7 = ("RSVD", true),
            bit6 = ("OT", false),
            bit5 = ("HT", false),
            bit4 = ("STH", false),
            bit3 = ("RT", false),
            bit2 = ("STL", false),
            bit1 = ("LT", false),
            bit0 = ("UT", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.GAUGING_STATUS_HI_HI,
            display_text = "Gauging Status Hi Hi",
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
            id = (uint)Status_Register_ID.GAUGING_STATUS_HI_LO,
            display_text = "Gauging Status Hi Lo",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("RSVD", true),
            bit4 = ("OCVFR", false),
            bit3 = ("LDMD", false),
            bit2 = ("RX", false),
            bit1 = ("QMAX", false),
            bit0 = ("VDQ", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.GAUGING_STATUS_LO_HI,
            display_text = "Gauging Status Lo Hi",
            bit7 = ("NSFM", false),
            bit6 = ("RSVD", true),
            bit5 = ("SLPQMAX", false),
            bit4 = ("QEN", false),
            bit3 = ("VOK", false),
            bit2 = ("R_DIS", false),
            bit1 = ("RSVD", true),
            bit0 = ("REST", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.GAUGING_STATUS_LO_LO,
            display_text = "Gauging Status Lo Lo",
            bit7 = ("CF", false),
            bit6 = ("DSG", false),
            bit5 = ("EDV", false),
            bit4 = ("BAL_EN", false),
            bit3 = ("TC", false),
            bit2 = ("TD", false),
            bit1 = ("FC", false),
            bit0 = ("FD", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.SAFETY_ALERT_HI_HI,
            display_text = "Safety Alert Hi Hi",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("OCDL", false),
            bit4 = ("COVL", false),
            bit3 = ("UTD", false),
            bit2 = ("UTC", false),
            bit1 = ("PCHGC", false),
            bit0 = ("CHGV", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.SAFETY_ALERT_HI_LO,
            display_text = "Safety Alert Hi Lo",
            bit7 = ("CHGC", false),
            bit6 = ("OC", false),
            bit5 = ("CTOS", false),
            bit4 = ("CTO", false),
            bit3 = ("PTOS", false),
            bit2 = ("PTO", false),
            bit1 = ("RSVD", true),
            bit0 = ("OTF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.SAFETY_ALERT_LO_HI,
            display_text = "Safety Alert Lo Hi",
            bit7 = ("RSVD", true),
            bit6 = ("CUVC", false),
            bit5 = ("OTD", false),
            bit4 = ("OTC", false),
            bit3 = ("ASCDL", false),
            bit2 = ("RSVD", true),
            bit1 = ("ASCCL", false),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.SAFETY_ALERT_LO_LO,
            display_text = "Safety Alert Lo Lo",
            bit7 = ("AOLDL", false),
            bit6 = ("RSVD", true),
            bit5 = ("OCD2", false),
            bit4 = ("OCD1", false),
            bit3 = ("OCC2", false),
            bit2 = ("OCC1", false),
            bit1 = ("COV", false),
            bit0 = ("CUV", false)
        },

        new()
        {
            id = (uint)Status_Register_ID.SAFETY_STATUS_HI_HI,
            display_text = "Safety Status Hi Hi",
            bit7 = ("RSVD", true),
            bit6 = ("RSVD", true),
            bit5 = ("OCDL", false),
            bit4 = ("COVL", false),
            bit3 = ("UTD", false),
            bit2 = ("UTC", false),
            bit1 = ("PCHGC", false),
            bit0 = ("CHGV", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.SAFETY_STATUS_HI_LO,
            display_text = "Safety Status Hi Lo",
            bit7 = ("CHGC", false),
            bit6 = ("OC", false),
            bit5 = ("RSVD", true),
            bit4 = ("CTO", false),
            bit3 = ("RSVD", true),
            bit2 = ("PTO", false),
            bit1 = ("RSVD", true),
            bit0 = ("OTF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.SAFETY_STATUS_LO_HI,
            display_text = "Safety Status Lo Hi",
            bit7 = ("RSVD", true),
            bit6 = ("CUVC", false),
            bit5 = ("OTD", false),
            bit4 = ("OTC", false),
            bit3 = ("ASCDL", false),
            bit2 = ("ASCD", false),
            bit1 = ("ASCCL", false),
            bit0 = ("ASCC", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.SAFETY_STATUS_LO_LO,
            display_text = "Safety Status Lo Lo",
            bit7 = ("AOLDL", false),
            bit6 = ("AOLD", false),
            bit5 = ("OCD2", false),
            bit4 = ("OCD1", false),
            bit3 = ("OCC2", false),
            bit2 = ("OCC1", false),
            bit1 = ("COV", false),
            bit0 = ("CUV", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PF_ALERT_HI_HI,
            display_text = "PF Alert Hi Hi",
            bit7 = ("TS4", false),
            bit6 = ("TS3", false),
            bit5 = ("TS2", false),
            bit4 = ("TS1", false),
            bit3 = ("RSVD", true),
            bit2 = ("RSVD", true),
            bit1 = ("RSVD", true),
            bit0 = ("RSVD", true)
        },
        new()
        {
            id = (uint)Status_Register_ID.PF_ALERT_HI_LO,
            display_text = "PF Alert Hi Lo",
            bit7 = ("RSVD", true),
            bit6 = ("2LVL", false),
            bit5 = ("AFEC", false),
            bit4 = ("AFER", false),
            bit3 = ("FUSE", false),
            bit2 = ("OCDL", false),
            bit1 = ("DFETF", false),
            bit0 = ("CFETF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PF_ALERT_LO_HI,
            display_text = "PF Alert Lo Hi",
            bit7 = ("ASCDL", false),
            bit6 = ("ASCCL", false),
            bit5 = ("AOLDL", false),
            bit4 = ("VIMA", false),
            bit3 = ("VIMR", false),
            bit2 = ("CD", false),
            bit1 = ("IMP", false),
            bit0 = ("CB", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PF_ALERT_LO_LO,
            display_text = "PF Alert Lo Lo",
            bit7 = ("QIM", false),
            bit6 = ("SOTF", false),
            bit5 = ("COVL", false),
            bit4 = ("SOT", false),
            bit3 = ("SOCD", false),
            bit2 = ("SOCC", false),
            bit1 = ("SOV", false),
            bit0 = ("SUV", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PF_STATUS_HI_HI,
            display_text = "PF Status Hi Hi",
            bit7 = ("TS4", false),
            bit6 = ("TS3", false),
            bit5 = ("TS2", false),
            bit4 = ("TS1", false),
            bit3 = ("RSVD", true),
            bit2 = ("DFW", false),
            bit1 = ("RSVD", true),
            bit0 = ("IFC", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PF_STATUS_HI_LO,
            display_text = "PF Status Hi Lo",
            bit7 = ("PTC", false),
            bit6 = ("2LVL", false),
            bit5 = ("AFEC", false),
            bit4 = ("AFER", false),
            bit3 = ("FUSE", false),
            bit2 = ("OCDL", false),
            bit1 = ("DFETF", false),
            bit0 = ("CFETF", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PF_STATUS_LO_HI,
            display_text = "PF Status Lo Hi",
            bit7 = ("ASCDL", false),
            bit6 = ("ASCCL", false),
            bit5 = ("AOLDL", false),
            bit4 = ("VIMA", false),
            bit3 = ("VIMR", false),
            bit2 = ("CD", false),
            bit1 = ("IMP", false),
            bit0 = ("CB", false)
        },
        new()
        {
            id = (uint)Status_Register_ID.PF_STATUS_LO_LO,
            display_text = "PF Status Lo Lo",
            bit7 = ("QIM", false),
            bit6 = ("SOTF", false),
            bit5 = ("COVL", false),
            bit4 = ("SOT", false),
            bit3 = ("SOCD", false),
            bit2 = ("SOCC", false),
            bit1 = ("SOV", false),
            bit0 = ("SUV", false)
        }
    };

    private static readonly HashSet<Query> s_query_set =
    new()
    {
        new() { id = (uint)Query_ID.WAKE, display_text = "Wake" },
        new() { id = (uint)Query_ID.CORE_STATS, display_text = "Core Stats" },
        new() { id = (uint)Query_ID.VOLTAGE, display_text = "Voltage" },
        new() { id = (uint)Query_ID.CURRENT, display_text = "Current" },
        new() { id = (uint)Query_ID.DESIGN, display_text = "Design" },
        new() { id = (uint)Query_ID.STATUS_A, display_text = "Status A" },
        new() { id = (uint)Query_ID.STATUS_B, display_text = "Status B" },
        new() { id = (uint)Query_ID.DA_STATUS, display_text = "DA Status" },
        new() { id = (uint)Query_ID.GAUGE_STATUS_A, display_text = "Gauge Status A" },
        new() { id = (uint)Query_ID.GAUGE_STATUS_B, display_text = "Gauge Status B" },
        new() { id = (uint)Query_ID.CB_STATUS, display_text = "CB Status" },
        new() { id = (uint)Query_ID.AFE_REGISTER, display_text = "AFE Register" },
        new() { id = (uint)Query_ID.LIFETIME_DATA_A, display_text = "Lifetime Data A" },
        new() { id = (uint)Query_ID.LIFETIME_DATA_B, display_text = "Lifetime Data B" },
        new() { id = (uint)Query_ID.MISC_DATA, display_text = "Misc Data" },
        new() { id = (uint)Query_ID.SERIAL_NUMBER, display_text = "Serial Number" },
        new() { id = (uint)Query_ID.PART_NUMBER, display_text = "Part Number" },
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
            id = (uint)Command_ID.SET_SERIAL_NUMBER,
            display_text = "Set Serial Number",
            arguments = ImmutableArray.Create(("SN:", string.Empty)),
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.SET_BUILD_DATE,
            display_text = "Set Manufacture Date",
            arguments =
                ImmutableArray.Create
                (
                    ("Day:", DateTime.Now.Day.ToString("D2")),
                    ("Month:", DateTime.Now.Month.ToString("D2")),
                    ("Year:", DateTime.Now.Year.ToString("D4"))
                ),
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_UNSEAL,
            display_text = "Unseal Fuel Gauge",
            arguments = ImmutableArray.Create(("Key:", "17406789")),
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_UNSEAL_FULL,
            display_text = "Unseal Fuel Gauge (full)",
            arguments = ImmutableArray.Create(("Key:", "1740AABB")),
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
            id = (uint)Command_ID.FG_GAUGING_ENABLE,
            display_text = "Gauging Enable",
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
            id = (uint)Command_ID.FG_PF_ENABLE,
            display_text = "PF Enable",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FG_BBR_ENABLE,
            display_text = "BBR Enable",
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
            id = (uint)Command_ID.FORCE_LED_OFF,
            display_text = "LED Force Off",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FORCE_LED_GREEN,
            display_text = "Green LED Force On",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FORCE_LED_RED,
            display_text = "Red LED Force On",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.FORCE_LED_ORANGE,
            display_text = "Orange LED Force On",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.RDP_ENABLE,
            display_text = "Readout Protect Enable",
            response_timeout = 1000
        }
    };

    private static readonly HashSet<Command> s_programmer_command_set =
    new()
    {
        new()
        {
            id = (uint)Command_ID.RESET_REQUEST,
            display_text = "Request Reset",
            response_timeout = 1000
        },
        new()
        {
            id = (uint)Command_ID.JTAG_CONNECT,
            display_text = "JTAG Connect",
            response_timeout = 3000
        },
        new()
        {
            id = (uint)Command_ID.ISQC_CONNECT,
            display_text = "I2C Connect",
            response_timeout = 3000
        },
        new()
        {
            id = (uint)Command_ID.DISCONNECT_IDLE,
            display_text = "Disconnect",
            response_timeout = 3000
        },
        new()
        {
            id = (uint)Command_ID.FG_PROGRAM,
            display_text = "Program Fuel Gauge",
            response_timeout = 40_000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_CC_OFFSET,
            display_text = "Calibrate FG CC Offset",
            response_timeout = 15_000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_BOARD_OFFSET,
            display_text = "Calibrate FG Board Offset",
            response_timeout = 15_000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_VOLTAGE,
            display_text = "Calibrate FG Voltage",
            arguments =
                ImmutableArray.Create
                (
                    ("Cell Volt:", "3.800"),
                    ("Batt Volt:", "7.600"),
                    ("Pack Volt:", "7.600")
                ),
            response_timeout = 15_000
        },
        new()
        {
            id = (uint)Command_ID.FG_CAL_CURRENT,
            display_text = "Calibrate FG Current",
            arguments = ImmutableArray.Create(("Curr:", "-2.000")),
            response_timeout = 15_000
        }
    };

    public
    Avd_One
    (Config_Data a_config) :
    base()
    {
        var a_table = Toml.Parse(a_config.config_file_text).ToModel();

        if(a_table.TryGetValue("avd", out var a_avd_tab_object))
        {
            var a_avd_tab = (TomlTable)a_avd_tab_object;

            if((string)a_avd_tab["commands-password"] is "poweroverwhelming")
            {
                var a_command_set = new HashSet<Command>(s_command_set);

                if((bool)a_avd_tab["programmer"])
                {
                    a_command_set.UnionWith(s_programmer_command_set);
                }

                m_command_set = a_command_set;

                return;
            }
        }

        m_command_set = new HashSet<Command>();
    }

    private readonly IReadOnlySet<Command> m_command_set;

    public override IReadOnlySet<Destination> destination_set => s_dest_set;
    public override IReadOnlySet<Message_Register> message_register_set => s_message_register_set;
    public override IReadOnlySet<Status_Register> status_register_set => s_status_register_set;
    public override IReadOnlySet<Query> query_set => s_query_set;
    public override IReadOnlySet<Command> command_set => m_command_set;
    public override Destination? default_destination => null;
    public override Query? default_query => s_default_query;
    public override Command? enter_bootloader_command => null;

    protected override void
    new_can_message
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(!a_id.is_can_fd || !a_id.is_ext_id || a_id.is_bitrate_switch || a_id.is_error_passive)
        {
            return;
        }

        if((a_id.id & 0xFFFFFF00u) is not 0x1AD77700u)
        {
            return;
        }

        var a_msg = (Message_Number)(a_id.id & 0xFFu);

        _ =
        a_msg switch
        {
            Message_Number.WAKE_R => parse_message_wake(a_id, a_data),
            Message_Number.COMMAND_R => parse_message_command(a_id, a_data),
            Message_Number.CORE_STATS_R => parse_message_core_stats(a_id, a_data),
            Message_Number.VOLTAGE_R => parse_message_voltage(a_id, a_data),
            Message_Number.CURRENT_R => parse_message_current(a_id, a_data),
            Message_Number.DESIGN_R => parse_message_design(a_id, a_data),
            Message_Number.STATUS_A_R => parse_message_status_a(a_id, a_data),
            Message_Number.STATUS_B_R => parse_message_status_b(a_id, a_data),
            Message_Number.DA_STATUS_R => parse_message_da_status(a_id, a_data),
            Message_Number.GAUGE_STATUS_A_R => parse_message_gauge_status_a(a_id, a_data),
            Message_Number.GAUGE_STATUS_B_R => parse_message_gauge_status_b(a_id, a_data),
            Message_Number.CB_STATUS_R => parse_message_cb_status(a_id, a_data),
            Message_Number.AFE_REGISTER_R => parse_message_afe_register(a_id, a_data),
            Message_Number.LIFETIME_DATA_A_R => parse_message_lifetime_data_a(a_id, a_data),
            Message_Number.LIFETIME_DATA_B_R => parse_message_lifetime_data_b(a_id, a_data),
            Message_Number.MISC_DATA_R => parse_message_misc_data(a_id, a_data),
            Message_Number.SERIAL_NUMBER_R => parse_message_serial_number(a_id, a_data),
            Message_Number.PART_NUMBER_R => parse_message_part_number(a_id, a_data),
            _ => false
        };
    }

    protected override void
    new_query
    (Destination? a_dest, Query a_query)
    {
        Contracts.assert(a_dest is null);

        _ =
        (Query_ID)a_query.id switch
        {
            Query_ID.WAKE => process_query_wake(),
            Query_ID.CORE_STATS => process_query_core_stats(),
            Query_ID.VOLTAGE => process_query_voltage(),
            Query_ID.CURRENT => process_query_current(),
            Query_ID.DESIGN => process_query_design(),
            Query_ID.STATUS_A => process_query_status_a(),
            Query_ID.STATUS_B => process_query_status_b(),
            Query_ID.DA_STATUS => process_query_da_status(),
            Query_ID.GAUGE_STATUS_A => process_query_gauge_status_a(),
            Query_ID.GAUGE_STATUS_B => process_query_gauge_status_b(),
            Query_ID.CB_STATUS => process_query_cb_status(),
            Query_ID.AFE_REGISTER => process_query_afe_register(),
            Query_ID.LIFETIME_DATA_A => process_query_lifetime_data_a(),
            Query_ID.LIFETIME_DATA_B => process_query_lifetime_data_b(),
            Query_ID.MISC_DATA => process_query_misc_data(),
            Query_ID.SERIAL_NUMBER => process_query_serial_number(),
            Query_ID.PART_NUMBER => process_query_part_number(),
            Query_ID.ALL => process_query_all(),
            _ => false
        };
    }

    protected override void
    new_command
    (Destination? a_dest, Command a_command, in ReadOnlySpan<string> a_args)
    {
        Contracts.assert(a_dest is null);

        _ =
        (Command_ID)a_command.id switch
        {
            Command_ID.FETS_OFF => process_command_fets_off(),
            Command_ID.FETS_ON => process_command_fets_on(),
            Command_ID.SET_SERIAL_NUMBER => process_command_set_serial_number(a_args[0]),
            Command_ID.SET_BUILD_DATE => process_command_set_build_date(a_args[0], a_args[1], a_args[2]),
            Command_ID.FG_UNSEAL => process_command_fg_unseal(a_args[0]),
            Command_ID.FG_UNSEAL_FULL => process_command_fg_unseal_full(a_args[0]),
            Command_ID.FG_RESET => process_command_fg_reset(),
            Command_ID.FG_GAUGING_ENABLE => process_command_fg_gauging_enable(),
            Command_ID.FG_LIFETIME_ENABLE => process_command_fg_lifetime_enable(),
            Command_ID.FG_PF_ENABLE => process_command_fg_pf_enable(),
            Command_ID.FG_BBR_ENABLE => process_command_fg_bbr_enable(),
            Command_ID.FG_SEAL => process_command_fg_seal(),
            Command_ID.FORCE_LED_OFF => process_command_force_led(0b00),
            Command_ID.FORCE_LED_GREEN => process_command_force_led(0b01),
            Command_ID.FORCE_LED_RED => process_command_force_led(0b10),
            Command_ID.FORCE_LED_ORANGE => process_command_force_led(0b11),
            Command_ID.RDP_ENABLE => process_command_rdp_enable(),
            Command_ID.RESET_REQUEST => process_command_reset_request(),
            Command_ID.JTAG_CONNECT => process_command_jtag_connect(),
            Command_ID.ISQC_CONNECT => process_command_isqc_connect(),
            Command_ID.DISCONNECT_IDLE => process_command_disconnect_idle(),
            Command_ID.FG_PROGRAM => process_command_fg_program(),
            Command_ID.FG_CAL_CC_OFFSET => process_command_fg_cal_cc_offset(),
            Command_ID.FG_CAL_BOARD_OFFSET => process_command_fg_cal_board_offset(),
            Command_ID.FG_CAL_VOLTAGE => process_command_fg_cal_voltage(a_args[0], a_args[1], a_args[2]),
            Command_ID.FG_CAL_CURRENT => process_command_fg_cal_current(a_args[0]),
            _ => false
        };
    }

    #region MESSAGES

    private void
    add_message_register
    (Message_Register_ID a_register_id, CAN_ID a_id, in ReadOnlySpan<byte> a_data, string a_data_interpreted)
    {
        using var a_guard = String_Builder_Pool.acquire();

        var a_msg = a_id.id & 0xFFu;

        add_mess_register_parsed
        (
            message_register_map[(uint)a_register_id],
            new(a_id, a_data)
            {
                id_interpreted = a_guard.value.Append($"MSG={a_msg:X2}").ToString(),
                data_interpreted = a_data_interpreted,
            }
        );
    }

    private bool
    parse_message_wake
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 4)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_uc_version, a_data, ref a_index);
        Misc.decode_le(out ushort a_fg_version, a_data, ref a_index);

        var a_fw_vmajor = (a_uc_version & 0b1111110000000000) >> 10;
        var a_fw_vminor = (a_uc_version & 0b0000001111110000) >> 4;
        var a_fw_rev =    (a_uc_version & 0b0000000000001111) >> 0;

        var a_fg_vmajor = (a_fg_version & 0b1111110000000000) >> 10;
        var a_fg_vminor = (a_fg_version & 0b0000001111110000) >> 4;
        var a_fg_rev =    (a_fg_version & 0b0000000000001111) >> 0;

        {

            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"µController Firmware Ver: {a_fw_vmajor}.{a_fw_vminor}.{a_fw_rev}; ")
            .Append($"Fuel Gauge Firmware Ver: {a_fg_vmajor}.{a_fg_vminor}.{a_fg_rev}; ");

            add_message_register
            (
                Message_Register_ID.WAKE,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_command
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is < 4)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_cmd, a_data, ref a_index);
        Misc.decode_le(out ushort a_err, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Last Command Response: 0x{a_cmd:X4}: {(Command_Number)a_cmd}; Error: {(Command_Error)a_err};");

            add_message_register
            (
                Message_Register_ID.COMMAND,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        set_pending_command_completed();

        return true;
    }

    private bool
    parse_message_core_stats
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 12)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_volt, a_data, ref a_index);
        Misc.decode_le(out short a_curr, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp, a_data, ref a_index);
        Misc.decode_le(out byte a_rel_soc, a_data, ref a_index);
        Misc.decode_le(out byte a_abs_soc, a_data, ref a_index);
        Misc.decode_le(out byte a_max_error, a_data, ref a_index);
        Misc.decode_le(out byte a_soh, a_data, ref a_index);
        Misc.decode_le(out ushort a_cycle_count, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Volt: {0.001 * a_volt:F3} V; ")
            .Append($"Curr: {0.001 * a_curr:F3} A; ")
            .Append($"Temp: {to_celcius(a_temp):F1} °C; ");

            add_message_register
            (
                Message_Register_ID.CORE_STATS_I,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Rel SoC: {a_rel_soc}%; ")
            .Append($"Abs SoC: {a_abs_soc}%; ")
            .Append($"Max Error: {a_max_error}%; ")
            .Append($"SoH: {a_soh}%; ")
            .Append($"Cycle Count: {a_cycle_count}; ");

            add_message_register
            (
                Message_Register_ID.CORE_STATS_II,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_voltage
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_v1, a_data, ref a_index);
        Misc.decode_le(out ushort a_v2, a_data, ref a_index);
        Misc.decode_le(out ushort a_batt, a_data, ref a_index);
        Misc.decode_le(out ushort a_pack, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 Volt: {0.001 * a_v1:F3} V; ")
            .Append($"Cell 2 Volt: {0.001 * a_v2:F3} V; ")
            .Append($"Batt Volt: {0.001 * a_batt:F3} V; ")
            .Append($"Pack Volt: {0.001 * a_pack:F3} V; ");

            add_message_register
            (
                Message_Register_ID.VOLTAGE,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_current
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 12)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out short a_avg_curr, a_data, ref a_index);
        Misc.decode_le(out ushort a_run_tte, a_data, ref a_index);
        Misc.decode_le(out ushort a_avg_tte, a_data, ref a_index);
        Misc.decode_le(out ushort a_avg_ttf, a_data, ref a_index);
        Misc.decode_le(out ushort a_rc, a_data, ref a_index);
        Misc.decode_le(out ushort a_fcc, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Avg Curr: {0.001 * a_avg_curr:F3} A; ")
            .Append($"Run TTE: {a_run_tte} min; ")
            .Append($"Avg TTE: {a_avg_tte} min; ")
            .Append($"Avg TTF: {a_avg_ttf} min; ");

            add_message_register
            (
                Message_Register_ID.CURRENT_I,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Remaining Capacity: {0.001 * a_rc:F3} Ah; ")
            .Append($"Full Charge Capacity: {0.001 * a_fcc:F3} Ah; ");

            add_message_register
            (
                Message_Register_ID.CURRENT_II,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_design
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 8)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_design_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_design_cap, a_data, ref a_index);
        Misc.decode_le(out ushort a_charging_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_charging_curr, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Design Volt: {0.001 * a_design_volt:F3} V; ")
            .Append($"Design Capacity: {0.001 * a_design_cap:F3} Ah; ")
            .Append($"Charging Volt: {0.001 * a_charging_volt:F3} V; ")
            .Append($"Charging Curr: {0.001 * a_charging_curr:F3} A; ");

            add_message_register
            (
                Message_Register_ID.DESIGN,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_status_a
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 16)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_batt_status, a_data, ref a_index);
        Misc.decode_le(out ushort a_manuf_status, a_data, ref a_index);
        Misc.decode_le(out uint a_oper_status, a_data, ref a_index);
        Misc.decode_le(out uint a_charging_status, a_data, ref a_index);
        Misc.decode_le(out uint a_gauging_status, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Batt. Stat: 0x{a_batt_status:X4}; ")
            .Append($"Manuf. Stat: 0x{a_manuf_status:X4}; ")
            .Append($"Oper. Stat: 0x{a_oper_status:X8}; ")
            .Append($"Charging Stat: 0x{a_charging_status:X8}; ")
            .Append($"Gauging Stat: 0x{a_gauging_status:X8}; ");

            add_message_register
            (
                Message_Register_ID.STATUS_A,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BATTERY_STATUS_HI], unchecked((byte)(a_batt_status >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.BATTERY_STATUS_LO], unchecked((byte)(a_batt_status >> 0)));

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.MANUFACTURING_STATUS_HI], unchecked((byte)(a_manuf_status >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.MANUFACTURING_STATUS_LO], unchecked((byte)(a_manuf_status >> 0)));

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.OPERATION_STATUS_HI_HI], unchecked((byte)(a_oper_status >> 24)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.OPERATION_STATUS_HI_LO], unchecked((byte)(a_oper_status >> 16)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.OPERATION_STATUS_LO_HI], unchecked((byte)(a_oper_status >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.OPERATION_STATUS_LO_LO], unchecked((byte)(a_oper_status >> 0)));

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.CHARGING_STATUS_HI_HI], unchecked((byte)(a_charging_status >> 24)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.CHARGING_STATUS_HI_LO], unchecked((byte)(a_charging_status >> 16)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.CHARGING_STATUS_LO_HI], unchecked((byte)(a_charging_status >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.CHARGING_STATUS_LO_LO], unchecked((byte)(a_charging_status >> 0)));

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.GAUGING_STATUS_HI_HI], unchecked((byte)(a_gauging_status >> 24)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.GAUGING_STATUS_HI_LO], unchecked((byte)(a_gauging_status >> 16)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.GAUGING_STATUS_LO_HI], unchecked((byte)(a_gauging_status >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.GAUGING_STATUS_LO_LO], unchecked((byte)(a_gauging_status >> 0)));

        return true;
    }

    private bool
    parse_message_status_b
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 16)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_safety_alert, a_data, ref a_index);
        Misc.decode_le(out uint a_safety_status, a_data, ref a_index);
        Misc.decode_le(out uint a_pf_alert, a_data, ref a_index);
        Misc.decode_le(out uint a_pf_status, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Safety Alert: 0x{a_safety_alert:X8}; ")
            .Append($"Safety Stat: 0x{a_safety_status:X8}; ")
            .Append($"PF Alert: 0x{a_pf_alert:X8}; ")
            .Append($"PF Stat: 0x{a_pf_status:X8}; ");

            add_message_register
            (
                Message_Register_ID.STATUS_B,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.SAFETY_ALERT_HI_HI], unchecked((byte)(a_safety_alert >> 24)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.SAFETY_ALERT_HI_LO], unchecked((byte)(a_safety_alert >> 16)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.SAFETY_ALERT_LO_HI], unchecked((byte)(a_safety_alert >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.SAFETY_ALERT_LO_LO], unchecked((byte)(a_safety_alert >> 0)));

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.SAFETY_STATUS_HI_HI], unchecked((byte)(a_safety_status >> 24)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.SAFETY_STATUS_HI_LO], unchecked((byte)(a_safety_status >> 16)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.SAFETY_STATUS_LO_HI], unchecked((byte)(a_safety_status >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.SAFETY_STATUS_LO_LO], unchecked((byte)(a_safety_status >> 0)));

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PF_ALERT_HI_HI], unchecked((byte)(a_pf_alert >> 24)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PF_ALERT_HI_LO], unchecked((byte)(a_pf_alert >> 16)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PF_ALERT_LO_HI], unchecked((byte)(a_pf_alert >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PF_ALERT_LO_LO], unchecked((byte)(a_pf_alert >> 0)));

        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PF_STATUS_HI_HI], unchecked((byte)(a_pf_status >> 24)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PF_STATUS_HI_LO], unchecked((byte)(a_pf_status >> 16)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PF_STATUS_LO_HI], unchecked((byte)(a_pf_status >> 8)));
        add_stat_register_parsed(status_register_map[(uint)Status_Register_ID.PF_STATUS_LO_LO], unchecked((byte)(a_pf_status >> 0)));

        return true;
    }

    private bool
    parse_message_da_status
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 48)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_v1, a_data, ref a_index);
        Misc.decode_le(out ushort a_v2, a_data, ref a_index);
        Misc.decode_le(out ushort a_v3, a_data, ref a_index);
        Misc.decode_le(out ushort a_v4, a_data, ref a_index);
        Misc.decode_le(out ushort a_batt_volt, a_data, ref a_index);
        Misc.decode_le(out ushort a_pack_volt, a_data, ref a_index);
        Misc.decode_le(out short a_i1, a_data, ref a_index);
        Misc.decode_le(out short a_i2, a_data, ref a_index);
        Misc.decode_le(out short a_i3, a_data, ref a_index);
        Misc.decode_le(out short a_i4, a_data, ref a_index);
        Misc.decode_le(out short a_p1, a_data, ref a_index);
        Misc.decode_le(out short a_p2, a_data, ref a_index);
        Misc.decode_le(out short a_p3, a_data, ref a_index);
        Misc.decode_le(out short a_p4, a_data, ref a_index);
        Misc.decode_le(out short a_power, a_data, ref a_index);
        Misc.decode_le(out short a_avg_power, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_int, a_data, ref a_index);
        Misc.decode_le(out ushort a_ts1, a_data, ref a_index);
        Misc.decode_le(out ushort a_ts2, a_data, ref a_index);
        Misc.decode_le(out ushort a_ts3, a_data, ref a_index);
        Misc.decode_le(out ushort a_ts4, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_cell, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_fet, a_data, ref a_index);
        Misc.decode_le(out ushort a_a_temp_gauging, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 Volt: {0.001 * a_v1:F3} V; ")
            .Append($"Cell 2 Volt: {0.001 * a_v2:F3} V; ")
            .Append($"Cell 3 Volt: {0.001 * a_v3:F3} V; ")
            .Append($"Cell 4 Volt: {0.001 * a_v4:F3} V; ");

            add_message_register
            (
                Message_Register_ID.DA_STATUS_I,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Batt Volt: {0.001 * a_batt_volt:F3} V; ")
            .Append($"Pack Volt: {0.001 * a_pack_volt:F3} V; ");

            add_message_register
            (
                Message_Register_ID.DA_STATUS_II,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 Curr: {0.001 * a_i1:F3} A; ")
            .Append($"Cell 2 Curr: {0.001 * a_i2:F3} A; ")
            .Append($"Cell 3 Curr: {0.001 * a_i3:F3} A; ")
            .Append($"Cell 4 Curr: {0.001 * a_i4:F3} A; ");

            add_message_register
            (
                Message_Register_ID.DA_STATUS_III,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 Powr: {0.01 * a_p1:F2} W; ")
            .Append($"Cell 2 Powr: {0.01 * a_p2:F2} W; ")
            .Append($"Cell 3 Powr: {0.01 * a_p3:F2} W; ")
            .Append($"Cell 4 Powr: {0.01 * a_p4:F2} W; ");

            add_message_register
            (
                Message_Register_ID.DA_STATUS_IV,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Power: {0.01 * a_power:F2} W; ")
            .Append($"Avg Power: {0.01 * a_avg_power:F2} W; ");

            add_message_register
            (
                Message_Register_ID.DA_STATUS_V,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Internal Temp: {to_celcius(a_temp_int):F1} °C; ")
            .Append($"Cell Temp: {to_celcius(a_temp_cell):F1} °C; ")
            .Append($"FET Temp: {to_celcius(a_temp_fet):F1} °C; ")
            .Append($"Gauging Temp: {to_celcius(a_a_temp_gauging):F1} °C; ");

            add_message_register
            (
                Message_Register_ID.DA_STATUS_VI,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"TS1 Temp: {to_celcius(a_ts1):F1} °C; ")
            .Append($"TS2 Temp: {to_celcius(a_ts2):F1} °C; ")
            .Append($"TS3 Temp: {to_celcius(a_ts3):F1} °C; ")
            .Append($"TS4 Temp: {to_celcius(a_ts4):F1} °C; ");

            add_message_register
            (
                Message_Register_ID.DA_STATUS_VII,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_gauge_status_a
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 64)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_true_rem_charge, a_data, ref a_index);
        Misc.decode_le(out ushort a_true_rem_energy, a_data, ref a_index);
        Misc.decode_le(out ushort a_init_charge, a_data, ref a_index);
        Misc.decode_le(out ushort a_init_energy, a_data, ref a_index);
        Misc.decode_le(out ushort a_true_fcc_charge, a_data, ref a_index);
        Misc.decode_le(out ushort a_true_fcc_energy, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_sim, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_amb, a_data, ref a_index);
        Misc.decode_le(out ushort a_ra_scale_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_ra_scale_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_ra_scale_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_ra_scale_c4, a_data, ref a_index);
        Misc.decode_le(out ushort a_comp_resist_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_comp_resist_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_comp_resist_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_comp_resist_c4, a_data, ref a_index);
        Misc.decode_le(out byte a_pack_grid, a_data, ref a_index);
        Misc.decode_le(out byte a_learned_status, a_data, ref a_index);
        Misc.decode_le(out byte a_grid_c1, a_data, ref a_index);
        Misc.decode_le(out byte a_grid_c2, a_data, ref a_index);
        Misc.decode_le(out byte a_grid_c3, a_data, ref a_index);
        Misc.decode_le(out byte a_grid_c4, a_data, ref a_index);
        Misc.decode_le(out ushort a_dod0_time, a_data, ref a_index);
        Misc.decode_le(out uint a_state_time, a_data, ref a_index);
        Misc.decode_le(out ushort a_dod0_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_dod0_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_dod0_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_dod0_c4, a_data, ref a_index);
        Misc.decode_le(out ushort a_dod0_passed_charge, a_data, ref a_index);
        Misc.decode_le(out ushort a_dod0_passed_energy, a_data, ref a_index);
        Misc.decode_le(out ushort a_dodeoc_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_dodeoc_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_dodeoc_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_dodeoc_c4, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"True Rem Charge: {0.001 * a_true_rem_charge:F3} Ah; ")
            .Append($"True Rem Energy: {0.01 * a_true_rem_energy:F2} Wh; ")
            .Append($"Initial Charge: {0.001 * a_init_charge:F3} Ah; ")
            .Append($"Initial Energy: {0.01 * a_init_energy:F2} Wh; ");

            add_message_register
            (
                Message_Register_ID.GAUGE_STATUS_A_I,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"True FCC Charge: {0.001 * a_true_fcc_charge:F3} Ah; ")
            .Append($"True FCC Energy: {0.01 * a_true_fcc_energy:F2} Wh; ")
            .Append($"Sim Temp: {to_celcius(a_temp_sim):F1} °C; ")
            .Append($"Ambient Temp: {to_celcius(a_temp_amb):F1} °C; ");

            add_message_register
            (
                Message_Register_ID.GAUGE_STATUS_A_II,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 RA Scale: {a_ra_scale_c1}; ")
            .Append($"Cell 2 RA Scale: {a_ra_scale_c2}; ")
            .Append($"Cell 3 RA Scale: {a_ra_scale_c3}; ")
            .Append($"Cell 4 RA Scale: {a_ra_scale_c4}; ");

            add_message_register
            (
                Message_Register_ID.GAUGE_STATUS_A_III,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 Cmp Rsist: {0.9765625 * a_comp_resist_c1:F7} mΩ; ")
            .Append($"Cell 2 Cmp Rsist: {0.9765625 * a_comp_resist_c2:F7} mΩ; ")
            .Append($"Cell 3 Cmp Rsist: {0.9765625 * a_comp_resist_c3:F7} mΩ; ")
            .Append($"Cell 4 Cmp Rsist: {0.9765625 * a_comp_resist_c4:F7} mΩ; ");

            add_message_register
            (
                Message_Register_ID.GAUGE_STATUS_A_IV,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Pack Grid Point: {a_pack_grid}; ")
            .Append($"Learned Status: 0x{a_learned_status:X2}; ");

            add_message_register
            (
                Message_Register_ID.GAUGE_STATUS_A_V,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 Grid Point: {a_grid_c1}; ")
            .Append($"Cell 2 Grid Point: {a_grid_c2}; ")
            .Append($"Cell 3 Grid Point: {a_grid_c3}; ")
            .Append($"Cell 4 Grid Point: {a_grid_c4}; ");

            add_message_register
            (
                Message_Register_ID.GAUGE_STATUS_A_VI,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"State Time: {a_state_time} s; ")
            .Append($"DOD0 Passed Charge: {0.001 * a_dod0_passed_charge:F3} Ah; ")
            .Append($"DOD0 Passed Energy: {0.01 * a_dod0_passed_energy:F2} Wh; ")
            .Append($"DOD0 Time: {3.75 * a_dod0_time:F2} min; ");

            add_message_register
            (
                Message_Register_ID.GAUGE_STATUS_A_VII,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 DOD0: {a_dod0_c1}; ")
            .Append($"Cell 2 DOD0: {a_dod0_c2}; ")
            .Append($"Cell 3 DOD0: {a_dod0_c3}; ")
            .Append($"Cell 4 DOD0: {a_dod0_c4}; ");

            add_message_register
            (
                Message_Register_ID.GAUGE_STATUS_A_VIII,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 DODEOC: {a_dodeoc_c1}; ")
            .Append($"Cell 2 DODEOC: {a_dodeoc_c2}; ")
            .Append($"Cell 3 DODEOC: {a_dodeoc_c3}; ")
            .Append($"Cell 4 DODEOC: {a_dodeoc_c4}; ");

            add_message_register
            (
                Message_Register_ID.GAUGE_STATUS_A_IX,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_gauge_status_b
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 24)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_qmax_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_qmax_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_qmax_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_qmax_c4, a_data, ref a_index);
        Misc.decode_le(out ushort a_qmax_dod0_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_qmax_dod0_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_qmax_dod0_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_qmax_dod0_c4, a_data, ref a_index);
        Misc.decode_le(out ushort a_qmax_passed_charge, a_data, ref a_index);
        Misc.decode_le(out ushort a_qmax_time, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_k, a_data, ref a_index);
        Misc.decode_le(out ushort a_temp_a, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 QMax: {0.001 * a_qmax_c1:F3} Ah; ")
            .Append($"Cell 2 QMax: {0.001 * a_qmax_c2:F3} Ah; ")
            .Append($"Cell 3 QMax: {0.001 * a_qmax_c3:F3} Ah; ")
            .Append($"Cell 4 QMax: {0.001 * a_qmax_c4:F3} Ah; ");

            add_message_register
            (
                Message_Register_ID.GAUGE_STATUS_B_I,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 QMax DOD0: {a_qmax_dod0_c1}; ")
            .Append($"Cell 2 QMax DOD0: {a_qmax_dod0_c2}; ")
            .Append($"Cell 3 QMax DOD0: {a_qmax_dod0_c3}; ")
            .Append($"Cell 4 QMax DOD0: {a_qmax_dod0_c4}; ");

            add_message_register
            (
                Message_Register_ID.GAUGE_STATUS_B_II,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"QMax Passed Charge: {0.001 * a_qmax_passed_charge:F3} Ah; ")
            .Append($"QMax Time: {3.75 * a_qmax_time:F2} min; ")
            .Append($"Temp k: {a_temp_k}; ")
            .Append($"Temp a: {a_temp_a}; ");

            add_message_register
            (
                Message_Register_ID.GAUGE_STATUS_B_III,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_cb_status
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 20)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_bal_time_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_bal_time_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_bal_time_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_bal_time_c4, a_data, ref a_index);
        Misc.decode_le(out ushort a_bal_dod_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_bal_dod_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_bal_dod_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_bal_dod_c4, a_data, ref a_index);
        Misc.decode_le(out ushort a_total_dod_charge, a_data, ref a_index);
        Misc.decode_le(out ushort _, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 Bal Time: {a_bal_time_c1} s; ")
            .Append($"Cell 2 Bal Time: {a_bal_time_c2} s; ")
            .Append($"Cell 3 Bal Time: {a_bal_time_c3} s; ")
            .Append($"Cell 4 Bal Time: {a_bal_time_c4} s; ");

            add_message_register
            (
                Message_Register_ID.CB_STATUS_I,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 Bal DOD: {a_bal_dod_c1}; ")
            .Append($"Cell 2 Bal DOD: {a_bal_dod_c2}; ")
            .Append($"Cell 3 Bal DOD: {a_bal_dod_c3}; ")
            .Append($"Cell 4 Bal DOD: {a_bal_dod_c4}; ")
            .Append($"Total DOD Charge: {a_total_dod_charge}; ");

            add_message_register
            (
                Message_Register_ID.CB_STATUS_II,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_afe_register
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 24)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out byte a_int_status, a_data, ref a_index);
        Misc.decode_le(out byte a_fet_status, a_data, ref a_index);
        Misc.decode_le(out byte a_rxin, a_data, ref a_index);
        Misc.decode_le(out byte a_latch_status, a_data, ref a_index);
        Misc.decode_le(out byte a_int_enable, a_data, ref a_index);
        Misc.decode_le(out byte a_fet_control, a_data, ref a_index);
        Misc.decode_le(out byte a_rxien, a_data, ref a_index);
        Misc.decode_le(out byte a_rlout, a_data, ref a_index);
        Misc.decode_le(out byte a_rhout, a_data, ref a_index);
        Misc.decode_le(out byte a_rhint, a_data, ref a_index);
        Misc.decode_le(out byte a_cell_balance, a_data, ref a_index);
        Misc.decode_le(out byte a_adc_control, a_data, ref a_index);
        Misc.decode_le(out byte a_adc_mux_control, a_data, ref a_index);
        Misc.decode_le(out byte a_led_control, a_data, ref a_index);
        Misc.decode_le(out byte a_control, a_data, ref a_index);
        Misc.decode_le(out byte a_timer_control, a_data, ref a_index);
        Misc.decode_le(out byte a_protection, a_data, ref a_index);
        Misc.decode_le(out byte a_ocd, a_data, ref a_index);
        Misc.decode_le(out byte a_scc, a_data, ref a_index);
        Misc.decode_le(out byte a_scd1, a_data, ref a_index);
        Misc.decode_le(out byte a_scd2, a_data, ref a_index);
        Misc.decode_le(out byte _, a_data, ref a_index);
        Misc.decode_le(out byte _, a_data, ref a_index);
        Misc.decode_le(out byte _, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Int Status: 0x{a_int_status:X2}; ")
            .Append($"FET Status: 0x{a_fet_status:X2}; ")
            .Append($"RXIN: 0x{a_rxin:X2}; ")
            .Append($"Latch Status: 0x{a_latch_status:X2}; ");

            add_message_register
            (
                Message_Register_ID.AFE_REGISTER_I,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Int Enable: 0x{a_int_enable:X2}; ")
            .Append($"FET Control: 0x{a_fet_control:X2}; ")
            .Append($"RXIEN: 0x{a_rxien:X2}; ")
            .Append($"RLOUT: 0x{a_rlout:X2}; ");

            add_message_register
            (
                Message_Register_ID.AFE_REGISTER_II,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"RHOUT: 0x{a_rhout:X2}; ")
            .Append($"RHINT: 0x{a_rhint:X2}; ")
            .Append($"Cell Balance: 0x{a_cell_balance:X2}; ")
            .Append($"ADC Control: 0x{a_adc_control:X2}; ");

            add_message_register
            (
                Message_Register_ID.AFE_REGISTER_III,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"ADC MUX Control: 0x{a_adc_mux_control:X2}; ")
            .Append($"LED Control: 0x{a_led_control:X2}; ")
            .Append($"Control: 0x{a_control:X2}; ")
            .Append($"Timer Control: 0x{a_timer_control:X2}; ");

            add_message_register
            (
                Message_Register_ID.AFE_REGISTER_IV,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Protection: 0x{a_protection:X2}; ")
            .Append($"OCD: 0x{a_ocd:X2}; ")
            .Append($"SCC: 0x{a_scc:X2}; ")
            .Append($"SCD1: 0x{a_scd1:X2}; ")
            .Append($"SCD2: 0x{a_scd2:X2}; ");

            add_message_register
            (
                Message_Register_ID.AFE_REGISTER_V,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_lifetime_data_a
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 64)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_max_volt_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_max_volt_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_max_volt_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_max_volt_c4, a_data, ref a_index);
        Misc.decode_le(out ushort a_min_volt_c1, a_data, ref a_index);
        Misc.decode_le(out ushort a_min_volt_c2, a_data, ref a_index);
        Misc.decode_le(out ushort a_min_volt_c3, a_data, ref a_index);
        Misc.decode_le(out ushort a_min_volt_c4, a_data, ref a_index);
        Misc.decode_le(out ushort a_max_volt_delta, a_data, ref a_index);
        Misc.decode_le(out short a_max_charge_curr, a_data, ref a_index);
        Misc.decode_le(out short a_max_dischg_curr, a_data, ref a_index);
        Misc.decode_le(out short a_max_avg_dischg_curr, a_data, ref a_index);
        Misc.decode_le(out short a_max_avg_dischg_powr, a_data, ref a_index);
        Misc.decode_le(out ushort a_max_cell_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_min_cell_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_max_cell_temp_delta, a_data, ref a_index);
        Misc.decode_le(out ushort a_max_int_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_min_int_temp, a_data, ref a_index);
        Misc.decode_le(out ushort a_max_fet_temp, a_data, ref a_index);
        Misc.decode_le(out byte a_nmbr_shutdowns, a_data, ref a_index);
        Misc.decode_le(out byte a_nmbr_partial_resets, a_data, ref a_index);
        Misc.decode_le(out byte a_nmbr_full_resets, a_data, ref a_index);
        Misc.decode_le(out byte a_nmbr_wdt_resets, a_data, ref a_index);
        Misc.decode_le(out byte a_cb_time_c1, a_data, ref a_index);
        Misc.decode_le(out byte a_cb_time_c2, a_data, ref a_index);
        Misc.decode_le(out byte a_cb_time_c3, a_data, ref a_index);
        Misc.decode_le(out byte a_cb_time_c4, a_data, ref a_index);
        Misc.decode_le(out ushort a_total_fw_runtime, a_data, ref a_index);
        Misc.decode_le(out ushort a_time_spent_ut, a_data, ref a_index);
        Misc.decode_le(out ushort a_time_spent_lt, a_data, ref a_index);
        Misc.decode_le(out ushort a_time_spent_stl, a_data, ref a_index);
        Misc.decode_le(out ushort a_time_spent_rt, a_data, ref a_index);
        Misc.decode_le(out ushort a_time_spent_sth, a_data, ref a_index);
        Misc.decode_le(out ushort a_time_spent_ht, a_data, ref a_index);
        Misc.decode_le(out ushort a_time_spent_ot, a_data, ref a_index);
        Misc.decode_le(out ushort _, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 Max Volt: {0.001 * a_max_volt_c1:F3} V; ")
            .Append($"Cell 2 Max Volt: {0.001 * a_max_volt_c2:F3} V; ")
            .Append($"Cell 3 Max Volt: {0.001 * a_max_volt_c3:F3} V; ")
            .Append($"Cell 4 Max Volt: {0.001 * a_max_volt_c4:F3} V; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_A_I,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 Min Volt: {0.001 * a_min_volt_c1:F3} V; ")
            .Append($"Cell 2 Min Volt: {0.001 * a_min_volt_c2:F3} V; ")
            .Append($"Cell 3 Min Volt: {0.001 * a_min_volt_c3:F3} V; ")
            .Append($"Cell 4 Min Volt: {0.001 * a_min_volt_c4:F3} V; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_A_II,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Max Charge Curr: {0.001 * a_max_charge_curr:F3} A; ")
            .Append($"Max Dischg Curr: {0.001 * a_max_dischg_curr:F3} A; ")
            .Append($"Max Avg Dischg Curr: {0.001 * a_max_avg_dischg_curr:F3} A; ")
            .Append($"Max Avg Dischg Powr: {0.01 * a_max_avg_dischg_powr:F2} W; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_A_III,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Max Cell Volt Δ: {0.001 * a_max_volt_delta:F3} V; ")
            .Append($"Max Cell Temp: {to_celcius(a_max_cell_temp):F1} °C; ")
            .Append($"Min Cell Temp: {to_celcius(a_min_cell_temp):F1} °C; ")
            .Append($"Max Cell Temp Δ: {to_celcius(a_max_cell_temp_delta):F1} °C; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_A_IV,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Max Internal Temp: {to_celcius(a_max_int_temp):F1} °C; ")
            .Append($"Min Internal Temp: {to_celcius(a_min_int_temp):F1} °C; ")
            .Append($"Max FET Temp: {to_celcius(a_max_fet_temp):F1} °C; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_A_V,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"# of Shutdowns: {a_nmbr_shutdowns}; ")
            .Append($"# of Partial Resets: {a_nmbr_partial_resets}; ")
            .Append($"# of Full Resets: {a_nmbr_full_resets}; ")
            .Append($"# of WDT Resets: {a_nmbr_wdt_resets}; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_A_VI,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Cell 1 CB Time: {2 * a_cb_time_c1} h; ")
            .Append($"Cell 2 CB Time: {2 * a_cb_time_c2} h; ")
            .Append($"Cell 3 CB Time: {2 * a_cb_time_c3} h; ")
            .Append($"Cell 4 CB Time: {2 * a_cb_time_c4} h; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_A_VII,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Total FW Runtime: {2 * a_total_fw_runtime} h; ")
            .Append($"Time Spent UT: {2 * a_time_spent_ut} h; ")
            .Append($"Time Spent LT: {2 * a_time_spent_lt} h; ")
            .Append($"Time Spent STL: {2 * a_time_spent_stl} h; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_A_VIII,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Time Spent RT: {2 * a_time_spent_rt} h; ")
            .Append($"Time Spent STH: {2 * a_time_spent_sth} h; ")
            .Append($"Time Spent HT: {2 * a_time_spent_ht} h; ")
            .Append($"Time Spent OT: {2 * a_time_spent_ot} h; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_A_IX,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_lifetime_data_b
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 64)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out ushort a_nmbr_event_cov, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_event_cov, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_event_cuv, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_event_cuv, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_event_ocd1, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_event_ocd1, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_event_ocd2, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_event_ocd2, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_event_occ1, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_event_occ1, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_event_occ2, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_event_occ2, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_event_aold, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_event_aold, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_event_ascd, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_event_ascd, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_event_ascc, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_event_ascc, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_event_otc, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_event_otc, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_event_otd, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_event_otd, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_event_otf, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_event_otf, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_valid_charge_term, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_valid_charge_term, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_qmax_update, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_qmax_update, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_ra_update, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_ra_update, a_data, ref a_index);
        Misc.decode_le(out ushort a_nmbr_ra_disable, a_data, ref a_index);
        Misc.decode_le(out ushort a_last_ra_disable, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"# of COV Event: {a_nmbr_event_cov}; ")
            .Append($"Last COV Event: {a_last_event_cov}; ")
            .Append($"# of CUV Event: {a_nmbr_event_cuv}; ")
            .Append($"Last CUV Event: {a_last_event_cuv}; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_B_I,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"# of OCD1 Event: {a_nmbr_event_ocd1}; ")
            .Append($"Last OCD1 Event: {a_last_event_ocd1}; ")
            .Append($"# of OCD2 Event: {a_nmbr_event_ocd2}; ")
            .Append($"Last OCD2 Event: {a_last_event_ocd2}; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_B_II,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"# of OCC1 Event: {a_nmbr_event_occ1}; ")
            .Append($"Last OCC1 Event: {a_last_event_occ1}; ")
            .Append($"# of OCC2 Event: {a_nmbr_event_occ2}; ")
            .Append($"Last OCC2 Event: {a_last_event_occ2}; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_B_III,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"# of AOLD Event: {a_nmbr_event_aold}; ")
            .Append($"Last AOLD Event: {a_last_event_aold}; ")
            .Append($"# of ASCD Event: {a_nmbr_event_ascd}; ")
            .Append($"Last ASCD Event: {a_last_event_ascd}; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_B_IV,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"# of ASCC Event: {a_nmbr_event_ascc}; ")
            .Append($"Last ASCC Event: {a_last_event_ascc}; ")
            .Append($"# of OTC Event: {a_nmbr_event_otc}; ")
            .Append($"Last OTC Event: {a_last_event_otc}; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_B_V,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"# of OTD Event: {a_nmbr_event_otd}; ")
            .Append($"Last OTD Event: {a_last_event_otd}; ")
            .Append($"# of OTF Event: {a_nmbr_event_otf}; ")
            .Append($"Last OTF Event: {a_last_event_otf}; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_B_VI,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"# of Valid Charge Term: {a_nmbr_valid_charge_term}; ")
            .Append($"Last Valid Charge Term: {a_last_valid_charge_term}; ")
            .Append($"# of QMax Update: {a_nmbr_qmax_update}; ")
            .Append($"Last QMax Update: {a_last_qmax_update}; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_B_VII,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"# of RA Update: {a_nmbr_ra_update}; ")
            .Append($"Last RA Update: {a_last_ra_update}; ")
            .Append($"# of RA Disable: {a_nmbr_ra_disable}; ")
            .Append($"Last RA Disable: {a_last_ra_disable}; ");

            add_message_register
            (
                Message_Register_ID.LIFETIME_DATA_B_VIII,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_misc_data
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 48)
        {
            return false;
        }

        var a_manuf_info_i = a_data[0..16];
        var a_manuf_info_ii = a_data[16..32];
        var a_manuf_info_iii = a_data[32..36];
        var a_index = 36;

        Misc.decode_le(out ushort a_soh_fcc, a_data, ref a_index);
        Misc.decode_le(out ushort a_soh_energy, a_data, ref a_index);
        Misc.decode_le(out ushort a_filt_rc, a_data, ref a_index);
        Misc.decode_le(out ushort a_filt_re, a_data, ref a_index);
        Misc.decode_le(out ushort a_filt_fcc, a_data, ref a_index);
        Misc.decode_le(out ushort a_filt_fce, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ = a_guard.value.Append($"Manufacturer Info: [");

            foreach(var a_byte in a_manuf_info_i[..^1])
            {
                _ = a_guard.value.Append($"{a_byte:X2}:");
            }

            _ = a_guard.value.Append($"{a_manuf_info_i[^1]:X2}]; ");

            add_message_register
            (
                Message_Register_ID.MISC_DATA_I,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ = a_guard.value.Append($"Manufacturer Info: [");

            foreach(var a_byte in a_manuf_info_ii[..^1])
            {
                _ = a_guard.value.Append($"{a_byte:X2}:");
            }

            _ = a_guard.value.Append($"{a_manuf_info_ii[^1]:X2}]; ");

            add_message_register
            (
                Message_Register_ID.MISC_DATA_II,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ = a_guard.value.Append($"Manufacturer Info B: [");

            foreach(var a_byte in a_manuf_info_iii[..^1])
            {
                _ = a_guard.value.Append($"{a_byte:X2}:");
            }

            _ = a_guard.value.Append($"{a_manuf_info_iii[^1]:X2}]; ");

            add_message_register
            (
                Message_Register_ID.MISC_DATA_III,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"SoH FCC: {0.001 * a_soh_fcc:F3} Ah; ")
            .Append($"SoH Energy: {0.01 * a_soh_energy:F2} Wh; ");

            add_message_register
            (
                Message_Register_ID.MISC_DATA_IV,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"Filtered RC: {0.001 * a_filt_rc:F3} Ah; ")
            .Append($"Filtered RE: {0.01 * a_filt_re:F2} Wh; ")
            .Append($"Filtered FCC: {0.001 * a_filt_fcc:F3} Ah; ")
            .Append($"Filtered FCE: {0.01 * a_filt_fce:F2} Wh; ");

            add_message_register
            (
                Message_Register_ID.MISC_DATA_V,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_serial_number
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 20)
        {
            return false;
        }

        var a_index = 0;

        Misc.decode_le(out uint a_uc_serial_a, a_data, ref a_index);
        Misc.decode_le(out uint a_uc_serial_b, a_data, ref a_index);
        Misc.decode_le(out uint a_uc_serial_c, a_data, ref a_index);
        Misc.decode_le(out uint a_pack_serial, a_data, ref a_index);
        Misc.decode_le(out byte a_build_dd, a_data, ref a_index);
        Misc.decode_le(out byte a_build_mm, a_data, ref a_index);
        Misc.decode_le(out ushort a_build_yyyy, a_data, ref a_index);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ =
            a_guard.value
            .Append($"µController Serial: 0x{a_uc_serial_c:X8}{a_uc_serial_b:X8}{a_uc_serial_a:X8}; ")
            .Append($"Pack Serial: {a_pack_serial:D10}; ")
            .Append($"Manufacture Date (dd/mm/yyyy): {a_build_dd:D2}/{a_build_mm:D2}/{a_build_yyyy:D4}; ");

            add_message_register
            (
                Message_Register_ID.SERIAL_NUMBER,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    private bool
    parse_message_part_number
    (CAN_ID a_id, in ReadOnlySpan<byte> a_data)
    {
        if(a_data.Length is not 12)
        {
            return false;
        }

        var a_part_number = Encoding.ASCII.GetString(a_data).TrimEnd((char)0);

        {
            using var a_guard = String_Builder_Pool.acquire();

            _ = a_guard.value.Append($"Part Number: {a_part_number}; ");

            add_message_register
            (
                Message_Register_ID.PART_NUMBER,
                a_id,
                a_data,
                a_guard.value.ToString()
            );
        }

        return true;
    }

    #endregion

    #region QUERIES

    private void
    add_query
    (Message_Number a_message_number, string a_text) =>
        add_query(a_message_number, [], a_text);

    private void
    add_query
    (Message_Number a_message_number, ReadOnlySpan<byte> a_data, string a_text)
    {
        _ =
        a_message_number switch
        {
            Message_Number.WAKE_S => false,
            Message_Number.CORE_STATS_S => false,
            Message_Number.VOLTAGE_S => false,
            Message_Number.CURRENT_S => false,
            Message_Number.DESIGN_S => false,
            Message_Number.STATUS_A_S => false,
            Message_Number.STATUS_B_S => false,
            Message_Number.DA_STATUS_S => false,
            Message_Number.GAUGE_STATUS_A_S => false,
            Message_Number.GAUGE_STATUS_B_S => false,
            Message_Number.CB_STATUS_S => false,
            Message_Number.AFE_REGISTER_S => false,
            Message_Number.LIFETIME_DATA_A_S => false,
            Message_Number.LIFETIME_DATA_B_S => false,
            Message_Number.MISC_DATA_S => false,
            Message_Number.SERIAL_NUMBER_S => false,
            Message_Number.PART_NUMBER_S => false,
            _ => throw new ArgumentOutOfRangeException(nameof(a_message_number))
        };

        const uint MSG = 0x1AD77700u;

        var a_msg = (uint)a_message_number & 0xFFu;

        using var a_guard = String_Builder_Pool.acquire();

        add_outgoing_can_message
        (
            new
            (
                new()
                {
                    ext_id = MSG | a_msg,
                    is_can_fd = true,
                    is_bitrate_switch = false,
                    is_error_passive = false,
                    size = a_data.Length
                },
                a_data
            )
            {
                id_interpreted = a_guard.value.Append($"MSG={a_msg:X2}").ToString(),
                data_interpreted = a_text
            }
        );
    }

    private static readonly ReadOnlyMemory<byte> s_deadbeef = new byte[] { 0xDE, 0xAD, 0xBE, 0xEF };

    private bool
    process_query_wake()
    {
        add_query(Message_Number.WAKE_S, s_deadbeef.Span, "Wake");

        return true;
    }

    private bool
    process_query_core_stats()
    {
        add_query(Message_Number.CORE_STATS_S, "Query Core Stats");

        return true;
    }

    private bool
    process_query_voltage()
    {
        add_query(Message_Number.VOLTAGE_S, "Query Voltage");

        return true;
    }

    private bool
    process_query_current()
    {
        add_query(Message_Number.CURRENT_S, "Query Current");

        return true;
    }

    private bool
    process_query_design()
    {
        add_query(Message_Number.DESIGN_S, "Query Design");

        return true;
    }

    private bool
    process_query_status_a()
    {
        add_query(Message_Number.STATUS_A_S, "Query Status A");

        return true;
    }

    private bool
    process_query_status_b()
    {
        add_query(Message_Number.STATUS_B_S, "Query Status B");

        return true;
    }

    private bool
    process_query_da_status()
    {
        add_query(Message_Number.DA_STATUS_S, "Query DA Status");

        return true;
    }

    private bool
    process_query_gauge_status_a()
    {
        add_query(Message_Number.GAUGE_STATUS_A_S, "Query Gauge Status A");

        return true;
    }

    private bool
    process_query_gauge_status_b()
    {
        add_query(Message_Number.GAUGE_STATUS_B_S, "Query Gauge Status B");

        return true;
    }

    private bool
    process_query_cb_status()
    {
        add_query(Message_Number.CB_STATUS_S, "Query CB Status");

        return true;
    }

    private bool
    process_query_afe_register()
    {
        add_query(Message_Number.AFE_REGISTER_S, "Query AFE Regsiter");

        return true;
    }

    private bool
    process_query_lifetime_data_a()
    {
        add_query(Message_Number.LIFETIME_DATA_A_S, "Query Lifetime Data A");

        return true;
    }

    private bool
    process_query_lifetime_data_b()
    {
        add_query(Message_Number.LIFETIME_DATA_B_S, "Query Lifetime Data B");

        return true;
    }

    private bool
    process_query_misc_data()
    {
        add_query(Message_Number.MISC_DATA_S, "Query Misc Data");

        return true;
    }

    private bool
    process_query_serial_number()
    {
        add_query(Message_Number.SERIAL_NUMBER_S, "Query Serial Number");

        return true;
    }

    private bool
    process_query_part_number()
    {
        add_query(Message_Number.PART_NUMBER_S, "Query Part Number");

        return true;
    }

    private bool
    process_query_all()
    {
        const string ALL = "Query All";

        add_query(Message_Number.WAKE_S, s_deadbeef.Span, ALL);
        add_query(Message_Number.CORE_STATS_S, ALL);
        add_query(Message_Number.VOLTAGE_S, ALL);
        add_query(Message_Number.CURRENT_S, ALL);
        add_query(Message_Number.DESIGN_S, ALL);
        add_query(Message_Number.STATUS_A_S, ALL);
        add_query(Message_Number.STATUS_B_S, ALL);
        add_query(Message_Number.DA_STATUS_S, ALL);
        add_query(Message_Number.GAUGE_STATUS_A_S, ALL);
        add_query(Message_Number.GAUGE_STATUS_B_S, ALL);
        add_query(Message_Number.CB_STATUS_S, ALL);
        add_query(Message_Number.AFE_REGISTER_S, ALL);
        add_query(Message_Number.LIFETIME_DATA_A_S, ALL);
        add_query(Message_Number.LIFETIME_DATA_B_S, ALL);
        add_query(Message_Number.MISC_DATA_S, ALL);
        add_query(Message_Number.SERIAL_NUMBER_S, ALL);
        add_query(Message_Number.PART_NUMBER_S, ALL);

        return true;
    }

    #endregion

    #region COMMANDS

    private void
    add_command
    (Command_Number a_command_number, in ReadOnlySpan<byte> a_arguments, string a_text)
    {
        const uint MSG = 0x1AD77700u | (uint)Message_Number.COMMAND_S;

        Span<byte> a_data = stackalloc byte[4 + a_arguments.Length];

        var a_index = 0;

        Misc.encode_le((ushort)a_command_number, a_data, ref a_index);
        Misc.encode_le((ushort)Command_Error.NONE, a_data, ref a_index);

        a_arguments.CopyTo(a_data[a_index..]);

        using var a_g1 = String_Builder_Pool.acquire();
        using var a_g2 = String_Builder_Pool.acquire();

        add_outgoing_can_message
        (
            new
            (
                new()
                {
                    ext_id = MSG,
                    is_can_fd = true,
                    is_error_passive = false,
                    is_bitrate_switch = false,
                    size = a_data.Length
                },
                a_data
            )
            {
                id_interpreted = a_g1.value.Append($"MSG={MSG & 0xFFu:X2}").ToString(),
                data_interpreted = a_g2.value.Append($"Command 0x{(uint)a_command_number & 0xFFFFu:X4}: {a_text}").ToString()
            }
        );
    }

    private bool
    process_command_fets_off()
    {
        add_command(Command_Number.FETS_OFF, [], "FETs Off");

        return true;
    }

    private bool
    process_command_fets_on()
    {
        add_command(Command_Number.FETS_ON, [], "FETs On");

        return true;
    }

    private bool
    process_command_set_serial_number
    (string a_arg0)
    {
        var a_serial = uint.Parse(a_arg0, NumberStyles.None);

        Span<byte> a_data = stackalloc byte[4];

        var a_index = 0;

        Misc.encode_le(a_serial, a_data, ref a_index);

        add_command(Command_Number.SET_SERIAL_NUMBER, a_data, $"Set Serial Number: {a_serial}");

        return true;
    }

    private bool
    process_command_set_build_date
    (string a_arg0, string a_arg1, string a_arg2)
    {
        var a_day = byte.Parse(a_arg0, NumberStyles.None);
        var a_month = byte.Parse(a_arg1, NumberStyles.None);
        var a_year = ushort.Parse(a_arg2, NumberStyles.None);

        Span<byte> a_data = stackalloc byte[4];

        var a_index = 0;

        Misc.encode_le(a_day, a_data, ref a_index);
        Misc.encode_le(a_month, a_data, ref a_index);
        Misc.encode_le(a_year, a_data, ref a_index);

        add_command(Command_Number.SET_BUILD_DATE, a_data, $"Set Manufacture Date: {a_day:D2}/{a_month:D2}/{a_year:D4}");

        return true;
    }

    private bool
    process_command_fg_unseal
    (string a_arg0)
    {
        var a_key = uint.Parse(a_arg0, NumberStyles.AllowHexSpecifier);

        Span<byte> a_data = stackalloc byte[4];

        var a_index = 0;

        Misc.encode_le(a_key, a_data, ref a_index);

        add_command(Command_Number.FG_UNSEAL, a_data, $"Unseal Fuel Gauge: 0x{a_key:X8}");

        return true;
    }

    private bool
    process_command_fg_unseal_full
    (string a_arg0)
    {
        var a_key = uint.Parse(a_arg0, NumberStyles.AllowHexSpecifier);

        Span<byte> a_data = stackalloc byte[4];

        var a_index = 0;

        Misc.encode_le(a_key, a_data, ref a_index);

        add_command(Command_Number.FG_UNSEAL_FULL, a_data, $"Unseal Fuel Gauge (full): 0x{a_key:X8}");

        return true;
    }

    private bool
    process_command_fg_reset()
    {
        add_command(Command_Number.FG_RESET, [], "Reset Fuel Gauge");

        return true;
    }

    private bool
    process_command_fg_gauging_enable()
    {
        add_command(Command_Number.FG_GAUGING_ENABLE, [], "Gauging Enable");

        return true;
    }

    private bool
    process_command_fg_lifetime_enable()
    {
        add_command(Command_Number.FG_LIFETIME_ENABLE, [], "Lieftime Enable");

        return true;
    }

    private bool
    process_command_fg_pf_enable()
    {
        add_command(Command_Number.FG_PF_ENABLE, [], "PF Enable");

        return true;
    }

    private bool
    process_command_fg_bbr_enable()
    {
        add_command(Command_Number.FG_BBR_ENABLE, [], "BBR Enable");

        return true;
    }

    private bool
    process_command_fg_seal()
    {
        add_command(Command_Number.FG_SEAL, [], "Seal Fuel Gauge");

        return true;
    }

    private bool
    process_command_force_led
    (byte a_code)
    {
        add_command(Command_Number.FORCE_LED, [a_code], "Force LED");

        return true;
    }

    private bool
    process_command_rdp_enable()
    {
        add_command(Command_Number.RDP_ENABLE, [], "Readout Protect Enable");

        return true;
    }

    private bool
    process_command_reset_request()
    {
        add_command(Command_Number.RESET_REQUEST, [], "Request Reset");

        return true;
    }

    private bool
    process_command_jtag_connect()
    {
        add_command(Command_Number.JTAG_CONNECT, [], "JTAG Connect");

        return true;
    }

    private bool
    process_command_isqc_connect()
    {
        add_command(Command_Number.ISQC_CONNECT, [], "I2C Connect");

        return true;
    }

    private bool
    process_command_disconnect_idle()
    {
        add_command(Command_Number.DISCONNECT_IDLE, [], "Disconnect");

        return true;
    }

    private bool
    process_command_fg_program()
    {
        add_command(Command_Number.FG_PROGRAM, [], "Program Fuel Gauge");

        return true;
    }

    private bool
    process_command_fg_cal_cc_offset()
    {
        add_command(Command_Number.FG_CAL_CC_OFFSET, [], "Calibrate FG CC Offset");

        return true;
    }

    private bool
    process_command_fg_cal_board_offset()
    {
        add_command(Command_Number.FG_CAL_BOARD_OFFSET, [], "Calibrate FG Board Offset");

        return true;
    }

    private bool
    process_command_fg_cal_voltage
    (string a_arg0, string a_arg1, string a_arg2)
    {
        const double MIN_LIMIT = 3.0;
        const double MAX_LIMIT = 4.2;

        var a_cell_volt = double.Parse(a_arg0, NumberStyles.Float);
        var a_batt_volt = double.Parse(a_arg1, NumberStyles.Float);
        var a_pack_volt = double.Parse(a_arg2, NumberStyles.Float);

        if(a_cell_volt is < MIN_LIMIT or > MAX_LIMIT)
        {
            throw new ArgumentException($"Calibrate Voltage: cell volt ({a_cell_volt:F3}V) must be >= {MIN_LIMIT:F3}V and <= {MAX_LIMIT:F3}V");
        }

        if(a_batt_volt is < 2 * MIN_LIMIT or > 2 * MAX_LIMIT)
        {
            throw new ArgumentException($"Calibrate Voltage: batt volt ({a_batt_volt:F3}V) must be >= {2 * MIN_LIMIT:F3}V and <= {2 * MAX_LIMIT:F3}V");
        }

        if(a_pack_volt is < 2 * MIN_LIMIT or > 2 * MAX_LIMIT)
        {
            throw new ArgumentException($"Calibrate Voltage: pack volt ({a_pack_volt:F3}V) must be >= {2 * MIN_LIMIT:F3}V and <= {2 * MAX_LIMIT:F3}V");
        }

        Span<byte> a_data = stackalloc byte[12];

        var a_index = 0;

        Misc.encode_le((uint)(1000.0 * a_cell_volt), a_data, ref a_index);
        Misc.encode_le((uint)(1000.0 * a_batt_volt), a_data, ref a_index);
        Misc.encode_le((uint)(1000.0 * a_pack_volt), a_data, ref a_index);

        add_command(Command_Number.FG_CAL_VOLTAGE, a_data, $"Calibrate FG Voltage");

        return true;
    }

    private bool
    process_command_fg_cal_current
    (string a_arg0)
    {
        const double MIN_LIMIT = -10.0;
        const double MAX_LIMIT = -1.0;

        var a_curr = double.Parse(a_arg0, NumberStyles.Float);

        if(a_curr is < MIN_LIMIT or > MAX_LIMIT)
        {
            throw new ArgumentException($"Calibrate Current: curr ({a_curr:F3}V) must be >= {MIN_LIMIT:F3}V and <= {MAX_LIMIT:F3}V");
        }

        Span<byte> a_data = stackalloc byte[4];

        var a_index = 0;

        Misc.encode_le((int)(1000.0 * a_curr), a_data, ref a_index);

        add_command(Command_Number.FG_CAL_CURRENT, a_data, $"Calibrate FG Current");

        return true;
    }

    #endregion

    private static double
    to_celcius
    (ushort a_raw) => 0.1 * a_raw - 273.1;
}
