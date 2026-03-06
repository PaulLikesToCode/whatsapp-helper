const { Client, LocalAuth } = require('whatsapp-web.js');
// const { Client, LocalAuth }  = require('@another-trial/whatsapp-web.js')
const qrcodeTerminal = require('qrcode-terminal');
const qrcodePng = require('qrcode')
const { appendFile } = require('fs/promises');
const { existsSync, writeFileSync } = require("fs");
const path = require("path");
const bunyan = require('bunyan');

// const logFileDir = process.env.LOG_FILE_DIR ?? path.join(__dirname, "../logs");
const appLogger = bunyan.createLogger({
  name: 'app',
  streams: [
    {
      type: 'file',          // single file stream
      path: './logs/app.log' // will be created if it doesn't exist
    }
  ]
});
const messagesLogger = bunyan.createLogger({
  name: 'messages',
  streams: [
    {
      type: 'rotating-file',
      path: './logs/messages.log',   // Bunyan will rotate this file
      period: '1d',             // daily rotation
      count: 7                  // keep 7 back copies (optional)
    }
  ]
});

appLogger.info('Initializing WhatsApp client...');

const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: '/app/auth'
    }),
    puppeteer: {
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--disable-gpu',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-features=VizDisplayCompositor',
            '--disable-ipc-flooding-protection',
            '--disable-features=TranslateUI'
        ],
        executablePath: '/usr/bin/chromium',
        headless: true,
        timeout: 0, // Disable timeout
        ignoreHTTPSErrors: true
    },
    // webVersionCache: {
    //     type: 'remote',
    //     remotePath: 'https://raw.githubusercontent.com/wppconnect-team/wa-version/main/html/2.2412.54.html'
    // }
});

// When the client is ready, run this code (only once)
client.once('ready', () => {
    appLogger.info('Client is ready! Successfully connected to WhatsApp Web');
    console.log('🟢 WhatsApp Client is ready!'); // Console log for immediate visibility
});

// When the client received QR-Code
client.on('qr', (qr: string) => {
    appLogger.info('QR code received: ')
    qrcodeTerminal.generate(qr, {small: true});
    
    // Save QR code as PNG file
    qrcodePng.toFile('./logs/qr-code.png', qr, {
        width: 600,
        margin: 4,
        color: {
            dark: '#000000',  // Black dots
            light: '#FFFFFF'  // White background
        }
    }, (err: any) => {
        if (err) {
            appLogger.error('Failed to save QR code to file:', err);
        } else {
            appLogger.info('QR code saved to ./logs/qr-code.png');
        }
    });
});

// Add more event listeners for debugging
client.on('loading_screen', (percent: number, message: string) => {
    appLogger.info(`Loading: ${percent}% - ${message}`);
});

client.on('authenticated', () => {
    appLogger.info('Client authenticated successfully');
    
    // Set a timeout to check if client gets stuck during loading
    setTimeout(() => {
        appLogger.warn('Client has been loading for 2 minutes, this may indicate a problem');
    }, 120000); // 2 minutes
});

client.on('auth_failure', (msg: string) => {
    appLogger.error('Authentication failed:', msg);
});

client.on('disconnected', (reason: string) => {
    appLogger.warn('Client disconnected:', reason);
});

client.on('change_state', (state: string) => {
    appLogger.info('Client state changed to:', state);
});

// Add general error handler
client.on('error', (error: any) => {
    appLogger.error('Client error:', error);
    console.error('Client error:', error); // Also log to console for immediate visibility
});

// Add process error handlers
process.on('uncaughtException', (error) => {
    appLogger.error('Uncaught exception:', error);
    console.error('Uncaught exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
    appLogger.error('Unhandled rejection:', reason);
    console.error('Unhandled rejection:', reason);
});

// Listening to all incoming messages
client.on('message_create', async (message: any) => {
    const chat = await message.getChat();
    const contact = await message.getContact();
    messagesLogger.info({'ts': message.timestamp, 'chat': chat.name, 
                         'sender': contact.pushname, 'body': message.body}) 
});

// Start your client
appLogger.info('Starting client initialization...');
client.initialize();

// Keep the process alive
setInterval(() => {
    appLogger.debug('Process heartbeat - client is running');
}, 300000); // Log every 5 minutes