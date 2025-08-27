import json

from pages.seongnam import scrape_seongnam_events_page
from pages.snyouth import scrape_snyouth_events_page
from pages.snart import scrape_snart_events_page
from pages.mpark import scrape_mpark_events_page
from pages.ppark import scrape_ppark_events_page
from pages.koreajobworld import scrape_koreajobworld_events_page
from pages.seongnamculture import scrape_seongnamculture_events_page
from pages.pangyomeseum import scrape_pangyomuseum_events_page
from pages.pangyowelfare import scrape_pangyowelfare_events_page

#소스: 판교종합사회복지관
#링크: https://xn--zb0byf185bxsd8wmczbx22apne40c.kr/notice

def deep_scrape_pangyowelfare_event_page(link):
    event_data = ""
    try:
        result = subprocess.run(["curl", link], capture_output=True, check=True, timeout=30)
        try:
            html_content = result.stdout.decode('utf-8')
        except UnicodeDecodeError:
            html_content = result.stdout.decode('euc-kr', errors='ignore')

        soup = BeautifulSoup(html_content, "html.parser")
        candidates = [
            ("div", "board_view"), ("div", "view_con"), ("div", "bbs_view"),
            ("div", "contents"), ("div", "content"), ("article", None),
            ("section", None), ("div", "sub")
        ]
        for name, cls in candidates:
            node = soup.find(name, class_=cls) if cls else soup.find(name)
            if node:
                event_data = node.get_text(separator="\n", strip=True)
                if event_data:
                    break

        if not event_data:
            for t in soup(["script", "style", "noscript"]):
                t.extract()
            event_data = soup.get_text(separator="\n", strip=True)[:7000]

    except subprocess.CalledProcessError as e:
        print(f"{link} 상세 페이지 curl 오류: {e}")
        print(f"표준 오류: {e.stderr.decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"{link} 상세 페이지 처리 오류: {e}")

    return event_data

def scrape_pangyowelfare_events(max_pages=5):
    base_url = "https://xn--zb0byf185bxsd8wmczbx22apne40c.kr"
    events_on_site = []
    page = 1
    print("판교종합사회복지관 스크레이핑 중...")
    while page <= max_pages:
        list_url = f"{base_url}/notice?page={page}"
        try:
            result = subprocess.run(["curl", list_url], capture_output=True, check=True, timeout=30)
            try:
                html_content = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                html_content = result.stdout.decode('euc-kr', errors='ignore')

            soup = BeautifulSoup(html_content, "html.parser")
            notice_list = soup.select("table tbody tr")

            if not notice_list or len(notice_list) <= 1:
                print(f"{page}페이지에서 공지사항 목록을 찾을 수 없습니다.")
                break

            found_count = 0
            for notice in notice_list:
                if not notice.find_all('td'):
                    continue
                
                cells = notice.find_all('td')
                if len(cells) < 5:
                    continue
                title_cell = cells[1]
                
                title = title_cell.get_text(strip=True)
                link_tag = title_cell.find('a')
                relative_link = link_tag['href'] if link_tag else None

                if not relative_link:
                    continue

                absolute_link = urljoin(base_url, relative_link)
                
                date_str = cells[4].get_text(strip=True) if len(cells) >= 5 else ""
                
                deep_text = deep_scrape_pangyowelfare_event_page(absolute_link)
                state = "진행예정"
                if "마감" in (title + " " + deep_text):
                    state = "마감"

                events_on_site.append({
                    "title": title,
                    "link": absolute_link,
                    "state": state,
                    "category": "복지",
                    "audience": "",
                    "image": "",
                    "date": date_str,
                    "source": "판교종합사회복지관",
                    "deep_data": deep_text
                })
                found_count += 1
            
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
            
    print(f"판교종합사회복지관에서 총 {len(events_on_site)}개의 이벤트를 찾았습니다.")
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
    events = scrape_snyouth_events_page(1)
    all_events.extend(events)
    # --- 맹산환경생태학습원 스크레이퍼 ---
    mpark_events = scrape_mpark_events_page()
    all_events.extend(mpark_events)
    # --- 성남아트센터 스크레이퍼 ---
    snart_events = scrape_snart_events_page()
    all_events.extend(snart_events)
    # --- 판교환경생태학습원 스크레이퍼 ---
    ppark_events = scrape_ppark_events_page()
    all_events.extend(ppark_events)
    # --- 한국잡월드 스크레이퍼 ---
    koreajobworld_events = scrape_koreajobworld_events_page()
    all_events.extend(koreajobworld_events)
    # --- 성남문화원 스크레이퍼 ---
    seongnamculture_events = scrape_seongnamculture_events_page()
    all_events.extend(seongnamculture_events)
    # --- 판교박물관 스크레이퍼 ---
    pangyomuseum_events = scrape_pangyomuseum_events_page()
    all_events.extend(pangyomuseum_events)

    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=4)

    print(f"스크래핑 완료. 총 {len(all_events)}개의 이벤트를 찾았으며 events.json에 저장했습니다.")


if __name__ == "__main__":
    main()
