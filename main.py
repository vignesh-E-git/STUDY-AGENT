from typing import Sequence,Annotated,TypedDict,Union

from langgraph.graph import StateGraph,START,END
from langchain_google_genai import ChatGoogleGenerativeAI # gemini-2.5-flash
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, AIMessage,HumanMessage,ToolMessage,SystemMessage
from langgraph.graph.message import add_messages

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

import asyncio
from Mytools.RAG import invoke_rag
from Mytools.firecrawler_ import scrape_website as scrp
from Mytools.firecrawler_ import search_website as srch
from Mytools.calci import McpLlmClient 
load_dotenv()

# AGENT STATE SCHEMA
class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage],add_messages] # to track conversation history


# TOOLS
@tool
async def calci(query:str)->str:
    '''This tool is an mcp calculator tool.'''
    print('-'*30)
    client = McpLlmClient()
    try:
        result = await client.process_query(query)
        return result
    except:
        return ''
    finally:
        await client.cleanup()

@tool
def rag_tool(query:str)->str:
    '''This tool is used to retrieve related data from student's textbook.'''
    print('-'*30)
    return invoke_rag(query)

@tool
def search_website(query:str)->str:
    '''This tool helps to search webistes on internet.
       it return 3 websites.'''
    print('-'*30)
    return srch(query)

@tool
def scrape_website(url:str)->str:
    '''This tool helps to scrape an website.'''
    print('-'*30)
    return scrp(url)


# LLM
tools = [calci,rag_tool,scrape_website,search_website]
llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash',
                             temperature = 0).bind_tools(tools)

# NODES
def process(state:AgentState)->AgentState:
    print('AT PROCESS NODE')
    system_prompt = SystemMessage(
        content='You are an student helper. always try to utilize your tools.')
    
    result = llm.invoke( [system_prompt] +state['messages'])

    print(f'\nAI : {result.content}')
    # setup user query for rag
    return {'messages':[result]}

def should_continue(state:AgentState): # conditional node
    print('AT SHOULD CONTINUE NODE')
    last_msg = state['messages'][-1]
    if not last_msg.tool_calls:
        return 'exit'
    else:
        return 'tool_edge'

async def tool_node(state:AgentState)->AgentState:
    tools = state['messages'][-1].tool_calls #->list
    # extract the names and args
    for tool in tools:
        name = tool['name']
        args = tool['args']
        id_ = tool['id']
        print(f'tool called : {name} with arguments : {args}')
        result = ''
        msg = []
        if name == 'calci':
            result = calci.ainvoke(args)
        elif name == 'rag_tool':
            result = rag_tool.invoke(args)
        elif name == 'search_website':
            result = search_website.invoke(args)
        elif name == 'scrape_website':
            result = scrape_website.invoke(args)
        else:
            result = 'provide proper tool name'
        msg.append(ToolMessage(content=result,
                               tool_call_id=id_) )
    return {'messages':msg}

# GRAPH
graph = StateGraph(AgentState)

graph.add_node('process',process) 
graph.add_node('should_continue',lambda state:state)
graph.add_node('tool_node',tool_node)

graph.add_edge(START,'process')
graph.add_edge('process','should_continue')
graph.add_conditional_edges('should_continue',should_continue,
                            path_map= {
                                'exit':END ,
                                'tool_edge': 'tool_node'
                            })
graph.add_edge('tool_node','process')

# PNG
app = graph.compile()
app.get_graph().draw_mermaid_png(output_file_path='assests/flowGraph.png')

# INPUT
async def starting():
    conversation = []
    user_input = input('YOU :')

    while user_input != 'quit':
        conversation.append(HumanMessage(content=user_input))

        final_state = await app.ainvoke({'messages':conversation})

        #print(f'final state : /n{final_state}')

        conversation = final_state["messages"]
        user_input = input('\nYOU : ')

if __name__ == '__main__':
    asyncio.run(starting())