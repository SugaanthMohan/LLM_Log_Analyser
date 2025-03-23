from langchain_core.prompts import PromptTemplate
from rag import parser
from rag.prompts import ERROR_SNIPPETS_EXTRACTOR_PROMPT, HAPPYPATH_SNIPPETS_EXTRACTOR_PROMPT
def get_relevant_snippets(llm, QUERY, PROMPT_TEMPLATE, results, error_summary=None):
    
   prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
   context_text = "\n\n---\n\n".join([doc.page_content for doc in results])
   llm_chain = prompt | llm

   prompt_parameters = {
        "context": context_text,
        "query": QUERY,
   }

   if error_summary is not None:
      prompt_parameters.update({'error_summary':error_summary})

   response_text = llm_chain.invoke(prompt_parameters)
   response_text = response_text.content

   response_text = response_text.replace('<<< RESPONSE START >>>', '')
   response_text = response_text.replace('<<< RESPONSE END >>>', '')

   line = [line for line in response_text.split('\n') if line.strip()]
   response_text = '\n'.join(line)

   return response_text

def error_flow(llm, QUERY, results):
   error_flow_snippets = get_relevant_snippets(llm, QUERY, ERROR_SNIPPETS_EXTRACTOR_PROMPT, results)
   error_flow_snippets = parser.parse_log_flow_snippets(error_flow_snippets)
   return error_flow_snippets

def success_flow(llm, QUERY, results, error_summary):
   success_flow_snippets = get_relevant_snippets(llm, QUERY, HAPPYPATH_SNIPPETS_EXTRACTOR_PROMPT, results, error_summary)
   success_flow_snippets = parser.parse_log_flow_snippets(success_flow_snippets)
   return success_flow_snippets