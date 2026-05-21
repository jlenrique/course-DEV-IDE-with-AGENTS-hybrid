from __future__ import annotations

from scripts.dev.check_mojibake import BAD_SEQUENCES, _find_hits


def test_known_mojibake_sequences_are_detected() -> None:
    text = "Lane split \u00e2\u2020\u2019 gate contract \u00c2\u00a7D3 and dash \u00e2\u20ac\u201d"
    hits = _find_hits(text)
    assert hits
    assert ("\u00e2\u2020\u2019", "\u2192") in hits
    assert ("\u00c2\u00a7", "\u00a7") in hits


def test_clean_text_has_no_hits() -> None:
    text = "Lane split \u2192 gate contract \u00a7D3 and dash \u2014"
    assert _find_hits(text) == []


def test_bad_sequence_table_covers_story_artifact_punctuation() -> None:
    expected = {
        "\u00c2\u00a7",
        "\u00c3\u2014",
        "\u00e2\u20ac\u201d",
        "\u00e2\u2020\u2019",
        "\u00e2\u2030\u00a5",
        "\u00e2\u0160\u00a5",
    }
    assert expected.issubset(BAD_SEQUENCES)
