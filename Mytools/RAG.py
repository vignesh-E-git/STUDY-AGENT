import os

from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.messages import SystemMessage,HumanMessage,ToolMessage
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

embed_model = GoogleGenerativeAIEmbeddings(model='gemini-embedding-2')
llm = ChatGoogleGenerativeAI(model= 'gemini-2.5-flash')

def load_db():
    print('LOADING DATABASE...')
    try:
        vector_db = Chroma(
            persist_directory= 'data/chroma_db',
            collection_name='chemistry',
            embedding_function= embed_model
        )
    except Exception as e:
        print(f'failed to load database , error : {e}')
        vector_db = []
    return vector_db

def llm_response(chunks:Document,query:str)->str:
    docs = ''
    for i,chunk in enumerate(chunks):
        text = chunk.page_content
        docs += f'\n\n{i+1}. {text}'

    system_prompt = 'you are an answer extract. extract relevant short answer for the input query using the chunks(docs) given.'
    print('CALLING GEMINI AI.')
    try:
        response = llm.invoke([SystemMessage(content = system_prompt)
                            ,HumanMessage(content = query),HumanMessage(content=docs)])
        return response.content
    except Exception as e:
        print(f'Something wrong with gemini AI .\nERROR : {e}')
        return ''

# steps :
# 1. load the database (func)
# 2. setup retiever
# 3. retrieve result
# 4. refine using llm (func)
# 5. return response

def invoke_rag(query:str)->str:

    # 1.LOAD DATABASE
    print('CHECKING WHERE DATA EXISTS or NOT...')
    db_path = 'data/chroma_db'
    if os.path.exists(db_path):      
        print('DATABASE EXISTS')
        vector_db = load_db()
    else:
        print('DATABASE NOT EXISTS')
        print('run the ingest.py to create db..\npython ingest.py')
        return f'error'
    # 2. RETRIEVE
    print('RETRIVING CHUNKS....')       
    retriver = vector_db.as_retriever(
        search_type = 'similarity',
        search_kwargs = {'k':1}
    )
    res = retriver.invoke(query)

    if not res:
        print('no relevant chunk is found for the query...')
        return ''
    else:
        print('chunks retrieved successfully.')
        response = llm_response(res,query)
        return response



