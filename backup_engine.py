import os, shutil, zipfile, logging, subprocess

LOG_PATH = os.path.join("Logs", "backup.log")
os.makedirs("Logs", exist_ok=True)
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def log(msg):
    print(msg)
    logging.info(msg)

def expand(path): return os.path.expandvars(path)

def path_exists(path):
    return os.path.isfile(expand(path)) or os.path.isdir(expand(path))

def registry_key_exists(key_path):
    try:
        import winreg
        hive_map = {
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER
        }
        hive, subkey = key_path.split("\\", 1)
        with winreg.OpenKey(hive_map[hive], subkey): return True
    except: return False

def backup_file(src, dst_dir):
    try:
        src = expand(src)
        dst = os.path.join(dst_dir, os.path.basename(src))
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, dst)
        log(f"[BACKUP] File: {src}")
    except Exception as e:
        log(f"[ERROR] File: {src} — {e}")

def backup_folder(src, dst_dir):
    try:
        src = expand(src)
        dst = os.path.join(dst_dir, os.path.basename(src))
        shutil.copytree(src, dst, dirs_exist_ok=True)
        log(f"[BACKUP] Folder: {src}")
    except Exception as e:
        log(f"[ERROR] Folder: {src} — {e}")

def backup_registry_key(key, outfile):
    try:
        subprocess.run(["reg", "export", key, outfile, "/y"], check=True)
        log(f"[BACKUP] Registry: {key}")
    except Exception as e:
        log(f"[ERROR] Registry: {key} — {e}")

def restore_file(src_file, dst_path):
    try:
        os.makedirs(os.path.dirname(expand(dst_path)), exist_ok=True)
        shutil.copy2(src_file, expand(dst_path))
        log(f"[RESTORE] File restored: {src_file} → {dst_path}")
    except Exception as e:
        log(f"[ERROR] Restore file: {e}")

def restore_folder(src_folder, dst_folder):
    try:
        shutil.copytree(src_folder, expand(dst_folder), dirs_exist_ok=True)
        log(f"[RESTORE] Folder restored: {src_folder} → {dst_folder}")
    except Exception as e:
        log(f"[ERROR] Restore folder: {e}")

def restore_registry_key(reg_file):
    try:
        subprocess.run(["reg", "import", reg_file], check=True)
        log(f"[RESTORE] Registry imported: {reg_file}")
    except Exception as e:
        log(f"[ERROR] Import registry: {e}")

def compress_folder(folder, zip_path):
    try:
        shutil.make_archive(zip_path, "zip", folder)
        log(f"[ZIP] {zip_path}.zip")
    except Exception as e:
        log(f"[ERROR] ZIP: {e}")
