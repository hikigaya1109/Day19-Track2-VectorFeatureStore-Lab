# Reflection — Lab 19

**Tên:** hikigaya1109
**Cohort:** A20
**Path đã chạy:** lite

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

Kết quả Precision@10 trên 50 golden queries: Keyword=77.8%, Semantic=73.2%, **Hybrid=78.6%** (thắng tổng thể).

- **Exact queries** (ví dụ: "Qdrant vector database"): BM25 thắng vì từ khóa chính xác là tín hiệu mạnh nhất; semantic dễ bị nhiễu bởi các doc "tương tự về nghĩa" nhưng không chứa keyword đó.
- **Paraphrase queries** (ví dụ: "mở rộng tự động theo tải" → docs về "auto-scaling"): Semantic thắng vì embedding hiểu ngữ nghĩa xuyên ngôn ngữ mà BM25 bỏ lỡ hoàn toàn.
- **Mixed queries**: Hybrid thắng nhờ RRF kết hợp cả hai tín hiệu — doc có cả keyword khớp lẫn vector gần được boost lên top.

**Khi nào KHÔNG dùng hybrid:** (1) Corpus toàn code/product SKU — exact match đủ, hybrid tăng latency 5× vô ích (33ms vs 7ms). (2) Budget latency cực thấp (<5ms) trong edge inference — chỉ dùng BM25.

**TTL lý do:** `query_velocity` TTL=1h vì rate-limit phải phát hiện spike real-time; dùng TTL=30d sẽ bỏ lỡ burst attack trong giờ đó.

---

## Điều ngạc nhiên nhất khi làm lab này

RRF với k=60 cố định đã đủ để hybrid vượt cả hai mode đơn lẻ mà không cần tuning — sự đơn giản của công thức `1/(k + rank)` che giấu một hiệu quả đáng kinh ngạc khi kết hợp hai phân phối score rất khác nhau (sparse BM25 vs dense cosine).

---

## Bonus challenge

- [ ] Đã làm bonus (xem `bonus/`)
- [ ] Pair work với: _không có_
