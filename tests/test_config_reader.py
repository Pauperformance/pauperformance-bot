import pytest

from pauperformance_bot.entity.api.miscellanea import Changelog, Newspauper
from pauperformance_bot.entity.config.archetype import ArchetypeConfig
from pauperformance_bot.exceptions import PauperformanceException
from pauperformance_bot.service.pauperformance.config_reader import ConfigReader


def test_list_creator_sheets():
    assert len(ConfigReader().list_creator_sheets()) >= 3


def test_list_creators():
    assert len(ConfigReader().list_creators()) >= 3


# --- ConfigReader._parse_list_value ---


def test_parse_list_value_empty_string():
    assert ConfigReader._parse_list_value("") == []


def test_parse_list_value_single():
    assert ConfigReader._parse_list_value("Burn") == ["Burn"]


def test_parse_list_value_multiple():
    result = ConfigReader._parse_list_value("Burn, Faeries, Affinity")
    assert result == ["Burn", "Faeries", "Affinity"]


def test_parse_list_value_strips_spaces():
    result = ConfigReader._parse_list_value("  Burn  ,  Faeries  ")
    assert result == ["Burn", "Faeries"]


# --- ConfigReader.list_archetypes and get_archetype ---


def test_list_archetypes_returns_archetype_configs():
    archetypes = ConfigReader().list_archetypes()
    assert len(archetypes) > 0
    assert all(isinstance(a, ArchetypeConfig) for a in archetypes)


def test_list_archetypes_all_have_names():
    for archetype in ConfigReader().list_archetypes():
        assert archetype.name


def test_list_archetypes_must_have_or_not_have_cards_are_lists():
    for archetype in ConfigReader().list_archetypes():
        assert isinstance(archetype.must_have_cards, list)
        assert isinstance(archetype.must_not_have_cards, list)


# --- ConfigReader.get_archetype_name_from_alias ---


def test_get_archetype_name_from_alias_by_exact_name():
    cr = ConfigReader()
    archetypes = cr.list_archetypes()
    first_name = archetypes[0].name
    assert cr.get_archetype_name_from_alias(first_name) == first_name


def test_get_archetype_name_from_alias_unknown_raises():
    with pytest.raises(PauperformanceException):
        ConfigReader().get_archetype_name_from_alias("__no_such_archetype__")


# --- ConfigReader.get_changelog and get_newspauper ---


def test_get_changelog_returns_changelog():
    result = ConfigReader().get_changelog()
    assert isinstance(result, Changelog)
    assert len(result.changes) > 0


def test_get_newspauper_returns_newspauper():
    result = ConfigReader().get_newspauper()
    assert isinstance(result, Newspauper)
