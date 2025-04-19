# Công Cụ Xác Thực Câu Hỏi XML

Hướng dẫn này giải thích cách cài đặt và chạy công cụ xác thực dữ liệu câu hỏi XML.

## Tệp XML
- Tệp mẫu `placeholder.xml` được cung cấp.
- Sử dụng tệp XML của bạn nếu được cung cấp, đảm bảo đúng cấu trúc. [Link đến drive của xml](https://drive.google.com/drive/u/1/folders/1gY8RWgrZnkmE3UnRUGauFLuqlzWIK9Kw)

## Video Hướng Dẫn
Xem video hướng dẫn cài đặt: [Link đến video](https://drive.google.com/file/d/17ufZjjW4X4WwbIQs47Cm1ehHFoY2pMG4/view?usp=drive_link).

## Yêu Cầu
- Python 3.9 trở lên (bao gồm `tkinter` trên Windows/macOS; Linux cần cài `python3-tk`).
- Git (tùy chọn, để tải mã nguồn; hoặc tải dưới dạng ZIP).

## Hướng Dẫn Cài Đặt
1. **Tải Mã Nguồn**:
   - Cài Git từ [git-scm.com](https://git-scm.com/) nếu cần.
   - Tải mã nguồn: `git clone https://github.com/yourusername/xml-validator.git`, có thể qua terminal hoặc Github Desktop (Desktop sẽ dễ hơn)
   - Hoặc tải ZIP từ GitHub và giải nén.
   - Chuyển đến thư mục: `cd UET_TextSeg_MMRC_Validator`.

2. **Cài Đặt Python**:
   - Kiểm tra Python 3.9 trở lên: `python --version` hoặc `python3 --version`.
   - Nếu chưa cài:
     - **Windows/macOS**: Tải từ [python.org](https://www.python.org/downloads/). Chọn "Add Python to PATH" khi cài đặt.
     - **Linux**: Chạy `sudo apt-get install python3 python3-tk` (Ubuntu/Debian) hoặc tương đương.
   - Kiểm tra `tkinter`: Chạy `python -m tkinter` (hoặc `python3 -m tkinter`). Một cửa sổ nhỏ sẽ xuất hiện.

3. **Chạy Ứng Dụng**:
   - Mở terminal trong thư mục mã nguồn.
   - Chạy:
     - Windows: `python xml_validation_ui.py [placeholder.xml]`
     - Linux/macOS: `python3 xml_validation_ui.py [placeholder.xml]`
   - Với tệp XML tùy chỉnh: Thay `placeholder.xml` bằng tệp của bạn (ví dụ: `python3 xml_validation_ui.py MaSv_Ho_Va_Ten.xml`).

4. **Xác Thực Qua Nhiều Phiên**:
   - Tiến độ (điểm số, nhận xét) tự động lưu vào `<tên_tệp>_progress.json` (ví dụ: `MaSv_Ho_Va_Ten.json`).
   - Chạy lại lệnh để tiếp tục từ vị trí đã dừng.
   - Sau khi hoàn thành gửi lại file `<tên_tệp>_progress.json` cho mình để hoàn thành điểm cộng

## Khắc Phục Sự Cố
- **Không tìm thấy Python**: Đảm bảo Python được cài và thêm vào PATH. Cài lại nếu cần.
- **Lỗi Tkinter**: Người dùng Linux cài `python3-tk` (`sudo apt-get install python3-tk`). Người dùng Windows/macOS cài lại Python.
- **Không tìm thấy tệp**: Đảm bảo tệp XML trong cùng thư mục với file .py và đường dẫn đúng.
- Liên hệ với mình nếu có vấn đề.

