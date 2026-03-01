# DPL Classifier Snapshot Optimization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reduce DPL classifier cold start from minutes to <5 seconds by pre-serializing all classifier state into a single pickle file.

**Architecture:** A build script runs the expensive initialization once and serializes archetypes, training decks, reference deck cache, and artifact land names into one pickle. At runtime, the service loads that single file — no Dropbox, Scryfall, or MTGGoldfish calls needed.

**Tech Stack:** Python pickle (already used throughout project), scipy (existing dependency for cosine similarity), pytest

**Design Doc:** `docs/plans/2026-03-01-classifier-snapshot-optimization-design.md`

---

### Task 1: Add `_artifact_land_names` to Decklassifier and decouple `_is_affinity`

The `_is_affinity` method currently calls `self.pauperformance.scryfall.get_legal_artifact_lands()` at classification time. We need it to work with pre-loaded data instead.

**Files:**
- Modify: `pauperformance_bot/service/pauperformance/silver/decklassifier.py:33-46` (constructor)
- Modify: `pauperformance_bot/service/pauperformance/silver/decklassifier.py:118-139` (`_is_affinity`)
- Test: `tests/test_decklassifier.py` (create)

**Step 1: Write the failing test**

Create `tests/test_decklassifier.py`:

```python
from pauperformance_bot.entity.deck.playable import PlayableDeck, PlayedCard
from pauperformance_bot.entity.config.archetype import ArchetypeConfig
from pauperformance_bot.service.pauperformance.silver.decklassifier import Decklassifier


def _make_archetype(name, must_have=None, must_not_have=None, reference_decks=None):
    return ArchetypeConfig(
        name=name,
        aliases=[],
        family=None,
        dominant_mana=[],
        game_type=["Aggro"],
        description="",
        must_have_cards=must_have or [],
        must_not_have_cards=must_not_have or [],
        reference_decks=reference_decks or [],
        resource_sideboard=None,
        resources_discord=[],
        resources=[],
    )


def _make_deck(mainboard_cards, sideboard_cards=None):
    mainboard = [PlayedCard(qty, name) for name, qty in mainboard_cards.items()]
    sideboard = [PlayedCard(qty, name) for name, qty in (sideboard_cards or {}).items()]
    return PlayableDeck(mainboard, sideboard, raise_error_if_invalid=False)


def test_is_affinity_with_preloaded_artifact_lands():
    """_is_affinity should use pre-loaded artifact land names when available."""
    archetype = _make_archetype("Affinity")
    archetypes = [archetype]

    artifact_land_names = [
        "Ancient Den",
        "Great Furnace",
        "Seat of the Synod",
        "Tree of Tales",
        "Vault of Whispers",
        "Darksteel Citadel",
        "Mistvault Bridge",
        "Razortide Bridge",
        "Rustvale Bridge",
        "Silverbluff Bridge",
        "Slagwoods Bridge",
        "Tanglepool Bridge",
        "Thornglint Bridge",
        "Drossforge Bridge",
        "Goldmire Bridge",
    ]

    # Build an Affinity deck
    deck = _make_deck({
        "Ancient Den": 4,
        "Great Furnace": 4,
        "Seat of the Synod": 4,
        "Tree of Tales": 4,
        "Frogmite": 4,
        "Myr Enforcer": 4,
        "Galvanic Blast": 4,
        "Thoughtcast": 4,
        "Chromatic Star": 4,
        "Springleaf Drum": 4,
        "Island": 4,
        "Ornithopter": 4,
        "Somber Hoverguard": 4,
        "Atog": 4,
        "Disciple of the Vault": 4,
    })

    classifier = Decklassifier.from_snapshot_data(
        archetypes=archetypes,
        known_decks=[],
        decks_cache={},
        artifact_land_names=artifact_land_names,
    )

    assert classifier._is_affinity(deck) is True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_decklassifier.py::test_is_affinity_with_preloaded_artifact_lands -v`
Expected: FAIL with `AttributeError: type object 'Decklassifier' has no attribute 'from_snapshot_data'`

**Step 3: Implement the changes**

