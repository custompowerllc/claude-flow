#!/usr/bin/env node

const http = require('http');
const express = require('express');
const RED = require('node-red');

// Create an Express app
const app = express();

// Create a server
const server = http.createServer(app);

// Create the settings object
const settings = require('./settings.js');

// Initialise the runtime with a server and settings
RED.init(server, settings);

// Serve the editor UI from /
app.use(settings.httpAdminRoot || '/', RED.httpAdmin);

// Serve the http nodes from /api
app.use(settings.httpNodeRoot || '/api', RED.httpNode);

const PORT = settings.uiPort || 1880;

server.listen(PORT);

// Start the runtime
RED.start().then(() => {
    console.log(`Node-RED server running at http://localhost:${PORT}`);
    console.log(`Node-RED dashboard available at http://localhost:${PORT}/`);
    console.log('\nInstalled nodes:');
    console.log('  ✓ Node-RED Core');
    console.log('  ✓ Modbus nodes (node-red-contrib-modbus)');
    console.log('  ✓ Serial port nodes (node-red-node-serialport)');
    console.log('\nPress Ctrl+C to stop the server');
}).catch((err) => {
    console.error('Failed to start Node-RED:', err);
    process.exit(1);
});