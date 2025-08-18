// FIXED CSV Formatter Function for Node-RED
// Replace the code in the "Format CSV Data" function node with this:

// Get configuration - FIX: Access individual config properties instead of config object
let config = {
    serial_number: flow.get('config.serial_number') || '0000',
    rma_number: flow.get('config.rma_number') || 'NONE', 
    output_path: flow.get('config.output_path') || './logs',
    read_extended: flow.get('config.read_extended') || false,
    slave_id: flow.get('config.slave_id') || 1,
    logging_enabled: flow.get('config.logging_enabled') || false
};

let timestamp = new Date();

// Register map order (matching Python implementation)
const register_order = [
    'fg_voltage', 'fg_current', 'fg_design_capacity', 'fg_remaining_capacity',
    'fg_full_charge_capacity', 'fg_state_of_charge', 'fg_temperature',
    'fg_charge_cycle', 'fg_state_of_health', 'fg_avg_time_empty',
    'fg_avg_time_full', 'afe_chip_status', 'afe_fet_status', 'afe_pack_volt',
    'afe_current', 'afe_temperature', 'afe_cell_volt_1', 'afe_cell_volt_2',
    'afe_cell_volt_3', 'afe_cell_volt_4', 'afe_cell_volt_5', 'afe_cell_volt_6',
    'afe_cell_volt_7', 'afe_cell_volt_8', 'afe_cell_volt_9', 'afe_cell_volt_10',
    'afe_cell_volt_11', 'afe_cell_volt_12', 'afe_cell_volt_13', 'afe_cell_volt_14',
    'afe_cell_volt_max', 'afe_cell_volt_min', 'afe_cell_volt_delta',
    'P1_cell_voltage', 'P2_cell_voltage', 'P3_cell_voltage', 'P4_cell_voltage',
    'P5_cell_voltage', 'P6_cell_voltage', 'P7_cell_voltage', 'P8_cell_voltage',
    'P9_cell_voltage', 'P10_cell_voltage', 'P11_cell_voltage', 'P12_cell_voltage',
    'P13_cell_voltage', 'P14_cell_voltage', 'P1_temperature', 'P2_temperature',
    'P3_temperature', 'P4_temperature', 'P5_temperature', 'P6_temperature',
    'P7_temperature', 'P8_temperature', 'P9_temperature', 'P10_temperature',
    'P11_temperature', 'P12_temperature', 'P13_temperature'
];

// Build CSV row
let csv_row = [];

// Add timestamp
csv_row.push(timestamp.toISOString().replace('T', ' ').split('.')[0]);

// Add input register data in order
for (let param of register_order) {
    let value = msg.input_registers ? msg.input_registers[param] : '';
    
    // Apply special current scaling for CSV (matching Python logic)
    if (param === 'afe_current' && value !== '') {
        value = Math.round(value * 2.0 * 1000);
    } else if (param === 'fg_current' && value !== '') {
        value = Math.round(value * 2.0 * 1000);
    }
    
    csv_row.push(value !== undefined ? value : '');
}

// Add extended register data if enabled
if (config.read_extended) {
    // Add coil registers (boolean values as 0/1)
    const coil_names = [
        'charge_discharge_enable', 'charge_immediately_1', 'charge_immediately_2',
        'discharge_enable', 'permanent_fail', 'safety_status', 'chg_enable',
        'dsg_enable', 'zvchg_enable', 'pchg_enable', 'pdsg_enable',
        'chg_fet', 'dsg_fet', 'zvchg_fet', 'pchg_fet'
    ];
    
    for (let coil_name of coil_names) {
        let value = msg.coils && msg.coils[coil_name] ? 1 : 0;
        csv_row.push(value);
    }
    
    // Add AFE status registers as hex
    const afe_status_names = [
        'afe_status_a', 'afe_status_b', 'afe_status_c', 'afe_battery_status',
        'afe_safety_status_a', 'afe_safety_status_b', 'afe_safety_status_c',
        'afe_pf_status_a', 'afe_pf_status_b', 'afe_pf_status_c'
    ];
    
    for (let status_name of afe_status_names) {
        let value = msg.afe_status && msg.afe_status[status_name] || 0;
        csv_row.push(`0x${value.toString(16).padStart(2, '0').toUpperCase()}`);
    }
    
    // Add FG status registers as hex
    const fg_status_names = [
        'fg_flags_msb', 'fg_flags_lsb', 'fg_it_status1', 'fg_it_status2',
        'fg_it_status3', 'fg_qmax_status', 'fg_ra_table_0', 'fg_ra_table_8',
        'fg_ra_table_16', 'fg_ra_table_24'
    ];
    
    for (let status_name of fg_status_names) {
        let value = msg.fg_status && msg.fg_status[status_name] || 0;
        csv_row.push(`0x${value.toString(16).padStart(2, '0').toUpperCase()}`);
    }
    
    // Add AFE config registers as hex
    const afe_config_names = ['afe_sys_ctrl1', 'afe_sys_ctrl2'];
    
    for (let config_name of afe_config_names) {
        let value = msg.afe_config && msg.afe_config[config_name] || 0;
        csv_row.push(`0x${value.toString(16).padStart(2, '0').toUpperCase()}`);
    }
}

// FIX: Set output properties correctly
msg.csv_row = csv_row;
msg.csv_string = csv_row.join(',');
msg.payload = csv_row.join(',');
msg.filename = flow.get('csv_filename') || './logs/modbus_data.csv';

// Debug output to help troubleshoot
node.warn("CSV formatter config check: " + JSON.stringify({
    config_keys: Object.keys(config),
    read_extended: config.read_extended,
    filename: msg.filename,
    payload_length: msg.payload.length
}));

return msg;