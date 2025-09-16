"""Command-line interface for midi-inspo."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable

from .analysis import MidiFeatureError, extract_features
from .ideas import InspirationGenerator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate musical inspiration from MIDI files")
    parser.add_argument("midi_file", nargs="?", help="Path to the MIDI file to analyze")
    parser.add_argument(
        "--show-features",
        action="store_true",
        help="Include a human-readable feature dump in the output",
    )
    parser.add_argument(
        "--show-json",
        action="store_true",
        help="Include the raw feature JSON in the output",
    )
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Launch the graphical user interface instead of using the CLI",
    )
    return parser


def run_cli(args: argparse.Namespace) -> int:
    if args.ui:
        return launch_ui()

    if not args.midi_file:
        raise SystemExit("error: midi_file is required unless --ui is specified")

    try:
        features = extract_features(args.midi_file)
    except MidiFeatureError as exc:
        print(f"Error extracting features: {exc}", file=sys.stderr)
        return 1

    generator = InspirationGenerator(features)
    ideas = generator.generate_ideas(
        show_features=args.show_features,
        show_json=args.show_json,
    )
    print(ideas)
    return 0


def launch_ui() -> int:
    from .ui import launch_ui as _launch

    try:
        _launch()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return run_cli(args)


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
