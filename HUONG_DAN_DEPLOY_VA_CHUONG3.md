# HƯỚNG DẪN TRIỂN KHAI STREAMLIT VÀ DEMO CHƯƠNG 3

## A. Kiểm tra trước khi upload

1. Giải nén tệp `credit_scoring_streamlit_ready.zip` trên máy tính.
2. Mở thư mục `credit_scoring_streamlit`. Bên trong phải có tối thiểu:
   - `app.py`
   - `credit_engine.py`
   - `requirements.txt`
   - `best_credit_model.joblib`
   - `preprocessor_pipeline.joblib`
   - `rule_configuration.json`
   - `momo_loan_simulation_results.csv`
3. Không thay thế các tệp `.joblib` bằng file từ Colab chạy lại trên phiên bản thư viện khác, trừ khi đã xuất lại đồng thời cả pipeline và model.
4. **Không cần tải `FINTECH.ipynb` lên GitHub để ứng dụng hoạt động.** Notebook chỉ là bằng chứng và nguồn mã nghiên cứu. Không đăng dữ liệu cá nhân thật lên repository công khai.

## B. Tải lên GitHub – thao tác từng bước

1. Truy cập https://github.com → Đăng nhập hoặc tạo tài khoản.
2. Mở https://github.com/new → nhập `Repository name`: `fintech-credit-demo`.
3. Chọn `Public` nếu bạn muốn dùng được ứng dụng Streamlit Community Cloud theo cấu hình cộng đồng, và đảm bảo dữ liệu tải lên chỉ là dữ liệu giả lập/public.
4. Nhấn `Create repository`.
5. Trong trang repository chọn `Add file` → `Upload files` (hoặc `uploading an existing file`).
6. **Chọn toàn bộ tệp *bên trong* thư mục đã giải nén, không chỉ kéo file zip**; `app.py` và `requirements.txt` phải ở **thư mục gốc** repository. Các tệp `.joblib`, `.json`, `.csv` ở cùng cấp với `app.py`.
7. Cuộn xuống, bấm `Commit changes`. Khi xong, kiểm tra danh sách file hiển thị.

## C. Triển khai trên Streamlit Community Cloud

1. Truy cập https://share.streamlit.io, đăng nhập bằng GitHub.
2. Nhấn `Create app` → `Yup, I have an app`.
3. Điền:
   - Repository: `TÊN-GITHUB-CỦA-BẠN/fintech-credit-demo`
   - Branch: `main` (nếu repository của bạn dùng `main`)
   - Main file path: `app.py`
4. Vào `Advanced settings`: chọn **Python 3.12**. Đây là lựa chọn phù hợp với file model tạo bằng `scikit-learn==1.6.1`.
5. Nhấn `Deploy`. Nền tảng sẽ cài các thư viện từ `requirements.txt` và khởi động ứng dụng.
6. Khi triển khai thành công, nhận đường link `https://...streamlit.app`. Có thể dùng link này khi thuyết trình.

Lưu ý: Các thao tác trên dựa vào tài liệu Streamlit Community Cloud chính thức, có thể có thay đổi nhẹ về tên nút trong giao diện.

## D. Kiểm tra demo sau khi lên Streamlit

**Phân hệ 1 – Dashboard**
- Chọn `1. Dashboard 2.000 hồ sơ` ở thanh bên.
- Kiểm tra tổng 2.000 hồ sơ (CSV gốc: 740 đề xuất duyệt, 1.014 đề xuất từ chối, 246 xem xét thêm).
- Chụp ảnh 4 chỉ số và biểu đồ phân bổ kết quả + phân phối điểm.
- Khi thuyết trình, nói đây là thống kê hồ sơ giả lập, không là dữ liệu thực của ví MoMo.

**Phân hệ 2 – Tra cứu hồ sơ**
- Chọn `2. Tra cứu hồ sơ đã mô phỏng`.
- Chọn một mã mẫu như `M_CUST_0002` (đề xuất duyệt theo dữ liệu lưu sẵn).
- Xem thông tin, điểm S_rule, S_AI, S_final, DTI, lý do.
- Chụp ảnh kết quả, đặc biệt giải thích xác suất trong CSV lấy mẫu từ tập test Home Credit, không được mô hình dự đoán riêng cho hồ sơ đó.

**Phân hệ 3 – Chấm điểm hồ sơ mới, gọi mô hình thật**
- Chọn `3. Chấm điểm khách hàng mới (AI thật)`.
- Nếu app không tải được model, phải sửa lỗi phiên bản; không sử dụng xác suất mặc định.
- Với tình huống TC01, giữ giá trị mẫu và nhấn `Chạy mô hình AI và đánh giá tín dụng`.
- Đọc: `P_risk` từ Logistic Regression → `S_AI = 100*(1-P_risk)` → `S_final = 0.6*S_rule + 0.4*S_AI` → quyết định.
- Chụp ảnh trạng thái kết quả, 4 chỉ số và danh sách quy tắc.
- Chuyển sang TC02, TC03, TC04, TC05 và chụp tương ứng.

## E. Kịch bản kiểm thử gợi ý khi thuyết trình

