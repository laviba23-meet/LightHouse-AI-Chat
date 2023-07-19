from llama_index import SimpleDirectoryReader, LLMPredictor, GPTVectorStoreIndex, PromptHelper, ServiceContext, load_index_from_storage, StorageContext
from langchain.chat_models import ChatOpenAI

import gradio as gr
import os
import sys
import openai



os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.environ["OPENAI_API_KEY"]
# define prompt helper
max_input_size = 4096
num_output = 512 # number of output tokens
max_chunk_overlap = 0.7

prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)
llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", max_tokens=num_output))
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)

def construct_index(directory_path):
    # load in the documents
    docs = SimpleDirectoryReader(directory_path).load_data()

    index = GPTVectorStoreIndex.from_documents(docs, service_context=service_context)

    # save index to disk
    index.set_index_id("vector_index")
    index.storage_context.persist(persist_dir="./gpt_store")

    return index
def chatbot(input_text):
    # If not already done, initialize ‘index’ and ‘query_engine’
    if not hasattr(chatbot, "index"):
        # rebuild storage context and load index
        storage_context = StorageContext.from_defaults(persist_dir="./gpt_store")
        chatbot.index = load_index_from_storage(service_context=service_context, storage_context=storage_context, index_id="vector_index")

    # Initialize query engine
    chatbot.query_engine = chatbot.index.as_query_engine()

    # Submit query
    response = chatbot.query_engine.query(input_text)

    return response.response

iface = gr.Interface(fn=chatbot,
inputs=gr.Textbox(lines=7, label="Enter your text"),
outputs="text",
title="Aurora")


index = construct_index("docs")
iface.launch(share=True)