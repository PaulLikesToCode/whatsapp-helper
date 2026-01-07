// const { Client, LocalAuth } = require('whatsapp-web.js');
const { Client, LocalAuth }  = require('@another-trial/whatsapp-web.js')
const qrcode = require('qrcode-terminal');
// const qrcode = require('qrcode')
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

const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: '/app/auth'
    }),
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
        executablePath: '/usr/bin/chromium'
    }
});

// When the client is ready, run this code (only once)
client.once('ready', () => {
    appLogger.info('Client is ready');
});

// When the client received QR-Code
client.on('qr', qr => {
    appLogger.info('QR code received')
    qrcode.generate(qr, {small: true}); 
});

// Listening to all incoming messages
client.on('message_create', async (message) => {
    const chat = await message.getChat();
    const contact = await message.getContact();
    messagesLogger.info({'ts': message.timestamp, 'chat': chat.name, 
                         'sender': contact.pushname, 'body': message.body}) 
});

// Start your client
client.initialize();