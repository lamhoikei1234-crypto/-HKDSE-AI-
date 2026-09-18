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

# 4. 圖片上傳區塊（可選）
uploaded_file = st.file_uploader("📷 上傳錯題圖片（可選，支援 PNG, JPG, JPEG）", type=["png", "jpg", "jpeg"])

img = None
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="目前附帶的題目圖片", use_container_width=True)

# 5. 渲染歷史對話紀錄
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"] is not None:
            st.image(message["image"], use_container_width=True)
        st.markdown(message["content"])

# 6. 對話輸入框
if prompt := st.chat_input("請輸入錯題內容、疑問，或針對圖片發問..."):
    # 準備本次訊息內容
    message_data = {"role": "user", "content": prompt}
    if img:
        message_data["image"] = img

    # 紀錄並顯示使用者訊息
    st.session_state.messages.append(message_data)
    with st.chat_message("user"):
        if img:
            st.image(img, use_container_width=True)
        st.markdown(prompt)

    # 呼叫 AI 進行分析與對話
    with st.chat_message("assistant"):
        with st.spinner("AI 導師正在分析中..."):
            try:
                system_instruction = (
                    "你是一位精通香港 HKDSE 課程與考評局 (HKEAA) 評分標準的 AI 錯題分析導師。"
                    "請針對使用者提供的錯題圖片或疑問進行詳細剖析，指出常見陷阱、關鍵得分點 (Marking Points) 及正確解題步驟：\n\n"
                )
                
                inputs = [system_instruction + prompt]
                if img:
                    inputs.append(img)
                
                response = model.generate_content(inputs)
                reply_text = response.text
                
                st.markdown(reply_text)
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
            except Exception as e:
                st.error(f"分析失敗，錯誤訊息：{str(e)}")

