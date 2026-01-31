import streamlit as st
import pandas as pd
import random
import time as pytime
from datetime import datetime, timedelta, time
from streamlit_gsheets import GSheetsConnection

# ==================== 1. 溫潤大地風格 CSS ====================
st.set_page_config(page_title="癒室 - 手工甜點", layout="wide", page_icon="🥐")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700&display=swap');
    
    /* 全域暖色調 */
    .stApp { background-color: #FFF9F0; font-family: 'Noto Serif TC', serif; }
    h1, h2, h3 { color: #3E2723 !important; }

    /* 卡片設計：溫柔陰影 */
    .custom-card {
        background: #ffffff; padding: 2.5rem; border-radius: 20px;
        box-shadow: 0 8px 25px rgba(62, 39, 35, 0.05); border: 1px solid #E6CCB2;
        margin-bottom: 2rem; transition: 0.3s;
    }
    .custom-card:hover { transform: translateY(-3px); box-shadow: 0 12px 35px rgba(160, 82, 45, 0.1); }

    /* 公告欄：肉桂暖陽色 */
    .announcement-box {
        background: linear-gradient(135deg, #A0522D 0%, #8B4513 100%);
        color: #FFFFFF; padding: 1.5rem; border-radius: 16px; margin-bottom: 2rem;
    }

    /* 按鈕：經典肉桂色 */
    .stButton>button { 
        background: linear-gradient(135deg, #A0522D 0%, #BC8F8F 100%);
        color: #ffffff; width: 100%; border-radius: 12px; 
        height: 3.8em; font-weight: 700; border: none; font-size: 1.1em;
    }
    .stButton>button:hover { background: #3E2723; color: #FFF9F0; }
    
    /* 進度條顏色 */
    .stProgress > div > div > div > div { background-color: #D4A373; }

    /* 塔羅牌組動態效果 */
    @keyframes cardFlip {
      from { transform: perspective(1000px) rotateY(-90deg); opacity: 0; }
      to { transform: perspective(1000px) rotateY(0deg); opacity: 1; }
    }
    .tarot-card {
        width: 290px; padding: 30px; border-radius: 24px; text-align: center;
        box-shadow: 0 15px 40px rgba(62, 39, 35, 0.1); border: 2px solid #D4A373;
        animation: cardFlip 1.2s ease-out forwards; background: #fff; margin: 0 auto;
    }
    .fire { border-color: #CD5C5C; background: #FFF5F5; }
    .water { border-color: #4682B4; background: #F0F8FF; }
    .air { border-color: #DAA520; background: #FFFAF0; }
    .earth { border-color: #556B2F; background: #F5F5DC; }
    </style>
    """, unsafe_allow_html=True)

# ==================== 2. 雲端連線與資料處理 ====================
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db_data():
    try:
        df = conn.read(worksheet="癒室訂單紀錄", ttl=0)
        df['聯絡電話'] = df['聯絡電話'].astype(str).str.replace("'", "")
        return df
    except:
        return pd.DataFrame(columns=["下單時間", "客戶姓名", "聯絡電話", "面交日期", "面交地點", "面交時間", "經典數量", "核桃數量", "總金額", "付款方式", "付款資訊"])

df_existing = get_db_data()

# ==================== 3. 打雜小妹管理後台 ====================
with st.sidebar:
    st.markdown("### 🍂 癒室 · 打雜小妹入口")
    admin_key = st.text_input("密碼驗證", type="password")
    
    if admin_key == "0512":
        st.success("辛苦了！驗證通過 ✨")
        ratio_choice = st.radio("本日產能配比", ["核桃 3 / 葡萄 15", "核桃 6 / 葡萄 12"])
        ratios = {"核桃 3 / 葡萄 15": (15, 3), "核桃 6 / 葡萄 12": (12, 6)}
        max_g, max_w = ratios[ratio_choice]
        prod_dates = [d.strip() for d in st.text_area("接單日期", "2026-02-07\n2026-02-12\n2026-02-13").split('\n') if d.strip()]
        st.session_state['admin_config'] = {"max_g": max_g, "max_w": max_w, "prod_dates": prod_dates}
        
        st.subheader("📋 營運調度")
        v_date = st.selectbox("選取日期", prod_dates)
        daily_df = df_existing[df_existing['面交日期'].str.contains(v_date, na=False)]
        if not daily_df.empty:
            st.metric("當日預約", f"{len(daily_df)} 筆")
            download_df = daily_df.copy()
            download_df['聯絡電話'] = "'" + download_df['聯絡電話'].astype(str)
            st.download_button("📥 下載清單", download_df.to_csv(index=False).encode('utf-8-sig'), f"癒室_{v_date}.csv")
    else:
        max_g, max_w, prod_dates = 15, 3, ["2026-02-07", "2026-02-12", "2026-02-13"]

# ==================== 4. 主頁面：品牌與公告 ====================
st.title("🍂 癒室 - 手工甜點")
st.markdown("##### *Every Bite is a Warm Hug for Your Soul*")

st.markdown(f"""
<div class="announcement-box">
    <strong>📢 癒室 - 手工甜點 2 月接單快訊</strong><br>
    <small>• 2/7 三重 (19:00+) / 2/8 華視 (11:00-17:00) | • 2/12 & 2/13 僅三重 (19:00+) | 均一價 $190</small>
</div>
""", unsafe_allow_html=True)

with st.expander("🔍 預約回溯：輸入電話確認您的訂單"):
    search_p = st.text_input("聯絡電話")
    if search_p:
        my_row = df_existing[df_existing['聯絡電話'] == search_p.replace("'", "")].tail(1)
        if not my_row.empty:
            st.success(f"Hi {my_row.iloc[0]['客戶姓名']}，找到紀錄囉！")
            st.info(f"📅 {my_row.iloc[0]['面交日期']} {my_row.iloc[0]['面交時間']} 在 {my_row.iloc[0]['面交地點']}")

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.image("548282507_1196129685655556_143484642680713398_n.jpg", caption="手工焦糖核桃，溫暖靈魂的味道。", use_container_width=True)
    st.subheader("📝 客戶資料")
    c_name = st.text_input("您的稱呼")
    c_phone = st.text_input("聯絡電話", placeholder="例：0912345678", key="phone_19")
    t_date = st.selectbox("製作梯次", prod_dates)
    
    n_day = (datetime.strptime(t_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    batch = df_existing[df_existing['面交日期'].isin([t_date, n_day])]
    u_g, u_w = pd.to_numeric(batch['經典數量']).sum(), pd.to_numeric(batch['核桃數量']).sum()
    rem_g, rem_w = int(max(0, max_g - u_g)), int(max(0, max_w - u_w))

    pickup_opts = ["2026-02-07 三重 (19:00+)", "2026-02-08 華視 (11:00-17:00)"] if t_date == "2026-02-07" else [f"{t_date} 三重 (19:00+)"]
    loc_opt = st.selectbox("面交安排", pickup_opts)
    p_time = st.time_input("預計時間", value=time(19, 0) if "三重" in loc_opt else time(12, 0))
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🥐 即時庫存")
    st.write(f"**蘭姆葡萄** (剩餘 {rem_g} 盒)")
    st.progress(min(1.0, u_g / max_g if max_g > 0 else 1))
    q_g = st.number_input("購買數量 (經典)", min_value=0, max_value=rem_g, step=1, key="q_g_19")
    st.write(f"**純焦糖核桃** (剩餘 {rem_w} 盒)")
    st.progress(min(1.0, u_w / max_w if max_w > 0 else 1))
    q_w = st.number_input("購買數量 (核桃)", min_value=0, max_value=rem_w, step=1, key="q_w_19")
    st.markdown(f"### 💰 預估總額：NT$ {(q_g + q_w) * 190}")
    pay_method = st.radio("付款方式", ["面交支付", "轉帳", "Line Pay"], horizontal=True)
    pay_info = st.text_input("付款備註 (後五碼等)") if pay_method != "面交支付" else "現場付款"
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== 5. 提交與 22 張塔羅完整牌組 ====================
st.divider()
if st.button("✨ 送出預約，並領取今日療癒指引 ✨"):
    if c_name and c_phone and (q_g + q_w) > 0:
        with st.spinner("打雜小妹洗牌中..."):
            formatted_phone = "'" + str(c_phone).replace("'", "")
            new_row = pd.DataFrame([{
                "下單時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "客戶姓名": c_name, "聯絡電話": formatted_phone, 
                "面交日期": loc_opt.split(' ')[0], "面交地點": "三重" if "三重" in loc_opt else "華視",
                "面交時間": p_time.strftime("%H:%M"),
                "經典數量": q_g, "核桃數量": q_w, "總金額": (q_g + q_w) * 190,
                "付款方式": pay_method, "付款資訊": pay_info
            }])
            df_for_up = df_existing.copy()
            df_for_up['聯絡電話'] = "'" + df_for_up['聯絡電話'].astype(str)
            conn.update(worksheet="癒室訂單紀錄", data=pd.concat([df_for_up, new_row], ignore_index=True))
            
            tarot_deck = [
                {"e": "air", "i": "🃏", "t": "0 愚者", "d": "新冒險的開始，為您的勇氣喝采！"},
                {"e": "fire", "i": "🪄", "t": "I 魔術師", "d": "您擁有一切創造美好生活的素材。"},
                {"e": "water", "i": "📜", "t": "II 女教皇", "d": "靜心傾聽內在，智慧就在那裡。"},
                {"e": "earth", "i": "👑", "t": "III 女皇", "d": "今日適合被美好與豐盛包圍。"},
                {"e": "fire", "i": "🏛️", "t": "IV 皇帝", "d": "穩定的秩序，掌控生活的節奏。"},
                {"e": "earth", "i": "🙏", "t": "V 教皇", "d": "智慧藏於經驗，聽從心的引導。"},
                {"e": "air", "i": "💞", "t": "VI 戀人", "d": "美好的連結正悄悄發生。"},
                {"e": "fire", "i": "🛒", "t": "VII 戰車", "d": "衝勁十足！今日無人能擋。"},
                {"e": "fire", "i": "🦁", "t": "VIII 力量", "d": "溫柔的堅韌，足以平定喧囂。"},
                {"e": "earth", "i": "💡", "t": "IX 隱者", "d": "在安靜中，找回真實的自己。"},
                {"e": "fire", "i": "🎡", "t": "X 命運之輪", "d": "轉機已至，好運隨香味而來。"},
                {"e": "air", "i": "⚖️", "t": "XI 正義", "d": "找回平衡，讓生活重新對焦。"},
                {"e": "water", "i": "🙃", "t": "XII 倒吊人", "d": "換個視角看世界，難題會變輕快。"},
                {"e": "water", "i": "🦋", "t": "XIII 死神", "d": "告別舊節奏，迎接新篇章。"},
                {"e": "fire", "i": "🏺", "t": "XIV 節制", "d": "完美比例的融合，平衡就是美。"},
                {"e": "earth", "i": "😈", "t": "XV 惡魔", "d": "偶爾的耽溺是健康的誘惑。"},
                {"e": "fire", "i": "⚡", "t": "XVI 高塔", "d": "突破性的重組，更好的未來。"},
                {"e": "air", "i": "⭐", "t": "XVII 星星", "d": "希望星光指引，願望正熟成。"},
                {"e": "water", "i": "🌙", "t": "XVIII 月亮", "d": "擁抱不安，星光會指引明早。"},
                {"e": "fire", "i": "☀️", "t": "XIX 太陽", "d": "充滿活力的光芒，今日圓滿。"},
                {"e": "fire", "i": "🎺", "t": "XX 審判", "d": "聽從內心呼喚，再次啟航。"},
                {"e": "earth", "i": "🌍", "t": "XXI 世界", "d": "圓滿的達成，最好的犒賞。"}
            ]
            drawn = random.choice(tarot_deck)
            st.balloons()
            st.success("✅ 預約成功！打雜小妹立刻去備貨囉。")
            pytime.sleep(0.5)
            st.markdown(f"<div class='tarot-container'><div class='tarot-card {drawn['e']}'><div class='tarot-icon'>{drawn['i']}</div><div style='font-size:1.3rem;font-weight:700;margin-bottom:10px'>{drawn['t']}</div><p>{drawn['d']}</p><small>— 來自 癒室 - 手工甜點 的專屬祝福</small></div></div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ 姓名電話或數量都要填寫完整喔！")