import json, glob, os, re
from collections import OrderedDict
import pandas as pd

def infer_locale_from_filename(fname):
    base = os.path.basename(fname)
    m = re.match(r"app_(.+)\.arb$", base, flags=re.IGNORECASE)
    return m.group(1) if m else os.path.splitext(base)[0]

def load_arb_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    locale = (data.get("@@locale") or infer_locale_from_filename(path)).strip()
    translations = {k: v for k, v in data.items() if not k.startswith("@")}
    return locale, translations

def ordered_locales(locales):
    loc_set = list(OrderedDict.fromkeys(locales))
    head = [l for l in ["ko", "en"] if l in loc_set]
    tail = sorted([l for l in loc_set if l not in {"ko", "en"}], key=lambda s: s.lower())
    return head + tail

def main():
    arb_files = sorted(glob.glob("*.arb"))
    locale_to_map = OrderedDict()
    all_keys = set()
    for fp in arb_files:
        locale, tr = load_arb_file(fp)
        locale_to_map[locale] = tr
        all_keys.update(tr.keys())
    sorted_keys = sorted(all_keys, key=lambda s: s.lower())
    locales = ordered_locales(list(locale_to_map.keys()))
    rows = []
    for k in sorted_keys:
        row = {"variable": k}
        for loc in locales:
            row[loc] = locale_to_map[loc].get(k, "")
        rows.append(row)
    df = pd.DataFrame(rows, columns=["variable"] + locales)
    with pd.ExcelWriter("다국어_번역.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="번역")

if __name__ == "__main__":
    main()
