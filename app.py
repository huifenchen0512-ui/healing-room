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
    .submit-reminder { 
        background: #FFEBEE; border-left: 5px solid #E53935; padding: 1rem; 
        border-radius: 4px; color: #C62828; font-weight: 500; margin: 15px 0;
    }
    .admin-box {
        background-color: #FDF5E6; border: 1px dashed #8B7355; padding: 10px; border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================== 2. 初始化連線與資料庫 ====================
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db_data():
    try:
        # 讀取現有訂單，ttl=0 確保不快取，每次都拿最新資料
        return conn.read(worksheet="癒室訂單紀錄", ttl=0)
    except:
        return pd.DataFrame(columns=[
            "下單時間", "客戶姓名", "聯絡電話", "面交日期", "面交地點", 
            "面交時間", "經典數量", "核桃數量", "總金額", "付款方式", "付款資訊"
        ])

# ==================== 3. 側邊欄：主理人管理入口 (密碼鎖) ====================
with st.sidebar:
    st.header("🍂 癒室 管理中心")
    # 管理密碼設定 (預設為你的生日 0512)
    admin_key = st.text_input("輸入管理密碼以開啟後台", type="password")
    
    if admin_key == "0512":
        st.success("主理人身分驗證成功")
        st.markdown("---")
        st.subheader("🥐 產能配置")
        ratio_choice = st.radio("今日生產配比", 
                                ["均衡生產 (各 9 盒)", "經典為主 (葡萄 12 / 核桃 6)", "核桃為主 (葡萄 6 / 核桃 12)"])
        ratios = {"均衡生產 (各 9 盒)": (9, 9), "經典為主 (葡萄 12 / 核桃 6)": (12, 6), "核桃為主 (葡萄 6 / 核桃 12)": (6, 12)}
        max_g, max_w = ratios[ratio_choice]
        
        st.subheader("📅 製作日期設定")
        date_input = st.text_area("輸入製作日期 (YYYY-MM-DD)", "2026-02-10\n2026-02-17\n2026-02-24")
        prod_dates = [d.strip() for d in date_input.split('\n') if d.strip()]
        
        # 存入 Session State 確保全域可用
        st.session_state['max_g'] = max_g
        st.session_state['max_w'] = max_w
        st.session_state['prod_dates'] = prod_dates
    else:
        st.info("💡 此區塊為「癒室」主理人專用。")
        st.caption("客人請直接在右側表單選擇現有梯次下單即可。")
        # 非管理員模式下使用預設或已設定值
        max_g = st.session_state.get('max_g', 9)
        max_w = st.session_state.get('max_w', 9)
        prod_dates = st.session_state.get('prod_dates', ["2026-02-10", "2026-02-17"])

# ==================== 4. 主頁面：消費者下單區 ====================
st.title("🍂 癒室 - 手工甜點")
st.markdown("**Healing Room Handmade · 2026 溫暖手作**")
st.markdown("---")

st.info("📦 為了確保品質，肉桂捲每盒兩顆入，均一價 $190。")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📝 1. 訂購人資訊")
    c_name = st.text_input("客戶姓名", placeholder="您的稱呼")
    c_phone = st.text_input("聯絡電話", placeholder="您的手機號碼")
    
    st.markdown("### 📍 2. 面交梯次選擇")
    selected_base_date = st.selectbox("請選擇預計製作的梯次", prod_dates) if prod_dates else None
    
    if selected_base_date:
        d0 = selected_base_date
        d1 = (datetime.strptime(d0, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        
        loc_opt = st.selectbox(
            "地點與時間限制",
            [f"{d0} 三重彰化銀行 (19:00後)", f"{d1} 華視大樓 (11:00-19:00)"]
        )
        
        # 自動給予預設時間建議
        default_t = time(19, 0) if "三重" in loc_opt else time(12, 0)
        p_time = st.time_input("預計面交時間", value=default_t)
        
        # 嚴謹的時間合規檢查
        time_ok = True
        if "三重" in loc_opt and p_time < time(19, 0):
            st.warning("⚠️ 三重面交限於 19:00 以後"); time_ok = False
        elif "華視" in loc_opt and (p_time < time(11, 0) or p_time >= time(19, 0)):
            st.warning("⚠️ 華視面交限於 11:00 - 19:00 之間"); time_ok = False

with col2:
    st.markdown("### 🥐 3. 口味與數量")
    q_g = st.number_input("經典款 - 蘭姆葡萄核桃 (盒)", min_value=0, max_value=max_g, step=1)
    q_w = st.number_input("純核桃 - 焦糖核桃 (盒)", min_value=0, max_value=max_w, step=1)
    
    total_price = (q_g + q_w) * 190
    st.markdown(f"#### 💰 訂單總額：NT$ {total_price}")
    
    st.markdown("### 💳 4. 支付管道")
    pay_method = st.radio("付款方式", ["面交支付", "銀行轉帳", "Line Pay"], horizontal=True)
    pay_info = ""
    if pay_method != "面交支付":
        pay_info = st.text_input("轉帳帳號後五碼 / Line Pay 顯示名稱")

# ==================== 5. 最終送出與雲端同步邏輯 ====================
st.divider()
can_submit = True
errors = []

# 檢查必填欄位
if not (c_name and c_phone): 
    can_submit = False; errors.append("姓名與電話為必填欄位")
if (q_g + q_w) == 0: 
    can_submit = False; errors.append("請至少選擇一盒產品")
if pay_method != "面交支付" and not pay_info: 
    can_submit = False; errors.append("非面交請填寫付款備查資訊")
if selected_base_date and not time_ok:
    can_submit = False; errors.append("面交時間不符合地點限制")

# 按鈕控制
if not can_submit:
    st.markdown(f'<div class="submit-reminder">⚠️ 尚未完成：{" · ".join(errors)}</div>', unsafe_allow_html=True)
    st.button("確認送出訂單", disabled=True)
else:
    if st.button("🚀 確認送出訂單 (系統自動記錄至 Google Sheets)"):
        with st.spinner("訂單飛向雲端中..."):
            # 準備數據行
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
            
            # 讀取並合併
            existing_df = get_db_data()
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            
            # 寫回試算表
            conn.update(worksheet="癒室訂單紀錄", data=updated_df)
            
            st.balloons()
            st.success("✅ 訂單成立！感謝您對癒室的支持。")
            
            # 🔮 能量塔羅指引 (2026 創業地基)
            st.markdown("---")
            st.markdown("### 🔮 癒室今日能量指引")
            tarot_msg = random.choice([
                "☀️ 太陽：今日運勢如陽光般燦爛，適合與他人分享這份甜蜜。",
                "⭐ 星星：您的直覺非常敏銳，目前的計畫（包含創業）正往好的方向發展。",
                "🌍 世界：代表圓滿與達成，這一批肉桂捲將為您帶來美好的循環。"
            ])
            st.info(tarot_msg)

st.markdown("---")
st.caption("癒室 - 手工甜點 · Healing Room Handmade · 2026 製作")