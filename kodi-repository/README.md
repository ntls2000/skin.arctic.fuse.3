# NTLS2000 Kodi DEV Repository

Development distribution for **Arctic Fuse 3 DEV (Original)**, based on jurialmunkey's Arctic Fuse 3 **3.4.2**.

## Published builds

| Kodi addon | Addon ID | Version |
|---|---|---|
| NTLS2000 Kodi DEV Repository | `repository.ntls2000.kodi.dev` | `0.1.0` |
| Arctic Fuse 3 DEV (Original) | `skin.arctic.fuse.3.dev` | **`3.4.2.5`** |

Source baseline: `omega` commit `1f0b8fd67fa73738ea7f6fe1ff6dd8e3859192fb`. The skin has the upstream visuals and interface features, and a separate addon ID to avoid overwriting `skin.arctic.fuse.3`. The Arctic Splash minimum dependency is `1.0.0`. The trailer service is automatically installed with the DEV skin (v0.2.0); preview itself remains disabled by default.

## Installation

1. Install [the NTLS2000 repository](https://raw.githubusercontent.com/ntls2000/skin.arctic.fuse.3/kodi-repo/kodi-repository/repository.ntls2000.kodi.dev/repository.ntls2000.kodi.dev-0.1.0.zip) from **Kodi > Add-ons > Install from ZIP** (once).
2. Go to **Install from repository > NTLS2000 - Kodi DEV Repository > Look and feel > Skins** and choose **Arctic Fuse 3 DEV (Original) 3.4.2.5**.
3. Existing original skin and installed dependencies remain untouched. Switch skins using **Settings > Interface > Skin**.

Alternatively download the same verified Kodi archive from [GitHub Releases](https://github.com/ntls2000/skin.arctic.fuse.3/releases/download/arctic-fuse-3-dev-3.4.2.5/skin.arctic.fuse.3.dev-3.4.2.5.zip) and choose **Install from ZIP**.

**IMPORTANT:** Earlier 3.4.2.1 and 3.4.2.2 packages were corrupted *after generation* when checked into Git because the inherited `.gitattributes` applied `* text eol=lf` to ZIP files. This repository now has `*.zip binary`. The 3.4.2.5 archive has been validated with both Python and GNU unzip, from the Git blob and after HTTP download from the public Raw GitHub URL **and** the GitHub Releases mirror. Do not install any earlier version.

If Kodi previously downloaded the invalid package, exit Kodi and delete only the stale files named `skin.arctic.fuse.3.dev-3.4.2.1.zip` and/or `skin.arctic.fuse.3.dev-3.4.2.2.zip` from `%APPDATA%\Kodi\addons\packages\`, then reopen Kodi. Do not delete the rest of the packages directory or `userdata`.

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
- [Companion trailer service 0.1.0](https://raw.githubusercontent.com/ntls2000/skin.arctic.fuse.3/kodi-repo/kodi-repository/service.skin.arctic.fuse.3.dev.trailers/service.skin.arctic.fuse.3.dev.trailers-0.2.0.zip)

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
