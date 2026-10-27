# Mô phỏng chấm điểm tín dụng và cho vay nhanh – Demo môn Fintech

Đây là phiên bản **Streamlit đã chỉnh sửa** để triển khai trên Streamlit Community Cloud. Ứng dụng gồm ba chức năng:

1. Dashboard: thống kê **2.000 hồ sơ được nhóm tạo giả lập** từ notebook `FINTECH.ipynb`.
2. Tra cứu: xem lại kết quả CSV đã lưu của từng hồ sơ giả lập.
3. Khách hàng mới: **chạy mô hình Logistic Regression thật** trên dữ liệu đầu vào Home Credit và kết hợp bộ quy tắc mô phỏng.

**Lưu ý nghiên cứu:** Không thuộc/không kết nối MoMo, không sử dụng dữ liệu MoMo thực tế, không kết nối CIC. File lịch sử CSV dùng xác suất rủi ro lấy mẫu ngẫu nhiên từ tập test Home Credit, chứ không dự đoán riêng từng khách hàng MoMo. Đây chỉ là demo học thuật.

## Cách triển khai nhanh

- Tạo repository mới trên GitHub.
- Upload **toàn bộ file trong thư mục này vào thư mục gốc** của repository (đặc biệt `app.py`, `credit_engine.py`, `requirements.txt`, hai file `.joblib`, một `.json`, một `.csv`).
- Mở https://share.streamlit.io → `Create app` → `Yup, I have an app` → chọn repository, branch `main`, file `app.py`.
- Vào `Advanced settings` → **Python 3.12** → Deploy.
- Mở link `*.streamlit.app` để trình chiếu.

> Đọc `HUONG_DAN_DEPLOY_VA_CHUONG3.md` để xem hướng dẫn từng thao tác bằng tiếng Việt, 5 kịch bản demo và lỗi thường gặp.

## Chạy trên máy (tùy chọn)

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Kiểm thử

```bash
python -m unittest discover -s tests -v
python kiem_tra_mo_hinh.py
```

## Cấu trúc

- `app.py`: giao diện ba phân hệ Streamlit.
- `credit_engine.py`: tải và gọi pipeline + model thật; chấm điểm quy tắc từ JSON.
- `best_credit_model.joblib`: mô hình Logistic Regression đã huấn luyện (scikit-learn 1.6.1).
- `preprocessor_pipeline.joblib`: 22 đặc trưng đầu vào → 27 sau tiền xử lý.
- `rule_configuration.json`: giới hạn độ tuổi, DTI, trọng số, ngưỡng xét duyệt.
- `momo_loan_simulation_results.csv`: kết quả mô phỏng của notebook; lưu nguyên bản.
- `requirements.txt`: phiên bản thư viện; đặc biệt pin `scikit-learn==1.6.1`.
- `tests/`: bài kiểm thử quy tắc, không cần dữ liệu khách hàng thật.

## Các lựa chọn minh bạch về mặt dữ liệu

- Quy tắc nghiệp vụ dùng tiền **VNĐ theo kịch bản giả lập**.
- AI Home Credit dùng **các đơn vị tiền của dữ liệu huấn luyện Home Credit**, không suy ra bằng phép đổi tiền tùy tiện từ VNĐ.
- Các trường `EXT_SOURCE` chưa có dữ liệu sẽ được bổ sung bằng thống kê học trên tập Train qua `SimpleImputer`.
- Các đầu vào ảnh hưởng đến bộ quy tắc (CIC, eKYC, giao dịch ví, DTI) **không phải là các biến đầu vào trực tiếp** của mô hình Home Credit nếu chưa qua một mô hình mới được huấn luyện riêng.
- **Không có xác suất AI giả** khi mất kết nối mô hình. Nếu không tải được `.joblib`, trang 3 hiển thị lỗi.

## Hạn chế quan trọng

Không sử dụng mô hình này để phê duyệt tín dụng thực tế. Mô hình huấn luyện trên Home Credit và chưa được hiệu chỉnh cho khách hàng MoMo. Công nghệ Big Data trong dự án thể hiện ở quy trình tổng hợp, tạo đặc trưng và phân tích dữ liệu trong Colab; demo Streamlit **không** phải một hạ tầng Big Data vận hành thời gian thực.
