import shutil
from pathlib import Path

SITE_TITLE = "field notes"
ENTRIES_DIR = Path("entries")
OUTPUT_DIR = Path("docs")

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{site_title}</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;1,300&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background: #f7f6f2;
      color: #111;
      font-family: 'DM Sans', sans-serif;
      font-size: 16px;
    }}

    header {{
      padding: 40px;
      border-bottom: 1px solid #ccc;
    }}

    header h1 {{
      font-size: 18px;
      font-weight: 400;
    }}

    .grid {{
      padding: 40px;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 32px;
    }}

    .entry img {{
      width: 100%;
      aspect-ratio: 1;
      object-fit: cover;
      display: block;
    }}

    .entry p {{
      margin-top: 8px;
      font-size: 14px;
      color: #555;
      line-height: 1.6;
    }}

    .entry h3 {{
      margin-top: 6px;
      font-size: 16px;
      font-weight: 400;
      font-style: italic;
    }}
  </style>
</head>
<body>

  <header>
    <h1>{site_title}</h1>
  </header>

  <div class="grid">
    {grid_items}
  </div>

</body>
</html>"""


def read_note(entry_path):
    f = entry_path / "note.txt"
    return f.read_text(encoding="utf-8").strip() if f.exists() else ""

def find_image(entry_path):
    for f in entry_path.iterdir():
        if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            return f
    return None

def build_site():
    (OUTPUT_DIR / "images").mkdir(parents=True, exist_ok=True)
    entries = sorted([e for e in ENTRIES_DIR.iterdir() if e.is_dir()], reverse=True)

    if not entries:
        print("No entries found.")
        return

    items = []
    for entry in entries:
        image = find_image(entry)
        note = read_note(entry)
        lines = note.split("\n") if note else []
        title = lines[0] if lines else entry.name.replace("-", " ")
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        if image:
            shutil.copy2(image, OUTPUT_DIR / "images" / image.name)
            items.append(f"""
    <div class="entry">
      <img src="images/{image.name}" alt="{title}" />
      <h3>{title}</h3>
      <p>{body.replace(chr(10), '<br>')}</p>
    </div>""")
        else:
            items.append(f"""
    <div class="entry">
      <h3>{title}</h3>
      <p>{body.replace(chr(10), '<br>')}</p>
    </div>""")

    html = PAGE_TEMPLATE.format(
        site_title=SITE_TITLE,
        grid_items="\n".join(items),
    )

    (OUTPUT_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"✓ Done — {len(entries)} entries")

if __name__ == "__main__":
    build_site()
