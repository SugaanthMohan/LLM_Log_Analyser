from langchain_core.prompts import PromptTemplate

def get_relevant_snippets(llm, QUERY, PROMPT_TEMPLATE, results):
    
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

     # Using the 'invoke' method instead of 'get_relevant_documents'
    
    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])

    # Update the prompt with conversation history
    llm_chain = prompt | llm
    response_text = llm_chain.invoke({
        "context": context_text,
        "query": QUERY,
        # "conversation_history": conversation_history_text
    })

    print(response_text)
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




def success_flow(llm, QUERY, results):

    PROMPT_TEMPLATE="""
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
"""

    return get_relevant_snippets(llm, QUERY, PROMPT_TEMPLATE, results)