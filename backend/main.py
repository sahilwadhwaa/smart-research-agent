from typing import Optional
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

from utils.utils import format_sse

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

class AskPayload(BaseModel):
    question: str
    files: Optional[list[UploadFile]] = File(None)

@app.post("/ask")
def ask(payload: AskPayload):
    try:
        print(f"API Key: {os.getenv('OPENAI_API_KEY')}")
        print(f"Received question: {payload.question}")
        """ response = client.responses.create(
            model="o4-mini",
            input=payload.question
        )

        answer = response.output_text

        print(f"Answer: {answer}") """
        return {
            "question": payload.question,
            #"answer": answer
            "answer": "hello world"
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "error": str(e)
        }

@app.post("/ask-stream")
def ask_stream(payload: AskPayload):
    print(f"Received streaming question: {payload.question}")
    def event_generator():
        try:
            stream = client.responses.create(
                model="gpt-4.1-nano",
                input=payload.question,
                stream=True,
                max_output_tokens=40
            )

            full_answer = ""

            for event in stream:
                if event.type == "response.output_text.delta":
                    chunk = event.delta
                    full_answer += chunk

                    yield format_sse("delta", {
                        "type": "delta",
                        "text": chunk,
                        "full_answer": full_answer
                    })
                elif event.type == "response.output_text.done":
                    yield format_sse("done", {
                        "type": "done",
                        "full_answer": full_answer
                    })
                elif event.type == "response.failed":
                    yield format_sse("error", {
                        "type": "error",
                        "message": str(event.response.error.message) if event.response.error else "Unknown error"
                    })
                elif event.type == "response.completed":
                    yield format_sse("completed", {
                        "type": "completed"
                    })
        except Exception as e:
            yield format_sse("error", {
                "type": "error",
                "message": str(e)
            })
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable buffering for nginx
        },
    )