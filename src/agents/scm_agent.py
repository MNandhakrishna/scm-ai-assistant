import json
import os

from dotenv import load_dotenv
from groq import Groq

from src.agents.groq_tools import TOOLS, TOOL_FUNCTIONS


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in the .env file.")

client = Groq(api_key=api_key)


SYSTEM_PROMPT = """
You are an AI Supply Chain Management Assistant.

You answer questions using the available SCM tools.

Rules:

1. Use tools whenever the question requires SCM data.

2. Never invent inventory, demand, supplier, or restocking values.

3. Treat tool output as the source of truth.

4. Do not combine values from different tools unless the
   user explicitly asks for a comparison.

5. Do not claim that one metric is highest unless you
   verify it directly from the returned data.

6. Distinguish between:
   - inventory risk
   - stock gap
   - demand
   - demand forecast
   - restocking requirement

7. If the data is insufficient to determine something,
   clearly state that.

8. When explaining a recommendation, show the important
   values used to reach the conclusion.

9. Keep answers concise and business-oriented.

10. For restocking questions, include the recommended
    order quantity when available.

11. When explaining a restocking recommendation, include
    current inventory, required inventory, and recommended
    order quantity when those values are available.

12. Do not say that a field is unavailable if it exists
    in the tool result.

13. Do not provide unnecessary recommendations or suggest
    additional analysis unless the user asks for it.

14. If the user asks about low-stock products, report products
    below the reorder point.

15. Do not state that a low-stock product requires replenishment
    unless the restock calculation confirms that
    Recommended_Order_Quantity > 0.

16. Keep "low stock" and "requires restocking" as separate
    business concepts.
"""


def run_scm_agent(user_question: str):
    """
    Run the SCM agent using Groq native tool calling.
    """

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_question,
        },
    ]

    while True:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0,
        )

        assistant_message = response.choices[0].message

        # No tool call means the model has produced the final answer.
        if not assistant_message.tool_calls:

            return assistant_message.content

        # Add the assistant's tool-call message to conversation.
        messages.append(assistant_message)

        # Execute every requested tool.
        for tool_call in assistant_message.tool_calls:

            function_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            if function_name not in TOOL_FUNCTIONS:
                raise ValueError(
                    f"Unknown tool requested: {function_name}"
                )

            function = TOOL_FUNCTIONS[function_name]

            result = function(**arguments)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        result,
                        default=str
                    ),
                }
            )


if __name__ == "__main__":

    questions = [
        "Which products currently need restocking?",
        "Which warehouse has the highest inventory risk?",
        "Which products have the highest demand forecast?",
        "What is the demand history for SKU_2?",
    ]

    for question in questions:

        print("\n" + "=" * 70)
        print(f"QUESTION: {question}")
        print("=" * 70)

        answer = run_scm_agent(question)

        print("\nANSWER:")
        print(answer)