In `pauperformance_bot/service/pauperformance/silver/decklassifier.py`:

Add `_artifact_land_names` field to `__init__`:

```python
class Decklassifier:
    def __init__(
        self,
        pauperformance: PauperformanceService,
        known_decks: list[tuple[PlayableDeck, ArchetypeConfig]] = None,
    ):
        self.pauperformance: PauperformanceService = pauperformance
        self.archetypes: list[ArchetypeConfig] = (
            self.pauperformance.config_reader.list_archetypes()
        )
        self.known_decks: list[tuple[PlayableDeck, ArchetypeConfig]] = (
            known_decks if known_decks else []
        )
        self._decks_cache: dict[str, PlayableDeck] = {}
        self._artifact_land_names: list[str] | None = None

    @classmethod
    def from_snapshot_data(
        cls,
        archetypes,
        known_decks,
        decks_cache,
        artifact_land_names,
    ):
        instance = cls.__new__(cls)
        instance.pauperformance = None
        instance.archetypes = archetypes
        instance.known_decks = known_decks if known_decks else []
        instance._decks_cache = decks_cache if decks_cache else {}
        instance._artifact_land_names = artifact_land_names
        return instance
```

Update `_is_affinity` to use pre-loaded data when available:

```python
    def _is_affinity(self, deck: PlayableDeck) -> bool:
        if self._artifact_land_names is not None:
            artifact_lands_names = self._artifact_land_names
        else:
            artifact_lands = self.pauperformance.scryfall.get_legal_artifact_lands()
            artifact_lands_names = [c["name"] for c in artifact_lands]
        affinity_creatures = [
            "Frogmite",
            "Atog",
            "Myr Enforcer",
            "Carapace Forger",
            "Sojourner's Companion",
            "Somber Hoverguard",
        ]
        has_artifact_mana_base = (
            len([c for c in artifact_lands_names if c in deck]) >= 4
        )
        has_affinity_creatures = len([c for c in affinity_creatures if c in deck]) >= 2
        if (
            has_artifact_mana_base
            and has_affinity_creatures
            and "Galvanic Blast" in deck
        ):
            return True
        return False
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_decklassifier.py::test_is_affinity_with_preloaded_artifact_lands -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_decklassifier.py pauperformance_bot/service/pauperformance/silver/decklassifier.py
git commit -m "feat: add from_snapshot_data classmethod and decouple _is_affinity from Scryfall"
```

---

### Task 2: Add `from_snapshot_data` classification test (no pauperformance dependency)

Verify the classifier can classify decks using only snapshot data, without any PauperformanceService.

**Files:**
- Modify: `tests/test_decklassifier.py`

**Step 1: Write the failing test**

Add to `tests/test_decklassifier.py`:

