import streamlit as st
import pandas as pd
import random
import time as pytime
from datetime import datetime, timedelta, time
from streamlit_gsheets import GSheetsConnection

# ==================== 1. 進階視覺美化 CSS ====================
st.set_page_config(page_title="癒室 - 手工甜點", layout="wide", page_icon="🥐")

st.markdown("""
    <style>
    /* 全域背景與字體 */
    .stApp { background-color: #FAF9F6; }
    h1, h2, h3 { color: #2D463E !important; font-family: 'Noto Serif TC', serif; }
    
    /* 自定義卡片容器 */
    .custom-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(45, 70, 62, 0.08);
        border: 1px solid #E9E4D9;
        margin-bottom: 1.5rem;
    }

    /* 公告欄樣式升級 */
    .announcement-box {
        background: linear-gradient(135deg, #FDF5E6 0%, #FAF3E0 100%);
        border-left: 6px solid #A67B5B;
        padding: 1.5rem;
        border-radius: 12px;
        color: #5D4E37;
        margin-bottom: 2rem;
    }

    /* 按鈕樣式升級 */
    .stButton>button { 
        background-color: #2D463E; color: #FAF9F6; 
        width: 100%; border-radius: 12px; 
        height: 3.8em; font-weight: 700; border: none; 
        font-size: 1.1em; transition: all 0.4s ease;
        box-shadow: 0 4px 10px rgba(45, 70, 62, 0.2);
    }
    .stButton>button:hover { 
        background-color: #A67B5B; 
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(166, 123, 91, 0.3);
    }
    
    /* 庫存進度條顏色 */
    .stProgress > div > div > div > div { background-color: #A67B5B; }

    /* 塔羅翻牌動畫 */
    @keyframes flipInY {
      from { transform: perspective(400px) rotateY(90deg); opacity: 0; }
      to { transform: perspective(400px) rotateY(0deg); opacity: 1; }
    }
    .tarot-container { display: flex; justify-content: center; margin-top: 2rem; }
    .tarot-card {
        width: 280px; padding: 25px; border-radius: 18px; text-align: center; color: #2D463E;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1); border: 2px solid #A67B5B;
        animation: flipInY 1.2s cubic-bezier(0.23, 1, 0.32, 1) forwards;
        background: white;
    }
    .tarot-icon { font-size: 3.5rem; margin-bottom: 0.8rem; }
    .card-sun { border-color: #EBC03F; background: #FFFDF5; }
    .card-star { border-color: #7BB8D4; background: #F5FAFF; }
    .card-world { border-color: #7FB069; background: #F7FFF5; }
    </style>
    """, unsafe_allow_html=True)

# ==================== 2. 雲端連線與資料處理 ====================
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db_data():
    try:
        return conn.read(worksheet="癒室訂單紀錄", ttl=0)
    except:
        return pd.DataFrame(columns=["下單時間", "客戶姓名", "聯絡電話", "面交日期", "面交地點", "面交時間", "經典數量", "核桃數量", "總金額", "付款方式", "付款資訊"])

# ==================== 3. 側邊欄：打雜小妹後台 ====================
with st.sidebar:
    st.markdown("## 🍂 癒室管理")
    admin_key = st.text_input("打雜小妹認證密碼", type="password")
    
    if admin_key == "0512":
        st.success("辛苦了！打雜小妹驗證通過 ✨")
        st.markdown("---")
        ratio_choice = st.radio("本日產能配置", ["核桃 3 / 葡萄 15", "核桃 6 / 葡萄 12"])
        ratios = {"核桃 3 / 葡萄 15": (15, 3), "核桃 6 / 葡萄 12": (12, 6)}
        max_g, max_w = ratios[ratio_choice]
        
        date_input = st.text_area("製作日期清單", "2026-02-07\n2026-02-12\n2026-02-13")
        prod_dates = [d.strip() for d in date_input.split('\n') if d.strip()]
        st.session_state['admin_config'] = {"max_g": max_g, "max_w": max_w, "prod_dates": prod_dates}
    else:
        st.caption("🔒 內部管理專用區")
        config = st.session_state.get('admin_config', {"max_g": 15, "max_w": 3, "prod_dates": ["2026-02-07", "2026-02-12", "2026-02-13"]})
        max_g, max_w, prod_dates = config['max_g'], config['max_w'], config['prod_dates']

# ==================== 4. 主頁面：品牌形象與公告 ====================
st.title("🍂 癒室 · Healing Room")
st.markdown("##### *Handmade Cinnamon Rolls & Soul Healing*")

st.markdown(f"""
<div class="announcement-box">
    <strong style="font-size: 1.1em;">📢 打雜小妹 2 月接單快訊</strong><br>
    <span style="font-size: 0.95em; line-height: 1.6;">
    • <b>2/07 梯次：</b>2/7 三重 (19:00+) / 2/8 華視 (11:00-17:00)<br>
    • <b>2/12 & 2/13 梯次：</b>僅開放三重自取 (19:00+)<br>
    ※ 慢火熬煮焦糖，每盒兩顆入均一價 $190。
    </span>
</div>
""", unsafe_allow_html=True)

