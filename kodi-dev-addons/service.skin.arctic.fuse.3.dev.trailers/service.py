# Arctic Fuse 3 DEV Spotlight trailer driver.
# Native Arctic Fuse 3 Background_Video renders the Kodi player for all widgets.
# This service ONLY creates an opt-in Spotlight preview; it must relinquish the
# player immediately on widget focus, item change, or leaving the Home window.
import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading
import time
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen

import xbmc
import xbmcgui

TAG = "[AF3DEV.Trailer] "
HOME_ID = 10000
HOME_PROPERTY = "AF3DEV.Trailer.Playing"
POLL_SECONDS = 0.20
START_DELAY = 1.1
STOP_LEAD_SECONDS = 2.0
MIN_PLAY_SECONDS = 1.5
START_TIMEOUT = 6.0
TRANSIENT_LIST_GRACE = 2.0
LATE_START_GRACE = 3.0
CACHE_MAX_FILE = 72 * 1024 * 1024
CACHE_MAX_TOTAL = 180 * 1024 * 1024
CACHE_DEADLINE = 6.0


def _log(message, level=xbmc.LOGINFO):
    xbmc.log(TAG + str(message), level)


def _interval():
    values = {"5s": 5, "8s": 8, "10s": 10, "12s": 12, "15s": 15,
              "20s": 20, "30s": 30, "60s": 60, "10m": 600}
    return values.get(xbmc.getInfoLabel("Skin.String(AutoScrollTime)").strip().lower(), 12)


def _normalize_trailer(uri):
    uri = (uri or "").strip()
    if not uri:
        return ""
    if uri.startswith("plugin://"):
        return uri
    parsed = urlparse(uri)
    host = (parsed.hostname or "").lower()
    if host in ("youtube.com", "www.youtube.com", "m.youtube.com",
                "youtu.be", "www.youtu.be"):
        video = (parsed.path.strip("/") if "youtu.be" in host
                 else parse_qs(parsed.query).get("v", [""])[0])
        if len(video) == 11 and all(c.isalnum() or c in "_-" for c in video):
            return "plugin://plugin.video.youtube/play/?video_id=" + video
        return ""
    if parsed.scheme in ("http", "https", "smb", "nfs", "file", "special"):
        return uri
    return ""


def _movie_db_trailer(dbid, dbtype):
    if not dbid.isdecimal() or dbtype not in ("", "movie"):
        return ""
    request = {"jsonrpc": "2.0", "id": 1,
               "method": "VideoLibrary.GetMovieDetails",
               "params": {"movieid": int(dbid), "properties": ["trailer"]}}
    try:
        data = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
        return data.get("result", {}).get("moviedetails", {}).get("trailer", "") or ""
    except Exception as err:
        _log("Kodi movie trailer metadata lookup failed: " + str(err),
             xbmc.LOGWARNING)
        return ""


def _spotlight(home):
    """Return item data only while Spotlight is the active metadata source."""
    if not xbmc.getCondVisibility("Skin.HasSetting(Spotlight.AutoTrailer)"):
        return None, "disabled"
    if not xbmc.getCondVisibility("Window.IsActive(Home)"):
        return None, "not_home"
    if xbmc.getCondVisibility(
            "Window.IsVisible(DialogVideoInfo.xml) | "
            "Window.IsVisible(DialogContextMenu.xml) | "
            "Window.IsVisible(DialogSelect.xml) | System.ScreenSaverActive"):
        return None, "dialog"
    # The original skin tracks exactly which collection was selected.
    # This is also updated by the native widget onfocus callbacks.
    # The hidden 301 wraplist keeps scrolling even while widgets are active.
    # Therefore do not infer focus from 301's item count.
    active = home.getProperty("TMDbHelper.WidgetContainer").strip()
    if active != "301":
        return None, "native_widget" if active else "not_spotlight"
    # Extra protection in the short interval before onfocus changes the property.
    if xbmc.getCondVisibility(
            "ControlGroup(500).HasFocus() | ControlGroup(600).HasFocus()"):
        return None, "widget_focus"
    count = xbmc.getInfoLabel("Container(301).NumItems").strip()
    if not count.isdecimal() or int(count) == 0:
        return None, "no_spotlight_items"
    def label(field):
        return xbmc.getInfoLabel("Container(301).ListItem." + field).strip()
    return {
        "title": label("Title"),
        "path": label("FileNameAndPath"),
        "pos": xbmc.getInfoLabel("Container(301).CurrentItem").strip(),
        "dbid": label("DBID"),
        "dbtype": label("DBType").lower(),
        "list_trailer": label("Trailer") or label("Property(Trailer)"),
    }, "spotlight"


