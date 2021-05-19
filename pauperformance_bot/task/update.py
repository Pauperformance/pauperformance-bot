from pauperformance_bot.client.pauperformance import Pauperformance


def update():
    pauperformance = Pauperformance()
    pauperformance.render_set_index()


if __name__ == '__main__':
    update()
