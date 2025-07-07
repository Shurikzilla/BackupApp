import winreg

def get_installed_display_names():
    names = set()

    paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    for root, path in paths:
        try:
            with winreg.OpenKey(root, path) as main:
                for i in range(winreg.QueryInfoKey(main)[0]):
                    try:
                        sub = winreg.EnumKey(main, i)
                        with winreg.OpenKey(main, sub) as k:
                            val, _ = winreg.QueryValueEx(k, "DisplayName")
                            names.add(val)
                    except:
                        continue
        except:
            continue

    # Поиск нестандартных браузеров (Opera, Vivaldi) через App Paths
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths") as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                subkey = winreg.EnumKey(key, i)
                if "opera" in subkey.lower():
                    names.add("Opera")
                elif "vivaldi" in subkey.lower():
                    names.add("Vivaldi")
    except:
        pass

    return names