def _resolve_trailer(info, home):
    candidates = [("spotlight", info["list_trailer"]),
                  ("kodi_movie_db", _movie_db_trailer(info["dbid"], info["dbtype"]))]
    candidates.extend([
        ("tmdb_helper", home.getProperty("TMDbHelper.ListItem.Trailer")),
        ("tmdb_base", home.getProperty("TMDbHelper.ListItem.base_trailer")),
    ])
    for source, raw in candidates:
        candidate = _normalize_trailer(raw)
        if candidate:
            return candidate, source
    return "", "unavailable"


def _is_emby_proxy_trailer(uri):
    """Only locally proxied Emby trailers are cached; never arbitrary local URLs."""
    uri = (uri or "").split("|", 1)[0]
    try:
        u = urlparse(uri)
        return (u.scheme == "http" and u.hostname in ("127.0.0.1", "localhost", "::1") and
                u.path.startswith("/dynamic/trailer/"))
    except ValueError:
        return False


class TrailerCache:
    """Finite, background-only Emby download; never blocks Kodi's UI thread.

    Kodi SaveFileState probes HTTP trailer paths when stopping the player; Emby's
    local proxy can time out three times at 5s. Playing a completed local copy
    avoids these repeated failing HTTP HEAD/stat probes.
    """
    def __init__(self):
        self.directory = Path(tempfile.mkdtemp(prefix="af3dev-preview-"))
        self.lock = threading.Lock()
        self.files = {}
        self.inflight = set()
        self.failed = set()
        self.stop_event = threading.Event()
        self.threads = []

    def prepare(self, uri):
        if not _is_emby_proxy_trailer(uri):
            return
        key = hashlib.sha256(uri.encode("utf-8")).hexdigest()
        with self.lock:
            if key in self.files or key in self.inflight or key in self.failed:
                return
            self.inflight.add(key)
        thread = threading.Thread(target=self._download, args=(uri, key),
                                  name="AF3DEV-Prefetch", daemon=True)
        self.threads.append(thread)
        thread.start()

    def ready(self, uri):
        if not _is_emby_proxy_trailer(uri):
            # Other remote HTTP(S) files can trigger similar HTTP stat delays;
            # skip them rather than risking a Kodi-wide freeze. Existing
            # plugin:// and local:// sources use Kodi's native player.
            if uri.startswith(("http://", "https://")):
                return ""
            return uri
        key = hashlib.sha256(uri.encode("utf-8")).hexdigest()
        with self.lock:
            path = self.files.get(key)
        return str(path) if path and path.is_file() else ""

    def _download(self, uri, key):
        # Preserve the genuine extension for local Kodi decoder selection.
        original_path = urlparse(uri.split("|", 1)[0]).path.lower()
        extension = next((x for x in (".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v")
                          if original_path.endswith(x)), ".mp4")
        destination = self.directory / (key + extension)
        partial = self.directory / (key + extension + ".part")
        ok = False
        length = 0
        started = time.monotonic()
        try:
            request = Request(uri.split("|", 1)[0],
                              headers={"User-Agent": "Kodi-AF3DEV-TrailerPreview/0.4"})
            with urlopen(request, timeout=2.0) as response:
                declared = response.headers.get("Content-Length", "")
                if declared.isdecimal() and int(declared) > CACHE_MAX_FILE:
                    raise ValueError("Trailer exceeds local preview cache size limit")
                with open(partial, "wb") as out:
                    while not self.stop_event.is_set():
                        if time.monotonic() - started >= CACHE_DEADLINE:
                            raise TimeoutError("Emby trailer prefetch deadline exceeded")
                        data = response.read(128 * 1024)
                        if not data:
                            break
                        length += len(data)
                        if length > CACHE_MAX_FILE:
                            raise ValueError("Trailer exceeds per-file cache limit")
                        out.write(data)
            if length > 0 and not self.stop_event.is_set():
                with self.lock:
                    total = sum(p.stat().st_size for p in self.files.values()
                                if p.is_file())
                    if total + length <= CACHE_MAX_TOTAL:
                        os.replace(str(partial), str(destination))
                        self.files[key] = destination
                        ok = True
        except Exception as err:
            _log("Emby preview cache unavailable; keep static artwork (" +
                 type(err).__name__ + ")", xbmc.LOGWARNING)
        finally:
            if not ok:
                try:
                    partial.unlink()
                except OSError:
                    pass
            with self.lock:
                self.inflight.discard(key)
                if not ok:
                    self.failed.add(key)
            if ok:
                _log("Emby trailer cached locally; original streaming URL not played")

    def close(self):
        self.stop_event.set()
        # This is a best-effort cleanup; do not block Kodi shutdown for network.
        for path in self.directory.glob("*"):
            try:
                path.unlink()
            except OSError:
                pass
        try:
            self.directory.rmdir()
        except OSError:
            pass


