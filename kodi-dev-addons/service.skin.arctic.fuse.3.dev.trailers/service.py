# Arctic Fuse 3 DEV: optional playback (setting defaults OFF); installed companion service.
# Reads Kodi skin infolabels + local VideoLibrary JSON-RPC, never Emby credentials.
import json
import time
from urllib.parse import urlparse, parse_qs

import xbmc
import xbmcgui

TAG = "[AF3DEV.Trailer] "
HOME_ID = 10000
HOME_PROPERTY = "AF3DEV.Trailer.Playing"
POLL_SECONDS = 0.25
START_DELAY = 1.1
STOP_LEAD_SECONDS = 2.0
MIN_PLAY_SECONDS = 1.5
RECOVER_TIMEOUT = 4.0


def _log(message, level=xbmc.LOGINFO):
    xbmc.log(TAG + str(message), level)


def _interval():
    values = {"5s": 5, "8s": 8, "10s": 10, "12s": 12, "15s": 15,
              "20s": 20, "30s": 30, "60s": 60, "10m": 600}
    return values.get(xbmc.getInfoLabel("Skin.String(AutoScrollTime)").strip().lower(), 12)


def _normalize_trailer(uri):
    """Accept Kodi/media links. Resolve ordinary YouTube links through installed Kodi add-on."""
    uri = (uri or "").strip()
    if not uri:
        return ""
    if uri.startswith("plugin://"):
        return uri
    parsed = urlparse(uri)
    host = (parsed.hostname or "").lower()
    if host in ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be"):
        video = parsed.path.strip("/") if "youtu.be" in host else parse_qs(parsed.query).get("v", [""])[0]
        if len(video) == 11 and all(c.isalnum() or c in "_-" for c in video):
            return "plugin://plugin.video.youtube/play/?video_id=" + video
        return ""
    if parsed.scheme in ("https", "http", "smb", "nfs", "file", "special"):
        return uri
    return ""


def _movie_db_trailer(dbid, dbtype):
    """Kodi VideoLibrary has a trailer even when Spotlight list items omit this infolabel."""
    if not dbid.isdecimal() or dbtype not in ("", "movie"):
        return ""
    request = {
        "jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.GetMovieDetails",
        "params": {"movieid": int(dbid), "properties": ["trailer"]},
    }
    try:
        response = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
        return response.get("result", {}).get("moviedetails", {}).get("trailer", "") or ""
    except Exception as err:
        _log("Kodi video database trailer lookup failed: " + str(err), xbmc.LOGWARNING)
        return ""


def _spotlight():
    """A Spotlight wraplist is offscreen (width=1,left=-1920), so don't gate on Control.IsVisible."""
    if not xbmc.getCondVisibility("Skin.HasSetting(Spotlight.AutoTrailer)"):
        return None, "disabled"
    if not xbmc.getCondVisibility("Window.IsActive(Home)"):
        return None, "not_home"
    if xbmc.getCondVisibility(
            "Window.IsVisible(DialogVideoInfo.xml) | Window.IsVisible(DialogContextMenu.xml) | "
            "Window.IsVisible(DialogSelect.xml) | System.ScreenSaverActive"):
        return None, "dialog"
    num = xbmc.getInfoLabel("Container(301).NumItems").strip()
    if not num.isdecimal() or int(num) < 1:
        return None, "no_spotlight_items"
    label = lambda field: xbmc.getInfoLabel("Container(301).ListItem." + field).strip()
    info = {
        "title": label("Title"),
        "path": label("FileNameAndPath"),
        "pos": xbmc.getInfoLabel("Container(301).CurrentItem").strip(),
        "dbid": label("DBID"),
        "dbtype": label("DBType").lower(),
        "list_trailer": label("Trailer") or label("Property(Trailer)"),
    }
    return info, "ready"


def _resolve_trailer(info, home):
    candidates = [("spotlight", info["list_trailer"])]
    candidates.append(("kodi_movie_db", _movie_db_trailer(info["dbid"], info["dbtype"])))
    if home.getProperty("TMDbHelper.WidgetContainer") == "301":
        candidates.extend([
            ("tmdb_helper", home.getProperty("TMDbHelper.ListItem.Trailer")),
            ("tmdb_base", home.getProperty("TMDbHelper.ListItem.base_trailer")),
        ])
    for source, raw in candidates:
        candidate = _normalize_trailer(raw)
        if candidate:
            return candidate, source
    return "", "unavailable"


