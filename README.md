# whatsapp-helper
App to get whatsapp messages, summerize them, and send a daily email

## Overview

1. Dockerize whatsapp-web.js. Mount the container to the filesystem so saved messages persist. 

2. cronjob that runs once a day. Get messages, use some model or api for summary, email to people using SMTP


## whatsapp-web.js
