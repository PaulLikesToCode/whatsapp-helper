## Initial work was putting the node and python work in the same image. 
## Moving away from this in favor of task specific images. See Dockerfile.node for the whatsapp-helper image. 
## Keeping this for reference. 

FROM node:25.1.0

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

ENV PUPPETEER_SKIP_DOWNLOAD=true

# Originally thought to use postfix before moving to AWS SES. 
# Keepign postfix in the dockerfile for future possibilities. 
RUN apt-get update && \
    echo "postfix postfix/main_mailer_type string Internet Site" | debconf-set-selections && \
    echo "postfix postfix/mailname string localhost" | debconf-set-selections && \
    apt-get install -y chromium postfix python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

COPY package*.json ./
COPY requirements.txt ./

RUN npm install && npm cache clean --force

ENV PYTHONDONTWRITEBYTECODE=1
RUN python3 -m venv /app
RUN rm -rf /root/.cache/pip
RUN /app/bin/python -m pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY summerizer/ ./summerizer/
COPY util/ ./util/
COPY hf-cache /root/.cache/huggingface/hub/

RUN mkdir /app/auth
RUN mkdir /app/logs

CMD ["npm", "start"]
# CMD ["tail", "-f", "/dev/null"]

