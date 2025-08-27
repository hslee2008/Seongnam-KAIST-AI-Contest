import subprocess
import json
from urllib.parse import urljoin
import time
from datetime import date, timedelta
import re
from bs4 import BeautifulSoup

from utils.url_parsing import extract_http_url_from_js

# 소스: 성남시청
# 링크: https://www.seongnam.go.kr/apply/event.do

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

# 소스: 성남시청소년재단
# 링크: https://www.snyouth.or.kr/


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
        result = subprocess.run(["curl", url], capture_output=True, check=True, timeout=30)
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

            date_cell = event.find_all("td")[4] if len(event.find_all("td")) > 4 else None
            date_str = date_cell.get_text(strip=True).replace("등록일자", "") if date_cell else ""

            events_on_page.append({
                "title": title,
                "link": absolute_link,
                "state": "진행예정",
                "category": "기타",
                "audience": "",
                "image": "",
                "date": date_str,
                "source": "성남시청소년재단",
                "deep_data": deep_scrape_snyouth_event_page(absolute_link)
            })

    except subprocess.CalledProcessError as e:
        print(f"{page_number}페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
        print(f"표준 오류: {e.stderr.decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"{page_number}페이지에서 오류가 발생했습니다: {e}")

    return events_on_page

# 소스: 성남아트센터
# 링크: https://www.snart.or.kr/

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
                result = subprocess.run(["curl", api_url], capture_output=True, check=True, timeout=30)
                try:
                    html_content = result.stdout.decode('utf-8')
                except UnicodeDecodeError:
                    html_content = result.stdout.decode('euc-kr', errors='ignore')

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
                            "audience": "",
                            "image": absolute_image,
                            "date": event_date,
                            "place": place,
                            "source": "성남아트센터",
                            "deep_data": ""
                        })
                time.sleep(0.1)
            except subprocess.CalledProcessError as e:
                print(f"{date_str} ({type_id}) 페이지에서 curl을 실행하는 중 오류가 발생했습니다: {e}")
                print(f"표준 오류: {e.stderr.decode('utf-8', errors='ignore')}")
            except Exception as e:
                print(f"{date_str} ({type_id}) 페이지에서 오류가 발생했습니다: {e}")
    
    print(f"성남아트센터에서 {len(events_on_site)}개의 이벤트를 찾았습니다.")
    return events_on_site

# 소스: 맹산환경생태학습원
# 링크: https://mpark.seongnam.go.kr:10003

def deep_scrape_mpark_event_page(link):
    event_data = ""
    try:
        result = subprocess.run(["curl", link], capture_output=True, check=True, timeout=30)
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

