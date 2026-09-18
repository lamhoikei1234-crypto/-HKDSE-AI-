import os
import google.generativeai as genai
import streamlit as st
from PIL import Image

# 1. 頁面基本設定
st.set_page_config(
    page_title="HKDSE 錯題 AI 分析助手",
    page_icon="📝",
import os
import google.generativeai as genai
import streamlit as st
from PIL import Image

# 1. 頁面基本設定
st.set_page_config(
    page_title="HKDSE 錯題 AI 分析助手",
    page_icon="📝",
    layout="centered"
)

st.title("📝 HKDSE 錯題 AI 分析助手")
st.write("歡迎使用！請上傳錯題圖片或輸入題目內容進行分析。")

# 2. 安全讀取 API Key
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.error("⚠️ 未偵測到 API 金鑰！請於 Streamlit Cloud 的 Settings -> Secrets 設定 GEMINI_API_KEY。")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# 3. 初始化對話紀錄與圖片狀態
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 功能區塊 1: 圖片上傳與分析 ---
with st.container(border=True):
    st.subheader("📷 錯題圖片上傳分析")
    
    # 這是最核心的「圖片上傳功能」按鈕，會顯示在畫面上方
    uploaded_file = st.file_uploader(
        "選擇或拍照上傳錯題圖片", 
        type=["png", "jpg", "jpeg"],
        key="uploader"
    )

    col1, col2 = st.columns([2, 1])
    
    with col1:
        img = None
        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            st.image(img, caption="已上傳待分析的圖片", use_container_width=True)

    with col2:
        # 單獨圖片分析的按鈕
        image_analysis_btn = st.button("🚀 開始分析上傳的圖片", type="primary")

    # 處理圖片分析按鈕點擊
    if image_analysis_btn:
        if uploaded_file is not None:
            # 準備圖片分析對話紀錄
            message_data = {"role": "user", "content": "這是上傳的錯題圖片，請分析此題目", "image": img}
            st.session_state.messages.append(message_data)
            
            with st.spinner("AI 導師正在深度分析圖片題目中..."):
                try:
                    system_instruction = (
                        "你是一位精通香港 HKDSE 課程與考評局 (HKEAA) 評分標準的 AI 錯題分析導師。"
                        "請針對使用者提供的錯題圖片進行詳細剖析，指出常見陷阱、關鍵得分點 (Marking Points) 及正確解題步驟：\n\n"
                    )
                    inputs = [system_instruction + "這是上傳的錯題圖片，請分析此題目", img]
                    
                    response = model.generate_content(inputs)
                    reply_text = response.text
                    
                    # 紀錄 AI 回答
                    st.session_state.messages.append({"role": "assistant", "content": reply_text})
                except Exception as e:
                    st.error(f"分析失敗，錯誤訊息：{str(e)}")
        else:
            st.warning("請先選擇要上傳的題目圖片！")

# --- 功能區塊 2: 聊天對話框 ---
with st.container():
    st.subheader("💬 文字分析與後續追問聊天室")

    # 渲染歷史對話紀錄
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "image" in message and message["image"] is not None:
                st.image(message["image"], use_container_width=True)
            st.markdown(message["content"])

    # 處理純文字輸入框（與圖片分開）
    if prompt := st.chat_input("輸入題目文字，或針對已上傳的圖片發問..."):
        # 紀錄使用者文字訊息
        message_data = {"role": "user", "content": prompt}
        st.session_state.messages.append(message_data)
        
        # 呼叫 AI 進行文字對話
        with st.chat_message("assistant"):
            with st.spinner("AI 導師正在分析文字問題..."):
                try:
                    system_instruction = (
                        "你是一位精通香港 HKDSE 課程與考評局 (HKEAA) 評分標準的 AI 錯題分析導師。"
                        "請針對使用者提供的問題或文字進行詳細剖析，指出常見陷阱、關鍵得分點 (Marking Points) 及正確解題步驟：\n\n"
                    )
                    inputs = [system_instruction + prompt]
                    response = model.generate_content(inputs)
                    reply_text = response.text
                    
                    # 紀錄 AI 回答
                    st.session_state.messages.append({"role": "assistant", "content": reply_text})
                except Exception as e:
                    st.error(f"分析失敗，錯誤訊息：{str(e)}")

