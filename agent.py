from langchain_core.messages import SystemMessage
from utils.utils import llm, search_tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, END
from langdetect import detect
from retrieve import retrieve  

def get_agent(thread_id: str = "abc123"):
    graph_builder = StateGraph(MessagesState)

    def query_or_respond(state: MessagesState):
        """Generate tool call for retrieval or respond."""
        llm_with_tools = llm.bind_tools([retrieve])
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    tools = ToolNode([retrieve])

    def generate(state: MessagesState):
        """Generate final answer from retrieved content."""
        for msg in reversed(state["messages"]):
            if msg.type == "human":
                user_input = msg.content
                break

        language = detect(user_input)

        recent_tool_messages = []
        for message in reversed(state["messages"]):
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break
        tool_messages = recent_tool_messages[::-1]

        docs_content = "\n\n".join(doc.content for doc in tool_messages)

        system_message_content = f"""
You are a highly intelligent and medically qualified assistant working for Magdi Yacoub Hospital (مجدي يعقوب). Your primary role is to respond to user queries with medically accurate, relevant, and easy-to-understand information, strictly based on the available context.

Guidelines for Generating Responses:
	•	Respond only with medically sound and verified information.
	•	Do not include general knowledge, opinions, or any non-medical content.
	•	If the internal documents and web search do not contain sufficient medical information to answer the question:
	•	Respond with:
	•	Arabic: "لا أملك معلومات كافية للإجابة على هذا السؤال."
	•	English: "I don't have enough information to answer this question."
	•	Maintain the same language used by the user (Arabic or English) throughout your response.
	•	Do not copy, quote, or paraphrase directly from the source texts.
	•	Keep your response clear, concise, and easy to understand, even for users with no medical background.


Internal Medical Knowledge:

{docs_content}


User Question:

{user_input}


Additional Instructions:

If the user’s input is not a medical inquiry or a greeting, respond with:
“It seems like your question is not related to medical information. Please ask a medical question for assistance.”

Carefully evaluate the input to determine whether it qualifies as a medical question or a greeting.


Your Answer (in {language} only):
"""

        conversation_messages = [
            m for m in state["messages"]
            if m.type in ("human", "system") or (m.type == "ai" and not m.tool_calls)
        ]

        prompt = [SystemMessage(system_message_content)] + conversation_messages

        response = llm.invoke(prompt)
        return {"messages": [response]}

    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)

    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)

    config = {"configurable": {"thread_id": thread_id}}
    return graph, config