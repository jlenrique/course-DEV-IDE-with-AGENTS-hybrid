import json
import pathlib

bundle = pathlib.Path("course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260403")
data = json.loads((bundle / "gary-dispatch-result.json").read_text(encoding="utf-8"))
slides = data["gary_slide_output"]
sc = json.loads((bundle / "gary-slide-content.json").read_text(encoding="utf-8"))
lt_slides = {3, 5, 6}
print("=== Literal-text content in gary-slide-content.json ===")
for s in sc["slides"]:
    if s["slide_number"] in lt_slides:
        print(f"  Slide {s['slide_number']}: {s['content'][:90]}...")
print()
print("=== Dispatch result slide entries ===")
for s in sorted(slides, key=lambda x: x.get("card_number", 0)):
    fid = s.get("fidelity", "(no fidelity)")
    print(f"  Card {s.get('card_number')}: fidelity={fid} | {s.get('slide_id')}")
