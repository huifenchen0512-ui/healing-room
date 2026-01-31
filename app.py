"""
癒室 - 手工甜點
Healing Room Handmade
肉桂捲接單系統 · 地點與時間嚴格對應 · 多元付款
"""

import streamlit as st
import random
import re
from datetime import date, datetime, timedelta, time
from typing import List, Dict, Any, Tuple

# ==================== 常數 ====================

TOTAL_BOXES_PER_RUN = 18  # 每次製作 3 盤 = 18 盒
PRICE_PER_BOX = 190

# 地點與製作日對應規則
LOCATION_SANCHONG = "三重彰化銀行"  # 製作當日 · 方案 A
LOCATION_HUASHI = "華視大樓 (警衛室旁面交)"  # 製作隔日 · 方案 B

# 時間限制：方案 A 三重 19:00 以後；方案 B 華視 11:00–19:00
TIME_SANCHONG_MIN = time(19, 0)   # 三重：僅限 19:00 以後
TIME_HUASHI_MIN = time(11, 0)     # 華視：11:00 至 19:00
TIME_HUASHI_MAX = time(19, 0)

# 產品
PRODUCT_GRAPE = "經典款-蘭姆葡萄核桃肉桂捲 (2入/盒)"
PRODUCT_WALNUT = "純核桃焦糖肉桂捲 (2入/盒)"

# 生產配比：(經典, 核桃)
PRODUCTION_RATIOS = {
    "均衡生產 (各 9 盒)": (9, 9),
    "經典為主 (葡萄 12 / 核桃 6)": (12, 6),
    "核桃為主 (葡萄 6 / 核桃 12)": (6, 12),
}

# 付款方式
PAYMENT_FACE = "面交"
PAYMENT_TRANSFER = "轉帳"
PAYMENT_LINEPAY = "Line Pay"

# 銀行帳號資訊（請依實際情況修改）
BANK_INFO = {
    "銀行名稱": "彰化銀行",
    "分行": "三重分行",
    "帳號": "（請於程式內修改為您的帳號）",
    "戶名": "（請於程式內修改為您的戶名）",
}

# Line Pay QR Code 圖片路徑（可設為 "" 若無圖片）
LINE_PAY_QR_PATH = ""  # 例: "images/linepay_qr.png"

# 癒室能量塔羅牌 · 2026 專屬
TAROT_CARDS = [
    {"name": "力量", "emoji": "🦁", "message": "2026 專屬能量：你的內在力量將引領你突破困境，如同肉桂的溫暖層層包裹。"},
    {"name": "皇后", "emoji": "👑", "message": "2026 專屬能量：豐饒與慷慨，願這份甜點為你帶來一整年的豐盛。"},
    {"name": "太陽", "emoji": "☀️", "message": "2026 專屬能量：光芒四射的一年，每一口都是陽光的滋味。"},
    {"name": "星星", "emoji": "⭐", "message": "2026 專屬能量：希望之星照亮前路，願美好如期而至。"},
    {"name": "世界", "emoji": "🌍", "message": "2026 專屬能量：圓滿的風味，象徵生命的美好循環。"},
    {"name": "戀人", "emoji": "💕", "message": "2026 專屬能量：與摯愛分享，甜蜜加倍，幸福滿溢。"},
    {"name": "愚者", "emoji": "🎭", "message": "2026 專屬能量：敞開心扉，迎接這份意外的甜美與驚喜。"},
    {"name": "魔術師", "emoji": "✨", "message": "2026 專屬能量：平凡食材的魔法，創造 2026 不凡的幸福。"},
]

# 塔羅牌圖片（維基百科 Rider-Waite）
TAROT_IMAGES = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/RWS_Tarot_08_Strength.jpg/200px-RWS_Tarot_08_Strength.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/RWS_Tarot_03_Empress.jpg/200px-RWS_Tarot_03_Empress.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/RWS_Tarot_19_Sun.jpg/200px-RWS_Tarot_19_Sun.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/RWS_Tarot_17_Star.jpg/200px-RWS_Tarot_17_Star.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/RWS_Tarot_21_World.jpg/200px-RWS_Tarot_21_World.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/TheLovers.jpg/200px-TheLovers.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/RWS_Tarot_00_Fool.jpg/200px-RWS_Tarot_00_Fool.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/RWS_Tarot_01_Magician.jpg/200px-RWS_Tarot_01_Magician.jpg",
]

