# Báo cáo Cá nhân - Lab Day 14

- **Họ và tên:** Nguyễn Đức Sĩ  
- **MSSV:** 2A202600152

## 1. Vai trò và phạm vi công việc
Trong dự án Lab Day 14, tôi phụ trách phần **Benchmark Execution, Quality Assurance và Integration Testing**, tập trung vào:
- Chạy benchmark pipeline end-to-end và kiểm tra kết quả
- Review và merge code từ các thành viên thông qua Pull Request
- Đảm bảo tích hợp giữa các module (agent, engine, data) hoạt động đúng

## 2. Đóng góp kỹ thuật chính

### 2.1. Benchmark Execution & QA
Tôi chịu trách nhiệm chạy thử và kiểm tra toàn bộ pipeline benchmark:
- Chạy `main.py` để thực thi BenchmarkRunner trên toàn bộ 60 test cases.
- Kiểm tra output sinh ra trong `reports/benchmark_results.json` và `reports/summary.json` có đầy đủ các metrics theo yêu cầu rubric.
- Xác nhận pipeline hoạt động end-to-end: Agent → Retrieval Eval → Multi-Judge → Pass/Fail → Report.

### 2.2. Code Integration & PR Review
Tôi thực hiện review và merge các Pull Request từ các nhánh feature:
- Merge PR từ nhánh `letung` (CAIRO-RAG implementation + synthetic data generation).
- Merge PR từ nhánh `si` (integration testing và pipeline verification).
- Đảm bảo không có conflict giữa các module khi merge về `main`.

### 2.3. Pipeline Verification
Kiểm tra tính nhất quán của dữ liệu qua các bước:
- Golden dataset (`data/golden_set.jsonl`) có đủ 60 cases với format đúng.
- Vector DB (`vector_db/`) được build đúng từ raw PDF data.
- Retrieval IDs format trong agent khớp với expected_retrieval_ids trong golden set.
- `check_lab.py` pass tất cả các kiểm tra.

## 3. Kết quả đạt được
- Pipeline benchmark chạy thành công end-to-end, sinh đầy đủ artifacts cho submission.
- Tất cả PR được merge clean, không có regression.
- `check_lab.py` xác nhận bài lab đạt yêu cầu.

## 4. Kiến thức và chiều sâu kỹ thuật rút ra

### 4.1. Hit Rate vs MRR
Hit Rate chỉ đo "có tìm đúng hay không" trong top-k, còn MRR đo "tìm đúng ở vị trí nào". Trong thực tế, MRR quan trọng hơn vì vị trí top-1 ảnh hưởng trực tiếp đến chất lượng context cho LLM generation. Hệ thống hiện tại có Hit Rate = 0.30 và MRR = 0.23, cho thấy retriever cần được cải thiện.

### 4.2. Async Batching cho Benchmark
Việc chạy benchmark song song bằng `asyncio.gather` với batch_size giúp giảm đáng kể thời gian tổng. Tuy nhiên cần cân nhắc rate limit của API — batch_size quá lớn sẽ gây lỗi 429 (Too Many Requests).

### 4.3. Cohen's Kappa trong Multi-Judge
Agreement rate hiện tại đo đơn giản bằng delta điểm. Trong thực tế, Cohen's Kappa sẽ chuẩn hơn vì nó loại trừ sự đồng thuận ngẫu nhiên, cho phép đánh giá chính xác hơn mức độ tin cậy giữa các judge.

## 5. Vấn đề phát sinh và cách xử lý
- **Conflict khi merge nhánh**: Khi merge PR từ nhánh `letung` và `si`, có conflict ở file cấu hình. Giải quyết bằng cách giữ lại cả hai thay đổi và test lại pipeline.
- **Thiếu dependencies**: Lần chạy đầu tiên bị lỗi do thiếu thư viện `langchain-chroma` và `sentence-transformers`. Đã bổ sung đầy đủ vào `requirements.txt` và `pyproject.toml`.
- **Golden set path mismatch**: Dữ liệu ban đầu ở `data/data/golden_set.jsonl` nhưng pipeline đọc từ `data/golden_set.jsonl`. Đã move file về đúng path.

## 6. Tự đánh giá cá nhân
Tôi đã đảm bảo pipeline chạy đúng và các module tích hợp không bị lỗi. Vai trò QA và integration giúp nhóm phát hiện sớm các vấn đề về path, dependencies, và format dữ liệu trước khi chạy benchmark chính thức. Nếu có thêm thời gian, tôi muốn viết thêm integration test tự động cho pipeline và bổ sung CI/CD check.
