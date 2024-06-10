import os
from typing import List, Optional, Dict
import csv
from langchain_community.vectorstores import Chroma
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain import hub
import pandas as pd
import os
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
                csv_reader = csv.DictReader(csvfile, **self.csv_args)  # type: ignore
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


# Rag
pwd=os.getcwd()
csv_folder = os.path.join(pwd, "utf8")
csv_files = [os.path.join(csv_folder, file) for file in os.listdir(csv_folder) if file.endswith('.csv')]
loader = CSVLoader(file_paths=csv_files, encoding='utf-8')
docs = loader.load()
print(len(docs))
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
split_docs = text_splitter.split_documents(docs)
Chroma.from_documents(documents=split_docs, embedding=OpenAIEmbeddings(model="text-embedding-3-large"), persist_directory="./chroma_db")
llm = ChatOpenAI(model="gpt-4o")
prompt = hub.pull("rlm/rag-prompt")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"))
qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": prompt}
    )
qu = """你是一名30年資歷並且擅長規劃行程的台灣導遊. 請幫我根據提供的信息，請給我制定一個詳細的旅遊計劃，包括具體的餐廳名稱和酒店名稱。此外，所有細節都應符合常識。景點參觀和用餐應該多樣化。。將“在家吃飯/在路上吃飯”這類非具體信息替換為更具體的餐廳。請給我一個台南的行程安排，為期4天，假設每天從上午10點開始到晚上8點結束，每個活動之間有30分鐘的緩衝時間。我喜歡參觀博物館，住宿類型我喜歡民宿。請告訴我明確且具體我要下榻的住宿地點，並且希望一天至兩天至少換一間酒店，請將輸出json字符串的長度限制在1200個字符內。生成旅行行程的結構化JSON表示。

       {
  "days": [
    {
      "day": 1,
      "activities": [
        {
          "title": "活動1",
          "description": "活動1的描述",
          "link": "https://XXXX",
          "start_time": "10:00 AM",
          "end_time": "12:00 PM",
          "location": "https://maps.google.com/?q=location1",
          "charge" : "$xxx"
        },
        {
          "title": "活動2",
          "description": "活動2的描述",
          "link": "https://XXXX",
          "start_time": "02:00 PM",
          "end_time": "04:00 PM",
          "location": "https://maps.google.com/?q=location2",
          "charge" : "$xxx"
        },
        ....
        {
          "title": "Day 1 飯店",
          "description": "Day 1 飯店的描述",
          "link": "https://XXXX",
          "start_time": "08:00 PM",
          "end_time": "12:00 PM",
          "location": "https://maps.google.com/?q=location2",
          "charge" : "$xxx"
        }
      ]
    },
    {
      "day": 2,
      "activities": [
        {
          "title": "另一個活動1",
          "description": "另一個活動1的描述",
          "link": "https://XXXX",
          "start_time": "09:30 AM",
          "end_time": "11:30 AM",
          "location": "https://maps.google.com/?q=location1",
          "charge" : "$xxx"
        },
        {
          "title": "另一個活動2",
          "description": "另一個活動2的描述",
          "link": "https://XXXX",
          "start_time": "01:00 PM",
          "end_time": "03:00 PM",
          "location": "https://maps.google.com/?q=location2",
          "charge" : "$xxx"
        },
        ...
        {
          "title": "Day 2 飯店",
          "description": "Day 2 飯店的描述",
          "link": "https://XXXX",
          "start_time": "08:00 PM",
          "end_time": "12:00 PM",
          "location": "https://maps.google.com/?q=location2",
          "charge" : "$xxx"}]}]}確保每一天都有一個 'day' 字段和一個包含 'title'、'description'、'link', 'start_time'、'end_time', 'location'和'charge' 字段的 'activities' 列表，請全部以小寫表示如果景點不用錢的話已0表示。並且chage費用請以新台幣表示，保持描述簡潔')"""
res = qa_chain({"query": qu })
print(res)