# Dependency compatibility matrix (from upstream Arctic Fuse 3 v3.4.2)

| Add-on | Minimum version | Notes |
| --- | --- | --- |
| xbmc.gui | 5.17.0 | Kodi runtime |
| script.skinvariables | 2.2.9 | generated menus / data |
| script.texturemaker | 0.2.9 | textures |
| plugin.video.themoviedb.helper | 6.17.9 | TMDb widgets / metadata |
| resource.images.weathericons.white | 0.0.1 | icons |
| resource.images.arctic.splash | 1.0.6 | splash resources |
| resource.images.studios.coloured | 0.0.1 | studio logos |
| resource.font.robotocjksc | 0.0.3 | font |

Additional installed add-ons, such as **Emby for Kodi Next Gen** and **Arctic Stream**, should be retained, not overwritten. Their versions and compatibility require validation on each device. Kodi 22 RC on Windows and the Android Kodi installation should be tested separately.

The `resource.images.arctic.waves` resource is referenced in the skin source but is not declared as a required import; verify whether its behavior is optional before testing custom loading animations.
