import streamlit as st
import pandas as pd
import random
import time as pytime
from datetime import datetime, timedelta, time
from streamlit_gsheets import GSheetsConnection

# ==================== 1. 精緻視覺 CSS ====================
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

# ==================== 2. 雲端連線與資料庫 ====================
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db_data():
    try:
        return conn.read(worksheet="癒室訂單紀錄", ttl=0)
    except:
        return pd.DataFrame(columns=["下單時間", "客戶姓名", "聯絡電話", "面交日期", "面交地點", "面交時間", "經典數量", "核桃數量", "總金額", "付款方式", "付款資訊"])

df_existing = get_db_data()

# ==================== 3. 側邊欄：打雜小妹管理看板 (密碼鎖與調度) ====================
with st.sidebar:
    st.markdown("## 🍂 癒室打雜小妹後台")
    admin_key = st.text_input("輸入小妹通關密碼", type="password")
    
    if admin_key == "0512":
        st.success("驗證成功！打雜小妹辛苦了 ✨")
        st.markdown("---")
        st.subheader("🥐 產能配置")
        ratio_choice = st.radio("本日比例設定", ["核桃 3 / 葡萄 15", "核桃 6 / 葡萄 12"])
        ratios = {"核桃 3 / 葡萄 15": (15, 3), "核桃 6 / 葡萄 12": (12, 6)}
        max_g, max_w = ratios[ratio_choice]
        
        st.subheader("📅 日期調整")
        date_input = st.text_area("製作梯次 (YYYY-MM-DD)", "2026-02-07\n2026-02-12\n2026-02-13")
        prod_dates = [d.strip() for d in date_input.split('\n') if d.strip()]
        st.session_state['admin_config'] = {"max_g": max_g, "max_w": max_w, "prod_dates": prod_dates}
        
        st.markdown("---")
        st.subheader("📋 營運看板")
        view_d = st.selectbox("查看單日數據", prod_dates)
        next_v = (datetime.strptime(view_d, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        daily_q = df_existing[df_existing['面交日期'].isin([view_d, next_v])]
        
        if not daily_q.empty:
            st.metric("總訂單數", f"{len(daily_q)} 筆")
            st.write(f"🥐 葡萄總計：{pd.to_numeric(daily_q['經典數量']).sum()} 盒")
            st.write(f"🥜 核桃總計：{pd.to_numeric(daily_q['核桃數量']).sum()} 盒")
            st.download_button("📥 下載出貨清單", daily_q.to_csv(index=False).encode('utf-8-sig'), f"癒室出貨_{view_d}.csv")
        else:
            st.info("該日期尚無訂單")
    else:
        st.caption("🔒 內部管理區 (密碼為生日)")
        max_g, max_w, prod_dates = 15, 3, ["2026-02-07", "2026-02-12", "2026-02-13"]

# ==================== 4. 主頁面：公告與查詢功能 ====================
st.title("🍂 癒室 · Healing Room")
st.markdown("##### *Handmade Cinnamon Rolls & Soul Healing*")

st.markdown(f"""
<div class="announcement-box">
    <strong>📢 2 月打雜小妹接單公告</strong><br>
    <small>
    • 2/7 梯次：2/7 三重 (19:00+) / 2/8 華視 (11:00-17:00)<br>
    • 2/12 & 2/13 梯次：僅開放三重自取 (19:00+)<br>
    ※ 均一價 $190 盒。
    </small>
</div>
""", unsafe_allow_html=True)

# --- 客人查詢功能區 ---
with st.expander("🔍 預約查詢：忘記訂了什麼？輸入電話查詢"):
    search_p = st.text_input("請輸入您的聯絡電話")
    if search_p:
        # 撈出最後一筆紀錄
        my_row = df_existing[df_existing['聯絡電話'] == search_p].tail(1)
        if not my_row.empty:
            st.success(f"Hi {my_row.iloc[0]['客戶姓名']}，打雜小妹幫您找到最近一筆紀錄囉！")
            st.info(f"📍 領取安排：{my_row.iloc[0]['面交日期']} {my_row.iloc[0]['面交時間']} 在 {my_row.iloc[0]['面交地點']}")
            st.write(f"🥐 訂購口味：經典葡萄 {my_row.iloc[0]['經典數量']} 盒 / 純核桃 {my_row.iloc[0]['核桃數量']} 盒")
        else:
            st.warning("查無紀錄，請確認電話號碼是否正確喔！")

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.image("548282507_1196129685655556_143484642680713398_n.jpg", caption="手工慢火熬煮焦糖，包裹著靈魂的滋味。", use_container_width=True)
    st.subheader("📝 預約資訊")
    c_name = st.text_input("您的稱呼")
    c_phone = st.text_input("聯絡電話", key="main_phone")
    t_date = st.selectbox("選擇製作日期", prod_dates)
    
    # 即時庫存計算
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
    q_g = st.number_input("購買經典款", min_value=0, max_value=rem_g, step=1, key="q_g_14")
    
    st.write(f"**純焦糖核桃** (剩 {rem_w} 盒)")
    st.progress(min(1.0, u_w / max_w if max_w > 0 else 1))
    q_w = st.number_input("購買純核桃 ", min_value=0, max_value=rem_w, step=1, key="q_w_14")
    
    st.markdown(f"### 💰 總額：NT$ {(q_g + q_w) * 190}")
    pay_method = st.radio("付款管道", ["面交", "轉帳", "Line Pay"], horizontal=True)
    pay_info = st.text_input("付款資訊 (後五碼等)") if pay_method != "面交" else "現場支付"
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== 5. 提交與 22 張塔羅完整牌組 ====================
st.divider()
if st.button("✨ 送出預約，並領取今日療癒指引 ✨"):
    if c_name and c_phone and (q_g + q_w) > 0:
        with st.spinner("打雜小妹洗牌中..."):
            new_row = pd.DataFrame([{
                "下單時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "客戶姓名": c_name, "聯絡電話": c_phone,
                "面交日期": loc_opt.split(' ')[0], "面交地點": "三重" if "三重" in loc_opt else "華視",
                "面交時間": p_time.strftime("%H:%M"),
                "經典數量": q_g, "核桃數量": q_w, "總金額": (q_g + q_w) * 190,
                "付款方式": pay_method, "付款資訊": pay_info
            }])
            conn.update(worksheet="癒室訂單紀錄", data=pd.concat([df_existing, new_row], ignore_index=True))
            
            # 完整 22 張大阿爾克那
            tarot_deck = [
                {"e": "air", "i": "🃏", "t": "愚者", "d": "新冒險的開始，打雜小妹為您的熱情鼓掌！"},
                {"e": "fire", "i": "🪄", "t": "魔術師", "d": "您手握創造生活的權限。"},
                {"e": "water", "i": "📜", "t": "女教皇", "d": "相信您的直覺。"},
                {"e": "earth", "i": "👑", "t": "女皇", "d": "享受豐盛美滿的當下。"},
                {"e": "fire", "i": "🏛️", "t": "皇帝", "d": "掌控節奏，主導生活。"},
                {"e": "earth", "i": "🙏", "t": "教皇", "d": "智慧藏於傳統之中。"},
                {"e": "air", "i": "💞", "t": "戀人", "d": "美好的連結，心動的選擇。"},
                {"e": "fire", "i": "🛒", "t": "戰車", "d": "衝勁十足！今日無人能擋。"},
                {"e": "fire", "i": "🦁", "t": "力量", "d": "溫柔的堅韌，平定喧囂。"},
                {"e": "earth", "i": "💡", "t": "隱者", "d": "在靜謐中找回自己。"},
                {"e": "fire", "i": "🎡", "t": "命運之輪", "d": "轉動契機已至。"},
                {"e": "air", "i": "⚖️", "t": "正義", "d": "找回核心的平衡。"},
                {"e": "water", "i": "🙃", "t": "倒吊人", "d": "換個視角，難題變輕快。"},
                {"e": "water", "i": "🦋", "t": "死神", "d": "告別舊節奏，迎接新篇章。"},
                {"e": "fire", "i": "🏺", "t": "節制", "d": "完美的融合與平衡。"},
                {"e": "earth", "i": "😈", "t": "惡魔", "d": "偶爾的耽溺是健康的誘惑。"},
                {"e": "fire", "i": "⚡", "t": "高塔", "d": "突破性的改變，更好的未來。"},
                {"e": "air", "i": "⭐", "t": "星星", "d": "希望指引，願望正熟成。"},
                {"e": "water", "i": "🌙", "t": "月亮", "d": "擁抱不安，晨曦將至。"},
                {"e": "fire", "i": "☀️", "t": "太陽", "d": "明亮陽光，今日圓滿。"},
                {"e": "fire", "i": "🎺", "t": "審判", "d": "聽從內心召喚，再次啟航。"},
                {"e": "earth", "i": "🌍", "t": "世界", "d": "圓滿達成，最好的犒賞。"}
            ]
            drawn = random.choice(tarot_deck)
            st.balloons()
            st.success("✅ 預約成功！請領取今日指引：")
            pytime.sleep(0.5)
            st.markdown(f"<div class='tarot-container'><div class='tarot-card {drawn['e']}'><div class='tarot-icon'>{drawn['i']}</div><h3>{drawn['t']}</h3><p>{drawn['d']}</p><small>— 打雜小妹親筆指引</small></div></div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ 姓名電話或數量都要填好喔！")