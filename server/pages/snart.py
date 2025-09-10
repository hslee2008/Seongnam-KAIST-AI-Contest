import subprocess
import json
import time
from datetime import date, timedelta
from bs4 import BeautifulSoup

# 소스: 성남아트센터
# 링크: https://www.snart.or.kr/

__all__ = ["scrape_snart_events_page"]

def scrape_snart_events_page():
    base_url = "https://www.snart.or.kr"
    events_on_site = []
    today = date.today()

    print("성남아트센터 스크레이핑 중...")
    for i in range(30):
        current_date = today + timedelta(days=i)
        date_str = current_date.strftime("%Y%m%d")

        for type_id in [1, 2]:  # 1: 공연, 2: 전시
            try:
                api_url = f"{base_url}/web/simpleShowsMainReNew?date={date_str}&type={type_id}"
                result = subprocess.run(
                    ["curl", api_url], capture_output=True, check=True, timeout=30)
                try:
                    html_content = result.stdout.decode('utf-8')
                except UnicodeDecodeError:
                    html_content = result.stdout.decode(
                        'euc-kr', errors='ignore')

                html_content = json.loads(html_content)
                soup = BeautifulSoup(html_content, "html.parser")
                events = soup.find_all("li", class_="list")

                for event in events:
                    if "empty" in event.get("class", []):
                        continue

                    title_tag = event.find("h3", class_="title")
                    date_tag = event.find("div", class_="date")
                    place_tag = event.find("div", class_="place")
                    img_tag = event.find("img")
                    link_tag = event.find("a", class_="read_more")

                    title = title_tag.get_text(
                        strip=True) if title_tag else "제목 없음"
                    event_date = date_tag.get_text(
                        strip=True) if date_tag else "날짜 정보 없음"
                    place = place_tag.get_text(
                        strip=True) if place_tag else "장소 정보 없음"

                    image_src = img_tag['src'] if img_tag else ""
                    absolute_image = f"{base_url}{image_src}" if image_src.startswith(
                        '/') else image_src

                    link_src = link_tag['href'] if link_tag else ""
                    absolute_link = f"{base_url}{link_src}" if link_src.startswith(
                        '/') else link_src

                    is_duplicate = False
                    for existing_event in events_on_site:
                        if existing_event["title"] == title and existing_event["date"] == event_date:
                            is_duplicate = True
                            break

                    if not is_duplicate:
                        events_on_site.append({
                            "title": title,
                            "link": absolute_link,
                            "state": "진행예정",
                            "category": "공연" if type_id == 1 else "전시",
                            "image": absolute_image,
                            "date": event_date,
                            "place": place,
                            "source": "성남아트센터"
                        })
                time.sleep(0.1)
            except subprocess.CalledProcessError as e:
                print(f"{date_str} ({type_id}) 페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
                print(f"표준 오류: {e.stderr.decode('utf-8', errors='ignore')}")
            except Exception as e:
                print(f"{date_str} ({type_id}) 페이지에서 오류가 발생했습니다: {e}")

    print(f"성남아트센터에서 {len(events_on_site)}개의 이벤트를 찾았습니다.")
    return events_on_site