# ==================== 核心邏輯 ====================


def init_session_state():
    if "orders" not in st.session_state:
        st.session_state.orders = []
    if "production_dates" not in st.session_state:
        st.session_state.production_dates = []
    if "production_ratio" not in st.session_state:
        st.session_state.production_ratio = "均衡生產 (各 9 盒)"


def parse_production_dates(text: str) -> List[date]:
    """解析製作日期清單"""
    if not text or not text.strip():
        return []
    results = []
    parts = re.split(r"[\n,，、;；\s]+", text.strip())
    for part in (p.strip() for p in parts if p.strip()):
        if not part:
            continue
        try:
            if re.match(r"\d{4}-\d{1,2}-\d{1,2}", part):
                d = datetime.strptime(part[:10], "%Y-%m-%d").date()
            elif re.match(r"\d{1,2}/\d{1,2}", part):
                year = date.today().year
                m, day = map(int, re.split(r"/", part)[:2])
                d = date(year, m, day)
            else:
                continue
            if d not in results:
                results.append(d)
        except (ValueError, IndexError):
            continue
    return sorted(results)


def build_pickup_options(production_dates: List[date]) -> List[Tuple[date, str, date]]:
    """
    根據製作日期生成兩大方案。
    回傳 [(面交日期, 地點, 製作日期), ...]
    - 方案 A：製作當日 - 三重，時間限 19:00 以後
    - 方案 B：製作隔日 - 華視，時間限 11:00–19:00
    """
    options = []
    for prod_date in production_dates:
        options.append((prod_date, LOCATION_SANCHONG, prod_date))
        options.append((prod_date + timedelta(days=1), LOCATION_HUASHI, prod_date))
    return options


def get_time_hint(location: str) -> str:
    """取得該地點的時段說明"""
    if location == LOCATION_SANCHONG:
        return "⏰ 三重：僅限 19:00 以後"
    if location == LOCATION_HUASHI:
        return "⏰ 華視：僅限 11:00 至 19:00"
    return ""


def get_default_time_for_location(location: str) -> time:
    """依地點回傳預設面交時間"""
    if location == LOCATION_SANCHONG:
        return time(19, 0)
    if location == LOCATION_HUASHI:
        return time(12, 0)  # 中午
    return time(12, 0)


def validate_pickup_time(location: str, t: time) -> Tuple[bool, str]:
    """
    驗證面交時間是否符合地點限制。
    回傳 (是否有效, 錯誤訊息)
    """
    if location == LOCATION_SANCHONG:
        if t < TIME_SANCHONG_MIN:
            return False, "三重面交僅限 19:00 以後，請重新選擇時間。"
    elif location == LOCATION_HUASHI:
        if t < TIME_HUASHI_MIN:
            return False, "華視面交僅限 11:00 至 19:00，請重新選擇時間。"
        if t > TIME_HUASHI_MAX:
            return False, "華視面交僅限 11:00 至 19:00，請重新選擇時間。"
    return True, ""


def get_orders_for_production(prod_date: date) -> List[Dict]:
    """取得指定製作日期的所有訂單（當天三重 + 隔天華視，共用該梯次庫存）"""
    prod_str = prod_date.isoformat()
    next_str = (prod_date + timedelta(days=1)).isoformat()
    return [
        o
        for o in st.session_state.orders
        if (o.get("面交日期") == prod_str and o.get("地點") == LOCATION_SANCHONG)
        or (o.get("面交日期") == next_str and o.get("地點") == LOCATION_HUASHI)
    ]


def get_remaining_quota_for_production(prod_date: date) -> Tuple[int, int]:
    """取得指定製作日的經典/核桃剩餘名額"""
    grape_max, walnut_max = PRODUCTION_RATIOS.get(
        st.session_state.production_ratio, (9, 9)
    )
    orders = get_orders_for_production(prod_date)
    grape_used = sum(o.get("經典數量", 0) for o in orders)
    walnut_used = sum(o.get("核桃數量", 0) for o in orders)
    return (
        max(0, grape_max - grape_used),
        max(0, walnut_max - walnut_used),
    )


# ==================== 木質調 CSS ====================

