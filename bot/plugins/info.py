from datetime import datetime

import crescent
import hikari

from bot import model

plugin = crescent.Plugin[hikari.GatewayBot, model.Model]()


@plugin.include
@crescent.command(
    name="userinfo", description="Get info on a server member.", dm_enabled=False
)
class UserInfo:
    user = crescent.option(
        hikari.User, "The user to get information about.", default=None
    )

    async def callback(self, ctx: crescent.Context) -> None:
        assert ctx.guild_id is not None

        user = self.user or ctx.user
        user = plugin.app.cache.get_member(ctx.guild_id, user)

        if not user:
            await ctx.respond("That user is not in this server.")
            return

        created_at = int(user.created_at.timestamp())
        joined_at = int(user.joined_at.timestamp())

        roles = [f"<@&{role}>" for role in user.role_ids if role != ctx.guild_id]

        embed = (
            hikari.Embed(
                title=f"User Info - {user.display_name}",
                description=f"ID: `{user.id}`",
                colour=0x3B9DFF,
                timestamp=datetime.now().astimezone(),
            )
            .set_footer(
                text=f"Requested by {ctx.user}",
                icon=ctx.user.display_avatar_url,
            )
            .set_thumbnail(user.avatar_url)
            .add_field(
                "Bot?",
                "Yes" if user.is_bot else "No",
                inline=True,
            )
            .add_field(
                "Created account on",
                f"<t:{created_at}:d>\n(<t:{created_at}:R>)",
                inline=True,
            )
            .add_field(
                "Joined server on",
                f"<t:{joined_at}:d>\n(<t:{joined_at}:R>)",
                inline=True,
            )
            .add_field(
                "Roles",
                ", ".join(roles) if roles else "No roles",
                inline=False,
            )
        )

        await ctx.respond(embed)
