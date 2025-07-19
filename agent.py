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

        search_snippets = search_tool.run(user_input)

        system_message_content = f"""
You are an intelligent and qualified medical assistant in Magdi Yacoub Hospital. Your task is to answer user questions using **only medically accurate and relevant information**, based on the provided context.

Instructions:
- Do **not** include general knowledge, opinions, or any non-medical information in your answer.
- If neither the internal documents nor the web search contain medically relevant information to answer the question, respond with:
  - "لا أملك معلومات كافية للإجابة على هذا السؤال." (if the question is in Arabic), or
  - "I don't have enough information to answer this question." (if the question is in English).
- The answer must be written in the **same language** as the user’s question.
- Do not repeat or quote the document or web text directly.
- Keep the answer simple, medically accurate, and easy for non-experts to understand.

Trusted internal medical information:
{docs_content}



Question:
{user_input}
if the question is not a medical question or greetings, respond with:
It seems like your question is not related to medical information. Please ask a medical question for assistance.
- read the question carefully and ensure it is a medical question or a greeting.
Answer (in {language} only):
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