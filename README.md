# whatsapp-helper
App to get whatsapp messages, summerize them, and send a daily email

## Overview

The components of this applications are:
1. whatsapp headless browser. Syncs your whatsapp account, saves messages to a log file. 
2. model. Builds the model used to summerize messages. 
3. summerizer. Uses the model to summerize messages, email important messages. Runs on a cron schedule. 
4. util. Various helpful scripts.

whatsapp headless browser requires a directory called `docker_dir` at the top level of the directory where this runs. This requires subdirectories `session` and `logs`. `session` is used to reauthenticate when restarting the whatsapp headless browser. `logs` are where messages are stored. Log files are rotated once a day and automatically deleted after 7 days. This is managed by the node package `bunyan`. 

## whatsapp-web.js
Located in `src/main.ts`, this is the headless browser that connects to WhatsApp. For every message either 1-1 or group messages, it logs to `logs/messages.log`. The format is:

`{"name":"messages","hostname":str,"pid":int,"level":int,"ts":int,"chat":<str, name of chat or individual>,"sender":<str, sender name>,"body":<str, text of message>,"msg":<str, from logger, currently empty string>,"time":<str, in the format yyyy-mm-ddThh:mm:ss.SSSZ,"v":<int>}`

Application logs are written to `logs/app.log`. 

### Authentication

#### Whatsapp web
`whatsapp-web` uses a QR code for authentication. This code is printed out in the terminal. The first time you run the app you can't run it in the background. It needs to run with the terminal. Open WhatsApp on your phone and go to "add a device", and scan the QR code. Once you do, session files will be written to `docker_dir/session`. Afterwards, you can `crtl-c` the app and run it in the background. It will use the session files to reauthenticate when it restarts. 

#### Huggingface to download model
If you download a model from huggingface, you need an auth token. Save the token as an environment variable `HF_TOKEN`. 

## Model
Still very much a work in progress. Data lives in `model/training_data` and `model/test_data`. `model.ipynb` builds the model. Currently just using a logistic regression TfidfVectorizer. The model should be good at knowing if a message is important (and therefore should be forwarded) or not. Currently the model is only about 65% accurate. I need to collect and label a lot more messages to increase accuracy. 

The model is saved to `model/message_model.joblib`. 

## summerizer
`summerizer/summerize.py` loads the model from `model`, reads the previous day's log file (`logs/messages.log.0`), compiles a list of important messages and emails using AWS SES.
AWS SES is used so email services don't reject the email for DKIM, etc.  

### Future work:
* Be able to support multiple users who are interested in only specific groups. For example, Bob might only want messages from group A, Alice from group B, and I want messages from groups A, B, and C. 

* By baking the model in the image, the image is now 13GB. By using multi stage builds I could probably get that down to 7-8GB. But maybe think about not baking the model into the same image as the node app. Or test using smaller models. 

## util
Various scripts that do things. 