| Mã | Tình huống | Điểm khác biệt | Kết quả mong đợi ở lớp quy tắc |
|---|---|---|---|
| TC01 | Hồ sơ tốt | Tuổi 27, eKYC đủ, CIC Nhóm 1, DTI 10%, dữ liệu AI trung vị | Đề xuất duyệt, nếu P_risk ≤10% |
| TC02 | Nợ xấu | CIC Nhóm 4 | Đề xuất từ chối (R06) |
| TC03 | Gánh nợ cao | Thu nhập 12 triệu, nợ 8 triệu, trả góp 2 triệu → DTI 83,3% | Đề xuất từ chối (R08) |
| TC04 | Chưa định danh | eKYC chưa xác minh | Đề xuất từ chối (R02) |
| TC05 | Trạng thái đối tác chưa rõ | `pending` | Xem xét thêm / chờ bổ sung (R04) |

Các TC02–TC05 minh họa **bộ quy tắc** và có thể bị loại trừ dù điểm AI vẫn cao, đúng theo thiết kế kết hợp. TC01 có kết quả dự kiến khi model tải đúng và đầu vào AI mặc định như bộ demo.

## F. Gợi ý nội dung báo cáo Chương 3

### 3.1. Thử nghiệm/Demo thực tế

**Mục tiêu:** Kiểm tra luồng xử lý từ nhập hồ sơ, tiền xử lý dữ liệu, dự đoán bằng AI và đánh giá theo quy tắc, đồng thời kiểm tra giao diện phản hồi và khả năng giải thích lý do.

**Môi trường:** Google Colab dùng huấn luyện và xuất hai tệp joblib; GitHub quản lý mã nguồn; Streamlit Community Cloud dùng hiển thị và mô phỏng các tình huống; dữ liệu thống kê là `momo_loan_simulation_results.csv` gồm 2.000 hồ sơ giả lập.

**Tổ chức kiểm thử:** Kiểm thử màn hình dashboard và truy vấn hồ sơ từ CSV; thực hiện ít nhất 5 test case trong bảng trên bằng mô hình AI thật ở màn hình nhập mới; lưu ảnh chụp kết quả và ghi nhận Pass/Fail theo tiêu chí.

**Kết quả:** Chỉ điền số liệu, ảnh minh chứng và kết quả thực tế sau khi đã chạy được bản công khai. Không viết rằng AI thực hiện chấm điểm từng hồ sơ MoMo trong CSV, bởi các xác suất CSV đã được lấy mẫu ngẫu nhiên từ dự đoán Home Credit.

**Giới hạn:** Model Home Credit chưa được hiệu chỉnh, đánh giá tính công bằng và kiểm định trên dữ liệu tín dụng thực tại Việt Nam; dữ liệu ví và CIC trong demo là giả lập. Đây là thử nghiệm khái niệm (proof of concept), không phải triển khai hệ thống cho vay thật.

### 3.2. Đề xuất, khuyến nghị và ý tưởng cải tiến

1. **Đồng nhất dữ liệu huấn luyện và dữ liệu vận hành:** Thu thập dữ liệu tín dụng thật hợp pháp, chọn biến phù hợp với hoạt động ví, xây dựng phương pháp ghép nối dữ liệu và quy đổi đơn vị thống nhất; không dùng quy đổi Home Credit/VNĐ tùy ý.
2. **Cải tiến mô hình:** Huấn luyện và so sánh Logistic Regression, Random Forest, XGBoost; kiểm định ROC-AUC/PR-AUC, calibration, dữ liệu ngoài mẫu, drift và sai lệch theo nhóm trước khi triển khai thực tế.
3. **Nâng cấp quy tắc nghiệp vụ:** Hoàn thiện định nghĩa đủ các luật nghiệp vụ được nhóm đề xuất (trong bản demo hiện tại thực thi R01–R10), thống nhất ngưỡng giữa Notebook, cấu hình và ứng dụng.
4. **Tăng tính giải thích:** Trình bày các nhân tố ảnh hưởng điểm AI, lý do bị từ chối/đề xuất xem xét; thiết lập cơ chế rà soát hồ sơ phức tạp bởi con người.
5. **Quản trị dữ liệu và bảo mật:** Tăng kiểm soát truy cập, sử dụng eKYC/CIC qua đối tác được phép, bảo vệ dữ liệu cá nhân, nhật ký đánh giá và giám sát hiệu quả hệ thống.

## G. Sửa lỗi thường gặp

| Dấu hiệu lỗi | Nguyên nhân thường gặp | Cách khắc phục |
|---|---|---|
| FileNotFoundError với `.joblib` / `.csv` | Upload thiếu file hoặc sai thư mục | Đảm bảo các file ở **cùng thư mục** với app.py |
| `_RemainderColsList` hoặc `SimpleImputer._fill_dtype` | Sai phiên bản scikit-learn | Dùng `scikit-learn==1.6.1`, Python 3.12; khởi động lại deployment |
| `No module named plotly` hoặc `sklearn` | Chưa có requirements hoặc requirements đặt sai vị trí | Kiểm tra file `requirements.txt` nằm ở root |
| Dashboard lỗi khi chạy biểu đồ | Code cũ dùng `kde=True` với Plotly | Upload `app.py` đã sửa trong bộ này |
| Màn hình 3 báo lỗi tiền xử lý | Đầu vào sai cột/thiếu feature hoặc phiên bản pipeline không tương thích | Dùng đúng `app.py`, `credit_engine.py` và 2 joblib đi cùng nhau |
| Mô hình trả lỗi khi Deploy | Môi trường Python khác môi trường training | Trong Advanced settings chọn Python 3.12 và pin thư viện |

**Lưu ý:** Ứng dụng này chưa được chạy thử trực tiếp trên Streamlit Community Cloud trong phiên làm việc hiện tại; chỉ triển khai trên tài khoản GitHub/Streamlit của nhóm mới kiểm chứng toàn bộ môi trường cloud.
