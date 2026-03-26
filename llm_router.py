import os
from dotenv import load_dotenv
from groq import Groq
import google.generativeai as genai

load_dotenv()

# Load API keys from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)

# Groq setup
groq_client = Groq(api_key=GROQ_API_KEY)


def ask_llm(context, question):
    prompt = f"""
You are a research assistant.
Use the research papers below to answer the question.

Papers:
{context}

Question:
{question}

Give a 5-6 line summary and key insights.
"""

    # Try Gemini first
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text

    # If Gemini fails → Use Groq
    except Exception as e:
        print("Gemini failed, switching to Groq...")

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return response.choices[0].message.content