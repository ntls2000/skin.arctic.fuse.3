# NTLS2000 - Kodi DEV Repository

This branch hosts a test Kodi add-on repository. Kodi add-on repository ID: `repository.ntls2000.kodi.dev`.

**Initial 0.1.0 release contains only the repository installer. The modified skin is not yet published.**

## Install
1. Download `kodi-repository/repository.ntls2000.kodi.dev/repository.ntls2000.kodi.dev-0.1.0.zip`.
2. In Kodi: Add-ons > Install from ZIP file; allow unknown sources if needed.
3. In Add-ons > Install from repository, open **NTLS2000 - Kodi DEV Repository**.
4. After the dev skin is validated and added here, it will appear as a separate add-on.

## Branch roles
- `omega`: unchanged upstream Arctic Fuse 3
- `dev-kodi22`: modified Kodi 22 skin development
- `kodi-repo`: online repository index and binary builds

## Distribution policy
- Test skin will use a distinct ID `skin.arctic.fuse.3.dev`, **not** the official `skin.arctic.fuse.3` ID.
- Only publish when SkinVariables paths, generated includes, source tree and dependencies have been audited.
- Keep all third-party extensions (Emby Next Gen, Arctic Stream, TMDb Helper and others) installed from their existing trusted repositories.
- Kodi resolves the dependencies from the skin's own `addon.xml`; this repo does not bundle these plugins.
- Each ZIP must be published at `kodi-repository/{addonid}/{addonid}-{version}.zip`; update `addons.xml` and its checksum together.
- No GitHub upstream release-dispatch workflow should run from this development branch.

## Upstream
https://github.com/jurialmunkey/skin.arctic.fuse.3

Arctic Fuse 3 source is under CC BY-NC-SA 4.0; maintain attribution and license if redistributing modified builds.
