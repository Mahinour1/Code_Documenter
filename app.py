import os
import getpass
from operator import itemgetter
from typing import List, Dict
import json
import requests



#LangChain, LangGraph
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, END
from typing_extensions import List, TypedDict
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.tools import Tool, tool
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

import chainlit as cl
import tempfile
import shutil




#helper imports
from code_analysis import *
from tools import search_pypi, write_to_docx
from prompts import describe_imports, main_prompt, documenter_prompt
from states import AgentState


# read openai key

# Global variables to store processed data
processed_file_path = None
document_file_path = None
vectorstore = None
main_chain = None
qdrant_client = None

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="Welcome to the Python Code Documentation Assistant! Please upload a Python file to get started.").send()

@cl.on_message
async def on_message(message: cl.Message):
    global processed_file_path, document_file_path, vectorstore, main_chain, qdrant_client
    
    if message.elements and any(el.type == "file" for el in message.elements):
        file_elements = [el for el in message.elements if el.type == "file"]
        file_element = file_elements[0]
        is_python_file = (
            file_element.mime.startswith("text/x-python") or 
            file_element.name.endswith(".py") or
            file_element.mime == "text/plain"  # Some systems identify .py as text/plain
        )
        if is_python_file:
            # Send processing message
            msg = cl.Message(content="Processing your Python file...")
            await msg.send()

            print(f'file element \n {file_element} \n')

            # Save uploaded file to a temporary location
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file_element.name)

            with open(file_element.path, "rb") as source_file:
                file_content_bytes = source_file.read()
                with open(file_path, "wb") as destination_file:
                    destination_file.write(file_content_bytes)
                
            processed_file_path = file_path

            try:
                
                # read file and extract imports
                file_content = read_python_file(file_path)
                imports = extract_imports(file_content, file_path)

                print(f'Done reading file')

                # Define describe packages graph
                search_packages_tools = [search_pypi]
                describe_imports_llm = ChatOpenAI(model="gpt-4o-mini")
                # describe_imports_llm = describe_imports_llm.bind_tools(tools = search_packages_tools, tool_choice="required")

                describe_imports_prompt = ChatPromptTemplate.from_messages([
                        ("system", describe_imports),
                        ("human", "{imports}")
                    ])

                describe_imports_chain = (
                    {"code_language": itemgetter("code_language"), "imports": itemgetter("imports")}
                    | describe_imports_prompt | describe_imports_llm | StrOutputParser()
                )

                print(f'done defining imports chain')


                # Define imports chain function
                def call_imports_chain(state):
                    last_message= state["messages"][-1]
                    content = json.loads(last_message.content)
                    chain_input = {"code_language": content['code_language'], 
                                    "imports": content['imports']}
                    response = describe_imports_chain.invoke(chain_input)
                    return {"messages": [AIMessage(content=response)]}

                # bind model to tool or ToolNode
                imports_tool_node = ToolNode(search_packages_tools)

                # construct graph and compile
                uncompiled_imports_graph = StateGraph(AgentState)
                uncompiled_imports_graph.add_node("imports_agent", call_imports_chain)
                uncompiled_imports_graph.add_node("imports_action", imports_tool_node)
                uncompiled_imports_graph.set_entry_point("imports_agent")
                
                def should_continue(state):
                    last_message = state["messages"][-1]

                    if last_message.tool_calls:
                        return "imports_action"

                    return END

                uncompiled_imports_graph.add_conditional_edges(
                    "imports_agent",
                    should_continue
                )

                uncompiled_imports_graph.add_edge("imports_action", "imports_agent")

                compiled_imports_graph = uncompiled_imports_graph.compile()

                print(f'compiled imports graph')
                # Invoke imports graph
                initial_state = {
                    "messages": [{
                        "role": "human",
                        "content": json.dumps({
                            "code_language": "python",
                            "imports": imports
                        })
                    }]
                }

                # await msg.update(content="Analyzing imports and generating documentation...")
                msg.content = "Analyzing your code and generating documentation..."
                await msg.update()

                msg = cl.Message(content="Analyzing your code and generating documentation...")
                await msg.send()

                result = compiled_imports_graph.invoke(initial_state)

                # Define qdrant Database
                qdrant_client = QdrantClient(":memory:")

                embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
                embedding_dim = 1536

                qdrant_client.create_collection(
                    collection_name="description_rag_data",
                    vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE),
                )

                vectorstore = Qdrant(qdrant_client, collection_name="description_rag_data", embeddings=embedding_model)

                # Add packages chunks
                text = result['messages'][-1].content
                chunks = [
                    {"type": "Imported Packages", "name": "Imported Packages", "content": text},
                    #{"type": "Source Code", "name": "Source Code", "content": file_content},
                    
                ]

                docs = [
                    Document(
                        page_content=f"{chunk['type']} - {chunk['name']} - {chunk['content']}",  # Content for the model
                        metadata={**chunk}  # Store metadata, but don't put embeddings here
                    )
                    for chunk in chunks
                ]
                vectorstore.add_documents(docs)
                qdrant_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

                print('done adding docs to DB')
                #define documenter chain
                documenter_llm = ChatOpenAI(model="gpt-4o-mini")
                documenter_llm_prompt = ChatPromptTemplate.from_messages([
                    ("system", documenter_prompt),
                ])
                documenter_chain = (
                    {"context": itemgetter("context")}
                    | documenter_llm_prompt
                    | documenter_llm
                    | StrOutputParser()
                )

                print('done defining documenter chain')
                #extract description chunks from database
                collection_name = "description_rag_data"
                all_points = qdrant_client.scroll(collection_name=collection_name, limit=1000)[0]  # Adjust limit if needed
                one_chunk = all_points[0].payload
                input_text = f"type: {one_chunk['metadata']['type']} \nname: {one_chunk['metadata']['name']} \ncontent: {one_chunk['metadata']['content']}"

                print('done extracting chunks form DB')

                document_response = documenter_chain.invoke({"context": input_text})

                print('done invoking documenter chain and will write in docx')
                # write packages description in word file
                document_file_path  = write_to_docx(document_response)

                print('done writing docx file')
                # Set up Main Chain for chat
                main_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


                main_llm_prompt = ChatPromptTemplate.from_messages([
                    ("system", main_prompt),
                    ("human", "{query}")
                ])

                main_chain = (
                    {"context": itemgetter("query") | qdrant_retriever, "code_language": itemgetter("code_language"), "query": itemgetter("query"), }
                    | main_llm_prompt
                    | main_llm
                    | StrOutputParser()
                )

                print('done defining main chain')
                # Present download button for the document
                elements = [
                    cl.File(
                        name="documentation.docx",
                        path=document_file_path,
                        display="inline"
                    )
                ]
                print('done defining elements')
                msg.content = "✅ Your Python file has been processed! You can download the documentation file below. How can I help you with your code?"
                msg.elements = elements
                await msg.update()

                # await msg.update(
                #         content="✅ Your Python file has been processed! You can download the documentation file below. How can I help you with your code?.",
                #         elements=elements
                #     )
                
            except Exception as e:
                # await msg.update(content=f"❌ Error processing file: {str(e)}")
                msg.content = f"❌ Error processing file: {str(e)}"
                await msg.update()

                # msg = cl.Message(content=f"second message ❌ Error processing file: {str(e)}")
                # await msg.send()
        
        else:
            await cl.Message(content="Please upload a Python (.py) file.").send()

    # Handle chat messages if file has been processed
    elif processed_file_path and main_chain:
        user_input = message.content
        # Send thinking message
        msg = cl.Message(content="Thinking...")
        await msg.send()

        try:
            # Use main_chain to answer the query
# invoke main chain
            inputs = {
                'code_language': 'Python',
                'query': user_input
            }

            response = main_chain.invoke(inputs)

            # Update with the response
            # await msg.update(content=response)
            msg.content = response
            await msg.update()

            # msg = cl.Message(content=response)
            # await msg.send()

        except Exception as e:
            # await msg.update(content=f"❌ Error processing your question: {str(e)}")
            msg.content = f"❌ Error processing your question: {str(e)}"
            await msg.update()

            # msg = cl.Message(content=f"❌ Error processing your question: {str(e)}")
            # await msg.send()

    else:
        await cl.Message(content="Please upload a Python file first before asking questions.").send()


@cl.on_stop
def on_stop():
    global processed_file_path
    # Clean up temporary files
    if processed_file_path and os.path.exists(os.path.dirname(processed_file_path)):
        shutil.rmtree(os.path.dirname(processed_file_path))

