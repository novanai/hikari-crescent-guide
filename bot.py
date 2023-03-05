import os
import model
import crescent
import dotenv
import hikari
import miru
from hikari import Intents

dotenv.load_dotenv()

INTENTS = Intents.GUILD_MEMBERS | Intents.GUILDS


bot = hikari.GatewayBot(
    os.environ["BOT_TOKEN"],
    intents=INTENTS,
    banner=None,
)
miru.install(bot)

client_model = model.Model()
client = crescent.Client(bot, client_model)
client.plugins.load_folder("plugins")

bot.subscribe(hikari.StartingEvent, client_model.on_starting)
bot.subscribe(hikari.StoppingEvent, client_model.on_stopping)


@client.include
@crescent.command(name="ping", description="The bot's ping.")
async def ping_cmd(ctx: crescent.Context) -> None:
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency * 1000:.2f}ms.")


@client.include
@crescent.command(name="announce", description="Make an announcement!")
class Announce:
    message = crescent.option(str, "The message to announce.")
    channel = crescent.option(
        hikari.TextableChannel, "Channel to post announcement to."
    )
    image = crescent.option(hikari.Attachment, "Announcement attachment.", default=None)
    ping = crescent.option(hikari.Role, "Role to ping with announcement.", default=None)

    async def callback(self, ctx: crescent.Context) -> None:
        embed = hikari.Embed(
            title="Announcement!",
            description=self.message,
        )
        embed.set_image(self.image)

        await ctx.app.rest.create_message(
            channel=self.channel.id,
            content=self.ping.mention if self.ping else hikari.UNDEFINED,
            embed=embed,
            role_mentions=True,
        )

        await ctx.respond(
            f"Announcement posted to <#{self.channel.id}>!", ephemeral=True
        )


if __name__ == "__main__":
    bot.run()
