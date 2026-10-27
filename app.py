"""Streamlit UI for educational MoMo-like simulated credit scoring.

- Dashboard and existing records: historical synthetic CSV, not per-row model inference.
- New record: a real call to the supplied Home Credit sklearn model and a separate
  academic simulation of business rules (not a real credit decision).
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from credit_engine import (
    ROOT, load_artifacts, load_rule_config, numeric_medians,
    predict_risk, evaluate_credit,
)

st.set_page_config(
    page_title="Demo chấm điểm tín dụng | Nhóm Fintech",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data(show_spinner=False)
def get_simulated_data():
    return pd.read_csv(ROOT / "momo_loan_simulation_results.csv")

@st.cache_resource(show_spinner="Đang tải mô hình AI của nhóm...")
def get_ai_model():
    return load_artifacts(ROOT)

@st.cache_data(show_spinner=False)
def get_config():
    return load_rule_config(ROOT)


def show_decision(decision):
    if decision == "Đề xuất duyệt":
        st.success("🟢 " + decision)
    elif "Xem xét thêm" in decision:
        st.warning("🟡 " + decision)
    else:
        st.error("🔴 " + decision)


def make_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=float(score),
        number={"suffix": " / 100"},
        title={"text": "S_final – Điểm tín dụng tổng hợp"},
        gauge={"axis": {"range": [0, 100]},
               "bar": {"color": "#493596"},
               "steps": [
                   {"range": [0, 60], "color": "#f8dedf"},
                   {"range": [60, 80], "color": "#fff0cb"},
                   {"range": [80, 100], "color": "#d9f0e4"},
               ]}
    ))
    fig.update_layout(margin=dict(l=15, r=15, t=45, b=5), height=265)
    return fig


st.title("📊 Demo hệ thống chấm điểm tín dụng và cho vay nhanh")
st.caption("Bài tập lớn Công nghệ dịch vụ tài chính • Học viện Ngân hàng")
st.info(
    "**Ứng dụng nghiên cứu, mô phỏng theo bối cảnh ví MoMo; không thuộc MoMo và không kết nối MoMo/CIC thật.** "
    "Mô hình AI được nhóm huấn luyện trên dữ liệu Home Credit, không được xác thực để xét duyệt khoản vay thực tế."
)

st.sidebar.header("🧭 Phân hệ demo")
mode = st.sidebar.radio("Chọn chức năng", [
    "1. Dashboard 2.000 hồ sơ",
    "2. Tra cứu hồ sơ đã mô phỏng",
    "3. Chấm điểm khách hàng mới (AI thật)",
])
st.sidebar.divider()
st.sidebar.caption(
    "Mục tiêu: minh họa quy trình AI + bộ quy tắc nghiệp vụ; "
    "không tạo quyết định cấp tín dụng trong thực tế."
)

if mode == "1. Dashboard 2.000 hồ sơ":
    st.header("1. Tổng quan kết quả trên tập hồ sơ mô phỏng")
    st.warning(
        "**Nguồn dữ liệu lịch sử:** Notebook đã sinh 2.000 hồ sơ giả lập và gán cho mỗi hồ sơ "
        "một xác suất rủi ro lấy ngẫu nhiên từ phân bố dự đoán trên tập kiểm thử Home Credit. "
        "Các xác suất này KHÔNG phải dự đoán AI riêng cho từng hồ sơ MoMo. "
        "Dashboard được hiển thị nguyên trạng theo CSV nhóm đã cung cấp."
    )
    try:
        df = get_simulated_data()
    except Exception as exc:
        st.error(f"Không mở được file dữ liệu: {exc}")
        st.stop()
    n = len(df)
    counts = df["Decision"].value_counts()
    n_ok = int(counts.get("Đề xuất duyệt", 0))
    n_refuse = int(counts.get("Đề xuất từ chối theo quy tắc mô phỏng", 0))
    n_review = n - n_ok - n_refuse
    a, b, c, d = st.columns(4)
    a.metric("Tổng hồ sơ mô phỏng", f"{n:,}")
    b.metric("Đề xuất duyệt", f"{n_ok:,}", f"{n_ok/n:.1%}")
    c.metric("Xem xét thêm", f"{n_review:,}", f"{n_review/n:.1%}")
    d.metric("Đề xuất từ chối", f"{n_refuse:,}", f"{n_refuse/n:.1%}")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(
            df, names="Decision", title="Phân bổ kết quả mô phỏng", hole=0.35,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_layout(legend=dict(orientation="h", y=-0.15), margin=dict(l=10, r=10, t=45, b=60))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.histogram(df, x="S_final", nbins=26,
                           title="Phân phối điểm tổng hợp S_final")
        fig.update_layout(xaxis_title="Điểm S_final", yaxis_title="Số hồ sơ")
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Danh sách hồ sơ mô phỏng")
    view_cols = ["momo_customer_id", "age_sim", "monthly_income_sim", "DTI", "AI_p_risk", "S_rule", "S_AI", "S_final", "Decision"]
    st.dataframe(df[view_cols], use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Tải bảng kết quả mô phỏng", df.to_csv(index=False).encode("utf-8-sig"),
        file_name="momo_loan_simulation_results.csv", mime="text/csv",
    )

elif mode == "2. Tra cứu hồ sơ đã mô phỏng":
    st.header("2. Tra cứu kết quả mô phỏng đã lưu")
    st.caption("Đây là kết quả lưu trong tệp CSV, không chạy lại mô hình AI ở trang này.")
    try:
        df = get_simulated_data()
    except Exception as exc:
        st.error(f"Không mở được file dữ liệu: {exc}")
        st.stop()
    cust_id = st.selectbox("Chọn mã hồ sơ giả lập", df["momo_customer_id"].tolist())
    row = df.loc[df["momo_customer_id"] == cust_id].iloc[0]
    l, r = st.columns([1.1, 1])
    with l:
        st.subheader("Thông tin hồ sơ")
        details = pd.DataFrame([
            ["Tuổi", f"{int(row['age_sim'])}"],
            ["eKYC", "Đã xác minh" if row["ekyc_verified_sim"] else "Chưa xác minh"],
            ["Khớp định danh", "Khớp" if row["identity_match_sim"] else "Không khớp"],
            ["CIC", row["cic_group_sim"]],
            ["Thu nhập/tháng (VNĐ)", f"{row['monthly_income_sim']:,.0f}"],
            ["Tổng trả nợ/tháng (VNĐ)", f"{row['current_monthly_debt_sim'] + row['proposed_monthly_installment_sim']:,.0f}"],
            ["DTI", f"{row['DTI']:.1%}"],
            ["Giao dịch ví/tháng", f"{int(row['monthly_txn_count_sim'])}"],
        ], columns=["Trường", "Giá trị"])
        st.dataframe(details, hide_index=True, use_container_width=True)
    with r:
        st.subheader("Kết quả ghi nhận trước đó")
        show_decision(str(row["Decision"]))
        st.write("**Giải thích:**", row["Reason"])
        st.plotly_chart(make_gauge(row["S_final"]), use_container_width=True)
        x, y, z = st.columns(3)
        x.metric("S_rule", f"{row['S_rule']:.1f}")
        y.metric("S_AI", f"{row['S_AI']:.1f}")
        z.metric("P_risk đã lấy mẫu", f"{row['AI_p_risk']:.1%}")
    st.warning(
        "P_risk trong tệp CSV được chọn ngẫu nhiên từ các dự đoán trên tập test Home Credit; "
        "không được diễn giải là xác suất vỡ nợ được AI đánh giá riêng cho khách hàng đang tra cứu."
    )

else:
    st.header("3. Chấm điểm hồ sơ mới với mô hình AI thực")
    st.write(
        "Trang này **gọi mô hình Logistic Regression thật** từ `best_credit_model.joblib`, "
        "sử dụng `preprocessor_pipeline.joblib` trước khi kết hợp bộ quy tắc quyết định."
    )
    st.warning(
        "**Hai nhóm đơn vị dữ liệu:** Các quy tắc nghiệp vụ sử dụng số tiền giả lập bằng VNĐ; "
        "mô hình AI sử dụng đơn vị tiền tệ gốc của bộ dữ liệu Home Credit. "
        "Chúng ta nhập riêng các đại lượng Home Credit, KHÔNG quy đổi tùy tiện từ VNĐ. "
        "Kết quả chỉ là minh họa kỹ thuật, không phải xác suất rủi ro đã được hiệu chỉnh cho khách hàng MoMo."
    )
    try:
        pipeline, model = get_ai_model()
        medians = numeric_medians(pipeline)
        config = get_config()
    except Exception as exc:
        st.error("**Chưa tải được mô hình AI. Không hiển thị xác suất giả.**")
        st.exception(exc)
        st.code("scikit-learn==1.6.1", language="text")
        st.caption("Kiểm tra lại 2 file .joblib và phiên bản trong requirements.txt.")
        st.stop()

    case = st.selectbox("🎭 Chọn tình huống để trình diễn", [
        "TC01 – Hồ sơ đáp ứng điều kiện",
        "TC02 – Nợ xấu CIC Nhóm 4",
        "TC03 – DTI trên 50%",
        "TC04 – Thiếu xác minh eKYC",
        "TC05 – Đối tác đang chờ xác minh",
    ])
    scenario = {
        "TC01 – Hồ sơ đáp ứng điều kiện": {"cic": "Nhóm 1", "income": 20_000_000, "debt": 1_000_000, "inst": 1_000_000, "ekyc": True, "partner": "eligible"},
        "TC02 – Nợ xấu CIC Nhóm 4": {"cic": "Nhóm 4", "income": 20_000_000, "debt": 1_000_000, "inst": 1_000_000, "ekyc": True, "partner": "eligible"},
        "TC03 – DTI trên 50%": {"cic": "Nhóm 1", "income": 12_000_000, "debt": 8_000_000, "inst": 2_000_000, "ekyc": True, "partner": "eligible"},
        "TC04 – Thiếu xác minh eKYC": {"cic": "Nhóm 1", "income": 20_000_000, "debt": 1_000_000, "inst": 1_000_000, "ekyc": False, "partner": "eligible"},
        "TC05 – Đối tác đang chờ xác minh": {"cic": "Nhóm 1", "income": 20_000_000, "debt": 1_000_000, "inst": 1_000_000, "ekyc": True, "partner": "pending"},
    }[case]

    with st.form("new_credit_form"):
        st.subheader("A. Hồ sơ giả lập cho quy tắc nghiệp vụ (VNĐ)")
        left, right = st.columns(2)
        with left:
            age = st.slider("Tuổi", 16, 65, 27)
            ekyc = st.checkbox("Đã hoàn thành eKYC", value=scenario["ekyc"])
            id_match = st.checkbox("Thông tin định danh trùng khớp", value=True)
            mandatory = st.checkbox("Đầy đủ hồ sơ bắt buộc", value=True)
            partner = st.selectbox("Trạng thái đối tác", ["eligible", "pending", "ineligible", "unknown"],
                                   index=["eligible", "pending", "ineligible", "unknown"].index(scenario["partner"]))
            cic = st.selectbox("Nhóm nợ CIC (giả lập)", ["Nhóm 1", "Nhóm 2", "Nhóm 3", "Nhóm 4", "Nhóm 5", "Không có lịch sử"],
                               index=["Nhóm 1", "Nhóm 2", "Nhóm 3", "Nhóm 4", "Nhóm 5", "Không có lịch sử"].index(scenario["cic"]))
            days_past_due = st.selectbox("Số ngày từng quá hạn", [0, 5, 15, 45, 90])
        with right:
            income = st.number_input("Thu nhập/tháng (VNĐ)", min_value=100_000, max_value=200_000_000,
                                     value=scenario["income"], step=500_000)
            debt = st.number_input("Khoản trả nợ hiện tại/tháng (VNĐ)", min_value=0,
                                   max_value=150_000_000, value=scenario["debt"], step=500_000)
            installment = st.number_input("Khoản trả góp dự kiến/tháng (VNĐ)", min_value=0,
                                          max_value=150_000_000, value=scenario["inst"], step=500_000)
            repayment = st.slider("Điểm lịch sử trả nợ giả lập", 0, 100, 90)
            wallet_known = st.checkbox("Có dữ liệu ví", value=True)
            wallet_txn = st.slider("Giao dịch ví/tháng", 0, 120, 25)

        st.divider()
        st.subheader("B. Đặc trưng đầu vào của AI (đơn vị dữ liệu Home Credit)")
        st.caption(
            "Mô hình huấn luyện trên dữ liệu Home Credit, có mức tiền và cách mã hóa riêng. "
            "Các giá trị mặc định dưới đây lấy từ trung vị dữ liệu TRAIN đã lưu trong pipeline."
        )
        x, y, z = st.columns(3)
        ai_income = x.number_input("AMT_INCOME_TOTAL", min_value=0.0,
                                   value=round(medians["AMT_INCOME_TOTAL"], 2), step=10000.0)
        ai_credit = y.number_input("AMT_CREDIT", min_value=0.0,
                                   value=round(medians["AMT_CREDIT"], 2), step=10000.0)
        ai_annuity = z.number_input("AMT_ANNUITY", min_value=0.0,
                                    value=round(medians["AMT_ANNUITY"], 2), step=1000.0)
        with st.expander("Tùy chỉnh đặc trưng Home Credit nâng cao (không bắt buộc)"):
            st.caption("Các trường không có dữ liệu sẽ dùng giá trị impute đã học trên tập Train.")
            t1, t2, t3 = st.columns(3)
            employment_years = t1.number_input("Số năm làm việc", min_value=0.0, max_value=45.0, value=5.0, step=0.5)
            children = t2.number_input("CNT_CHILDREN", min_value=0, max_value=15, value=0)
            gender = t3.selectbox("CODE_GENDER (không bắt buộc)", ["Không cung cấp", "F", "M"])
            own_car = st.checkbox("FLAG_OWN_CAR = Y", value=False)
            own_realty = st.checkbox("FLAG_OWN_REALTY = Y", value=True)
            user_ext = st.checkbox("Tự nhập ba chỉ số EXT_SOURCE (nếu có)", value=False)
            if user_ext:
                ec1, ec2, ec3 = st.columns(3)
                ext1 = ec1.slider("EXT_SOURCE_1", 0.0, 1.0, 0.50, 0.01)
                ext2 = ec2.slider("EXT_SOURCE_2", 0.0, 1.0, 0.50, 0.01)
                ext3 = ec3.slider("EXT_SOURCE_3", 0.0, 1.0, 0.50, 0.01)
            else:
                ext1 = ext2 = ext3 = np.nan
        submitted = st.form_submit_button("⚡ Chạy mô hình AI và đánh giá tín dụng", type="primary", use_container_width=True)

    if submitted:
        ai_form = {
            "age": age, "children": children, "employment_years": employment_years,
            "code_gender": np.nan if gender == "Không cung cấp" else gender,
            "own_car": own_car, "own_realty": own_realty,
            "ai_income": ai_income, "ai_credit": ai_credit, "ai_annuity": ai_annuity,
            "ext_source_1": ext1, "ext_source_2": ext2, "ext_source_3": ext3,
        }
        business_row = {
            "age_sim": age,
            "ekyc_verified_sim": int(ekyc),
            "identity_match_sim": int(id_match),
            "mandatory_data_complete_sim": int(mandatory),
            "partner_eligibility_sim": partner,
            "cic_group_sim": cic,
            "days_past_due_sim": days_past_due,
            "monthly_income_sim": float(income),
            "current_monthly_debt_sim": float(debt),
            "proposed_monthly_installment_sim": float(installment),
            "repayment_history_score_sim": repayment,
            "wallet_data_available_sim": int(wallet_known),
            "monthly_txn_count_sim": wallet_txn,
        }
        try:
            p_risk, ai_payload = predict_risk(pipeline, model, ai_form)
            result = evaluate_credit(business_row, p_risk, config)
        except Exception as exc:
            st.error("Không thể chấm điểm: mô hình AI hoặc dữ liệu đầu vào gặp lỗi. Không dùng điểm giả.")
            st.exception(exc)
            st.stop()
        st.divider()
        st.subheader("Kết quả hệ thống (minh họa, không phải phê duyệt thực)")
        show_decision(result["Decision"])
        st.write("**Lý do:**", result["Reason"])
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("P_risk từ mô hình Home Credit", f"{p_risk:.2%}")
        m2.metric("Điểm S_rule", f"{result['S_rule']:.1f} / 100")
        m3.metric("Điểm S_AI", f"{result['S_AI']:.1f} / 100")
        m4.metric("Điểm S_final", f"{result['S_final']:.1f} / 100")
        l, r = st.columns([1, 1])
        with l:
            st.plotly_chart(make_gauge(result["S_final"]), use_container_width=True)
            st.metric("DTI", f"{result['DTI']:.1%}", result["DTI_Status"], delta_color="off")
        with r:
            with st.expander("🧾 Chi tiết các quy tắc", expanded=True):
                for group_name, label in [
                    ("rejections", "Điều kiện loại trừ"),
                    ("manual_checks", "Cần bổ sung"),
                    ("warnings", "Cảnh báo"),
                ]:
                    st.markdown(f"**{label}: {len(result[group_name])}**")
                    for item in result[group_name]:
                        st.write("• " + item)
        with st.expander("🔬 Xem 22 đặc trưng Home Credit thực sự đưa vào pipeline"):
            display = ai_payload.T.reset_index()
            display.columns = ["Đặc trưng AI", "Giá trị đầu vào"]
            st.dataframe(display, hide_index=True, use_container_width=True)
        st.caption("S_final = 60% × S_rule + 40% × [100 × (1 - P_risk)]. Ngưỡng dùng từ rule_configuration.json.")
        st.warning("Đây là ví dụ minh họa giáo dục. Mô hình chưa được kiểm định/hiệu chỉnh trên dữ liệu thực của ví MoMo.")
