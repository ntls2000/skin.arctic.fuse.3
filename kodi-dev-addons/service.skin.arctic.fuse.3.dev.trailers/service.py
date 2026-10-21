# Arctic Fuse 3 DEV Spotlight trailer driver.
# Native Arctic Fuse 3 Background_Video renders the Kodi player for all widgets.
# This service ONLY creates an opt-in Spotlight preview; it must relinquish the
# player immediately on widget focus, item change, or leaving the Home window.
import json
import time
from urllib.parse import urlparse, parse_qs

import xbmc
import xbmcgui

TAG = "[AF3DEV.Trailer] "
HOME_ID = 10000
HUB_IDS = (1101, 1102, 1103, 1104)
SUPPORTED_WINDOWS = (HOME_ID,) + HUB_IDS
HOME_PROPERTY = "AF3DEV.Trailer.Playing"
POLL_SECONDS = 0.20
START_DELAY = 1.1
STOP_LEAD_SECONDS = 2.0
MIN_PLAY_SECONDS = 1.5
START_TIMEOUT = 6.0
TRANSIENT_LIST_GRACE = 2.0
LATE_START_GRACE = 3.0
STOP_SETTLE_SECONDS = 0.45


def _log(message, level=xbmc.LOGINFO):
    xbmc.log(TAG + str(message), level)


def _interval():
    values = {"5s": 5, "8s": 8, "10s": 10, "12s": 12, "15s": 15,
              "20s": 20, "30s": 30, "60s": 60, "10m": 600}
    return values.get(xbmc.getInfoLabel("Skin.String(AutoScrollTime)").strip().lower(), 12)


def _preview_cutoff():
    # Exact same AutoScrollTime values as Includes_Defaults.xml / Defs_AutoScroll.
    # No artificial 15-second cap: a 30s slide stops at 28s, 60s at 58s.
    return max(0.0, _interval() - STOP_LEAD_SECONDS)


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


def _active_window_id():
    # Home and the four customizable Arctic Fuse 3 hubs use the same
    # Spotlight wraplist ID 301, but have independent window properties.
    if xbmc.getCondVisibility("Window.IsActive(Home)"):
        return HOME_ID
    for hub_id in HUB_IDS:
        if xbmc.getCondVisibility("Window.IsActive(" + str(hub_id) + ")"):
            return hub_id
    return None


def _spotlight(home):
    """Return item data only while Spotlight is the active metadata source."""
    if not xbmc.getCondVisibility("Skin.HasSetting(Spotlight.AutoTrailer)"):
        return None, "disabled"
    if _active_window_id() is None:
        return None, "not_spotlight_window"
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
        "count": int(count),
        "dbid": label("DBID"),
        "dbtype": label("DBType").lower(),
        "tmdb_id": label("UniqueID(tmdb)") or label("Property(TMDb_ID)") or label("Property(tmdb_id)"),
        "list_trailer": label("Trailer") or label("Property(Trailer)"),
    }, "spotlight"


def _monitor_trailer(info):
    """TMDbHelper classic monitor publishes on Window(Home), even inside hubs.

    Avoid using a stale monitor result from a previously selected TV show.
    The Kodi movie-db lookup is not valid for DBType=tvshow; this monitor is
    therefore the main fallback for series whose list items omit Trailer.
    """
    monitor = xbmcgui.Window(HOME_ID)
    prop = monitor.getProperty
    tmdb_id = prop("TMDbHelper.ListItem.Monitor.TMDb_ID").strip()
    selected_id = info.get("tmdb_id", "").strip()
    if tmdb_id and selected_id and tmdb_id != selected_id:
        return "", "monitor_different_item"
    # If both sides lack comparable IDs, do not use outdated window metadata
    # for the next item. Titles must match before using a fallback trailer.
    if not (tmdb_id and selected_id):
        monitor_title = (prop("TMDbHelper.ListItem.Title") or
                         prop("TMDbHelper.ListItem.base_Title") or
                         prop("TMDbHelper.ListItem.base_label")).strip()
        title = info.get("title", "").strip()
        if not monitor_title or not title or monitor_title.casefold() != title.casefold():
            return "", "monitor_not_ready"
    for property_name in ("TMDbHelper.ListItem.Trailer", "TMDbHelper.ListItem.base_trailer"):
        uri = _normalize_trailer(prop(property_name))
        if uri:
            return uri, "tmdb_monitor_home"
    return "", "monitor_without_trailer"


def _resolve_trailer(info, home):
    for source, raw in (
            ("spotlight", info["list_trailer"]),
            ("kodi_movie_db", _movie_db_trailer(info["dbid"], info["dbtype"]))):
        candidate = _normalize_trailer(raw)
        if candidate:
            return candidate, source
    trailer, source = _monitor_trailer(info)
    return (trailer, source) if trailer else ("", source)


