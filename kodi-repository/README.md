# NTLS2000 Kodi DEV Repository

Development distribution for **Arctic Fuse 3 DEV (Original)**, based on jurialmunkey's Arctic Fuse 3 **3.4.2**.

## Published builds

| Kodi addon | Addon ID | Version |
|---|---|---|
| NTLS2000 Kodi DEV Repository | `repository.ntls2000.kodi.dev` | `0.1.0` |
| Arctic Fuse 3 DEV (Original) | `skin.arctic.fuse.3.dev` | **`3.4.2.24`** |
| Arctic Fuse 3 Premium LAB (experimental) | `skin.arctic.fuse.3.premium.lab` | **`3.4.2.30`** |

Source baseline: `omega` commit `1f0b8fd67fa73738ea7f6fe1ff6dd8e3859192fb`. The skin has the upstream visuals and interface features, and a separate addon ID to avoid overwriting `skin.arctic.fuse.3`. The Arctic Splash minimum dependency is `1.0.0`. The trailer service is automatically installed with the DEV skin (v0.4.8); preview itself remains disabled by default.

## Premium LAB as a separate repository skin

**Premium LAB 3.4.2.30 is available directly from the NTLS2000 Kodi DEV Repository.** The two Spotlight buttons now use a more compact 360×84px rounded design (was 410×84px), with the Play group width reduced from 435 to 385px to preserve its 25px horizontal gap, with precisely named actions **Lecture** and **Informations**. Both buttons have an anti-aliased rounded white outline and translucent dark interior when not focused; the focused button alone has a rounded opaque white fill, dark label and icon. Two dedicated lightweight 96×84px PNGs (outline and fill) stretch with a 22px fixed-corner texture border; thus the curves are preserved at the new 360px width. This replaces the square four-stroke outline of 3.4.2.28 without altering Kodi's original focus IDs 311 and 312, parent group 316, actions or navigation. Actual Kodi 22 appearance is still awaiting user confirmation. In Kodi use **Add-ons > Install from repository > NTLS2000 - Kodi DEV Repository > Look and feel > Skins > Arctic Fuse 3 Premium LAB**. When Kodi displays cached repository results, use **Check for updates** first.

This is a DIFFERENT skin addon ID (`skin.arctic.fuse.3.premium.lab`), not an upgrade to the tested stable `skin.arctic.fuse.3.dev` version **3.4.2.24**. Both packages are listed in the same Kodi `addons.xml` catalog with different IDs. Both depend on the shared, unchanged `service.skin.arctic.fuse.3.dev.trailers` **0.4.8**. Reinstall or switch back to Arctic Fuse 3 DEV using **Settings > Interface > Skin** if Premium LAB navigation misbehaves.

LAB is an **UNVALIDATED visual experiment**. GitHub Actions checked archive structure, public raw download, separate IDs, manifest, the four-add-on repository catalog, and preserved the stable ZIP unchanged. This does NOT establish that Premium rendering or navigation is correct in actual Kodi 22.

## Installation

