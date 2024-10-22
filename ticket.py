import nextcord
from nextcord.ext import commands
import asyncio
from embed_builder import EmbedBuilderView

class TicketBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_counter = 0

    @nextcord.slash_command(name="setup", description="Set up the ticket system")
    @commands.has_permissions(administrator=True)
    async def setup(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Support Ticket System", description="Click a button below to open a ticket:", color=nextcord.Color.blue())
        
        view = nextcord.ui.View()
        view.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.primary, label="Support Ticket", emoji="🎫", custom_id="support_ticket"))
        view.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.danger, label="Report a Bug", emoji="🐛", custom_id="bug_report"))
        view.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.secondary, label="Other", emoji="❓", custom_id="other_ticket"))

        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("Ticket system set up successfully!", ephemeral=True)

    @nextcord.slash_command(name="ticket", description="Create a new support ticket")
    async def create_ticket(self, interaction: nextcord.Interaction):
        await self._create_ticket(interaction, "Support")

    async def _create_ticket(self, interaction: nextcord.Interaction, ticket_type: str):
        guild = interaction.guild
        author = interaction.user

        channel_prefixes = {
            "Support": "support",
            "Bug Report": "bug",
            "Other": "inquiry"
        }
        prefix = channel_prefixes.get(ticket_type, "ticket")

        existing_ticket = nextcord.utils.get(guild.text_channels, name=f"{prefix}-{author.name.lower()}")
        if existing_ticket:
            await interaction.response.send_message("You already have an open ticket!", ephemeral=True)
            return

        self.ticket_counter += 1
        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            author: nextcord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: nextcord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        channel = await guild.create_text_channel(
            f"{prefix}-{author.name.lower()}",
            overwrites=overwrites,
            topic=f"{ticket_type} ticket for {author.name}"
        )

        ticket_emojis = {
            "Support": "🎫",
            "Bug Report": "🐛",
            "Other": "❓"
        }
        emoji = ticket_emojis.get(ticket_type, "🎫")

        await channel.send(f"{emoji} {author.mention} Welcome to your {ticket_type.lower()} ticket! Please describe your issue here.")
        
        # Send the embed builder message
        embed_builder_embed = nextcord.Embed(title="Ticket Embed Builder", description="Welcome to the interactive ticket embed builder.\nUse the buttons below to build the embed, when you're done click Post Embed!", color=nextcord.Color.blue())
        view = EmbedBuilderView()
        await channel.send(embed=embed_builder_embed, view=view)

        await interaction.response.send_message(f"Ticket created! Please check {channel.mention}", ephemeral=True)

    @nextcord.slash_command(name="close", description="Close the current support ticket")
    async def close_ticket(self, interaction: nextcord.Interaction):
        if not interaction.channel.name.startswith(("support-", "bug-", "inquiry-")):
            await interaction.response.send_message("This command can only be used in ticket channels!", ephemeral=True)
            return

        await interaction.response.send_message("Closing this ticket in 5 seconds...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.type == nextcord.InteractionType.component:
            custom_id = interaction.data['custom_id']
            if custom_id in ["support_ticket", "bug_report", "other_ticket"]:
                ticket_type = {
                    "support_ticket": "Support",
                    "bug_report": "Bug Report",
                    "other_ticket": "Other"
                }[custom_id]
                await self._create_ticket(interaction, ticket_type)

def setup(bot):
    bot.add_cog(TicketBot(bot))