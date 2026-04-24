"""Canonical scaffold specialist reference for Slab 2 generator output.

This package is the source template for generated specialists:
- `graph.py`: canonical 9-node graph shape
- `state.py`: SpecialistEnvelope/SpecialistReturn subclass pins
- `model_config.yaml`: three-level model cascade shape
- `expertise/README.md`: expertise directory contract
"""

from app.specialists._scaffold.graph import build_scaffold_graph
from app.specialists._scaffold.state import ScaffoldEnvelope, ScaffoldReturn

__all__ = ["ScaffoldEnvelope", "ScaffoldReturn", "build_scaffold_graph"]
