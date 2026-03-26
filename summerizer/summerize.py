from transformers import AutoTokenizer, pipeline, AutoModelForCausalLM
import torch
import os
import logging
import glob
import json
import sys
from datetime import datetime
sys.path.append('../')
from util.emailer import Emailer

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/summerizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get model name from environment variables
# google/gemma-1.1-2b-it requires too much RAM, making google/t5-efficient-tiny default
MODEL_NAME = os.getenv('MODEL_NAME', 'google/t5-efficient-tiny')

# Get Hugging Face token from environment variables
HF_TOKEN = os.getenv('HF_TOKEN')

# Set cache directory (optional - useful for volume mounting)
# CACHE_DIR = os.getenv('HF_HOME', '/app/huggingface_cache')

logger.info(f"Loading model: {MODEL_NAME}")

summarizer = pipeline("summarization", model=MODEL_NAME, token=HF_TOKEN)

# google's gemma, keeping for reference but using pipeline
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=HF_TOKEN, cache_dir=CACHE_DIR)
# model = AutoModelForCausalLM.from_pretrained(
#     MODEL_NAME,
#     torch_dtype=torch.bfloat16,
#     token=HF_TOKEN,
#     cache_dir=CACHE_DIR
# )


logger.info("model loaded successfully")

# 3. Get list of log files
log_files = glob.glob('../logs/messages.log.*')

if log_files:
    logger.info(f"Found {len(log_files)} log files: {log_files}")
    
    # Process all log files
    all_text = ""
    for log_file in log_files:
        # gemma-1.1-2b-it has a limit of 8k tokens, which allows for 5k-6k words in the input. 
        # My whapsapp groups aren't very active so not worrying about this at the moment
        logger.info(f"Reading file: {log_file}")
        with open(log_file, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    log_entry = json.loads(line.strip())
                    if 'sender' in log_entry and 'body' in log_entry:
                        formatted_message = f'"sender": "{log_entry["sender"]}", "body": "{log_entry["body"]}"'
                        all_text += formatted_message + "\n"

                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    logger.error(f'couldnt load json: {line}')
                    continue
    
    logger.info(f"All files read successfully. Total text length: {len(all_text)} characters")
    
    # Check if there's enough content to summarize
    if len(all_text) < 10:
        logger.info("Not enough content to summarize (less than 10 characters). Exiting gracefully.")
        exit(0)
    
    logger.info("Generating summary...")
    
    # Create a prompt for summarization - commenting out because I've moved to summerizer model.
#     prompt = f"""<start_of_turn>user
# Please provide a concise summary of the following WhatsApp messages. Focus on the main topics discussed, key participants, and important information:

# {all_text[:4000]}  # Limit input to avoid token limits
# <end_of_turn>
# <start_of_turn>model
# """
    
    # Tokenize and generate summary for google gemma, above. Saving for future use. 
    # inputs = tokenizer(prompt, return_tensors="pt")
    
    # with torch.no_grad():
    #     outputs = model.generate(
    #         **inputs,
    #         max_new_tokens=500,
    #         temperature=0.7,
    #         do_sample=True,
    #         pad_token_id=tokenizer.eos_token_id
    #     )
    
    # # Decode the response
    # response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # # Extract just the model's response (after the prompt)
    # summary = response.split("<start_of_turn>model\n")[-1].strip()

    summary = summarizer(all_text, max_length=100, min_length=30, do_sample=False, length_penalty=2.0, num_beams=4)
    
    logger.info("Summary generation completed successfully")
    
    formatted_output = f"\n{'='*50}\nWHATSAPP MESSAGES SUMMARY\n{'='*50}\n{summary}\n{'='*50}\n"
    logger.info(formatted_output)
    # email to recipients. TODO: Allow emails by group. 
    to_email = os.getenv('EMAIL_ADDRESS')
    
    # Get nicely formatted date
    formatted_date = datetime.now().strftime("%B %d, %Y")

    if not to_email:
        logger.error('no to email set')
        sys.exit(1)
    emailer = Emailer("localhost", 25)

    emailer.send(
        sender="hello@whatsapp.helper",
        recipients=[to_email],
        subject=f'Whatsapp summary for {formatted_date}',
        body=formatted_output
    )


    
    
        
else:
    logger.error(f"No log files found matching pattern '../logs/messages.log.*'")
