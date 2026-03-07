import shutil
from pathlib import Path

SITE_TITLE = "screenshots"
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
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background: #f7f6f2;
      color: #111;
      font-family: 'DM Sans', sans-serif;
      font-weight: 300;
      height: 100vh;
      overflow: hidden;
    }}

    header {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      padding: 24px 40px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 10;
    }}

    header h1 {{
      font-size: 13px;
      font-weight: 400;
      letter-spacing: 0.05em;
      color: #aaa;
    }}

    .counter {{
      font-size: 12px;
      color: #aaa;
      letter-spacing: 0.05em;
    }}

    /* CAROUSEL */
    .carousel {{
      position: fixed;
      inset: 0;
      display: flex;
      transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .slide {{
      min-width: 100vw;
      height: 100vh;
      display: grid;
      grid-template-columns: 1fr 1fr;
      padding: 80px 40px 40px;
      gap: 40px;
      align-items: center;
    }}

    .slide-image {{
      height: 100%;
      max-height: calc(100vh - 120px);
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .slide-image img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
    }}

    .slide-text {{
      padding: 40px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 20px;
    }}

    .slide-text h2 {{
      font-size: 13px;
      font-weight: 400;
      color: #aaa;
      letter-spacing: 0.05em;
    }}

    .slide-text p {{
      font-size: 15px;
      line-height: 2;
      color: #111;
      white-space: pre-line;
    }}

    /* text-only slide */
    .slide.text-only {{
      grid-template-columns: 1fr;
      max-width: 600px;
      margin: 0 auto;
    }}

    /* ARROWS */
    .arrow {{
      position: fixed;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      cursor: pointer;
      font-size: 20px;
      color: #ccc;
      padding: 16px;
      transition: color 0.2s;
      z-index: 10;
      user-select: none;
    }}

    .arrow:hover {{ color: #111; }}
    .arrow.left {{ left: 8px; }}
    .arrow.right {{ right: 8px; }}
    .arrow:disabled {{ opacity: 0; pointer-events: none; }}

    @media (max-width: 640px) {{
      .slide {{ grid-template-columns: 1fr; grid-template-rows: 1fr auto; padding: 72px 24px 24px; gap: 24px; }}
      .slide-text {{ padding: 0; }}
    }}
  </style>
</head>
<body>

  <header>
    <h1>{site_title}</h1>
    <span class="counter"><span id="current">1</span> / {entry_count}</span>
  </header>

  <div class="carousel" id="carousel">
    {slides}
  </div>

  <button class="arrow left" id="prev" onclick="go(-1)" disabled>&#8592;</button>
  <button class="arrow right" id="next" onclick="go(1)">&#8594;</button>

  <script>
    let current = 0;
    const total = {entry_count};

    function go(dir) {{
      current = Math.max(0, Math.min(total - 1, current + dir));
      document.getElementById('carousel').style.transform = `translateX(-${{current * 100}}vw)`;
      document.getElementById('current').textContent = current + 1;
      document.getElementById('prev').disabled = current === 0;
      document.getElementById('next').disabled = current === total - 1;
    }}

    document.addEventListener('keydown', e => {{
      if (e.key === 'ArrowRight') go(1);
      if (e.key === 'ArrowLeft') go(-1);
    }});
  </script>

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

    slides = []
    for entry in entries:
        image = find_image(entry)
        note = read_note(entry)
        lines = note.split("\n") if note else []
        title = lines[0] if lines else entry.name.replace("-", " ")
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        if image:
            shutil.copy2(image, OUTPUT_DIR / "images" / image.name)
            slides.append(f"""
    <div class="slide">
      <div class="slide-text">
        <h2>{title}</h2>
        <p>{body}</p>
      </div>
      <div class="slide-image">
        <img src="images/{image.name}" alt="{title}" />
      </div>
    </div>""")
        else:
            slides.append(f"""
    <div class="slide text-only">
      <div class="slide-text">
        <h2>{title}</h2>
        <p>{body}</p>
      </div>
    </div>""")

    html = PAGE_TEMPLATE.format(
        site_title=SITE_TITLE,
        slides="\n".join(slides),
        entry_count=len(entries),
    )

    (OUTPUT_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"✓ Done — {len(entries)} entries")

if __name__ == "__main__":
    build_site()
