import asyncio
import os
from typing import List, Dict
from dotenv import load_dotenv

# Import các thư viện từ Cairo RAG của bạn
from langchain_deepseek import ChatDeepSeek
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate

class MainAgent:
    def __init__(self):
        self.name = "CairoRAG-v1"
        load_dotenv()
        
        print("🚀 Đang khởi tạo bộ não Cairo RAG...")
        
        # 1. Khởi tạo Embedding & VectorDB (Lấy cấu hình từ ingestion.py/chat.py của bạn)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'} 
        )
        
        # Đảm bảo đường dẫn đến vector_db của bạn là chính xác tương đối so với file main.py của Lab 14
        self.vector_db = Chroma(
            persist_directory="vector_db/", # Chú ý copy thư mục vector_db vào repo lab 14
            embedding_function=self.embeddings
        )
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 3})

        # 2. Khởi tạo LLM DeepSeek
        self.llm = ChatDeepSeek(
            model='deepseek-chat', 
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            temperature=0.1 
        )

        # 3. Prompt Template (Lấy từ chain.py của bạn)
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""Bạn là một trợ lý ảo tư vấn chương trình kỹ sư chuyên sâu. 
            Hãy sử dụng các đoạn ngữ cảnh sau đây để trả lời câu hỏi. 
            Nếu không biết câu trả lời, hãy nói là bạn không biết, đừng cố tự tạo ra câu trả lời.
            Trả lời bằng tiếng Việt một cách chuyên nghiệp.

            Ngữ cảnh: {context}

            Câu hỏi: {question}

            Trả lời:"""
        )

    async def query(self, question: str) -> Dict:
        """
        Thực hiện RAG nhưng tách bạch 2 bước để lấy được retrieved_ids cho việc Benchmark.
        """
        # --- BƯỚC 1: RETRIEVAL ---
        # Thay vì dùng invoke đồng bộ, gọi get_relevant_documents 
        docs = self.retriever.invoke(question)
        
        # Tạo danh sách ID ảo dựa trên source và trang để làm mốc đánh giá Hit Rate
        # Ví dụ: "data/Quy_che_Dao_tao.pdf_page_2"
        retrieved_ids = [f"{doc.metadata.get('source', 'unknown')}_page_{doc.metadata.get('page', 'unknown')}" for doc in docs]
        
        # Trích xuất nội dung text
        contexts = [doc.page_content for doc in docs]
        context_str = "\n\n".join(contexts)

        # --- BƯỚC 2: GENERATION ---
        # Điền context và câu hỏi vào Prompt
        prompt_val = self.prompt_template.invoke({"context": context_str, "question": question})
        
        # Gọi LLM (sử dụng ainvoke để chạy bất đồng bộ - async giúp hệ thống chạy nhanh hơn)
        response = await self.llm.ainvoke(prompt_val)

        # --- BƯỚC 3: TRẢ VỀ ĐÚNG FORMAT CỦA EVAL ENGINE ---
        return {
            "answer": response.content,
            "retrieved_ids": retrieved_ids, # <--- Cực kỳ quan trọng để chấm điểm Retrieval
            "contexts": contexts,
            "metadata": {
                "model": "deepseek-chat",
                "sources": retrieved_ids
            }
        }

if __name__ == "__main__":
    # Test chạy thử Agent trước khi Benchmark
    agent = MainAgent()
    async def test():
        resp = await agent.query("Chương trình đào tạo gồm bao nhiêu tín chỉ?")
        print("\n--- Câu trả lời ---")
        print(resp["answer"])
        print("\n--- IDs truy xuất được ---")
        print(resp["retrieved_ids"])
    asyncio.run(test())