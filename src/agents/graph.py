import json
import os
from typing import Annotated

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from typing_extensions import TypedDict
from groq import Groq, APIStatusError
from src.agents.groq_tools import TOOLS, TOOL_FUNCTIONS
from src.utils.logger import get_logger

logger = get_logger(__name__)


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in the .env file.")

client = Groq(api_key=api_key)


MODEL = "llama-3.1-8b-instant"


SYSTEM_PROMPT = """
You are an AI Supply Chain Management Assistant.

Use the available SCM tools to answer questions about:

- Inventory
- Demand
- Restocking

Rules:

1. Use tools whenever SCM data is required.
2. Never invent data.
3. Treat tool output as the source of truth.
4. Clearly distinguish inventory, demand, forecast,
   stock gap, and replenishment.
5. For restocking questions, include recommended
   order quantities when available.
6. Explain important numbers used in a recommendation.
7. Do not provide unnecessary recommendations.
8. If the data does not contain the requested information,
   clearly say so.
"""


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def call_model(state: AgentState):
    """
    Send the conversation to Groq and allow the model
    to request SCM tools.
    """

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    # -----------------------------------------------------
    # Convert LangChain messages to Groq message format
    # -----------------------------------------------------

    for message in state["messages"]:

        if isinstance(message, HumanMessage):

            messages.append(
                {
                    "role": "user",
                    "content": message.content,
                }
            )

        elif isinstance(message, AIMessage):

            assistant_message = {
                "role": "assistant",
                "content": message.content or "",
            }

            if message.tool_calls:

                assistant_message["tool_calls"] = [
                    {
                        "id": tool_call["id"],
                        "type": "function",
                        "function": {
                            "name": tool_call["name"],
                            "arguments": json.dumps(
                                tool_call["args"]
                            ),
                        },
                    }
                    for tool_call in message.tool_calls
                ]

            messages.append(assistant_message)

        elif isinstance(message, ToolMessage):

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": message.tool_call_id,
                    "content": message.content,
                }
            )

    # -----------------------------------------------------
    # Call Groq with error handling
    # -----------------------------------------------------

    try:

        logger.info(
            "Calling Groq model: %s",
            MODEL,
        )

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0,
            max_tokens=800,
        )

        logger.info(
            "Groq response received successfully"
        )

    except APIStatusError as exc:

        logger.error(
            "Groq API error: status=%s, message=%s",
            exc.status_code,
            str(exc),
        )

        if exc.status_code == 413:

            raise RuntimeError(
                "The SCM request is too large for the current "
                "Groq usage limit. Please ask a shorter question "
                "or reduce the amount of data requested."
            ) from exc

        raise RuntimeError(
            "The SCM AI service returned an API error. "
            "Please try again."
        ) from exc

    except Exception as exc:

        logger.exception(
            "Unexpected Groq error: %s",
            exc,
        )

        raise RuntimeError(
            "The SCM AI service could not process the request."
        ) from exc

    # -----------------------------------------------------
    # Process Groq response
    # -----------------------------------------------------

    assistant_message = response.choices[0].message

    tool_calls = []

    if assistant_message.tool_calls:

        for tool_call in assistant_message.tool_calls:

            raw_arguments = tool_call.function.arguments

            logger.info(
                "Raw tool arguments for %s: %r",
                tool_call.function.name,
                raw_arguments,
            )

            if raw_arguments:

                try:
                    parsed_arguments = json.loads(raw_arguments)

                except json.JSONDecodeError:

                    logger.error(
                        "Invalid JSON tool arguments for %s: %s",
                        tool_call.function.name,
                        raw_arguments,
                    )

                    parsed_arguments = {}

            else:

                parsed_arguments = {}

            # Groq may return "null", which json.loads()
            # converts to Python None. LangChain requires
            # tool_call args to always be a dictionary.
            if not isinstance(parsed_arguments, dict):

                logger.warning(
                    "Tool arguments were not a dictionary for %s. "
                    "Using empty arguments instead. Received: %r",
                    tool_call.function.name,
                    parsed_arguments,
                )

                parsed_arguments = {}

            tool_calls.append(
                {
                    "name": tool_call.function.name,
                    "args": parsed_arguments,
                    "id": tool_call.id,
                }
            )

    return {
        "messages": [
            AIMessage(
                content=assistant_message.content or "",
                tool_calls=tool_calls,
            )
        ]
    }

def execute_tools(state: AgentState):
    """
    Execute the tools requested by the LLM.
    """

    tool_messages = []

    last_message = state["messages"][-1]

    for tool_call in last_message.tool_calls:

        function_name = tool_call["name"]
        arguments = tool_call["args"]

        if function_name not in TOOL_FUNCTIONS:
            result = {
                "error": f"Unknown tool: {function_name}"
            }

        else:
            function = TOOL_FUNCTIONS[function_name]
            result = function(**arguments)

        tool_messages.append(
            ToolMessage(
                content=json.dumps(
                    result,
                    default=str
                ),
                tool_call_id=tool_call["id"],
            )
        )

    return {
        "messages": tool_messages
    }


def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return END


workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", execute_tools)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    },
)

workflow.add_edge("tools", "agent")

scm_graph = workflow.compile()


if __name__ == "__main__":

    question = "Which products currently need restocking?"

    result = scm_graph.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ]
        }
    )

    print("\n=== LANGGRAPH SCM ASSISTANT ===\n")

    for message in result["messages"]:

        if isinstance(message, AIMessage):

            if message.content:
                print(message.content)