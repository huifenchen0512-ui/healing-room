import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta, time
from streamlit_gsheets import GSheetsConnection

# ==================== 1. 基礎設定與木質調 CSS ====================
st.set_page_config(page_title="癒室 - 手工甜點", layout="wide", page_icon="🥐")

st.markdown("""
    <style>
    .main { background-color: #F5E6D3; }
    .stButton>button { 
        background-color: #8B7355; color: white; width: 100%; border-radius: 8px; 
        height: 3em; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #5D4E37; border: 1px solid #C4A574; }
    .submit-reminder { 
        background: #FFEBEE; border-left: 4px solid #E53935; padding: 0.75rem; 
        border-radius: 4px; color: #C62828; font-weight: 500; margin: 10px 0;
    }
    .product-card {
        background: white; border: 1px solid #C4A574; border-radius: 12px;
        padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== 2. 初始化雲端連線與資料 ====================
# 建立 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db_data():
    # 讀取現有訂單，ttl=0 確保每次拿到的都是最新資料
    try:
        return conn.read(worksheet="癒室訂單紀錄", ttl=0)
    except:
        # 如果是第一次運行或讀取失敗，回傳空表
        return pd.DataFrame(columns=[
            "下單時間", "客戶姓名", "聯絡電話", "面交日期", "面交地點", 
            "面交時間", "經典數量", "核桃數量", "總金額", "付款方式", "付款資訊"
        ])

# ==================== 3. 側邊欄：主理人管理區 ====================
with st.sidebar:
    st.header("🍂 癒室 後台調度")
    st.markdown("---")
    
    # 產能設定
    ratio_choice = st.radio("今日生產配比 (上限 18 盒)", 
                            ["均衡生產 (各 9 盒)", "經典為主 (葡萄 12 / 核桃 6)", "核桃為主 (葡萄 6 / 核桃 12)"])
    ratios = {"均衡生產 (各 9 盒)": (9, 9), "經典為主 (葡萄 12 / 核桃 6)": (12, 6), "核桃為主 (葡萄 6 / 核桃 12)": (6, 12)}
    max_g, max_w = ratios[ratio_choice]
    
    # 日期設定 (你的接單排程)
    st.subheader("📅 製作日期設定")
    date_input = st.text_area("輸入製作日期 (YYYY-MM-DD)", "2026-02-10\n2026-02-17")
    prod_dates = [d.strip() for d in date_input.split('\n') if d.strip()]

# ==================== 4. 主頁面：消費者下單區 ====================
st.title("🍂 癒室 - 手工甜點")
st.markdown("**Healing Room Handmade · 2026 溫暖手作**")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📝 1. 客戶資訊")
    c_name = st.text_input("您的姓名", placeholder="請輸入姓名")
    c_phone = st.text_input("聯絡電話", placeholder="例：0912-345-678")
    
    st.markdown("### 📍 2. 面交選擇")
    selected_base_date = st.selectbox("選擇製作梯次", prod_dates) if prod_dates else None
    
    if selected_base_date:
        d0 = selected_base_date
        d1 = (datetime.strptime(d0, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        
        loc_opt = st.selectbox(
            "地點與時間規範",
            [f"{d0} 三重彰化銀行 (19:00後)", f"{d1} 華視大樓 (11:00-19:00)"]
        )
        
        # 依地點預設時間
        default_t = time(19, 0) if "三重" in loc_opt else time(12, 0)
        p_time = st.time_input("預計面交時間", value=default_t)
        
        # 時間合規性檢查 (編輯的精準要求)
        time_ok = True
        if "三重" in loc_opt and p_time < time(19, 0):
            st.warning("⚠️ 三重面交僅限 19:00 以後"); time_ok = False
        elif "華視" in loc_opt and (p_time < time(11, 0) or p_time >= time(19, 0)):
            st.warning("⚠️ 華視面交僅限 11:00 - 19:00 之間"); time_ok = False

with col2:
    st.markdown("### 🥐 3. 訂購數量")
    q_g = st.number_input("經典款 - 蘭姆葡萄 (盒)", min_value=0, max_value=max_g, step=1)
    q_w = st.number_input("純核桃 - 焦糖核桃 (盒)", min_value=0, max_value=max_w, step=1)
    
    total_price = (q_g + q_w) * 190
    st.info(f"💰 訂單總額：NT$ {total_price}")
    
    st.markdown("### 💳 4. 付款方式")
    pay_method = st.radio("支付管道", ["面交支付", "銀行轉帳", "Line Pay"], horizontal=True)
    pay_info = ""
    if pay_method != "面交支付":
        pay_info = st.text_input("轉帳後五碼 / Line Pay 顯示名稱")

# ==================== 5. 送出邏輯 (即時驗證) ====================
st.divider()
can_submit = True
errors = []

# 邏輯門鎖檢查
if not (c_name and c_phone): 
    can_submit = False; errors.append("請填寫姓名與電話")
if (q_g + q_w) == 0: 
    can_submit = False; errors.append("請至少選擇一盒肉桂捲")
if not (pay_method == "面交支付" or pay_info): 
    can_submit = False; errors.append("請填寫付款備查資訊")
if selected_base_date and not time_ok:
    can_submit = False; errors.append("面交時間不符合地點限制")

# 顯示未完成提示
if not can_submit:
    st.markdown(f'<div class="submit-reminder">⚠️ 尚未完成：{" · ".join(errors)}</div>', unsafe_allow_html=True)
    st.button("確認送出訂單", disabled=True)
else:
    if st.button("🚀 確認送出訂單 (將同步至雲端)"):
        with st.spinner("訂單同步中，請稍候..."):
            # 準備新資料
            new_row = pd.DataFrame([{
                "下單時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "客戶姓名": c_name,
                "聯絡電話": c_phone,
                "面交日期": loc_opt.split(' ')[0],
                "面交地點": "三重" if "三重" in loc_opt else "華視",
                "面交時間": p_time.strftime("%H:%M"),
                "經典數量": q_g,
                "核桃數量": q_w,
                "總金額": total_price,
                "付款方式": pay_method,
                "付款資訊": pay_info
            }])
            
            # 讀取、合併並寫回 Google Sheets
            existing_df = get_db_data()
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            conn.update(worksheet="癒室訂單紀錄", data=updated_df)
            
            st.balloons()
            st.success("✅ 訂單成立！資料已穩妥存入 Google 表格。")
            
            # 🔮 2026 塔羅指引 (為創業注入能量)
            st.markdown("---")
            st.markdown("### 🔮 癒室今日能量指引")
            tarot_msg = random.choice([
                "太陽：充滿希望的一天，您的創意將如肉桂香氣般散發。",
                "星星：靈感與直覺正旺，適合為 2027 年的夢想做規劃。",
                "世界：階段性的圓滿，您在編輯台與甜點間的平衡做得非常好。"
            ])
            st.info(tarot_msg)