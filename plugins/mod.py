import asyncio
from typing import Annotated as Atd, Optional

import crescent
import hikari
import toolbox
from crescent.ext import cooldowns

plugin = crescent.Plugin()


async def on_cooldown(ctx: crescent.Context, time_remaining: float) -> None:
    await ctx.respond(
        f"This command is on cooldown! You can use it again in {int(time_remaining)} seconds."
    )


async def check_permissions(ctx: crescent.Context) -> Optional[crescent.HookResult]:
    if not (
        toolbox.calculate_permissions(ctx.member, ctx.channel)
        & hikari.Permissions.MANAGE_MESSAGES
    ):
        await ctx.respond("You do not have permission to use this command.")
        return crescent.HookResult(exit=True)


@plugin.include
@crescent.hook(
    cooldowns.cooldown(1, 5, callback=on_cooldown)
)  # 1 use every 5 seconds per user
@crescent.hook(check_permissions)
@crescent.command(name="purge", description="Purge messages.", dm_enabled=False)
class Purge:
    messages = crescent.option(int, "The number of messages to purge.")
    
    async def callback(
        self,
        ctx: crescent.Context
    ) -> None:
        channel = ctx.channel_id

        msgs = await ctx.app.rest.fetch_messages(channel).limit(self.messages)
        await ctx.app.rest.delete_messages(channel, msgs)

        msg = await ctx.respond(f"{len(msgs)} messages deleted.", ensure_message=True)
        await asyncio.sleep(5)
        await msg.delete()


@plugin.include
@crescent.catch_command(hikari.BulkDeleteError)
async def on_cmd_error(exc: hikari.BulkDeleteError, ctx: crescent.Context) -> None:
    exception = exc.__cause__

    if isinstance(exception, hikari.ForbiddenError):
        await ctx.respond("I do not have permission to delete messages.")
        return

    raise exc
