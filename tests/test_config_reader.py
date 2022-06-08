from pauperformance_bot.service.pauperformance.config_reader import ConfigReader


def test_list_phd_sheets():
    assert len(ConfigReader().list_phd_sheets()) >= 3


def test_list_phds():
    assert len(ConfigReader().list_phds()) >= 3
