import streamlit as st
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a friendly assistant for Howrah Properties, a real estate agency in Howrah, West Bengal.

Help buyers find flats. Answer questions about properties, home loans, and registration.

Respond in the same language the user writes in (Bengali, Hindi, or English). Keep replies short and friendly, like WhatsApp chat.

CURRENT PROPERTIES:
1. Shibpur - 2BHK, 950 sq ft, Rs 45 lakh, 3rd floor, ready to move
2. Salkia - 3BHK, 1250 sq ft, Rs 65 lakh, 5th floor, possession in 6 months
3. Liluah - 2BHK, 850 sq ft, Rs 38 lakh, 2nd floor, ready to move
4. Bally - 3BHK, 1400 sq ft, Rs 72 lakh, 7th floor, possession in 3 months
5. Howrah Maidan - 2BHK, 1000 sq ft, Rs 55 lakh, 4th floor, ready to move

When buyer is interested, ask for: name, phone number, budget, preferred area. Then say an agent will call within 24 hours."""

st.set_page_config(page_title="Howrah Properties", page_icon="🏠")
st.title("🏠 Howrah Properties")
st.caption("Ask about flats in Bengali, Hindi, or English")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask about properties..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=st.session_state.messages,
        )
        reply = response.content[0].text
        st.write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})