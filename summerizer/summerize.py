from transformers import AutoTokenizer, pipeline
import os
import logging
import glob

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('summerizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 1. Use BERT NER model for named entity recognition
model_name = "dslim/bert-base-ner"

logger.info(f"Loading model: {model_name}")

# 2. Create a pipeline for named entity recognition
ner_pipeline = pipeline("ner", model=model_name, tokenizer=model_name, aggregation_strategy="simple")

logger.info("NER pipeline loaded successfully")

# 3. Get list of log files
log_files = glob.glob('../logs/messages.log.*')

if log_files:
    logger.info(f"Found {len(log_files)} log files: {log_files}")
    
    # Process all log files
    all_text = ""
    for log_file in log_files:
        logger.info(f"Reading file: {log_file}")
        with open(log_file, 'r', encoding='utf-8') as file:
            all_text += file.read() + "\n"
    
    logger.info(f"All files read successfully. Total text length: {len(all_text)} characters")
    
    logger.info("Extracting named entities...")
    # 4. Extract named entities
    entities = ner_pipeline(all_text)
    
    # 5. Print results
    logger.info("Named entity extraction completed successfully")
    print("Named Entities Found:")
    for entity in entities:
        print(f"- {entity['word']}: {entity['entity_group']} (confidence: {entity['score']:.2f})")
        
else:
    logger.error(f"No log files found matching pattern '../logs/messages.log.*'")
