#!/usr/bin/env python3
# Reuse at a new release: python3 tools/sv_apply.py <web-apps checkout> tools/sv-translations.json
# then translate whatever is still missing/English and add it to sv-translations.json.
"""Fill Swedish UI strings that are missing or still English.
Usage: sv_apply.py <web-apps repo> <translations.json ...>
A value is written only where sv.json lacks the key, has it empty, or has it
identical to the English source. Existing Swedish is never changed."""
import json, subprocess, sys, os
repo = sys.argv[1]
tr = {}
for f in sys.argv[2:]:
    tr.update(json.load(open(f, encoding='utf-8')))
def fill(sv, en):
    n = 0
    for k, e in en.items():
        if isinstance(e, dict):
            if k not in sv: sv[k] = {}
            if isinstance(sv[k], dict): n += fill(sv[k], e)
        elif isinstance(e, str) and e:
            cur = sv.get(k)
            if (not cur or cur == e) and e in tr and tr[e] != cur:
                sv[k] = tr[e]; n += 1
    return n
paths = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", "HEAD", "apps"],
                       capture_output=True, check=True).stdout.decode().split()
total = 0
for p in [p for p in paths if p.endswith("/locale/sv.json")]:
    full = os.path.join(repo, p)
    en = json.load(open(full[:-7] + "en.json", encoding="utf-8-sig"))
    raw = open(full, "rb").read(); text = raw.decode("utf-8-sig")
    nl = "\r\n" if "\r\n" in text else "\n"
    sv = json.loads(text)
    n = fill(sv, en)
    if not n: continue
    ind = 2
    for line in text.split(nl)[1:3]:
        s = len(line) - len(line.lstrip(" "))
        if s: ind = s; break
    out = json.dumps(sv, ensure_ascii=False, indent=ind)
    if text.endswith(nl): out += "\n"
    out = out.replace("\n", nl)
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    open(full, "wb").write(bom + out.encode("utf-8"))
    print(f"{n:5}  {p}"); total += n
print(f"{total:5}  total")
