"""Basic MIDI feature extraction utilities."""

from __future__ import annotations

import json
import os
import struct
from typing import Dict, List


class MidiFeatureError(RuntimeError):
    """Raised when feature extraction fails."""


def _read_chunk(stream) -> tuple[str, bytes]:
    header = stream.read(8)
    if len(header) < 8:
        raise MidiFeatureError("Unexpected end of file while reading chunk header")
    name = header[:4].decode("ascii", errors="replace")
    length = struct.unpack(">I", header[4:])[0]
    data = stream.read(length)
    if len(data) < length:
        raise MidiFeatureError("Unexpected end of file while reading chunk data")
    return name, data


def extract_features(path: str) -> Dict[str, object]:
    """Extract lightweight, general MIDI features.

    The implementation is intentionally minimal to avoid heavy dependencies.
    It inspects the MIDI header and track chunks to build a summary that can be
    used by other components of the package.
    """

    if not os.path.exists(path):
        raise MidiFeatureError(f"MIDI file not found: {path}")

    with open(path, "rb") as handle:
        header = handle.read(14)
        if len(header) < 14:
            raise MidiFeatureError("File too small to be a valid MIDI file")
        if header[:4] != b"MThd":
            raise MidiFeatureError("Missing MIDI header chunk (MThd)")

        declared_length = struct.unpack(">I", header[4:8])[0]
        if declared_length != 6:
            # Skip to the end of the declared header to continue parsing tracks.
            handle.read(declared_length - 6)

        format_type = struct.unpack(">H", header[8:10])[0]
        num_tracks_declared = struct.unpack(">H", header[10:12])[0]
        division_raw = struct.unpack(">H", header[12:14])[0]

        # Parse track chunks sequentially.
        track_lengths: List[int] = []
        note_on_events: List[int] = []
        distinct_status_bytes: set[int] = set()
        while True:
            try:
                chunk_name, chunk_data = _read_chunk(handle)
            except MidiFeatureError:
                break
            except Exception as exc:  # pragma: no cover - defensive
                raise MidiFeatureError(str(exc)) from exc

            if chunk_name != "MTrk":
                # Ignore non-track chunks (rare but valid extension chunks).
                continue

            track_lengths.append(len(chunk_data))
            status_counts = 0
            idx = 0
            prev_status = None
            while idx < len(chunk_data):
                # Skip delta time (variable-length quantity)
                delta = 0
                while idx < len(chunk_data):
                    delta_byte = chunk_data[idx]
                    idx += 1
                    delta = (delta << 7) | (delta_byte & 0x7F)
                    if not delta_byte & 0x80:
                        break

                if idx >= len(chunk_data):
                    break
                status = chunk_data[idx]
                if status < 0x80:
                    if prev_status is None:
                        break
                    status = prev_status
                    data_start = idx
                else:
                    idx += 1
                    data_start = idx
                    prev_status = status

                channel = status & 0x0F
                command = status & 0xF0
                distinct_status_bytes.add(status)

                if command in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                    data_length = 2
                elif command in (0xC0, 0xD0):
                    data_length = 1
                elif status == 0xFF:
                    data_length = 0
                    if data_start >= len(chunk_data):
                        break
                    meta_type = chunk_data[data_start]
                    data_start += 1
                    idx = data_start
                    length = 0
                    while idx < len(chunk_data):
                        length_byte = chunk_data[idx]
                        idx += 1
                        length = (length << 7) | (length_byte & 0x7F)
                        if not length_byte & 0x80:
                            break
                    idx += length
                    continue
                else:
                    data_length = 0

                idx = data_start + data_length

                if command == 0x90:
                    velocity = chunk_data[data_start + 1] if data_length == 2 and data_start + 1 < len(chunk_data) else 0
                    if velocity > 0:
                        status_counts += 1

            note_on_events.append(status_counts)

        features = {
            "format_type": format_type,
            "tracks_declared": num_tracks_declared,
            "division": division_raw,
            "track_lengths": track_lengths,
            "note_on_events": note_on_events,
            "distinct_status_bytes": sorted(distinct_status_bytes),
            "file_size": os.path.getsize(path),
        }

    features["tracks_observed"] = len(features["track_lengths"])
    features["track_consistency"] = (
        features["tracks_observed"] == features["tracks_declared"]
    )
    features["density"] = (
        sum(features["note_on_events"]) / features["tracks_observed"]
        if features["tracks_observed"]
        else 0
    )

    return features


def features_to_json(features: Dict[str, object]) -> str:
    """Return a JSON representation of extracted features."""

    return json.dumps(features, indent=2, sort_keys=True)