```python
def test_classify_deck_with_known_decks():
    """Classifier should find the most similar archetype from known_decks."""
    burn_archetype = _make_archetype("Burn")
    elves_archetype = _make_archetype("Elves")

    # A known Burn deck
    known_burn = _make_deck({
        "Lightning Bolt": 4,
        "Lava Spike": 4,
        "Rift Bolt": 4,
        "Chain Lightning": 4,
        "Fireblast": 2,
        "Searing Blaze": 4,
        "Ghitu Lavarunner": 4,
        "Thermo-Alchemist": 4,
        "Mountain": 18,
        "Needle Drop": 4,
        "Skewer the Critics": 4,
        "Shard Volley": 4,
    })

    # A new deck that's clearly Burn
    new_burn = _make_deck({
        "Lightning Bolt": 4,
        "Lava Spike": 4,
        "Rift Bolt": 4,
        "Chain Lightning": 4,
        "Fireblast": 4,
        "Searing Blaze": 2,
        "Ghitu Lavarunner": 4,
        "Thermo-Alchemist": 4,
        "Mountain": 18,
        "Needle Drop": 4,
        "Skewer the Critics": 4,
        "Shard Volley": 4,
    })

    classifier = Decklassifier.from_snapshot_data(
        archetypes=[burn_archetype, elves_archetype],
        known_decks=[(known_burn, burn_archetype)],
        decks_cache={},
        artifact_land_names=[],
    )

    archetype, similarity = classifier.classify_deck(new_burn)
    assert archetype.name == "Burn"
    assert similarity > 0.9
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/test_decklassifier.py::test_classify_deck_with_known_decks -v`
Expected: PASS (the `from_snapshot_data` and `classify_deck` code should already handle this - known_decks comparison at line 267-273 doesn't need `pauperformance`)

Note: If this fails because `classify_deck` tries to access `self.pauperformance.get_playable_deck()` for reference decks, that's expected — the test has no reference_decks in archetypes so that code path won't execute. The known_decks path (lines 267-273) works independently.

**Step 3: Commit**

```bash
git add tests/test_decklassifier.py
git commit -m "test: add classification test using snapshot data without PauperformanceService"
```

---

### Task 3: Handle `classify_deck` reference deck path when `pauperformance` is None

When running from a snapshot, `self.pauperformance` is `None`, but reference decks are pre-cached in `_decks_cache`. We need `classify_deck` to handle the case where a reference deck isn't in the cache and `pauperformance` is unavailable.

**Files:**
- Modify: `pauperformance_bot/service/pauperformance/silver/decklassifier.py:247-265`
- Test: `tests/test_decklassifier.py`

**Step 1: Write the failing test**

Add to `tests/test_decklassifier.py`:

```python
def test_classify_deck_with_precached_reference_decks():
    """Classifier should use _decks_cache for reference decks without calling pauperformance."""
    burn_archetype = _make_archetype("Burn", reference_decks=["burn_ref_1"])

    burn_ref_deck = _make_deck({
        "Lightning Bolt": 4,
        "Lava Spike": 4,
        "Rift Bolt": 4,
        "Chain Lightning": 4,
        "Fireblast": 2,
        "Searing Blaze": 4,
        "Ghitu Lavarunner": 4,
        "Thermo-Alchemist": 4,
        "Mountain": 18,
        "Needle Drop": 4,
        "Skewer the Critics": 4,
        "Shard Volley": 4,
    })

    new_burn = _make_deck({
        "Lightning Bolt": 4,
        "Lava Spike": 4,
        "Rift Bolt": 4,
        "Chain Lightning": 4,
        "Fireblast": 4,
        "Searing Blaze": 2,
        "Ghitu Lavarunner": 4,
        "Thermo-Alchemist": 4,
        "Mountain": 18,
        "Needle Drop": 4,
        "Skewer the Critics": 4,
        "Shard Volley": 4,
    })

    classifier = Decklassifier.from_snapshot_data(
        archetypes=[burn_archetype],
        known_decks=[],
        decks_cache={"burn_ref_1": burn_ref_deck},
        artifact_land_names=[],
    )

    archetype, similarity = classifier.classify_deck(new_burn)
    assert archetype.name == "Burn"
    assert similarity > 0.9


def test_classify_deck_skips_uncached_reference_when_no_pauperformance():
    """When pauperformance is None and reference deck is not cached, skip it gracefully."""
    burn_archetype = _make_archetype("Burn", reference_decks=["missing_ref_1"])

    known_burn = _make_deck({
        "Lightning Bolt": 4,
        "Lava Spike": 4,
        "Rift Bolt": 4,
        "Chain Lightning": 4,
        "Fireblast": 2,
        "Searing Blaze": 4,
        "Ghitu Lavarunner": 4,
        "Thermo-Alchemist": 4,
        "Mountain": 18,
        "Needle Drop": 4,
        "Skewer the Critics": 4,
        "Shard Volley": 4,
    })

    new_burn = _make_deck({
        "Lightning Bolt": 4,
        "Lava Spike": 4,
        "Rift Bolt": 4,
        "Chain Lightning": 4,
        "Fireblast": 4,
        "Searing Blaze": 2,
        "Ghitu Lavarunner": 4,
        "Thermo-Alchemist": 4,
        "Mountain": 18,
        "Needle Drop": 4,
        "Skewer the Critics": 4,
        "Shard Volley": 4,
    })

    classifier = Decklassifier.from_snapshot_data(
        archetypes=[burn_archetype],
        known_decks=[(known_burn, burn_archetype)],
        decks_cache={},  # reference deck NOT cached
        artifact_land_names=[],
    )

    # Should still classify via known_decks, skipping the missing reference
    archetype, similarity = classifier.classify_deck(new_burn)
    assert archetype.name == "Burn"
    assert similarity > 0.9
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_decklassifier.py::test_classify_deck_skips_uncached_reference_when_no_pauperformance -v`
Expected: FAIL with `AttributeError: 'NoneType' object has no attribute 'get_playable_deck'` (because `self.pauperformance` is `None`)

**Step 3: Implement the fix**

In `decklassifier.py`, modify the reference deck fetch block (lines 253-259):

```python
            for reference_deck in archetype.reference_decks:
                logger.debug(f"Comparing deck with reference list {reference_deck}...")
                if reference_deck not in self._decks_cache:
                    if self.pauperformance is None:
                        logger.debug(
                            f"Skipping uncached reference deck {reference_deck} "
                            f"(no pauperformance service available)."
                        )
                        continue
                    self._decks_cache[reference_deck] = (
                        self.pauperformance.get_playable_deck(reference_deck)
                    )
                deck2 = self._decks_cache[reference_deck]
```

**Step 4: Run all decklassifier tests**

Run: `pytest tests/test_decklassifier.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add pauperformance_bot/service/pauperformance/silver/decklassifier.py tests/test_decklassifier.py
git commit -m "feat: handle missing reference decks gracefully when pauperformance is None"
```

---

### Task 4: Create the build_snapshot script

This script runs the expensive initialization once and serializes everything needed.

**Files:**
- Create: `pauperformance_bot/task/build_snapshot.py`
- Reference: `pauperformance_bot/task/silver.py` (for existing `get_dpl_classifier()`)

**Step 1: Write the build script**

Create `pauperformance_bot/task/build_snapshot.py`:

```python
import pickle

from pauperformance_bot.constant.pauperformance.myr import (
    SILVER_DIR,
)
from pauperformance_bot.task.silver import get_dpl_classifier
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path

logger = get_application_logger()

SNAPSHOT_PATH = posix_path(SILVER_DIR, "classifier_snapshot.pkl")


def build_snapshot(output_path=SNAPSHOT_PATH):
    logger.info("Building classifier snapshot...")

    logger.info("Running full classifier initialization...")
    classifier = get_dpl_classifier()

    logger.info("Pre-warming reference deck cache...")
    for archetype in classifier.archetypes:
        for reference_deck in archetype.reference_decks:
            if reference_deck not in classifier._decks_cache:
                logger.info(f"Fetching reference deck: {reference_deck}")
                classifier._decks_cache[reference_deck] = (
                    classifier.pauperformance.get_playable_deck(reference_deck)
                )

    logger.info("Extracting artifact land names...")
    artifact_lands = classifier.pauperformance.scryfall.get_legal_artifact_lands()
    artifact_land_names = [c["name"] for c in artifact_lands]

    snapshot = {
        "archetypes": classifier.archetypes,
        "known_decks": classifier.known_decks,
        "decks_cache": classifier._decks_cache,
        "artifact_land_names": artifact_land_names,
    }

    logger.info(f"Serializing snapshot to {output_path}...")
    with open(output_path, "wb") as f:
        pickle.dump(snapshot, f)

    logger.info(
        f"Snapshot built: {len(classifier.archetypes)} archetypes, "
        f"{len(classifier.known_decks)} known decks, "
        f"{len(classifier._decks_cache)} cached reference decks, "
        f"{len(artifact_land_names)} artifact land names."
    )
    return output_path


if __name__ == "__main__":
    build_snapshot()
```

**Step 2: Verify SILVER_DIR exists in constants**

Check: `pauperformance_bot/constant/pauperformance/myr.py` should have `SILVER_DIR` or a path we can derive. If not, use `posix_path(RESOURCES_DIR, "silver")` based on what's available. Adjust the import accordingly.

**Step 3: Commit**

```bash
git add pauperformance_bot/task/build_snapshot.py
git commit -m "feat: add build_snapshot script to pre-serialize classifier state"
```

---

### Task 5: Add `from_snapshot` classmethod that loads from file

**Files:**
- Modify: `pauperformance_bot/service/pauperformance/silver/decklassifier.py`
- Test: `tests/test_decklassifier.py`

**Step 1: Write the failing test**

Add to `tests/test_decklassifier.py`:

```python
import os
import pickle
import tempfile


def test_from_snapshot_loads_from_file():
    """Decklassifier.from_snapshot should load classifier state from a pickle file."""
    burn_archetype = _make_archetype("Burn")
    known_burn = _make_deck({
        "Lightning Bolt": 4,
        "Lava Spike": 4,
        "Rift Bolt": 4,
        "Chain Lightning": 4,
        "Fireblast": 2,
        "Searing Blaze": 4,
        "Ghitu Lavarunner": 4,
        "Thermo-Alchemist": 4,
        "Mountain": 18,
        "Needle Drop": 4,
        "Skewer the Critics": 4,
        "Shard Volley": 4,
    })

    snapshot = {
        "archetypes": [burn_archetype],
        "known_decks": [(known_burn, burn_archetype)],
        "decks_cache": {},
        "artifact_land_names": ["Ancient Den", "Great Furnace"],
    }

    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        pickle.dump(snapshot, f)
        snapshot_path = f.name

    try:
        classifier = Decklassifier.from_snapshot(snapshot_path)
        assert len(classifier.archetypes) == 1
        assert classifier.archetypes[0].name == "Burn"
        assert len(classifier.known_decks) == 1
        assert classifier._artifact_land_names == ["Ancient Den", "Great Furnace"]
        assert classifier.pauperformance is None
    finally:
        os.unlink(snapshot_path)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_decklassifier.py::test_from_snapshot_loads_from_file -v`
Expected: FAIL with `AttributeError: type object 'Decklassifier' has no attribute 'from_snapshot'`

**Step 3: Implement from_snapshot**

Add to `Decklassifier` class in `decklassifier.py`:

```python
    @classmethod
    def from_snapshot(cls, snapshot_path):
        import pickle

        logger.info(f"Loading classifier snapshot from {snapshot_path}...")
        with open(snapshot_path, "rb") as f:
            snapshot = pickle.load(f)
        logger.info(
            f"Loaded snapshot: {len(snapshot['archetypes'])} archetypes, "
            f"{len(snapshot['known_decks'])} known decks, "
            f"{len(snapshot['decks_cache'])} cached reference decks."
        )
        return cls.from_snapshot_data(**snapshot)
```

**Step 4: Run all decklassifier tests**

Run: `pytest tests/test_decklassifier.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add pauperformance_bot/service/pauperformance/silver/decklassifier.py tests/test_decklassifier.py
git commit -m "feat: add from_snapshot classmethod to load classifier from pickle file"
```

---

### Task 6: Update silver.py to load from snapshot

**Files:**
- Modify: `pauperformance_bot/task/silver.py`

**Step 1: Implement the change**

Update `silver.py` to try loading from snapshot first, falling back to the current behavior:

```python
import json
import os

import jsonpickle

from pauperformance_bot.constant.pauperformance.myr import TOP_PATH
from pauperformance_bot.service.pauperformance.silver.decklassifier import Decklassifier
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import (
    posix_path,
    safe_dump_json_to_file,
)

logger = get_application_logger()

# Path to pre-built snapshot (see build_snapshot.py)
SNAPSHOT_PATH = posix_path(TOP_PATH, "resources", "silver", "classifier_snapshot.pkl")


def get_dpl_classifier():
    from pauperformance_bot.service.academy.data_exporter import AcademyDataExporter
    from pauperformance_bot.service.pauperformance.archive.mtggoldfish import (
        MTGGoldfishArchiveService,
    )
    from pauperformance_bot.service.pauperformance.pauperformance import (
        PauperformanceService,
    )
    from pauperformance_bot.service.pauperformance.storage.dropbox_ import DropboxService

    storage = DropboxService()
    archive = MTGGoldfishArchiveService(storage)
    pauperformance = PauperformanceService(storage, archive)

    exporter = AcademyDataExporter(pauperformance)
    known_decks, _ = exporter._load_mtggoldfish_tournament_training_data()
    other_known_decks, _ = exporter._load_dpl_training_data()
    known_decks += other_known_decks
    return Decklassifier(pauperformance, known_decks)


def load_dpl_classifier():
    if os.path.exists(SNAPSHOT_PATH):
        logger.info(f"Loading classifier from snapshot: {SNAPSHOT_PATH}")
        return Decklassifier.from_snapshot(SNAPSHOT_PATH)
    logger.warning(
        f"Snapshot not found at {SNAPSHOT_PATH}. "
        f"Falling back to full initialization (this will be slow)."
    )
    return get_dpl_classifier()


DPL_SILVER = load_dpl_classifier()


def generate_dpl_meta(data, name="DPL metagame"):
    return DPL_SILVER.get_dpl_metagame(data, name=name)


def main(input_file, output_file):
    logger.info(f"Getting DPL decks from {input_file}...")
    data = json.load(open(input_file))
    dpl_meta = generate_dpl_meta(data, name=input_file)
    try:
        out_dir, out_file = output_file.rsplit(os.path.sep, maxsplit=1)
    except ValueError:
        out_dir = os.getcwd()
        out_file = output_file
    safe_dump_json_to_file(out_dir, out_file, dpl_meta)
    logger.info(f"Stored DPL meta in {output_file}...")


def dpl_classifier(environ, start_response):
    try:
        method = environ["REQUEST_METHOD"]
        if method != "POST":
            start_response(
                "405 Method Not Allowed", [("Content-Type", "application/json")]
            )
            return [json.dumps({"error": "Method not allowed"}).encode("utf-8")]
        try:
            request_length = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            request_length = 0
        request_body = environ["wsgi.input"].read(request_length)
        data = json.loads(request_body.decode("utf-8"))
        response = generate_dpl_meta(data)
        response = json.loads(jsonpickle.encode(response, make_refs=False, warn=True))
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(response).encode("utf-8")]
    except Exception as e:
        start_response(
            "500 Internal Server Error", [("Content-Type", "application/json")]
        )
        return [json.dumps({"error": str(e)}).encode("utf-8")]


if __name__ == "__main__":
    main(
        posix_path(TOP_PATH, "dev", "decks-all-tournaments.json"),
        posix_path(TOP_PATH, "dev", "decks-all-tournaments-classified.json"),
    )
```

Key changes:
- Moved heavy imports inside `get_dpl_classifier()` so they're only loaded on fallback
- Added `load_dpl_classifier()` that tries snapshot first
- `DPL_SILVER = load_dpl_classifier()` replaces `DPL_SILVER = get_dpl_classifier()`

**Step 2: Run existing tests**

Run: `pytest tests/ -v`
Expected: All existing tests still PASS (silver.py is not imported by other tests)

**Step 3: Commit**

```bash
git add pauperformance_bot/task/silver.py
git commit -m "feat: load classifier from snapshot with fallback to full initialization"
```

---

### Task 7: Add Makefile target for building snapshot

**Files:**
- Modify: `Makefile`

**Step 1: Add the target**

Add to `Makefile`:

```makefile
build-snapshot:
	python -m pauperformance_bot.task.build_snapshot
```

**Step 2: Commit**

```bash
git add Makefile
git commit -m "feat: add make build-snapshot target"
```

---

### Task 8: Final verification — run full test suite

**Step 1: Run the full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS

**Step 2: Run linting**

Run: `black --check pauperformance_bot/service/pauperformance/silver/decklassifier.py pauperformance_bot/task/silver.py pauperformance_bot/task/build_snapshot.py tests/test_decklassifier.py`
Run: `isort --check pauperformance_bot/service/pauperformance/silver/decklassifier.py pauperformance_bot/task/silver.py pauperformance_bot/task/build_snapshot.py tests/test_decklassifier.py`

Fix any formatting issues and commit.
