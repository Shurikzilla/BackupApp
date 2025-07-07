import os

EXTENSIONS = [".ini", ".json", ".cfg", ".xml"]

BASE_DIRS = [
    os.path.expandvars("%APPDATA%"),
    os.path.expandvars("%LOCALAPPDATA%"),
    os.path.expandvars("%USERPROFILE%\\Documents")
]

def scan_user_configs():
    found = []
    for base in BASE_DIRS:
        for root, _, files in os.walk(base):
            for file in files:
                if os.path.splitext(file)[1].lower() in EXTENSIONS:
                    path = os.path.join(root, file)
                    if os.path.isfile(path) and os.path.getsize(path) < 5_000_000:  # до 5 МБ
                        found.append(path)
    return found

