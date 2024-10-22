import nextcord
from nextcord.ext import commands

class ApplicationModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="Application Form")
        self.name = nextcord.ui.TextInput(label="Name", placeholder="Enter your name")
        self.age = nextcord.ui.TextInput(label="Age", placeholder="Enter your age")
        self.link = nextcord.ui.TextInput(label="Link", placeholder="Enter a relevant link (e.g., portfolio)")
        self.other = nextcord.ui.TextInput(label="Other Information", style=nextcord.TextInputStyle.paragraph, placeholder="Any other information you'd like to share")
        self.add_item(self.name)
        self.add_item(self.age)
        self.add_item(self.link)
        self.add_item(self.other)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        await create_application_channel(interaction, self.name.value, self.age.value, self.link.value, self.other.value)

class ApplicationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="setup_application", description="Set up the application system")
    @commands.has_permissions(administrator=True)
    async def setup_application(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Application System", description="Click the button below to submit an application:", color=nextcord.Color.green())
        
        view = nextcord.ui.View(timeout=None)
        view.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.success, label="Submit Application", emoji="📝", custom_id="submit_application"))

        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("Application system set up successfully!", ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.type == nextcord.InteractionType.component:
            custom_id = interaction.data['custom_id']
            if custom_id == "submit_application":
                application_modal = ApplicationModal()
                await interaction.response.send_modal(application_modal)
            elif custom_id == "accept_application":
                await handle_application_response(interaction, accepted=True)
            elif custom_id == "reject_application":
                await handle_application_response(interaction, accepted=False)

async def create_application_channel(interaction: nextcord.Interaction, name: str, age: str, link: str, other: str):
    guild = interaction.guild
    category = nextcord.utils.get(guild.categories, name="Applications")
    if not category:
        category = await guild.create_category("Applications")

    channel_name = f"application-{interaction.user.name.lower()}"
    channel = await category.create_text_channel(channel_name)

    embed = nextcord.Embed(title="New Application", color=nextcord.Color.gold())
    embed.add_field(name="Name", value=name, inline=False)
    embed.add_field(name="Age", value=age, inline=False)
    embed.add_field(name="Link", value=link, inline=False)
    embed.add_field(name="Other Information", value=other, inline=False)
    embed.set_footer(text=f"Applicant ID: {interaction.user.id}")  # Ensure this is always set

    view = nextcord.ui.View(timeout=None)
    view.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.success, label="Accept", custom_id="accept_application"))
    view.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.danger, label="Reject", custom_id="reject_application"))

    await channel.send(embed=embed, view=view)
    await interaction.followup.send("Your application has been submitted successfully!", ephemeral=True)

async def handle_application_response(interaction: nextcord.Interaction, accepted: bool):
    try:
        # Check if the footer exists and contains "Applicant ID: "
        footer_text = interaction.message.embeds[0].footer.text
        if "Applicant ID: " in footer_text:
            user_id = int(footer_text.split(": ")[1])
        else:
            raise ValueError("Invalid footer format")
    except (IndexError, AttributeError, ValueError):
        await interaction.response.send_message("Error: Could not retrieve applicant ID. Please check the application message.", ephemeral=True)
        return

    # If application is accepted
    if accepted:
        roles = [role for role in interaction.guild.roles if role.name != "@everyone"]
        options = [nextcord.SelectOption(label=role.name, value=str(role.id)) for role in roles]
        
        class RoleSelect(nextcord.ui.Select):
            def __init__(self):
                super().__init__(placeholder="Select a role to assign", options=options)

            async def callback(self, interaction: nextcord.Interaction):
                # Defer the interaction since this action may take some time
                await interaction.response.defer(ephemeral=True)

                role = interaction.guild.get_role(int(self.values[0]))
                member = await interaction.guild.fetch_member(user_id)

                try:
                    # Assign the role
                    await member.add_roles(role)

                    # Follow up with success message
                    await interaction.followup.send(f"Role ***{role.name}*** has been assigned to the applicant.", ephemeral=True)

                    # Send DM with a polished embed
                    embed = nextcord.Embed(
                        title="🎉 Application Accepted!",
                        description=f"Congratulations, **{member.name}**! Your application has been approved.",
                        color=nextcord.Color.green()
                    )
                    embed.add_field(name="Assigned Role", value=f"You have been assigned the **{role.name}** role!", inline=False)
                    embed.add_field(name="Welcome to the team!", value="We're excited to have you with us. If you have any questions, feel free to reach out.", inline=False)
                    embed.set_footer(text=f"Server: {interaction.guild.name}")
                    embed.timestamp = nextcord.utils.utcnow()

                    # Send the embed as a DM to the applicant
                    await member.send(embed=embed)

                except nextcord.errors.Forbidden:
                    # Handle permission error
                    await interaction.followup.send("Error: Missing permissions to assign this role. Please check the bot's role hierarchy and permissions.", ephemeral=True)

                # Delete the message in the application channel
                await interaction.message.delete()

        view = nextcord.ui.View()
        view.add_item(RoleSelect())

        # Acknowledge the interaction first to avoid the "already acknowledged" error
        await interaction.response.defer(ephemeral=True)

        # Ensure we only send a followup message since interaction is already acknowledged
        await interaction.followup.send("Please select a role to assign to the applicant:", view=view, ephemeral=True)

    # If application is rejected
    else:
        class RejectModal(nextcord.ui.Modal):
            def __init__(self):
                super().__init__(title="Rejection Reason")
                self.reason = nextcord.ui.TextInput(label="Reason", style=nextcord.TextInputStyle.paragraph, placeholder="Enter the reason for rejection")
                self.add_item(self.reason)

            async def callback(self, interaction: nextcord.Interaction):
                member = await interaction.guild.fetch_member(user_id)

                # Send DM with rejection embed
                embed = nextcord.Embed(
                    title="❌ Application Rejected!",
                    description=f"We're sorry **{member.name}**, but your application has been rejected.",
                    color=nextcord.Color.red()
                )
                embed.add_field(name="Reason:", value=self.reason.value, inline=False)
                embed.set_footer(text=f"Server: {interaction.guild.name}")
                embed.timestamp = nextcord.utils.utcnow()

                await member.send(embed=embed)
                await interaction.followup.send("The applicant has been notified of the rejection.", ephemeral=True)
                await interaction.message.delete()

        # No need to defer here, just send the modal directly
        await interaction.response.send_modal(RejectModal())

def setup(bot):
    bot.add_cog(ApplicationCog(bot))