from datetime import datetime
from dateutil.parser import parse
import os
import glob
import re


def parse_unix_epoch_timestamp(timestamp_str):
    try:
        # Convert the timestamp string to a datetime object
        timestamp_obj = parse(timestamp_str)
        
        # Convert to milliseconds if needed (multiply by 1000)
        epoch_milliseconds = int(timestamp_obj.timestamp() * 1000)
        
        return epoch_milliseconds
    
    except Exception as e:
        print(f"Error: {e}")
        return None


def process_all_log_files(directory):

    """Processes all log files in the specified directory and ensures proper spacing."""
    
    log_files = glob.glob(os.path.join(directory, "*.log"))  # Adjust the extension if needed
    # for file in log_files:
    #     add_delimiter_on_trace_change(file)
    add_delimiter(log_files)    


def add_delimiter_on_trace_change(input_file):
    with open(input_file, 'r+', encoding='utf-8') as f:
        lines = f.readlines()

        previous_trace_id = None
        modified_lines = []

        for line in lines:
            # Extract traceId using regex (assuming format like '[TRACE1234]')
            match = re.search(r'\[(TRACE[0-9]+)\]', line)
            trace_id = match.group(1) if match else None

            if trace_id and trace_id != previous_trace_id:
                line = '|||' + line  # Add delimiter when traceId changes

            modified_lines.append(line)
            previous_trace_id = trace_id  # Update previous traceId

        f.writelines(modified_lines)




def add_delimiter(log_files):
    for file in log_files:
        with open(file, "r+", encoding="utf-8") as f:
            
            content = f.read()
            content = content.replace('|||', '')
            processed = preprocess_logs(content)
            f.seek(0)
            f.write(processed)

def preprocess_logs(log_text: str) -> str:
    # Regex to match common timestamp formats (customize as needed)
    TIMESTAMP_PATTERN = r"""
    ^
    (
        \[\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\] |  # e.g., [2023-10-05 12:34:56]
        \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z      |  # ISO 8601 (UTC)
        \d{10}\.\d{3}                              |  # Unix timestamp (e.g., 1672531200.123)
        \w{3}\s\d{2}\s\d{2}:\d{2}:\d{2}               # e.g., Oct 05 12:34:56
    )
    """
    

    # Add '|||' before timestamps and strip leading delimiters
    processed = re.sub(
        pattern=TIMESTAMP_PATTERN,
        repl=r"|||\1",  # Insert delimiter before the timestamp
        string=log_text,
        flags=re.VERBOSE | re.MULTILINE
    )

    # Remove leading '|||' if present
    return processed.lstrip("|||")