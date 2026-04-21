# Báo cáo Cá nhân - Lab Day 14

- **Họ và tên:** Đinh Thái Tuấn  
- **MSSV:** 2A202600360

## 1. Vai trò và phạm vi công việc
Trong dự án Lab Day 14, tôi phụ trách chính phần **Phân tích kết quả benchmark và Failure Analysis**, tập trung vào:
- Phân tích kết quả từ `reports/benchmark_results.json` và `reports/summary.json`
- Viết báo cáo phân tích thất bại `analysis/failure_analysis.md`
- Đánh giá chất lượng hệ thống dựa trên các chỉ số Retrieval, Multi-Judge, và Latency

## 2. Đóng góp kỹ thuật chính

### 2.1. Phân tích Benchmark Results
Tôi phân tích toàn bộ 60 test cases từ kết quả benchmark để rút ra các insight:
- **Avg Score:** 2.61/5.0 — cho thấy hệ thống còn nhiều room để cải thiện, đặc biệt ở nhóm câu hỏi adversarial.
- **Hit Rate:** 0.30 — retrieval chưa tối ưu, cần cải thiện chunking strategy hoặc bổ sung reranking.
- **MRR:** 0.23 — tài liệu đúng thường không nằm ở vị trí top-1.
- **Agreement Rate:** 0.69 — mức đồng thuận giữa 2 judge ở mức trung bình, phản ánh sự khác biệt giữa API judge và heuristic fallback.

### 2.2. Failure Clustering & 5-Whys Analysis
Tôi phân nhóm các lỗi thành 4 nhóm chính:
1. **Prompt Injection không bị chặn** (19/24 case adversarial): System prompt thiếu guardrail cứng.
2. **Over-answer ngoài phạm vi tài liệu** (8 case): Model bổ sung suy luận ngoài context.
3. **Latency cao** (5 case > 35s): Context dài + streaming chưa có giới hạn.
4. **False pass do ngưỡng đơn giản**: Gate chỉ dựa `final_score >= 3`, chưa tách riêng safety.

Áp dụng phương pháp 5-Whys cho 3 case tệ nhất, tìm được root cause chung: thiếu policy guardrail độc lập và thiếu safety gate riêng cho nhóm red-team.

### 2.3. Action Plan
Đề xuất 6 hướng cải tiến cụ thể bao gồm: Semantic Chunking, Strict Refusal prompt, Reranking pipeline, Safety Gate riêng, và Cost/Token report.

## 3. Kết quả đạt được
- Hoàn thành `analysis/failure_analysis.md` với đầy đủ: tổng quan benchmark, phân nhóm lỗi, 5-Whys cho 3 case tệ nhất, và action plan.
- Các phân tích giúp nhóm hiểu rõ điểm yếu chính của hệ thống nằm ở adversarial handling và retrieval quality.

## 4. Kiến thức và chiều sâu kỹ thuật rút ra

### 4.1. Release Gate Design
Một release gate đơn giản (chỉ dựa trên average score) có thể che giấu các lỗi nghiêm trọng. Cần thiết kế gate đa chiều: tách riêng functional metrics, safety metrics, và performance metrics với ngưỡng riêng cho từng nhóm.

### 4.2. Multi-Judge Conflict Resolution
Khi 2 judge cho điểm lệch nhau nhiều (delta > 1), việc lấy trung bình không phản ánh đúng chất lượng. Chiến lược conservative (lấy điểm thấp hơn) giúp giảm rủi ro false positive, đặc biệt quan trọng với nhóm câu hỏi safety-critical.

### 4.3. Adversarial Evaluation
Trong thực tế, chatbot production cần được đánh giá riêng biệt với bộ test adversarial (prompt injection, out-of-context, ambiguous). Điểm trung bình cao trên bộ test tổng không đảm bảo an toàn khi triển khai.

## 5. Vấn đề phát sinh và cách xử lý
- **Kết quả benchmark không có API judge thật**: Do thiếu API key lúc chạy, hệ thống fallback sang heuristic scoring. Điều này làm agreement rate thấp hơn kỳ vọng. Giải pháp: cần chạy lại với đầy đủ API key để có kết quả chính xác hơn.
- **Khó phân loại lỗi tự động**: Việc phân nhóm lỗi phải thực hiện thủ công vì pipeline chưa có tag tự động cho từng loại câu hỏi. Đề xuất bổ sung metadata tagging trong benchmark results.

## 6. Tự đánh giá cá nhân
Tôi đã hoàn thành phần phân tích kết quả và failure analysis, đóng góp vào việc hiểu rõ điểm mạnh và điểm yếu của hệ thống. Phần phân tích 5-Whys giúp nhóm xác định được root cause và ưu tiên cải tiến. Nếu có thêm thời gian, tôi muốn tự động hóa phần failure clustering bằng script Python và bổ sung visualization cho benchmark results.
