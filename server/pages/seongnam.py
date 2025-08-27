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
            print(f"{link} 페이지를 찾을 수 없습니다.")
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

        event_list = soup.select("ul.n-apl-ls2.event-ls > li")

        if not event_list:
            print(f"{page_number}페이지에서 이벤트 목록을 찾을 수 없습니다.")
            return []

        for event in event_list:
            link_tag = event.find('a')
            if not link_tag:
                continue

            onclick_attr = link_tag.get("onclick", "")
            parts = onclick_attr.split("goView('")
            if len(parts) > 1:
                app_idx = parts[1].split("'")[0]
                absolute_link = f"https://www.seongnam.go.kr/apply/view.do?appIdx={app_idx}"
            else:
                absolute_link = "링크를 찾을 수 없습니다."

            state_tag = event.select_one(".type > span")
            state = state_tag.get_text(strip=True) if state_tag else ""

            if state in ["진행중", "진행예정"]:
                title = event.select_one(".ti").get_text(strip=True)
                date_str = event.select_one(".date").get_text(strip=True)

                category_audience_tag = event.select_one(".type > i")
                category_audience_text = category_audience_tag.get_text(
                    strip=True) if category_audience_tag else "#"
                category, audience = category_audience_text.split(
                    "·") if "·" in category_audience_text else (category_audience_text, "")
                category = category.replace('#', '').strip()
                audience = audience.strip()

                img_tag = event.select_one(".ph img")
                image_src = img_tag['src'] if img_tag else ""

                events_on_page.append({
                    "title": title,
                    "link": absolute_link,
                    "state": state,
                    "category": category,
                    "audience": audience,
                    "image": image_src,
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
