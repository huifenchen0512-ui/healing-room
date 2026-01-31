import streamlit as st
import random
from datetime import date, datetime, timedelta, time

# === 基礎設定與 CSS (保持你的木質調與癒室品牌) ===
st.set_page_config(page_title="癒室 - 手工甜點", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fdf5e6; }
    .stButton>button { background-color: #8b4513; color: white; width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    .submit-reminder { background: #FFEBEE; border-left: 4px solid #E53935; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 10px 0; color: #C62828; }
    </style>
    """, unsafe_allow_html=True)

# === 初始化狀態 ===
if "orders" not in st.session_state: st.session_state.orders = []

# === 側邊欄：主理人管理 (你的創業地基) ===
with st.sidebar:
    st.header("🍂 癒室 後台設定")
    # 產能設定
    ratio_choice = st.radio("選擇今日配比 (上限 18 盒)", ["均衡生產 (各 9 盒)", "經典為主 (葡萄 12 / 核桃 6)", "核桃為主 (葡萄 6 / 核桃 12)"])
    ratios = {"均衡生產 (各 9 盒)": (9, 9), "經典為主 (葡萄 12 / 核桃 6)": (12, 6), "核桃為主 (葡萄 6 / 核桃 12)": (6, 12)}
    max_g, max_w = ratios[ratio_choice]
    
    # 日期設定 (你珍貴的休假日)
    date_input = st.text_area("輸入製作日期 (YYYY-MM-DD)", "2026-02-10\n2026-02-17")
    prod_dates = [d.strip() for d in date_input.split('\n') if d.strip()]

# === 主頁面 ===
st.title("🥐 癒室 - 手工甜點")
st.info("📦 每盒兩顆入，均一價 $190")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 1. 填寫資料")
    c_name = st.text_input("客戶姓名")
    c_phone = st.text_input("聯絡電話")
    
    st.markdown("### 2. 面交資訊")
    base_date = st.selectbox("選擇製作梯次", prod_dates) if prod_dates else None
    if base_date:
        d0 = base_date
        d1 = (datetime.strptime(d0, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        loc_opt = st.selectbox("地點與日期", [f"{d0} 三重彰化銀行 (19:00後)", f"{d1} 華視大樓 (11:00-19:00)"])
        p_time = st.time_input("面交時間", value=time(19, 0) if "三重" in loc_opt else time(12, 0))
        
        # 時間檢查
        time_ok = True
        if "三重" in loc_opt and p_time.hour < 19:
            st.warning("⚠️ 三重僅限 19:00 後"); time_ok = False
        elif "華視" in loc_opt and (p_time.hour < 11 or p_time.hour >= 19):
            st.warning("⚠️ 華視僅限 11:00-19:00"); time_ok = False

with col2:
    st.markdown("### 3. 選擇數量")
    q_g = st.number_input("經典蘭姆葡萄 (盒)", min_value=0, max_value=max_g, step=1)
    q_w = st.number_input("純核桃焦糖 (盒)", min_value=0, max_value=max_w, step=1)
    st.write(f"💰 總金額：${(q_g + q_w) * 190}")
    
    st.markdown("### 4. 付款方式")
    pay = st.radio("付款方式", ["面交", "轉帳", "Line Pay"], horizontal=True)
    pay_info = st.text_input("後五碼 / Line Pay 名稱") if pay != "面交" else "面交支付"

# === 送出邏輯 (即時檢查，不再卡死) ===
st.divider()
can_submit = True
errors = []

if not (c_name and c_phone): 
    can_submit = False; errors.append("請填寫姓名與電話")
if (q_g + q_w) == 0: 
    can_submit = False; errors.append("請選擇數量")
if not (pay == "面交" or pay_info): 
    can_submit = False; errors.append("請填寫付款資訊")
if base_date and not time_ok:
    can_submit = False; errors.append("面交時間不符")

if not can_submit:
    st.markdown(f'<div class="submit-reminder">⚠️ {" · ".join(errors)}</div>', unsafe_allow_html=True)
    st.button("送出訂單", disabled=True)
else:
    if st.button("✅ 確認送出訂單"):
        st.balloons()
        st.success(f"訂單成立！感謝支持癒室。")
        # 2026 塔羅指引
        st.markdown("### 🔮 癒室今日能量指引")
        msg = random.choice(["太陽：充滿溫暖與希望", "星星：靈感湧現的一天", "世界：美好的圓滿循環"])
        st.info(f"今日能量：{msg}")
# === 老闆專屬：隱藏訂單看版 (僅供測試用) ===
st.divider()
with st.expander("🔐 老闆後台：查看目前所有訂單 (網頁重整後會消失)"):
    if st.session_state.orders:
        for i, order in enumerate(st.session_state.orders):
            st.write(f"**訂單 #{i+1}**")
            st.json(order) # 用 JSON 格式顯示所有欄位，最清楚
    else:
        st.write("目前尚未收到任何訂單。")