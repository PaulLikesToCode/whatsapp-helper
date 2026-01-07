FROM node:25.1.0

WORKDIR /app

ENV PUPPETEER_SKIP_DOWNLOAD=true

RUN apt-get update && apt-get install -y chromium

COPY package*.json ./

RUN npm install

COPY src/ ./src/

RUN mkdir /app/auth
RUN mkdir /app/logs

CMD ["npm", "start"]
# CMD ["tail", "-f", "/dev/null"]

