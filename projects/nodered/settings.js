module.exports = {
    // Flow file settings
    flowFile: 'flows.json',
    flowFilePretty: true,
    
    // User directory - stores flows, credentials and all config
    userDir: './data/',
    
    // Node-RED server settings
    uiPort: process.env.PORT || 1880,
    
    // Securing Node-RED
    // adminAuth: {
    //     type: "credentials",
    //     users: [{
    //         username: "admin",
    //         password: "$2a$08$hash_here",
    //         permissions: "*"
    //     }]
    // },
    
    // Allow anonymous read access
    httpNodeAuth: false,
    httpStaticAuth: false,
    
    // Logging
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    },
    
    // Context Storage
    contextStorage: {
        default: {
            module: "memory"
        },
        file: {
            module: "localfilesystem",
            config: {
                dir: "./data/context",
                cache: true,
                flushInterval: 30
            }
        }
    },
    
    // Export settings
    exportGlobalContextKeys: false,
    
    // Configure the palette
    paletteCategories: [
        'subflows',
        'common',
        'function',
        'network',
        'sequence',
        'parser',
        'storage',
        'modbus',
        'serial'
    ],
    
    // Editor theme
    editorTheme: {
        page: {
            title: "Node-RED with Modbus RTU & Serial"
        },
        header: {
            title: "Node-RED Modbus/Serial",
            image: null
        },
        palette: {
            allowInstall: true,
            catalogues: [
                'https://catalogue.nodered.org/catalogue.json'
            ]
        },
        projects: {
            enabled: false
        }
    },
    
    // Function nodes settings
    functionGlobalContext: {
        // Add any global libraries/objects here
    },
    
    // Debug settings
    debugMaxLength: 1000,
    debugUseColors: true,
    
    // Serial port settings
    serialReconnectTime: 15000,
    
    // Modbus settings
    modbusReconnectTime: 15000
}