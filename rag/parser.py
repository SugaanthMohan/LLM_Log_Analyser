from datetime import datetime
from dateutil.parser import parse
import os
import glob
import re

def parse_unix_epoch_timestamp(timestamp_str):
    """
    Converts various timestamp formats into Unix epoch (milliseconds).
    """
    try:
        timestamp_obj = parse(timestamp_str)
        return int(timestamp_obj.timestamp() * 1000)
    except Exception as e:
        print(f"Error parsing timestamp: {e}")
        return None

def process_all_log_files(directory):
    """
    Processes all log files in a directory to standardize formatting.
    """
    log_files = glob.glob(os.path.join(directory, "*.log"))
    add_delimiter(log_files)

def add_delimiter_on_trace_change(input_file):
    """
    Adds a delimiter (|||) whenever the trace ID changes in a log file.
    """
    with open(input_file, 'r+', encoding='utf-8') as f:
        lines = f.readlines()
        previous_trace_id = None
        modified_lines = []

        for line in lines:
            match = re.search(r'\[(TRACE[0-9A-Za-z_]+)\]', line)
            trace_id = match.group(1) if match else None

            if trace_id and trace_id != previous_trace_id:
                line = '|||' + line
            modified_lines.append(line)
            previous_trace_id = trace_id

        f.seek(0)
        f.writelines(modified_lines)

def add_delimiter(log_files):
    """
    Adds delimiters to separate log entries in each log file.
    """
    for file in log_files:
        with open(file, "r+", encoding="utf-8") as f:
            content = f.read()
            content = content.replace('|||', '')
            processed = preprocess_logs(content)
            f.seek(0)
            f.write(processed)

def preprocess_logs(log_text: str) -> str:
    """
    Formats logs by adding delimiters before timestamps.
    """
    TIMESTAMP_PATTERN = r"""
    ^(
        \[\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\] |
        \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z |
        \d{10}\.\d{3} |
        \w{3}\s\d{2}\s\d{2}:\d{2}:\d{2}
    )
    """
    processed = re.sub(
        pattern=TIMESTAMP_PATTERN,
        repl=r"|||\1",
        string=log_text,
        flags=re.VERBOSE | re.MULTILINE
    )
    return processed.lstrip("|||")

def parse_mermaid_llm_output(llm_output):
    """
    Extracts raw MermaidJS code from an LLM output.
    """
    if llm_output.startswith("```mermaid") and llm_output.endswith("```"):
        return llm_output[len("```mermaid\n"):-len("```")].strip()
    return llm_output

def parse_response(text):
    """
    Parses structured LLM response into predefined sections.
    """
    headings = [
        ['Summary', 'Analysis'],
        ['Incident/Scenario Report', 'Incident Report', 'Scenario Report', 'Incident Details'],
        ['Explanation'],
        ['Expected Ideal Flow (Happy Path)', 'Expected Ideal Flow'],
        ['Remediation / Recommendations', 'Remediation', 'Recommendation']
    ]
    keys = [heading[0] for heading in headings]
    response = dict.fromkeys(keys, "")
    key = None
    
    for line in text.split('\n'):
        for heading in headings:
            if any(name in line for name in heading):
                key = heading[0]
                break
        if key and line.strip():
            line = line.replace("**", "").replace("### **Answer**", "").replace("**Answer**", "")
            response[key] += line + "\n"
    
    response['Summary'] = add_bullets(response.get("Summary", ""))
    response['Explanation'] = add_bullets(response.get("Explanation", ""))
    return (
        response.get("Summary", "").strip(),
        response.get("Incident/Scenario Report", "").strip(),
        response.get("Explanation", "").strip(),
        response.get("Expected Ideal Flow (Happy Path)", "").strip(),
        response.get("Remediation / Recommendations", "").strip(),
    )

def parse_log_flow_snippets(log_flow):
    """
    Removes redundant lines and trims logs for concise output.
    """
    lines = list(dict.fromkeys(log_flow.split('\n')))
    return "\n".join(lines[:5])  # Limit to 5 lines for brevity

def add_bullets(text):
    """
    Formats text with bullet points if missing.
    """
    lines = text.strip().split("\n")
    if all(not re.match(r"(\d+\.\s+|[-•*])", line.strip()) for line in lines):
        lines = [f"* {line}" if line.strip() else line for line in lines]
    return "\n".join(lines)

if __name__ == '__main__':
    print(parse_unix_epoch_timestamp('2025-02-01T21:39'))
