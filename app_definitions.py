import json
import os

def load_plugins(dir="Plugins"):
    out = {}
    if not os.path.exists(dir):
        return out
    for f in os.listdir(dir):
        if f.endswith(".json"):
            try:
                with open(os.path.join(dir, f), "r", encoding="utf-8") as j:
                    out.update(json.load(j))
            except Exception as e:
                print(f"[ERROR] Не удалось загрузить {f}: {e}")
    return out

def load_custom_rules(path="Config/custom_rules.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}
