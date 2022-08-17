from typing import Annotated as Atd

import crescent
import hikari
from crescent.ext import cooldowns

plugin = crescent.Plugin()


async def on_cooldown(ctx: crescent.Context, time_remaining: float) -> None:
    await ctx.respond(
        f"This command is on cooldown! You can use it again in {int(time_remaining)} seconds."
    )


@plugin.include
@crescent.hook(
    cooldowns.cooldown(1, 5, callback=on_cooldown)
)  # 1 use every 5 seconds per user
@crescent.command(name="purge", description="Purge messages.")
async def purge_messages(
    ctx: crescent.Context, messages: Atd[int, "The number of messages to purge."]
) -> None:
    channel = ctx.channel_id

    msgs = await ctx.app.rest.fetch_messages(channel).limit(messages)
    await ctx.app.rest.delete_messages(channel, msgs)

    await ctx.respond(f"{len(msgs)} messages deleted.")


@plugin.include
@crescent.catch_command(hikari.BulkDeleteError)
async def on_cmd_error(exc: hikari.BulkDeleteError, ctx: crescent.Context) -> None:
    cause = exc.__cause__
    if isinstance(cause, hikari.ForbiddenError):
        await ctx.respond(
            "I do not have permission to delete messages.", ephemeral=True
        )
        return

    raise exc
