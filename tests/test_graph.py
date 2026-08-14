from langchain_core.messages import HumanMessage, AIMessage

from src.agents.graph import scm_graph


def run_question(question: str) -> str:
    result = scm_graph.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ]
        }
    )

    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage):
            if message.content:
                return message.content

    raise AssertionError(
        "No final AI response was generated."
    )


def test_low_stock_question():
    answer = run_question(
        "Which products are currently low in stock?"
    )

    assert answer
    assert "SKU_" in answer
    assert "reorder" in answer.lower()


def test_restock_question():
    answer = run_question(
        "Which products actually need restocking?"
    )

    assert answer
    assert "SKU_" in answer
    assert "restock" in answer.lower()


def test_inventory_risk_question():
    answer = run_question(
        "Which warehouse has the highest inventory risk?"
    )

    assert answer
    assert "WH_" in answer
    assert "43" in answer