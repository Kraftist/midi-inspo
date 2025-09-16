"""Generate creative prompts from MIDI feature data."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List

from .analysis import features_to_json


@dataclass
class InspirationContext:
    features: Dict[str, object]

    def describe_structure(self) -> str:
        tracks = self.features.get("tracks_observed", 0)
        fmt = self.features.get("format_type")
        division = self.features.get("division")
        density = self.features.get("density", 0)
        segments = [
            f"Format {fmt} with {tracks} track{'s' if tracks != 1 else ''}",
            f"Timing division: {division}",
            f"Average note density: {density:.2f}",
        ]
        if not self.features.get("track_consistency", True):
            segments.append("Declared track count does not match observed data")
        return "; ".join(segments)

    def suggested_focus(self) -> str:
        density = self.features.get("density", 0)
        if density < 4:
            return "Consider adding rhythmic ostinatos to increase energy."
        if density > 16:
            return "Try introducing sparse breakdowns for contrast."
        return "Balance momentum with space by alternating busy and calm sections."

    def groove_tip(self) -> str:
        status_bytes: Iterable[int] = self.features.get("distinct_status_bytes", [])
        percussive_channels = [status & 0x0F for status in status_bytes if status & 0xF0 == 0x99]
        if percussive_channels:
            channel_list = ", ".join(str(ch) for ch in sorted(set(percussive_channels)))
            return f"Highlight the percussion on channel(s) {channel_list} with subtle dynamics."
        return "Experiment with layering tuned percussion or found sounds for unique grooves."


class InspirationGenerator:
    """Convert MIDI features into natural-language inspiration."""

    def __init__(self, features: Dict[str, object], *, rng: random.Random | None = None):
        self.context = InspirationContext(features)
        self._rng = rng or random.Random()

    def _choice(self, options: List[str]) -> str:
        return self._rng.choice(options)

    def generate_ideas(self, *, show_features: bool = False, show_json: bool = False) -> str:
        context = self.context
        outline = [
            "🎼 MIDI Snapshot",
            context.describe_structure(),
            "",
            "✨ Creative Directions",
            self._choice(
                [
                    "Transform the harmonic rhythm by extending progressions over multiple bars.",
                    "Use call-and-response motifs between melodic voices for dialogue.",
                    "Swap a track's instrumentation with an unexpected timbre to spark a new vibe.",
                ]
            ),
            context.suggested_focus(),
            context.groove_tip(),
        ]

        if show_features:
            outline.extend([
                "",
                "📊 Feature Summary",
                json.dumps(context.features, indent=2, sort_keys=True),
            ])
        elif show_json:
            outline.extend([
                "",
                "📊 Feature JSON",
                features_to_json(context.features),
            ])

        return "\n".join(outline).strip()
