import argparse, os
from backup_engine import *
from app_definitions import *
from detect_installed_apps import get_installed_display_names

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["backup", "restore"], required=True)
    parser.add_argument("--apps", required=True)
    parser.add_argument("--zip", action="store_true")
    args = parser.parse_args()

    defs = load_plugins()
    defs.update(load_custom_rules())
    installed = get_installed_display_names()
    apps = args.apps.split(",")

    for app in apps:
        app = app.strip()
        if app not in defs:
            log(f"[SKIP] Неизвестное приложение: {app}")
            continue
        if app not in installed and not app.startswith("My"):
            log(f"[SKIP] Программа не установлена: {app}")
            continue

        data = defs[app]
        out_dir = os.path.join("Backup", app)
        os.makedirs(out_dir, exist_ok=True)

        if args.mode == "backup":
            any_data = False
            for f in data.get("files", []):
                if path_exists(f):
                    backup_file(f, out_dir)
                    any_data = True
            for d in data.get("folders", []):
                if path_exists(d):
                    backup_folder(d, out_dir)
                    any_data = True
            for r in data.get("registry", []):
                if registry_key_exists(r):
                    regfile = os.path.join(out_dir, f"{app}_reg.reg")
                    backup_registry_key(r, regfile)
                    any_data = True
            if args.zip and any_data:
                zipname = os.path.join("Backup", f"{app}_backup")
                compress_folder(out_dir, zipname)
        elif args.mode == "restore":
            for f in data.get("files", []):
                src = os.path.join(out_dir, os.path.basename(f))
                if os.path.exists(src):
                    restore_file(src, f)
            for d in data.get("folders", []):
                src = os.path.join(out_dir, os.path.basename(d))
                if os.path.exists(src):
                    restore_folder(src, d)
            for r in data.get("registry", []):
                regfile = os.path.join(out_dir, f"{app}_reg.reg")
                if os.path.exists(regfile):
                    restore_registry_key(regfile)

if __name__ == "__main__":
    main()

