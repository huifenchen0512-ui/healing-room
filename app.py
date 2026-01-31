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
    .stApp { background-color: #FAF9F6; }
    h1, h2, h3 { color: #2D463E !important; font-family: 'Noto Serif TC', serif; }
    .custom-card {
        background-color: #ffffff; padding: 2rem; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(45, 70, 62, 0.05); border: 1px solid #E9E4D9; margin-bottom: 1.5rem;
    }
    .announcement-box {
        background: linear-gradient(135deg, #FDF5E6 0%, #FAF3E0 100%);
        border-left: 6px solid #A67B5B; padding: 1.2rem; border-radius: 12px; margin-bottom: 1.5rem;
    }
    .stButton>button { 
        background-color: #2D463E; color: #FAF9F6; width: 100%; border-radius: 12px; 
        height: 3.8em; font-weight: 700; border: none; font-size: 1.1em; transition: 0.4s;
    }
    .stButton>button:hover { background-color: #A67B5B; transform: translateY(-2px); }
    
    /* 塔羅 3D 翻牌動畫 */
    @keyframes flipInY {
      from { transform: perspective(400px) rotateY(90deg); opacity: 0; }
      to { transform: perspective(400px) rotateY(0deg); opacity: 1; }
    }
    .tarot-container { display: flex; justify-content: center; margin-top: 2rem; }
    .tarot-card {
        width: 300px; padding: 25px; border-radius: 20px; text-align: center; color: #2D463E;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1); border: 3px solid #A67B5B;
        animation: flipInY 1.2s cubic-bezier(0.23, 1, 0.32, 1) forwards; background: white;
    }
    .tarot-icon { font-size: 3.5rem; margin-bottom: 10px; }
    .fire { border-color: #E57373; background: #FFF5F5; }
    .water { border-color: #64B5F6; background: #F5F9FF; }
    .air { border-color: #FFD54F; background: #FFFDF5; }
    .earth { border-color: #81C784; background: #F7FFF7; }
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

# ==================== 3. 打雜小妹管理看板 (密碼鎖與調度) ====================
with st.sidebar:
    st.markdown("## 🍂 癒室管理")
    admin_key = st.text_input("打雜小妹通關密碼", type="password")
    
    if admin_key == "0512":
        st.success("辛苦了！小妹驗證通過 ✨")
        ratio_choice = st.radio("本日產能配置", ["核桃 3 / 葡萄 15", "核桃 6 / 葡萄 12"])
        ratios = {"核桃 3 / 葡萄 15": (15, 3), "核桃 6 / 葡萄 12": (12, 6)}
        max_g, max_w = ratios[ratio_choice]
        prod_dates = [d.strip() for d in st.text_area("製作日期設定", "2026-02-07\n2026-02-12\n2026-02-13").split('\n') if d.strip()]
        st.session_state['admin_config'] = {"max_g": max_g, "max_w": max_w, "prod_dates": prod_dates}
        
        st.markdown("---")
        st.subheader("📋 營運看板")
        v_date = st.selectbox("選擇日期", prod_dates)
        daily_df = df_existing[df_existing['面交日期'].str.contains(v_date, na=False)]
        if not daily_df.empty:
            st.metric("總訂單數", f"{len(daily_df)} 筆")
            download_df = daily_df.copy()
            download_df['聯絡電話'] = "'" + download_df['聯絡電話'].astype(str)
            st.download_button("📥 下載清單", download_df.to_csv(index=False).encode('utf-8-sig'), f"癒室出貨_{v_date}.csv")
    else:
        st.caption("🔒 內部管理專用 (密碼為生日)")
        max_g, max_w, prod_dates = 15, 3, ["2026-02-07", "2026-02-12", "2026-02-13"]

# ==================== 4. 主頁面：公告與查詢 ====================
st.title("🍂 癒室 · Healing Room")
st.markdown("##### *Handmade Cinnamon Rolls & Soul Healing*")

st.markdown(f"""
<div class="announcement-box">
    <strong>📢 2 月打雜小妹接單快訊</strong><br>
    <small>
    • 2/7 梯次：2/7 三重 (19:00+) / 2/8 華視 (11:00-17:00)<br>
    • 2/12 & 2/13 梯次：僅開放三重自取 (19:00+)<br>
    ※ 慢火焦糖均一價 $190 每盒。
    </small>
</div>
""", unsafe_allow_html=True)

with st.expander("🔍 預約查詢：輸入電話找回您的訂單資訊"):
    search_p = st.text_input("聯絡電話")
    if search_p:
        clean_s = search_p.replace("'", "")
        my_row = df_existing[df_existing['聯絡電話'] == clean_s].tail(1)
        if not my_row.empty:
            st.success(f"Hi {my_row.iloc[0]['客戶姓名']}，找到囉！")
            st.info(f"📍 安排：{my_row.iloc[0]['面交日期']} {my_row.iloc[0]['面交時間']} 於 {my_row.iloc[0]['面交地點']}")
            st.write(f"🥐 口味：葡萄 {my_row.iloc[0]['經典數量']} 盒 / 核桃 {my_row.iloc[0]['核桃數量']} 盒")
        else:
            st.warning("查無紀錄，請確認電話號碼（例：09...）是否正確。")

# ==================== 5. 下單區卡片排版 ====================
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.image("548282507_1196129685655556_143484642680713398_n.jpg", caption="手工慢火熬煮焦糖，包裹著打雜小妹的靈魂。", use_container_width=True)
    st.subheader("📝 預約資訊")
    c_name = st.text_input("您的稱呼")
    c_phone = st.text_input("聯絡電話", placeholder="例：0912345678", key="main_phone_16")
    t_date = st.selectbox("選擇日期", prod_dates)
    
    n_day_calc = (datetime.strptime(t_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    batch_d = df_existing[df_existing['面交日期'].isin([t_date, n_day_calc])]
    u_g = pd.to_numeric(batch_d['經典數量']).sum()
    u_w = pd.to_numeric(batch_d['核桃數量']).sum()
    rem_g, rem_w = int(max(0, max_g - u_g)), int(max(0, max_w - u_w))

    pickup_opts = ["2026-02-07 三重 (19:00+)", "2026-02-08 華視 (11:00-17:00)"] if t_date == "2026-02-07" else [f"{t_date} 三重 (19:00+)"]
    loc_opt = st.selectbox("面交安排", pickup_opts)
    p_time = st.time_input("預計時間", value=time(19, 0) if "三重" in loc_opt else time(12, 0))
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🥐 產能進度")
    st.write(f"**蘭姆葡萄** (剩 {rem_g} 盒)")
    st.progress(min(1.0, u_g / max_g if max_g > 0 else 1))
    q_g = st.number_input("購買經典 (盒)", min_value=0, max_value=rem_g, step=1, key="q_g_16")
    st.write(f"**純焦糖核桃** (剩 {rem_w} 盒)")
    st.progress(min(1.0, u_w / max_w if max_w > 0 else 1))
    q_w = st.number_input("購買純核桃 (盒)", min_value=0, max_value=rem_w, step=1, key="q_w_16")
    st.markdown(f"### 💰 總額：NT$ {(q_g + q_w) * 190}")
    pay_method = st.radio("付款管道", ["面交", "轉帳", "Line Pay"], horizontal=True)
    pay_info = st.text_input("付款資訊 (後五碼等)") if pay_method != "面交" else "現場支付"
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== 6. 提交與 22 張大阿爾克那完整牌組 ====================
st.divider()
if st.button("✨ 送出預約，並領取今日療癒指引 ✨"):
    if c_name and c_phone and (q_g + q_w) > 0:
        with st.spinner("打雜小妹洗牌中..."):
            # 電話號碼補 0 修復
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
            
            # 【完整 22 張大阿爾克那】指引內容
            tarot_deck = [
                {"e": "air", "i": "🃏", "t": "0 愚者", "d": "新冒險的開始，打雜小妹為您的純真與勇氣喝采！"},
                {"e": "fire", "i": "🪄", "t": "I 魔術師", "d": "您擁有一切創造美好生活的素材，現在就開始動手吧！"},
                {"e": "water", "i": "📜", "t": "II 女教皇", "d": "靜心傾聽內在，智慧會在最平靜的時刻顯現。"},
                {"e": "earth", "i": "👑", "t": "III 女皇", "d": "今日適合被美好與豐盛包圍，盡情享受這份甜蜜。"},
                {"e": "fire", "i": "🏛️", "t": "IV 皇帝", "d": "穩定與掌控，您就是自己生活的主導者。"},
                {"e": "earth", "i": "🙏", "t": "V 教皇", "d": "智慧藏於傳統與規則之中，聽從經驗的引導。"},
                {"e": "air", "i": "💞", "t": "VI 戀人", "d": "美好的連結正悄悄發生，請跟隨您的心做選擇。"},
                {"e": "fire", "i": "🛒", "t": "VII 戰車", "d": "衝勁十足！今日無人能擋，目標就在前方。"},
                {"e": "fire", "i": "🦁", "t": "VIII 力量", "d": "溫柔的堅韌勝過剛硬，用愛平定生活中的喧囂。"},
                {"e": "earth", "i": "💡", "t": "IX 隱者", "d": "獨處是靈魂的休息，在安靜中找回真實的自己。"},
                {"e": "fire", "i": "🎡", "t": "X 命運之輪", "d": "轉機已至，好運正隨著肉桂香氣轉動而來。"},
                {"e": "air", "i": "⚖️", "t": "XI 正義", "d": "公平與對稱，找回生活的核心平衡。"},
                {"e": "water", "i": "🙃", "t": "XII 倒吊人", "d": "換個視角看世界，難題會展現出意想不到的出口。"},
                {"e": "water", "i": "🦋", "t": "XIII 死神", "d": "告別舊節奏，新篇章的勇氣就在您的手心中。"},
                {"e": "fire", "i": "🏺", "t": "XIV 節制", "d": "精準的比例與融合，就像焦糖與核桃的完美結合。"},
                {"e": "earth", "i": "😈", "t": "XV 惡魔", "d": "偶爾耽溺於甜點的誘惑，是為了儲備下次出發的動力。"},
                {"e": "fire", "i": "⚡", "t": "XVI 高塔", "d": "突破性的重組，是為了建立更穩固的藍圖。"},
                {"e": "air", "i": "⭐", "t": "XVII 星星", "d": "希望的星光指引，願望正隨著肉桂香氣慢慢熟成。"},
                {"e": "water", "i": "🌙", "t": "XVIII 月亮", "d": "擁抱潛意識的不安，星光終會指引明晨的路。"},
                {"e": "fire", "i": "☀️", "t": "XIX 太陽", "d": "充滿活力的明亮光芒，今日是一切美好的圓滿。"},
                {"e": "fire", "i": "🎺", "t": "XX 審判", "d": "聽從內心的呼喚，再次覺醒與啟航。"},
                {"e": "earth", "i": "🌍", "t": "XXI 世界", "d": "圓滿的達成，給辛苦生活的您一份應得的犒賞。"}
            ]
            drawn = random.choice(tarot_deck)
            st.balloons()
            st.success("✅ 預約成功！打雜小妹立刻去準備。")
            pytime.sleep(0.5)
            st.markdown(f"<div class='tarot-container'><div class='tarot-card {drawn['e']}'><div class='tarot-icon'>{drawn['i']}</div><div style='font-size:1.4rem;font-weight:700;margin-bottom:10px'>{drawn['t']}</div><p>{drawn['d']}</p><small style='color:#A67B5B'>— 打雜小妹親筆指引</small></div></div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ 資料填寫不完整喔！")