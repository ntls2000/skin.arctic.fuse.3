# Arctic Fuse 3 DEV - opt-in Spotlight trailer preview. No Emby credentials or API calls.
# Only Kodi's currently exposed ListItem.Trailer is used.
import time
from urllib.parse import urlparse

import xbmc
import xbmcgui

TAG = "[AF3DEV.Trailer] "
HOME_ID = 10000
HOME_PROPERTY = "AF3DEV.Trailer.Playing"
POLL_SECONDS = 0.25
START_DELAY = 1.1
STOP_LEAD_SECONDS = 2.0
MIN_PLAY_SECONDS = 1.5


def _interval():
    """Match the skin's Defs_AutoScroll mapping; 12 seconds is the default."""
    raw = xbmc.getInfoLabel("Skin.String(AutoScrollTime)").strip().lower()
    values = {"5s": 5, "8s": 8, "10s": 10, "12s": 12, "15s": 15,
              "20s": 20, "30s": 30, "60s": 60, "10m": 600}
    return values.get(raw, 12)


def _allowed_trailer(uri):
    # Standard Kodi/Emby trailer links: plugin://plugin.video.youtube or HTTP(S).
    # Reject arbitrary built-in commands; Kodi will resolve the media itself.
    return bool(uri and (uri.startswith(("plugin://", "https://", "http://",
                                         "smb://", "nfs://", "file://", "special://"))))


def _spotlight():
    if not xbmc.getCondVisibility("Skin.HasSetting(Spotlight.AutoTrailer)"):
        return None
    if not xbmc.getCondVisibility("Window.IsActive(Home) + Control.IsVisible(301)"):
        return None
    if xbmc.getCondVisibility("Window.IsVisible(DialogVideoInfo.xml) | Window.IsVisible(DialogContextMenu.xml) | Window.IsVisible(DialogSelect.xml) | System.ScreenSaverActive"):
        return None
    trailer = xbmc.getInfoLabel("Container(301).ListItem.Trailer").strip()
    title = xbmc.getInfoLabel("Container(301).ListItem.Title").strip()
    path = xbmc.getInfoLabel("Container(301).ListItem.FileNameAndPath").strip()
    position = xbmc.getInfoLabel("Container(301).CurrentItem").strip()
    if not _allowed_trailer(trailer):
        return ((path, title, position, trailer), None)
    return ((path, title, position, trailer), trailer)


class SpotlightService:
    def __init__(self):
        self.monitor = xbmc.Monitor()
        self.player = xbmc.Player()
        self.home = xbmcgui.Window(HOME_ID)
        self.key = None
        self.changed_at = 0.0
        self.preview_attempted = False
        self.start_pending = False
        self.start_requested_at = 0.0
        self.owned_file = None
        self.owned = False

    def _property(self, on):
        self.home.setProperty(HOME_PROPERTY, "true" if on else "false")

    def _stop_preview(self):
        self._property(False)
        try:
            if self.owned and self.player.isPlayingVideo():
                current = self.player.getPlayingFile()
                # A user-started film must never be stopped if playback has changed.
                if current and current == self.owned_file:
                    self.player.stop()
        except RuntimeError:
            pass
        self.start_pending = False
        self.owned = False
        self.owned_file = None

    def _tick(self):
        now = time.monotonic()
        item = _spotlight()
        if item is None:
            if self.owned or self.start_pending:
                self._stop_preview()
            self.key = None
            return

        key, trailer = item
        if key != self.key:
            if self.owned or self.start_pending:
                self._stop_preview()
            self.key = key
            self.changed_at = now
            self.preview_attempted = False

        if self.owned:
            try:
                if not self.player.isPlayingVideo() or self.player.getPlayingFile() != self.owned_file:
                    # Playback has ended or been replaced by a user action.
                    self._stop_preview()
                    return
            except RuntimeError:
                self._stop_preview()
                return

        if self.start_pending:
            if self.player.isPlayingVideo():
                try:
                    file_now = self.player.getPlayingFile()
                    if file_now:
                        self.owned_file = file_now
                        self.owned = True
                        self.start_pending = False
                        self._property(True)
                        xbmc.log(TAG + "Preview started for spotlight item", xbmc.LOGINFO)
                except RuntimeError:
                    pass
            if self.start_pending and now - self.start_requested_at > 3.0:
                self.start_pending = False
                self._property(False)

        elapsed = now - self.changed_at
        # Always end the preview before the *next* expected autoscroll, never
        # play a trailer longer than 15 seconds in preview mode.
        cutoff = min(max(0.0, _interval() - STOP_LEAD_SECONDS), 15.0)
        if elapsed >= cutoff:
            if self.owned or self.start_pending:
                self._stop_preview()
            return

        if (not trailer or self.preview_attempted or elapsed < START_DELAY or
                cutoff - elapsed < MIN_PLAY_SECONDS):
            return
        # Never interrupt a movie/TV channel already playing in Kodi.
        if self.player.isPlaying():
            return
        self.preview_attempted = True
        self.start_pending = True
        self.start_requested_at = now
        try:
            self.player.play(trailer, windowed=True)
        except Exception as exc:
            self.start_pending = False
            xbmc.log(TAG + "Preview launch failed: " + str(exc), xbmc.LOGWARNING)

    def run(self):
        xbmc.log(TAG + "Started; preview is opt-in and Home-only", xbmc.LOGINFO)
        self._property(False)
        try:
            while not self.monitor.waitForAbort(POLL_SECONDS):
                try:
                    self._tick()
                except Exception as exc:
                    xbmc.log(TAG + "Preview loop: " + str(exc), xbmc.LOGWARNING)
                    if self.owned or self.start_pending:
                        self._stop_preview()
        finally:
            self._stop_preview()
            xbmc.log(TAG + "Stopped", xbmc.LOGINFO)


if __name__ == "__main__":
    SpotlightService().run()
