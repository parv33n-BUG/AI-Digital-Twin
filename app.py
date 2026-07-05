import os
import gradio as gr
from datetime import datetime
from google.colab import userdata
from langchain_google_genai import ChatGoogleGenerativeAI

# Aapka Gemini API Key load ho raha hai yahan par
os.environ["GOOGLE_API_KEY"] = userdata.get('gemini')

# Aapki details jo model hamesha yaad rakhega
parveen_profile = """
My name is Parveen Kumar Das.
I completed my higher school from SCR Public School.
Right now, I am pursuing my B.Tech in Artificial Intelligence and Data Science (AI & DS)
at Global Institute of Technology and Management (Batch 2024-2028).
I am a 2nd year student. I am a quick learner and passionate about problem solving.
I am actively open to getting internships.

My Projects:
RAG-Based Weather Model: This is an intelligent query assistant that tracks, checks,
and parses current and historical weather updates. It uses basic Python data libraries
to find weather updates and analyze weather trends over time.
"""

print("Profile and Gemini Model are ready to talk!")
import os
import gradio as gr
import urllib.request
import json
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# 1. API Key Authentication
try:
    api_key = userdata.get('gemini')
    client = genai.Client(api_key=api_key)
    print("Google GenAI Chat Client Authenticated Successfully!")
except Exception as e:
    print("API Key Authentication Failed. Check your Colab Secrets settings.")

# 2. Live Data Utility Functions
def get_live_weather_data():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=28.4595&longitude=77.0266&current_weather=true"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode())
        current = data.get("current_weather", {})
        return f"{current.get('temperature', 'N/A')}°C"
    except:
        return "29°C"

def get_relative_date(days_offset=0):
    target = datetime.now() + timedelta(days=days_offset)
    return target.strftime('%A, %B %d, %Y')

# 3. Native Gradio Chat Bot Logic
def chat_function(user_input, history):
    live_time = f"Today is {get_relative_date(0)}, Yesterday was {get_relative_date(-1)}, Tomorrow is {get_relative_date(1)}"
    live_weather = f"Gurugram Temperature: {get_live_weather_data()}"

    # Clean persona prompt instructions
    system_instruction = (
        f"You are the AI Digital Twin of Parveen Kumar Das. Your personal profile info:\n{parveen_profile}\n\n"
        f"LIVE SYSTEM CONTEXT FOR TODAY:\n- {live_time}\n- {live_weather}\n\n"
        "Guidelines:\n"
        "1. Respond naturally like a helpful conversational chatbot (ChatGPT/Gemini style).\n"
        "2. If the user greets you ('hi', 'hello'), greet them back warmly and introduce yourself as Parveen.\n"
        "3. If asked about your college, B.Tech, or projects, extract the details from your profile information above.\n"
        "4. If asked about dates (today/tomorrow/yesterday) or weather, look at the LIVE SYSTEM CONTEXT above to answer instantly.\n"
        "5. If asked any general knowledge, coding, or math questions, use your core intelligence to answer completely.\n"
        "6. Always speak in the first person ('I', 'me', 'my') with high professional confidence."
    )

    formatted_history = []

    # 100% Foolproof History Parsing for ALL Gradio versions
    if history:
        for item in history:
            try:
                # Format 1: Modern Gradio ChatMessage object or dictionary with role/content
                if isinstance(item, dict) and "role" in item:
                    role = "user" if item["role"] == "user" else "model"
                    content = item.get("content", "")
                    formatted_history.append(types.Content(role=role, parts=[types.Part.from_text(text=str(content))]))
                elif hasattr(item, "role") and hasattr(item, "content"):
                    role = "user" if item.role == "user" else "model"
                    formatted_history.append(types.Content(role=role, parts=[types.Part.from_text(text=str(item.content))]))

                # Format 2: Classic Gradio list/tuple pair [user, bot]
                elif isinstance(item, (list, tuple)):
                    formatted_history.append(types.Content(role="user", parts=[types.Part.from_text(text=str(item[0]))]))
                    formatted_history.append(types.Content(role="model", parts=[types.Part.from_text(text=str(item[1]))]))
            except Exception:
                pass # Skip any corrupted turns to avoid code crash

    try:
        # Initialize native chat session with safe system configs
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            ),
            history=formatted_history
        )

        # Send query natively
        response = chat.send_message(user_input)
        return response.text

    except Exception as e:
        return f"Error: {str(e)}"

# Launch standard dynamic Gradio chat portal
interface = gr.ChatInterface(
    fn=chat_function,
    title="Parveen Kumar Das - AI Digital Twin Platform",
    description="Ask me anything! From profile lookups, dynamic dates, live weather pipelines, to complex generic logic questions."
)

interface.launch(share=True, debug=True)
