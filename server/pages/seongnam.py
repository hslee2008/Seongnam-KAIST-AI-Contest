import subprocess
from bs4 import BeautifulSoup

# 소스: 성남시청
# 링크: https://www.seongnam.go.kr/apply/event.do


__all__ = ["scrape_seongnam_events_page"]


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
                app_idx = app_idx_parts[1].split("'")[0]
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
