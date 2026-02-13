#!/usr/bin/env python
# coding: utf-8
# %%
import streamlit as st
import pandas as pd
import os

# HEADER
st.set_page_config(page_title="Enterprise HealthScore", layout="wide")

# HÀM MÀU SẮC HIỂN THỊ THEO HẠNG
def get_rating_color(rating):
    colors = {
        'AAA': '#1B5E20', 'AA': '#43A047', 'A': '#A5D6A7',
        'B': '#FFF3B0', 'C': '#FFB74D', 'D': '#E57373'
    }
    return colors.get(str(rating).upper(), '#1e3a8a')

# THANH ĐIỂM
def get_visual_position(score):
    # Ánh xạ điểm số thực tế vào 6 khoảng bằng nhau (mỗi khoảng 16.66%)
    if score <= 35: # Khoảng D
        return (score / 35) * 16.66
    elif score <= 50: # Khoảng C
        return 16.66 + ((score - 35) / 15) * 16.66
    elif score <= 65: # Khoảng B
        return 33.32 + ((score - 50) / 15) * 16.66
    elif score <= 75: # Khoảng A
        return 49.98 + ((score - 65) / 10) * 16.66
    elif score <= 85: # Khoảng AA
        return 66.64 + ((score - 75) / 10) * 16.66
    else: # Khoảng AAA
        return 83.30 + ((score - 85) / 15) * 16.70

#CUSTOM CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main-header {
    color: #1e3a8a;
    font-weight: 700;
    padding-bottom: 15px;
    border-bottom: 2px solid #f1f5f9;
    margin-bottom: 25px;
}
.metric-card {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 24px;
    border-radius: 16px;
    text-align: center;
}
.gauge-wrapper {
    position: relative;
    padding: 45px 0 30px 0;
    margin: 20px 0;
}
.gauge-bar {
    display: flex;
    height: 16px;
    border-radius: 8px;
    overflow: hidden;
    background-color: #f1f5f9;
}
.gauge-segment { height: 100%; width: 16.66%; }

