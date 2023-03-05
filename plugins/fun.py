import asyncio

import crescent
import hikari
import miru

import model

plugin = crescent.Plugin[hikari.GatewayBot, model.Model]()


fun_group = crescent.Group(
    name="fun",
    description="All the entertainment commands you'll ever need!",
)


@plugin.include
@fun_group.child
@crescent.command(name="meme", description="Get a meme!")
async def meme_subcommand(ctx: crescent.Context) -> None:
    async with plugin.model.client_session.get("https://meme-api.com/gimme") as res:
        if not res.ok:
            await ctx.respond(
                f"API returned a {res.status} status :c",
                ephemeral=True,
            )
            return

        data = await res.json()

        if data["nsfw"]:
            await ctx.respond(
                "Response was NSFW, couldn't send :c",
                ephemeral=True,
            )
            return

        embed = hikari.Embed(colour=0x3B9DFF)
        embed.set_author(name=data["title"], url=data["postLink"])
        embed.set_image(data["url"])

        await ctx.respond(embed)


ANIMALS = {
    "Bird": "🐦",
    "Cat": "🐱",
    "Dog": "🐶",
    "Fox": "🦊",
    "Kangaroo": "🦘",
    "Koala": "🐨",
    "Panda": "🐼",
    "Raccoon": "🦝",
    "Red Panda": "🐼",
}


@plugin.include
@fun_group.child
@crescent.command(name="animal", description="Get a fact & picture of a cute animal :3")
async def animal_subcommand(ctx: crescent.Context) -> None:
    select_menu = (
        plugin.app.rest.build_message_action_row()
        .add_select_menu(hikari.ComponentType.TEXT_SELECT_MENU, "animal_select")
        .set_placeholder("Pick an animal")
    )

    for name, emoji in ANIMALS.items():
        select_menu.add_option(
            name,  # the label, which users see
            name.lower().replace(" ", "_"),  # the value, which is used by us later
        ).set_emoji(emoji).add_to_menu()

    msg = await ctx.respond(
        "Pick an animal from the dropdown :3",
        component=select_menu.add_to_container(),
        ensure_message=True,
    )

    try:
        event = await plugin.app.wait_for(
            hikari.InteractionCreateEvent,
            timeout=60,
            predicate=lambda e: isinstance(e.interaction, hikari.ComponentInteraction)
            and e.interaction.user.id == ctx.user.id
            and e.interaction.message.id == msg.id
            and e.interaction.component_type == hikari.ComponentType.TEXT_SELECT_MENU,
        )
    except asyncio.TimeoutError:
        await ctx.edit("The menu timed out :c", components=[])
    else:
        animal = event.interaction.values[0]
        async with plugin.model.client_session.get(
            f"https://some-random-api.ml/animal/{animal}"
        ) as res:
            if not res.ok:
                await ctx.edit(f"API returned a {res.status} status :c", components=[])
                return

            data = await res.json()
            embed = hikari.Embed(description=data["fact"], colour=0x3B9DFF)
            embed.set_image(data["image"])

            animal = animal.replace("_", " ")

            await ctx.edit(f"Here's a {animal} for you! :3", embed=embed, components=[])


class AnimalView(miru.View):
    def __init__(self, author: hikari.User) -> None:
        self.author = author
        super().__init__(timeout=60)

    @miru.text_select(
        custom_id="animal_select",
        placeholder="Pick an animal",
        options=[
            miru.SelectOption(name, name.lower().replace(" ", "_"), emoji=emoji)
            for name, emoji in ANIMALS.items()
        ],
    )
    async def select_menu(self, select: miru.TextSelect, ctx: miru.ViewContext) -> None:
        animal = select.values[0]
        async with plugin.model.client_session.get(
            f"https://some-random-api.ml/animal/{animal}"
        ) as res:
            if not res.ok:
                await ctx.edit_response(
                    f"API returned a {res.status} status :c", components=[]
                )
                return

            data = await res.json()
            embed = hikari.Embed(description=data["fact"], colour=0x3B9DFF)
            embed.set_image(data["image"])

            animal = animal.replace("_", " ")

            await ctx.edit_response(
                f"Here's a {animal} for you! :3", embed=embed, components=[]
            )

    async def on_timeout(self) -> None:
        assert self.message is not None
        await self.message.edit("The menu timed out :c", components=[])

    async def view_check(self, ctx: miru.ViewContext) -> bool:
        return ctx.user.id == self.author.id


@plugin.include
@fun_group.child
@crescent.command(
    name="animal2", description="Get a fact + picture of a cute animal :3"
)
async def animal_subcommand_2(ctx: crescent.Context) -> None:
    view = AnimalView(ctx.user)
    msg = await ctx.respond(
        "Pick an animal from the dropdown :3",
        components=view.build(),
        ensure_message=True,
    )

    await view.start(msg)
    await view.wait()