1. Install [the NTLS2000 repository](https://raw.githubusercontent.com/ntls2000/skin.arctic.fuse.3/kodi-repo/kodi-repository/repository.ntls2000.kodi.dev/repository.ntls2000.kodi.dev-0.1.0.zip) from **Kodi > Add-ons > Install from ZIP** (once).
2. Go to **Install from repository > NTLS2000 - Kodi DEV Repository > Look and feel > Skins** and choose **Arctic Fuse 3 DEV (Original) 3.4.2.24**.
3. Existing original skin and installed dependencies remain untouched. Switch skins using **Settings > Interface > Skin**.

Alternatively download the same verified Kodi archive from [GitHub Releases](https://github.com/ntls2000/skin.arctic.fuse.3/releases/download/arctic-fuse-3-dev-3.4.2.24/skin.arctic.fuse.3.dev-3.4.2.24.zip) and choose **Install from ZIP**.

**IMPORTANT:** Earlier 3.4.2.1 and 3.4.2.2 packages were corrupted *after generation* when checked into Git because the inherited `.gitattributes` applied `* text eol=lf` to ZIP files. This repository now has `*.zip binary`. The 3.4.2.24 archive has been validated with both Python and GNU unzip, from the Git blob and after HTTP download from the public Raw GitHub URL **and** the GitHub Releases mirror. Do not install any earlier version.

If Kodi previously downloaded the invalid package, exit Kodi and delete only the stale files named `skin.arctic.fuse.3.dev-3.4.2.1.zip` and/or `skin.arctic.fuse.3.dev-3.4.2.2.zip` from `%APPDATA%\Kodi\addons\packages\`, then reopen Kodi. Do not delete the rest of the packages directory or `userdata`.


## Settings cleanup — 3.4.2.24

The obsolete **Style des boutons du Spotlight** Premium/Standard choice has been removed from the skin settings. The user approved keeping the original Standard Arctic Fuse 3 buttons after confirming navigation works in 3.4.2.23.

Only `1080i/Includes_SkinSettings.xml` changed in the source branch. The existing stable Spotlight layout, native focus IDs **311/312**, group **316**, click/navigation actions, three hubs and the companion trailers service **0.4.8** remain exactly as in 3.4.2.23. The previously saved Premium setting may still exist in Kodi userdata but is ignored and can no longer be toggled from Settings. No user data is removed.

The **Activer les trailers dans le Spotlight** setting and all other relevant skin settings are preserved. Automated XML/navigation/Emby regression tests and ZIP verification are required before distribution; actual Kodi interface validation remains with the user.

## Emergency safe navigation rollback — 3.4.2.23 (Kodi 22 validation pending)

The user tested 3.4.2.22 on Kodi 22 and reported that Spotlight Premium STILL split the Information and Resume action labels while **navigation was blocked**. Versions 3.4.2.19–3.4.2.22 must not be treated as valid Premium skins.

**3.4.2.23 is intentionally a recovery build, NOT a new Premium design.** It restores the complete `1080i/Includes_Hubs.xml` and `1080i/Includes_Home.xml` layout from the user's functional 3.4.2.18 source baseline, with only these safety changes:

- The original Spotlight button artwork, underline, focusable IDs `311`/`312`, play parent `316`, focus routes, click actions, and widget flow are restored.
- `Skin.HasSetting(Spotlight.PremiumButtons)` no longer controls ANY part of `Includes_Hubs.xml`, so even existing installations with Premium saved as enabled render the original Standard controls.
- The settings label reads **Standard (Premium suspendu)** to make this deliberate fallback clear; the saved choice is not deleted.
- No Emby / service / video / ThemeVideo / Stop / widget / custom Hub source logic is changed. Companion service stays **0.4.8**.

To recover a frozen Kodi interface, **exit Kodi completely**, back up the installed `skin.arctic.fuse.3.dev` folder, and extract `skin.arctic.fuse.3.dev-3.4.2.23.zip` so the archive's own top-level `skin.arctic.fuse.3.dev` folder replaces the installed skin folder in the Kodi `addons` directory. On Windows the default is `%APPDATA%\\Kodi\\addons\\`; on Linux it is `~/.kodi/addons/`. Never extract the ZIP inside the skin folder, and never delete `userdata`.

CI validates the recovered XML and the Emby 0.4.8 regression suite. **Actual navigation recovery needs user testing in Kodi 22. Premium design work must stay suspended until normal focus behavior is confirmed.**

## Corrective layout — 3.4.2.22 (Kodi 22 user test pending)

The user confirmed on Kodi 22 that version 3.4.2.21 STILL drew Information in a gray rectangle at the upper position, while "Reprendre la lecture" appeared below, disconnected from the intended Premium primary button. This release replaces the underlying layout mistake rather than tweaking widths again.

Root cause: the original reusable `Hub_Spotlight_Button_Circle` include expanded into two sibling controls: one graphic group plus its real button. In Kodi's horizontal `grouplist` 310, that causes them to be treated as separate layout items. The 3.4.2.21 geometry and negative compensating offsets did not solve the mismatched layout.

Correction: each existing include now expands into EXACTLY ONE permanent `group` (IDs 321 and 322), which contains its existing native focusable button (311 or 312) and decoration. The original Play group 316 remains intact, and both grouplist children have 160px layout height. In Premium each decoration is 420x72 with a 32x32 icon, labels inset 78px, a 20px spacer provided by the Play group; Standard remains selectable with its own icon and text layout. Navigation explicitly links 311 <-> 312 and keeps the original click/back/up/down/widget actions. Neither the native button controls nor their parent groups are conditionally hidden or replaced.

**Only `1080i/Includes_Hubs.xml` and `1080i/Includes_Home.xml` changed for this build.** Frozen Emby Spotlight service **0.4.8**, movie and series ThemeVideo playback and auto-scroll behavior are unchanged. CI verifies the XML nesting and no focus duplication as well as the unchanged Emby regression suite and ZIP. **Visual and navigation behavior require user approval in Kodi 22; release is UNVALIDATED until the user's test.**

## Visual alignment fix — 3.4.2.21: Premium Spotlight buttons (awaiting Kodi feedback)

The user's actual Kodi 22 screenshot of 3.4.2.20 **did not validate the Premium design**: Play/Resume was rendered below the button row while the Info caption and rectangle overlapped. This is a visual regression, not a request to modify playback.

Only `1080i/Includes_Hubs.xml` and `1080i/Includes_Home.xml` were edited. The original permanently focusable buttons **311/312**, their actions, the parent Play group **316**, the Standard option, and the original three Spotlight/hub/video flows are preserved. No code or dependencies were added to the frozen Emby service **0.4.8**.

Premium now assigns each rectangular action a **420x72** painting surface with a **32x32 icon at x=26**, text inset **78**, and **20px horizontal space** between actions. Both captions are vertically centered. The button defaults are applied before each call site's `<nested />` so the native Standard Play offset of **140px** takes precedence, while the Premium Play offset is **0px**. The 316 group is explicitly 160px high and the Info caption compensates for its existing 60px decorative group. No new focusable controls or conditional button substitutions are introduced.

The GitHub build checks XML validity, permanent focus IDs, geometry assertions, Emby 0.4.8 regression and ZIP integrity. **Automated tests are not proof of correct Premium rendering in Kodi 22; the user must test and validate 3.4.2.21.**

## Recovery patch — 3.4.2.20: Premium navigation lock

The user reports that **as soon as Spotlight Premium buttons are enabled in 3.4.2.19, Kodi focus/navigation becomes unusable**. The cause is the conditional replacement of Kodi's original focusable controls 311 (Play) and 312 (Info) by separate Premium-only includes, coupled with hiding the existing parent group. This can remove the intended navigation targets.

**This patch restores a SINGLE PERMANENT pair of focusable controls** in both Standard and Premium:
- Keeps the original Arctic Fuse include `Hub_Spotlight_Button_Circle`, clickable controls `311` and `312`, and their original `onclick`, `onback`, `onright`, `onup` and `ondown` actions.
- Removes the newly introduced `Hub_Spotlight_Button_Premium` focusable-button include and all conditional replacement call sites.
- Uses conditional *decorative* groups only. Premium adds a single rectangular 72px background with 32px icon and adapted text placement; Standard retains its native circular design and underline.
- The original Play group `316` always remains present; cosmetic values use skin variables for spacing and button widths. No focusable control is ever disabled or removed on a style switch.
- `Style des boutons du Spotlight` still toggles the option and reloads the skin for conditional texture refresh.
- **The validated service `0.4.8` and all Accueil/Films/Séries playback, Emby ThemeVideo, native Stop and widget logic are unchanged.**

CI adds an explicit structural regression test requiring two unconditional uses of the original button include, one focusable button per include, permanent group 316, retained navigation actions, and unchanged Emby trailer regression tests.

**Emergency recovery when Kodi cannot be navigated:** Close Kodi, back up `%APPDATA%\Kodi\addons\skin.arctic.fuse.3.dev` to a safe location, and extract the 3.4.2.20 release ZIP into `%APPDATA%\Kodi\addons\` with the included folder structure, allowing replacement. Do not extract into the skin folder itself (which would create a nested directory). Restart Kodi and verify navigation first. Users who can still reach Kodi's Add-ons installer should use the normal repository update. If installation or focus is still broken, return to stable skin 3.4.2.18, where all three Spotlights were confirmed operational.

**Status:** ZIP and XML tests are necessary but cannot replace actual focus/navigation testing in Kodi 22. User confirmation is still required before labelling Premium behavior validated.

## Spotlight Premium Buttons v2 — 3.4.2.19 (skin-only)

With the user confirming the three Spotlight previews working in **3.4.2.18**, this update intentionally changes **only the look of the Spotlight action buttons**. Companion service **0.4.8 is frozen**: no trailer, hub, Emby, TMDb, video, timer, player or Stop logic was changed.

### Premium design

- Replaces the older detached icon circle and underlined text combination with **two complete 72px-high rectangular buttons**, aligned vertically in a single Spotlight row.
- **Primary Play/Resume**: 272px wide, light opaque background, dark icon/label with 78px text inset.
- **Secondary Information**: 306px wide, subtler transparent dark background, white icon/label.
- An evenly spaced 20px gap separates actions; icon is 32×32 and sits at x=26, centered vertically, **inside the same rectangle** as the text.
- Focus uses Arctic Fuse's existing theme highlight color with readable selected foreground. The original click actions are preserved for button **311** (Play) and **312** (Info), including widget navigation and refocus actions.
- **Standard remains the original circular icon plus underline style**, with zero structural edits to that include.
- XML conditionally expands one style at a time so Kodi has **no duplicate focusable IDs**; switching `Style des boutons du Spotlight` from the skin settings invokes `ReloadSkin()` to make the layout change take effect immediately.

### Regression scope

CI confirms XML well-formedness, both exclusive Standard/Premium expansions and button sizing/focus wiring, as well as every previously passing movie/TV-series ThemeVideo/Emby DialogBusy regression. Service source and version remain **0.4.8**.

**Test:** Install **3.4.2.19** (service remains **0.4.8**). Choose *Premium* in the Spotlight button style setting, inspect **Accueil**, **Films**, and **Séries**; verify both controls are cleanly aligned and Play/Info still work. Toggle back to *Standard* to verify the original appearance. Actual screen presentation still requires testing in Kodi; mock XML checks cannot guarantee visual quality.

## Series Spotlight Emby ThemeVideo support — 3.4.2.18

The user's Kodi widget successfully plays the Emby Next Gen 12.4.23 `ThemeVideo` of TV series. These are independent of the video's normal `tvshow.c16` trailer value, which can contain a YouTube plugin URI even when the user stores a real `backdrops/theme.mp4` on the Emby server.

**Companion service 0.4.8** reads the exact, already-indexed Emby Next Gen theme metadata:

1. Only for Spotlight entries with `ListItem.DBType=tvshow` or `series`, obtain the selected Kodi `ListItem.DBID`.
2. Open the user's `special://profile/Database/emby_*.db` databases strictly read-only. Emby Next Gen uses `SELECT EmbyId, EmbyMetaData FROM Video WHERE EmbyParentType='Series' AND KodiParentId=?`; this service also checks `EmbyExtraType='ThemeVideo'` for safety.
3. Parse `EmbyMetaData` to retrieve `Id`, `Container`, and the first `MediaSources[].Id`. If the matching `special://profile/addon_data/plugin.service.emby-next-gen/EMBY-themes/{ServerId}_{Id}.{Container}` file exists, play that original downloaded file.
4. Otherwise use the existing `servers_{ServerId}.json` connector settings to form the same authenticated `/emby/videos/{Id}/stream.{Container}` playback URI used by `hooks/themes.py`. No server discovery, no extra network request, no secret printed in the service's logs.
5. Fall back to the existing direct Spotlight/Kodi video trailer source when there is no matching Emby ThemeVideo. YouTube-only links are still deliberately excluded.

**Preserved Films:** The movie-resolution branch is unchanged from user-validated skin **3.4.2.17** / companion **0.4.7**. The background-video player, GUI window properties, Stop two seconds before slide change, widget handoff, and startup grace also remain unchanged.

**Tests:** CI tests validate both the downloaded local theme and authenticated remote URI using fixtures matching Emby Next Gen's real `Video` SQLite schema, Kodi ID matching and type guards, and unchanged movie/background-video behavior, as well as Git ZIP integrity. These are mock tests; runtime testing in Kodi is still necessary.

**Install:** Skin **3.4.2.18**, service **0.4.8**. Restart Kodi, let the **Séries** Spotlight show several known series with an Emby `ThemeVideo`, and check that they play one at a time and stop before the 30-second slide change. Then check a film to confirm non-regression. If needed, collect `kodi.log` lines with `[AF3DEV.Trailer]`: a successful series uses source `emby_series_theme`. If no source is found, the item continues to advance without playing anything.

## Playback recovery 3.4.2.17 — Emby loading dialog focus regression

The user's `kodi(2).logg` showed that the 3.4.2.16 service repeatedly launched an Emby movie trailer, immediately got `Selection mode: not_spotlight` while Kodi showed `DialogBusy.xml`, queued a delayed native Stop and reopened the **same** trailer roughly every 3 seconds. This was a regression caused by reading `Window.Property(TMDbHelper.WidgetContainer)` on the **frontmost window**, which can be the busy dialog rather than the Home/Hub window.

**Service 0.4.7** now reads `Window(Home).Property(TMDbHelper.WidgetContainer)` on Home or `Window(11101..11104).Property(TMDbHelper.WidgetContainer)` for custom hubs. These are Kodi's actual window IDs; it never instantiates `xbmcgui.Window(1102)`. It falls back to foreground `Window.Property` only if the window-specific value is empty. A short grace also preserves the preview and its slide timer if both labels are briefly absent. **Stop remains asynchronous and occurs at interval minus 2 seconds**, or on real widget focus/Hub change.

The CI test reproduces the regression by forcing foreground `Window.Property` to be empty during active Emby playback, then verifying playback ownership stays active, no Stop command is queued and the same movie is not opened again. It additionally tests both labels missing momentarily, TV Hub window 11102, DB `tvshow.c16` lookup, unavailable Python window 1102, widget handoff and YouTube exclusion.

**Series note:** The user log also shows `no trailer (emby_youtube_trailer_ignored)` for three selected TV shows. Emby/Kodi metadata for these items contains a YouTube-dependent trailer but no independent playable local Emby URL. This release does **not** re-enable YouTube or try to circumvent that limitation.

**Test:** update to skin **3.4.2.17**, companion **0.4.7**; restart Kodi, let a movie with a local Emby trailer play and check that it runs continuously, stops 2s before the next slide and does not loop. Then test Series. If playback still stops abruptly, attach the new `kodi.log` rather than repeatedly adjusting options.

## Custom Emby Series Spotlight fix — 3.4.2.16

The user's `kodi(1).logg` confirmed Kodi successfully opened `Custom_1102_Hub.xml` and its Emby synchronized series list (`library://video/emby_tvshows_Serie/recentlyadded.xml/`), but companion **0.4.5** raised `EXCEPTION: Window id does not exist` during window transitions. The script tried to construct `xbmcgui.Window(1102)` although Kodi actually activates the custom Series hub with GUI window ID `11102`.

**Service 0.4.6** fixes this mismatch without modifying Emby, Kodi libraries, or previously working movies:
- Reads the active hub's selected container via `xbmc.getInfoLabel("Window.Property(TMDbHelper.WidgetContainer)")`, the same mechanism used by `1080i/Includes_Hubs.xml`.
- No longer constructs Python `xbmcgui.Window(1101...1104)` objects. A regression test explicitly makes those constructors raise `Window id does not exist` while the hubs remain active.
- Retains read-only access to Emby-synchronized `tvshow.c16`, native Stop, unified Spotlight timing, widget focus and YouTube exclusion.
- Distinguishes log reasons: `no_emby_trailer_in_kodi_library`, `emby_youtube_trailer_ignored`, and `emby_trailer_format_unsupported`. Includes a non-sensitive `DBType` classification so missing-series metadata can be diagnosed from the next log.

The recorded log also showed `no_playable_emby_trailer` for several Series slides, but that alone cannot prove those series have playable Emby trailers. Once the window-transition exception is fixed, the updated diagnostics can distinguish absent TV-series metadata from an unavailable YouTube-only link.

**Test:** update skin **3.4.2.16** and companion service **0.4.6**, restart Kodi, leave the Emby Series hub Spotlight active for at least three titles (30 seconds each) and confirm whether videos start. When a show has no playable trailer, the artwork should continue to display and the slide should advance normally. If missing, send the new `kodi.log` with `[AF3DEV.Trailer]` entries.

## Safety update 3.4.2.15: Emby-only trailers (YouTube not required)

User reported Kodi 22 RC1 terminating at startup shortly after Spotlight launched a `plugin://plugin.video.youtube` trailer, even though they do not use the YouTube add-on. The prior `kodi.old.log` shows service 0.4.4 launching a trailer at 16:08:40, Kodi reporting `Unable to find plugin plugin.video.youtube`, and subsequent audio sink errors before the log ends. These observations identify an invalid automatic playback request but do **not** prove it is the only cause of the crash.

**Root source:** The supplied Emby Next Gen 12.4.23 ZIP itself turns remote YouTube trailer URLs into `plugin://plugin.video.youtube/play/?video_id=...` in `core/common.py` `set_RemoteTrailerURL`. The user need not install YouTube for the DEV skin to function. To avoid this request, service **0.4.5**:

- Refuses YouTube URLs and `plugin://plugin.video.youtube` trailers; no install prompt is triggered by our service. Items with no independently playable Emby trailer show static artwork.
- Never fetches trailers from TMDb Helper or IMDb; uses the active Emby-synced list-item trailer and the Kodi movie video library.
- For non-dynamic **Emby Séries**, reads the Kodi `tvshow.c16` field that Emby Next Gen populates with a trailer URL. It discovers the newest `MyVideosNNN.db` file and queries it **read-only** with a short SQLite timeout. It performs no writes to Kodi/Emby databases or direct calls to the Emby server.
- Waits 12 seconds after the trailer companion service starts before launching any preview, allowing Emby and other Kodi services to initialize.
- Keeps all previously tested 2-second early Stop, native asynchronous Stop without UI delays, full-duration unified carousel timer, and independent Film/TV hubs.
- Requires **no YouTube add-on, no new plugin, no server credentials**.

**Recovery:** If Kodi crashes before the update can be installed, exit Kodi and temporarily move the folder `%APPDATA%\Kodi\addons\service.skin.arctic.fuse.3.dev.trailers` outside the `addons` directory. Relaunch Kodi, install updated skin/service, restore the add-on by reinstallation, and restart. Keep Emby and Kodi userdata untouched. If this does not help, save `guisettings.xml` and change active skin to `skin.estuary` to isolate the problem.

**Test:** After updating to skin 3.4.2.15 and service 0.4.5, restart Kodi, verify normal startup, watch 3 or 4 Spotlight slides and the custom Series hub, then check `kodi.log` if any error persists. Kodi is not proven stable merely because its add-on ZIP builds successfully.

## Fixed in 3.4.2.14 — TV-show Spotlight trailers and Premium button grouping

**Observed:** The user confirmed trailer previews play in Home and the Films hub, but not their TV Series hub. The earlier implementation used `VideoLibrary.GetMovieDetails` to find movie trailers, then tried `TMDbHelper.ListItem.Trailer` on the **currently active hub window**. TMDbHelper's classic service monitor actually publishes the detailed item under **Window(Home)** even for customized hubs. In addition, TV shows do not have an equivalent supported `VideoLibrary.GetTVShowDetails(...properties=["trailer"])` lookup to rely on.

**Companion service 0.4.4:**
- Always prefers the trailer provided directly by the selected Spotlight list item, including for TV.
- For movies, keeps the existing Kodi movie database lookup.
- For TV shows, consults the TMDbHelper global **Window(Home)** monitor's `TMDbHelper.ListItem.Trailer` and `TMDbHelper.ListItem.base_trailer`.
- Verifies the monitor's TMDb identifier (when available on both sides) or matching title to avoid playing a stale trailer from a previously selected series.
- Retries unavailable TV metadata after 1.5 seconds while that slide is active, because TMDbHelper updates asynchronously.
- Retains the original nonblocking native Stop, 2-second early cutoff, unified autoscroll timing, custom hubs and native widget playback.
- Does **not** invent or search for videos for shows that have no trailer in the available metadata.

**Premium UI:** The previous build had a separate grey rectangle behind the Play/Info icon and another behind the text, causing broken alignment. The new Premium mode hides the original icon panel and keeps one unified rectangular action button. **Standard** is still available as the original design.

**Kodi test:** Update skin **3.4.2.14** with companion **0.4.4**; restart Kodi, select the Series hub and let a TV show with a known trailer appear. If no video plays, check `kodi.log` for `[AF3DEV.Trailer]` and specifically `no trailer (monitor_not_ready)`, `no trailer (monitor_without_trailer)`, or `Series Spotlight trailer ready via tmdb_monitor_home`. These log messages expose no trailer URL. A title without a trailer must continue to show its artwork and advance on schedule.

The CI tests cover global monitor fallback, an asynchronously arriving trailer, stale-title and TMDb-ID protection, the prior movie and hub transitions, UI XML integrity and published ZIP checks. Interactive Kodi testing is still needed.

## New in 3.4.2.13 — custom Hub trailers and Spotlight button styles

Arctic Fuse 3 defines Home and four independent customizable hubs (`1101`, `1102`, `1103`, `1104`), each with its own Spotlight wraplist (ID `301`) and window-local `TMDbHelper.WidgetContainer` property. Previously service 0.4.2 explicitly rejected any window except Home, so assigning separate Spotlights to Film and TV Series hubs did not start previews.

**Service 0.4.3** now detects the active Home/Hub window, gets the correct window-local selection property, and plays available trailers in each hub. It retains the validated native asynchronous Stop, configured autoscroll/early stop synchronized timer, and restores original widget playback upon leaving Spotlight. A hub switch cancels the prior hub's preview; each hub's selection clock starts independently. The skin's own native Spotlight autoscroll is disabled while auto-trailers are active for those windows, preventing competing slide timers.

**Design setting:** Go to **Skin Settings > Menus > Style des boutons du Spotlight**. Select:
- **Standard** (default): original circular Play/Info icons and underline focus.
- **Premium**: more rectangular, understated icon backgrounds and rectangular focus, with exactly the same clickable Play and Information actions. Toggle freely; previous button choices do not affect trailer functionality.

The existing **« Activer les trailers dans le Spotlight »** option remains global. A trailer only starts when the current Spotlight item or its available Kodi/TMDb metadata contains a playable trailer URL. TV-series items lacking trailer metadata remain static, even if their custom hub Spotlight is configured.

GitHub Actions verifies each custom Hub 1101–1104, playback/Stop on each, switching to Home, the two design options, source XML validity, all configured timer values and archive integrity. **Visual rendering and video playback on Kodi 22 still require real-device confirmation.**

**Installation:** Update Arctic Fuse 3 DEV to **3.4.2.13** and verify that **AF3 DEV - Spotlight Trailers** is **0.4.3**. Restart Kodi once. Try an item with a known trailer on your custom Film and Series hubs, then switch to widgets and back. Compare Standard and Premium buttons in the same Spotlight settings.

## Spotlight setting label update — 3.4.2.12

This release changes only the visible skin-settings label to **« Activer les trailers dans le Spotlight »** (previously « Spotlight : bandes-annonces auto »). The control remains in Skin Settings > Menus, close to the existing Spotlight options, and continues using the unchanged `Skin.HasSetting(Spotlight.AutoTrailer)` / `Skin.ToggleSetting(Spotlight.AutoTrailer)` key. Existing user settings, native nonblocking stop, 30-second shared scroll timing, original widgets and companion service version **0.4.2** are unchanged.

The CI build checks the exact new French label and confirms the underlying setting key has not changed. No settings reset or manual reconfiguration is needed.

**Next design work:** Premium focus buttons, spacing and styling in the Spotlight, then home navigation and widget cards. Treat visuals as a separate revision from the proven trailer subsystem.

## Unified Spotlight timer fix — 3.4.2.11

**User report:** With the original skin AutoScrollTime set to **30 seconds**, the trailer ended around **27–28 seconds**, but Kodi advanced to the next film at **60 seconds**. Kodi's native GUI container timer is reset whenever its condition becomes false or its list is reset (see `CGUIBaseContainer::UpdateAutoScrolling` / `ResetAutoScrolling`). A separately timed Python trailer cutoff does not reflect the actual native GUI delay.

**Fix:** When and only when `Spotlight.AutoTrailer` is active **on Home**, the skin disables Kodi's native autoscroll for the Spotlight wraplist (ID 301). Companion service **0.4.2** owns the full Spotlight timing:
- It reads the actual `Skin.String(AutoScrollTime)` and starts a single monotonic clock when the current film changes.
- It queues native `PlayerControl(Stop)` at **interval minus 2 seconds**, retaining the smooth stop behavior from 0.4.0.
- It moves wraplist 301 using Kodi's official `Control.Move(301,1)` action at the **full configured interval** (30 seconds -> stop ~28 seconds -> next title ~30 seconds).
- It sends only one move per title, and only if there are at least two Spotlight items. It retains that clock across brief Emby container refreshes.
- On moving to a different widget, Home losing focus, or preview being turned off, its Spotlight timers stop; the original widget video handling stays unchanged.
- When preview is disabled, or in another window, the original skin's autoscroll is unchanged.

**Verification:** CI simulates native and delayed Stop, widget handoff, all nine skin autoscroll interval values, and asserts 30-second preview stops at 28 seconds and moves exactly once at 30 seconds.

**Live test:** Install skin **3.4.2.11** with service **0.4.2**, reboot Kodi, set 30s interval and verify that the 1st, 2nd and 3rd titles each advance about every 30 seconds (not 60). If a film lacks a trailer, its image must still advance on the same timer. If Kodi blocks its GUI thread or Emby fails to start a stream, transitions may be later than the configured timer; this feature remains experimental.

## Spotlight duration fix in 3.4.2.10

**Problem:** The Spotlight trailer service capped the early-stop threshold at **15 seconds**, regardless of the selected slide interval. Thus a 20-second setting stopped after 15 seconds, a 30-second setting after 15 seconds instead of 28, a 60-second setting after 15 instead of 58, and a ten-minute setting after 15 seconds.

**Fix:** Service **0.4.1** reads Kodi's actual `Skin.String(AutoScrollTime)` on each poll and uses the exact same values as `1080i/Includes_Defaults.xml` `Defs_AutoScroll`. The stop deadline is **configured interval minus 2 seconds**, measured from the current Spotlight item change:

| AutoScrollTime | Stop at |
|---|---|
| 5s | 3s |
| 8s | 6s |
| 10s | 8s |
| 12s (or unset, Kodi skin default) | 10s |
| 15s | 13s |
| 20s | 18s |
| 30s | 28s |
| 60s | 58s |
| 10m | 9m 58s |

- The configured setting is reread, so changing the skin interval does not require restarting the service.
- Logs on each new Spotlight item show `autoscroll=<N>s; stop_at=<N-2>s` for easy verification, without exposing trailer URLs.
- Existing native nonblocking `PlayerControl(Stop)`, trailer startup handling, and original widget video system are retained. No local trailer cache.
- CI tests all nine intervals and specifically asserts that a 30-second setting does **not** stop at 16 seconds but **does** stop at 28 seconds.

**Note:** Kodi may pause or defer autoscroll because of focus or dialogs; the service currently uses the chosen time from the item's selection, not a private Kodi GUI timer. On those unusual paused cases, the calculated stop can precede the actual slide. The next iteration can synchronize with the UI's pause state if reported.

**Test:** Update **Arctic Fuse 3 DEV 3.4.2.10** and its companion **0.4.1**, restart Kodi, set Autoscroll to **30s**, and confirm the trailer stops around **28 seconds after that Spotlight title appears**. Then try a different interval and inspect `[AF3DEV.Trailer]` lines if necessary.

## Kodi 22 native Stop experiment — 3.4.2.9

Following Kodi (6).log, user reported a six-second UI freeze between Spotlight previews. Kodi's `CSaveFileState::DoWork` issued HTTP stat requests against Emby Next Gen's `http://127.0.0.1:57342/dynamic/trailer/...` local proxy, producing repeated 5-second curl timeouts on stopping video.

**User's suggested simpler path:** mimic a standard Stop button and preserve the pre-existing Arctic Fuse 3 widget renderer.

- Service **0.4.0** now uses **`xbmc.executebuiltin("PlayerControl(Stop)", False)`**, the native Kodi Stop action, rather than the synchronous `xbmc.Player().stop()` call.
- The service does not block waiting for Kodi to stop; it prevents a new trailer until Kodi reports playback has ended (with a short settle period).
- No HTTP downloads, local cache, background prefetch or second `videowindow`. The original widget video renderer remains unchanged.
- As before, trailers are stopped when Spotlight changes, when widgets gain focus, or two seconds before the expected autoscroll transition.
- Tests cover native Stop queueing, stopping once per preview, non-blocking transitions in the service simulation, and original widget handoff.

**Limit:** Both Stop mechanisms ultimately invoke Kodi's player shutdown. Kodi's own HTTP state-save work may still stall the application even if the Python service no longer blocks. This build is an **experiment** to check whether the manually tested Stop-button behaviour avoids visible freezes. If the freeze persists, collect a fresh Kodi log and revert to disabling the Spotlight auto-trailer option; do not repeatedly force the UI through long stalls. This version does not claim that a player can be "virtually" stopped while also making it available for a different video.

**Test** after installing skin **3.4.2.9** and service **0.4.0**: restart Kodi, leave the Spotlight autoscroll at 10 seconds, verify that item 1 can have no trailer, item 2 plays then stops, and item 3 starts only once Kodi finishes stopping the prior trailer. Also confirm that the original widgets play their usual previews.

## Kodi log fix: delayed Emby trailer playback in 3.4.2.8

**Issue reproduced from `kodi(4).log` (2026-10-21):** at 13:14:40.651 the Spotlight preview service requested an Emby trailer; at 13:14:40.873 Kodi briefly reported an empty Spotlight list; only afterward, at approximately 13:14:41, did Kodi start actual AV playback. The previous service relinquished the pending launch during the temporary empty-list state. The trailer consequently kept playing through later Spotlight title changes.

The revised **0.3.2** companion service now:
- Retains trailer ownership across a transient **two-second** Spotlight item-list refresh during Emby video startup.
- Checks the next-stop deadline independently of whether the current item list is temporarily empty.
- Stops active trailers **two seconds before the expected slide**; a change to the next title also stops the preceding trailer.
- After a confirmed stop, resolves and previews the following title only if it has a playable trailer.
- Watches briefly for a late-starting exact Emby trailer URL if Kodi had not yet reported playback when the stop was requested.
- Immediately relinquishes playback when actual widgets receive focus; the original Arctic Fuse 3 native background video remains unchanged.
- Never starts a preview while another player is already active; fullscreen playback is not forcibly stopped.

**Expected 10-second slide test:** film 1 has no trailer (no video). Film 2 has a trailer (start approximately after 1 second, stop by around 8 seconds after its selection). Film 3 should then launch its own trailer if available. Navigate down to the widgets at any point to verify the Spotlight trailer stops.

The Kodi GitHub workflow includes automated mocked tests for delayed Emby startup, a temporarily empty Spotlight container, the two-second cutoff and the third film preview. These are **not substitutes** for testing on Windows Kodi 22.

## Video playback handoff fix in 3.4.2.7

**Important design decision:** Arctic Fuse 3 already renders the Kodi player in its original \`Includes_Background.xml\` / \`Background_Video\` / \`videowindow\`. We now use this **unchanged native renderer**. The extra \`videowindow\` introduced by our 3.4.2.4 preview patch was removed.

The optional Spotlight preview setting now uses service **0.3.1**:
- Plays only while Spotlight is the active item container (301).
- When you move to any widget, the original skin's \`TMDbHelper.WidgetContainer\` changes to its widget ID (501, 502, etc). Our service immediately **stops only its own Spotlight trailer** and relinquishes the player to the native widget behaviour.
- On Spotlight slide change, it stops the previous trailer and can preview the new one.
- Retains preview ownership when YouTube or another Kodi plugin resolves \`plugin://\` to a different streaming URL during playback. The earlier service could otherwise lose its ownership and leave a video running.
- Stops the preview two seconds before the normal Spotlight auto-scroll timeout. Never starts a preview if Kodi is already playing another video. It does not change the underlying Emby Next Gen or the original skin's widget playback.
- Video preview remains **OFF by default** until enabled in Skin Settings.

**To test:** Install DEV skin **3.4.2.7** and confirm companion **0.3.1** under Kodi Add-ons > My add-ons > Services. Restart Kodi. Enable Spotlight preview with a 12s or 15s autoscroll. Let a Spotlight trailer start, then navigate down into widgets. The trailer should stop immediately and normal widget video behaviour should resume. Return to Spotlight and wait for the next slide; the old trailer must stop before new playback.

The GitHub CI tests simulate Spotlight-to-widget focus, resolved streaming URL changes, auto-scroll stop, original background video layer presence, service Python compilation and ZIP integrity. **Interactive playback on Windows Kodi 22 still requires verification.**

## Trailer launch fix in 3.4.2.5

The first service (0.1.0) could be **absent** even when the skin was installed because the dependency was `optional="true"`. In 3.4.2.5, `AF3 DEV - Spotlight Trailers 0.2.0` is an automatic/required *installed dependency* but preview is still **OFF by default** and must be enabled in the skin settings.

Other fixes:
- Do not gate on `Control.IsVisible(301)`, because Arctic Fuse 3 Spotlight wraplist 301 is intentionally placed off screen.
- Check the Spotlight `ListItem.Trailer` value, then **Kodi's own** `VideoLibrary.GetMovieDetails(movieid,properties=["trailer"])` if there is a Kodi movie DBID; finally use appropriate TMDbHelper window metadata when focused on Spotlight.
- Normalize regular YouTube `watch?v=` URLs to the Kodi YouTube add-on's playable `plugin://` URI. This does not fetch arbitrary internet trailers or connect to a private Emby server.
- `[AF3DEV.Trailer]` log lines report the service start and whether the Spotlight current item has a playable trailer (without showing private media paths).

**Test sequence:** First update skin and service. Restart Kodi. Check Add-ons > My add-ons > Services > AF3 DEV - Spotlight Trailers version 0.2.0 is enabled. Activate **Skin Settings > Menus > Spotlight : bandes-annonces auto**. Set **Behaviour > Autoscroll** to 12s or 15s. Try a local Kodi-library movie with a trailer (check its info page for Trailer first). If preview does not start, collect a fresh `%APPDATA%\Kodi\kodi.log` and search `[AF3DEV.Trailer]`: `disabled` means option off, `no_spotlight_items` means the list is not accessible, `trailer=missing` means no matching trailer in available metadata, `Requesting windowed trailer preview` means Kodi playback was requested.

The source ZIP for Emby Next Gen v12.4.23 shows the addon writes remote movie trailers to the Kodi database **only when Emby actually supplies `RemoteTrailers`**. Do not assume every item has a trailer. Installed Emby Next Gen was previously v12.4.24 in the user's Kodi log, so functionality with the exact installed version and its media data is not yet verified.

## Features in 3.4.2.5: premium tabs and Spotlight trailer preview

This is the **first modified** Arctic Fuse 3 DEV version and is still awaiting interactive Kodi 22 testing.

### Premium home tabs

**Settings > Skin Settings > Menus > Style des onglets** allows switching between:
- `Original - arrondi`: unchanged Arctic Fuse 3 rounded tab focus.
- `Premium - angles droits`: squared button focus derived from `common/box.png`.

The option appears with the horizontal text home navigation, not the icon or vertical layout. The original style remains the default.

### Spotlight video trailers (opt-in)

1. From **NTLS2000 - Kodi DEV Repository**, install `AF3 DEV - Spotlight Trailers` (`service.skin.arctic.fuse.3.dev.trailers`, v0.2.0), under **Services**.
2. In **Arctic Fuse 3 DEV**, navigate to **Settings > Skin Settings > Menus > Spotlight : bandes-annonces auto**, and enable the option.
3. Configure the normal automatic Spotlight slide interval under **Skin Settings > Behaviour > Autoscroll**. Default is 12 seconds. A 5-second interval leaves only a very brief preview.
4. Return to the **Home** Spotlight, select a movie with a valid `ListItem.Trailer` URL, wait about one second, and verify video preview and stopping before the next slide.

The service plays only Kodi `Container(301).ListItem.Trailer` when available. Emby Next Gen writes a remote movie trailer URL to Kodi's movie video database during synchronization (as inspected in source v12.4.23); no credentials or extra Emby connection is required. Trailer URLs may need a supported player/add-on (e.g. YouTube), and may be missing for a given movie.

Safety measures: *off by default*, does not launch when Kodi is already playing media, starts on Home only, checks for user-initiated playback changes, stops its own trailer before the expected auto-scroll transition (2-second margin), and automatically stops on Home exit or deactivation. It does not modify Emby or the original skin.

**Known limitation:** timing follows Kodi's nominal autoscroll interval from `AutoScrollTime`; timing and windowed video behaviour must be tested interactively. This feature is experimental. If video playback behaves unexpectedly, disable the option immediately and uninstall the optional service. The skin remains usable without it.

Direct packages:
- [Skin DEV 3.4.2.5](https://github.com/ntls2000/skin.arctic.fuse.3/releases/download/arctic-fuse-3-dev-3.4.2.5/skin.arctic.fuse.3.dev-3.4.2.5.zip)
- [Companion trailer service 0.1.0](https://raw.githubusercontent.com/ntls2000/skin.arctic.fuse.3/kodi-repo/kodi-repository/service.skin.arctic.fuse.3.dev.trailers/service.skin.arctic.fuse.3.dev.trailers-0.3.1.zip)

## Dependencies

- `xbmc.gui >= 5.17.0`
- `script.skinvariables >= 2.2.9`
- `script.texturemaker >= 0.2.9`
- `plugin.video.themoviedb.helper >= 6.17.9`
- `resource.images.weathericons.white >= 0.0.1`
- **`resource.images.arctic.splash >= 1.0.0`** (available from jurialmunkey's upstream repository)
- `resource.images.studios.coloured >= 0.0.1`
- `resource.font.robotocjksc >= 0.0.3`

The complete but much larger [Arctic Splash 1.0.6 resource ZIP](https://github.com/ntls2000/skin.arctic.fuse.3/releases/tag/arctic-splash-1.0.6-dependency) remains available as an **optional** manual upgrade. It is **not required** for DEV skin 3.4.2.5.

Emby Next Gen, Arctic Stream and other third-party extensions are not bundled. The skin is packaged and downloaded successfully in GitHub Actions, but still requires a real functional test on Kodi 22.

## Branches and build

- `omega`: original upstream source, unchanged.
- `dev-kodi22`: future modifications.
- `kodi-repo`: packages, repository index and publication CI.
- `.github/workflows/publish-baseline.yml`: generates the test skin and tests the Git-stored ZIP.
- `.github/workflows/verify-kodi-zip.yml`: downloads the publicly hosted ZIP, checks byte-for-byte identity, and publishes a GitHub Releases mirror.

## Credits and licensing

Original Arctic Fuse 3 authored by **jurialmunkey**. The separately authored preview service is licensed MIT. The original Creative Commons Attribution-NonCommercial-ShareAlike 4.0 license and credits are retained in the packaged addon.
