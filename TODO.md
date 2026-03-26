* Be able to support multiple users who are interested in only specific groups. For example, Bob might only want messages from group A, Alice from group B, and I want messages from groups A, B, and C. 

* Currently saving the image as a tar file and scp'ing up to the box. TODO is build image, push to repo and pull updated image on box, restart docker all in 1 go. 

* Models from HuggingFace are between 7 and 16MB. I don't want to continuously run a server with that much memory just for this 1 task. Investigate cheaper options to run different models to summerize the messages. 

* Add monitoring/alerting. 

* Once a message has been successfully emailed, mark it as such so it doesn't get emailed twice. Possibly use a timestamp to check last successful email. 