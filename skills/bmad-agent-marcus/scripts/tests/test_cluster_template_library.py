from __future__ import annotations

from importlib import util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "cluster_template_library.py"
TEMPLATE_PATH = ROOT / "skills" / "bmad-agent-content-creator" / "references" / "cluster-templates.yaml"


def _load_module():
    spec = util.spec_from_file_location("cluster_template_library", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()
load_cluster_template_library = mod.load_cluster_template_library
validate_cluster_template_library = mod.validate_cluster_template_library
get_template_index = mod.get_template_index
REQUIRED_TEMPLATE_IDS = mod.REQUIRED_TEMPLATE_IDS
VALID_INTERSTITIAL_TYPES = mod.VALID_INTERSTITIAL_TYPES
VALID_CLUSTER_POSITIONS = mod.VALID_CLUSTER_POSITIONS
VALID_PACING_PROFILES = mod.VALID_PACING_PROFILES


def test_library_file_exists_and_parses():
    assert TEMPLATE_PATH.is_file()
    data = load_cluster_template_library(TEMPLATE_PATH)
    assert isinstance(data, dict)
    assert data.get("schema_version") == "1.0"


def test_required_template_ids_present():
    data = load_cluster_template_library(TEMPLATE_PATH)
    index = get_template_index(data)
    assert REQUIRED_TEMPLATE_IDS.issubset(index.keys())


def test_each_template_has_required_fields():
    data = load_cluster_template_library(TEMPLATE_PATH)
    templates = data.get("templates", [])
    required_fields = {
        "template_id",
        "display_name",
        "purpose",
        "interstitial_sequence",
        "interstitial_count",
        "best_for",
        "avoid_when",
        "pacing_profile",
        "head_word_range",
        "interstitial_word_ranges",
    }
    for template in templates:
        assert required_fields.issubset(template.keys())


def test_interstitial_count_matches_sequence_length():
    data = load_cluster_template_library(TEMPLATE_PATH)
    for template in data.get("templates", []):
        sequence = template.get("interstitial_sequence", [])
        count = template.get("interstitial_count")
        assert isinstance(count, int)
        assert count == len(sequence)
        assert 1 <= count <= 3


def test_sequence_uses_canonical_vocab():
    data = load_cluster_template_library(TEMPLATE_PATH)
    for template in data.get("templates", []):
        for step in template.get("interstitial_sequence", []):
            assert step["position"] in VALID_CLUSTER_POSITIONS
            assert step["interstitial_type"] in VALID_INTERSTITIAL_TYPES


def test_pacing_profile_enum_valid():
    data = load_cluster_template_library(TEMPLATE_PATH)
    for template in data.get("templates", []):
        assert template["pacing_profile"] in VALID_PACING_PROFILES


def test_word_ranges_are_two_int_bounds():
    data = load_cluster_template_library(TEMPLATE_PATH)
    for template in data.get("templates", []):
        head_range = template["head_word_range"]
        assert isinstance(head_range, list)
        assert len(head_range) == 2
        assert all(isinstance(v, int) for v in head_range)
        assert head_range[0] <= head_range[1]
        for position, span in template["interstitial_word_ranges"].items():
            assert position in VALID_CLUSTER_POSITIONS
            assert isinstance(span, list)
            assert len(span) == 2
            assert all(isinstance(v, int) for v in span)
            assert span[0] <= span[1]


def test_validator_passes_on_library():
    data = load_cluster_template_library(TEMPLATE_PATH)
    result = validate_cluster_template_library(data)
    assert result["passed"] is True
    assert result["errors"] == []


def test_validator_reports_errors_for_broken_fixture():
    broken = {
        "schema_version": "0.9",
        "templates": [
            {
                "template_id": "broken",
                "display_name": "Broken",
                "purpose": "bad",
                "interstitial_sequence": [{"position": "invalid", "interstitial_type": "bad"}],
                "interstitial_count": 2,
                "best_for": [],
                "avoid_when": [],
                "pacing_profile": "unknown",
                "head_word_range": [40, 20],
                "interstitial_word_ranges": {"invalid": [10]},
            }
        ],
    }
    result = validate_cluster_template_library(broken)
    assert result["passed"] is False
    assert result["errors"]


def test_validator_rejects_non_kebab_template_id():
    broken = {
        "schema_version": "1.0",
        "templates": [
            {
                "template_id": "Not-Kebab",
                "display_name": "Broken",
                "purpose": "bad",
                "interstitial_sequence": [{"position": "develop", "interstitial_type": "reveal"}],
                "interstitial_count": 1,
                "best_for": ["x"],
                "avoid_when": ["y"],
                "pacing_profile": "tight",
                "head_word_range": [20, 30],
                "interstitial_word_ranges": {"develop": [10, 20]},
            }
        ],
    }
    result = validate_cluster_template_library(broken)
    assert result["passed"] is False
    assert any("kebab-case" in msg for msg in result["errors"])


def test_validator_rejects_empty_best_for_or_avoid_when():
    broken = {
        "schema_version": "1.0",
        "templates": [
            {
                "template_id": "valid-id",
                "display_name": "Broken",
                "purpose": "bad",
                "interstitial_sequence": [{"position": "develop", "interstitial_type": "reveal"}],
                "interstitial_count": 1,
                "best_for": [],
                "avoid_when": [],
                "pacing_profile": "tight",
                "head_word_range": [20, 30],
                "interstitial_word_ranges": {"develop": [10, 20]},
            }
        ],
    }
    result = validate_cluster_template_library(broken)
    assert result["passed"] is False
    assert any(".best_for must not be empty" in msg for msg in result["errors"])
    assert any(".avoid_when must not be empty" in msg for msg in result["errors"])

