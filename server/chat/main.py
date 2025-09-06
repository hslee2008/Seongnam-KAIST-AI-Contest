import json
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiofiles
from openai import AsyncOpenAI

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

openai_client = AsyncOpenAI(api_key='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')  # Ensure OPENAI_API_KEY is set in your environment

events_data = []

@app.on_event("startup")
async def load_events_data():
    global events_data
    try:
        async with aiofiles.open('../events.json', mode='r', encoding='utf-8') as f:
            content = await f.read()
            events_data = json.loads(content)
    except FileNotFoundError:
        events_data = []
        print("events.json 파일을 찾을 수 없습니다.")
    except json.JSONDecodeError:
        events_data = []
        print("events.json 디코딩 중 오류가 발생했습니다.")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "").lower()

    if not user_message:
        return {"response": "메시지를 입력해주세요."}
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 사용자의 메시지에서 주요 주제, 카테고리, 또는 키워드를 추출하여 관련 행사를 추천하는 도우미입니다. 키워드 또는 카테고리를 포함한 JSON 객체로 응답하세요. 예: {\"keywords\": [\"수영\", \"교육\", \"청소년\"]}."},
                {"role": "user", "content": f"다음 메시지에서 주요 주제 또는 카테고리를 추출하세요: '{user_message}'"}
            ],
            response_format={"type": "json_object"}
        )
        analysis = json.loads(response.choices[0].message.content)
        keywords = analysis.get("keywords", []) or analysis.get("categories", [])
    except Exception as e:
        print(f"openai api 오류  {e}")
        keywords = [user_message]
    response_events = []
    for event in events_data:
        for keyword in keywords:
            if (keyword.lower() in event.get('title', '').lower() or 
                keyword.lower() in event.get('source', '').lower() or 
                keyword.lower() in event.get('category', '').lower() or
                keyword.lower() in event.get('deep_data', '').lower()):
                response_events.append(event)
                break

    if not response_events:
        return {"response": f"'{user_message}'와 관련된 행사를 찾을 수 없습니다."}

    return {"response": response_events}