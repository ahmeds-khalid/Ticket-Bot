import nextcord
from nextcord.ext import commands
import asyncio

class EmbedBuilderView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Title Text", style=nextcord.ButtonStyle.secondary)
    async def title_text(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(TitleModal())

    @nextcord.ui.button(label="Description Text", style=nextcord.ButtonStyle.secondary)
    async def description_text(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(DescriptionModal())

    @nextcord.ui.button(label="Footer Text", style=nextcord.ButtonStyle.secondary)
    async def footer_text(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(FooterModal())

    @nextcord.ui.button(label="Thumbnail Image", style=nextcord.ButtonStyle.secondary)
    async def thumbnail_image(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(ThumbnailImageModal())

    @nextcord.ui.button(label="Big Image", style=nextcord.ButtonStyle.secondary)
    async def big_image(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(BigImageModal())

    @nextcord.ui.button(label="Embed Color", style=nextcord.ButtonStyle.secondary)
    async def embed_color(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("Choose a color using the dropdown below.", ephemeral=True, view=ColorDropdownView())

    @nextcord.ui.button(label="Add Field", style=nextcord.ButtonStyle.secondary)
    async def add_field(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(FieldModal())

    @nextcord.ui.button(label="Set Author", style=nextcord.ButtonStyle.secondary)
    async def set_author(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        # Automatically set author using the interaction user
        EmbedBuilder.author_name = interaction.user.name
        EmbedBuilder.author_image = interaction.user.avatar.url if interaction.user.avatar else None
        await interaction.response.send_message(f"Author set as {EmbedBuilder.author_name}.", ephemeral=True)

    @nextcord.ui.button(label="Add Timestamp", style=nextcord.ButtonStyle.secondary)
    async def add_timestamp(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        EmbedBuilder.add_timestamp = True
        await interaction.response.send_message("Timestamp will be added to the embed.", ephemeral=True)

    @nextcord.ui.button(label="Send Embed", style=nextcord.ButtonStyle.success)
    async def post_embed(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = EmbedBuilder.build_embed()
        delete_view = DeleteEmbedView()
        await interaction.channel.send(embed=embed, view=delete_view)
        await interaction.response.send_message("Embed sent!", ephemeral=True)


class DeleteEmbedView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Delete Embed", style=nextcord.ButtonStyle.danger)
    async def delete_embed(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.message.delete()
        await interaction.response.send_message("Embed deleted!", ephemeral=True)


class ColorDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="Red", value="#FF0000", description="Bright red color", emoji="🔴"),
            nextcord.SelectOption(label="Green", value="#00FF00", description="Bright green color", emoji="🟢"),
            nextcord.SelectOption(label="Blue", value="#0000FF", description="Bright blue color", emoji="🔵"),
            nextcord.SelectOption(label="Yellow", value="#FFFF00", description="Bright yellow color", emoji="🟡"),
            nextcord.SelectOption(label="Purple", value="#800080", description="Purple color", emoji="🟣"),
            nextcord.SelectOption(label="Orange", value="#FFA500", description="Orange color", emoji="🟠"),
            nextcord.SelectOption(label="Pink", value="#FFC0CB", description="Light pink color", emoji="🌸"),
            nextcord.SelectOption(label="Black", value="#000000", description="Black color", emoji="⚫"),
            nextcord.SelectOption(label="White", value="#FFFFFF", description="White color", emoji="⚪"),
            nextcord.SelectOption(label="Cyan", value="#00FFFF", description="Cyan color", emoji="🟦")
        ]
        super().__init__(placeholder="Choose a color", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        color_value = self.values[0]
        try:
            EmbedBuilder.color = nextcord.Color(int(color_value.lstrip('#'), 16))
            await interaction.response.send_message(f"Color set to {color_value}!", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Invalid color selected. Please try again.", ephemeral=True)


class ColorDropdownView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ColorDropdown())


class TitleModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Set Embed Title")
        self.title_input = nextcord.ui.TextInput(label="Title", placeholder="Enter the title for your embed")
        self.add_item(self.title_input)

    async def callback(self, interaction: nextcord.Interaction):
        EmbedBuilder.title = self.title_input.value
        await interaction.response.send_message("Title set!", ephemeral=True)


class DescriptionModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Set Embed Description")
        self.desc_input = nextcord.ui.TextInput(label="Description", style=nextcord.TextInputStyle.paragraph, placeholder="Enter the description for your embed")
        self.add_item(self.desc_input)

    async def callback(self, interaction: nextcord.Interaction):
        EmbedBuilder.description = self.desc_input.value
        await interaction.response.send_message("Description set!", ephemeral=True)


class FooterModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Set Embed Footer")
        self.footer_input = nextcord.ui.TextInput(label="Footer", placeholder="Enter the footer text for your embed")
        self.add_item(self.footer_input)

    async def callback(self, interaction: nextcord.Interaction):
        EmbedBuilder.footer = self.footer_input.value
        await interaction.response.send_message("Footer set!", ephemeral=True)


class FieldModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Add a Field")
        self.field_name = nextcord.ui.TextInput(label="Field Name", placeholder="Enter the name of the field")
        self.field_value = nextcord.ui.TextInput(label="Field Value", style=nextcord.TextInputStyle.paragraph, placeholder="Enter the value of the field")
        self.add_item(self.field_name)
        self.add_item(self.field_value)

    async def callback(self, interaction: nextcord.Interaction):
        EmbedBuilder.fields.append((self.field_name.value, self.field_value.value))
        await interaction.response.send_message(f"Field '{self.field_name.value}' added!", ephemeral=True)


class ThumbnailImageModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Set Thumbnail Image URL")
        self.thumbnail_image_input = nextcord.ui.TextInput(label="Thumbnail Image URL", placeholder="Enter the URL for the thumbnail image")
        self.add_item(self.thumbnail_image_input)

    async def callback(self, interaction: nextcord.Interaction):
        EmbedBuilder.thumbnail_image = self.thumbnail_image_input.value
        await interaction.response.send_message("Thumbnail image set!", ephemeral=True)


class BigImageModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Set Big Image URL")
        self.big_image_input = nextcord.ui.TextInput(label="Big Image URL", placeholder="Enter the URL for the big image")
        self.add_item(self.big_image_input)

    async def callback(self, interaction: nextcord.Interaction):
        EmbedBuilder.big_image = self.big_image_input.value
        await interaction.response.send_message("Big image set!", ephemeral=True)


class EmbedBuilder:
    title = "Ticket Embed"
    description = "Welcome to the ticket system!"
    footer = None
    thumbnail_image = None
    big_image = None
    author_name = None
    author_image = None
    color = nextcord.Color.blue()
    add_timestamp = False
    fields = []

    @classmethod
    def build_embed(cls):
        embed = nextcord.Embed(title=cls.title, description=cls.description, color=cls.color)
        if cls.footer:
            embed.set_footer(text=cls.footer)
        if cls.thumbnail_image:
            embed.set_thumbnail(url=cls.thumbnail_image)
        if cls.big_image:
            embed.set_image(url=cls.big_image)
        if cls.author_name:
            embed.set_author(name=cls.author_name, icon_url=cls.author_image if cls.author_image else None)
        if cls.add_timestamp:
            embed.timestamp = nextcord.utils.utcnow()
        for field_name, field_value in cls.fields:
            embed.add_field(name=field_name, value=field_value, inline=False)
        return embed


class EmbedBuilderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="embedbuilder", description="Start the embed builder")
    async def embed_builder(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Embed Builder", description="Welcome to the interactive embed builder! Use the buttons below to customize your embed, and click 'Send Embed' when you're finished!", color=nextcord.Color.blue())
        view = EmbedBuilderView()
        await interaction.response.send_message(embed=embed, view=view)


def setup(bot):
    bot.add_cog(EmbedBuilderCog(bot))
