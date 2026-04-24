"""Tests for compositor_operations.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "compositor_operations.py"
SPEC = importlib.util.spec_from_file_location("compositor_operations", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def sample_manifest() -> dict:
    return {
        "lesson_id": "C1-M1-L1",
        "title": "Compositor Smoke",
        "segments": [
            {
                "id": "seg-01",
                "narration_duration": 3.2,
                "narration_file": "course-content/staging/C1-M1-L1/audio/seg-01.mp3",
                "narration_vtt": "course-content/staging/C1-M1-L1/captions/seg-01.vtt",
                "visual_file": "course-content/staging/C1-M1-L1/visuals/seg-01.jpg",
                "visual_duration": 3.2,
                "transition_in": "fade",
                "transition_out": "cross-dissolve",
                "behavioral_intent": "credible",
                "music": "duck",
                "sfx_file": None,
                "visual_mode": "static-hold",
            }
        ],
    }


class TestTimelineRows:
    def test_build_timeline_rows(self) -> None:
        rows = MODULE.build_timeline_rows(sample_manifest())
        assert len(rows) == 1
        assert rows[0]["start"] == 0.0
        assert rows[0]["behavioral_intent"] == "credible"

    def test_build_timeline_rows_uses_longer_motion_window(self) -> None:
        manifest = sample_manifest()
        manifest["segments"][0].update(
            {
                "motion_type": "video",
                "motion_asset_path": "course-content/staging/C1-M1-L1/motion/seg-01_motion.mp4",
                "motion_duration_seconds": 5.0,
            }
        )
        manifest["segments"].append(
            {
                "id": "seg-02",
                "narration_duration": 2.0,
                "narration_file": "course-content/staging/C1-M1-L1/audio/seg-02.mp3",
                "narration_vtt": "course-content/staging/C1-M1-L1/captions/seg-02.vtt",
                "visual_file": "course-content/staging/C1-M1-L1/visuals/seg-02.jpg",
                "visual_duration": 2.0,
                "transition_in": "fade",
                "transition_out": "cross-dissolve",
                "behavioral_intent": "credible",
                "music": "duck",
                "sfx_file": None,
                "visual_mode": "static-hold",
            }
        )

        rows = MODULE.build_timeline_rows(manifest)

        assert rows[0]["segment_duration"] == 5.0
        assert rows[1]["start"] == 5.0

    def test_build_timeline_rows_generates_cluster_and_audio_annotations(self) -> None:
        manifest = {
            "lesson_id": "C1-M1-L1",
            "title": "Clustered Assembly",
            "segments": [
                {
                    "id": "seg-01",
                    "narration_duration": 4.8,
                    "narration_text": (
                        "Cognitive load theory explains why working memory constraints "
                        "shape learning."
                    ),
                    "narration_file": "course-content/staging/C1-M1-L1/audio/seg-01.mp3",
                    "visual_file": "course-content/staging/C1-M1-L1/visuals/seg-01.jpg",
                    "visual_duration": 4.8,
                    "transition_in": "fade",
                    "transition_out": "cut",
                    "behavioral_intent": "credible",
                    "bridge_type": "none",
                    "cluster_id": "c3",
                    "cluster_topic": "Cognitive Load Theory",
                    "master_behavioral_intent": "credible",
                    "cluster_role": "head",
                    "cluster_position": "establish",
                },
                {
                    "id": "seg-02",
                    "narration_duration": 12.0,
                    "narration_text": (
                        "Working memory can overload quickly when learners must track "
                        "too many interacting elements at once during an unfamiliar "
                        "task without scaffolded sequencing."
                    ),
                    "narration_file": "course-content/staging/C1-M1-L1/audio/seg-02.mp3",
                    "visual_file": "course-content/staging/C1-M1-L1/visuals/seg-02.jpg",
                    "visual_duration": 12.0,
                    "transition_in": "cut",
                    "transition_out": "cut",
                    "behavioral_intent": "clear-guidance",
                    "bridge_type": "none",
                    "cluster_id": "c3",
                    "cluster_role": "interstitial",
                    "cluster_position": "develop",
                    "interstitial_type": "emphasis-shift",
                    "isolation_target": "working memory",
                },
                {
                    "id": "seg-03",
                    "narration_duration": 3.0,
                    "narration_text": (
                        "That foundation now sets up the next cluster where we compare "
                        "high-load and low-load instructional designs."
                    ),
                    "narration_file": "course-content/staging/C1-M1-L1/audio/seg-03.mp3",
                    "visual_file": "course-content/staging/C1-M1-L1/visuals/seg-03.jpg",
                    "visual_duration": 3.0,
                    "transition_in": "fade",
                    "transition_out": "fade",
                    "behavioral_intent": "credible",
                    "bridge_type": "cluster_boundary",
                },
            ],
        }

        rows = MODULE.build_timeline_rows(manifest)

        assert rows[0]["cluster_label"] == '[HEAD — Cluster c3: "Cognitive Load Theory"]'
        assert rows[1]["cluster_label"] == '[INTERSTITIAL 1/1 — emphasis-shift: "working memory"]'
        assert rows[2]["cluster_label"] == "[STANDALONE]"
        assert rows[1]["transition_annotation"] == "[TRANSITION: cut — no effect]"
        assert rows[2]["transition_annotation"] == "[TRANSITION: beat/pause — brief black or fade]"
        assert rows[0]["audio_note"] == "[AUDIO: VO segment, 32-56s]"
        assert rows[1]["audio_note"] == "[AUDIO: VO segment, 10-16s]"
        assert rows[2]["boundary_audio_note"] == "[AUDIO: bridge VO, 15-20s]"
        assert rows[1]["expected_audio_seconds"] == round(
            rows[1]["word_count"] * 60.0 / 150.0,
            1,
        )


class TestGuideGeneration:
    def test_generate_assembly_guide_contains_behavioral_intent(self) -> None:
        guide = MODULE.generate_assembly_guide(
            sample_manifest(),
            "course-content/staging/C1-M1-L1/manifest.yaml",
        )
        assert "Behavioral Intent" in guide
        assert "`credible`" in guide
        assert "Intent note:" in guide
        assert "Track plan" in guide

    def test_generate_assembly_guide_file(self, tmp_path: Path) -> None:
        manifest_path = tmp_path / "manifest.yaml"
        manifest_path.write_text(
            """
