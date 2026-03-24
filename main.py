import os
import sys
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

file_name = "playlists.txt"
if len(sys.argv) > 1:
    file_name = sys.argv[1]

if not os.path.exists(file_name):
    print(f"Error: File '{file_name}' not found.")
    exit(1)

with open(file_name, "r") as f:
    urls = [line.strip() for line in f.readlines() if line.strip()]

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)


def extract_tracks(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    titles = soup.find_all(class_=lambda c: c and 'Meta_title__' in c)
    artists_divs = soup.find_all(class_=lambda c: c and 'Meta_artists__' in c)

    tracks = []
    seen = set()
    for title_el, artist_el in zip(titles, artists_divs):
        song = title_el.text.strip()
        artist = artist_el.text.strip()
        key = (song, artist)
        if key not in seen:
            seen.add(key)
            tracks.append(key)
    return tracks, seen


for idx, url in enumerate(urls, start=1):
    print(f"\n[{idx}/{len(urls)}] Processing: {url}")
    driver.get(url)
    time.sleep(8)

    # Get playlist title
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    h1 = soup.find('h1')
    playlist_title = h1.text.strip() if h1 else None
    print(f"  Playlist: {playlist_title or 'Unknown'}")

    # Scroll the VirtualScroll_scroller element to load all tracks
    all_tracks = []
    all_seen = set()
    no_new = 0
    max_no_new = 5
    scroll_pos = 0
    scroll_step = 600

    while no_new < max_no_new:
        tracks, seen = extract_tracks(driver)
        new_found = seen - all_seen
        if new_found:
            for t in tracks:
                if t not in all_seen:
                    all_tracks.append(t)
                    all_seen.add(t)
            print(f"  Loaded {len(all_tracks)} tracks...")
            no_new = 0
        else:
            no_new += 1

        scroll_pos += scroll_step
        driver.execute_script(f"""
            var scroller = document.querySelector('[class*="VirtualScroll_scroller"]');
            if (scroller) {{
                scroller.scrollTop = {scroll_pos};
            }}
        """)
        time.sleep(1)

    # One final extraction
    tracks, seen = extract_tracks(driver)
    for t in tracks:
        if t not in all_seen:
            all_tracks.append(t)
            all_seen.add(t)

    # Extract playlist ID from URL
    match = re.search(r"/users/([^/]+)/playlists/(\d+)", url)
    if match:
        user_name, playlist_id = match.groups()
    else:
        uuid_match = re.search(r"/playlists/([a-f0-9-]+)", url)
        playlist_id = uuid_match.group(1) if uuid_match else str(idx)
        user_name = "exported"

    user_dir = os.path.join("my_playlists", user_name)
    os.makedirs(user_dir, exist_ok=True)

    if playlist_title:
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', playlist_title)[:80]
        playlist_file_name = os.path.join(user_dir, f"{safe_title}.txt")
    else:
        playlist_file_name = os.path.join(user_dir, f"{playlist_id}.txt")

    if all_tracks:
        with open(playlist_file_name, "w", encoding="utf-8") as f:
            for song, artist in all_tracks:
                f.write(f"{song} - {artist}\n")
        print(f"  Exported {len(all_tracks)} songs to {playlist_file_name}")
    else:
        print(f"  Warning: No songs found in {url}")

driver.quit()
print("\nDone! All playlists processed.")
