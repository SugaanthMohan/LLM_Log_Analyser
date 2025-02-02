from langchain_core.prompts import PromptTemplate
from backend import parse_documents

def get_relevant_snippets(llm, QUERY, PROMPT_TEMPLATE, results, error_summary=None):
    
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

     # Using the 'invoke' method instead of 'get_relevant_documents'
    
    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])

    # Update the prompt with conversation history
    llm_chain = prompt | llm

    prompt_parameters = {
        "context": context_text,
        "query": QUERY,
    }

    if error_summary is not None:
      prompt_parameters.update({'error_summary':error_summary})

    response_text = llm_chain.invoke(prompt_parameters)
   
    response_text = response_text.replace('<<< RESPONSE START >>>', '')
    response_text = response_text.replace('<<< RESPONSE END >>>', '')
    return response_text



def error_flow(llm, QUERY, results):


    PROMPT_TEMPLATE="""
[TASK] Extract and present only the relevant error log snippets.

### **Objective**
You are given a set of log snippets and a user query related to an error. Your task is to:
1. Identify and extract the exact log snippet that **directly corresponds** to the error in the query.
2. Identify and extract any **preceding log snippets** that are causally linked to this error.
3. Arrange the extracted logs **in chronological order** to depict the flow of events leading to the error.

### **Step-by-Step Reasoning (Chain of Thought)**
1. **Locate the Error**: Scan the provided log context to find the log entry that matches or explicitly describes the error mentioned in the query.
2. **Trace Back Relevant Logs**: Identify logs that occurred before the error, which may have led to or contributed to the issue. This includes:
   - Warnings
   - Timeout messages
   - Failed connections or retries
   - Stack traces
3. **Maintain Log Integrity**: Extract only the necessary logs while preserving their original structure, order, and content.
4. **Ensure Precision**: Do NOT include irrelevant logs, even if they contain the same keywords as the error.
5. **Output Format Strictness**:
   - **NO explanations.**
   - **NO reformatting.**
   - **NO summaries or analysis.**
   - **ONLY the relevant raw log snippets** in their original order.

### OUTPUT FORMAT
Your output MUST be structured exactly as follows (with no additional text):

<<< RESPONSE START >>> 
<log snippet 1> 
<log snippet 2> 
... 
<log snippet N> 
<<< RESPONSE END >>>

- If no error-related logs are found, output exactly:
<<< RESPONSE START >>> 
No error log snippets available 
<<< RESPONSE END >>>

### **Context for Reference**
{context}

### **User Query**
{query}
"""
    return get_relevant_snippets(llm, QUERY, PROMPT_TEMPLATE, results)




def success_flow(llm, QUERY, results, error_summary):

   PROMPT_TEMPLATE_v1="""
[TASK] Extract and present only the "happy path" log snippets that correspond to the provided query.

You are given a set of log snippets and a user query. Your task is to:

1. **Focus on Successful Log Entries**  
   - Identify log entries that **indicate success** and normal operation (e.g., INFO level logs, successful completion logs, and steps that are part of the intended process flow).
   - **Exclude** any log entries that denote issues such as errors, warnings, or failed processes (e.g., ERROR, WARN, exception traces).

2. **Construct a Flow of Events in the Happy Path**  
   - Collect **only the logs** (or simulated log entries) that show the process progressing normally without interruptions or issues. These logs should reflect an ideal, uninterrupted flow of the application or system.
   - Do **not** include any log entries that indicate the process was disrupted (e.g., error handling logs, retries, or timeouts).
   - If no clear happy path logs are found in the context, **simulate a plausible happy path flow** based solely on the provided context.

3. **Ensure Accurate Log Order**  
   - Present the log entries in **chronological order** as they occurred in the normal flow.
   - If multiple logs depict a sequence of actions, return them in the correct order without reordering or omitting any relevant logs that contribute to the happy path.

4. **Maintain Log Integrity**  
   - Do **not modify**, **reformat**, or **edit** any of the logs. Present them **exactly as they appear** in the provided context.
   - Do **not** include explanations, summaries, or additional commentary. Simply present the raw log snippets or simulated logs if necessary.

5. **Keep the Response Focused**  
   - Your entire response must not exceed **10 lines** of log snippets to maintain brevity.
   - The logs (or simulated logs) should cover the complete successful flow from the start to the completion of the process, ensuring the user gets the full picture without any irrelevant or extra logs.
   - If the provided logs exceed the context window, ensure the happy path is summarized appropriately, making sure no key steps are missed.

   STRICT INSTRUCTIONS:
- **NO** ERROR or WARN logs (e.g., ERROR, WARN, exceptions).
- Present only **successful, normal operations** in the exact order.
- Keep the response concise: **No more than 10 lines** of log data.
- If the context does not contain explicit happy path logs, simulate a plausible happy path flow based on the provided context.
- Do not include any additional text beyond the required output.


### OUTPUT FORMAT
Your output MUST be structured exactly as follows (with no additional text):

<<< RESPONSE START >>>
<log snippet 1>
<log snippet 2>
...
<log snippet N>
<<< RESPONSE END >>>

Context for your reference:
{context}

Query to answer:
{query}

** PS: Additional context ** 
Below is the summary of the error user is talking about with information on what could have been the remediation steps and
happy path flow. Use this information to derive the appropriate happy path flow.
{error_summary}
"""


   PROMPT_TEMPLATE_v2 = """
Based on the provided context of log snippets and the summary information about the log error requested by the user, 
generate an end-to-end flow of the ideal (happy path) scenario – i.e., the log sequence that would have occurred 
if the error had not happened.

Follow these steps in your chain of thought (but DO NOT include this reasoning in the final answer):

1. Identify the key actions and events in the normal (successful) process from the context.
2. Exclude any logs that indicate errors, warnings, or failures.
3. If explicit happy path logs are missing, simulate a plausible sequence that covers all important steps (you may mask repetitive details with a brief summary on one or two lines).
4. Ensure the resulting log flow is in strict chronological order and captures the full process from start to finish.
5. Keep your output concise and within 10 lines in total.

STRICT OUTPUT REQUIREMENTS:
- Your response MUST include ONLY the raw log snippets (or plausible simulated ones) and nothing else.
- Do NOT provide any explanations, summaries, or chain-of-thought details in the final output.
- The entire flow must be limited to no more than 10 lines.

OUTPUT FORMAT:
<<< RESPONSE START >>>
<log snippet 1>
<log snippet 2>
...
<log snippet N>
<<< RESPONSE END >>>

Context of log snippets for you to refer:
{context}

Summary of the error:
{error_summary}

User's query:
{query}

Generate a sequence (or a plausible simulation) of log snippets representing the entire end-to-end happy path flow.
"""

   success_flow_snippets = get_relevant_snippets(llm, QUERY, PROMPT_TEMPLATE_v2, results, error_summary)

   success_flow_snippets = parse_documents.parse_success_flow_snippets(success_flow_snippets)
   return success_flow_snippets