# Chất Lượng Tổng Thể của QA (1-5)

Hướng dẫn này cung cấp tiêu chí để đánh giá chất lượng cặp câu hỏi-trả lời (QA) trong công cụ xác thực XML. Vui lòng đọc kỹ trước khi chấm điểm.

## Những Điều Cần Kiểm Tra

1. **Tính Rõ Ràng**:
   - Đoạn văn có dễ hiểu không?
   - Câu hỏi có rõ ràng và dễ hiểu không?
   - Câu hỏi có liên quan trực tiếp đến đoạn văn không?

2. **Tính Chính Xác**:
   - Câu trả lời đúng có được hỗ trợ hoàn toàn bởi thông tin trong đoạn văn không?
   - Các lựa chọn sai (distractors) có hợp lý nhưng rõ ràng là sai không?

3. **Tính Phù Hợp**:
   - Cặp QA hoặc đoạn văn có tránh được các chủ đề nhạy cảm (ví dụ: chính trị, tôn giáo) không?
   - Nội dung có phù hợp để mọi người hoặc mô hình sử dụng không?

## Hướng Dẫn Chấm Điểm

- **1**: Cặp QA không thể sử dụng được. Ví dụ:
  - Đoạn văn đề cập đến vấn đề nhạy cảm hoặc không phù hợp.
  - Câu hỏi mơ hồ, không rõ ràng.
  - Câu trả lời sai hoặc nội dung không phù hợp.
- **2**: Cặp QA có vấn đề nghiêm trọng. Ví dụ:
  - Đoạn văn khó hiểu.
  - Câu hỏi không rõ ràng.
  - Câu trả lời không chính xác hoặc không được hỗ trợ bởi đoạn văn.
- **3**: Cặp QA chấp nhận được nhưng có vấn đề nhỏ. Ví dụ:
  - Câu hỏi hơi khó hiểu.
  - Các lựa chọn sai không đủ mạnh hoặc không rõ ràng.
- **4**: Cặp QA tốt, chỉ cần chỉnh sửa nhỏ. Ví dụ:
  - Câu hỏi rõ ràng, câu trả lời đúng.
  - Một lựa chọn sai hơi yếu hoặc cần cải thiện.
  - Câu hỏi và trả lời đòi hỏi đọc 1 câu trong toàn bộ đoạn văn
- **5**: Cặp QA xuất sắc. Đặc điểm:
  - Rõ ràng, dễ hiểu.
  - Liên quan chặt chẽ đến đoạn văn.
  - Chính xác và được hỗ trợ đầy đủ.
  - Câu hỏi và trả lời đòi hỏi phải đọc hiểu toàn bộ đoạn văn
  - Phù hợp với mọi đối tượng.

## Lưu Ý
- Khi chấm điểm, sử dụng thang điểm từ 1 đến 5 trong giao diện công cụ (`xml_validation_ui.py`).
- Ghi chú các vấn đề cụ thể trong phần nhận xét để hỗ trợ cải thiện QA.
- Đảm bảo đánh giá công bằng, dựa trên các tiêu chí trên.
