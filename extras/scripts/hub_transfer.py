# -*- coding: utf-8 -*-
"""Hub-only profile transfer for Arctic Fuse 3 on Kodi 22 / Android TV."""
import copy
import datetime
import hashlib
import json
import os
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

import xbmc
import xbmcgui
import xbmcvfs

# The skin packager changes the original addon ID in all text source assets.
SKIN_ID = "skin.arctic.fuse.3"
FORMAT = "ntls2000-af3-hubs-v1"
MAX_FILES = 350
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 70 * 1024 * 1024
HUB_KEYS = (
    "homeswitcher.",
    "shortcuts.",
    "skinvariables.skinuser",
    "hub.",
)


def _user_root():
    return os.path.normpath(xbmcvfs.translatePath("special://profile/addon_data/"))


def _node_root(root):
    return os.path.join(root, "script.skinvariables", "nodes")


def _setting_file(root):
    return os.path.join(root, SKIN_ID, "settings.xml")


def _valid_profile(name):
    return name == SKIN_ID or name.startswith(SKIN_ID + "-")


def _is_hub_setting(name):
    return bool(name) and name.lower().startswith(HUB_KEYS)


def _read_hub_settings(xml_bytes):
    if not xml_bytes:
        return None
    root = ET.fromstring(xml_bytes)
    if root.tag != "settings" or any(child.tag != "setting" for child in root):
        raise ValueError("Format des reglages Kodi non reconnu")
    selected = ET.Element("settings", root.attrib)
    for el in root:
        if _is_hub_setting(el.get("id", "")):
            selected.append(copy.deepcopy(el))
    if len(selected) == 0:
        return None
    return ET.tostring(selected, encoding="utf-8", xml_declaration=True)


def _merge_hub_settings(current, backup):
    """Only hub keys; preserve the trailer toggle and Normal/Premium selector."""
    imported = ET.fromstring(backup)
    if imported.tag != "settings" or any(child.tag != "setting" for child in imported):
        raise ValueError("Reglages de sauvegarde invalides")
    if any(not _is_hub_setting(c.get("id", "")) for c in imported):
        raise ValueError("Reglages non lies aux hubs interdits")
    if current:
        dest = ET.fromstring(current)
        if dest.tag != "settings" or any(c.tag != "setting" for c in dest):
            raise ValueError("Reglages locaux Kodi non reconnus")
    else:
        dest = ET.Element("settings", imported.attrib)
    for el in list(dest):
        if _is_hub_setting(el.get("id", "")):
            dest.remove(el)
    for el in imported:
        dest.append(copy.deepcopy(el))
    return ET.tostring(dest, encoding="utf-8", xml_declaration=True)


def _read_limited(path):
    if os.path.getsize(path) > MAX_FILE_BYTES:
        raise ValueError("Fichier de hub trop volumineux")
    with open(path, "rb") as f:
        return f.read(MAX_FILE_BYTES + 1)


def _valid_member(name):
    if name == "hub_settings.xml":
        return True
    if "\\" in name or "\x00" in name or name.startswith("/") or ":" in name:
        return False
    parts = name.split("/")
    if len(parts) < 3 or parts[0] != "nodes" or any(x in ("", ".", "..") for x in parts):
        return False
    return _valid_profile(parts[1]) and parts[-1].lower().endswith((".json", ".xml"))


def _validate_payload(data):
    if len(data) > MAX_FILES or any(not _valid_member(x) for x in data):
        raise ValueError("Chemins ou nombre de fichiers invalides")
    if any(len(b) > MAX_FILE_BYTES for b in data.values()) or sum(map(len, data.values())) > MAX_TOTAL_BYTES:
        raise ValueError("Sauvegarde trop volumineuse")
    for name, blob in data.items():
        if name == "hub_settings.xml":
            _read_hub_settings(blob)
        elif name.lower().endswith(".json"):
            json.loads(blob.decode("utf-8"))
        elif name.lower().endswith(".xml"):
            ET.fromstring(blob)


