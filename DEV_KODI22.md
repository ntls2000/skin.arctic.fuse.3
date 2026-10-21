# Kodi 22 development branch

Base: upstream Arctic Fuse 3 3.4.2 (source commit `1f0b8fd67fa73738ea7f6fe1ff6dd8e3859192fb`).

## Safety
- Do not change `omega`; test work goes here.
- Do not publish this source as a ZIP using the original `skin.arctic.fuse.3` identity.
- Planned independent Kodi add-on ID: `skin.arctic.fuse.3.dev`.
- Before building a distributable DEV skin, migrate all hard-coded skin IDs, SkinVariables names and generated include paths, and validate all referenced media files.
- Do not rename or update existing Emby Next Gen, Arctic Stream, TMDb Helper, SkinVariables or TextureMaker addons; refer to their installed IDs/paths.
- Dependency versions come from `addon.xml` of the original skin (source, not necessarily versions currently installed on the target Kodi).
- Test Windows Kodi 22 RC and Android separately, including EPG, Emby dynamic paths, Spotlight, trailers, playback OSD, focus, low-memory behavior and rollback.
- Maintain attribution/license CC BY-NC-SA 4.0.

## Release channel
Compiled and validated addon archives will be published in the separate `kodi-repo` Git branch under `kodi-repository/<addon.id>/<addon.id>-<version>.zip`; update `addons.xml` and checksum together.

## Dependency inventory (minimums, not installed versions)
```
xbmc.gui >= 5.17.0
script.skinvariables >= 2.2.9
script.texturemaker >= 0.2.9
plugin.video.themoviedb.helper >= 6.17.9
resource.images.weathericons.white >= 0.0.1
resource.images.arctic.splash >= 1.0.6
resource.images.studios.coloured >= 0.0.1
resource.font.robotocjksc >= 0.0.3
```

Additional add-ons used for integration checks: Emby for Kodi Next Gen 12.4.24 (service `plugin.service.emby-next-gen`; optional dynamic-node helper components), and Arctic Stream. Installed versions on each device have **not** been queried.
