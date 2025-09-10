import subprocess
from bs4 import BeautifulSoup
from server.utils.date_parsing import is_within_month

# 소스: 성남시청소년재단
# 링크: https://www.snyouth.or.kr/

__all__ = ["scrape_snyouth_events_page"]


def deep_scrape_snyouth_event_page(link):
    event_data = ""
    try:
        result = subprocess.run(
            ["curl", "-d", "", link],
            capture_output=True, check=True, timeout=30
        )
        try:
            html_content = result.stdout.decode('utf-8')
        except UnicodeDecodeError:
            html_content = result.stdout.decode('euc-kr', errors='ignore')

        soup = BeautifulSoup(html_content, "html.parser")
        event_list = soup.find("div", class_="board-view")

        if not event_list:
            print(f"{link}: 페이지를 찾을 수 없습니다.")
            return ""

        event_data = event_list.get_text(separator="\n", strip=True)

    except subprocess.CalledProcessError as e:
        print(f"{link} 페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
        print(f"표준 오류: {e.stderr.decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"{link} 페이지에서 오류가 발생했습니다: {e}")

    return event_data


def scrape_snyouth_events_page(page_number):
    url = f"https://www.snyouth.or.kr/fmcs/123?page={page_number}"
    events_on_page = []

    try:
        result = subprocess.run(
            ["curl", url], capture_output=True, check=True, timeout=30)
        try:
            html_content = result.stdout.decode('utf-8')
        except UnicodeDecodeError:
            html_content = result.stdout.decode('euc-kr', errors='ignore')

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
            link_tag = title_cell.find("a")
            link = link_tag["href"] if link_tag else ""
            absolute_link = f"https://www.snyouth.or.kr/fmcs/123{link}" if link else ""

            date_cell = event.find_all("td")[4] if len(
                event.find_all("td")) > 4 else None
            date_str = date_cell.get_text(strip=True).replace(
                "등록일자", "") if date_cell else ""

            if not is_within_month(date_str):
                continue

            file_cell = event.find_all("td")[3]
            file_links_abs = file_cell.find_all("a") if file_cell else []
            file_links = [
                f"https://www.snyouth.or.kr{a['href']}" for a in file_links_abs if 'href' in a.attrs]

            events_on_page.append({
                "title": title,
                "link": absolute_link,
                "date": date_str,
                "source": "성남시청소년재단",
                "files": file_links,
                "deep_data": deep_scrape_snyouth_event_page(absolute_link)
            })

    except subprocess.CalledProcessError as e:
        print(f"{page_number}페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
        print(f"표준 오류: {e.stderr.decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"{page_number}페이지에서 오류가 발생했습니다: {e}")

    return events_on_page
