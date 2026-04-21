# Báo cáo Cá nhân - Lab Day 14

- **Họ và tên:** Lê Văn Tùng  
- **MSSV:** 2A202600111

## 1. Vai trò và phạm vi công việc
Trong dự án Lab Day 14, tôi phụ trách chính phần **RAG Agent và Data Pipeline**, bao gồm:
- Xây dựng chatbot RAG thật (`agent/main_agent.py`) thay thế dummy agent
- Xây dựng pipeline ingestion dữ liệu (`src/ingestion.py`) 
- Hoàn thiện bộ sinh dữ liệu tự động (`data/synthetic_gen.py`)
- Tạo Vector Database từ tài liệu PDF gốc

## 2. Đóng góp kỹ thuật chính

### 2.1. CAIRO-RAG Agent Implementation
Tôi triển khai agent RAG hoàn chỉnh trong `agent/main_agent.py` với kiến trúc:
- **Retrieval**: Sử dụng ChromaDB với embedding model `paraphrase-multilingual-MiniLM-L12-v2` hỗ trợ tiếng Việt, retriever top-k=3.
- **Generation**: Sử dụng GPT-4o-mini với streaming mode để hiển thị phản hồi realtime.
- **Prompt Engineering**: Thiết kế system prompt chuyên biệt cho tư vấn chương trình kỹ sư chuyên sâu, ép model trả lời dựa trên context.
- **Output Format**: Trả về đầy đủ `answer`, `retrieved_ids`, `contexts`, `metadata` để tương thích với BenchmarkRunner.

### 2.2. Data Ingestion Pipeline
Hoàn thiện `src/ingestion.py` cho pipeline:
- Đọc toàn bộ PDF từ thư mục `raw_data/` bằng PyPDFLoader.
- Chunking bằng RecursiveCharacterTextSplitter (chunk_size=1000, overlap=150) với các separators phù hợp văn bản tiếng Việt.
- Lưu vào ChromaDB tại `vector_db/` với embedding đã normalize.

### 2.3. Synthetic Data Generation (SDG)
Hoàn thiện `data/synthetic_gen.py` để tạo Golden Dataset tự động:
- Sử dụng DeepSeek Chat để sinh 3 cặp QA từ mỗi trang tài liệu (easy, medium, hard).
- Triển khai chiến lược Hard Cases theo yêu cầu lab: fact-check, prompt-injection, out-of-context, ambiguous.
- Mapping `expected_retrieval_ids` theo format khớp với agent output để tính Hit Rate chính xác.
- Chạy async với `asyncio.gather` để sinh 60 test cases từ 20 trang tài liệu.

## 3. Kết quả đạt được
- Agent RAG chạy thành công với streaming, trả lời câu hỏi về chương trình kỹ sư chuyên sâu Bách Khoa.
- Vector DB được build từ 7 file PDF gốc (quy định, chương trình đào tạo, học bổng, ngoại ngữ).
- Golden Dataset 60 cases bao gồm đầy đủ các loại: easy, medium, và hard (adversarial).
- Toàn bộ data pipeline hoạt động end-to-end, sẵn sàng cho benchmark.

## 4. Kiến thức và chiều sâu kỹ thuật rút ra

### 4.1. Chunking Strategy và ảnh hưởng đến Retrieval
RecursiveCharacterTextSplitter với separators `["\n\n", "\n", ".", " ", ""]` hoạt động tốt cho văn bản quy định có cấu trúc rõ ràng. Tuy nhiên, với tài liệu có bảng biểu hoặc danh sách phức tạp, fixed-size chunking có thể cắt đứt ngữ nghĩa. Semantic chunking sẽ là hướng cải tiến tiếp theo.

### 4.2. Embedding Model Selection cho Tiếng Việt
`paraphrase-multilingual-MiniLM-L12-v2` là lựa chọn tốt cho balance giữa chất lượng và tốc độ trên CPU. Tuy nhiên, các model như `bge-m3` hoặc `multilingual-e5-large` có thể cho retrieval quality cao hơn với trade-off về tốc độ và RAM.

### 4.3. Streaming vs Non-streaming trong Benchmark
Streaming mode giúp UX tốt hơn khi demo, nhưng trong benchmark context, nó tăng tổng latency do overhead mỗi chunk. Đối với benchmark, nên switch sang non-streaming để có measurement chính xác hơn.

## 5. Vấn đề phát sinh và cách xử lý
- **Retrieval ID format mismatch**: Ban đầu agent trả về ID khác format so với golden set, dẫn đến Hit Rate = 0. Đã chuẩn hóa format `{source}_page_{page}` ở cả agent và synthetic_gen.
- **DeepSeek API trả về format sai**: Một số lần gọi SDG, LLM trả về text thay vì JSON, gây lỗi parse. Đã xử lý bằng try-catch và JsonOutputParser, skip case lỗi.
- **Vector DB persistence**: ChromaDB cần `persist_directory` để lưu dữ liệu giữa các lần chạy. Ban đầu quên config dẫn đến mất data khi restart.

## 6. Tự đánh giá cá nhân
Tôi đã hoàn thành toàn bộ phần data pipeline và RAG agent, tạo nền tảng để nhóm có thể chạy benchmark và đánh giá. Phần việc chiếm khối lượng lớn nhất trong dự án vì mọi module khác đều phụ thuộc vào agent và data. Nếu có thêm thời gian, tôi muốn thử nghiệm hybrid retrieval (dense + sparse) và semantic chunking để cải thiện Hit Rate từ 0.30 lên mức cao hơn.
