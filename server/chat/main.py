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
        # OpenAI API로 키워드/카테고리 정규화 추출 (Few-shot 적용)
        messages = [
            {
                "role": "system",
                "content": """
당신은 행사 추천 시스템을 위한 '키워드 정규화 추출기'입니다.
반드시 JSON 객체만 반환합니다.

[목표]
- 사용자의 자유로운 한국어 입력에서 검색/필터에 유용한 핵심 키워드를 3~7개 추출합니다.
- 동의어/상위어/연령대/대상/활동유형/공간유형/비용 등으로 '정규화'된 키워드를 포함합니다.
- '가족'이 포함되면 '초등학생','놀이','사회성','어린이' 같은 연관 키워드를 적극 확장합니다.

[출력 형식 - 반드시 준수]
{
  "keywords": ["정규화된, 소문자, 공백 제거 최소화, 한글 유지"],
  "categories": ["(선택) 카테고리 라벨"],
  "inferred": ["(선택) 암시된 조건/의도"],
  "excluded": ["(선택) 제외해야 할 것(부정 표현)"]
}

[정규화 규칙]
- 소문자화하되 고유명사(예: 성남아트센터, 분당구)는 원형 유지.
- 날짜/기간 언급은 의미 키워드로 환원: 오늘/주말/이번주/이번달 → ["주말","이번주","이번달"] 등
- 비용: 무료/유료/할인 → ["무료"] 또는 ["유료"] 중 하나
- 공간유형: 실내/실외/야외/온라인 → ["실내"] / ["야외"] / ["온라인"]
- 대상/연령: 가족/아이/어린이/초등/중등/고등/성인/시니어 → ["가족","어린이","초등학생","청소년","고등학생","성인","어르신"] 등으로 표준화
- 활동유형: 체험/공연/전시/강연/교육/공모/대회/봉사/캠프/워크숍 등으로 표준화
- 주제: 환경/과학/ai/코딩/미술/음악/스포츠/독서/진로/취업/진학 등
- 지역: 성남/분당/수정/중원/야탑/정자동 등 지명 유지
- 부정/제외: "~말고", "제외", "빼고", "싫어" → excluded에 등록
- 중복 제거, 불용어 제거(은/는/이/가/좀/되도록 등)

[확장 규칙]
- "가족" 포함 시: ["가족","어린이","초등학생","놀이","사회성"] 중 맥락 맞는 것 포함
- "아이/어린이" 언급 시: ["어린이","초등학생"]로 통일
- "중학생/고등학생/청소년" → ["청소년"] 유지, 필요 시 구체 레벨 병행
- "과학/ai/코딩"은 ["ai","코딩","과학"] 같이 주제군 보강 가능
- "실내/야외" 같이 공간 조건이 있으면 반드시 포함
- "무료/유료" 언급을 비용 조건으로 포함
- "이번 주말/오늘/평일 저녁" 등 시간 조건은 ["주말","오늘","평일 저녁"]처럼 보존(한국어)

[제한]
- 키워드는 3~7개로 간결하게. 너무 일반적인 단어(행사, 추천, 알려줘)는 제외.
- 최종 응답은 반드시 JSON 객체 하나만 출력(설명 금지).
"""
            },

            # -------- Few-shot 예시 1 --------
            {
                "role": "user",
                "content": "주말에 가족이랑 아이가 즐길 수 있는 무료 야외 체험 있어?"
            },
            {
                "role": "assistant",
                "content": """
{
  "keywords": ["주말","가족","어린이","초등학생","야외","체험","무료"],
  "categories": ["교육","체험"],
  "inferred": ["가족 동반","놀이","사회성"],
  "excluded": []
}
"""
            },

            # -------- Few-shot 예시 2 --------
            {
                "role": "user",
                "content": "고등학생 대상 ai 경진대회 같은 거 있을까? 분당 근처면 좋고, 온라인 말고 오프라인 원해."
            },
            {
                "role": "assistant",
                "content": """
{
  "keywords": ["고등학생","청소년","ai","대회","경진대회","분당","오프라인"],
  "categories": ["대회","교육"],
  "inferred": ["진학/스펙","코딩"],
  "excluded": ["온라인"]
}
"""
            },

            # -------- Few-shot 예시 3 --------
            {
                "role": "user",
                "content": "실내 전시 찾아줘. 어린이용 말고 성인 위주로, 미술 쪽이면 좋겠어."
            },
            {
                "role": "assistant",
                "content": """
{
  "keywords": ["실내","전시","미술","성인"],
  "categories": ["전시","문화"],
  "inferred": [],
  "excluded": ["어린이","초등학생","가족"]
}
"""
            },

            # -------- Few-shot 예시 4 (부정/제외) --------
            {
                "role": "user",
                "content": "무료 강연 좋은데 야외는 말고 실내 위주로. 어린이 프로그램은 빼줘."
            },
            {
                "role": "assistant",
                "content": """
{
  "keywords": ["무료","강연","실내"],
  "categories": ["강연","교육"],
  "inferred": [],
  "excluded": ["야외","어린이","초등학생","가족"]
}
"""
            },

            # -------- 실제 사용자 입력 --------
            {
                "role": "user",
                "content": f"{user_message}"
            }
        ]

        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
            top_p=0.9
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