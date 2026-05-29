#!/usr/bin/env python3
"""
artist-image-fetcher.py

Fetch artist/band images and logos for Clipped video generation.

Sources:
  - Last.fm: artist images via API response when available
  - Spotify: artist images via Client Credentials API
  - Discogs: artist profile images via API
  - TheAudioDB: transparent logos and artist thumbs
  - MusicBrainz + Fanart.tv: transparent clearlogos
  - Metal Archives: metal logos/photos fallback

Outputs per artist:
  artist.jpg
  logo.png
  metadata.json

Safe defaults:
  - Will not overwrite existing images unless --force is used
  - Supports --dry-run
  - Validates downloaded files as real images
  - Uses env vars for API tokens

Required:
  python3 -m pip install requests pillow beautifulsoup4

Optional API env vars:
  export LASTFM_API_KEY="..."
  export SPOTIFY_CLIENT_ID="..."
  export SPOTIFY_CLIENT_SECRET="..."
  export DISCOGS_USER_TOKEN="..."
  export FANART_API_KEY="..."

Examples:
  # Single artist folder
  artist-image-fetcher.py "/Volumes/Eksternal/Audio/Metal/D/Death"

  # Direct artist name into an output directory
  artist-image-fetcher.py --artist "Death" --out "/tmp/clipped-assets/Death"

  # One letter in your library
  artist-image-fetcher.py --letter D --genre Metal

  # Whole genre, preview only
  artist-image-fetcher.py --all --genre Metal --dry-run

  # Prefer Spotify/Discogs/Last.fm first for artist photos
  artist-image-fetcher.py --artist "Nas" --out "/tmp/nas" --photo-sources spotify,discogs,lastfm,audiodb,metallum

  # Prefer transparent logos first
  artist-image-fetcher.py --artist "Death" --out "/tmp/death" --logo-sources audiodb,fanart,metallum
"""

from __future__ import annotations

import argparse
import base64
import imghdr
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
from urllib.parse import quote, urljoin

import requests


AUDIODB_API_BASE = "https://www.theaudiodb.com/api/v1/json/2"
FANART_API_BASE = "https://webservice.fanart.tv/v3/music"
MUSICBRAINZ_API_BASE = "https://musicbrainz.org/ws/2"
LASTFM_API_BASE = "https://ws.audioscrobbler.com/2.0/"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"
DISCOGS_API_BASE = "https://api.discogs.com"


IMAGE_EXTS = {
    "jpeg": ".jpg",
    "jpg": ".jpg",
    "png": ".png",
    "webp": ".webp",
    "gif": ".gif",
}


@dataclass
class ImageCandidate:
    kind: str              # "photo" or "logo"
    source: str
    url: str
    score: int = 0
    width: int | None = None
    height: int | None = None
    transparent: bool = False
    notes: str = ""


