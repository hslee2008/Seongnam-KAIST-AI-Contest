import subprocess
import json
from bs4 import BeautifulSoup


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
            date = text_span.find("span", class_="date").get_text(
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
                    "audience": category.split("·")[1].strip(),
                    "image": "https://www.seongnam.go.kr" + image_src,
                    "date": date,
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
소스: 성남시총서년청년재단
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
            absolute_link = f"https://www.snyouth.or.kr/fmcs/123{link}"

            date_cell = event.find_all("td")[4]
            date = date_cell.get_text(strip=True).replace("등록일자", "")

            events_on_page.append({
                "title": title,
                "link": absolute_link,
                "state": "진행예정",
                "category": "기타",
                "date": date,
                "source": "성남시청소년재단",
                "deep_data": deep_scrape_snyouth_event_page(absolute_link)
            })

    except subprocess.CalledProcessError as e:
        print(f"{page_number}페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
        print(f"표준 오류: {e.stderr}")

    except Exception as e:
        print(f"{page_number}페이지에서 오류가 발생했습니다: {e}")

    return events_on_page


def main():
    all_events = []

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

    page = 1
    while True:
        print(f"snyouth.or.kr {page}페이지를 스크래핑하는 중...")

        events = scrape_snyouth_events_page(page)

        if not events:
            print(f"snyouth.or.kr {page}페이지에서 더 이상 이벤트를 찾을 수 없습니다. 중지합니다.")
            break

        all_events.extend(events)
        print(f"{page}페이지에서 {len(events)}개의 이벤트를 찾았습니다.")

        page += 1

    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=4)

    print(f"스크래핑 완료. 총 {len(all_events)}개의 이벤트를 찾았으며 events.json에 저장했습니다.")


if __name__ == "__main__":
    main()
