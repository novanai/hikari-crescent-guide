import asyncio

import crescent
import hikari
import datetime
from crescent.ext import cooldowns

import model

plugin = crescent.Plugin[hikari.GatewayBot, model.Model]()


async def on_cooldown(
    ctx: crescent.Context, time_remaining: datetime.timedelta
) -> None:
    await ctx.respond(
        f"This command is on cooldown! You can use it again in {int(time_remaining.total_seconds())} seconds."
    )


@plugin.include
@crescent.hook(
    cooldowns.cooldown(1, datetime.timedelta(seconds=5), callback=on_cooldown)
)  # 1 use every 5 seconds per user
@crescent.command(
    name="purge",
    description="Purge messages.",
    dm_enabled=False,
    default_member_permissions=hikari.Permissions.MANAGE_MESSAGES,
)
class Purge:
    messages = crescent.option(
        int, "The number of messages to purge.", min_value=2, max_value=200
    )
    sent_by = crescent.option(
        hikari.User, "Only purge messages sent by this user.", default=None
    )

    async def callback(self, ctx: crescent.Context) -> None:
        bulk_delete_limit = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(days=14)

        iterator = (
            plugin.app.rest.fetch_messages(ctx.channel_id)
            .take_while(lambda msg: msg.created_at > bulk_delete_limit)
            .filter(lambda msg: not (msg.flags & hikari.MessageFlag.LOADING))
        )
        if self.sent_by:
            iterator = iterator.filter(lambda msg: msg.author.id == self.sent_by.id)

        iterator = iterator.limit(self.messages)

        count = 0

        async for messages in iterator.chunk(100):
            count += len(messages)
            await plugin.app.rest.delete_messages(ctx.channel_id, messages)

        await ctx.respond(f"{count} messages deleted.")
        await asyncio.sleep(5)
        await ctx.delete()


@plugin.include
@crescent.catch_command(hikari.BulkDeleteError)
async def on_cmd_error(exc: hikari.BulkDeleteError, ctx: crescent.Context) -> None:
    exception = exc.__cause__

    if isinstance(exception, hikari.ForbiddenError):
        await ctx.respond("I do not have permission to delete messages.")
        return

    raise exc
