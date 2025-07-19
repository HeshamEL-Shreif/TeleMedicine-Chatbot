from fastapi import FastAPI
from pydantic import BaseModel
from db.vector_db import save_docs_to_vector_store
from agent import get_agent
import uvicorn

app = FastAPI()


vector_db = save_docs_to_vector_store()
graph, config = get_agent()


class QueryRequest(BaseModel):
    query: str


@app.post("/query")
async def handle_query(request: QueryRequest):
    input_query = request.query
    answer = None

    for step in graph.stream(
        {"messages": [{"role": "user", "content": input_query}]},
        stream_mode="values",
        config=config,
    ):
        answer = step["messages"][-1]

    return {"answer": answer.content}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)