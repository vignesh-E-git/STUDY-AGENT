import pytesseract
import pdf2image

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

import os
from dotenv import load_dotenv

load_dotenv()
pdf_path = 'data/CHEMISTRY-BK.pdf'
db_path = 'data/chroma_db'
embed_model = GoogleGenerativeAIEmbeddings(model='gemini-embedding-2')

print('.....RAG PROCESS STARTED.....')

#-----------------------------------------
# 1. LOADING
image_pages = pdf2image.convert_from_path(pdf_path)
docs = []
for i,each_image in enumerate(image_pages[:2]):   # first two pages only
    text = pytesseract.image_to_string(each_image)
    doc = Document(page_content=text,
                   metadata = {"page":i+1})
    docs.append(doc)
 
if not docs:               # STEP 1 LOG
    print('1.ocr not extracted text.. properly')
else:
    print('1.text extracted successfully..')

#-----------------------------------------
# 2. CHUNKING
text_spliter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 250
)
chunks = text_spliter.split_documents(docs) # list of pdf-object-chunk-by-chunk
chunks = [c for c in chunks if c.page_content.strip()]

if not chunks:       # STEP-2 LOG
    print('2.error : chunking is empty..')
else:
    print('2.chunking process done successfully..')

#-----------------------------------------
# 3.EMBEDDING

def create_db(db_path):
    print('CREATING DATABASE....') # sSTEP-3 LOG
    try:
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embed_model,
            collection_name='chemistry',
            persist_directory = db_path
        )
    except Exception as e:
        print(f'FAILED TO CREATE DATA BASE . error : {e}')
        return 

    return 
#-----------------------------------------

create_db(db_path)




