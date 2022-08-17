import asyncio

import crescent
import hikari
import miru

plugin = crescent.Plugin()


fun_group = crescent.Group(
    name="fun",
    description="All the entertainment commands you'll ever need.",
)


@plugin.include
@fun_group.child
@crescent.command(name="meme", description="Get a meme!")
async def meme_subcommand(ctx: crescent.Context) -> None:
    async with ctx.app.aio_session.get(
        "https://meme-api.herokuapp.com/gimme"
    ) as response:
        res = await response.json()
        if response.ok and res["nsfw"] != True:
            link = res["postLink"]
            title = res["title"]
            img_url = res["url"]

            embed = hikari.Embed(colour=0x3B9DFF)
            embed.set_author(name=title, url=link)
            embed.set_image(img_url)

            await ctx.respond(embed)

        else:
            await ctx.respond("Could not fetch a meme :c", ephemeral=True)


ANIMALS = {
    "Dog": "🐶",
    "Cat": "🐱",
    "Panda": "🐼",
    "Fox": "🦊",
    "Red Panda": "🐼",
    "Koala": "🐨",
    "Bird": "🐦",
    "Racoon": "🦝",
    "Kangaroo": "🦘",
}


@plugin.include
@fun_group.child
@crescent.command(name="animal", description="Get a fact + picture of a cute animal :3")
async def animal_subcommand(ctx: crescent.Context) -> None:
    select_menu = (
        ctx.app.rest.build_action_row()
        .add_select_menu("animal_select")
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
        event = await ctx.app.wait_for(
            hikari.InteractionCreateEvent,
            timeout=60,
            predicate=lambda e: isinstance(e.interaction, hikari.ComponentInteraction)
            and e.interaction.user.id == ctx.user.id
            and e.interaction.message.id == msg.id
            and e.interaction.component_type == hikari.ComponentType.SELECT_MENU,
        )
    except asyncio.TimeoutError:
        await msg.edit("The menu timed out :c", components=[])
    else:
        animal = event.interaction.values[0]
        async with ctx.app.aio_session.get(
            f"https://some-random-api.ml/animal/{animal}"
        ) as res:
            if res.ok:
                res = await res.json()
                embed = hikari.Embed(description=res["fact"], colour=0x3B9DFF)
                embed.set_image(res["image"])

                animal = animal.replace("_", " ")

                await msg.edit(
                    f"Here's a {animal} for you! :3", embed=embed, components=[]
                )
            else:
                await msg.edit(f"API returned a {res.status} status :c", components=[])


class AnimalView(miru.View):
    def __init__(self, author: hikari.User) -> None:
        self.author = author
        super().__init__(timeout=60)

    @miru.select(
        custom_id="animal_select",
        placeholder="Pick an animal",
        options=[
            miru.SelectOption("Dog", "dog", emoji="🐶"),
            miru.SelectOption("Cat", "cat", emoji="🐱"),
            miru.SelectOption("Panda", "panda", emoji="🐼"),
            miru.SelectOption("Fox", "fox", emoji="🦊"),
            miru.SelectOption("Red Panda", "red_panda", emoji="🐼"),
            miru.SelectOption("Koala", "koala", emoji="🐨"),
            miru.SelectOption("Bird", "bird", emoji="🐦"),
            miru.SelectOption("Racoon", "racoon", emoji="🦝"),
            miru.SelectOption("Kangaroo", "kangaroo", emoji="🦘"),
        ],
    )
    async def select_menu(self, select: miru.Select, ctx: miru.Context) -> None:
        animal = select.values[0]
        async with ctx.app.aio_session.get(
            f"https://some-random-api.ml/animal/{animal}"
        ) as res:
            if res.ok:
                res = await res.json()
                embed = hikari.Embed(description=res["fact"], colour=0x3B9DFF)
                embed.set_image(res["image"])

                animal = animal.replace("_", " ")

                await ctx.edit_response(
                    f"Here's a {animal} for you! :3", embed=embed, components=[]
                )
            else:
                await ctx.edit_response(
                    f"API returned a {res.status} status :c", components=[]
                )

    async def on_timeout(self) -> None:
        await self.message.edit("The menu timed out :c", components=[])

    async def view_check(self, ctx: miru.Context) -> bool:
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

    view.start(msg)
    await view.wait()
