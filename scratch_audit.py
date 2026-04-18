import os, glob, re

print("== SQL AUDIT ==")
for fpath in glob.glob("**/*.py", recursive=True):
    with open(fpath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if any(kw in line.upper() for kw in ["SELECT", "INSERT", "UPDATE", "DELETE", "FROM", "WHERE"]):
                if "f\"" in line or "f'" in line or "+" in line:
                    print(f"[{fpath}:{i+1}] {line.strip()}")

print("== FILE PATH AUDIT ==")
for fpath in glob.glob("**/*.py", recursive=True):
    with open(fpath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if "os.path.join" in line or "open(" in line or ".to_csv" in line or "os.makedirs" in line:
                print(f"[{fpath}:{i+1}] {line.strip()}")

print("== PROMPT AUDIT ==")
for fpath in glob.glob("**/*.py", recursive=True):
    with open(fpath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if "system_prompt" in line or "user_prompt" in line or "prompt =" in line or "prompt=" in line:
                if "f\"" in line or "f'" in line:
                    print(f"[{fpath}:{i+1}] {line.strip()}")
