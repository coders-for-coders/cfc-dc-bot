from utils import (
    SlashCommand,
    Option,
    ApplicationCommandOptionType,
    InteractionResponseType,
)
from core.command import command, send_deferred_response
from core.embed import EmbedBuilder

from utils.github import GitHubAPI

github = GitHubAPI()

async def send_invitation(username: str):
    await github.invite_user(username)

async def get_org_members():
    return await github.get_members()


@command(
    name="github",
    description="GitHub organization commands",
    options=[
        Option(
            name="members",
            description="List organization members",
            type=ApplicationCommandOptionType.SUB_COMMAND
        ),
    ]
)
class GitHubCommand(SlashCommand):
    async def respond(self, interaction_data: dict):
        # Defer the response since GitHub API calls might take time
        await self.defer_response(interaction_data, ephemeral=True)
        
        try:
            # Get the subcommand
            subcommand = interaction_data["data"]["options"][0]["name"]
            
            if subcommand == "members":
                return await self._handle_members(interaction_data)
                
            return await self.edit_response(
                interaction_data,
                content="Unknown subcommand"
            )
            
        except Exception as e:
            return await self.edit_response(
                interaction_data,
                content=f"Error executing command: {str(e)}"
            )

    async def _handle_members(self, interaction_data: dict):
        """Handle the members subcommand"""
        github = GitHubAPI()
        try:
            status, members = await github.get_members()
            
            if status != 200:
                return await self.edit_response(
                    interaction_data,
                    content=f"Failed to fetch members: {members.get('message', 'Unknown error')}"
                )
            
            # Create embed for members list
            embed = EmbedBuilder()
            embed.set_title("Organization Members")
            embed.set_color(0x2b2d31)  # Discord dark theme color
            
            # Add members to embed
            member_list = []
            for member in members:
                username = member.get("login")
                profile_url = member.get("html_url")
                member_list.append(f"• [{username}]({profile_url})")
            
            if member_list:
                embed.set_description("\n".join(member_list))
            else:
                embed.set_description("No members found")
                
            embed.set_footer(
                text=f"Total Members: {len(members)}",
                icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            )
            
            return await self.edit_response(
                interaction_data,
                embeds=[embed.to_dict()]
            )
            
        except Exception as e:
            return await self.edit_response(
                interaction_data,
                content=f"Error fetching members: {str(e)}"
            )
        finally:
            await github.close()
