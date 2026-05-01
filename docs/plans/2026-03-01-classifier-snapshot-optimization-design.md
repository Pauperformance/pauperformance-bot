# DPL Classifier Snapshot Optimization

## Problem

The DPL deck classifier (`pauperformance_bot/task/silver.py`) takes minutes to initialize because `get_dpl_classifier()` runs at module load time and:

1. Connects to Dropbox (OAuth2 session)
2. Builds card index from Scryfall (100s of API calls on first run)
3. Initializes `AcademyDataExporter` which logs into MTGGoldfish and paginates all decks (unused for classification)
4. Reads ~1,200 training deck files from disk
5. At runtime, fetches reference decks from MTGGoldfish archive and artifact land data from Scryfall

This makes it impractical for Lambda/serverless deployment and slow even on the Raspberry Pi server.

## Solution: Pre-serialized Classifier Snapshot

Split into two phases:

### Build Phase (offline, when training data changes)

A new script `pauperformance_bot/task/build_snapshot.py`:

1. Runs the existing `get_dpl_classifier()` flow (Dropbox, Scryfall, MTGGoldfish)
2. Pre-warms `_decks_cache` by fetching all archetype reference decks
3. Extracts artifact land names from Scryfall
4. Serializes to `resources/silver/classifier_snapshot.pkl`:

```python
{
    "archetypes": list[ArchetypeConfig],
    "known_decks": list[tuple[PlayableDeck, ArchetypeConfig]],
    "decks_cache": dict[str, PlayableDeck],
    "artifact_land_names": list[str],
}
```

Triggered manually or via CI. Training data changes every few days.

### Serve Phase (runtime, per cold start)

Changes to `silver.py` and `Decklassifier`:

- Replace `get_dpl_classifier()` with `load_dpl_classifier()` that loads from snapshot
- Add `Decklassifier.from_snapshot(path)` classmethod
- Modify `_is_affinity` to use pre-loaded artifact land names
- `_decks_cache` is pre-populated, so `classify_deck` skips `get_playable_deck()` calls

Cold start drops from minutes to <5 seconds (single file load).

## Changes Required

### New file: `pauperformance_bot/task/build_snapshot.py`

- Runs `get_dpl_classifier()` as today
- Pre-warms `_decks_cache` for all reference decks
- Extracts `artifact_land_names`
- Serializes snapshot to pickle

### Modified: `pauperformance_bot/service/pauperformance/silver/decklassifier.py`

- Add `_artifact_land_names: list[str]` field
- Add `from_snapshot(cls, path)` classmethod
- Modify `_is_affinity`: use `self._artifact_land_names` when available, fallback to Scryfall
- No changes to `classify_deck` (cache is pre-populated)

### Modified: `pauperformance_bot/task/silver.py`

- Replace `get_dpl_classifier()` with `load_dpl_classifier()`
- Load from snapshot file, fallback to current behavior if snapshot missing

## Error Handling

- Missing snapshot: fall back to current `get_dpl_classifier()` with warning log
- Stale snapshot: no automatic detection; rely on rebuild when data changes
- Optional: add timestamp to snapshot for logging

## Testing

- Test that builds a small snapshot and verifies classification matches live path

## Constraints

- Snapshot estimated at 5-20MB (within Lambda's 250MB limit)
- Project already uses pickle for caching (Scryfall cards, Deckstats decks)
- Backward compatible: existing `get_dpl_classifier()` still works as fallback
