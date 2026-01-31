import streamlit as st
import pandas as pd
import random
import time as pytime
from datetime import datetime, timedelta, time
from streamlit_gsheets import GSheetsConnection

# ==================== 1. 頁面配置與進階 CSS ====================
st.set_page_config(page_title="癒室 - 手工甜點", layout="wide", page_icon="🥐")

st.markdown("""
    <style>
    .main { background-color: #F5E6D3; }
    .stButton>button { 
        background-color: #8B7355; color: white; width: 100%; border-radius: 8px; 
        height: 3.5em; font-weight: bold; border: none; font-size: 1.1em; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #5D4E37; }
    .announcement-box {
        background-color: #FFF8E7; border: 2px solid #C4A574; padding: 1.2rem;
        border-radius: 12px; color: #5D4E37; margin-bottom: 1.5rem;
    }
    .product-img {
        border-radius: 15px; border: 3px solid #C4A574; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .submit-reminder { 
        background: #FFEBEE; border-left: 5px solid #E53935; padding: 1rem; 
        border-radius: 4px; color: #C62828; font-weight: 500; margin: 15px 0;
    }
    
    /* 塔羅翻牌動畫 CSS */
    @keyframes flipInY {
      from { transform: perspective(400px) rotateY(90deg); opacity: 0; }
      to { transform: perspective(400px) rotateY(0deg); opacity: 1; }
    }
    .tarot-container { display: flex; justify-content: center; margin-top: 2rem; }
    .tarot-card {
        width: 300px; padding: 20px; border-radius: 15px; text-align: center; color: #5D4E37;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15); border: 3px solid #C4A574;
        animation: flipInY 1s ease-out forwards;
        background: linear-gradient(135deg, #fff8e7 0%, #f5e6d3 100%);
    }
    .tarot-icon { font-size: 4rem; margin-bottom: 1rem; }
    .tarot-title { font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem; color: #8B7355;}
    .card-sun { border-color: #FFD700; background: linear-gradient(135deg, #FFFDE7 0%, #FFF9C4 100%); }
    .card-star { border-color: #81D4FA; background: linear-gradient(135deg, #E1F5FE 0%, #B3E5FC 100%); }
    .card-world { border-color: #A5D6A7; background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); }
    </style>
    """, unsafe_allow_html=True)

# ==================== 2. 雲端連線 ====================
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db_data():
    try:
        return conn.read(worksheet="癒室訂單紀錄", ttl=0)
    except:
        return pd.DataFrame(columns=["下單時間", "客戶姓名", "聯絡電話", "面交日期", "面交地點", "面交時間", "經典數量", "核桃數量", "總金額", "付款方式", "付款資訊"])

# ==================== 3. 側邊欄：打雜小妹專區 ====================
with st.sidebar:
    st.header("🍂 癒室 打雜小妹入口")
    admin_key = st.text_input("請輸入打雜小妹專屬密碼", type="password")
    
    if admin_key == "0512":
        st.success("身分確認：打雜小妹辛苦了！")
        st.markdown("---")
        st.subheader("🥐 生產排班")
        ratio_choice = st.radio("今日產能配置", ["均衡生產 (各 9 盒)", "經典為主 (12/6)", "核桃為主 (6/12)"])
        ratios = {"均衡生產 (各 9 盒)": (9, 9), "經典為主 (12/6)": (12, 6), "核桃為主 (6/12)": (6, 12)}
        max_g, max_w = ratios[ratio_choice]
        
        st.subheader("📅 接單日期調整")
        date_input = st.text_area("製作日期 (YYYY-MM-DD)", "2026-02-07\n2026-02-12\n2026-02-13")
        prod_dates = [d.strip() for d in date_input.split('\n') if d.strip()]
        st.session_state['admin_config'] = {"max_g": max_g, "max_w": max_w, "prod_dates": prod_dates}
    else:
        st.info("💡 此區塊為打雜小妹專用。")
        config = st.session_state.get('admin_config', {"max_g": 9, "max_w": 9, "prod_dates": ["2026-02-07", "2026-02-12", "2026-02-13"]})
        max_g, max_w, prod_dates = config['max_g'], config['max_w'], config['prod_dates']

# ==================== 4. 主頁面：公告、照片與下單 ====================
st.title("🍂 癒室 - 手工甜點")
st.markdown("**Healing Room Handmade · 2026 溫暖手作**")

# 公告欄
st.markdown(f"""
<div class="announcement-box">
    <h4 style="margin-top:0;">📢 癒室 2月打雜小妹接單快訊</h4>
    <small>
    • <b>2/07 梯次：</b>2/7 三重 (19:00+) / 2/8 華視 (11:00-17:00)<br>
    • <b>2/12 & 2/13 梯次：</b>僅開放三重自取 (19:00+)<br>
    ※ 均一價 $190/盒，打雜小妹親手包裝寄送。
    </small>
</div>
""", unsafe_allow_html=True)

df_existing = get_db_data()

col1, col2 = st.columns([1, 1.2]) # 稍微調整比例讓照片更吸睛

