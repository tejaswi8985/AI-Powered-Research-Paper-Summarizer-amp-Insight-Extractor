from google import genai
import os
from dotenv import load_dotenv
from google.genai import types
from groq import Groq

load_dotenv()

# Load API keys from .env
GEMINI_API_KEY = os.getenv("")
GROQ_API_KEY = os.getenv("")

client = genai.Client(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

def ask_gemini(content, query):
    prompt = f"""
You are an AI research assistant.

Analyze the research papers and generate insights.

Instructions:
- Summarize the research
- Mention methods used
- Mention key findings
- Write 6–8 lines
- Use simple academic language

Research Paper Content:
{content}

User Question:
{query}

AI Insights:
"""

    # Try Gemini
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4
            ),
        )
        return response.text.strip()

    # If Gemini fails → Use Groq
    except Exception as e:
        try:
            chat = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            return chat.choices[0].message.content.strip()


        except Exception as e:
            return "AI service unavailable. But relevant papers are shown above."