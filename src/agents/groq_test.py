import os

from dotenv import load_dotenv
from groq import Groq

from src.agents.groq_tools import RESTOCK_TOOLS

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

print("Number of tools:", len(RESTOCK_TOOLS))
print("Tool JSON size:", len(str(RESTOCK_TOOLS)))

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "You are an SCM assistant."
        },
        {
            "role": "user",
            "content": "Which products currently need restocking?"
        }
    ],
    tools=RESTOCK_TOOLS,
    tool_choice="auto",
    temperature=0,
    max_completion_tokens=300,
)

print(response.choices[0].message)