lesson_id: C1-M1-L1
title: Compositor Smoke
segments:
  - id: seg-01
    narration_duration: 3.2
    narration_file: course-content/staging/C1-M1-L1/audio/seg-01.mp3
    narration_vtt: course-content/staging/C1-M1-L1/captions/seg-01.vtt
    visual_file: course-content/staging/C1-M1-L1/visuals/seg-01.jpg
    visual_duration: 3.2
    transition_in: fade
    transition_out: cross-dissolve
    behavioral_intent: credible
    music: duck
    sfx_file: null
    visual_mode: static-hold
""".strip()
            + "\n",
            encoding="utf-8",
        )
        output = MODULE.generate_assembly_guide_file(
            manifest_path, tmp_path / "descript-assembly-guide.md"
        )
        content = output.read_text(encoding="utf-8")
        assert "Descript Assembly Guide" in content
        assert "course-content/staging/C1-M1-L1/audio/seg-01.mp3" in content

    def test_generate_assembly_guide_contains_motion_instruction(self) -> None:
        manifest = sample_manifest()
        manifest["segments"][0].update(
            {
                "motion_type": "video",
                "motion_asset_path": "course-content/staging/C1-M1-L1/motion/seg-01_motion.mp4",
                "motion_duration_seconds": 5.0,
            }
        )
        guide = MODULE.generate_assembly_guide(
            manifest,
            "course-content/staging/C1-M1-L1/manifest.yaml",
        )
        assert "seg-01_motion.mp4" in guide
        assert "video track" in guide
        assert "Set segment duration to `5.00s`" in guide

    def test_generate_assembly_guide_includes_cluster_and_bridge_context(self) -> None:
        manifest = {
            "lesson_id": "C1-M1-L1",
            "title": "Clustered Assembly",
            "segments": [
                {
                    "id": "seg-01",
                    "narration_duration": 3.2,
                    "narration_text": (
                        "Cognitive load theory explains how working memory limits "
                        "learning."
                    ),
                    "narration_file": "course-content/staging/C1-M1-L1/audio/seg-01.mp3",
                    "visual_file": "course-content/staging/C1-M1-L1/visuals/seg-01.jpg",
                    "visual_duration": 3.2,
                    "transition_in": "fade",
                    "transition_out": "cross-dissolve",
                    "behavioral_intent": "credible",
                    "bridge_type": "cluster_boundary",
                    "cluster_id": "c1",
                    "cluster_topic": "Cognitive Load Theory",
                    "master_behavioral_intent": "credible",
                    "cluster_role": "head",
                    "cluster_position": "establish",
                },
                {
                    "id": "seg-02",
                    "narration_duration": 2.1,
                    "narration_text": (
                        "Notice the working memory bottleneck before layering extra "
                        "elements."
                    ),
                    "narration_file": "course-content/staging/C1-M1-L1/audio/seg-02.mp3",
                    "visual_file": "course-content/staging/C1-M1-L1/visuals/seg-02.jpg",
                    "visual_duration": 2.1,
                    "transition_in": "cut",
                    "transition_out": "cut",
                    "behavioral_intent": "credible",
                    "bridge_type": "none",
                    "cluster_id": "c1",
                    "cluster_role": "interstitial",
                    "cluster_position": "develop",
                    "interstitial_type": "emphasis-shift",
                    "isolation_target": "working memory",
                    "master_behavioral_intent": "credible",
                },
                {
                    "id": "seg-03",
                    "narration_duration": 2.0,
                    "narration_text": (
                        "This synthesis bridges us forward into practical teaching "
                        "moves that reduce overload."
                    ),
                    "narration_file": "course-content/staging/C1-M1-L1/audio/seg-03.mp3",
                    "visual_file": "course-content/staging/C1-M1-L1/visuals/seg-03.jpg",
                    "visual_duration": 2.0,
                    "transition_in": "fade",
                    "transition_out": "fade",
                    "behavioral_intent": "clear-guidance",
                    "bridge_type": "cluster_boundary",
                },
            ],
        }

        guide = MODULE.generate_assembly_guide(
            manifest,
            "course-content/staging/C1-M1-L1/manifest.yaml",
        )

        assert '[HEAD — Cluster c1: "Cognitive Load Theory"]' in guide
        assert '[INTERSTITIAL 1/1 — emphasis-shift: "working memory"]' in guide
        assert "[TRANSITION: cut — no effect]" in guide
        assert "[TRANSITION: beat/pause — brief black or fade]" in guide
        assert "[AUDIO: VO segment, 10-16s]" in guide
        assert "[AUDIO: bridge VO, 15-20s]" in guide
        assert "Bridge text (synthesis + forward pull)" in guide
        assert "Master behavioral intent: `credible`" in guide

    def test_generate_assembly_guide_marks_standalone_segments(self) -> None:
        guide = MODULE.generate_assembly_guide(
            sample_manifest(),
            "course-content/staging/C1-M1-L1/manifest.yaml",
        )

        assert "[STANDALONE]" in guide
        assert "[HEAD — Cluster" not in guide

    def test_generate_assembly_guide_normalizes_bridge_type_case(self) -> None:
        manifest = {
            "lesson_id": "C1-M1-L1",
            "title": "Bridge Case",
            "segments": [
                {
                    "id": "seg-01",
                    "narration_duration": 3.0,
                    "narration_text": "Cluster intro.",
                    "narration_file": "course-content/staging/C1-M1-L1/audio/seg-01.mp3",
                    "visual_file": "course-content/staging/C1-M1-L1/visuals/seg-01.jpg",
                    "visual_duration": 3.0,
                    "transition_in": "fade",
                    "transition_out": "fade",
                    "behavioral_intent": "credible",
                    "cluster_id": "c1",
                    "cluster_role": "head",
                    "cluster_position": "establish",
                },
                {
                    "id": "seg-02",
                    "narration_duration": 3.0,
                    "narration_text": "Boundary bridge narration keeps continuity.",
                    "narration_file": "course-content/staging/C1-M1-L1/audio/seg-02.mp3",
                    "visual_file": "course-content/staging/C1-M1-L1/visuals/seg-02.jpg",
                    "visual_duration": 3.0,
                    "transition_in": "fade",
                    "transition_out": "fade",
                    "behavioral_intent": "credible",
                    "bridge_type": "CLUSTER_BOUNDARY",
                },
            ],
        }

        guide = MODULE.generate_assembly_guide(
            manifest,
            "course-content/staging/C1-M1-L1/manifest.yaml",
        )

        assert "[AUDIO: bridge VO, 15-20s]" in guide
        assert "bridge audio covers the transition — no additional pause needed" in guide


class TestValidation:
    def test_validate_manifest_raises_for_missing_fields(self) -> None:
        manifest = {"segments": [{"id": "seg-01"}]}
        try:
            MODULE.validate_manifest(manifest)
        except ValueError as exc:
            assert "missing required fields" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("Expected validation failure")

    def test_validate_manifest_requires_motion_asset_for_non_static_segments(self) -> None:
        manifest = sample_manifest()
        manifest["segments"][0]["motion_type"] = "video"
        try:
            MODULE.validate_manifest(manifest)
        except ValueError as exc:
            assert "motion_asset_path" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("Expected validation failure")

    def test_validate_manifest_rejects_video_visual_file_for_motion_segments(self) -> None:
        manifest = sample_manifest()
        manifest["segments"][0].update(
            {
                "motion_type": "video",
                "motion_asset_path": "course-content/staging/C1-M1-L1/motion/seg-01_motion.mp4",
                "motion_duration_seconds": 5.0,
                "visual_file": "course-content/staging/C1-M1-L1/motion/seg-01_motion.mp4",
            }
        )
        try:
            MODULE.validate_manifest(manifest)
        except ValueError as exc:
            assert "visual_file as the approved still reference" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("Expected validation failure")


class TestSyncApprovedVisuals:
    def test_copies_visuals_and_updates_manifest(self, tmp_path: Path) -> None:
        repo = tmp_path
        (repo / ".git").mkdir()
        remote = repo / "gary-export" / "png"
        remote.mkdir(parents=True)
        (remote / "1_Slide.png").write_bytes(b"png-bytes")

        bundle = repo / "assembly-bundle"
        bundle.mkdir()
        manifest_path = bundle / "manifest.yaml"
        manifest_path.write_text(
            """
