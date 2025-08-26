import subprocess
import json
from bs4 import BeautifulSoup
import time
from datetime import date, timedelta

'''
소스: 성남시청
링크: https://www.seongnam.go.kr/apply/event.do
'''


def deep_scrape_seongnam_event_page(link):
    event_data = ""

    try:
        result = subprocess.run(
            ["curl", "-d", "", link],
            capture_output=True, check=True
        )
        html_content = result.stdout.decode('utf-8')

        soup = BeautifulSoup(html_content, "html.parser")

        event_list = soup.find("div", class_="sub")

        if not event_list:
            print("페이지를 찾을 수 없습니다.")
            return []

        event_data = event_list.get_text(separator="\n", strip=True)

    except subprocess.CalledProcessError as e:
        print(f"{link} 페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
        print(f"표준 오류: {e.stderr}")

    except Exception as e:
        print(f"{link} 페이지에서 오류가 발생했습니다: {e}")

    return event_data


def scrape_seongnam_events_page(page_number):
    url = "https://www.seongnam.go.kr/apply/event.do"
    events_on_page = []

    try:
        result = subprocess.run(
            ["curl", "-d", f"currentPage={page_number}", url],
            capture_output=True, check=True
        )
        html_content = result.stdout.decode('utf-8')

        soup = BeautifulSoup(html_content, "html.parser")

        event_list = soup.find("div", class_="event_img_list")

        if not event_list:
            print(f"{page_number}페이지에서 이벤트 목록을 찾을 수 없습니다.")
            return []

        events = event_list.find_all("a", class_="item")

        for event in events:
            title = event.find("span", class_="name").get_text(strip=True)
            onclick_attr = event.get("onclick", "")
            app_idx_parts = onclick_attr.split("goView('")

            if len(app_idx_parts) > 1:
                app_idx = app_idx_parts[1].split("')")[0]
                app_idx = ''.join(filter(str.isdigit, app_idx.split(',')[0]))
                absolute_link = f"https://www.seongnam.go.kr/apply/view.do?appIdx={app_idx}"
            else:
                absolute_link = "링크를 찾을 수 없습니다."

            text_span = event.find("span", class_="text")
            state = text_span.find("span", class_="state").get_text(strip=True)
            category = text_span.find(
                "span", class_="category").get_text(strip=True)
            date_str = text_span.find("span", class_="date").get_text(
                strip=True).replace("\r\n", "").replace("\t", "").strip()

            image_span = event.find("span", class_="img")
            image_src = image_span.find(
                "img")["src"] if image_span else "이미지를 찾을 수 없습니다."

            if state in ["진행중", "진행예정"]:
                events_on_page.append({
                    "title": title,
                    "link": absolute_link,
                    "state": state,
                    "category": category.split("·")[0].strip(),
                    "audience": category.split("·")[1].strip() if len(category.split("·")) > 1 else "",
                    "image": "https://www.seongnam.go.kr" + image_src,
                    "date": date_str,
                    "source": "성남시청",
                    "deep_data": deep_scrape_seongnam_event_page(absolute_link)
                })

    except subprocess.CalledProcessError as e:
        print(f"{page_number}페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
        print(f"표준 오류: {e.stderr}")

    except Exception as e:
        print(f"{page_number}페이지에서 오류가 발생했습니다: {e}")

    return events_on_page


'''
소스: 성남시청소년재단
링크: https://www.snyouth.or.kr/
'''


def deep_scrape_snyouth_event_page(link):
    event_data = ""

    try:
        result = subprocess.run(
            ["curl", "-d", "", link],
            capture_output=True, check=True
        )
        html_content = result.stdout.decode('utf-8')

        soup = BeautifulSoup(html_content, "html.parser")

        event_list = soup.find("div", class_="board-view")

        if not event_list:
            print("페이지를 찾을 수 없습니다.")
            return []

        event_data = event_list.get_text(separator="\n", strip=True)

    except subprocess.CalledProcessError as e:
        print(f"{link} 페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
        print(f"표준 오류: {e.stderr}")

    except Exception as e:
        print(f"{link} 페이지에서 오류가 발생했습니다: {e}")

    return event_data


def scrape_snyouth_events_page(page_number):
    url = f"https://www.snyouth.or.kr/fmcs/123?page={page_number}"
    events_on_page = []

    try:
        result = subprocess.run(["curl", url], capture_output=True, check=True)
        html_content = result.stdout.decode('utf-8')

        soup = BeautifulSoup(html_content, "html.parser")

        event_list = soup.find("tbody")

        if not event_list:
            print(f"{page_number}페이지에서 이벤트 목록을 찾을 수 없습니다.")
            return []

        events = event_list.find_all("tr")

        for event in events:
            title_cell = event.find("td", class_="text-left")

            if not title_cell:
                continue

            title = title_cell.get_text(strip=True)
            link = title_cell.find("a")["href"]
            absolute_link = f"https://www.snyouth.or.kr{link}"

            date_cell = event.find_all("td")[4]
            date_str = date_cell.get_text(strip=True).replace("등록일자", "")

            events_on_page.append({
                "title": title,
                "link": absolute_link,
                "state": "진행예정",
                "category": "기타",
                "date": date_str,
                "source": "성남시청소년재단",
                "deep_data": deep_scrape_snyouth_event_page(absolute_link)
            })

    except subprocess.CalledProcessError as e:
        print(f"{page_number}페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
        print(f"표준 오류: {e.stderr}")

    except Exception as e:
        print(f"{page_number}페이지에서 오류가 발생했습니다: {e}")

    return events_on_page

'''
소스: 성남아트센터
링크: https://www.snart.or.kr/
'''
def scrape_snart_events():
    base_url = "https://www.snart.or.kr"
    events_on_site = []
    today = date.today()

    print("성남아트센터 스크레이핑 중...")
    for i in range(365):
        current_date = today + timedelta(days=i)
        date_str = current_date.strftime("%Y%m%d")
        
        for type_id in [1, 2]: # 1: 공연, 2: 전시
            try:
                api_url = f"{base_url}/web/simpleShowsMainReNew?date={date_str}&type={type_id}"
                result = subprocess.run(["curl", api_url], capture_output=True, check=True)
                json_string = result.stdout.decode('utf-8')
                
                html_content = json.loads(json_string)

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

                    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
                    event_date = date_tag.get_text(strip=True) if date_tag else "날짜 정보 없음"
                    place = place_tag.get_text(strip=True) if place_tag else "장소 정보 없음"
                    
                    image_src = img_tag['src'] if img_tag else ""
                    absolute_image = f"{base_url}{image_src}" if image_src.startswith('/') else image_src
                    
                    link_src = link_tag['href'] if link_tag else ""
                    absolute_link = f"{base_url}{link_src}" if link_src.startswith('/') else link_src

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
                            "date": event_date,
                            "place": place,
                            "image": absolute_image,
                            "source": "성남아트센터"
                        })
                time.sleep(0.1) # 서버 부하 방지
            except subprocess.CalledProcessError as e:
                print(f"{date_str} ({type_id}) 페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
                print(f"표준 오류: {e.stderr}")
            except Exception as e:
                print(f"{date_str} ({type_id}) 페이지에서 오류가 발생했습니다: {e}")
    
    print(f"성남아트센터에서 {len(events_on_site)}개의 이벤트를 찾았습니다.")
    return events_on_site

'''
소스: 맹산환경생태학습원
링크: https://mpark.seongnam.go.kr:10003
'''
def deep_scrape_mpark_event_page(link):
    event_data = ""
    try:
        result = subprocess.run(["curl", link], capture_output=True, check=True)
        html_content = result.stdout.decode('utf-8')
        soup = BeautifulSoup(html_content, "html.parser")
        content_div = soup.find("div", class_="bbsContents")
        if content_div:
            event_data = content_div.get_text(separator="\n", strip=True)
    except subprocess.CalledProcessError as e:
        print(f"{link} 페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
        print(f"표준 오류: {e.stderr}")
    except Exception as e:
        print(f"{link} 페이지에서 오류가 발생했습니다: {e}")
    return event_data

def scrape_mpark_events():
    base_url = "https://mpark.seongnam.go.kr:10003"
    events_on_site = []
    page = 1
    print("맹산환경생태학습원 스크레이핑 중...")
    while page <= 5:
        list_url = f"{base_url}/main.php?menugrp=040100&master=bbs&act=list&master_sid=3&Page={page}"
        try:
            result = subprocess.run(["curl", list_url], capture_output=True, check=True)
            html_content = result.stdout.decode('utf-8')
            soup = BeautifulSoup(html_content, "html.parser")
            
            notice_list = soup.select("div.bbsContent table tr")
            
            if len(notice_list) <= 1:
                break

            found_count = 0
            for notice in notice_list:
                if not notice.find_all('td'):
                    continue
                
                title_cell = notice.find("td", class_="text-left")
                if not title_cell:
                    continue
                
                title = title_cell.get_text(strip=True)
                link_tag = title_cell.find('a')
                relative_link = link_tag['href'] if link_tag else None

                if not relative_link:
                    continue

                absolute_link = f"{base_url}/{relative_link}"
                
                cells = notice.find_all("td")
                date_str = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                found_count += 1
                events_on_site.append({
                    "title": title,
                    "link": absolute_link,
                    "date": date_str,
                    "source": "맹산환경생태학습원",
                    "deep_data": deep_scrape_mpark_event_page(absolute_link)
                })
            
            print(f"{page}페이지에서 {found_count}개의 이벤트를 찾았습니다.")
            if found_count == 0:
                break
            page += 1
            time.sleep(0.1)

        except subprocess.CalledProcessError as e:
            print(f"{list_url} 페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
            break
        except Exception as e:
            print(f"{list_url} 페이지에서 오류가 발생했습니다: {e}")
            break
            
    print(f"맹산환경생태학습원에서 총 {len(events_on_site)}개의 이벤트를 찾았습니다.")
    return events_on_site


def main():
    all_events = []

    # --- 성남시청 스크레이퍼 ---
    page = 1
    while True:
        print(f"seongnam.go.kr {page}페이지를 스크래핑하는 중...")
        events = scrape_seongnam_events_page(page)
        if not events:
            print(f"seongnam.go.kr {page}페이지에서 더 이상 이벤트를 찾을 수 없습니다. 중지합니다.")
            break
        all_events.extend(events)
        print(f"{page}페이지에서 {len(events)}개의 이벤트를 찾았습니다.")
        if not any(event['state'] in ['진행중', '진행예정'] for event in events):
            print(f"{page}페이지에서 '진행중' 또는 '진행예정'인 이벤트를 더 이상 찾을 수 없습니다. 중지합니다.")
            break
        page += 1

    # --- 성남시청소년재단 스크레이퍼 ---
    page = 1
    while page <= 5:
        print(f"snyouth.or.kr {page}페이지를 스크래핑하는 중...")
        events = scrape_snyouth_events_page(page)
        if not events:
            print(f"snyouth.or.kr {page}페이지에서 더 이상 이벤트를 찾을 수 없습니다. 중지합니다.")
            break
        all_events.extend(events)
        print(f"{page}페이지에서 {len(events)}개의 이벤트를 찾았습니다.")
        page += 1
        
    # --- 성남아트센터 스크레이퍼 ---
    snart_events = scrape_snart_events()
    all_events.extend(snart_events)

    # --- 맹산환경생태학습원 스크레이퍼 ---
    mpark_events = scrape_mpark_events()
    all_events.extend(mpark_events)

    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=4)

    print(f"스크래핑 완료. 총 {len(all_events)}개의 이벤트를 찾았으며 events.json에 저장했습니다.")


if __name__ == "__main__":
    main()
