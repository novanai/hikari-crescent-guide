import asyncio
import os
from typing import Annotated as Atd

import aiohttp
import crescent
import dotenv
import hikari
import miru

dotenv.load_dotenv()


class Bot(crescent.Bot):
    def __init__(self):
        self.aio_session: aiohttp.ClientSession

        super().__init__(
            os.environ["BOT_TOKEN"],
            intents=hikari.Intents.ALL,
            banner=None,
        )


bot = Bot()
miru.load(bot)
bot.plugins.load_folder("plugins")


@bot.include
@crescent.event
async def on_starting(event: hikari.StartingEvent) -> None:
    bot.aio_session = aiohttp.ClientSession()


@bot.include
@crescent.event
async def on_stopping(event: hikari.StoppingEvent) -> None:
    await bot.aio_session.close()


@bot.include
@crescent.command(name="ping", description="The bot's ping.")
async def ping(ctx: crescent.Context) -> None:
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms.")


@bot.include
@crescent.command(name="announce", description="Make an announcement!")
async def announce(
    ctx: crescent.Context,
    message: Atd[str, "The message to announce."],
    image: Atd[hikari.Attachment, "Announcement attachment."],
    channel: Atd[hikari.TextableChannel, "Channel to post announcement to."],
    ping: Atd[hikari.Role, "Role to ping with announcement."],
) -> None:
    embed = hikari.Embed(
        title="Announcement!",
        description=message,
    )
    embed.set_image(image)

    await ctx.app.rest.create_message(
        content=ping.mention,
        channel=channel.id,
        embed=embed,
        role_mentions=True,
    )

    await ctx.respond(f"Announcement posted to <#{channel.id}>!", ephemeral=True)


@bot.include
@crescent.command(name="announce2", description="Make an announcement!")
class Announce:
    message = crescent.option(str, "The message to announce.")
    image = crescent.option(hikari.Attachment, "Announcement attachment.")
    channel = crescent.option(
        hikari.TextableChannel, "Channel to post announcement to."
    )
    ping = crescent.option(hikari.Role, "Role to ping with announcement.")

    async def callback(self, ctx: crescent.Context) -> None:
        embed = hikari.Embed(
            title="Announcement!",
            description=self.message,
        )
        embed.set_image(self.image)

        await ctx.app.rest.create_message(
            content=self.ping.mention,
            channel=self.channel.id,
            embed=embed,
            role_mentions=True,
        )

        await ctx.respond(
            f"Announcement posted to <#{self.channel.id}>!", ephemeral=True
        )


if __name__ == "__main__":
    if os.name == "nt":
        # we are running on a Windows machine, and we have to add this so
        # the code doesn't error :< (it most likely will error without this)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    bot.run()
