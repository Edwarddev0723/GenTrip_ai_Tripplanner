import os
from typing import List, Optional, Dict
import csv
from flask import Flask, request, jsonify, send_from_directory
from langchain_community.vectorstores import Chroma
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain import hub
import pandas as pd

app = Flask(__name__)

os.environ["OPENAI_API_KEY"] = "Your_OPENAI_API_KEY"

class CSVLoader(BaseLoader):
    def __init__(
        self,
        file_paths: List[str],
        source_column: Optional[str] = None,
        csv_args: Optional[Dict] = None,
        encoding: Optional[str] = None,
    ):
        self.file_paths = file_paths
        self.source_column = source_column
        self.encoding = encoding
        self.csv_args = csv_args or {}

    def load(self) -> List[Document]:
        docs = []
        for file_path in self.file_paths:
            with open(file_path, newline="", encoding=self.encoding) as csvfile:
                csv_reader = csv.DictReader(csvfile, **self.csv_args)
                for i, row in enumerate(csv_reader):
                    content = "\n".join(f"{k.strip()}: {v.strip()}" for k, v in row.items())
                    try:
                        source = (
                            row[self.source_column]
                            if self.source_column is not None
                            else file_path
                        )
                    except KeyError:
                        raise ValueError(
                            f"Source column '{self.source_column}' not found in CSV file."
                        )
                    metadata = {"source": source, "row": i}
                    doc = Document(page_content=content, metadata=metadata)
                    docs.append(doc)
        return docs

# Load CSV files and initialize components
pwd=os.getcwd()
csv_folder = os.path.join(pwd, "utf8")
csv_files = [os.path.join(csv_folder, file) for file in os.listdir(csv_folder) if file.endswith('.csv')]
loader = CSVLoader(file_paths=csv_files, encoding='utf-8')
docs = loader.load()
print(len(docs))
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
split_docs = text_splitter.split_documents(docs)
Chroma.from_documents(documents=split_docs, embedding=OpenAIEmbeddings(model="text-embedding-3-large"), persist_directory="./chroma_db")
llm = ChatOpenAI(model="gpt-4o", temperature=0.65, max_tokens=None, timeout=None, max_retries=2,)
prompt = hub.pull("rlm/rag-prompt")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"))
qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": prompt}
    )

@app.route('/images/<filename>')
def send_image(filename):
    return send_from_directory('images', filename)

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query_text = data.get('query')
    if not query_text:
        return jsonify({"error": "No query provided"}), 400

    answer = qa_chain(query_text)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