.gauge-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 12px;
}
.gauge-label-item {
    font-size: 0.75rem;
    font-weight: 800;
    color: #64748b;
    width: 16.66%;
    text-align: center;
}
.gauge-pointer {
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: left 1s ease-in-out;
}
.gauge-bubble {
    color: white;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.95rem;
    font-weight: 800;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.gauge-arrow {
    width: 0; height: 0;
    border-left: 6px solid transparent; border-right: 6px solid transparent;
    border-top: 8px solid; margin-top: -1px;
}
</style>
""", unsafe_allow_html=True)

# DỮ LIỆU
FILE_PATH = "scored_data_423501.xlsx"
LOGO_PATH = os.path.join("images", "1.png")

# Mapping đặc điểm cụm
CLUSTER_MAP = {
    4: "Sinh lời cao, nợ thấp, thanh khoản tốt",
    2: "Vòng quay vốn nhanh, hiệu suất cao",
    3: "Thừa tiền mặt, ít nợ, tăng trưởng chậm",
    5: "Đòn bẩy cao, sinh lời trung bình",
    0: "Tăng trưởng âm, sinh lời yếu",
    1: "Thua lỗ, mất khả năng thanh toán"
}

@st.cache_data
def load_data():
    if os.path.exists(FILE_PATH):
        try:
            return pd.read_excel(FILE_PATH)
        except:
            return None
    return None

df = load_data()
if df is None:
    st.error("Không tìm thấy file dữ liệu.")
    st.stop()

# SIDEBAR
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    st.markdown("TÌM KIẾM MÃ DOANH NGHIỆP")
    selected_ma = st.selectbox("Mã doanh nghiệp", sorted(df['MÃ'].unique()))
    st.markdown("---")
    st.caption("Enterprise HealthScore System v2.6")

# Xử lý dữ liệu
company_data = df[df['MÃ'] == selected_ma].sort_values('NĂM')
latest_data = company_data.iloc[-1]
score = int(round(latest_data['CREDIT_SCORE']))
rating = str(latest_data['RATING']).upper()
rating_color = get_rating_color(rating)
visual_pos = get_visual_position(score)

# Lấy đặc điểm cụm
cluster_val = latest_data.get('CLUSTER_CLASS')
cluster_desc = CLUSTER_MAP.get(cluster_val, "Chưa xác định đặc điểm nhóm")

# --- 6. GIAO DIỆN CHÍNH ---
st.markdown("<h1 style='font-size: 60px;'>ENTERPRISE HEALTHSCORE</h1>", unsafe_allow_html=True)
st.markdown(f"#### {latest_data['TÊN CÔNG TY']} | {selected_ma}")

c1, c2, c3 = st.columns([1, 1, 2.2])
with c1: 
    st.metric("Điểm tín dụng", f"{score}/100")
with c2: 
    st.metric("Xếp hạng", rating)
with c3: 
    st.write("**Sức khỏe tài chính:**")
    st.info(cluster_desc)

#GIAO DIỆN CHÍNH HIỂN THỊ ĐIỂM
colors = ["#E57373", "#FFB74D", "#FFF3B0", "#A5D6A7", "#43A047", "#1B5E20"]
segments_html = "".join([f'<div style="background-color:{c};flex:1;height:100%;"></div>' for c in colors])
gauge_html = f"""
<div class="gauge-wrapper" style="position:relative; padding:45px 0 30px 0; margin:20px 0;">
    <div class="gauge-pointer" style="position:absolute; top:0; left:{visual_pos}%; transform:translateX(-50%); display:flex; flex-direction:column; align-items:center; transition:left 1s ease-in-out; z-index:10;">
        <div class="gauge-bubble" style="background-color:{rating_color}; color:white; padding:4px 14px; border-radius:20px; font-size:0.95rem; font-weight:800; white-space:nowrap; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
            {score} điểm
        </div>
        <div class="gauge-arrow" style="width:0; height:0; border-left:6px solid transparent; border-right:6px solid transparent; border-top:8px solid {rating_color}; margin-top:-1px;"></div>
    </div>
    <div class="gauge-bar" style="display:flex; height:16px; border-radius:8px; overflow:hidden; background-color:#f1f5f9; box-shadow:inset 0 2px 5px rgba(0,0,0,0.2);">
        {segments_html}
    </div>
    <div class="gauge-labels" style="display:flex; justify-content:space-between; margin-top:12px;">
        <div style="width:16.66%; text-align:center; font-size:0.75rem; font-weight:800; color:#64748b;">D</div>
        <div style="width:16.66%; text-align:center; font-size:0.75rem; font-weight:800; color:#64748b;">C</div>
        <div style="width:16.66%; text-align:center; font-size:0.75rem; font-weight:800; color:#64748b;">B</div>
        <div style="width:16.66%; text-align:center; font-size:0.75rem; font-weight:800; color:#64748b;">A</div>
        <div style="width:16.66%; text-align:center; font-size:0.75rem; font-weight:800; color:#64748b;">AA</div>
        <div style="width:16.66%; text-align:center; font-size:0.75rem; font-weight:800; color:#64748b;">AAA</div>
    </div>
</div>
"""

st.markdown(gauge_html, unsafe_allow_html=True)

# Bảng dữ liệu chi tiết
st.markdown("<br> CHI TIẾT CHỈ SỐ TÀI CHÍNH", unsafe_allow_html=True)
financial_vars = [
    'QUICK_RATIO', 'CURRENT_RATIO', 'NO NH/VCSH', 'NO NH/TTS', 
    'TONG NO/VCSH', 'TONG NO/TTS', 'NO DH/VCSH', 'NO DH/TTS', 
    'ROA', 'VONG QUAY TTS', 'VONG QUAY KPT', 'VONG QUAY VCSH', 
    'TANG TRUONG DT', 'EBIT MARGIN', 'DIVIDEND/OCF'
]
display_df = company_data[['NĂM'] + financial_vars].copy()
st.dataframe(display_df.set_index('NĂM'), use_container_width=True)

st.markdown("---")
st.caption("Dữ liệu được trích xuất phục vụ mục đích phân tích tín dụng nội bộ.")

# %%

# %%

# %%

# %%

