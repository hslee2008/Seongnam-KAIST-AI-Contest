
import subprocess
from urllib.parse import urljoin
import re
from bs4 import BeautifulSoup

from utils.url_parsing import extract_http_url_from_js

# 소스: 한국잡월드
# 링크: https://www.koreajobworld.or.kr/

__all__ = ["scrape_koreajobworld_events_page"]

def deep_scrape_koreajobworld_page(link):
    event_data = ""
    try:
        result = subprocess.run(
            ["curl", link], capture_output=True, check=True, timeout=30)
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


def scrape_koreajobworld_events_page(max_news_pages=5):
    sources = []
    news_base = "https://www.koreajobworld.or.kr/boardList.do?mid=42&menuId=55&bid=1&site=10&portalMenuNo=39"
    print("한국잡월드(새소식&공지) 크롤링 시작...")
    for page in range(1, max_news_pages + 1):
        list_url = f"{news_base}&pageIndex={page}"
        try:
            res = subprocess.run(["curl", list_url],
                                 capture_output=True, check=True, timeout=30)
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

                    title_cell = tr.find(
                        "td", class_="text-left") or (tds[1] if len(tds) > 1 else None)
                    if not title_cell:
                        continue

                    a = title_cell.find("a")
                    title = a.get_text(" ", strip=True) if a else title_cell.get_text(
                        " ", strip=True)

                    raw_href = a.get("href", "") if a else ""
                    raw_onclick = a.get("onclick", "") if a else ""
                    js_url = extract_http_url_from_js(
                        raw_href) or extract_http_url_from_js(raw_onclick)
                    link = js_url if js_url else urljoin(list_url, raw_href) if raw_href and not raw_href.lower(
                    ).startswith("javascript:") else list_url

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
                        "category": "새소식&공지",
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
                    js_url = extract_http_url_from_js(
                        raw_href) or extract_http_url_from_js(raw_onclick)
                    link = js_url if js_url else urljoin(list_url, raw_href) if raw_href and not raw_href.lower(
                    ).startswith("javascript:") else list_url

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
            result = subprocess.run(
                ["curl", url], capture_output=True, check=True, timeout=30)
            try:
                html_content = result.stdout.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                html_content = result.stdout.decode('euc-kr', errors='ignore')
            soup = BeautifulSoup(html_content, "html.parser")

            containers = soup.select(
                "li, article, div.list, div.item, ul li, div.program, div.program_list li")
            if not containers:
                containers = [soup]

            seen = set()
            for c in containers:
                block = c.get_text("\n", strip=True)
                if not any(k in block for k in ["일자", "장소"]):
                    continue

                title = "제목 없음"
                for sel in ["h3", "h4", "dt", "strong", "p", ".title", ".name"]:
                    node = c.select_one(sel) if sel.startswith(
                        ".") else c.find(sel)
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
                    js_url = extract_http_url_from_js(
                        raw_href) or extract_http_url_from_js(raw_onclick)
                    detail_link = js_url if js_url else urljoin(
                        url, raw_href) if raw_href and not raw_href.lower().startswith("javascript:") else ""

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

                deep_text = deep_scrape_koreajobworld_page(
                    detail_link) if detail_link else ""

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

            print(
                f"한국잡월드({category_label})에서 {len([s for s in sources if s['category'] == category_label])}건 누적 수집.")
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