def _gather(root):
    """Collect only this skin's shortcut/profile nodes and hub-specific keys."""
    result = {}
    nodes = _node_root(root)
    if os.path.isdir(nodes):
        for profile in sorted(os.listdir(nodes)):
            if not _valid_profile(profile):
                continue
            base = os.path.join(nodes, profile)
            if os.path.islink(base):
                raise ValueError("Lien symbolique dans les hubs")
            if not os.path.isdir(base):
                continue
            for folder, dirs, files in os.walk(base, followlinks=False):
                if os.path.islink(folder) or any(os.path.islink(os.path.join(folder, d)) for d in dirs):
                    raise ValueError("Lien symbolique dans les hubs")
                for name in sorted(files):
                    path = os.path.join(folder, name)
                    if os.path.islink(path):
                        raise ValueError("Lien symbolique dans les hubs")
                    if name.lower().endswith((".json", ".xml")):
                        rel = os.path.relpath(path, nodes).replace(os.sep, "/")
                        result["nodes/" + rel] = _read_limited(path)
    path = _setting_file(root)
    if os.path.isfile(path):
        hub_settings = _read_hub_settings(_read_limited(path))
        if hub_settings:
            result["hub_settings.xml"] = hub_settings
    _validate_payload(result)
    return result


def _make_zip(data, dest):
    _validate_payload(data)
    manifest = {
        "format": FORMAT,
        "skin_id": SKIN_ID,
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "files": {k: hashlib.sha256(v).hexdigest() for k, v in sorted(data.items())},
    }
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as arc:
        arc.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))
        for name, blob in sorted(data.items()):
            arc.writestr(name, blob)


def _read_zip(path):
    with zipfile.ZipFile(path, "r") as arc:
        infos = arc.infolist()
        names = [i.filename for i in infos]
        if len(names) != len(set(names)) or "manifest.json" not in names or len(names) > MAX_FILES + 1:
            raise ValueError("ZIP invalide ou fichiers en double")
        if any(i.is_dir() or ((i.external_attr >> 16) & 0o170000) == 0o120000 for i in infos):
            raise ValueError("Liens symboliques/repertoires ZIP interdits")
        if arc.getinfo("manifest.json").file_size > 128 * 1024:
            raise ValueError("Manifeste trop volumineux")
        manifest = json.loads(arc.read("manifest.json"))
        if manifest.get("format") != FORMAT or manifest.get("skin_id") != SKIN_ID:
            raise ValueError("Ceci n'est pas une sauvegarde Arctic Fuse 3 DEV")
        hashes = manifest.get("files")
        if not isinstance(hashes, dict) or set(names) != set(hashes) | {"manifest.json"}:
            raise ValueError("Contenu ZIP non conforme au manifeste")
        data = {}
        total = 0
        for info in infos:
            if info.filename == "manifest.json":
                continue
            if not _valid_member(info.filename) or info.file_size > MAX_FILE_BYTES:
                raise ValueError("Chemin ou taille ZIP interdits")
            total += info.file_size
            if total > MAX_TOTAL_BYTES:
                raise ValueError("ZIP trop volumineux")
            blob = arc.read(info)
            if len(blob) != info.file_size or hashlib.sha256(blob).hexdigest() != hashes[info.filename]:
                raise ValueError("Verification SHA256 du ZIP echouee")
            data[info.filename] = blob
        _validate_payload(data)
        return data


