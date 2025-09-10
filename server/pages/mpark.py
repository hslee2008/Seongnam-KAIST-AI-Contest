import subprocess
import time
from bs4 import BeautifulSoup
from utils.date_parsing import is_within_month

# 소스: 맹산환경생태학습원
# 링크: https://mpark.seongnam.go.kr:10003

__all__ = ["scrape_mpark_events_page"]

def deep_scrape_mpark_event_page(link):
    event_data = ""
    try:
        result = subprocess.run(
            ["curl", link], capture_output=True, check=True, timeout=30)
        try:
            html_content = result.stdout.decode('utf-8')
        except UnicodeDecodeError:
            html_content = result.stdout.decode('euc-kr', errors='ignore')

        soup = BeautifulSoup(html_content, "html.parser")
        content_div = soup.find("div", class_="bbsContents")
        if content_div:
            event_data = content_div.get_text(separator="\n", strip=True)
    except subprocess.CalledProcessError as e:
        print(f"{link} 페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
        print(f"표준 오류: {e.stderr.decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"{link} 페이지에서 오류가 발생했습니다: {e}")
    return event_data


def scrape_mpark_events_page():
    base_url = "https://mpark.seongnam.go.kr:10003"
    events_on_site = []
    page = 1
    print("맹산환경생태학습원 스크레이핑 중...")
    while page <= 5:
        list_url = f"{base_url}/main.php?menugrp=040100&master=bbs&act=list&master_sid=3&Page={page}"
        try:
            result = subprocess.run(
                ["curl", list_url], capture_output=True, check=True, timeout=30)
            try:
                html_content = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                html_content = result.stdout.decode('euc-kr', errors='ignore')

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
                date_str = cells[3].get_text(
                    strip=True) if len(cells) > 3 else ""
                found_count += 1
                
                if not is_within_month(date_str):
                    continue
                
                events_on_site.append({
                    "title": title,
                    "link": absolute_link,
                    "category": "환경",
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
            print(f"표준 오류: {e.stderr.decode('utf-8', errors='ignore')}")
            break
        except Exception as e:
            print(f"{list_url} 페이지에서 오류가 발생했습니다: {e}")
            break

    print(f"맹산환경생태학습원에서 총 {len(events_on_site)}개의 이벤트를 찾았습니다.")
    return events_on_site