class SpotlightService:
    def __init__(self):
        self.monitor = xbmc.Monitor()
        self.player = xbmc.Player()
        self.home = xbmcgui.Window(HOME_ID)
        self.cache = TrailerCache()
        self.key = None
        self.changed_at = 0.0
        self.trailer = ""
        self.attempted = False
        self.pending = False
        self.pending_since = 0.0
        self.owned = False
        self.owned_file = ""
        self.last_state = None
        self.missing_since = None
        self.late_stop_until = 0.0
        self.late_stop_uri = ""

    def _property(self, active):
        self.home.setProperty(HOME_PROPERTY, "true" if active else "false")

    def _forget_preview(self):
        self.pending = False
        self.owned = False
        self.owned_file = ""
        self._property(False)

    def _stop_preview(self, reason):
        """Stop only a trailer this service launched, including Emby streams.

        Kodi can report 'not playing' between a play() request and AV start.
        Keep a short late-start guard rather than orphaning that video.
        """
        if not (self.pending or self.owned):
            self._property(False)
            return
        was_pending = self.pending
        video_was_running = False
        try:
            video_was_running = self.player.isPlayingVideo()
            if video_was_running:
                if xbmc.getCondVisibility("Window.IsActive(fullscreenvideo)"):
                    _log("Fullscreen user playback: release without stopping")
                else:
                    self.player.stop()
                    _log("Stopped Spotlight trailer: " + reason)
        except RuntimeError as err:
            _log("Player stop failed: " + str(err), xbmc.LOGWARNING)
        if was_pending and not video_was_running:
            # Only match an expected media URI; never kill a widget/user video
            # merely because it started while our late-stop timer was armed.
            self.late_stop_until = time.monotonic() + LATE_START_GRACE
            self.late_stop_uri = self.trailer
            _log("Waiting briefly to cancel a delayed trailer start")
        self._forget_preview()

    def _check_late_start(self, now):
        if not self.late_stop_until:
            return
        if now > self.late_stop_until:
            self.late_stop_until = 0.0
            self.late_stop_uri = ""
            return
        try:
            if self.player.isPlayingVideo():
                current = self.player.getPlayingFile()
                # Emby trailer URLs are direct local HTTP links; Kodi commonly
                # retains the requested URL when playback begins.
                if (current and self.late_stop_uri and
                        current.split("|")[0] == self.late_stop_uri.split("|")[0] and
                        not xbmc.getCondVisibility("Window.IsActive(fullscreenvideo)")):
                    self.player.stop()
                    _log("Stopped late-starting Spotlight trailer")
                self.late_stop_until = 0.0
                self.late_stop_uri = ""
        except RuntimeError:
            pass

    def _tick(self):
        now = time.monotonic()
        self._check_late_start(now)
        # The deadline is independent of container visibility: Kodi may
        # transiently empty/rebuild 301 while opening an Emby video.
        if (self.pending or self.owned) and self.key is not None:
            cutoff = min(max(0.0, _interval() - STOP_LEAD_SECONDS), 15.0)
            if now - self.changed_at >= cutoff:
                self._stop_preview("before_auto_scroll")

        item, state = _spotlight(self.home)
        if state != self.last_state:
            _log("Selection mode: " + state)
            self.last_state = state

        if item is None:
            if state == "no_spotlight_items" and (self.pending or self.owned):
                if self.missing_since is None:
                    self.missing_since = now
                if now - self.missing_since < TRANSIENT_LIST_GRACE:
                    # Keep pending player ownership until Kodi has completed
                    # the launch and restored the Spotlight item list.
                    return
            self.missing_since = None
            if self.pending or self.owned:
                self._stop_preview("left_spotlight")
            self.key = None
            self.attempted = False
            return

        self.missing_since = None
        key = (item["path"], item["title"], item["pos"], item["dbid"])
        if key != self.key:
            self._stop_preview("spotlight_item_changed")
            self.key = key
            self.changed_at = now
            self.attempted = False
            self.trailer, source = _resolve_trailer(item, self.home)
            if self.trailer:
                self.cache.prepare(self.trailer)
            _log("Spotlight item: " + ("trailer " + source if self.trailer else
                                       "no trailer") + "; DBID " +
                 ("present" if item["dbid"] else "absent"))

        if self.owned:
            try:
                if not self.player.isPlayingVideo():
                    self._forget_preview()
                    return
                # A stream resolver may change getPlayingFile() mid-preview.
                # Don't relinquish ownership solely because the URI changed.
            except RuntimeError:
                self._forget_preview()
                return

        if self.pending:
            try:
                if self.player.isPlayingVideo():
                    playing = self.player.getPlayingFile()
                    if playing:
                        self.owned = True
                        self.owned_file = playing
                        self.pending = False
                        self._property(True)
                        _log("Spotlight preview playback confirmed")
            except RuntimeError:
                pass
            if self.pending and now - self.pending_since >= START_TIMEOUT:
                self._stop_preview("start_timeout")
                _log("Trailer did not start within six seconds", xbmc.LOGWARNING)

        elapsed = now - self.changed_at
        cutoff = min(max(0.0, _interval() - STOP_LEAD_SECONDS), 15.0)
        if elapsed >= cutoff:
            if self.pending or self.owned:
                self._stop_preview("before_auto_scroll")
            return

        if (self.attempted or not self.trailer or elapsed < START_DELAY or
                cutoff - elapsed < MIN_PLAY_SECONDS or self.late_stop_until):
            return
        playable = self.cache.ready(self.trailer)
        if not playable:
            # Cache is not ready; the image is kept instead of freezing Kodi.
            # Recheck every poll until the cutoff, never play the Emby URL direct.
            return
        # Kodi's normal widget/media playback must never be preempted.
        if self.player.isPlaying():
            return
        self.attempted = True
        self.pending = True
        self.pending_since = now
        try:
            _log("Opening Spotlight trailer with native background videowindow" +
                 (" (local cached file)" if playable != self.trailer else ""))
            self.player.play(playable, windowed=True)
        except Exception as err:
            self._forget_preview()
            _log("Trailer preview launch failed: " + str(err), xbmc.LOGWARNING)

    def run(self):
        _log("Service 0.4.0: cached Emby trailers avoid Kodi HTTP stat delays")
        self._property(False)
        try:
            while not self.monitor.waitForAbort(POLL_SECONDS):
                try:
                    self._tick()
                except Exception as err:
                    _log("Preview loop failed: " + str(err), xbmc.LOGERROR)
                    self._stop_preview("exception")
        finally:
            self._stop_preview("service_stop")
            self.cache.close()
            _log("Service stopped")


if __name__ == "__main__":
    SpotlightService().run()
