const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { appendFile } = require('fs/promises');
const { existsSync, writeFileSync } = require("fs");
const path = require("path");

const logFileDir = process.env.LOG_FILE_DIR ?? path.join(__dirname, "../logs");

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
    console.log('Client is ready!');
});

// When the client received QR-Code
client.on('qr', qr => {
    qrcode.generate(qr, {small: true});
});

// Listening to all incoming messages
client.on('message_create', async (message) => {
    const chat = await message.getChat();

    const todaysDate = new Date().toLocaleDateString('en-GB');
    const logFilePath = `${logFileDir}/${todaysDate}-${chat.name}.log`;
    
    await appendFile(logFilePath, JSON.stringify({'ts': message.timestamp, 'sender': message.author, 
                    'body': message.body}), { encoding: 'utf8', flag: 'w' } );
    console.log(message.body);
});

// Start your client
client.initialize();