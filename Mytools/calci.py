from mcp import StdioServerParameters
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

from google import genai
from google.genai import types

from typing import Optional,Any,Union
import asyncio
from dotenv import load_dotenv

load_dotenv('.env')

DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

class McpLlmClient:
    def __init__(self,model = 'gemini-2.5-flash'):
        self.session : Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        self.write : Optional[Any] = None
        self.read : Optional[Any] = None

        self.model = model

        #self.llm_async : it is not a 
        # seperate object for google sdk.

    async def load_tools(self):
        '''it loads the mcp tools in mcp schema format ,
        then we need to covert it to llm schema - function declaration.'''
        
        debug_print("[DEBUG] load_tools: creating server params")
        server_params = StdioServerParameters(
            command='python',
            args= ["Mytools/calci_mcp.py"]
        )

    # ASYNCHOROUS STACK IMPLEMENTATION
       # 1.  async with stdio_client(server_params) as (read,write)
        debug_print("[DEBUG] load_tools: entering stdio_client")
        self.read,self.write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        debug_print(f"[DEBUG] load_tools: read={type(self.read)}, write={type(self.write)}")
        
      # 2. async with clientSession(read,write) as session
        debug_print("[DEBUG] load_tools: creating ClientSession")
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.read,self.write)
        )
        debug_print(f"[DEBUG] load_tools: session={type(self.session)}")

      # 3. await ssssion.initialize()
        debug_print("[DEBUG] load_tools: initializing session")
        await self.session.initialize()
        debug_print("[DEBUG] load_tools: session initialized")

    # LIST TOOLS
        debug_print("[DEBUG] load_tools: listing tools")
        tools = await self.session.list_tools()
        debug_print(f"[DEBUG] load_tools: raw tools count={len(tools.tools)}")

    # CONVERT-TO-LLM SCHEME(see below)
        llm_tools = [{
            "name": tool.name ,
            "description" : tool.description ,
            "parameters" : tool.inputSchema

                } for tool in tools.tools ]
        debug_print(f"[DEBUG] load_tools: llm_tools={llm_tools}")
        return llm_tools

    async def process_query(self , query):
        ''' it takes the query and the listed tools and 
        give it to llm , to pick proper a tool with proper
        parameters.'''

        debug_print(f"[DEBUG] process_query: query={query!r}")
        tools = await self.load_tools()
        debug_print(f"[DEBUG] process_query: loaded {len(tools)} tools")
    # CONFIG
        debug_print("[DEBUG] process_query: creating Gemini client/config")
        client = genai.Client()
        tools = types.Tool(function_declarations=tools)
        config = types.GenerateContentConfig(tools=[tools])
    # GOOGLE - TOOL - CALLING RESPONSE
        debug_print("[DEBUG] process_query: sending first request to Gemini")
        response = await client.aio.models.generate_content(
            model = self.model,
            contents = query ,
            config = config
        )
        debug_print(f"[DEBUG] process_query: first response={response}")
    # CALL MCP TOOL
        result = ''
        function_call = ''
        debug_print("[DEBUG] process_query: checking for function call")
        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            debug_print(f"[DEBUG] process_query: function_call name={function_call.name}")
            debug_print(f"[DEBUG] process_query: function_call args={function_call.args}")
            result = await self.session.call_tool(
                    name = function_call.name ,
                    arguments = function_call.args
                    )
            debug_print(f"[DEBUG] process_query: tool result={result}")
    # 
        if not result or not function_call:
            debug_print("[DEBUG] process_query: no result/function_call, returning empty string")
            return ''
    # RESULT -> LLM -> FINAL RESPONSE
        debug_print("[DEBUG] process_query: building function response")
        function_response_part = types.Part.from_function_response(
            name=function_call.name,
            response={"result": result}
            )
        # 1.user-message
        # 2.ai response
        # 3.tools response
        contents = [
            types.Content(
                role="user", parts=[types.Part(text=query)]
                )
            ]
        contents.append(response.candidates[0].content)
        contents.append(types.Content(role="user", parts=[function_response_part]))
        
        client = genai.Client()
        debug_print("[DEBUG] process_query: sending final request to Gemini")
        final_response = await client.aio.models.generate_content(
            model=self.model,
            config=config,
            contents=contents,
        )
        debug_print(f"[DEBUG] process_query: final_response={final_response}")

        return final_response
    
    async def cleanup(self):
        """Clean up resources."""
        debug_print("[DEBUG] cleanup: closing exit stack")
        await self.exit_stack.aclose()
        debug_print("[DEBUG] cleanup: closed")
 