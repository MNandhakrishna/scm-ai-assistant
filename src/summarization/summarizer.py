import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in the .env file.")

client = Groq(api_key=api_key)

MODEL = "llama-3.1-8b-instant"


def summarize_conversation(conversation: str) -> str:
    """
    Summarize an SCM conversation.

    The summary focuses on:
    - Key issues
    - Inventory risks
    - Restocking actions
    - Demand insights
    """

    prompt = f"""
You are an SCM operations analyst.

Summarize the following supply-chain conversation.

Return the summary using exactly these sections:

1. Key Issues
2. Inventory Risks
3. Restocking Actions
4. Demand Insights

Rules:
- Use only information present in the conversation.
- Do not invent values.
- Preserve SKU, warehouse, and quantity information.
- If a section has no relevant information, write "None identified."
- Keep the summary concise and business-oriented.

Conversation:
{conversation}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise supply-chain "
                    "operations summarization assistant."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
        max_tokens=600,
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    test_conversation = """
    User: Which products currently need restocking?

    Assistant:
    SKU_27 in WH_4 requires 181 units.
    SKU_29 in WH_2 requires 133 units.
    SKU_44 in WH_3 requires 112 units.

    User: Which warehouse has the highest inventory risk?

    Assistant:
    WH_3 has the highest stock gap of 43 units.

    User: Which product has the highest demand forecast?

    Assistant:
    SKU_27 has the highest demand forecast at 41.52 units.
    """

    summary = summarize_conversation(test_conversation)

    print("\n=== SCM CONVERSATION SUMMARY ===\n")
    print(summary)