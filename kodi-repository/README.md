# NTLS2000 Kodi DEV Repository

Development distribution for **Arctic Fuse 3 DEV (Original)**, based on jurialmunkey's Arctic Fuse 3 **3.4.2**.

## Published builds

| Kodi addon | Addon ID | Version |
|---|---|---|
| NTLS2000 Kodi DEV Repository | `repository.ntls2000.kodi.dev` | `0.1.0` |
| Arctic Fuse 3 DEV (Original) | `skin.arctic.fuse.3.dev` | **`3.4.2.3`** |

Source baseline: `omega` commit `1f0b8fd67fa73738ea7f6fe1ff6dd8e3859192fb`. The skin has the upstream visuals and interface features, and a separate addon ID to avoid overwriting `skin.arctic.fuse.3`. The Arctic Splash minimum dependency is `1.0.0`.

## Installation

1. Install [the NTLS2000 repository](https://raw.githubusercontent.com/ntls2000/skin.arctic.fuse.3/kodi-repo/kodi-repository/repository.ntls2000.kodi.dev/repository.ntls2000.kodi.dev-0.1.0.zip) from **Kodi > Add-ons > Install from ZIP** (once).
2. Go to **Install from repository > NTLS2000 - Kodi DEV Repository > Look and feel > Skins** and choose **Arctic Fuse 3 DEV (Original) 3.4.2.3**.
3. Existing original skin and installed dependencies remain untouched. Switch skins using **Settings > Interface > Skin**.

Alternatively download the same verified Kodi archive from [GitHub Releases](https://github.com/ntls2000/skin.arctic.fuse.3/releases/download/arctic-fuse-3-dev-3.4.2.3/skin.arctic.fuse.3.dev-3.4.2.3.zip) and choose **Install from ZIP**.

**IMPORTANT:** Earlier 3.4.2.1 and 3.4.2.2 packages were corrupted *after generation* when checked into Git because the inherited `.gitattributes` applied `* text eol=lf` to ZIP files. This repository now has `*.zip binary`. The 3.4.2.3 archive has been validated with both Python and GNU unzip, from the Git blob and after HTTP download from the public Raw GitHub URL **and** the GitHub Releases mirror. Do not install any earlier version.

If Kodi previously downloaded the invalid package, exit Kodi and delete only the stale files named `skin.arctic.fuse.3.dev-3.4.2.1.zip` and/or `skin.arctic.fuse.3.dev-3.4.2.2.zip` from `%APPDATA%\Kodi\addons\packages\`, then reopen Kodi. Do not delete the rest of the packages directory or `userdata`.

## Dependencies

- `xbmc.gui >= 5.17.0`
- `script.skinvariables >= 2.2.9`
- `script.texturemaker >= 0.2.9`
- `plugin.video.themoviedb.helper >= 6.17.9`
- `resource.images.weathericons.white >= 0.0.1`
- **`resource.images.arctic.splash >= 1.0.0`** (available from jurialmunkey's upstream repository)
- `resource.images.studios.coloured >= 0.0.1`
- `resource.font.robotocjksc >= 0.0.3`

The complete but much larger [Arctic Splash 1.0.6 resource ZIP](https://github.com/ntls2000/skin.arctic.fuse.3/releases/tag/arctic-splash-1.0.6-dependency) remains available as an **optional** manual upgrade. It is **not required** for DEV skin 3.4.2.3.

Emby Next Gen, Arctic Stream and other third-party extensions are not bundled. The skin is packaged and downloaded successfully in GitHub Actions, but still requires a real functional test on Kodi 22.

## Branches and build

- `omega`: original upstream source, unchanged.
- `dev-kodi22`: future modifications.
- `kodi-repo`: packages, repository index and publication CI.
- `.github/workflows/publish-baseline.yml`: generates the test skin and tests the Git-stored ZIP.
- `.github/workflows/verify-kodi-zip.yml`: downloads the publicly hosted ZIP, checks byte-for-byte identity, and publishes a GitHub Releases mirror.

## Credits and licensing

Original Arctic Fuse 3 authored by **jurialmunkey**. The original Creative Commons Attribution-NonCommercial-ShareAlike 4.0 license and credits are retained in the packaged addon.
