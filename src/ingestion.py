import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DATA_PATH = "raw_data/"
DB_PATH = "vector_db/"

def build_vector_db():
    #Loading
    print("Đang đọc các file PDF...")
    loader = DirectoryLoader(DATA_PATH, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    print(f"Đã tải {len(documents)} trang tài liệu.")

    #Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Đã chia thành {len(chunks)} đoạn văn bản nhỏ.")

    #Initialize Embedding Model
    print("Đang khởi tạo Embedding model (paraphrase-multilingual-MiniLM-L12-v2)...")
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" # Model này hỗ trợ tiếng Việt cực tốt
    model_kwargs = {'device': 'cpu'} # Đổi thành 'cuda' nếu bạn có GPU
    encode_kwargs = {'normalize_embeddings': True}
    
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    # VectorDB
    print("Đang lưu dữ liệu vào Vector DB...")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    print(f"Hoàn thành! Vector DB đã được lưu tại: {DB_PATH}")

if __name__ == "__main__":
    # Đảm bảo thư mục data tồn tại
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"Thư mục {DATA_PATH} trống. Hãy bỏ các file PDF vào đó rồi chạy lại.")
    else:
        build_vector_db()