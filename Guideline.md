# Hướng Dẫn Đánh Giá Chất Lượng Cặp Câu Hỏi-Trả Lời (QA)

Hướng dẫn này cung cấp tiêu chí để đánh giá chất lượng cặp câu hỏi-trả lời (QA) trong công cụ xác thực XML.

## Những Tiêu Chí Đánh Giá

Công cụ sử dụng **6 tiêu chí** để đánh giá chất lượng QA. Mỗi tiêu chí có một checkbox trong giao diện. Hãy đánh dấu checkbox nếu tiêu chí đó đúng với cặp QA đang được đánh giá. **Lưu ý**: Có thể đánh dấu nhiều checkbox cho mỗi cặp QA nếu nhiều tiêu chí đều đúng.

1. **Cần một câu**:
   - Đánh dấu nếu câu hỏi chỉ cần thông tin từ **một câu** trong đoạn văn để trả lời.
   - Ví dụ: Câu hỏi hỏi về một chi tiết cụ thể được nêu rõ trong một câu duy nhất.

2. **Cần nhiều câu**:
   - Đánh dấu nếu câu hỏi cần thông tin từ **nhiều câu** trong đoạn văn để trả lời.
   - Ví dụ: Câu hỏi yêu cầu tổng hợp ý, hiểu hoặc so sánh thông tin từ nhiều phần của đoạn văn.

3. **Lựa chọn sai kém chất lượng**:
   - Đánh dấu nếu các lựa chọn sai (distractors) **không liên quan đến đoạn văn** hoặc **quá dễ loại bỏ**, làm đáp án đúng quá rõ ràng.
   - Ví dụ: Lựa chọn sai không dựa trên nội dung đoạn văn hoặc quá khác biệt so với đáp án đúng (vd: độ dài ngắn).

4. **Đoạn văn không phù hợp**:
   - Đánh dấu nếu đoạn văn **quá nhạy cảm** (ví dụ: liên quan đến chính trị, tôn giáo) hoặc **không phù hợp** để đặt câu hỏi.

5. **Đáp án không rõ ràng**:
   - Đánh dấu nếu câu hỏi có **nhiều đáp án đúng** hoặc đáp án đúng **không rõ ràng** dựa trên đoạn văn.
   - Ví dụ: Câu hỏi mơ hồ, hoặc thông tin trong đoạn văn không đủ để xác định đáp án duy nhất.

6. **Cần kiến thức ngoài**:
   - Đánh dấu nếu câu hỏi hoặc đáp án cần **kiến thức bên ngoài đoạn văn** để trả lời.
   - Ví dụ: Câu hỏi yêu cầu thông tin lịch sử hoặc khoa học không được đề cập trong đoạn văn.

## Lưu Ý
- Khi chấm điểm, hãy tick các checkbox trong giao diện công cụ (`xml_validation_ui.py`).
- Ghi chú không bắt buộc nhưng khuyến khích để biết rõ hơn các vấn đề cụ thể trong phần nhận xét để hỗ trợ cải thiện QA.
- Đảm bảo đánh giá công bằng, dựa trên các tiêu chí trên.
