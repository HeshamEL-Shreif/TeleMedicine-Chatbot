from fastapi import FastAPI
import streamlit as st
import requests

# Custom CSS for clean white background and modern chat bubbles
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #fff !important;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .user-msg {
        background: linear-gradient(90deg, #b2f7ef 0%, #f6d365 100%);
        color: #222;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        max-width: 75%;
        align-self: flex-end;
        margin-left: auto;
        font-size: 1.08rem;
        box-shadow: 0 2px 8px rgba(178,247,239,0.08);
    }
    .bot-msg {
        background: linear-gradient(90deg, #e0eafc 0%, #cfdef3 100%);
        color: #222;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        max-width: 75%;
        align-self: flex-start;
        margin-right: auto;
        font-size: 1.08rem;
        box-shadow: 0 2px 8px rgba(207,222,243,0.08);
    }
    .colored-title {
        background: linear-gradient(90deg, #1e90ff 0%, #00c6ff 100%);
        color: #fff;
        padding: 20px 0 20px 0;
        border-radius: 14px;
        text-align: center;
        font-size: 2.3rem;
        font-weight: bold;
        margin-bottom: 28px;
        margin-top: 0;
        letter-spacing: 1px;
        box-shadow: 0 2px 8px rgba(30,144,255,0.10);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Colored title above white background
st.markdown('<div class="colored-title">TeleMedicine Chatbot</div>', unsafe_allow_html=True)

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history above input
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for sender, message in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f'<div class="user-msg">{message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">{message}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Chat input form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message...", key="form_input")
    submit = st.form_submit_button("Send")
    if submit and user_input:
        st.session_state.chat_history.append(("You", user_input))
        with st.spinner("Bot is typing..."):
            payload = {"query": user_input}
            response = requests.post("http://localhost:8000/query", json=payload)
            if response.status_code == 200:
                answer = response.json().get("answer", "No answer found.")
                st.session_state.chat_history.append(("Bot", answer))
            else:
                st.session_state.chat_history.append(("Bot", "Error: Unable to get a response from the server."))
        # Force rerun to update chat history immediately (Streamlit >=1.27)
        st.rerun()
    elif submit and not user_input:
        st.markdown(
            '<div style="color: black; background-color: #fff3cd; border-left: 6px solid #ffe066; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px;">'
            'Please enter a message before sending.'
            '</div>',
            unsafe_allow_html=True
        )