WOOD_CSS = """
<style>
    :root {
        --wood-dark: #5D4E37;
        --wood-medium: #8B7355;
        --wood-light: #C4A574;
        --wood-cream: #F5E6D3;
        --wood-warm: #E8D5B7;
        --accent-cinnamon: #B8860B;
    }

    .stApp {
        background: linear-gradient(135deg, #F5E6D3 0%, #E8D5B7 50%, #F5E6D3 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #5D4E37 0%, #8B7355 100%) !important;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #F5E6D3 !important;
    }

    h1, h2, h3 {
        color: #5D4E37 !important;
        font-weight: 600 !important;
    }

    .product-card {
        background: linear-gradient(145deg, #FFFFFF 0%, #F5E6D3 100%);
        border: 2px solid #C4A574;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(93, 78, 55, 0.15);
        transition: transform 0.2s;
    }

    .product-card:hover {
        transform: translateY(-2px);
    }

    .spec-banner {
        background: linear-gradient(90deg, #8B7355 0%, #C4A574 100%);
        color: #F5E6D3;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 500;
        margin: 1rem 0;
    }

    .time-hint {
        background: #FFF8E7;
        border: 1px solid #C4A574;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        font-size: 0.9rem;
        color: #5D4E37;
        margin: 0.25rem 0;
    }

    .time-warning {
        background: #FFEBEE;
        border-left: 4px solid #E53935;
        padding: 0.5rem 0.75rem;
        border-radius: 0 6px 6px 0;
        font-size: 0.9rem;
        color: #5D4E37;
        margin: 0.25rem 0;
    }

    .tarot-box {
        background: linear-gradient(145deg, #5D4E37 0%, #8B7355 100%);
        color: #F5E6D3;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(93, 78, 55, 0.3);
    }

    .full-quota-msg {
        background: #FFEBEE;
        border-left: 4px solid #E53935;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: #5D4E37;
    }

    .payment-info-box {
        background: #FFF8E7;
        border: 1px solid #C4A574;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-size: 0.95rem;
        color: #5D4E37;
    }
</style>
"""


# ==================== 主程式 ====================