lesson_id: L1
title: Test
segments:
  - id: seg-01
    narration_duration: 1.0
    narration_file: assembly-bundle/audio/seg-01.mp3
    visual_file: gary-export/png/1_Slide.png
""".strip()
            + "\n",
            encoding="utf-8",
        )

        summary = MODULE.sync_approved_visuals_to_assembly_bundle(
            manifest_path, repo_root=repo
        )
        assert summary["copies"]
        copied = bundle / "visuals" / "1_Slide.png"
        assert copied.is_file()
        assert copied.read_bytes() == b"png-bytes"

        updated = MODULE.load_manifest(manifest_path)
        assert updated["segments"][0]["visual_file"] == "assembly-bundle/visuals/1_Slide.png"

    def test_idempotent_when_visual_already_in_bundle(self, tmp_path: Path) -> None:
        repo = tmp_path
        (repo / ".git").mkdir()
        bundle = repo / "assembly-bundle"
        vis = bundle / "visuals"
        vis.mkdir(parents=True)
        (vis / "a.png").write_bytes(b"x")
        manifest_path = bundle / "manifest.yaml"
        manifest_path.write_text(
            """
lesson_id: L1
title: Test
segments:
  - id: seg-01
    narration_duration: 1.0
    narration_file: assembly-bundle/audio/seg-01.mp3
    visual_file: assembly-bundle/visuals/a.png
