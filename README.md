### 1.PROJECT STRUCTURE
```
assests         : contain assests for readme.md   
data            : knowledge base for RAG
Mytools         : tools available to AGENT
   |--- calci_mcp.py      
   |--- calci.py        : tool to implement mcp tool calling
   |--- firecrawler_.py : for web scrap,web search
   |--- RAG.py          : to retrieve data from knowlege base
main.py             : main AGENT file
ingest.py           : to create chroma db (ingestion phase)
README.md           
.envexample
```

### 2. TABLE OF CONTENT
This **documentation** covers some important topics for begginer to understand the following things ,
  - Tool calling
  - RAG working
  - Main agent working
---
### 3. HOW TO RUN THIS PROJECT 

Download all **requirements** by running and also make sure you have python installed,
```python
python install -r requirements.txt
```

1. First run the following code to **create chroma db** for RAG .
```python
python run ingest.py
```

2. Then, run main.py to have **conversation** with the agent.
```python
python run main.py
```
---
### 4. TOOL CALLING

#### LLM AND TOOLS :

In order to make our **AI agent** powerful and more structured we need to provide them access to **tools**. The tools can be , 
- A Simple **python** function 
- A **MCP** tool
- A **RAG** tool
---
#### 4.a HOW THE LLM USES MCP TOOLS :

The llm does not directly use those tools , instead it **two important things** :  
1. It **identifies** the correct tool for the user's **query**. Then , return a structured schema with **tool name** , **args** , etc ..,  
2. After , we call the tool with that **structured schema** , we need **AI** to refine the **result**.
---
#### 4.b SIMPLE WORKFLOW
The following picture shows how the llm and tool work together ,
![workflow-1](assests/workflow.jpeg)
- Here the **llm** picks the **proper tool** for the user's **query**.
- Then return a **structured response** to call a specific tool.

![workflow-2](assests/workflow2.jpeg)
- After that we call our python function(or **tool**) using the llm's **structured response to call tool**.
- Finally we once again pass the result taken from the tool to **llm** , to make the result as an **human friendly response**.
- Also , we need to pass **three** things to maintain the **context** of conversation with llm :   
    1. The user **query**
    2. llm's **tool call request**
    3. tool's **return value**


- You can see this documentation for more detailed explaination : [Gemini-Function-Calling-Docs](https://ai.google.dev/gemini-api/docs/function-calling)
- see the files calci.py , calci_mcp.py  for coding related to this.

---  

#### 4.c NOTE
- you dont need a **seperate llm** to handle mcp tools (in calci.py ). You can just use the **main llm** ( in main.py ) to do the mcp tool work.

#### 5. RAG FLOW
RAG stands for **retrieval Augmented Generation** , it is used to get **predictable** outcome from llm that becomes **usefull** at some senarios.
There are **two phases** in RAG implementation :
   1. **ingestion phase** : creating a db for llm to work on 
   2. **retrieval phase** : to get information from db for a particular user query
- The ingestion phase have to **run only once** , and the retrieval phase have to run **every time** when the user sends a query that needs RAG tool.

Work of ingest.py (ingestion phase) :
  1. Load PDF 
  2. Extract text
    - If PDF has selectable text, use PyMuPDF
    - If scanned PDF, use OCR
  3. Convert each page into Document objects
  4. Split documents into chunks
  5. Embed chunks in vector db
  6. Store chunks into Chroma
  7. Exit
note : 
- if your pdf is a text based , you can directly use normal pdf_loader from langchain_core.documents_loader.
- if you have an image based pdf , you need to use this flow pdf -> pages -> text.

Work of RAG.py (retrieval phase) :
  1. load the chroma database 
  2. setup retiever tool
  3. retrieve result for the user query
  4. refine that result using llm 
  5. return the final response

#### DISCLAIMER
This **repository** is only for begginers to **understand** how agents call mcp tools, how rag system works , how to design a basic agent using langgraph.This **study agent** does not actually aimed to solve any real world problems.It is for **educational purpose**.