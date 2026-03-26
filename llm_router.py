from groq import Groq
import google.generativeai as genai

# Gemini setup
genai.configure(api_key="AIzaSyALgdJwFc7XYv3CN0a6G-rnGC4b22JwQFc")

# Groq setup
groq_client = Groq(api_key="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")


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
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return response.choices[0].message.content