""".strip()
            + "\n",
            encoding="utf-8",
        )
        MODULE.sync_approved_visuals_to_assembly_bundle(manifest_path, repo_root=repo)
        assert (vis / "a.png").read_bytes() == b"x"

    def test_sync_copies_motion_assets_and_updates_manifest(self, tmp_path: Path) -> None:
        repo = tmp_path
        (repo / ".git").mkdir()
        remote_visual = repo / "gary-export" / "png"
        remote_visual.mkdir(parents=True)
        (remote_visual / "1_Slide.png").write_bytes(b"png-bytes")
        remote_motion = repo / "motion-src"
        remote_motion.mkdir()
        (remote_motion / "slide-01_motion.mp4").write_bytes(b"mp4-bytes")

        bundle = repo / "assembly-bundle"
        bundle.mkdir()
        manifest_path = bundle / "manifest.yaml"
        manifest_path.write_text(
            """
lesson_id: L1
title: Test
segments:
  - id: seg-01
    narration_duration: 1.0
    narration_file: assembly-bundle/audio/seg-01.mp3
    visual_file: gary-export/png/1_Slide.png
    motion_type: video
    motion_asset_path: motion-src/slide-01_motion.mp4
    motion_duration_seconds: 5.0
""".strip()
            + "\n",
            encoding="utf-8",
        )

        summary = MODULE.sync_approved_visuals_to_assembly_bundle(manifest_path, repo_root=repo)
        assert summary["motion_copies"]
        copied = bundle / "motion" / "slide-01_motion.mp4"
        assert copied.is_file()
        assert copied.read_bytes() == b"mp4-bytes"

        updated = MODULE.load_manifest(manifest_path)
        assert (
            updated["segments"][0]["motion_asset_path"]
            == "assembly-bundle/motion/slide-01_motion.mp4"
        )

    def test_sync_clusters_visuals_into_cluster_subdirectories(self, tmp_path: Path) -> None:
        repo = tmp_path
        (repo / ".git").mkdir()
        remote = repo / "gary-export"
        (remote / "c1").mkdir(parents=True)
        (remote / "standalone").mkdir(parents=True)
        (remote / "c1" / "head.png").write_bytes(b"head")
        (remote / "c1" / "interstitial.png").write_bytes(b"interstitial")
        (remote / "standalone" / "flat.png").write_bytes(b"flat")

        bundle = repo / "assembly-bundle"
        bundle.mkdir()
        manifest_path = bundle / "manifest.yaml"
        manifest_path.write_text(
            """