class SpotlightService:
    def __init__(self):
        self.monitor = xbmc.Monitor()
        self.player = xbmc.Player()
        self.home = xbmcgui.Window(HOME_ID)
        self.active_window_id = HOME_ID
        self.key = None
        self.changed_at = 0.0
        self.slide_advance_requested = False
        self.trailer = ""
        self.last_lookup_at = 0.0
        self.attempted = False
        self.pending = False
        self.pending_since = 0.0
        self.owned = False
        self.owned_file = ""
        self.last_state = None
        self.missing_since = None
        self.late_stop_until = 0.0
        self.late_stop_uri = ""
        self.stop_queued = False
        self.stop_queued_at = 0.0

    def _property(self, active):
        self.home.setProperty(HOME_PROPERTY, "true" if active else "false")

    def _forget_preview(self):
        self.pending = False
        self.owned = False
        self.owned_file = ""
        self._property(False)

    def _request_stop(self, reason):
        # Same native Kodi Stop action as a remote/skin button. Unlike the
        # previous xbmc.Player.stop(), executebuiltin defaults to non-blocking
        # execution. Avoid waiting for Kodi's Emby URL state-save operations.
        if self.stop_queued:
            return
        self.stop_queued = True
        self.stop_queued_at = time.monotonic()
        xbmc.executebuiltin("PlayerControl(Stop)", False)
        _log("Queued native Kodi Stop: " + reason)

    def _update_stop_state(self, now):
        if not self.stop_queued:
            return
        try:
            stopped = not self.player.isPlaying()
        except RuntimeError:
            stopped = False
        if stopped and now - self.stop_queued_at >= STOP_SETTLE_SECONDS:
            self.stop_queued = False
            _log("Kodi stop completed; safe to resume Spotlight")

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
                    self._request_stop(reason)
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
                    self._request_stop("late_start")
                self.late_stop_until = 0.0
                self.late_stop_uri = ""
        except RuntimeError:
            pass

    def _tick(self):
        now = time.monotonic()
        active_id = _active_window_id()
        if active_id != self.active_window_id:
            # On hub switch, release the previous hub's trailer and property.
            # Each hub stores TMDbHelper.WidgetContainer on its own window.
            self._stop_preview("spotlight_window_changed")
            self.active_window_id = active_id
            self.home = xbmcgui.Window(active_id if active_id is not None else HOME_ID)
            self._property(False)
            self.key = None
            self.attempted = False
            self.slide_advance_requested = False
            self.missing_since = None
            self.last_state = None
            _log("Spotlight window switched: " + str(active_id))
        self._update_stop_state(now)
        self._check_late_start(now)
        # The deadline is independent of container visibility: Kodi may
        # transiently empty/rebuild 301 while opening an Emby video.
        if (self.pending or self.owned) and self.key is not None:
            cutoff = _preview_cutoff()
            if now - self.changed_at >= cutoff:
                self._stop_preview("before_auto_scroll")

        item, state = _spotlight(self.home)
        if state != self.last_state:
            _log("Selection mode: " + state)
            self.last_state = state

        if item is None:
            if state == "no_spotlight_items" and self.key is not None:
                if self.missing_since is None:
                    self.missing_since = now
                if now - self.missing_since < TRANSIENT_LIST_GRACE:
                    # Preserve slide clock and any pending trailer while Kodi
                    # briefly refreshes the list; do not reset its countdown.
                    return
            self.missing_since = None
            if self.pending or self.owned:
                self._stop_preview("left_spotlight")
            self.key = None
            self.attempted = False
            self.slide_advance_requested = False
            return

        self.missing_since = None
        key = (item["path"], item["title"], item["pos"], item["dbid"])
        if key != self.key:
            self._stop_preview("spotlight_item_changed")
            self.key = key
            self.changed_at = now
            self.slide_advance_requested = False
            self.attempted = False
            self.trailer, source = _resolve_trailer(item, self.home)
            self.last_lookup_at = now
            _log("Spotlight item: " + ("trailer " + source if self.trailer else
                                       "no trailer (" + source + ")") + "; DBID " +
                 ("present" if item["dbid"] else "absent") +
                 "; autoscroll=" + str(_interval()) + "s; stop_at=" +
                 str(_preview_cutoff()) + "s")

        # The TMDbHelper monitor updates asynchronously after a TV item is
        # selected. Retry missing series trailers while this slide is active,
        # instead of permanently recording a negative result on first tick.
        if (not self.trailer and item["dbtype"] in ("tvshow", "season", "episode", "") and
                now - self.last_lookup_at >= 1.5 and
                now - self.changed_at < _preview_cutoff() - MIN_PLAY_SECONDS):
            self.last_lookup_at = now
            self.trailer, source = _resolve_trailer(item, self.home)
            if self.trailer:
                _log("Series Spotlight trailer ready via " + source)

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
        cutoff = _preview_cutoff()
        if elapsed >= cutoff and (self.pending or self.owned):
            self._stop_preview("before_auto_scroll")

        # When previews are enabled on Home, native autoscroll is gated off.
        # A single monotonic clock controls both Stop (interval-2) and the
        # actual next slide (interval). The original Kodi autoscroll is used
        # unchanged when the setting is turned off.
        if elapsed >= _interval():
            if not self.slide_advance_requested and item["count"] > 1:
                self.slide_advance_requested = True
                try:
                    # Official GUI built-in: sends GUI_MSG_MOVE_OFFSET to
                    # the (unfocused, offscreen) Spotlight wraplist 301.
                    xbmc.executebuiltin("Control.Move(301,1)", False)
                    _log("Advancing Spotlight after " + str(_interval()) + "s")
                except Exception as err:
                    _log("Spotlight advance failed: " + type(err).__name__, xbmc.LOGWARNING)
            return

        if elapsed >= cutoff:
            return

        if (self.attempted or not self.trailer or elapsed < START_DELAY or
                cutoff - elapsed < MIN_PLAY_SECONDS or self.late_stop_until or
                self.stop_queued):
            return
        # Kodi's normal widget/media playback must never be preempted.
        if self.player.isPlaying():
            return
        self.attempted = True
        self.pending = True
        self.pending_since = now
        try:
            _log("Opening Spotlight trailer with native background videowindow")
            self.player.play(self.trailer, windowed=True)
        except Exception as err:
            self._forget_preview()
            _log("Trailer preview launch failed: " + str(err), xbmc.LOGWARNING)

    def run(self):
        _log("Service 0.4.4: global TMDb monitor fallback for series and delayed metadata retry")
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
            _log("Service stopped")


if __name__ == "__main__":
    SpotlightService().run()
