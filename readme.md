# Yandex Music Playlist Exporter

Export public Yandex Music playlists to text files (song - artist format).

Works on macOS, Linux, and Windows. Uses Chrome via Selenium to scrape playlist pages with virtual scroll support.

Based on [dudelez/yandex-music-playlist-exporter](https://github.com/dudelez/yandex-music-playlist-exporter), rewritten for modern Selenium and cross-platform support.

## Prerequisites

- Python 3.8+
- Google Chrome installed

## Setup

```bash
git clone https://github.com/p0nyque/yandex-music-playlist-exporter-mac.git
cd yandex-music-playlist-exporter-mac
pip install -r requirements.txt
```

ChromeDriver is downloaded automatically via `webdriver-manager`.

## Usage

1. Add your playlist URLs to `playlists.txt`, one per line:

```
https://music.yandex.ru/users/username/playlists/123
https://music.yandex.kz/playlists/some-uuid-here
```

Both `/users/<name>/playlists/<id>` and `/playlists/<uuid>` URL formats are supported.

2. Run the exporter:

```bash
python3 main.py
```

Or specify a custom file:

```bash
python3 main.py my_urls.txt
```

3. Exported playlists are saved to `my_playlists/` as text files named after the playlist title.

## Notes

- Playlists must be set to public in your Yandex Music account settings.
- Do not close or minimize the Chrome window while the script is running. It scrolls through each playlist to load all tracks.
- The script handles Yandex Music's virtual scroll, so large playlists (100+ tracks) are fully exported.

## Output format

Each exported file contains one line per track:

```
Song Name - Artist Name
```
