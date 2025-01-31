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



def ensure_blank_lines_inplace(file_path):

    """Modifies a log file in-place, adding a blank line between consecutive log entries if missing."""
    
    with open(file_path, 'r+', encoding='utf-8') as file:
        lines = file.readlines()  # Read all lines into memory
        updated_lines = []
        
        prev_line = None  # Track the previous line to check spacing

        for line in lines:
            stripped_line = line.strip()  # Remove leading/trailing spaces but keep empty lines
            
            if prev_line is not None:
                updated_lines.append(prev_line + "\n")  # Write previous line
                
                # If previous line is not empty and current line is not empty, add a blank line
                if prev_line.strip() and stripped_line:
                    updated_lines.append("\n")
            
            prev_line = line.rstrip()  # Store the current line without trailing newline
        
        # Append the last line (if file is not empty)
        if prev_line is not None:
            updated_lines.append(prev_line + "\n")

        # Move the file pointer to the beginning and overwrite the file with updated content
        file.seek(0)
        file.writelines(updated_lines)
        file.truncate()  # Remove any leftover content if new content is shorter than the original



def process_all_log_files(directory):

    """Processes all log files in the specified directory and ensures proper spacing."""
    
    log_files = glob.glob(os.path.join(directory, "*.log"))  # Adjust the extension if needed
    add_delimiter(log_files)    


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
        flags=re.VERBOSE
    )

    # Remove leading '|||' if present
    return processed.lstrip("|||")