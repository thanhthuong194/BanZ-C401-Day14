import asyncio
import os
import sys
from typing import List, Dict
from dotenv import load_dotenv

# Import các thư viện từ Cairo RAG
from langchain_deepseek import ChatDeepSeek
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate

class MainAgent:
    def __init__(self):
        self.name = "CairoRAG-Streaming-v1"
        load_dotenv()
        
        # Khởi tạo tương tự như trước
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'} 
        )
        
        self.vector_db = Chroma(
            persist_directory="vector_db/",
            embedding_function=self.embeddings
        )
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 3})

        self.llm = ChatDeepSeek(
            model='deepseek-chat', 
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            temperature=0.1,
            streaming=True # Bật streaming mode
        )

        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""Bạn là một trợ lý ảo tư vấn chương trình kỹ sư chuyên sâu. 
            Sử dụng ngữ cảnh sau để trả lời. Trả lời bằng tiếng Việt chuyên nghiệp.
            Ngữ cảnh: {context}
            Câu hỏi: {question}
            Trả lời:"""
        )

    async def query(self, question: str) -> Dict:
        """
        Thực hiện RAG với chế độ Streaming nội bộ.
        """
        # 1. RETRIEVAL
        docs = self.retriever.invoke(question)
        retrieved_ids = [f"{doc.metadata.get('source', 'unknown')}_page_{doc.metadata.get('page', 'unknown')}" for doc in docs]
        context_str = "\n\n".join([doc.page_content for doc in docs])

        # 2. GENERATION (STREAMING)
        prompt_val = self.prompt_template.invoke({"context": context_str, "question": question})
        
        full_answer = ""
        # In header để phân biệt trong log khi chạy benchmark
        print(f"\n[Streaming Response for: {question[:30]}...]", flush=True)
        
        # Sử dụng astream để nhận các chunk dữ liệu
        async for chunk in self.llm.astream(prompt_val):
            content = chunk.content
            if content:
                print(content, end="", flush=True) # Hiển thị token ngay lập tức
                full_answer += content
        
        print("\n[End of Stream]\n", flush=True)

        # 3. RETURN FULL DATA FOR EVALUATION
        # Trả về format cũ để không làm gãy logic của BenchmarkRunner
        return {
            "answer": full_answer,
            "retrieved_ids": retrieved_ids,
            "contexts": [doc.page_content for doc in docs],
            "metadata": {
                "model": "deepseek-chat",
                "sources": retrieved_ids
            }
        }

if __name__ == "__main__":
    agent = MainAgent()
    async def test():
        await agent.query("Thời gian đào tạo hệ kỹ sư chuyên sâu là bao lâu?")
    asyncio.run(test())