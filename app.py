import streamlit as st
import anthropic
import gspread
import json
import re
from datetime import datetime
from google.oauth2.service_account import Credentials

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

SHEET_ID = "1sq3xXX8kG0RFaagaBMfq1GiLZ5pIvNl7z15zQU2AFMA"

SYSTEM_PROMPT = """You are a friendly assistant for Howrah Properties, a real estate agency in Howrah, West Bengal.

Help buyers find flats. Answer questions about properties, home loans, and registration.

Respond in the same language the user writes in (Bengali, Hindi, or English). Keep replies short and friendly, like WhatsApp chat.

CURRENT PROPERTIES:
1. Shibpur - 2BHK, 950 sq ft, Rs 45 lakh, 3rd floor, ready to move
2. Salkia - 3BHK, 1250 sq ft, Rs 65 lakh, 5th floor, possession in 6 months
3. Liluah - 2BHK, 850 sq ft, Rs 38 lakh, 2nd floor, ready to move
4. Bally - 3BHK, 1400 sq ft, Rs 72 lakh, 7th floor, possession in 3 months
5. Howrah Maidan - 2BHK, 1000 sq ft, Rs 55 lakh, 4th floor, ready to move

IMPORTANT LEAD CAPTURE RULES:
- Collect lead details ONLY if they have not already been saved in this chat
- When you have collected name, phone, budget, area, and property interest from a NEW buyer, respond ONLY with this exact JSON on a single line, nothing else:
{"lead": true, "name": "FULL NAME", "phone": "PHONE", "budget": "BUDGET", "area": "AREA", "interest": "PROPERTY DETAILS"}
- If a lead has already been saved earlier in this conversation, DO NOT ask for details again. Just continue the conversation normally and answer their questions.
- If they want to inquire about a DIFFERENT property after saving, politely tell them their existing details are saved and the agent will discuss all options. Don't ask for details again."""

def save_lead(data):
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(SHEET_ID).sheet1
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("name", ""),
            data.get("phone", ""),
            data.get("budget", ""),
            data.get("area", ""),
            data.get("interest", ""),
        ])
        return True
    except Exception as e:
        st.error(f"Error saving lead: {e}")
        return False

st.set_page_config(page_title="Howrah Properties", page_icon="🏠")
st.title("🏠 Howrah Properties")
st.caption("Ask about flats in Bengali, Hindi, or English")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "lead_saved" not in st.session_state:
    st.session_state.lead_saved = False

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask about properties..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    system_with_status = SYSTEM_PROMPT
    if st.session_state.lead_saved:
        system_with_status += "\n\nNOTE: Lead details have ALREADY been saved for this buyer. Do not ask for or collect lead details again. Just chat helpfully."

    with st.chat_message("assistant"):
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_with_status,
            messages=st.session_state.messages,
        )
        reply = response.content[0].text
        
        json_match = re.search(r'\{.*"lead".*\}', reply, re.DOTALL)
        if json_match and not st.session_state.lead_saved:
            try:
                lead_data = json.loads(json_match.group())
                if lead_data.get("lead"):
                    if save_lead(lead_data):
                        st.session_state.lead_saved = True
                        thank_you = f"Thank you {lead_data.get('name', '')}! 🏠 Our agent will call you on {lead_data.get('phone', '')} within 24 hours. Feel free to ask anything else!"
                        st.write(thank_you)
                        st.session_state.messages.append({"role": "assistant", "content": thank_you})
                    else:
                        error_msg = "Sorry, there was an issue saving your details. Please try again."
                        st.write(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    st.write(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
            except:
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
