# NTLS2000 Kodi DEV Repository

Development distribution for **Arctic Fuse 3 DEV (Original)**, based on jurialmunkey's Arctic Fuse 3 **3.4.2**.

## Published builds

| Kodi addon | Addon ID | Version |
|---|---|---|
| NTLS2000 Kodi DEV Repository | `repository.ntls2000.kodi.dev` | `0.1.0` |
| Arctic Fuse 3 DEV (Original) | `skin.arctic.fuse.3.dev` | **`3.4.2.10`** |

Source baseline: `omega` commit `1f0b8fd67fa73738ea7f6fe1ff6dd8e3859192fb`. The skin has the upstream visuals and interface features, and a separate addon ID to avoid overwriting `skin.arctic.fuse.3`. The Arctic Splash minimum dependency is `1.0.0`. The trailer service is automatically installed with the DEV skin (v0.4.1); preview itself remains disabled by default.

## Installation

1. Install [the NTLS2000 repository](https://raw.githubusercontent.com/ntls2000/skin.arctic.fuse.3/kodi-repo/kodi-repository/repository.ntls2000.kodi.dev/repository.ntls2000.kodi.dev-0.1.0.zip) from **Kodi > Add-ons > Install from ZIP** (once).
2. Go to **Install from repository > NTLS2000 - Kodi DEV Repository > Look and feel > Skins** and choose **Arctic Fuse 3 DEV (Original) 3.4.2.10**.
3. Existing original skin and installed dependencies remain untouched. Switch skins using **Settings > Interface > Skin**.

Alternatively download the same verified Kodi archive from [GitHub Releases](https://github.com/ntls2000/skin.arctic.fuse.3/releases/download/arctic-fuse-3-dev-3.4.2.10/skin.arctic.fuse.3.dev-3.4.2.10.zip) and choose **Install from ZIP**.

**IMPORTANT:** Earlier 3.4.2.1 and 3.4.2.2 packages were corrupted *after generation* when checked into Git because the inherited `.gitattributes` applied `* text eol=lf` to ZIP files. This repository now has `*.zip binary`. The 3.4.2.10 archive has been validated with both Python and GNU unzip, from the Git blob and after HTTP download from the public Raw GitHub URL **and** the GitHub Releases mirror. Do not install any earlier version.

If Kodi previously downloaded the invalid package, exit Kodi and delete only the stale files named `skin.arctic.fuse.3.dev-3.4.2.1.zip` and/or `skin.arctic.fuse.3.dev-3.4.2.2.zip` from `%APPDATA%\Kodi\addons\packages\`, then reopen Kodi. Do not delete the rest of the packages directory or `userdata`.

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
