import streamlit as st
import pandas as pd
import random
import time as pytime
from datetime import datetime, timedelta, time
from streamlit_gsheets import GSheetsConnection

# ==================== 1. 導播級視覺美化 CSS ====================
st.set_page_config(page_title="癒室 - 手工甜點", layout="wide", page_icon="🥐")

st.markdown("""
    <style>
    /* 引入 Google 字體 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700&display=swap');

    /* 全域背景設定 */
    .stApp { 
        background-color: #FAF9F6;
        font-family: 'Noto Serif TC', serif;
    }

    /* 漸層進入動畫 */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main-container { animation: fadeInUp 1.2s ease-out; }

    /* 精緻卡片設計 */
    .custom-card {
        background: #ffffff;
        padding: 2.5rem;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(45, 70, 62, 0.05);
        border: 1px solid #E9E4D9;
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    .custom-card:hover {
        box-shadow: 0 15px 45px rgba(166, 123, 91, 0.1);
        transform: translateY(-5px);
    }

    /* 公告欄：森林色調 */
    .announcement-box {
        background: linear-gradient(135deg, #2D463E 0%, #1A2E28 100%);
        color: #FAF9F6;
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(45, 70, 62, 0.2);
    }

    /* 專業按鈕樣式 */
    .stButton>button { 
        background: linear-gradient(135deg, #A67B5B 0%, #8B6B4D 100%);
        color: #ffffff; width: 100%; border-radius: 16px; 
        height: 4em; font-weight: 700; border: none; font-size: 1.1em;
        letter-spacing: 2px;
        transition: 0.5s;
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #2D463E 0%, #1A2E28 100%);
        box-shadow: 0 8px 25px rgba(45, 70, 62, 0.3);
    }

    /* 塔羅牌組 3D 動畫強化 */
    @keyframes cardFlip {
      from { transform: perspective(1000px) rotateY(-90deg); opacity: 0; }
      to { transform: perspective(1000px) rotateY(0deg); opacity: 1; }
    }
    .tarot-card {
        width: 300px; padding: 35px; border-radius: 24px; text-align: center;
        box-shadow: 0 20px 50px rgba(0,0,0,0.1);
        animation: cardFlip 1.5s cubic-bezier(0.23, 1, 0.32, 1) forwards;
        background: #fff;
        border: 2px solid #A67B5B;
        margin: 0 auto;
    }
    .tarot-icon { font-size: 4rem; margin-bottom: 15px; }
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
    st.markdown("### 🍂 癒室 · 打雜小妹後台")
    admin_key = st.text_input("密碼驗證", type="password")
    
    if admin_key == "0512":
        st.success("辛苦了！驗證通過")
        st.markdown("---")
        ratio_choice = st.radio("產能配比", ["核桃 3 / 葡萄 15", "核桃 6 / 葡萄 12"])
        ratios = {"核桃 3 / 葡萄 15": (15, 3), "核桃 6 / 葡萄 12": (12, 6)}
        max_g, max_w = ratios[ratio_choice]
        prod_dates = [d.strip() for d in st.text_area("接單日期", "2026-02-07\n2026-02-12\n2026-02-13").split('\n') if d.strip()]
        st.session_state['admin_config'] = {"max_g": max_g, "max_w": max_w, "prod_dates": prod_dates}
        
        st.subheader("📋 營運數據")
        v_date = st.selectbox("選取日期", prod_dates)
        daily_df = df_existing[df_existing['面交日期'].str.contains(v_date, na=False)]
        if not daily_df.empty:
            st.metric("當日訂單", f"{len(daily_df)} 筆")
            st.download_button("📥 出貨清單下載", daily_df.to_csv(index=False).encode('utf-8-sig'), f"癒室_{v_date}.csv")
    else:
        max_g, max_w, prod_dates = 15, 3, ["2026-02-07", "2026-02-12", "2026-02-13"]

# ==================== 4. 主頁面：光影視覺排版 ====================
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.title("🍂 癒室 · Healing Room")
st.markdown("##### *每一顆肉桂捲，都是為靈魂準備的溫暖慰藉*")

st.markdown(f"""
<div class="announcement-box">
    <strong>📢 2 月打雜小妹接單通報</strong><br>
    <span style="font-size:0.9em; opacity:0.9;">
    • 2/7 梯次：三重 (19:00+) / 華視 (11:00-17:00)<br>
    • 2/12 & 2/13：僅開放三重自取 (19:00+)<br>
    ※ 慢火熬煮焦糖，每盒兩顆入均一價 $190。
    </span>
</div>
""", unsafe_allow_html=True)

# 查詢功能
with st.expander("🔍 預約回溯：輸入電話確認您的訂單"):
    search_p = st.text_input("聯絡電話")
    if search_p:
        my_row = df_existing[df_existing['聯絡電話'] == search_p.replace("'", "")].tail(1)
        if not my_row.empty:
            st.success(f"Hi {my_row.iloc[0]['客戶姓名']}，打雜小妹幫您找回來囉！")
            st.info(f"📅 {my_row.iloc[0]['面交日期']} {my_row.iloc[0]['面交時間']} 於 {my_row.iloc[0]['面交地點']}")

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.image("548282507_1196129685655556_143484642680713398_n.jpg", caption="手工焦糖核桃，溫暖靈魂的味道。", use_container_width=True)
    st.subheader("📝 預約資訊")
    c_name = st.text_input("您的稱呼")
    c_phone = st.text_input("聯絡電話", placeholder="例：0912345678", key="phone_17")
    t_date = st.selectbox("選擇製作梯次", prod_dates)
    
    # 庫存計算
    n_day = (datetime.strptime(t_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    batch = df_existing[df_existing['面交日期'].isin([t_date, n_day])]
    u_g, u_w = pd.to_numeric(batch['經典數量']).sum(), pd.to_numeric(batch['核桃數量']).sum()
    rem_g, rem_w = int(max(0, max_g - u_g)), int(max(0, max_w - u_w))

    pickup_opts = ["2026-02-07 三重 (19:00+)", "2026-02-08 華視 (11:00-17:00)"] if t_date == "2026-02-07" else [f"{t_date} 三重 (19:00+)"]
    loc_opt = st.selectbox("領取方式", pickup_opts)
    p_time = st.time_input("預計時間", value=time(19, 0) if "三重" in loc_opt else time(12, 0))
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🥐 產能進度")
    st.write(f"**蘭姆葡萄** (剩餘 {rem_g} 盒)")
    st.progress(min(1.0, u_g / max_g if max_g > 0 else 1))
    q_g = st.number_input("訂購數量 (經典)", min_value=0, max_value=rem_g, step=1, key="q_g_17")
    
    st.write(f"**純焦糖核桃** (剩餘 {rem_w} 盒)")
    st.progress(min(1.0, u_w / max_w if max_w > 0 else 1))
    q_w = st.number_input("訂購數量 (核桃)", min_value=0, max_value=rem_w, step=1, key="q_w_17")
    
    st.markdown(f"### 💰 預估總額：NT$ {(q_g + q_w) * 190}")
    pay_method = st.radio("付款方式", ["面交支付", "轉帳", "Line Pay"], horizontal=True)
    pay_info = st.text_input("付款備註 (後五碼等)") if pay_method != "面交支付" else "現場付款"
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== 5. 提交與 22 張完整牌組 ====================
st.divider()
if st.button("✨ 送出預約，並領取今日療癒指引 ✨"):
    if c_name and c_phone and (q_g + q_w) > 0:
        with st.spinner("打雜小妹正在為您洗牌..."):
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
                {"e": "air", "i": "🃏", "t": "0 愚者", "d": "新冒險的開始，打雜小妹為您的熱情鼓掌！"},
                {"e": "fire", "i": "🪄", "t": "I 魔術師", "d": "您手握創造生活的權限，精彩正要開始。"},
                {"e": "water", "i": "📜", "t": "II 女教皇", "d": "靜聽直覺，它是您最準確的導播。"},
                {"e": "earth", "i": "👑", "t": "III 女皇", "d": "今日適合被美好豐盛包圍，盡情享受。"},
                {"e": "fire", "i": "🏛️", "t": "IV 皇帝", "d": "掌控節奏，您就是生活的主導者。"},
                {"e": "earth", "i": "🙏", "t": "V 教皇", "d": "傳統中藏著智慧，聽從經驗的引導。"},
                {"e": "air", "i": "💞", "t": "VI 戀人", "d": "美好的連結正在發生，跟隨您的心。"},
                {"e": "fire", "i": "🛒", "t": "VII 戰車", "d": "衝勁十足！今日無人能擋。"},
                {"e": "fire", "i": "🦁", "t": "VIII 力量", "d": "溫柔的堅韌，足以平定喧囂。"},
                {"e": "earth", "i": "💡", "t": "IX 隱者", "d": "獨處時光也很珍貴，找回真實的自己。"},
                {"e": "fire", "i": "🎡", "t": "X 命運之輪", "d": "轉動契機已至，好運隨香而來。"},
                {"e": "air", "i": "⚖️", "t": "XI 正義", "d": "找回平衡，讓生活重新對焦。"},
                {"e": "water", "i": "🙃", "t": "XII 倒吊人", "d": "換個視角看世界，難題會變輕盈。"},
                {"e": "water", "i": "🦋", "t": "XIII 死神", "d": "告別舊節奏，迎接新篇章的勇氣。"},
                {"e": "fire", "i": "🏺", "t": "XIV 節制", "d": "完美比例的融合，平衡就是美。"},
                {"e": "earth", "i": "😈", "t": "XV 惡魔", "d": "偶爾的耽溺是健康的誘惑。"},
                {"e": "fire", "i": "⚡", "t": "XVI 高塔", "d": "突破性的重組，為了更穩固的藍圖。"},
                {"e": "air", "i": "⭐", "t": "XVII 星星", "d": "希望星光指引，願望正慢慢熟成。"},
                {"e": "water", "i": "🌙", "t": "XVIII 月亮", "d": "擁抱不安，星光會指引明早的路。"},
                {"e": "fire", "i": "☀️", "t": "XIX 太陽", "d": "充滿活力的明亮光芒，今日圓滿。"},
                {"e": "fire", "i": "🎺", "t": "XX 審判", "d": "聽從內心呼喚，再次覺醒。"},
                {"e": "earth", "i": "🌍", "t": "XXI 世界", "d": "圓滿的達成，給辛苦生活的您最好的犒賞。"}
            ]
            drawn = random.choice(tarot_deck)
            st.balloons()
            st.success("✅ 預約成功！請領取您的療癒卡片：")
            pytime.sleep(0.5)
            st.markdown(f"<div class='tarot-container'><div class='tarot-card {drawn['e']}'><div class='tarot-icon'>{drawn['i']}</div><h3>{drawn['t']}</h3><p>{drawn['d']}</p><small>— 癒室 · 打雜小妹親筆指引</small></div></div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ 姓名電話或數量都要填寫完整喔！")
st.markdown('</div>', unsafe_allow_html=True)