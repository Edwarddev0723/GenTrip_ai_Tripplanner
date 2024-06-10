from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.document_loaders import JSONLoader

def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["Name"] = record.get("Name")
    metadata["Add"] = record.get("Add")
    metadata["Tel"] = record.get("Tel")
    metadata["Website"] = record.get("Website")
    metadata["Px"] = record.get("Px")
    metadata["Py"] = record.get("Py")
    metadata["LowestPrice"] = record.get("LowestPrice")
    metadata["CeilingPrice"] = record.get("CeilingPrice")
    return metadata

loader = JSONLoader(
    file_path='data/hdata.json',
    jq_schema='Description',
    metadata_func=metadata_func,
)

documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
documents = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings(api_key="Your_OPENAI_API_KEY")
vectorstore = FAISS.from_documents(documents, embeddings)

query = (
        f"Based on the provided keywords, search for all relevant data in the 'Description', 'Add' field descriptions from the business report data, and return the values of the 'Name' field. Here are the keyword: "
    )
keyword = '南投'
docs = vectorstore.similarity_search_with_score(query + keyword, k=5)
print(docs)