df_existing = get_db_data()

# ==================== 5. 下單區卡片排版 ====================
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.image("548282507_1196129685655556_143484642680713398_n.jpg", 
             caption="手工慢火熬煮，裹滿核桃的療癒滋味。", use_container_width=True)
    
    st.subheader("📝 預約資訊")
    c_name = st.text_input("您的稱呼")
    c_phone = st.text_input("聯絡電話")
    
    st.subheader("📍 領取安排")
    target_date = st.selectbox("選擇梯次", prod_dates)
    
    # 即時計算庫存
    next_day = (datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    batch_orders = df_existing[df_existing['面交日期'].isin([target_date, next_day])]
    used_g = pd.to_numeric(batch_orders['經典數量'], errors='coerce').sum()
    used_w = pd.to_numeric(batch_orders['核桃數量'], errors='coerce').sum()
    rem_g, rem_w = int(max(0, max_g - used_g)), int(max(0, max_w - used_w))

    pickup_options = ["2026-02-07 三重 (19:00+)", "2026-02-08 華視 (11:00-17:00)"] if target_date == "2026-02-07" else [f"{target_date} 三重 (19:00+)"]
    loc_opt = st.selectbox("面交地點", pickup_options)
    
    p_time = st.time_input("預計抵達時間", value=time(19, 0) if "三重" in loc_opt else time(12, 0))
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🥐 產能與訂購數量")
    
    st.write(f"**蘭姆葡萄核桃** (剩餘 {rem_g} 盒)")
    st.progress(min(1.0, used_g / max_g if max_g > 0 else 1))
    q_g = st.number_input("訂購經典款", min_value=0, max_value=rem_g, step=1, key="q_g_9")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.write(f"**純核桃焦糖** (剩餘 {rem_w} 盒)")
    st.progress(min(1.0, used_w / max_w if max_w > 0 else 1))
    q_w = st.number_input("訂購純核桃", min_value=0, max_value=rem_w, step=1, key="q_w_9")
    
    total_price = (q_g + q_w) * 190
    st.markdown(f"### 💰 總額：NT$ {total_price}")
    
    st.subheader("💳 支付管道")
    pay_method = st.radio("付款方式", ["面交支付", "轉帳", "Line Pay"], horizontal=True)
    pay_info = st.text_input("付款備註 (後五碼等)") if pay_method != "面交支付" else "現場付款"
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== 6. 提交邏輯 ====================
st.divider()
can_submit = (c_name and c_phone and (q_g + q_w) > 0)

if not can_submit:
    st.warning("⚠️ 記得填寫姓名電話，並選擇至少一盒肉桂捲喔！")
    st.button("確認預約", disabled=True)
else:
    if st.button("✨ 送出預約，並領取今日療癒指引 ✨"):
        with st.spinner("打雜小妹洗牌中..."):
            # 寫入資料庫
            new_row = pd.DataFrame([{
                "下單時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "客戶姓名": c_name, "聯絡電話": c_phone,
                "面交日期": loc_opt.split(' ')[0], "面交地點": "三重" if "三重" in loc_opt else "華視",
                "面交時間": p_time.strftime("%H:%M"),
                "經典數量": q_g, "核桃數量": q_w, "總金額": total_price,
                "付款方式": pay_method, "付款資訊": pay_info
            }])
            conn.update(worksheet="癒室訂單紀錄", data=pd.concat([df_existing, new_row], ignore_index=True))
            
            # 塔羅儀式
            tarot_deck = [
                {"class": "card-sun", "icon": "☀️", "title": "太陽 The Sun", "desc": "溫暖且明亮的能量，這份甜點將為您的明天帶來滿滿元氣！"},
                {"class": "card-star", "icon": "⭐", "title": "星星 The Star", "desc": "療癒與希望的指引。放下煩惱，享受這一刻的純粹甜美。"},
                {"class": "card-world", "icon": "🌍", "title": "世界 The World", "desc": "階段性的圓滿達成。給努力生活的您一份應得的獎勵。"}
            ]
            drawn = random.choice(tarot_deck)
            
            st.balloons()
            st.success("✅ 預約成功！打雜小妹已將您的需求排入製作清單。")
            st.markdown(f"""
            <div class="tarot-container">
                <div class="tarot-card {drawn['class']}">
                    <div class="tarot-icon">{drawn['icon']}</div>
                    <div class="tarot-title">{drawn['title']}</div>
                    <div class="tarot-desc">{drawn['desc']}</div>
                    <div style="margin-top:15px; font-size:0.85em; color:#A67B5B;">— 打雜小妹親筆祝福</div>
                </div>
            </div>
            """, unsafe_allow_html=True)