with col1:
    st.markdown("### 🖼️ 產品展示")
    # 插入你的美照
    st.image("548282507_1196129685655556_143484642680713398_n.jpg", 
             caption="手工慢火熬煮焦糖醬，每一顆都包裹著滿滿核桃與靈魂。", 
             use_container_width=True)
    
    st.markdown("### 📝 客戶資料")
    c_name = st.text_input("如何稱呼您")
    c_phone = st.text_input("聯絡電話")
    
    st.markdown("### 📍 面交梯次")
    target_date = st.selectbox("選擇製作日期", prod_dates)
    
    # 庫存計算
    next_day = (datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    batch_orders = df_existing[df_existing['面交日期'].isin([target_date, next_day])]
    used_g = pd.to_numeric(batch_orders['經典數量'], errors='coerce').sum()
    used_w = pd.to_numeric(batch_orders['核桃數量'], errors='coerce').sum()
    rem_g, rem_w = int(max(0, max_g - used_g)), int(max(0, max_w - used_w))

    if target_date == "2026-02-07":
        pickup_options = ["2026-02-07 三重彰化銀行 (19:00後)", "2026-02-08 華視大樓 (11:00-17:00)"]
    else:
        pickup_options = [f"{target_date} 三重彰化銀行 (19:00後)"]
    loc_opt = st.selectbox("面交地點", pickup_options)
    
    p_time = st.time_input("預計時間", value=time(12, 0) if "華視" in loc_opt else time(19, 0))
    time_ok = True
    if "華視" in loc_opt and (p_time < time(11, 0) or p_time > time(17, 0)): time_ok = False
    if "三重" in loc_opt and p_time < time(19, 0): time_ok = False

with col2:
    st.markdown("### 🥐 今日產能進度")
    st.markdown(f"**經典蘭姆葡萄 (剩 {rem_g} 盒)**")
    st.progress(min(1.0, used_g / max_g if max_g > 0 else 1))
    q_g = st.number_input("購買經典 (盒)", min_value=0, max_value=rem_g, step=1, key="q_g_7")
    
    st.markdown(f"**純核桃焦糖 (剩 {rem_w} 盒)**")
    st.progress(min(1.0, used_w / max_w if max_w > 0 else 1))
    q_w = st.number_input("購買核桃 (盒)", min_value=0, max_value=rem_w, step=1, key="q_w_7")
    
    st.markdown(f"#### 💰 總金額：NT$ {(q_g + q_w) * 190}")
    pay_method = st.radio("付款方式", ["面交", "轉帳", "Line Pay"], horizontal=True)
    pay_info = st.text_input("付款資訊 (後五碼/名稱)") if pay_method != "面交" else "現場支付"

# ==================== 5. 存檔與塔羅儀式 ====================
st.divider()
can_submit = True
errs = []
if not (c_name and c_phone): can_submit = False; errs.append("姓名電話漏填囉")
if (q_g + q_w) == 0: can_submit = False; errs.append("記得帶幾盒肉桂捲")
if not time_ok: can_submit = False; errs.append("時間不符合打雜小妹規範")

if not can_submit:
    st.markdown(f'<div class="submit-reminder">⚠️ 打雜小妹提醒：{" · ".join(errs)}</div>', unsafe_allow_html=True)
    st.button("確認送出訂單", disabled=True)
else:
    if st.button("✨ 確認送出，並抽取今日療癒指引 ✨"):
        with st.spinner("打雜小妹正在洗牌..."):
            # 寫入 Google Sheets
            new_row = pd.DataFrame([{
                "下單時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "客戶姓名": c_name, "聯絡電話": c_phone,
                "面交日期": loc_opt.split(' ')[0], "面交地點": "三重" if "三重" in loc_opt else "華視",
                "面交時間": p_time.strftime("%H:%M"),
                "經典數量": q_g, "核桃數量": q_w, "總金額": (q_g + q_w) * 190,
                "付款方式": pay_method, "付款資訊": pay_info
            }])
            conn.update(worksheet="癒室訂單紀錄", data=pd.concat([df_existing, new_row], ignore_index=True))
            
            tarot_deck = [
                {"class": "card-sun", "icon": "☀️", "title": "太陽 The Sun", "desc": "充滿希望與活力的能量！打雜小妹覺得您今天閃閃發光，這份甜點是您的陽光。"},
                {"class": "card-star", "icon": "⭐", "title": "星星 The Star", "desc": "療癒與靈感之泉。您的願望正慢慢發芽，就像肉桂捲在烤箱中熟成一般。"},
                {"class": "card-world", "icon": "🌍", "title": "世界 The World", "desc": "完美的圓滿與達成。辛苦了！這份甜點是給您努力生活最好的犒賞。"}
            ]
            drawn_card = random.choice(tarot_deck)
            
            st.balloons()
            st.success("✅ 訂單已收到！打雜小妹立刻去準備。")
            pytime.sleep(0.5)
            st.markdown(f"""
            <div class="tarot-container">
                <div class="tarot-card {drawn_card['class']}">
                    <div class="tarot-icon">{drawn_card['icon']}</div>
                    <div class="tarot-title">{drawn_card['title']}</div>
                    <div class="tarot-desc">{drawn_card['desc']}</div>
                    <div class="tarot-helper">— 來自打雜小妹的祝福</div>
                </div>
            </div>
            """, unsafe_allow_html=True)