class SpotlightService:
    def __init__(self):
        self.monitor = xbmc.Monitor()
        self.player = xbmc.Player()
        self.home = xbmcgui.Window(HOME_ID)
        self.key = None
        self.changed_at = 0.0
        self.attempted = False
        self.preview_uri = ""
        self.start_pending = False
        self.requested_at = 0.0
        self.owned_file = None
        self.owned = False
        self.last_state = None

    def _property(self, playing):
        self.home.setProperty(HOME_PROPERTY, "true" if playing else "false")

    def _stop_preview(self):
        self._property(False)
        if self.owned:
            try:
                if self.player.isPlayingVideo():
                    current = self.player.getPlayingFile()
                    if current and current == self.owned_file:
                        self.player.stop()
            except RuntimeError:
                pass
        self.owned = False
        self.owned_file = None
        self.start_pending = False

    def _tick(self):
        now = time.monotonic()
        item, state = _spotlight()
        if state != self.last_state:
            self.last_state = state
            _log("Spotlight state: " + state)
        if item is None:
            if self.owned or self.start_pending:
                self._stop_preview()
            self.key = None
            self.attempted = False
            return

        key = (item["path"], item["title"], item["pos"], item["dbid"])
        if key != self.key:
            self._stop_preview()
            self.key = key
            self.changed_at = now
            self.attempted = False
            self.preview_uri, source = _resolve_trailer(item, self.home)
            # This is intentionally a URI-free log: no account tokens, paths or URLs.
            _log("New Spotlight item: trailer=" + ("available via " + source if self.preview_uri else
                                                   "missing") + "; dbid=" + ("yes" if item["dbid"] else "no"))

        if self.owned:
            try:
                if not self.player.isPlayingVideo() or self.player.getPlayingFile() != self.owned_file:
                    # User/media player changed; don't stop somebody else's playback.
                    self._stop_preview()
                    return
            except RuntimeError:
                self._stop_preview()
                return

        if self.start_pending:
            if self.player.isPlayingVideo():
                try:
                    current = self.player.getPlayingFile()
                    if current:
                        self.owned_file = current
                        self.owned = True
                        self.start_pending = False
                        self._property(True)
                        _log("Trailer preview started")
                except RuntimeError:
                    pass
            if self.start_pending and now - self.requested_at > RECOVER_TIMEOUT:
                self.start_pending = False
                self._property(False)
                _log("Trailer player did not start in 4s; check URL/player add-on", xbmc.LOGWARNING)

        elapsed = now - self.changed_at
        cutoff = min(max(0, _interval() - STOP_LEAD_SECONDS), 15.0)
        if elapsed >= cutoff:
            if self.owned or self.start_pending:
                _log("Stopping preview before Spotlight advances")
                self._stop_preview()
            return

        if (self.attempted or not self.preview_uri or elapsed < START_DELAY or
                cutoff - elapsed < MIN_PLAY_SECONDS):
            return
        # Do not interrupt films/music/videos started by the user.
        if self.player.isPlaying():
            return
        self.attempted = True
        self.start_pending = True
        self.requested_at = now
        try:
            _log("Requesting windowed trailer preview")
            self.player.play(self.preview_uri, windowed=True)
        except Exception as err:
            self.start_pending = False
            _log("Trailer launch failed: " + str(err), xbmc.LOGWARNING)

    def run(self):
        _log("Service v0.2.0 started; enable Spotlight : bandes-annonces auto in skin settings")
        self._property(False)
        try:
            while not self.monitor.waitForAbort(POLL_SECONDS):
                try:
                    self._tick()
                except Exception as err:
                    _log("Preview loop exception: " + str(err), xbmc.LOGERROR)
                    if self.owned or self.start_pending:
                        self._stop_preview()
        finally:
            self._stop_preview()
            _log("Service stopped")


if __name__ == "__main__":
    SpotlightService().run()