def _replace_data(root, data):
    """Stage incoming hubs; rollback both old nodes and settings on error."""
    _validate_payload(data)
    nodes = _node_root(root)
    os.makedirs(nodes, exist_ok=True)
    work = tempfile.mkdtemp(prefix="af3-hubs-stage-", dir=root)
    settings = _setting_file(root)
    old_settings = None
    moved, installed = [], []
    settings_touched = False
    try:
        incoming = os.path.join(work, "incoming")
        for rel, blob in data.items():
            if rel == "hub_settings.xml":
                continue
            target = os.path.join(incoming, *rel.split("/")[1:])
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "wb") as fp:
                fp.write(blob)
        old = os.path.join(work, "old")
        os.makedirs(old)
        for profile in os.listdir(nodes):
            if not _valid_profile(profile):
                continue
            existing = os.path.join(nodes, profile)
            if os.path.islink(existing):
                raise ValueError("Lien symbolique existant dans les hubs")
            os.replace(existing, os.path.join(old, profile))
            moved.append(profile)
        if os.path.isdir(incoming):
            for profile in os.listdir(incoming):
                os.replace(os.path.join(incoming, profile), os.path.join(nodes, profile))
                installed.append(profile)
        if "hub_settings.xml" in data:
            if os.path.islink(settings):
                raise ValueError("Lien symbolique dans les reglages")
            if os.path.isfile(settings):
                old_settings = _read_limited(settings)
            combined = _merge_hub_settings(old_settings, data["hub_settings.xml"])
            os.makedirs(os.path.dirname(settings), exist_ok=True)
            scratch = os.path.join(work, "settings.xml")
            with open(scratch, "wb") as fp:
                fp.write(combined)
            os.replace(scratch, settings)
            settings_touched = True
    except Exception:
        for profile in installed:
            path = os.path.join(nodes, profile)
            if os.path.isdir(path):
                shutil.rmtree(path)
        for profile in moved:
            os.replace(os.path.join(work, "old", profile), os.path.join(nodes, profile))
        if settings_touched:
            if old_settings is None:
                os.unlink(settings)
            else:
                with open(settings, "wb") as fp:
                    fp.write(old_settings)
        raise
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _local_temp():
    folder = xbmcvfs.translatePath("special://temp/")
    os.makedirs(folder, exist_ok=True)
    return folder


def _export():
    dialog = xbmcgui.Dialog()
    data = _gather(_user_root())
    if not data:
        dialog.ok("Sauvegarder mes hubs", "Aucun hub personnalise a sauvegarder.")
        return
    folder = dialog.browseSingle(3, "Destination (cle USB / dossier reseau)", "files", defaultt="")
    if not folder:
        return
    filename = "ArcticFuse3-DEV-Hubs-{}.zip".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    target = folder.rstrip("/\\") + "/" + filename
    with tempfile.TemporaryDirectory(dir=_local_temp()) as temp:
        archive = os.path.join(temp, filename)
        _make_zip(data, archive)
        if not xbmcvfs.copy(archive, target):
            raise IOError("Impossible d'ecrire vers ce dossier")
    dialog.ok("Sauvegarde des hubs", "ZIP enregistre :\n{}\n\nConserver ce ZIP en lieu prive.".format(target))


def _import():
    dialog = xbmcgui.Dialog()
    source = dialog.browseSingle(1, "Choisir une sauvegarde Arctic Fuse 3", "files", mask=".zip", defaultt="")
    if not source:
        return
    with tempfile.TemporaryDirectory(dir=_local_temp()) as temp:
        local = os.path.join(temp, "import.zip")
        if not xbmcvfs.copy(source, local):
            raise IOError("Impossible de lire le ZIP")
        incoming = _read_zip(local)
        if not incoming:
            raise ValueError("Sauvegarde vide")
        if not dialog.yesno(
            "Restaurer mes hubs ?",
            "Remplacer les hubs de cette TV ?\n"
            "Une sauvegarde de securite sera d'abord creee.\n"
            "Les reglages trailers et Premium/Normal seront preserves."
        ):
            return
        root = _user_root()
        safety = _gather(root)
        folder = os.path.join(root, SKIN_ID, "hub-backups")
        os.makedirs(folder, exist_ok=True)
        name = "avant-import-{}.zip".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
        destination = os.path.join(folder, name)
        with tempfile.NamedTemporaryFile(prefix="af3-backup-", suffix=".zip", dir=folder, delete=False) as stream:
            part = stream.name
        try:
            _make_zip(safety, part)
            os.replace(part, destination)
        finally:
            if os.path.exists(part):
                os.unlink(part)
        _replace_data(root, incoming)
        dialog.ok(
            "Restauration reussie",
            "{} fichier(s) restaures.\nBackup precedent : {}\n\n"
            "Fermez et redemarrez Kodi pour recharger hubs et widgets.".format(len(incoming), name)
        )


def main(action):
    try:
        if action == "export":
            _export()
        elif action == "import":
            _import()
        else:
            raise ValueError("Action inconnue")
    except Exception as exc:
        xbmc.log("Arctic Fuse hubs export/import: {}".format(exc), xbmc.LOGERROR)
        xbmcgui.Dialog().ok("Sauvegarde des hubs - erreur", "Operation interrompue :\n{}".format(exc))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