def main():
    st.set_page_config(
        page_title="癒室 - 手工甜點 (Healing Room Handmade)",
        page_icon="🍂",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(WOOD_CSS, unsafe_allow_html=True)
    init_session_state()

    # ========== 側邊欄 ==========
    with st.sidebar:
        st.markdown("### 🍂 癒室 後台設定")
        st.markdown("---")

        st.markdown("**📅 製作日期設定**")
        st.caption("輸入 3–4 個製作日，系統自動生成兩大方案")
        default_days = "\n".join(
            d.strftime("%Y-%m-%d") for d in st.session_state.production_dates
        ) or "2026-02-10\n2026-02-17\n2026-02-24\n2026-03-03"
        days_input = st.text_area(
            "輸入製作日期（每行一個或逗號分隔）",
            value=default_days,
            height=120,
            placeholder="例：2/10 或 2026-02-10",
            key="production_dates_input",
        )
        parsed = parse_production_dates(days_input)
        if parsed:
            st.session_state.production_dates = parsed
            st.caption(f"已設定 {len(parsed)} 個製作日")

            options = build_pickup_options(parsed)
            with st.expander("預覽面交方案"):
                st.caption("方案 A：製作當日 · 三重 · 19:00 以後")
                st.caption("方案 B：製作隔日 · 華視 · 11:00–19:00")
                for pickup_d, loc, _ in options:
                    st.caption(f"• {pickup_d.strftime('%m/%d')} {loc}")
        else:
            st.caption("請輸入至少一個有效日期")

        st.markdown("---")
        st.markdown("**🥐 產能配置**")
        st.caption("每次製作上限 3 盤 (共 18 盒)")
        ratio_choice = st.radio(
            "選擇配比",
            options=list(PRODUCTION_RATIOS.keys()),
            key="ratio_radio",
            label_visibility="collapsed",
        )
        st.session_state.production_ratio = ratio_choice
        grape_q, walnut_q = PRODUCTION_RATIOS[ratio_choice]
        st.caption(f"葡萄 {grape_q} 盒 / 核桃 {walnut_q} 盒")

    # ========== 主頁標題 ==========
    st.markdown("# 🍂 癒室 - 手工甜點")
    st.markdown("**Healing Room Handmade · 溫暖手作肉桂捲**")
    st.markdown("---")

    st.markdown(
        '<div class="spec-banner">📦 每盒兩顆入，均一價 $190</div>',
        unsafe_allow_html=True,
    )

    # ========== 產品展示 ==========
    st.markdown("### 選擇產品")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown(
            """
            <div class="product-card">
                <h4>🥖 經典蘭姆葡萄 (2入/盒)</h4>
                <p>蘭姆酒漬葡萄與核桃的經典交織。</p>
                <p><strong>NT$ 190 / 盒</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="product-card">
                <h4>🌰 純核桃焦糖 (2入/盒)</h4>
                <p>焦糖與核桃的華麗搭配。</p>
                <p><strong>NT$ 190 / 盒</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown("")

    # ========== 下單表單 ==========
    st.markdown("### 📝 下單表單")

    production_dates = st.session_state.production_dates
    pickup_options = build_pickup_options(production_dates)
    has_options = len(pickup_options) > 0

    if not has_options:
        st.warning("請先在側邊欄設定製作日期，才能接受訂單。")

    with st.form("order_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            customer_name = st.text_input("客戶姓名", placeholder="請輸入姓名")
            customer_phone = st.text_input("聯絡電話", placeholder="例：0912-345-678")

            if has_options:
                option_labels = [
                    f"{p.strftime('%m/%d')} {loc}"
                    for p, loc, _ in pickup_options
                ]
                selected_idx = st.selectbox(
                    "面交日期與地點",
                    options=range(len(pickup_options)),
                    format_func=lambda i: option_labels[i],
                )
                pickup_date, pickup_location, prod_date = pickup_options[selected_idx]
            else:
                pickup_date = date.today()
                pickup_location = LOCATION_SANCHONG
                prod_date = date.today()

            default_time = get_default_time_for_location(pickup_location)
            pickup_time = st.time_input(
                "面交時間",
                value=default_time,
                key="pickup_time_input",
            )

            # 顯示時段限制提示
            hint = get_time_hint(pickup_location)
            st.markdown(
                f'<div class="time-hint">{hint}</div>',
                unsafe_allow_html=True,
            )

            # 即時檢查：若時間不符，顯示提醒
            time_ok, time_err = validate_pickup_time(pickup_location, pickup_time)
            if not time_ok:
                st.markdown(
                    f'<div class="time-warning">⚠️ {time_err}</div>',
                    unsafe_allow_html=True,
                )

            # ========== 付款方式 ==========
            st.markdown("**💳 付款方式**")
            payment_method = st.radio(
                "選擇付款方式",
                options=[PAYMENT_FACE, PAYMENT_TRANSFER, PAYMENT_LINEPAY],
                key="payment_radio",
                label_visibility="collapsed",
            )

            transfer_last5 = ""
            linepay_display_name = ""

            if payment_method == PAYMENT_FACE:
                st.markdown(
                    '<div class="payment-info-box">📍 請於約定時間抵達面交地點支付</div>',
                    unsafe_allow_html=True,
                )
            elif payment_method == PAYMENT_TRANSFER:
                st.markdown(
                    f'<div class="payment-info-box">'
                    f'<strong>銀行：</strong> {BANK_INFO["銀行名稱"]} {BANK_INFO["分行"]}<br>'
                    f'<strong>帳號：</strong> {BANK_INFO["帳號"]}<br>'
                    f'<strong>戶名：</strong> {BANK_INFO["戶名"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                transfer_last5 = st.text_input(
                    "轉帳帳號後五碼",
                    placeholder="請輸入轉帳帳號後五碼（5 位數字）",
                    max_chars=5,
                    key="transfer_last5",
                )
            elif payment_method == PAYMENT_LINEPAY:
                st.markdown(
                    '<div class="payment-info-box">📱 請掃描下方 QR Code 付款（或提供 Line ID）</div>',
                    unsafe_allow_html=True,
                )
                if LINE_PAY_QR_PATH:
                    try:
                        st.image(LINE_PAY_QR_PATH, caption="Line Pay QR Code", use_container_width=False, width=120)
                    except Exception:
                        st.caption("（Line Pay QR Code 圖片請放置於指定路徑）")
                else:
                    st.caption("（可於程式內設定 LINE_PAY_QR_PATH 顯示 QR Code）")
                linepay_display_name = st.text_input(
                    "Line Pay 顯示名稱",
                    placeholder="請輸入您的 Line Pay 顯示名稱",
                    key="linepay_name",
                )

        with col_b:
            grape_rem, walnut_rem = (
                get_remaining_quota_for_production(prod_date)
                if has_options
                else (9, 9)
            )

            st.markdown("**數量（可自由組合）**")
            qty_grape = st.number_input(
                "經典蘭姆葡萄 (盒)",
                min_value=0,
                max_value=grape_rem,
                value=0,
                step=1,
                key="qty_grape",
            )
            qty_walnut = st.number_input(
                "純核桃焦糖 (盒)",
                min_value=0,
                max_value=walnut_rem,
                value=0,
                step=1,
                key="qty_walnut",
            )

        total_boxes = qty_grape + qty_walnut

        # 依付款方式驗證必填欄位
        payment_valid = True
        payment_err = ""
        if payment_method == PAYMENT_TRANSFER:
            if not transfer_last5.strip() or len(transfer_last5) != 5 or not transfer_last5.isdigit():
                payment_valid = False
                payment_err = "請填寫正確的轉帳帳號後五碼（5 位數字）。"
        elif payment_method == PAYMENT_LINEPAY:
            if not linepay_display_name.strip():
                payment_valid = False
                payment_err = "請填寫 Line Pay 顯示名稱。"

        can_submit = (
            has_options
            and total_boxes >= 1
            and qty_grape <= grape_rem
            and qty_walnut <= walnut_rem
            and time_ok
            and payment_valid
        )

        if has_options:
            grape_r, walnut_r = get_remaining_quota_for_production(prod_date)
            if grape_r == 0 and walnut_r == 0:
                can_submit = False
                st.markdown(
                    '<div class="full-quota-msg">⚠️ 該梯次已滿額，請選擇其他日期。</div>',
                    unsafe_allow_html=True,
                )

        if not payment_valid:
            st.error(payment_err)

        submitted = st.form_submit_button("送出訂單", disabled=not can_submit)

        if submitted and can_submit:
            if not customer_name.strip():
                st.error("請填寫客戶姓名。")
            elif not customer_phone.strip():
                st.error("請填寫聯絡電話。")
            elif total_boxes < 1:
                st.error("請至少選擇一盒。")
            elif not time_ok:
                st.error(time_err)
            elif not payment_valid:
                st.error(payment_err)
            else:
                total_amount = (qty_grape + qty_walnut) * PRICE_PER_BOX
                items_desc = []
                if qty_grape > 0:
                    items_desc.append(f"{PRODUCT_GRAPE} x{qty_grape}")
                if qty_walnut > 0:
                    items_desc.append(f"{PRODUCT_WALNUT} x{qty_walnut}")

                order_record = {
                    "客戶": customer_name,
                    "電話": customer_phone,
                    "經典數量": qty_grape,
                    "核桃數量": qty_walnut,
                    "金額": total_amount,
                    "地點": pickup_location,
                    "面交日期": pickup_date.isoformat(),
                    "面交時間": pickup_time.strftime("%H:%M"),
                    "製作日期": prod_date.isoformat(),
                    "下單日期": date.today().isoformat(),
                    "付款方式": payment_method,
                }
                if payment_method == PAYMENT_TRANSFER:
                    order_record["轉帳後五碼"] = transfer_last5
                elif payment_method == PAYMENT_LINEPAY:
                    order_record["Line Pay 顯示名稱"] = linepay_display_name

                st.session_state.orders.append(order_record)

                st.balloons()
                st.success("✅ 訂單成立！感謝您的訂購。")

                idx = random.randint(0, len(TAROT_CARDS) - 1)
                card = TAROT_CARDS[idx]

                st.markdown(
                    f"""
                    <div class="tarot-box">
                        <p>🔮 癒室能量塔羅牌 · 2026 專屬</p>
                        <p><strong>{card['emoji']} {card['name']}牌</strong></p>
                        <p>{card['message']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                try:
                    st.image(
                        TAROT_IMAGES[idx],
                        caption=f"{card['name']}牌",
                        use_container_width=False,
                        width=150,
                    )
                except Exception:
                    st.caption("（塔羅牌圖片載入中，請稍候重新整理）")

                st.info(f"訂單金額：NT$ {total_amount}（{' + '.join(items_desc)}）")

    st.markdown("---")
    st.caption("癒室 - 手工甜點 · Healing Room Handmade · 溫暖手作")


if __name__ == "__main__":
    main()
