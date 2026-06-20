# tool calculator mcp 

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name = 'calculator-mcp',
    host = '0.0.0.0' ,
    port = 8050
)

@mcp.tool()
def adder(a:int,b:int)->int:
    '''This tools is used add two integers.'''
    return a+b

@mcp.tool()
def subtractor(a:int,b:int)->int:
    '''This tools is used to subtract two integers.'''
    return a-b

@mcp.tool()
def multipy(a:int,b:int)->int:
    '''This tools is used to multiply two integers.'''
    return a*b

@mcp.tool()
def divide(a:int,b:int)->int:
    '''This tools is used to divide two integers.'''
    if b == 0:
        return -1
    return a/b

transport_method = 'stdio'
if __name__ == "__main__":
    mcp.run(transport= transport_method)