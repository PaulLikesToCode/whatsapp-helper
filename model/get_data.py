'''
Data is in ../logs/messages.log, ../logs/messages.log.0, etc. 
Each message is in the format: {"name":"","hostname":"","pid":<int>,"level":<int>,"ts":<int>,"chat":"","sender":"","body":"","msg":"","time":"","v":<int>}
We just want to extract the body of the message dump to the training_data
'''

import glob
import json

log_files = glob.glob('../logs/messages.log*')

with open('training_data/data.txt', 'w', encoding='utf-8') as output_file:
    # Process each log file
    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8') as input_file:
            for line in input_file:
                line = line.strip()
                if line:
                    try:
                        json_obj = json.loads(line)
                        body = json_obj.get('body', '')
                        if body:
                            output_file.write(body + '\n')
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        pass

