# Báo cáo Cá nhân - Lab Day 14

- **Họ và tên:** Le Thanh Thuong  
- **MSSV:** 2A202600106

## 1. Vai trò và phạm vi công việc
Trong dự án Lab Day 14, tôi phụ trách chính phần **Eval Engine** trong thư mục `engine/`, tập trung vào các module:
- `engine/retrieval_eval.py`
- `engine/llm_judge.py`
- `engine/runner.py` 

Mục tiêu phần việc của tôi là hoàn thiện các thành phần đo lường để hệ thống benchmark có thể đánh giá Agent theo đúng yêu cầu rubric: Retrieval Metrics, Multi-Judge Consensus, và luồng chạy Benchmark/Regression.

## 2. Đóng góp kỹ thuật chính
### 2.1. Retrieval Evaluation
Tôi hoàn thiện logic đánh giá retrieval gồm:
- **Hit Rate**: kiểm tra khả năng lấy đúng tài liệu trong top-k.
- **MRR (Mean Reciprocal Rank)**: đo vị trí xuất hiện đầu tiên của tài liệu đúng.
- **Batch retrieval evaluation**: tổng hợp `avg_hit_rate`, `avg_mrr`, số lượng case hợp lệ/bị bỏ qua, giúp báo cáo ổn định khi dữ liệu thiếu trường.

Ý nghĩa kỹ thuật: đo được chất lượng truy xuất trước khi đánh giá chất lượng câu trả lời, giảm rủi ro kết luận sai nguyên nhân lỗi.

### 2.2. Multi-Judge Consensus
Tôi triển khai logic chấm điểm theo hướng multi-judge trong `llm_judge.py`:
- Duy trì chấm điểm từ 2 judge.
- Tính **agreement_rate** dựa trên độ lệch điểm.
- Bổ sung cơ chế xử lý xung đột điểm (khi lệch lớn thì chọn phương án bảo thủ).
- Hoàn thiện hàm kiểm tra **position bias** để phục vụ kiểm tra thiên vị thứ tự phản hồi.

Ý nghĩa kỹ thuật: tăng độ tin cậy của kết quả chấm, hạn chế phụ thuộc vào một judge đơn lẻ.

### 2.3. Benchmark Runner Integration
Tôi kiểm tra và đảm bảo `BenchmarkRunner` hoạt động đúng luồng:
1. Gọi agent lấy câu trả lời.
2. Chạy evaluator lấy metrics.
3. Chạy judge lấy điểm.
4. Gắn trạng thái pass/fail theo ngưỡng.
5. Hỗ trợ chạy async theo batch để tăng tốc benchmark.

## 3. Kết quả đạt được
- Pipeline benchmark chạy và sinh được báo cáo `reports/summary.json` và `reports/benchmark_results.json`.
- Hệ thống có đầy đủ chỉ số chính để chấm theo rubric:
  - Retrieval metrics (Hit Rate, MRR)
  - Multi-judge metrics (agreement + conflict handling)
  - Regression compare và release gate (V1 vs V2)
- `check_lab.py` xác nhận bài lab sẵn sàng để chấm điểm.

## 4. Kiến thức và chiều sâu kỹ thuật rút ra
### 4.1. MRR
MRR phản ánh không chỉ “có tìm đúng hay không” mà còn phản ánh “tìm đúng sớm hay muộn”. Vì vậy MRR rất hữu ích để đánh giá chất lượng ranking của retriever.

### 4.2. Position Bias
Khi judge so sánh hai phản hồi, thứ tự A/B có thể ảnh hưởng điểm. Vì thế cần cơ chế đảo vị trí để kiểm tra độ thiên vị và tăng tính công bằng.

### 4.3. Trade-off Chi phí vs Chất lượng
Chạy nhiều judge giúp tăng độ ổn định nhưng tăng chi phí và thời gian. Async batching là cách giảm thời gian tổng thể mà vẫn giữ được độ tin cậy của benchmark.

## 5. Vấn đề phát sinh và cách xử lý
- **Lỗi thiếu dataset đúng đường dẫn**: benchmark yêu cầu `data/golden_set.jsonl` nhưng dữ liệu ban đầu ở `data/data/golden_set.jsonl`; đã đưa về đúng path để pipeline chạy.
- **Lỗi thiếu API key**: khi thiếu `DEEPSEEK_API_KEY`, hệ thống không khởi tạo được model; đã bổ sung key qua `.env`.
- **Theo dõi file reports trong Git**: khi `reports/` từng bị ignore, cần cập nhật `.gitignore` và add lại đúng cách để nộp đủ artifacts.

## 6. Tự đánh giá cá nhân
Tôi đã hoàn thành đúng phần việc được phân công ở `engine/` và đóng góp trực tiếp vào các hạng mục kỹ thuật trọng tâm của lab (Metrics, Multi-Judge, Async Benchmark flow).  
Nếu có thêm thời gian, tôi muốn mở rộng phần judge calibration theo thống kê nâng cao (ví dụ Cohen's Kappa) và bổ sung báo cáo cost/token usage chi tiết để tối ưu thêm điểm phần Performance.
