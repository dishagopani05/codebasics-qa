from langchain.document_loaders import CSVLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os 
from model import llm

load_dotenv()

instructor_embeddings = HuggingFaceInstructEmbeddings()
vectoerdb_file_path="faiss_index"

def create_vector_db():
    loader = CSVLoader(file_path='codebasics_faqs.csv', source_column="prompt")
    data = loader.load()
    vectordb = FAISS.from_documents(documents=data, embedding=instructor_embeddings)
    vectordb.save_local(vectoerdb_file_path)

def get_qa_chain():
        
    vectordb = FAISS.load_local(
        folder_path=vectoerdb_file_path,    
        embeddings=instructor_embeddings,
        allow_dangerous_deserialization=True
    )

    retriever=vectordb.as_retriever(score_threshold=0.7)
    
    prompt_template = """Given the following context and a question, generate an answer based on this context only.
        In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
        If the answer is not found in the context, kindly state "I don't know." Don't try to make up an answer.

        CONTEXT: {context}  

        QUESTION: {question}"""
        
    PROMPT = PromptTemplate(
            template = prompt_template, 
            input_variables = ['context', 'question']
        )
    
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  
        retriever=retriever,
        input_key="query",
        return_source_documents=True,
        chain_type_kwargs = {"prompt" : PROMPT}
        )   
    print(chain)
    return chain

if __name__ == "__main__":
    # create_vector_db()
    
    chain = get_qa_chain()
    
    print(chain("Do you provide internships? Do you have EMI options?"))


