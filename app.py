import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta, time
from streamlit_gsheets import GSheetsConnection

# ==================== 1. 頁面配置與木質調風格 ====================
st.set_page_config(page_title="癒室 - 手工甜點", layout="wide", page_icon="🥐")

st.markdown("""
    <style>
    .main { background-color: #F5E6D3; }
    .stButton>button { 
        background-color: #8B7355; color: white; width: 100%; border-radius: 8px; 
        height: 3.5em; font-weight: bold; border: none; font-size: 1.1em;
    }
    .stButton>button:hover { background-color: #5D4E37; border: 1px solid #C4A574; }
    .announcement-box {
        background-color: #FFF8E7; border: 2px solid #C4A574; padding: 1.5rem;
        border-radius: 12px; color: #5D4E37; margin-bottom: 2rem;
    }
    .submit-reminder { 
        background: #FFEBEE; border-left: 5px solid #E53935; padding: 1rem; 
        border-radius: 4px; color: #C62828; font-weight: 500; margin: 15px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== 2. 初始化雲端連線 ====================
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db_data():
    try:
        return conn.read(worksheet="癒室訂單紀錄", ttl=0)
    except:
        return pd.DataFrame(columns=["下單時間", "客戶姓名", "聯絡電話", "面交日期", "面交地點", "面交時間", "經典數量", "核桃數量", "總金額", "付款方式", "付款資訊"])

# ==================== 3. 側邊欄：主理人後台 (密碼鎖) ====================
with st.sidebar:
    st.header("🍂 癒室 管理中心")
    admin_key = st.text_input("輸入管理密碼", type="password")
    
    if admin_key == "0512":
        st.success("主理人驗證成功")
        st.markdown("---")
        ratio_choice = st.radio("今日生產配比", ["均衡生產 (各 9 盒)", "經典為主 (12/6)", "核桃為主 (6/12)"])
        ratios = {"均衡生產 (各 9 盒)": (9, 9), "經典為主 (12/6)": (12, 6), "核桃為主 (6/12)": (6, 12)}
        max_g, max_w = ratios[ratio_choice]
        
        st.subheader("📅 2月接單日期設定")
        date_input = st.text_area("輸入製作日期 (YYYY-MM-DD)", "2026-02-07\n2026-02-12\n2026-02-13")
        prod_dates = [d.strip() for d in date_input.split('\n') if d.strip()]
        st.session_state['admin_config'] = {"max_g": max_g, "max_w": max_w, "prod_dates": prod_dates}
    else:
        st.info("💡 主理人專用後台")
        config = st.session_state.get('admin_config', {"max_g": 9, "max_w": 9, "prod_dates": ["2026-02-07", "2026-02-12", "2026-02-13"]})
        max_g, max_w, prod_dates = config['max_g'], config['max_w'], config['prod_dates']

# ==================== 4. 主頁面：公告欄與下單流程 ====================
st.title("🍂 癒室 - 手工甜點")
st.markdown("**Healing Room Handmade · 2026 二月特別專場**")

# --- 2月接單公告區 ---
st.markdown(f"""
<div class="announcement-box">
    <h3 style="margin-top:0;">📢 癒室 2月接單公告</h3>
    <p>親愛的朋友，癒室 2 月僅開放以下三梯次接單，請留意各場次時間限制：</p>
    <ul>
        <li><b>2/07 梯次：</b>製作當晚 (2/7) <b>三重自取</b> (19:00後)；隔日 (2/8) <b>華視面交</b> (11:00-17:00)。</li>
        <li><b>2/12 梯次：</b>僅開放 <b>三重自取</b> (19:00後)，無華視面交。</li>
        <li><b>2/13 梯次：</b>僅開放 <b>三重自取</b> (19:00後)，無華視面交。</li>
    </ul>
    <small>※ 2/12、2/13 因主理人行程調整，僅提供三重自取，敬請見諒。</small>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📝 1. 訂購人資訊")
    c_name = st.text_input("客戶姓名", placeholder="如何稱呼您")
    c_phone = st.text_input("聯絡電話", placeholder="您的手機號碼")
    
    st.markdown("### 📍 2. 選擇面交梯次")
    target_date = st.selectbox("請選擇預計製作的日期", prod_dates)
    
    # 根據日期顯示不同地點選項
    pickup_options = []
    if target_date == "2026-02-07":
        pickup_options = ["2026-02-07 三重彰化銀行 (19:00後)", "2026-02-08 華視大樓 (11:00-17:00)"]
    else:
        pickup_options = [f"{target_date} 三重彰化銀行 (19:00後)"]
    
    loc_opt = st.selectbox("地點與規範", pickup_options)
    
    # 時間邏輯檢查
    is_huashi = "華視" in loc_opt
    default_t = time(12, 0) if is_huashi else time(19, 0)
    p_time = st.time_input("預計面交時間", value=default_t)
    
    time_ok = True
    if is_huashi:
        if p_time < time(11, 0) or p_time > time(17, 0):
            st.warning("⚠️ 提醒：2/8 華視面交僅開放 11:00 - 17:00"); time_ok = False
    else:
        if p_time < time(19, 0):
            st.warning("⚠️ 提醒：三重自取僅限 19:00 以後"); time_ok = False

with col2:
    st.markdown("### 🥐 3. 數量選擇 ($190/盒)")
    q_g = st.number_input("經典蘭姆葡萄核桃 (盒)", min_value=0, max_value=max_g, step=1)
    q_w = st.number_input("純核桃焦糖 (盒)", min_value=0, max_value=max_w, step=1)
    
    total_price = (q_g + q_w) * 190
    st.markdown(f"#### 💰 訂單總額：NT$ {total_price}")
    
    st.markdown("### 💳 4. 支付管道")
    pay_method = st.radio("付款方式", ["面交支付", "銀行轉帳", "Line Pay"], horizontal=True)
    pay_info = st.text_input("後五碼 / Line Pay 名稱") if pay_method != "面交支付" else "現場支付"

# ==================== 5. 存檔與同步 ====================
st.divider()
can_submit = True
errs = []

if not (c_name and c_phone): can_submit = False; errs.append("請填寫姓名與電話")
if (q_g + q_w) == 0: can_submit = False; errs.append("請至少訂購一盒")
if not time_ok: can_submit = False; errs.append("時間不符規範")

if not can_submit:
    st.markdown(f'<div class="submit-reminder">⚠️ 尚未完成：{" · ".join(errs)}</div>', unsafe_allow_html=True)
    st.button("確認送出訂單", disabled=True)
else:
    if st.button("🚀 確認送出訂單 (將同步至雲端表格)"):
        with st.spinner("訂單飛向雲端中..."):
            new_row = pd.DataFrame([{
                "下單時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "客戶姓名": c_name, "聯絡電話": c_phone,
                "面交日期": loc_opt.split(' ')[0],
                "面交地點": "三重" if "三重" in loc_opt else "華視",
                "面交時間": p_time.strftime("%H:%M"),
                "經典數量": q_g, "核桃數量": q_w, "總金額": total_price,
                "付款方式": pay_method, "付款資訊": pay_info
            }])
            # 同步至 Google Sheets
            existing_df = get_db_data()
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            conn.update(worksheet="癒室訂單紀錄", data=updated_df)
            
            st.balloons()
            st.success("✅ 訂單成立！感謝您對「癒室」的支持。")
            st.info(f"🔮 今日能量指引：{random.choice(['太陽：光芒照亮前路', '星星：願望如期而至', '世界：完美的平衡與圓滿'])}")