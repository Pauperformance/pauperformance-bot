from pauperformance_bot.entity.api.phd_sheet import PhDSheet


def test_phd_sheet():
    phd_sheet = PhDSheet("TEST")
    print(phd_sheet)
    print(phd_sheet.__dict__)
    phd_sheet.dump_to_file()
