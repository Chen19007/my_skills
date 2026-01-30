from __future__ import annotations
from pathlib import Path
import yaml

root = Path(".")
paths = sorted(root.rglob("SKILL.md"))

print(f"total_skills: {len(paths)}")

for path in paths:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    report = []

    # Extract frontmatter
    if not lines or lines[0].strip() != "---":
        report.append("frontmatter: missing")
        fm_text = None
    else:
        end_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end_idx = i
                break
        if end_idx is None:
            report.append("frontmatter: missing closing delimiter")
            fm_text = None
        else:
            fm_text = "\n".join(lines[1:end_idx])

    # Parse YAML
    if fm_text is not None:
        try:
            data = yaml.safe_load(fm_text)
            report.append("yaml_parse: ok")
        except Exception as e:
            report.append(f"yaml_parse: fail ({type(e).__name__}: {e})")
            data = None
    else:
        data = None

    # Validate fields
    required = ["name", "description"]
    if data is None:
        report.append("required_fields: skipped (no yaml)")
    else:
        missing = [k for k in required if k not in data]
        if missing:
            report.append("required_fields: missing " + ", ".join(missing))
        else:
            report.append("required_fields: ok")

        for k in required:
            if k in data:
                report.append(f"type_{k}: {'ok' if isinstance(data[k], str) else 'fail'}")

    print("====", str(path).replace('\\', '/'))
    for item in report:
        print(item)