lesson_id: L1
title: Test
segments:
  - id: seg-01
    narration_duration: 1.0
    narration_file: assembly-bundle/audio/seg-01.mp3
    visual_file: gary-export/c1/head.png
    cluster_id: c1
    cluster_role: head
  - id: seg-02
    narration_duration: 1.0
    narration_file: assembly-bundle/audio/seg-02.mp3
    visual_file: gary-export/c1/interstitial.png
    cluster_id: c1
    cluster_role: interstitial
  - id: seg-03
    narration_duration: 1.0
    narration_file: assembly-bundle/audio/seg-03.mp3
    visual_file: gary-export/standalone/flat.png
""".strip()
            + "\n",
            encoding="utf-8",
        )

        MODULE.sync_approved_visuals_to_assembly_bundle(manifest_path, repo_root=repo)
        updated = MODULE.load_manifest(manifest_path)
        visuals = {
            segment["id"]: segment["visual_file"] for segment in updated["segments"]
        }

        assert visuals["seg-01"].startswith("assembly-bundle/visuals/cluster_c1/")
        assert visuals["seg-02"].startswith("assembly-bundle/visuals/cluster_c1/")
        assert visuals["seg-03"].startswith("assembly-bundle/visuals/")
        assert "/cluster_" not in visuals["seg-03"]

    def test_sync_raises_on_cluster_visual_filename_collision(self, tmp_path: Path) -> None:
        repo = tmp_path
        (repo / ".git").mkdir()
        remote = repo / "gary-export"
        (remote / "c1-a").mkdir(parents=True)
        (remote / "c1-b").mkdir(parents=True)
        (remote / "c1-a" / "head.png").write_bytes(b"head-a")
        (remote / "c1-b" / "head.png").write_bytes(b"head-b")

        bundle = repo / "assembly-bundle"
        bundle.mkdir()
        manifest_path = bundle / "manifest.yaml"
        manifest_path.write_text(
            """
lesson_id: L1
title: Test
segments:
  - id: seg-01
    narration_duration: 1.0
    narration_file: assembly-bundle/audio/seg-01.mp3
    visual_file: gary-export/c1-a/head.png
    cluster_id: c1
    cluster_role: head
  - id: seg-02
    narration_duration: 1.0
    narration_file: assembly-bundle/audio/seg-02.mp3
    visual_file: gary-export/c1-b/head.png
    cluster_id: c1
    cluster_role: interstitial
""".strip()
            + "\n",
            encoding="utf-8",
        )

        try:
            MODULE.sync_approved_visuals_to_assembly_bundle(manifest_path, repo_root=repo)
        except ValueError as exc:
            assert "Refusing visual overwrite collision" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("Expected collision failure")
