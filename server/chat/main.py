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

openai_client = AsyncOpenAI(api_key='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') 

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
        # OpenAI API로 키워드만 추출
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """
당신은 사용자의 메시지에서 주요 주제, 카테고리, 또는 키워드를 추출하는 도우미입니다. 
다음 지침을 따라 응답하세요:
1. 사용자의 메시지에서 주요 키워드(예: '가족', '야외', '교육', '수영', '사회성')를 추출합니다. 
2. '가족'이 포함되면 '초등학생', '놀이', '사회성', '어린이' 같은 관련 키워드도 추가로 고려합니다.
3. 응답은 JSON 객체로 반환하며, 형식은 다음과 같습니다:
   {
     "keywords": ["추출된 키워드"]
   }
                """},
                {"role": "user", "content": f"다음 메시지에서 주요 주제 또는 카테고리를 추출하세요: '{user_message}'"}
            ],
            response_format={"type": "json_object"}
        )
        analysis = json.loads(response.choices[0].message.content)
        keywords = analysis.get("keywords", []) or analysis.get("categories", []) or [user_message]
        print(f"추출된 키워드: {keywords}")

        matching_events = []
        for event in events_data:
            score = 0
            for keyword in keywords:
                if keyword.lower() in event.get('title', '').lower():
                    score += 2
                if keyword.lower() in event.get('deep_data', '').lower():
                    score += 1
                if keyword.lower() in event.get('category', '').lower():
                    score += 1
            if score > 0:
                matching_events.append((event, score))

        print(f"매칭된 행사 수: {len(matching_events)}")

        if not matching_events:
            return {
                "response": {
                    "keywords": keywords,
                    "recommended_event": {},
                    "reason": f"'{user_message}'와 관련된 행사를 events.json에서 찾을 수 없습니다."
                }
            }
        best_event, best_score = max(matching_events, key=lambda x: x[1])
        return {
            "response": {
                "keywords": keywords,
                "recommended_event": best_event
            }
        }

    except Exception as e:
        print(f"OpenAI API 오류: {e}")
        return {
            "response": {
                "keywords": [user_message],
                "recommended_event": {},
                "reason": f"오류가 발생했습니다: {str(e)}"
            }
        }