"""Per-slide Storyboard-A "chooser" HTML emitter for Section 07C.

Renders a single static, dependency-free HTML document that a non-technical
client opens on gh-pages and a Playwright script can drive deterministically.

Playwright-stable contract (do not rename without updating the driver):
  - pick a variant:  ``.variant-card[data-slide="N"][data-variant="A"|"B"]``
  - finalize:        ``#copy-selections``
  - read result:     text content of ``#selection-code``

Result code format::

    SBA-{run_tag}-{idx}:{V} {idx}:{V} ...

every slide, ascending ``slide_index``, ``V`` = chosen variant, space-separated.
"""

from __future__ import annotations

import json
from html import escape
from typing import Any

__all__ = ["render_chooser_html"]


def _card(slide_index: int, variant: str, image_url: str) -> str:
    src = escape(str(image_url), quote=True)
    var = escape(str(variant), quote=True)
    return (
        f'      <div class="variant-card" data-slide="{slide_index}" '
        f'data-variant="{var}">\n'
        f'        <img src="{src}" alt="Slide {slide_index} variant {var}" />\n'
        f"        <div>Choose {var}</div>\n"
        f"      </div>"
    )


def _row(slide: dict[str, Any], total: int) -> list[str]:
    slide_index = int(slide["slide_index"])
    slide_id = escape(str(slide["slide_id"]))
    lines = [
        f'    <section class="slide-row" data-slide="{slide_index}">',
        "      <header>",
        f"        Slide {slide_index} of {total} — {slide_id}",
        f'        <span class="status-chip" data-slide="{slide_index}">Not chosen yet</span>',
        "      </header>",
        '      <div class="variants">',
    ]
    for variant in slide.get("variants", []):
        lines.append(_card(slide_index, variant["variant"], variant["image_url"]))
    lines.append("      </div>")
    lines.append("    </section>")
    return lines


_CSS = """\
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; margin: 0; padding: 0 16px 96px; }
    .slide-row { border-bottom: 1px solid #ddd; padding: 16px 0; }
    .slide-row header { font-weight: 600; margin-bottom: 8px; display: flex;
      align-items: center; gap: 12px; }
    .status-chip { font-weight: 600; padding: 2px 10px; border-radius: 12px;
      background: #fde2e2; color: #a40000; }
    .status-chip.chosen { background: #e2fde6; color: #006400; }
    .variants { display: flex; gap: 16px; flex-wrap: wrap; }
    .variant-card { border: 3px solid transparent; border-radius: 8px;
      padding: 8px; cursor: pointer; text-align: center; }
    .variant-card img { display: block; max-width: 360px; height: auto; }
    .variant-card.selected { border-color: #0066cc; background: #eef6ff; }
    #sticky-bar { position: fixed; left: 0; right: 0; bottom: 0;
      background: #fff; border-top: 1px solid #ccc; padding: 12px 16px;
      display: flex; align-items: center; gap: 16px; }
    #copy-selections:disabled { opacity: 0.5; cursor: not-allowed; }
    #selection-code { font-family: monospace; word-break: break-all; }\
"""


def _script(total: int, run_tag: str) -> str:
    # Pre-build the full "SBA-{run_tag}-" prefix, HTML-escape the run_tag so no
    # raw HTML-special characters leak into the <script> body, then JSON-encode
    # for safe embedding as a JS string literal. The emitted document therefore
    # contains the literal "SBA-{run_tag}-" prefix string.
    code_prefix = f"SBA-{escape(str(run_tag), quote=True)}-"
    code_prefix_js = json.dumps(code_prefix)
    return f"""\
  <script>
    (function () {{
      var TOTAL = {total};
      var CODE_PREFIX = {code_prefix_js};
      var picks = {{}};

      function refresh() {{
        var keys = Object.keys(picks);
        document.getElementById("picked-count").textContent = keys.length;
        var btn = document.getElementById("copy-selections");
        btn.disabled = keys.length !== TOTAL;
      }}

      function buildCode() {{
        var idxs = Object.keys(picks).map(Number).sort(function (a, b) {{
          return a - b;
        }});
        var parts = idxs.map(function (i) {{ return i + ":" + picks[i]; }});
        return CODE_PREFIX + parts.join(" ");
      }}

      var cards = document.querySelectorAll(".variant-card");
      for (var i = 0; i < cards.length; i++) {{
        cards[i].addEventListener("click", function () {{
          var slide = this.getAttribute("data-slide");
          var variant = this.getAttribute("data-variant");
          var siblings = document.querySelectorAll(
            '.variant-card[data-slide="' + slide + '"]'
          );
          for (var j = 0; j < siblings.length; j++) {{
            siblings[j].classList.remove("selected");
          }}
          this.classList.add("selected");
          picks[slide] = variant;
          var chip = document.querySelector(
            '.status-chip[data-slide="' + slide + '"]'
          );
          chip.textContent = "Chose " + variant;
          chip.classList.add("chosen");
          refresh();
        }});
      }}

      document.getElementById("copy-selections").addEventListener(
        "click",
        function () {{
          var code = buildCode();
          document.getElementById("selection-code").textContent = code;
          if (navigator.clipboard && navigator.clipboard.writeText) {{
            navigator.clipboard.writeText(code).catch(function () {{}});
          }}
        }}
      );

      refresh();
    }})();
  </script>\
"""


def render_chooser_html(slides: list[dict], run_tag: str) -> str:
    """Render the per-slide Storyboard-A chooser as a static HTML document.

    Args:
        slides: ``[{"slide_id": str, "slide_index": int, "variants":
            [{"variant": "A"|"B", "image_url": str}, ...]}, ...]`` already
            ordered by ``slide_index``.
        run_tag: run identifier embedded into the emitted selection code.

    Returns:
        A complete static HTML document (all CSS/JS inline, no external deps).
    """
    total = len(slides)
    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        f"  <title>Storyboard A chooser — {escape(str(run_tag))}</title>",
        "  <style>",
        _CSS,
        "  </style>",
        "</head>",
        "<body>",
        "  <main>",
    ]
    for slide in slides:
        lines.extend(_row(slide, total))
    lines.extend(
        [
            "  </main>",
            '  <div id="sticky-bar">',
            f'    <span>Picked <span id="picked-count">0</span> of {total}</span>',
            '    <button id="copy-selections" disabled>Copy my selections</button>',
            '    <code id="selection-code"></code>',
            "  </div>",
            _script(total, run_tag),
            "</body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(lines)
