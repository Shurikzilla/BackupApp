import os, json

PLUGINS = {
    "Google Chrome": {
        "folders": ["%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default"],
        "registry": ["HKEY_CURRENT_USER\\Software\\Google\\Chrome"]
    },
    "Mozilla Firefox": {
        "folders": ["%APPDATA%\\Mozilla\\Firefox\\Profiles"],
        "registry": ["HKEY_CURRENT_USER\\Software\\Mozilla"]
    },
    "Opera": {
        "folders": ["%APPDATA%\\Opera Software\\Opera Stable"],
        "registry": ["HKEY_CURRENT_USER\\Software\\Opera Software"]
    },
    "Vivaldi": {
        "folders": ["%LOCALAPPDATA%\\Vivaldi\\User Data\\Default"],
        "registry": ["HKEY_CURRENT_USER\\Software\\Vivaldi"]
    },
    "Microsoft Edge": {
        "folders": ["%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Default"],
        "registry": ["HKEY_CURRENT_USER\\Software\\Microsoft\\Edge"]
    },
    "Brave": {
        "folders": ["%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\User Data\\Default"],
        "registry": ["HKEY_CURRENT_USER\\Software\\BraveSoftware"]
    },
    "Telegram": {
        "folders": ["%APPDATA%\\Telegram Desktop"]
    },
    "Discord": {
        "folders": ["%APPDATA%\\discord"],
        "registry": ["HKEY_CURRENT_USER\\Software\\Discord"]
    },
    "Skype": {
        "folders": ["%APPDATA%\\Skype"]
    },
    "Zoom": {
        "folders": ["%APPDATA%\\Zoom"],
        "registry": ["HKEY_CURRENT_USER\\Software\\Zoom"]
    },
    "WhatsApp Desktop": {
        "folders": ["%APPDATA%\\WhatsApp"]
    },
    "Visual Studio Code": {
        "folders": ["%APPDATA%\\Code\\User"]
    },
    "Notepad++": {
        "folders": ["%APPDATA%\\Notepad++"]
    },
    "Sublime Text 3": {
        "folders": ["%APPDATA%\\Sublime Text 3"]
    },
    "IntelliJ IDEA": {
        "folders": ["%APPDATA%\\JetBrains\\IntelliJIdea2023.1"]
    },
    "PyCharm": {
        "folders": ["%APPDATA%\\JetBrains\\PyCharm2023.1"]
    },
    "Git": {
        "registry": ["HKEY_CURRENT_USER\\Software\\GitForWindows"]
    },
    "GitHub Desktop": {
        "folders": ["%APPDATA%\\GitHub Desktop"]
    },
    "Postman": {
        "folders": ["%APPDATA%\\Postman"]
    },
    "Node.js": {
        "registry": ["HKEY_LOCAL_MACHINE\\SOFTWARE\\Node.js"]
    },
    "Python": {
        "registry": ["HKEY_LOCAL_MACHINE\\SOFTWARE\\Python\\PythonCore"]
    },
    "Steam": {
        "folders": ["%PROGRAMFILES(X86)%\\Steam\\userdata"],
        "registry": ["HKEY_CURRENT_USER\\Software\\Valve\\Steam"]
    },
    "Battle.net": {
        "folders": ["%PROGRAMDATA%\\Battle.net"]
    },
    "Epic Games Launcher": {
        "folders": ["%LOCALAPPDATA%\\EpicGamesLauncher", "%PROGRAMDATA%\\Epic"]
    },
    "GOG Galaxy": {
        "folders": ["%PROGRAMDATA%\\GOG.com"]
    },
    "7-Zip": {
        "folders": ["%PROGRAMFILES%\\7-Zip"]
    },
    "WinRAR": {
        "folders": ["%APPDATA%\\WinRAR"]
    },
    "Total Commander": {
        "folders": ["%APPDATA%\\GHISLER"]
    },
    "ShareX": {
        "folders": ["%APPDATA%\\ShareX"]
    },
    "KeePassXC": {
        "folders": ["%APPDATA%\\KeePassXC"]
    },
    "OBS Studio": {
        "folders": ["%APPDATA%\\obs-studio"]
    },
    "VLC": {
        "folders": ["%APPDATA%\\vlc"]
    },
    "Spotify": {
        "folders": ["%APPDATA%\\Spotify"]
    },
    "Adobe Reader": {
        "folders": ["%APPDATA%\\Adobe\\Acrobat\\DC"]
    },
    "PotPlayer": {
        "folders": ["%APPDATA%\\DAUM\\PotPlayer"]
    },
    "Paint.NET": {
        "folders": ["%APPDATA%\\paint.net"]
    }
}

os.makedirs("Plugins", exist_ok=True)

for name, info in PLUGINS.items():
    data = {
        name: {
            "files": info.get("files", []),
            "folders": info.get("folders", []),
            "registry": info.get("registry", [])
        }
    }
    fname = f"Plugins/example_{name.lower().replace(' ', '_').replace('.', '').replace('-', '')}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Установлено {len(PLUGINS)} плагинов в папку Plugins/")

