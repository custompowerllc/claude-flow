using System;
using System.Collections.Generic;
using System.IO;
using serial;
using Tomlyn;
using Tomlyn.Model;
using utility.can;

namespace program_ns.processing;

internal sealed class
Config_Data
{
    public
    Config_Data
    (string a_file_name)
    {
        config_file_text = File.ReadAllText(a_file_name);

        var a_table = Toml.Parse(config_file_text).ToModel();

        general = new(a_table);
        komodo = Komodo_Table.make(a_table);
        serial = Serial_Table.make(a_table);
        modbus = Modbus_Table.make(a_table);
        bootloader = Bootloader_Table.make(a_table);

        if(komodo is null && serial is null && modbus is null)
        {
            throw new Exception("missing table");
        }
    }

    public string config_file_text { get; }

    public readonly struct
    General_Table
    {
        public
        General_Table
        (TomlTable a_table)
        {
            var a_tab = (TomlTable)a_table["general"];

            title = (string)a_tab["title"];
            device = (string)a_tab["device"];
        }

        public string title { get; }
        public string device { get; }
    }

    public General_Table general { get; }

    public readonly struct
    Komodo_Table
    {
        public static Komodo_Table?
        make(TomlTable a_table)
        {
            if(a_table.ContainsKey("komodo"))
            {
                return new((TomlTable)a_table["komodo"]);
            }

            return null;
        }

        private
        Komodo_Table
        (TomlTable a_tab)
        { 
            var a_port = (long)a_tab["port"];
            var a_bitrate = (long)a_tab["bitrate"];
            var a_timeout = (long)a_tab["timeout"];
            var a_latency = (long)a_tab["latency"];

            port = checked((uint)a_port);
            bitrate = checked((uint)a_bitrate);
            timeout = checked((uint)a_timeout);
            latency = checked((uint)a_latency);
            physical_loopback = (bool)a_tab["physical-loopback"];

            if(a_tab.ContainsKey("std-id-filter"))
            {
                var a_filter = (TomlTable)a_tab["std-id-filter"];

                var a_filter_and = (long)a_filter["filter-and"];
                var a_filter_cmp = (long)a_filter["filter-cmp"];
                var a_accept_rmt = (bool)a_filter["accept-rmt"];

                std_id_filter = (checked((uint)a_filter_and), checked((uint)a_filter_cmp), a_accept_rmt);
            }
            else
            {
                std_id_filter = null;
            }

            if(a_tab.ContainsKey("ext-id-filter"))
            {
                var a_filter = (TomlTable)a_tab["ext-id-filter"];

                var a_filter_and = (long)a_filter["filter-and"];
                var a_filter_cmp = (long)a_filter["filter-cmp"];
                var a_accept_rmt = (bool)a_filter["accept-rmt"];

                ext_id_filter = (checked((uint)a_filter_and), checked((uint)a_filter_cmp), a_accept_rmt);
            }
            else
            {
                ext_id_filter = null;
            }
        }

        public uint port { get; }
        public uint bitrate { get; }
        public uint timeout { get; }
        public uint latency { get; }
        public bool physical_loopback { get; }
        public (uint std_id_and, uint std_id_cmp, bool std_id_accept_rmt)? std_id_filter { get; }
        public (uint ext_id_and, uint ext_id_cmp, bool ext_id_accept_rmt)? ext_id_filter { get; }
    }

    public Komodo_Table? komodo { get; }

    public readonly struct
    Serial_Table
    {
        public static Serial_Table?
        make(TomlTable a_table)
        {
            if(a_table.ContainsKey("serial"))
            {
                return new((TomlTable)a_table["serial"]);
            }

            return null;
        }

        private
        Serial_Table
        (TomlTable a_tab)
        {
            var a_channel = (long)a_tab["channel"];

            channel = checked((uint)a_channel);

            var a_default_baud_rate = (long)a_tab["default-baud-rate"];

            default_baud_rate = checked((int)(uint)a_default_baud_rate);

            var a_data_bits = (long)a_tab["data-bits"];

            data_bits = checked((int)(uint)a_data_bits);

            parity_type =
                (string)a_tab["parity"] switch
                {
                    "none" => Serial_Device.Parity_Type.NONE,
                    "odd" => Serial_Device.Parity_Type.ODD,
                    "even" => Serial_Device.Parity_Type.EVEN,
                    _ => throw new Exception("invalid parity")
                };

            stop_bits =
                (string)a_tab["stop-bits"] switch
                {
                    "none" => Serial_Device.Stop_Bits.NONE,
                    "one" => Serial_Device.Stop_Bits.ONE,
                    "two" => Serial_Device.Stop_Bits.TWO,
                    "1.5" => Serial_Device.Stop_Bits.ONE_POINT_FIVE,
                    _ => throw new Exception("invalid stop-bits")
                };

            hand_shake = 
                (string)a_tab["handshake"] switch
                {
                    "none" => Serial_Device.Hand_Shake.NONE,
                    "xon-xoff" => Serial_Device.Hand_Shake.XON_XOFF,
                    "rts-cts" => Serial_Device.Hand_Shake.RTS_CTS,
                    "rts-cts-xon-xoff" => Serial_Device.Hand_Shake.RTS_CTS_XON_XOFF,
                    _ => throw new Exception("invalid handshake")
                };
        }

        public uint channel { get; }
        public int default_baud_rate { get; }
        public int data_bits { get; }
        public Serial_Device.Parity_Type parity_type { get; }
        public Serial_Device.Stop_Bits stop_bits { get; }
        public Serial_Device.Hand_Shake hand_shake { get; }
    }

    public Serial_Table? serial { get; }

    public readonly struct
    Modbus_Table
    {
        public static Modbus_Table?
        make(TomlTable a_table)
        {
            if(a_table.ContainsKey("modbus"))
            {
                return new((TomlTable)a_table["modbus"]);
            }

            return null;
        }

        private
        Modbus_Table
        (TomlTable a_tab)
        {
            translator = (string)a_tab["translator"];

            var a_default_baud_rate = (long)a_tab["default-baud-rate"];

            default_baud_rate = checked((int)(uint)a_default_baud_rate);

            var a_data_bits = (long)a_tab["data-bits"];

            data_bits = checked((int)(uint)a_data_bits);

            parity_type =
                (string)a_tab["parity"] switch
                {
                    "none" => Serial_Device.Parity_Type.NONE,
                    "odd" => Serial_Device.Parity_Type.ODD,
                    "even" => Serial_Device.Parity_Type.EVEN,
                    _ => throw new Exception("invalid parity")
                };

            stop_bits =
                (string)a_tab["stop-bits"] switch
                {
                    "none" => Serial_Device.Stop_Bits.NONE,
                    "one" => Serial_Device.Stop_Bits.ONE,
                    "two" => Serial_Device.Stop_Bits.TWO,
                    "1.5" => Serial_Device.Stop_Bits.ONE_POINT_FIVE,
                    _ => throw new Exception("invalid stop-bits")
                };

            hand_shake =
                (string)a_tab["handshake"] switch
                {
                    "none" => Serial_Device.Hand_Shake.NONE,
                    "xon-xoff" => Serial_Device.Hand_Shake.XON_XOFF,
                    "rts-cts" => Serial_Device.Hand_Shake.RTS_CTS,
                    "rts-cts-xon-xoff" => Serial_Device.Hand_Shake.RTS_CTS_XON_XOFF,
                    _ => throw new Exception("invalid handshake")
                };
        }

        public string translator { get; }
        public int default_baud_rate { get; }
        public int data_bits { get; }
        public Serial_Device.Parity_Type parity_type { get; }
        public Serial_Device.Stop_Bits stop_bits { get; }
        public Serial_Device.Hand_Shake hand_shake { get; }
    }

    public Modbus_Table? modbus { get; }

    public readonly struct
    Bootloader_Table
    {
        public static Bootloader_Table?
        make(TomlTable a_table)
        {
            if(a_table.ContainsKey("bootloader"))
            {
                return new((TomlTable)a_table["bootloader"]);
            }

            return null;
        }

        private
        Bootloader_Table
        (TomlTable a_tab)
        {
            var a_hex_file_content_raw = (TomlArray)a_tab["hex-file-content"];
            var a_devices_raw = (TomlArray)a_tab["upgrade-tasks"];

            var a_reboot_time_raw = (long)a_tab["reboot-time"];
            var a_reboot_time = checked((int)a_reboot_time_raw);

            var a_normal_timeout_raw = (long)a_tab["normal-timeout"];
            var a_normal_timeout = checked((int)a_normal_timeout_raw);

            var a_verify_timeout_raw = (long)a_tab["verify-timeout"];
            var a_verify_timeout = checked((int)a_verify_timeout_raw);

            if(a_reboot_time < CAN_Bootloader.MIN_REBOOT_TIME)
            {
                throw new Exception($"reboot-time '{a_reboot_time}' must be >= {CAN_Bootloader.MIN_REBOOT_TIME}");
            }

            if(a_normal_timeout < CAN_Bootloader.MIN_TIMEOUT)
            {
                throw new Exception($"normal-timeout '{a_normal_timeout}' must be >= {CAN_Bootloader.MIN_TIMEOUT}");
            }

            if(a_verify_timeout < CAN_Bootloader.MIN_TIMEOUT)
            {
                throw new Exception($"verify_timeout '{a_verify_timeout}' must be >= {CAN_Bootloader.MIN_TIMEOUT}");
            }

            hex_file_content = parse_hex_file_content(a_hex_file_content_raw);
            upgrade_tasks = parse_upgrade_tasks(a_devices_raw, a_hex_file_content_raw.Count);
            reboot_time = a_reboot_time;
            normal_timeout = a_normal_timeout;
            verify_timeout = a_verify_timeout;
            auto_exit = (bool)a_tab["auto-exit"];
        }

        public ReadOnlyMemory<(int max_size, string signature)> hex_file_content { get; }
        public ReadOnlyMemory<(int firmware_index, uint id_prefix)> upgrade_tasks { get; }
        public int reboot_time { get; }
        public int normal_timeout { get; }
        public int verify_timeout { get; }
        public bool auto_exit { get; }

        private static ReadOnlyMemory<(int, string)>
        parse_hex_file_content
        (TomlArray a_array)
        {
            if(a_array.Count is 0)
            {
                throw new Exception("hex-file-content array cannot be empty");
            }

            var a_result = new List<(int, string)>(a_array.Count);

            foreach(var a_obj in a_array)
            {
                if(a_obj is null)
                {
                    throw new Exception("hex-file-content array element null");
                }

                var a_tab = (TomlTable)a_obj;
                var a_signature = (string)a_tab["signature"];
                var a_max_size_raw = (long)a_tab["max-size"];
                var a_max_size = checked((int)a_max_size_raw);

                if(a_max_size < CAN_Bootloader.MIN_APP_SIZE)
                {
                    throw new Exception($"max-size '{a_max_size}' must be >= {CAN_Bootloader.MIN_APP_SIZE}");
                }

                a_result.Add((a_max_size, a_signature));
            }

            return a_result.ToArray();
        }

        private static ReadOnlyMemory<(int, uint)>
        parse_upgrade_tasks
        (TomlArray a_array, int a_hex_file_content_size)
        {
            if(a_array.Count is 0)
            {
                throw new Exception("upgrade-tasks array cannot be empty");
            }

            var a_result = new List<(int, uint)>(a_array.Count);

            foreach(var a_obj in a_array)
            {
                if(a_obj is null)
                {
                    throw new Exception("upgrade-tasks array element null");
                }

                var a_tab = (TomlTable)a_obj;
                var a_firmware_index_raw = (long)a_tab["firmware-index"];
                var a_firmware_index = checked((int)a_firmware_index_raw);
                var a_id_prefix_raw = (long)a_tab["id-prefix"];
                var a_id_prefix = checked((uint)a_id_prefix_raw);

                if(a_firmware_index is < 0 || a_firmware_index >= a_hex_file_content_size)
                {
                    throw new Exception($"firmware-index out of range '{a_firmware_index_raw}'");
                }

                if((a_id_prefix & (~CAN_Bootloader.ID_PREFIX_MASK)) is not 0u)
                {
                    throw new Exception($"invalid id-prefix '0x{a_id_prefix:X8}'");
                }

                a_result.Add((a_firmware_index, a_id_prefix));
            }

            return a_result.ToArray();
        }
    }

    public Bootloader_Table? bootloader { get; }
}
