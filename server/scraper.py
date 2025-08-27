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
    # --- 판교복지관 스크레이퍼 ---
    pangyowelfare_events = scrape_pangyowelfare_events_page()
    all_events.extend(pangyowelfare_events)

    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=4)

    print(f"스크래핑 완료. 총 {len(all_events)}개의 이벤트를 찾았으며 events.json에 저장했습니다.")


if __name__ == "__main__":
    main()