def scrape_mpark_events():
    base_url = "https://mpark.seongnam.go.kr:10003"
    events_on_site = []
    page = 1
    print("맹산환경생태학습원 스크레이핑 중...")
    while page <= 5:
        list_url = f"{base_url}/main.php?menugrp=040100&master=bbs&act=list&master_sid=3&Page={page}"
        try:
            result = subprocess.run(["curl", list_url], capture_output=True, check=True, timeout=30)
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
                date_str = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                found_count += 1
                events_on_site.append({
                    "title": title,
                    "link": absolute_link,
                    "state": "진행예정",
                    "category": "환경",
                    "audience": "",
                    "image": "",
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


# 소스: 판교환경생태학습원
# 링크: https://ppark.seongnam.go.kr:10013

def deep_scrape_ppark_event_page(b_idx):
    event_data = ""
    try:
        url = "https://ppark.seongnam.go.kr:10013/community/noticeView"
        result = subprocess.run(["curl", "-d", f"b_idx={b_idx}", url], capture_output=True, check=True, timeout=30)
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

def scrape_ppark_events():
    base_url = "https://ppark.seongnam.go.kr:10013"
    events_on_site = []
    page = 1
    print("판교환경생태학습원 스크레이핑 중...")
    while page <= 5:
        list_url = f"{base_url}/community/noticeList"
        try:
            result = subprocess.run(["curl", "-d", f"cPage={page}", list_url], capture_output=True, check=True, timeout=30)
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
                date_str = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                found_count += 1
                events_on_site.append({
                    "title": title,
                    "link": absolute_link,
                    "state": "진행예정",
                    "category": "환경",
                    "audience": "",
                    "image": "",
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

# 소스: 한국잡월드
# 링크: https://www.koreajobworld.or.kr/

def deep_scrape_koreajobworld_page(link):
    event_data = ""
    try:
        result = subprocess.run(["curl", link], capture_output=True, check=True, timeout=30)
        try:
            html_content = result.stdout.decode('utf-8', errors='ignore')
        except UnicodeDecodeError:
            html_content = result.stdout.decode('euc-kr', errors='ignore')

        soup = BeautifulSoup(html_content, "html.parser")
        candidates = [
            ("div", "board-view"), ("div", "view_con"), ("div", "bbs_view"),
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
        try:
            print(f"표준 오류: {e.stderr.decode('utf-8', errors='ignore')}")
        except Exception:
            pass
    except Exception as e:
        print(f"{link} 상세 페이지 처리 오류: {e}")

    return event_data

def scrape_koreajobworld_events(max_news_pages=5):
    sources = []
    news_base = "https://www.koreajobworld.or.kr/boardList.do?mid=42&menuId=55&bid=1&site=10&portalMenuNo=39"
    print("한국잡월드(새소식&공지) 크롤링 시작...")
    for page in range(1, max_news_pages + 1):
        list_url = f"{news_base}&pageIndex={page}"
        try:
            res = subprocess.run(["curl", list_url], capture_output=True, check=True, timeout=30)
            try:
                html = res.stdout.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                html = res.stdout.decode('euc-kr', errors='ignore')
            soup = BeautifulSoup(html, "html.parser")

            rows = soup.select("table tbody tr")
            found = 0
            if rows:
                for tr in rows:
                    tds = tr.find_all("td")
                    if not tds or len(tds) < 2:
                        continue

                    title_cell = tr.find("td", class_="text-left") or (tds[1] if len(tds) > 1 else None)
                    if not title_cell:
                        continue

                    a = title_cell.find("a")
                    title = a.get_text(" ", strip=True) if a else title_cell.get_text(" ", strip=True)

                    raw_href = a.get("href", "") if a else ""
                    raw_onclick = a.get("onclick", "") if a else ""
                    js_url = extract_http_url_from_js(raw_href) or extract_http_url_from_js(raw_onclick)
                    link = js_url if js_url else urljoin(list_url, raw_href) if raw_href and not raw_href.lower().startswith("javascript:") else list_url

                    date_text = ""
                    for td in reversed(tds):
                        txt = td.get_text(" ", strip=True)
                        if re.search(r"\d{4}[.\-]\d{1,2}[.\-]\d{1,2}", txt):
                            date_text = txt
                            break

                    deep_text = deep_scrape_koreajobworld_page(link)
                    sources.append({
                        "title": title or "제목 없음",
                        "link": link,
                        "state": "진행예정",
                        "category": "새소식&공지",
                        "audience": "",
                        "image": "",
                        "date": date_text,
                        "source": "한국잡월드",
                        "deep_data": deep_text
                    })
                    found += 1

            if found == 0:
                anchors = soup.find_all("a", href=True)
                for a in anchors:
                    t = a.get_text(" ", strip=True)
                    if not t:
                        continue
                    href_low = (a.get("href") or "").lower()
                    if any(x in href_low for x in ["#", "login", "sitemap", "facebook", "instagram", "youtube", "blog", "kakao"]):
                        continue

                    raw_href = a.get("href", "") or ""
                    raw_onclick = a.get("onclick", "") or ""
                    js_url = extract_http_url_from_js(raw_href) or extract_http_url_from_js(raw_onclick)
                    link = js_url if js_url else urljoin(list_url, raw_href) if raw_href and not raw_href.lower().startswith("javascript:") else list_url

                    deep_text = deep_scrape_koreajobworld_page(link)
                    if not any(k in (t + " " + deep_text) for k in ["공지", "안내", "모집", "이벤트", "프로그램", "행사"]):
                        continue

                    sources.append({
                        "title": t,
                        "link": link,
                        "state": "진행예정",
                        "category": "새소식&공지",
                        "audience": "",
                        "image": "",
                        "date": "",
                        "source": "한국잡월드",
                        "deep_data": deep_text
                    })

            print(f"한국잡월드(새소식&공지) p{page}: {found}건(테이블기반) 수집")
        except subprocess.CalledProcessError as e:
            print(f"한국잡월드(새소식&공지) 목록 curl 오류 p{page}: {e}")
            try:
                print(f"표준 오류: {e.stderr.decode('utf-8', errors='ignore')}")
            except Exception:
                pass
        except Exception as e:
            print(f"한국잡월드(새소식&공지) 목록 처리 오류 p{page}: {e}")

    card_targets = [
        ("https://www.koreajobworld.or.kr/event/showList.do?site=10&searchEvent=01&portalMenuNo=239", "기획공연·교육문화"),
        ("https://www.koreajobworld.or.kr/event/showList.do?site=10&searchEvent=04&portalMenuNo=247", "이벤트·공모전"),
    ]
    for url, category_label in card_targets:
        print(f"한국잡월드({category_label}) 목록 크롤링: {url}")
        try:
            result = subprocess.run(["curl", url], capture_output=True, check=True, timeout=30)
            try:
                html_content = result.stdout.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                html_content = result.stdout.decode('euc-kr', errors='ignore')
            soup = BeautifulSoup(html_content, "html.parser")

            containers = soup.select("li, article, div.list, div.item, ul li, div.program, div.program_list li")
            if not containers:
                containers = [soup]

            seen = set()
            for c in containers:
                block = c.get_text("\n", strip=True)
                if not any(k in block for k in ["일자", "장소"]):
                    continue

                title = "제목 없음"
                for sel in ["h3", "h4", "dt", "strong", "p", ".title", ".name"]:
                    node = c.select_one(sel) if sel.startswith(".") else c.find(sel)
                    if node:
                        t = node.get_text(" ", strip=True)
                        if t:
                            title = t
                            break
                if title == "제목 없음" and block:
                    title = block.split("\n", 1)[0][:200]

                def pick(pattern):
                    m = re.search(pattern, block)
                    return m.group(1).strip() if m else ""
                date_str = pick(r"일자\s*:\s*([^\n]+)") or \
                           (lambda m: f"{m.group(1)} ~ {m.group(2)}" if (m := re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})\s*[-~–]\s*(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", block)) else "")("") \
                           or (re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", block).group(1) if re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", block) else "")
                place = pick(r"장소\s*:\s*([^\n]+)")

                detail_link = ""
                a = None
                for txt in ["상세", "자세히", "더보기", "상세내용", "detail", "more"]:
                    a = c.find("a", string=re.compile(txt))
                    if a and (a.get("href") or a.get("onclick")):
                        break
                if not (a and (a.get("href") or a.get("onclick"))):
                    a = c.find("a")

                if a:
                    raw_href = a.get("href", "") or ""
                    raw_onclick = a.get("onclick", "") or ""
                    js_url = extract_http_url_from_js(raw_href) or extract_http_url_from_js(raw_onclick)
                    detail_link = js_url if js_url else urljoin(url, raw_href) if raw_href and not raw_href.lower().startswith("javascript:") else ""

                if not detail_link:
                    detail_link = url

                img = ""
                img_tag = c.find("img")
                if img_tag and img_tag.get("src"):
                    img = urljoin(url, img_tag["src"])

                key = (title, detail_link or img or date_str)
                if key in seen:
                    continue
                seen.add(key)

                deep_text = deep_scrape_koreajobworld_page(detail_link) if detail_link else ""

                state = "진행예정"
                if "마감" in (title + " " + block + " " + deep_text):
                    state = "마감"

                sources.append({
                    "title": title,
                    "link": detail_link,
                    "state": state,
                    "category": category_label,
                    "audience": "",
                    "image": img,
                    "date": date_str,
                    "place": place,
                    "source": "한국잡월드",
                    "deep_data": deep_text
                })

            print(f"한국잡월드({category_label})에서 {len([s for s in sources if s['category']==category_label])}건 누적 수집.")
        except subprocess.CalledProcessError as e:
            print(f"한국잡월드({category_label}) 목록 curl 오류: {e}")
            try:
                print(f"표준 오류: {e.stderr.decode('utf-8', errors='ignore')}")
            except Exception:
                pass
        except Exception as e:
            print(f"한국잡월드({category_label}) 목록 처리 오류: {e}")

    print(f"한국잡월드 총 {len(sources)}건 수집 완료.")
    return sources

# 소스: 성남문화원
# 링크: https://www.seongnamculture.or.kr/

def deep_scrape_seongnamculture_event_page(link):
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

def scrape_seongnamculture_events(max_pages=5):
    base_url = "https://www.seongnamculture.or.kr"
    events_on_site = []
    page = 1
    print("성남문화원 스크레이핑 중...")
    while page <= max_pages:
        list_url = f"{base_url}/sub/community_01.html?Table=ins_bbs1&page={page}"
        try:
            result = subprocess.run(["curl", list_url], capture_output=True, check=True, timeout=30)
            try:
                html_content = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                html_content = result.stdout.decode('euc-kr', errors='ignore')

            soup = BeautifulSoup(html_content, "html.parser")
            notice_list = soup.select('table[cellspacing="1"] tr[bgcolor="#FFFFFF"]')

            if not notice_list or len(notice_list) <= 1:
                print(f"{page}페이지에서 공지사항 목록을 찾을 수 없습니다.")
                break

            found_count = 0
            for notice in notice_list:
                if not notice.find_all('td'):
                    continue
                
                cells = notice.find_all('td')
                if len(cells) < 6:
                    continue
                title_cell = cells[2]
                
                title = title_cell.get_text(strip=True)
                link_tag = title_cell.find('a')
                relative_link = link_tag['href'] if link_tag else None

                if not relative_link:
                    continue

                absolute_link = urljoin(base_url, relative_link)
                
                cells = notice.find_all("td")
                date_str = cells[-1].get_text(strip=True) if len(cells) >= 2 else ""
                
                deep_text = deep_scrape_seongnamculture_event_page(absolute_link)
                state = "진행예정"
                if "마감" in (title + " " + deep_text):
                    state = "마감"

                events_on_site.append({
                    "title": title,
                    "link": absolute_link,
                    "state": state,
                    "category": "문화",
                    "audience": "",
                    "image": "",
                    "date": date_str,
                    "source": "성남문화원",
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
            
    print(f"성남문화원에서 총 {len(events_on_site)}개의 이벤트를 찾았습니다.")
    return events_on_site

def main():
    all_events = []

    #--- 성남시청 스크레이퍼 ---
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
    print("snyouth.or.kr 1페이지를 스크래핑하는 중...")
    events = scrape_snyouth_events_page(1)
    if not events:
        print("snyouth.or.kr 1페이지에서 더 이상 이벤트를 찾을 수 없습니다. 중지합니다.")
    all_events.extend(events)
    print(f"1페이지에서 {len(events)}개의 이벤트를 찾았습니다.")
        
    # --- 맹산환경생태학습원 스크레이퍼 ---
    mpark_events = scrape_mpark_events()
    all_events.extend(mpark_events)
    # --- 성남아트센터 스크레이퍼 ---
    snart_events = scrape_snart_events()
    all_events.extend(snart_events)
    # --- 판교환경생태학습원 스크레이퍼 ---
    ppark_events = scrape_ppark_events()
    all_events.extend(ppark_events)
    # --- 한국잡월드 스크레이퍼 ---
    koreajobworld_events = scrape_koreajobworld_events()
    all_events.extend(koreajobworld_events)
    #ㄷ--- 성남문화원 스크레이퍼 ---
    seongnamculture_events = scrape_seongnamculture_events()
    all_events.extend(seongnamculture_events)

    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=4)

    print(f"스크래핑 완료. 총 {len(all_events)}개의 이벤트를 찾았으며 events.json에 저장했습니다.")

if __name__ == "__main__":
    main()