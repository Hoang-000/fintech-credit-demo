# Biên bản kiểm tra nội bộ – bản ứng dụng trước khi triển khai

- Đã xác minh bằng cách đọc tệp mô hình đã cung cấp: **LogisticRegression** (Huấn luyện với scikit-learn 1.6.1).
- Đặc trưng đầu vào mô hình: **22 cột** (tên và thứ tự được lấy từ pipeline đã fit).
- Số cột sau tiền xử lý: **27**; trùng với số đầu vào của Logistic Regression.
- Khi kiểm thử mô hình với các giá trị trung vị dữ liệu Home Credit và hồ sơ minh họa, P_risk thử nghiệm xấp xỉ **7,36%**; điểm tổng hợp khoảng **97,06**. Đây là thử nghiệm offline sử dụng lớp tương thích với sklearn 1.8, không phải kiểm chứng trên Streamlit Community Cloud.
- Đã thử 5 tình huống quy tắc với xác suất lấy **trực tiếp từ mô hình** trong môi trường kiểm thử: 5/5 ra trạng thái dự kiến.
- Đã thử bộ 8 bài kiểm thử quy tắc độc lập (`python -m unittest discover -s tests -v`): **8/8 PASS**.
- Biên bản này **không** chứng minh hiệu năng hay độ chính xác của mô hình trên dữ liệu MoMo thật hoặc kết quả triển khai cloud.

## Tình huống kiểm tra

| Mã | Điều kiện | Kết quả quy tắc |
|---|---|---|
| TC01 | Hồ sơ tốt, DTI 10%, CIC 1 | Đề xuất duyệt |
| TC02 | CIC Nhóm 4 | Đề xuất từ chối |
| TC03 | DTI 83,3% | Đề xuất từ chối |
| TC04 | eKYC chưa xác minh | Đề xuất từ chối |
| TC05 | Trạng thái đối tác pending | Xem xét thêm / Chờ bổ sung |

Lưu ý phiên bản: tệp joblib gốc được tạo bằng scikit-learn 1.6.1. Môi trường phân tích offline hiện có scikit-learn 1.8.0 nên các phép thử mô hình được chạy trong môi trường có bản vá tương thích **chỉ dùng để kiểm tra**, không chuyển bản vá vào ứng dụng. Bản triển khai được yêu cầu pin `scikit-learn==1.6.1` trong requirements, chọn Python 3.12 trên Streamlit Cloud.
