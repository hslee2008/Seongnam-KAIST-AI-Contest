
import subprocess
import time
import re
from bs4 import BeautifulSoup

# 소스: 판교환경생태학습원
# 링크: https://ppark.seongnam.go.kr:10013

__all__ = ["scrape_ppark_events_page"]

def deep_scrape_ppark_event_page(b_idx):
    event_data = ""
    try:
        url = "https://ppark.seongnam.go.kr:10013/community/noticeView"
        result = subprocess.run(
            ["curl", "-d", f"b_idx={b_idx}", url], capture_output=True, check=True, timeout=30)
        try:
            html_content = result.stdout.decode('utf-8')
        except UnicodeDecodeError:
            html_content = result.stdout.decode('euc-kr', errors='ignore')

        soup = BeautifulSoup(html_content, "html.parser")
        content_div = soup.find("div", class_="view_con")
        if content_div:
            event_data = content_div.get_text(separator="\n", strip=True)
    except subprocess.CalledProcessError as e:
        print(f"판교 상세 페이지({b_idx})에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
        print(f"표준 오류: {e.stderr.decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"판교 상세 페이지({b_idx})에서 오류가 발생했습니다: {e}")
    return event_data


def scrape_ppark_events_page():
    base_url = "https://ppark.seongnam.go.kr:10013"
    events_on_site = []
    page = 1
    print("판교환경생태학습원 스크레이핑 중...")
    while page <= 5:
        list_url = f"{base_url}/community/noticeList"
        try:
            result = subprocess.run(
                ["curl", "-d", f"cPage={page}", list_url], capture_output=True, check=True, timeout=30)
            try:
                html_content = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                html_content = result.stdout.decode('euc-kr', errors='ignore')

            soup = BeautifulSoup(html_content, "html.parser")
            notice_list = soup.select("table.bbs_list1 tbody tr")

            if not notice_list:
                break

            found_count = 0
            for notice in notice_list:
                title_cell = notice.find("td", class_="text-left")
                if not title_cell:
                    continue

                title = title_cell.get_text(strip=True)
                link_tag = title_cell.find('a')
                onclick_attr = link_tag.get("onclick", "") if link_tag else ""

                match = re.search(r"goView\('(\d+)'\)", onclick_attr)
                if not match:
                    continue

                b_idx = match.group(1)
                absolute_link = f"{base_url}/community/noticeView?b_idx={b_idx}"

                cells = notice.find_all("td")
                date_str = cells[2].get_text(
                    strip=True) if len(cells) > 2 else ""
                found_count += 1
                events_on_site.append({
                    "title": title,
                    "link": absolute_link,
                    "category": "환경",
                    "date": date_str,
                    "source": "판교환경생태학습원",
                    "deep_data": deep_scrape_ppark_event_page(b_idx)
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

    print(f"판교환경생태학습원에서 총 {len(events_on_site)}개의 이벤트를 찾았습니다.")
    return events_on_site
