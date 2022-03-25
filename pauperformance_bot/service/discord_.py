import discord

from pauperformance_bot.credentials import DISCORD_CHANNEL_IMPORT_DECK_ID


class DiscordService(discord.Client):

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    def import_decks_from_channel(self, channel_id):
        channel = self.get_channel(channel_id)
        messages = await channel.history(limit=200).flatten()
        for m in messages:
            # print(m)
            print(f"{m.author.name} ({m.author.id}): {m.content}")
            emoji = '\N{THUMBS UP SIGN}'

            # await m.add_reaction('✅')
            # await m.remove_reaction(emoji, self.user)

            if m.author.name == 'MEE6' and m.content.startswith('Hey <@'):
                new_user_id = int(m.content[
                              m.content.index('@') + 1:
                              m.content.index('>')
                              ])
                print(f"New user: {new_user_id}")
                user = self.get_user(new_user_id)
                if user:
                    print(f"FOUND USER: {user.display_name} ({new_user_id})")

    def foo(self):
        DISCORD_CHANNEL_IMPORT_DECK_ID


def discord_test():
    client = discord.Client()
    client.run()


def main
main()

            # await m.author.send("Padrone, mi ricevi?")

    # async def on_message(self, message):
    #     print('Message from {0.author}: {0.content}'.format(message))