class ArtistImageFetcher:
    def __init__(
        self,
        base_path: str = "/Volumes/Eksternal/Audio",
        force: bool = False,
        dry_run: bool = False,
        verbose: bool = False,
        sleep: float = 0.35,
    ) -> None:
        self.base_path = Path(base_path)
        self.force = force
        self.dry_run = dry_run
        self.verbose = verbose
        self.sleep = sleep

        self.lastfm_api_key = os.environ.get("LASTFM_API_KEY", "")
        self.spotify_client_id = os.environ.get("SPOTIFY_CLIENT_ID", "")
        self.spotify_client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
        self.discogs_token = os.environ.get("DISCOGS_USER_TOKEN", "")
        self.fanart_api_key = os.environ.get("FANART_API_KEY", "")

        self._spotify_token: str | None = None

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ClippedArtistImageFetcher/1.0 (+local macOS media toolkit)",
            "Accept": "application/json,text/html,*/*",
        })

        self.stats = {
            "processed": 0,
            "photos_downloaded": 0,
            "logos_downloaded": 0,
            "skipped": 0,
            "failed": 0,
        }

    # ---------------------------------------------------------------------
    # Logging
    # ---------------------------------------------------------------------

    def log(self, msg: str) -> None:
        print(msg)

    def debug(self, msg: str) -> None:
        if self.verbose:
            print(f"  {msg}")

    # ---------------------------------------------------------------------
    # Generic helpers
    # ---------------------------------------------------------------------

    def safe_name(self, name: str) -> str:
        return re.sub(r"[/:]+", "_", name).strip()

    def get_albums_from_folder(self, artist_folder: Path) -> list[str]:
        albums: list[str] = []
        if not artist_folder.exists():
            return albums

        for item in artist_folder.iterdir():
            if not item.is_dir() or item.name.startswith("."):
                continue
            album_name = item.name
            album_name = album_name.split(" - ", 1)[-1]
            album_name = album_name.split(" (", 1)[0]
            album_name = album_name.strip()
            if album_name:
                albums.append(album_name.lower())
        return albums

    def image_is_valid(self, path: Path) -> bool:
        if not path.exists() or path.stat().st_size < 512:
            return False

        kind = imghdr.what(path)
        if kind in IMAGE_EXTS:
            return True

        # Pillow gives better validation if installed.
        try:
            from PIL import Image
            with Image.open(path) as img:
                img.verify()
            return True
        except Exception:
            return False

    def pick_ext_from_url_or_content(self, url: str, content_type: str = "") -> str:
        lowered = url.lower().split("?", 1)[0]
        for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
            if lowered.endswith(ext):
                return ".jpg" if ext == ".jpeg" else ext

        if "png" in content_type:
            return ".png"
        if "webp" in content_type:
            return ".webp"
        if "gif" in content_type:
            return ".gif"
        return ".jpg"

    def download_image(self, candidate: ImageCandidate, output_path: Path) -> bool:
        self.log(f"⬇ {candidate.kind}: {candidate.source} → {output_path.name}")

        if self.dry_run:
            self.log(f"  DRY-RUN would download: {candidate.url}")
            return True

        output_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")

        try:
            headers = {
                "User-Agent": "ClippedArtistImageFetcher/1.0",
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            }
            with self.session.get(candidate.url, headers=headers, timeout=30, stream=True) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")

                if "text/html" in content_type.lower():
                    self.debug(f"Rejected HTML response from {candidate.url}")
                    return False

                with tmp_path.open("wb") as fh:
                    for chunk in response.iter_content(chunk_size=1024 * 64):
                        if chunk:
                            fh.write(chunk)

            if not self.image_is_valid(tmp_path):
                self.debug(f"Invalid image downloaded: {tmp_path}")
                tmp_path.unlink(missing_ok=True)
                return False

            tmp_path.replace(output_path)
            return True

        except Exception as exc:
            self.debug(f"Download failed: {exc}")
            tmp_path.unlink(missing_ok=True)
            return False

    def write_metadata(self, out_dir: Path, metadata: dict[str, Any]) -> None:
        if self.dry_run:
            return
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "metadata.json"
        path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------------------------------------------------------------------
    # Last.fm
    # ---------------------------------------------------------------------

    def get_lastfm_photos(self, artist_name: str) -> list[ImageCandidate]:
        if not self.lastfm_api_key:
            self.debug("Last.fm skipped: LASTFM_API_KEY not set")
            return []

        try:
            params = {
                "method": "artist.getinfo",
                "artist": artist_name,
                "api_key": self.lastfm_api_key,
                "format": "json",
                "autocorrect": 1,
            }
            self.debug(f"Last.fm: searching {artist_name}")
            response = self.session.get(LASTFM_API_BASE, params=params, timeout=12)
            response.raise_for_status()
            data = response.json()

            artist = data.get("artist") or {}
            images = artist.get("image") or []
            candidates: list[ImageCandidate] = []

            size_scores = {
                "small": 10,
                "medium": 20,
                "large": 30,
                "extralarge": 40,
                "mega": 50,
            }

            for img in images:
                url = img.get("#text") or ""
                if not url:
                    continue
                size = img.get("size", "")
                candidates.append(ImageCandidate(
                    kind="photo",
                    source="lastfm",
                    url=url,
                    score=size_scores.get(size, 1),
                    notes=f"lastfm size={size}",
                ))

            candidates.sort(key=lambda c: c.score, reverse=True)
            return candidates

        except Exception as exc:
            self.debug(f"Last.fm error: {exc}")
            return []

    # ---------------------------------------------------------------------
    # Spotify
    # ---------------------------------------------------------------------

    def get_spotify_token(self) -> str | None:
        if self._spotify_token:
            return self._spotify_token

        if not self.spotify_client_id or not self.spotify_client_secret:
            self.debug("Spotify skipped: SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET not set")
            return None

        try:
            raw = f"{self.spotify_client_id}:{self.spotify_client_secret}".encode("utf-8")
            auth = base64.b64encode(raw).decode("ascii")
            headers = {"Authorization": f"Basic {auth}"}
            data = {"grant_type": "client_credentials"}

            response = self.session.post(SPOTIFY_TOKEN_URL, headers=headers, data=data, timeout=12)
            response.raise_for_status()
            self._spotify_token = response.json().get("access_token")
            return self._spotify_token

        except Exception as exc:
            self.debug(f"Spotify token error: {exc}")
            return None

    def get_spotify_photos(self, artist_name: str) -> list[ImageCandidate]:
        token = self.get_spotify_token()
        if not token:
            return []

        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"q": artist_name, "type": "artist", "limit": 5}
            self.debug(f"Spotify: searching {artist_name}")

            response = self.session.get(
                f"{SPOTIFY_API_BASE}/search",
                headers=headers,
                params=params,
                timeout=12,
            )
            response.raise_for_status()
            data = response.json()

            items = ((data.get("artists") or {}).get("items") or [])
            candidates: list[ImageCandidate] = []

            for idx, artist in enumerate(items):
                name = artist.get("name", "")
                images = artist.get("images") or []
                popularity = int(artist.get("popularity") or 0)

                # Prefer exact-ish name matches, then largest images.
                name_bonus = 50 if name.lower() == artist_name.lower() else 0
                rank_penalty = idx * 5

                for img in images:
                    url = img.get("url")
                    width = img.get("width")
                    height = img.get("height")
                    if not url:
                        continue
                    pixel_score = int(((width or 0) * (height or 0)) / 10000)
                    candidates.append(ImageCandidate(
                        kind="photo",
                        source="spotify",
                        url=url,
                        score=name_bonus + popularity + pixel_score - rank_penalty,
                        width=width,
                        height=height,
                        notes=f"spotify artist={name}",
                    ))

            candidates.sort(key=lambda c: c.score, reverse=True)
            return candidates

        except Exception as exc:
            self.debug(f"Spotify error: {exc}")
            return []

    # ---------------------------------------------------------------------
    # Discogs
    # ---------------------------------------------------------------------

    def get_discogs_photos(self, artist_name: str) -> list[ImageCandidate]:
        if not self.discogs_token:
            self.debug("Discogs skipped: DISCOGS_USER_TOKEN not set")
            return []

        try:
            headers = {
                "Authorization": f"Discogs token={self.discogs_token}",
                "User-Agent": "ClippedArtistImageFetcher/1.0",
            }
            params = {
                "q": artist_name,
                "type": "artist",
                "per_page": 5,
            }

            self.debug(f"Discogs: searching {artist_name}")
            response = self.session.get(
                f"{DISCOGS_API_BASE}/database/search",
                headers=headers,
                params=params,
                timeout=12,
            )
            response.raise_for_status()
            results = response.json().get("results") or []

            candidates: list[ImageCandidate] = []

            for idx, item in enumerate(results):
                title = item.get("title", "")
                cover = item.get("cover_image") or item.get("thumb") or ""
                resource_url = item.get("resource_url") or ""

                name_bonus = 50 if title.lower() == artist_name.lower() else 0
                rank_penalty = idx * 5

                if cover and "spacer.gif" not in cover:
                    candidates.append(ImageCandidate(
                        kind="photo",
                        source="discogs",
                        url=cover,
                        score=name_bonus + 40 - rank_penalty,
                        notes=f"discogs result={title}",
                    ))

                # Fetch artist resource for better images.
                if resource_url:
                    try:
                        time.sleep(self.sleep)
                        detail = self.session.get(resource_url, headers=headers, timeout=12)
                        detail.raise_for_status()
                        detail_data = detail.json()
                        images = detail_data.get("images") or []
                        for img in images:
                            uri = img.get("uri") or img.get("resource_url") or ""
                            if not uri:
                                continue
                            width = img.get("width")
                            height = img.get("height")
                            img_type = img.get("type", "")
                            candidates.append(ImageCandidate(
                                kind="photo",
                                source="discogs",
                                url=uri,
                                score=name_bonus + 60 + (10 if img_type == "primary" else 0) - rank_penalty,
                                width=width,
                                height=height,
                                notes=f"discogs artist={title} type={img_type}",
                            ))
                    except Exception as exc:
                        self.debug(f"Discogs detail skipped: {exc}")

            candidates.sort(key=lambda c: c.score, reverse=True)
            return candidates

        except Exception as exc:
            self.debug(f"Discogs error: {exc}")
            return []

    # ---------------------------------------------------------------------
    # TheAudioDB
    # ---------------------------------------------------------------------

    def get_audiodb_images(self, artist_name: str) -> list[ImageCandidate]:
        try:
            search_url = f"{AUDIODB_API_BASE}/search.php"
            params = {"s": artist_name}
            self.debug(f"AudioDB: searching {artist_name}")

            response = self.session.get(search_url, params=params, timeout=12)
            response.raise_for_status()
            artists = response.json().get("artists") or []
            if not artists:
                return []

            candidates: list[ImageCandidate] = []
            for idx, artist in enumerate(artists[:3]):
                name = artist.get("strArtist", "")
                name_bonus = 50 if name.lower() == artist_name.lower() else 0
                rank_penalty = idx * 8

                logo = artist.get("strArtistLogo")
                if logo:
                    candidates.append(ImageCandidate(
                        kind="logo",
                        source="audiodb",
                        url=logo,
                        score=name_bonus + 80 - rank_penalty,
                        transparent=True,
                        notes=f"audiodb artist={name}",
                    ))

                for key, base_score in (
                    ("strArtistThumb", 70),
                    ("strArtistFanart", 65),
                    ("strArtistFanart2", 60),
                    ("strArtistFanart3", 55),
                    ("strArtistFanart4", 50),
                ):
                    url = artist.get(key)
                    if url:
                        candidates.append(ImageCandidate(
                            kind="photo",
                            source="audiodb",
                            url=url,
                            score=name_bonus + base_score - rank_penalty,
                            notes=f"audiodb artist={name} field={key}",
                        ))

            candidates.sort(key=lambda c: c.score, reverse=True)
            return candidates

        except Exception as exc:
            self.debug(f"AudioDB error: {exc}")
            return []

    # ---------------------------------------------------------------------
    # MusicBrainz + Fanart.tv
    # ---------------------------------------------------------------------

    def get_musicbrainz_mbid(self, artist_name: str) -> str | None:
        try:
            params = {
                "query": f'artist:"{artist_name}"',
                "fmt": "json",
                "limit": 3,
            }
            headers = {
                "User-Agent": "ClippedArtistImageFetcher/1.0 (local)",
                "Accept": "application/json",
            }

            self.debug(f"MusicBrainz: searching {artist_name}")
            response = self.session.get(
                f"{MUSICBRAINZ_API_BASE}/artist",
                params=params,
                headers=headers,
                timeout=12,
            )
            response.raise_for_status()
            artists = response.json().get("artists") or []
            if not artists:
                return None

            # Prefer exact name, else first result.
            for artist in artists:
                if (artist.get("name") or "").lower() == artist_name.lower():
                    return artist.get("id")

            return artists[0].get("id")

        except Exception as exc:
            self.debug(f"MusicBrainz error: {exc}")
            return None

    def get_fanart_logos(self, artist_name: str) -> list[ImageCandidate]:
        if not self.fanart_api_key:
            self.debug("Fanart.tv skipped: FANART_API_KEY not set")
            return []

        mbid = self.get_musicbrainz_mbid(artist_name)
        if not mbid:
            return []

        try:
            params = {"api_key": self.fanart_api_key}
            self.debug(f"Fanart.tv: fetching {mbid}")
            response = self.session.get(f"{FANART_API_BASE}/{mbid}", params=params, timeout=12)
            response.raise_for_status()
            data = response.json()

            candidates: list[ImageCandidate] = []

            for key, base_score in (
                ("artistclearlogo", 90),
                ("hdmusiclogo", 85),
                ("musiclogo", 80),
            ):
                for idx, img in enumerate(data.get(key) or []):
                    url = img.get("url")
                    if not url:
                        continue
                    likes = int(img.get("likes") or 0)
                    candidates.append(ImageCandidate(
                        kind="logo",
                        source="fanart",
                        url=url,
                        score=base_score + likes - idx,
                        transparent=True,
                        notes=f"fanart field={key}",
                    ))

            candidates.sort(key=lambda c: c.score, reverse=True)
            return candidates

        except Exception as exc:
            self.debug(f"Fanart.tv error: {exc}")
            return []

    # ---------------------------------------------------------------------
    # Metal Archives
    # ---------------------------------------------------------------------

    def metallum_search(self, artist_name: str, artist_folder: Path | None = None) -> dict[str, str] | None:
        try:
            from bs4 import BeautifulSoup
        except Exception:
            self.debug("Metal Archives skipped: beautifulsoup4 not installed")
            return None

        try:
            folder_albums = self.get_albums_from_folder(artist_folder) if artist_folder else []
            search_url = (
                "https://www.metal-archives.com/search/ajax-band-search/"
                f"?field=name&query={quote(artist_name)}"
            )

            self.debug(f"Metal Archives: searching {artist_name}")
            result = subprocess.run(
                ["curl", "-sL", "-H", "User-Agent: Mozilla/5.0", search_url],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode != 0:
                return None

            data = json.loads(result.stdout)
            rows = data.get("aaData") or []
            candidates: list[dict[str, str]] = []

            for row in rows:
                first_col = row[0] if row else ""
                soup = BeautifulSoup(first_col, "html.parser")
                link = soup.find("a")
                if not link:
                    continue
                candidates.append({
                    "name": link.get_text(strip=True),
                    "url": urljoin("https://www.metal-archives.com", link.get("href", "")),
                })

            if not candidates:
                return None

            if len(candidates) > 1 and folder_albums:
                match = self.metallum_match_discography(candidates[:3], folder_albums)
                if match:
                    return match

            for candidate in candidates:
                if candidate["name"].lower() == artist_name.lower():
                    return candidate

            return candidates[0]

        except Exception as exc:
            self.debug(f"Metal Archives search error: {exc}")
            return None

    def metallum_match_discography(
        self,
        candidates: list[dict[str, str]],
        folder_albums: list[str],
    ) -> dict[str, str] | None:
        try:
            from bs4 import BeautifulSoup
        except Exception:
            return None

        best: dict[str, str] | None = None
        best_score = 0.0

        for candidate in candidates:
            try:
                result = subprocess.run(
                    ["curl", "-sL", "-H", "User-Agent: Mozilla/5.0", candidate["url"]],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                if result.returncode != 0:
                    continue

                soup = BeautifulSoup(result.stdout, "html.parser")
                remote_albums: list[str] = []
                for link in soup.find_all("a", href=lambda x: x and "/albums/" in x):
                    album = link.get_text(strip=True).split(" (", 1)[0].lower()
                    if album:
                        remote_albums.append(album)

                matches = sum(
                    1
                    for local_album in folder_albums
                    if any(local_album in remote_album or remote_album in local_album for remote_album in remote_albums)
                )
                score = matches / max(len(folder_albums), 1)

                if score > best_score:
                    best = candidate
                    best_score = score

                time.sleep(self.sleep)

            except Exception:
                continue

        return best if best_score >= 0.3 else None

    def get_metallum_images(self, artist_name: str, artist_folder: Path | None = None) -> list[ImageCandidate]:
        band = self.metallum_search(artist_name, artist_folder)
        if not band:
            return []

        try:
            result = subprocess.run(
                ["curl", "-sL", "-H", "User-Agent: Mozilla/5.0", band["url"]],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode != 0:
                return []

            html = result.stdout
            candidates: list[ImageCandidate] = []

            patterns = [
                ("logo", "logo", 75, True),
                ("photo", "photo", 80, False),
            ]

            for kind, html_id, score, transparent in patterns:
                regexes = [
                    rf'<a[^>]+id=["\']{html_id}["\'][^>]+href=["\']([^"\']+)["\']',
                    rf'<img[^>]+id=["\']{html_id}["\'][^>]+src=["\']([^"\']+)["\']',
                ]

                for regex in regexes:
                    match = re.search(regex, html, re.IGNORECASE)
                    if not match:
                        continue
                    url = match.group(1).replace("_thumb", "").replace("_small", "")
                    if not url.startswith("http"):
                        url = urljoin(band["url"], url)

                    candidates.append(ImageCandidate(
                        kind="logo" if kind == "logo" else "photo",
                        source="metallum",
                        url=url,
                        score=score,
                        transparent=transparent,
                        notes=f"metallum band={band['name']}",
                    ))
                    break

            candidates.sort(key=lambda c: c.score, reverse=True)
            return candidates

        except Exception as exc:
            self.debug(f"Metal Archives image error: {exc}")
            return []

    # ---------------------------------------------------------------------
    # Collection
    # ---------------------------------------------------------------------

    def collect_candidates(
        self,
        artist_name: str,
        artist_folder: Path | None,
        photo_sources: list[str],
        logo_sources: list[str],
    ) -> tuple[list[ImageCandidate], list[ImageCandidate]]:
        all_candidates: list[ImageCandidate] = []

        # Avoid duplicate API calls where one provider returns both.
        needs_audiodb = "audiodb" in photo_sources or "audiodb" in logo_sources
        needs_metallum = "metallum" in photo_sources or "metallum" in logo_sources

        if "spotify" in photo_sources:
            all_candidates.extend(self.get_spotify_photos(artist_name))
            time.sleep(self.sleep)

        if "discogs" in photo_sources:
            all_candidates.extend(self.get_discogs_photos(artist_name))
            time.sleep(self.sleep)

        if "lastfm" in photo_sources:
            all_candidates.extend(self.get_lastfm_photos(artist_name))
            time.sleep(self.sleep)

        if needs_audiodb:
            all_candidates.extend(self.get_audiodb_images(artist_name))
            time.sleep(self.sleep)

        if "fanart" in logo_sources:
            all_candidates.extend(self.get_fanart_logos(artist_name))
            time.sleep(self.sleep)

        if needs_metallum:
            all_candidates.extend(self.get_metallum_images(artist_name, artist_folder))
            time.sleep(self.sleep)

        photos = [c for c in all_candidates if c.kind == "photo" and c.source in photo_sources]
        logos = [c for c in all_candidates if c.kind == "logo" and c.source in logo_sources]

        photos = self.sort_by_source_order(photos, photo_sources)
        logos = self.sort_by_source_order(logos, logo_sources)

        return photos, logos

    def sort_by_source_order(self, candidates: list[ImageCandidate], source_order: list[str]) -> list[ImageCandidate]:
        order = {source: idx for idx, source in enumerate(source_order)}
        return sorted(
            candidates,
            key=lambda c: (order.get(c.source, 999), -c.score),
        )

    # ---------------------------------------------------------------------
    # Processing
    # ---------------------------------------------------------------------

    def process_artist(
        self,
        artist_name: str,
        out_dir: Path,
        artist_folder: Path | None = None,
        photo_sources: list[str] | None = None,
        logo_sources: list[str] | None = None,
    ) -> bool:
        photo_sources = photo_sources or ["spotify", "discogs", "lastfm", "audiodb", "metallum"]
        logo_sources = logo_sources or ["audiodb", "fanart", "metallum"]

        self.stats["processed"] += 1

        out_dir = Path(out_dir)
        photo_path = out_dir / "artist.jpg"
        logo_path = out_dir / "logo.png"

        need_photo = self.force or not photo_path.exists()
        need_logo = self.force or not logo_path.exists()

        if not need_photo and not need_logo:
            self.log(f"⊘ {artist_name} - already complete")
            self.stats["skipped"] += 1
            return True

        self.log("")
        self.log("=" * 72)
        self.log(f"Artist: {artist_name}")
        self.log(f"Output: {out_dir}")
        self.log(f"Need: {'photo ' if need_photo else ''}{'logo' if need_logo else ''}".strip())
        self.log("=" * 72)

        photos, logos = self.collect_candidates(
            artist_name=artist_name,
            artist_folder=artist_folder,
            photo_sources=photo_sources,
            logo_sources=logo_sources,
        )

        success = True
        selected: dict[str, Any] = {
            "artist": artist_name,
            "output": str(out_dir),
            "photo_sources": photo_sources,
            "logo_sources": logo_sources,
            "selected": {},
            "candidates": {
                "photos": [asdict(c) for c in photos[:10]],
                "logos": [asdict(c) for c in logos[:10]],
            },
        }

        if need_photo:
            if not self.try_candidates(photos, photo_path):
                self.log("✗ No usable artist photo found")
                success = False
            else:
                self.stats["photos_downloaded"] += 1
                selected["selected"]["photo"] = str(photo_path)

        if need_logo:
            if not self.try_candidates(logos, logo_path):
                self.log("✗ No usable logo found")
                success = False
            else:
                self.stats["logos_downloaded"] += 1
                selected["selected"]["logo"] = str(logo_path)

        self.write_metadata(out_dir, selected)

        if not success:
            self.stats["failed"] += 1

        return success

    def clean_logo_background(self, logo_path: Path) -> None:
        rmbg_path = "/Users/rd/Scripts/Riley/rmbg/bin/rmbg"
        rmbg = Path(rmbg_path).expanduser()
        if not rmbg.exists():
            return

        tmp_logo = logo_path.with_name(logo_path.stem + ".cleaned.png")
        cmd = [str(rmbg), "-i", str(logo_path), "-o", str(tmp_logo), "--fuzz", "15"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and tmp_logo.exists():
                tmp_logo.replace(logo_path)
                self.log(f"✨ Logo background cleaned using rmbg")
        except Exception as e:
            self.debug(f"Failed to clean logo with rmbg: {e}")

    def try_candidates(self, candidates: list[ImageCandidate], output_path: Path) -> bool:
        if not candidates:
            return False

        for candidate in candidates:
            if self.download_image(candidate, output_path):
                self.log(f"✓ Saved: {output_path}")
                if candidate.kind == "logo":
                    self.clean_logo_background(output_path)
                return True
            self.debug(f"Candidate failed: {candidate.source} {candidate.url}")

        return False

    def find_artist_folders(self, path: Path) -> list[Path]:
        if not path.exists():
            return []

        folders: list[Path] = []
        for item in path.iterdir():
            if not item.is_dir() or item.name.startswith("."):
                continue

            try:
                has_albums = any(
                    child.is_dir() and re.match(r"^\d{4}\s*-\s*.+", child.name)
                    for child in item.iterdir()
                )
            except PermissionError:
                has_albums = False

            if has_albums:
                folders.append(item)

        return sorted(folders, key=lambda p: p.name.lower())

    def process_letter(
        self,
        letter: str,
        genre: str,
        photo_sources: list[str],
        logo_sources: list[str],
    ) -> None:
        letter_path = self.base_path / genre / letter.upper()
        if not letter_path.exists():
            raise SystemExit(f"Letter folder not found: {letter_path}")

        self.log(f"Processing letter: {letter.upper()} / {genre}")
        self.log(f"Path: {letter_path}")

        folders = self.find_artist_folders(letter_path)
        self.log(f"Found {len(folders)} artist folders")

        for idx, folder in enumerate(folders, 1):
            self.log(f"[{idx}/{len(folders)}] {folder.name}")
            self.process_artist(
                artist_name=folder.name,
                out_dir=folder,
                artist_folder=folder,
                photo_sources=photo_sources,
                logo_sources=logo_sources,
            )
            time.sleep(self.sleep)

        self.print_stats()

    def process_all(
        self,
        genre: str,
        photo_sources: list[str],
        logo_sources: list[str],
    ) -> None:
        genre_path = self.base_path / genre
        if not genre_path.exists():
            raise SystemExit(f"Genre folder not found: {genre_path}")

        letters = [
            p.name
            for p in genre_path.iterdir()
            if p.is_dir()
            and not p.name.startswith(".")
            and not p.name.startswith("-")
            and (len(p.name) <= 2 or p.name == "#")
        ]

        for letter in sorted(letters):
            self.process_letter(letter, genre, photo_sources, logo_sources)

        self.log("")
        self.log("=" * 72)
        self.log("FINAL STATS")
        self.log("=" * 72)
        self.print_stats()

    def print_stats(self) -> None:
        self.log("")
        self.log("Stats:")
        for key, value in self.stats.items():
            self.log(f"  {key}: {value}")


def split_sources(value: str) -> list[str]:
    return [part.strip().lower() for part in value.split(",") if part.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch artist images/logos for Clipped.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("artist_path", nargs="?", help="Existing artist folder to process")
    parser.add_argument("--artist", help="Artist name for direct lookup")
    parser.add_argument("--out", help="Output directory for --artist mode")
    parser.add_argument("--base-path", default="/Volumes/Eksternal/Audio")
    parser.add_argument("--genre", default="Metal")
    parser.add_argument("--letter", help="Process a library letter folder")
    parser.add_argument("--all", action="store_true", help="Process all letter folders in genre")
    parser.add_argument("--force", action="store_true", help="Overwrite existing artist.jpg/logo.png")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.35, help="Delay between provider calls")
    parser.add_argument(
        "--photo-sources",
        default="spotify,discogs,lastfm,audiodb,metallum",
        help="Comma source order for artist.jpg",
    )
    parser.add_argument(
        "--logo-sources",
        default="audiodb,fanart,metallum",
        help="Comma source order for logo.png",
    )

    args = parser.parse_args()

    photo_sources = split_sources(args.photo_sources)
    logo_sources = split_sources(args.logo_sources)

    valid_photo_sources = {"spotify", "discogs", "lastfm", "audiodb", "metallum"}
    valid_logo_sources = {"audiodb", "fanart", "metallum"}

    bad_photo = set(photo_sources) - valid_photo_sources
    bad_logo = set(logo_sources) - valid_logo_sources

    if bad_photo:
        raise SystemExit(f"Invalid photo source(s): {', '.join(sorted(bad_photo))}")
    if bad_logo:
        raise SystemExit(f"Invalid logo source(s): {', '.join(sorted(bad_logo))}")

    fetcher = ArtistImageFetcher(
        base_path=args.base_path,
        force=args.force,
        dry_run=args.dry_run,
        verbose=args.verbose,
        sleep=args.sleep,
    )

    if args.artist_path:
        folder = Path(args.artist_path).expanduser().resolve()
        fetcher.process_artist(
            artist_name=folder.name,
            out_dir=folder,
            artist_folder=folder,
            photo_sources=photo_sources,
            logo_sources=logo_sources,
        )
        fetcher.print_stats()
        return

    if args.artist:
        if not args.out:
            safe = fetcher.safe_name(args.artist)
            out_dir = Path.cwd() / safe
        else:
            out_dir = Path(args.out).expanduser().resolve()

        fetcher.process_artist(
            artist_name=args.artist,
            out_dir=out_dir,
            artist_folder=None,
            photo_sources=photo_sources,
            logo_sources=logo_sources,
        )
        fetcher.print_stats()
        return

    if args.letter:
        fetcher.process_letter(args.letter, args.genre, photo_sources, logo_sources)
        return

    if args.all:
        fetcher.process_all(args.genre, photo_sources, logo_sources)
        return

    parser.print_help()
    raise SystemExit(1)


if __name__ == "__main__":
    main()
