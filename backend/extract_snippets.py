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

    return response_text



def error_flow(llm, QUERY, results):

    PROMPT_TEMPLATE="""
[TASK] Extract and present only the relevant error log snippets.

You are given a set of log snippets and a user query. Your task is to:
1. Identify and extract the exact log snippet that directly corresponds to the error in the query.
2. Identify and extract other log snippets that led to this error.
3. Present these logs in sequence to depict the flow leading to the error.

STRICT INSTRUCTIONS:
- Your response MUST contain ONLY log snippets. No explanations, summaries, or additional words.
- Do NOT repeat or reformat the logs. Keep them exactly as they appear in the provided context.
- Do NOT mention or include any analysis. Simply present the raw log snippets in order.
- Do NOT print the provided context in full. Extract only relevant log snippets.

--- START OF RESPONSE ---

Log snippets depicting the flow of events causing the error:

<Only log snippets in exact order, without any additional space or explanation>

--- END OF RESPONSE ---

Context for your reference:
{context}

Query to answer:
{query}
"""


    return get_relevant_snippets(llm, QUERY, PROMPT_TEMPLATE, results)




def success_flow(llm, QUERY, results):

    PROMPT_TEMPLATE="""
[TASK] Extract and present only the "happy path" log snippets.

You are given a set of log snippets and a user query. Your task is to:
1. Identify and extract only the successful log snippets related to the query.
2. Construct a "happy path" log sequence by excluding any error or warning logs.
3. Present the logs in the exact format and sequence as they should appear in an ideal, error-free scenario.

STRICT INSTRUCTIONS:
- Your response MUST contain ONLY log snippets. No explanations, summaries, or additional words.
- Do NOT include any ERROR or WARN log entries.
- Do NOT repeat, reformat, or modify the logs. Keep them exactly as they appear in the provided context.
- Do NOT mention or include any analysis. Simply present the raw log snippets in order.
- Do NOT print the provided context in full. Extract only relevant log snippets.
- Do NOT print anything in plain English. Only the technical log snippets.
- Your whole response shouldn't exceed more than 10 lines
- Understand your context window limit and try to summarize the whole flow without truncating 

--- START OF RESPONSE ---

Log snippets depicting the flow of events in case the error didn't occur:
<Only successful log snippets in exact order, without any additional space, unnecessary blanks/symbols or explanation>

--- END OF RESPONSE ---

Context for your reference:
{context}

Query to answer:
{query}
"""
    return get_relevant_snippets(llm, QUERY, PROMPT_TEMPLATE, results)