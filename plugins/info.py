from datetime import datetime
from typing import Annotated as Atd
from typing import Optional

import crescent
import hikari

plugin = crescent.Plugin()


@plugin.include
@crescent.command(name="userinfo", description="Get info on a server member.", dm_enabled=False)
class UserInfo:
    user = crescent.option(hikari.User, "The user to get information about.", default=None)

    async def callback(
        self,
        ctx: crescent.Context,
    ) -> None:
        user = self.user or ctx.user
        user = ctx.app.cache.get_member(ctx.guild, user)

        if not user:
            await ctx.respond("That user is not in the server.")
            return

        created_at = int(user.created_at.timestamp())
        joined_at = int(user.joined_at.timestamp())

        roles = (await user.fetch_roles())[1:]  # All but @everyone
        roles = sorted(
            roles, key=lambda role: role.position, reverse=True
        )  # sort them by position, then reverse the order to go from top role down

        embed = (
            hikari.Embed(
                title=f"User Info - {user.display_name}",
                description=f"ID: `{user.id}`",
                colour=0x3B9DFF,
                timestamp=datetime.now().astimezone(),
            )
            .set_footer(
                text=f"Requested by {ctx.user.username}",
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
                ", ".join(r.mention for r in roles),
                inline=False,
            )
        )

        await ctx.respond(embed)
