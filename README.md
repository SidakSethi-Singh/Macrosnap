# MacroSnap 🥗 - AI Vision Nutrition Buddy

MacroSnap is an intelligent nutrition tracking assistant powered by Google Gemini 2.5 Flash and Streamlit. Users can snap or upload photos of their meals (or describe them in text), and MacroSnap instantly identifies the food, estimates calories, and calculates macronutrients (protein, carbs, and fats). With a single click, users can send their daily nutrition breakdown directly to their phone via WhatsApp using Twilio.

---

## 🚀 Features

- **Multimodal Food Recognition**: Upload food images or text descriptions to receive instant calorie and macro estimations.
- **Conversational AI Nutrition Buddy**: Powered by Gemini 2.5 Flash with dedicated system instructions for accurate nutritional breakdowns.
- **WhatsApp Integration**: Automatically compile daily meal summaries and send them straight to WhatsApp via Twilio.
- **Image Optimization**: Automatic client-side/server-side image compression and resizing for fast AI response times.

---

## 🛠️ Tech Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/)
- **Vision & Language AI**: [Google GenAI SDK](https://github.com/googleapis/python-genai) (`gemini-2.5-flash`)
- **Messaging API**: [Twilio REST API](https://www.twilio.com/) (WhatsApp Messaging & Content Templates)
- **Image Processing**: [Pillow](https://python-pillow.org/)

---

## 📋 Getting Started Locally

### 1. Clone the Repository
```bash
git clone https://github.com/SidakSethi-Singh/Macrosnap.git
cd Macrosnap
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Secrets
Create a `.streamlit/secrets.toml` file based on `.streamlit/secrets.toml.example`:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
TWILIO_ACCOUNT_SID = "your_twilio_account_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_WHATSAPP_FROM = "+14155238886"
TWILIO_CONTENT_SID = "your_twilio_content_sid"
```

### 5. Run the Application
```bash
streamlit run app.py
```

---

## 🌐 Deployment

MacroSnap is deployed on **Streamlit Community Cloud**. To deploy your own instance:
1. Fork or push this repository to GitHub.
2. Connect your repository on [Streamlit Community Cloud](https://share.streamlit.io/).
3. Add the secrets in **App Settings → Secrets**.
4. Deploy!
