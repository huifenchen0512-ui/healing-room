# --- 側邊欄：主理人管理區 (新增密碼鎖) ---
with st.sidebar:
    st.header("🍂 癒室 管理入口")
    admin_password = st.text_input("請輸入管理密碼", type="password")
    
    # 只有密碼正確 (假設密碼是 0512) 才會顯示後台調度
    if admin_password == "0512":
        st.success("身分驗證成功，主理人您好")
        st.markdown("---")
        st.header("🍂 癒室 後台調度")
        
        # 這裡放原本的產能設定與日期設定程式碼...
        ratio_choice = st.radio("今日生產配比", ["均衡生產 (各 9 盒)", ...])
        # (以此類推)
        
    else:
        st.info("💡 此區塊為「癒室」主理人專用。")
        st.caption("客人請直接在右側表單選擇現有梯次下單即可。")
        
        # 如果沒輸密碼，我們給系統一個「預設值」，確保右側表單不會出錯
        max_g, max_w = 9, 9
        prod_dates = ["2026-02-10", "2026-02-17"] # 這裡可以寫死你目前的固定日期