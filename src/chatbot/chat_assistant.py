from langchain_core.messages import HumanMessage, AIMessage

from src.agents.graph import scm_graph
from src.summarization.summarizer import summarize_conversation


class SCMChatAssistant:
    """
    Stateful SCM chatbot.

    Only user questions and final AI answers are retained
    between turns. Internal tool calls and tool results are
    not reused as conversation history.
    """

    def __init__(self):
        self.messages = []

    def ask(self, question: str) -> str:
        """
        Execute each SCM question independently.

        Previous tool calls and previous answers are not sent
        back to the SCM agent. This prevents stale tool results
        from influencing the current business query.
        """

        result = scm_graph.invoke(
            {
                "messages": [
                    HumanMessage(content=question)
                ]
            }
        )

        answer = None

        for message in reversed(result["messages"]):

            if isinstance(message, AIMessage):

                if message.content:
                    answer = message.content
                    break

        if not answer:
            answer = "No response was generated."

        # Store only the visible conversation for summarization.
        self.messages.append(
            HumanMessage(content=question)
        )

        self.messages.append(
            AIMessage(content=answer)
        )

        return answer

    def summarize(self) -> str:
        """
        Summarize only the visible conversation.
        """

        conversation_parts = []

        for message in self.messages:

            if isinstance(message, HumanMessage):

                conversation_parts.append(
                    f"User: {message.content}"
                )

            elif isinstance(message, AIMessage):

                if message.content:
                    conversation_parts.append(
                        f"Assistant: {message.content}"
                    )

        conversation = "\n\n".join(
            conversation_parts
        )

        if not conversation:
            return "There is no conversation to summarize."

        return summarize_conversation(conversation)


if __name__ == "__main__":

    assistant = SCMChatAssistant()

    questions = [
        "Which products are currently low in stock?",
        "Which products actually need restocking?",
        "Which warehouse has the highest inventory risk?",
    ]

    for question in questions:

        print("\n" + "=" * 70)
        print(f"USER: {question}")
        print("=" * 70)

        answer = assistant.ask(question)

        print("\nASSISTANT:")
        print(answer)

    print("\n" + "=" * 70)
    print("CONVERSATION SUMMARY")
    print("=" * 70)

    print(assistant.summarize())