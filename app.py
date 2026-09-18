import streamlit as st
import pdfplumber
import google.generativeai as genai
import json

st.set_page_config(page_title="AI CV Analyzer Pro", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    .big-font { font-size:20px !important; font-weight: bold; color: #1E88E5;}
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Hệ Thống Đánh Giá CV Theo Vị Trí")

api_key = st.text_input("🔑 Nhập Google Gemini API Key:", type="password")

# 1. TẠO THƯ VIỆN CÁC VỊ TRÍ CÔNG VIỆC CÓ SẴN (Có thể chỉnh sửa/thêm mới tùy ý)
DANH_SACH_JD = {
    "Data Scientist / Machine Learning Engineer": '''
        - Thiết kế, huấn luyện và tối ưu các mô hình học máy (Linear Regression, Random Forest, XGBoost).
        - Phân tích dữ liệu lớn, trích xuất đặc trưng và đánh giá mức độ quan trọng của các biến.
        - Thành thạo Python (Jupyter, Pandas, Scikit-Learn) và xử lý dữ liệu với SQL Server / MySQL.
        - Ưu tiên ứng viên có kinh nghiệm triển khai thuật toán trên dữ liệu không gian, đồ thị hoặc hệ thống IoT.
    ''',
    "Computer Vision / AI Researcher": '''
        - Nghiên cứu và áp dụng các kiến trúc Deep Learning, đặc biệt là Convolutional Neural Networks (CNN), YOLO, MobileNetV2.
        - Xử lý các tập dữ liệu hình ảnh phức tạp (ví dụ: nhận diện vật thể, hình ảnh thực vật).
        - Có khả năng đọc hiểu tài liệu học thuật tiếng Anh, nắm vững kiến thức Đại số tuyến tính, Giải tích và Xác suất.
    ''',
    "Software Developer (Backend & Desktop App)": '''
        - Xây dựng phần mềm quản lý và hệ thống web thương mại điện tử bằng PHP (mô hình MVC) hoặc Java Swing.
        - Triển khai kiến trúc thiết kế chuẩn (như DAO pattern), kết nối ổn định với hệ quản trị cơ sở dữ liệu quan hệ.
        - Quản lý mã nguồn bằng Git/GitHub. Thành thạo môi trường Visual Studio Code, PyCharm.
    '''
}

col1, col2 = st.columns(2)
with col1:
    st.markdown('<p class="big-font">📄 1. Hồ sơ ứng viên (CV)</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Tải file PDF", type="pdf", label_visibility="collapsed")
    
with col2:
    st.markdown('<p class="big-font">🎯 2. Chọn vị trí ứng tuyển</p>', unsafe_allow_html=True)
    
    # 2. DÙNG SELECTBOX TẠO MENU CHỌN VỊ TRÍ
    vi_tri_chon = st.selectbox("Danh sách vị trí:", list(DANH_SACH_JD.keys()), label_visibility="collapsed")
    
    # 3. LẤY NỘI DUNG JD TƯƠNG ỨNG TỪ TỪ ĐIỂN
    jd_text = DANH_SACH_JD[vi_tri_chon]
    
    # Hiển thị nội dung JD bên dưới dạng bảng rút gọn để người dùng xem trước
    with st.expander(f"Xem yêu cầu chi tiết của vị trí {vi_tri_chon}", expanded=True):
        st.markdown(jd_text)

if st.button("🧠 Bắt đầu Phân Tích Chuyên Sâu", type="primary", use_container_width=True):
    if not api_key or not uploaded_file:
        st.warning("Vui lòng điền đủ API Key và tải CV lên.")
    else:
        with st.spinner(f"AI đang phân tích độ phù hợp cho vị trí {vi_tri_chon}..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3.6-flash')
                
                cv_text = ""
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        cv_text += page.extract_text() + "\n"
                        
                prompt = f"""
                Đóng vai một Tech Lead và Senior HR. Hãy phân tích cực kỳ chuyên sâu CV này dựa trên JD.
                Đặc biệt chú ý đến các Technical Stack, độ phức tạp của các dự án thực tế.
                Trả về ĐÚNG định dạng JSON sau (không chứa markdown ```json):
                {{
                    "ho_ten": "Tên",
                    "chuyen_nganh": "Ngành học",
                    "match_score": Điểm từ 0-100,
                    "tong_quan": "Nhận xét tổng quan",
                    "danh_gia_ky_thuat": ["Phân tích sâu 1", "Phân tích 2"],
                    "danh_gia_du_an": ["Đánh giá dự án 1", "Đánh giá 2"],
                    "diem_manh": ["Điểm mạnh 1", "Điểm mạnh 2"],
                    "loi_khuyen_nang_cap": ["Lời khuyên 1", "Lời khuyên 2"]
                }}
                YÊU CẦU CÔNG VIỆC CHO VỊ TRÍ {vi_tri_chon}:\n{jd_text}\n
                NỘI DUNG CV:\n{cv_text}
                """
                
                response = model.generate_content(prompt)
                json_str = response.text.replace('```json', '').replace('```', '').strip()
                data = json.loads(json_str)
                
                st.divider()
                st.header(f"👤 Ứng viên: {data.get('ho_ten', 'Không xác định')} - 🎯 Ứng tuyển: {vi_tri_chon}")
                
                score = data.get('match_score', 0)
                st.metric(label="Độ phù hợp tổng thể (Match Score)", value=f"{score}/100")
                st.progress(score / 100)
                st.info(f"**Đánh giá tổng quan:** {data.get('tong_quan', '')}")
                
                tab1, tab2, tab3, tab4 = st.tabs(["💻 Phân tích Kỹ thuật", "🚀 Đánh giá Dự án", "⚖️ Ưu / Nhược điểm", "💡 Lời khuyên bứt phá"])
                
                with tab1:
                    for item in data.get('danh_gia_ky_thuat', []): st.markdown(f"- 🔹 {item}")
                with tab2:
                    for item in data.get('danh_gia_du_an', []): st.markdown(f"- 📦 {item}")
                with tab3:
                    col_pro, col_con = st.columns(2)
                    with col_pro:
                        st.success("**Điểm mạnh:**")
                        for item in data.get('diem_manh', []): st.markdown(f"- ✅ {item}")
                    with col_con:
                        st.error("**Điểm yếu:**")
                        st.markdown("- ⚠️ Cần xem xét thêm ở phần Lời khuyên.")
                with tab4:
                    for item in data.get('loi_khuyen_nang_cap', []): st.markdown(f"- 🎯 {item}")

            except Exception as e:
                st.error(f"Lỗi hệ thống: {e}")