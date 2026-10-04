import json
import io
from PIL import Image
from google import genai
from google.genai import types
import streamlit as st 

from twilio.rest import Client as TwilioClient


from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_CONTENT_SID = st.secrets["TWILIO_CONTENT_SID"]
TWILIO_WHATSAPP_FROM = st.secrets["TWILIO_WHATSAPP_FROM"]

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)



@st.cache_resource
def get_twilio_client():
    return TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

twilio_client = get_twilio_client()
gemini_client = get_gemini_client()

MODEL_NAME = "gemini-2.5-flash"

def clean_whatsapp_text(text):
    if not text:
        return "No nutrition summary available."
    text = " ".join(text.split())
    return text[:1500] + "..." if len(text) > 1500 else text
 

 
def format_whatsapp_number(number: str) -> str:
    cleaned = "".join(c for c in str(number) if c.isdigit() or c == "+")
    if not cleaned.startswith("+"):
        cleaned = f"+{cleaned}"
    return f"whatsapp:{cleaned}"

def send_whatsapp(to_number, user_name, summary):
    try:
        content_variables = json.dumps(
            {"1": str(user_name), "2": clean_whatsapp_text(summary)}, ensure_ascii=False
        )
        from_num = TWILIO_WHATSAPP_FROM
        if not from_num.startswith("whatsapp:"):
            from_num = f"whatsapp:{from_num}"

        to_num = format_whatsapp_number(to_number)

        message = twilio_client.messages.create(
            from_=from_num,
            to=to_num,
            content_sid=TWILIO_CONTENT_SID,
            content_variables=content_variables,
        )
        return True, message.sid
    except Exception as error:
        return False, str(error)

def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])
       

def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])

def optimize_image(photo_bytes, max_dim=1024):
    try:
        image = Image.open(io.BytesIO(photo_bytes))
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=85, optimize=True)
        return buf.getvalue(), "image/jpeg"
    except Exception:
        return photo_bytes, "image/jpeg"

def ask_gemini(parts):
    for attempt in range(2):
        try:
            return st.session_state.chat.send_message(parts).text
        except Exception as error:
            if attempt == 0:
                try:
                    # Reconnect chat session if connection was severed or timed out
                    st.session_state.chat = gemini_client.chats.create(
                        model=MODEL_NAME,
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                    )
                    continue
                except Exception:
                    pass
            return f"Sorry, something went wrong: {error}"


#step 1: onboarding (username and phone)

if 'onboarded' not in st.session_state:
    st.title(" MacroSnap 🥗")
    st.caption("Snap it. Track it. Text yourself the results.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        whatsapp_number = st.text_input(
            "WhatsApp number (with country code)",
            placeholder="+91XXXXXXXXXX",
            help = "This is the number MacroSnap will text you a summary"
        )

        submit = st.form_submit_button("Let's go 🚀")

        if submit:
            if not name.strip() or not whatsapp_number.strip():
                st.warning("Please enter both your name and WhatsApp number")
            else:
                st.session_state.name = name.strip()
                st.session_state.whatsapp_number = whatsapp_number.strip()
                st.session_state.chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                st.session_state.messages = []
                st.session_state.onboarded = True
                st.rerun()
    st.stop()



#step 2: chat interface
header_col, button_col = st.columns([5, 2], vertical_alignment = "center")

with header_col:
    st.title("MacroSnap 🥗")
with button_col:
    if st.button("📤 Send to WhatsApp", use_container_width=True):
        has_user_meals = any(m.get("role") == "user" for m in st.session_state.messages)
        if not has_user_meals:
            st.warning("Please snap a photo or describe a meal first before requesting a summary!")
        else:
            with st.spinner("Summarizing your day..."):
                summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
            success, info = send_whatsapp(st.session_state.whatsapp_number, st.session_state.name, summary)
            if success:
                st.success("Sent! Check your WhatsApp 📲")
            else:
                st.error(f"Couldn't send that: {info}")
 
st.caption(f"Logged in as {st.session_state.name} - updates go to {st.session_state.whatsapp_number}")    

 
if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
else:
    for message in st.session_state.messages:
        render_message(message)

user_input = st.chat_input(
    "Ask a question, or attach a photo of your meal",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []
 
    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        optimized_bytes, mime = optimize_image(photo_bytes)
        parts.append(types.Part.from_bytes(data=optimized_bytes, mime_type=mime))
    if text:
        add_message("user", "text", text)
        parts.append(types.Part.from_text(text=text))
    elif photo is not None:
        parts.append(types.Part.from_text(text="What is this meal? Give me the calories and macros."))
 
    with st.spinner("Crunching the numbers..."):
        answer = ask_gemini(parts)
    add_message("assistant", "text", answer)
