from langchain_core.prompts import PromptTemplate

def get_relevant_snippets(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY, PROMPT_TEMPLATE):
    retriever = db.as_retriever(
                search_type="mmr",  # Maximal Marginal Relevance
                search_kwargs={
                    'k': 10,  # Final results
                    'fetch_k': 20,  # Initial candidate pool
                    'lambda_mult': 0.65,  # 65% relevance, 35% diversity
                    'score_threshold': 0.6,  # Minimum relevance floor
                    'where': {   # Metadata filtering
                        "$and": [
                            {"APP_ID": APP_ID},  
                            {"Timestamp": {"$gte": TIME_FROM}},  
                            {"Timestamp": {"$lte": TIME_TO}}  
                        ]
                    }
                }
            )
    
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

     # Using the 'invoke' method instead of 'get_relevant_documents'
    results = retriever.invoke(QUERY)
    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])

    # Update the prompt with conversation history
    llm_chain = prompt | llm
    response_text = llm_chain.invoke({
        "context": context_text,
        "query": QUERY,
        # "conversation_history": conversation_history_text
    })

    return response_text



def error_flow(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY):

    PROMPT_TEMPLATE="""
[TASK] To understand the context, correlate and collate the error log snippets

You will be provided with some bunch of log snippets that are related to one another and a user query.

Carefully interpret and figure out the error logs relevant to the user query. Once you are able to
extract the exact error snippet the query is referring, you are to now extract other snippets of logs
that has led to this error.

Analyse the available context and create a meaningful flow on log snippets that have led to this error.
Be very precise, and only use the provided context to creat this flow. Don't hallucinate. 

Lay down the snippets one by one.

*** YOUR RESPONSE SHOULD ONLY CONTAIN THE LOG SNIPPETS AND NO OTHER WORDINGS ***
*** DON'T PRINT BACK THE CONTEXT AT ANY TIME. SUMMARIZE YOURSELF AND ONLY PROVIDE THE OUTPUT LOG SNIPPETS ***


Context for your refernce:
{context}

Query to answer:
{query}

Response Format:
<A one line short summary>

<snippet 1>
<snippet 2>
<snippet 3>
<snippet 4>
<snippet 5>

-*- END OF RESPONSE -*-
"""

    return get_relevant_snippets(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY, PROMPT_TEMPLATE)




def success_flow(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY):

    PROMPT_TEMPLATE="""
[TASK] To understand the context, correlate and collate the happy path log snippets

You will be provided with some bunch of log snippets that are related to one another and a user query.

Carefully interpret and figure out the error logs relevant to the user query. Once you are able to
extract the exact error snippet the query is referring, you are to now extract other snippets of logs
that has led to this error.

Analyse the available context and create a meaningful flow on log snippets that have led to this error.

Once you have the flow of logs that led to error, examine the context once again to create the ideal scenario.
That is, create a happy path flow that should represent what would have the logs looked like if the error
didn't occur. Be very precise, and only use the provided context to creat this flow. Don't hallucinate. 

*** YOUR RESPONSE SHOULD ONLY CONTAIN THE LOG SNIPPETS AND NO OTHER WORDINGS ***
*** THERE SHOULDN'T BE ANY ERROR / WARN LOG ENTRIES ***
*** DON'T PRINT BACK THE CONTEXT AT ANY TIME. SUMMARIZE YOURSELF AND ONLY PROVIDE THE OUTPUT LOG SNIPPETS ***

Context for your refernce:
{context}

Query to answer:
{query}

Response Format:
<A one line short summary>

<snippet 1>
<snippet 2>
<snippet 3>
<snippet 4>
<snippet 5>

-*- END OF RESPONSE -*-
"""
    TIME_FROM = 0
    TIME_TO = 1735689600000
    return get_relevant_snippets(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY, PROMPT_TEMPLATE)