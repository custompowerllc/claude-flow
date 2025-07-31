using System;
using System.IO;
using Tomlyn;
using Tomlyn.Model;

namespace GEHC_Forms_GUI
{
    public class AppConfig
    {
        private const string CONFIG_FILE = "config.toml";
        
        public string ComPort { get; set; } = string.Empty;
        public int BaudRate { get; set; } = 115200;

        // Singleton instance
        private static AppConfig _instance;
        public static AppConfig Instance => _instance ??= LoadConfig();

        // Load configuration from file
        private static AppConfig LoadConfig()
        {
            var config = new AppConfig();
            
            try
            {
                if (File.Exists(CONFIG_FILE))
                {
                    string tomlContent = File.ReadAllText(CONFIG_FILE);
                    var model = Toml.ToModel(tomlContent);
                    
                    if (model.TryGetValue("ComPort", out var comPort) && comPort is string comPortStr)
                    {
                        config.ComPort = comPortStr;
                    }
                    
                    if (model.TryGetValue("BaudRate", out var baudRate) && baudRate is long baudRateValue)
                    {
                        config.BaudRate = (int)baudRateValue;
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading config file: {ex.Message}");
                // Use default values
            }
            
            return config;
        }

        // Save configuration to file
        public void Save()
        {
            try
            {
                var model = new TomlTable
                {
                    ["ComPort"] = ComPort,
                    ["BaudRate"] = BaudRate
                };
                
                string tomlContent = Toml.FromModel(model);
                File.WriteAllText(CONFIG_FILE, tomlContent);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error saving config file: {ex.Message}");
            }
        }
    }
}
