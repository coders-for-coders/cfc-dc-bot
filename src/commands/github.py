from utils import (
    SlashCommand,
    Option,
    ApplicationCommandOptionType
)
from core.command import command
from core.embed import EmbedBuilder
from utils.github import GitHubAPI
from core.ui import Button, ActionRow

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
            name="orgs",
            description="Organization related commands", 
            type=ApplicationCommandOptionType.SUB_COMMAND_GROUP,
            options=[
                Option(
                    name="members",
                    description="List organization members",
                    type=ApplicationCommandOptionType.SUB_COMMAND
                ),
                Option(
                    name="join",
                    description="Join the organization",
                    type=ApplicationCommandOptionType.SUB_COMMAND,
                    options=[
                        Option(
                            name="username",
                            description="GitHub username",
                            type=ApplicationCommandOptionType.STRING,
                            required=True
                        )
                    ]
                )
            ]
        ),
        Option(
            name="get",
            description="Get a GitHub user or repository",
            type=ApplicationCommandOptionType.SUB_COMMAND_GROUP,
            options=[
                Option(
                    name="user",
                    description="Get a GitHub user",
                    type=ApplicationCommandOptionType.SUB_COMMAND,
                    options=[
                        Option(
                            name="username",
                            description="GitHub username", 
                            type=ApplicationCommandOptionType.STRING,
                            required=True
                        )
                    ]
                ),
                Option(
                    name="repo",
                    description="Get a GitHub repository",
                    type=ApplicationCommandOptionType.SUB_COMMAND,
                    options=[
                        Option(
                            name="username",
                            description="GitHub username",
                            type=ApplicationCommandOptionType.STRING,
                            required=True
                        ),
                        Option(
                            name="repo",
                            description="GitHub repository",
                            type=ApplicationCommandOptionType.STRING,
                            required=True
                        )
                    ]
                )
            ]
        ),
        Option(
            name="search",
            description="Search GitHub",
            type=ApplicationCommandOptionType.SUB_COMMAND_GROUP,
            options=[
                Option(
                    name="users",
                    description="Search GitHub users",
                    type=ApplicationCommandOptionType.SUB_COMMAND,
                    options=[
                        Option(
                            name="query",
                            description="Search query",
                            type=ApplicationCommandOptionType.STRING,
                            required=True
                        )
                    ]
                ),
                Option(
                    name="repos", 
                    description="Search GitHub repositories",
                    type=ApplicationCommandOptionType.SUB_COMMAND,
                    options=[
                        Option(
                            name="query",
                            description="Search query",
                            type=ApplicationCommandOptionType.STRING,
                            required=True
                        )
                    ]
                )
            ]
        )
    ]
)
class GitHubCommand(SlashCommand):
    async def respond(self, interaction_data: dict):
        await self.defer_response(interaction_data, ephemeral=False)
        
        try:
            command_group = interaction_data["data"]["options"][0]["name"]
            subcommand = interaction_data["data"]["options"][0]["options"][0]["name"]
            
            handlers = {
                "orgs": {
                    "members": self._handle_members,
                    "join": self._handle_join
                },
                "search": {
                    "users": self._handle_search_users,
                    "repos": self._handle_search_repos
                },
                "get": {
                    "user": self._handle_user,
                    "repo": self._handle_repo
                }
            }
            
            if handler := handlers.get(command_group, {}).get(subcommand):
                return await handler(interaction_data)
                
            return await self.edit_response(
                interaction_data,
                content="Unknown command"
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
            
            embed = EmbedBuilder()
            embed.set_title("Organization Members")
            embed.set_color(0x2b2d31)
            
            member_list = [
                f"• [{member['login']}]({member['html_url']})" 
                for member in members
            ]
            
            embed.set_description("\n".join(member_list) if member_list else "No members found")
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

    async def _handle_join(self, interaction_data: dict):
        """Handle the join subcommand"""
        github = GitHubAPI()
        try:
            username = interaction_data["data"]["options"][0]["options"][0]["options"][0]["value"]
            
            status, user = await github.get_user(username)
            if status != 200:
                return await self.edit_response(
                    interaction_data,
                    content=f"Failed to find GitHub user: {username}"
                )
                
            status, response = await github.invite_user(username)
            if status != 201:
                return await self.edit_response(
                    interaction_data,
                    content=f"Failed to send invitation: {response.get('message', 'Unknown error')}"
                )
                
            return await self.edit_response(
                interaction_data,
                content=f"Successfully sent invitation to {username}"
            )
            
        except Exception as e:
            return await self.edit_response(
                interaction_data,
                content=f"Error sending invitation: {str(e)}"
            )
        finally:
            await github.close()

    async def _handle_search_users(self, interaction_data: dict):
        """Handle the search users subcommand"""
        github = GitHubAPI()
        try:
            query = interaction_data["data"]["options"][0]["options"][0]["options"][0]["value"]
            
            status, response = await github.search_users(query)
            if status != 200:
                return await self.edit_response(
                    interaction_data,
                    content=f"Failed to search users: {response.get('message', 'Unknown error')}"
                )
                
            items = response.get("items", [])[:10]
            
            embed = EmbedBuilder()
            embed.set_title(f"GitHub User Search: {query}")
            embed.set_color(0x2b2d31)
            
            results = [
                f"• [{user['login']}]({user['html_url']})"
                for user in items
            ]
            
            embed.set_description("\n".join(results) if results else "No users found")
            embed.set_footer(
                text=f"Total Results: {response.get('total_count', 0)}",
                icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            )
            
            return await self.edit_response(
                interaction_data,
                embeds=[embed.to_dict()]
            )
            
        except Exception as e:
            return await self.edit_response(
                interaction_data,
                content=f"Error searching users: {str(e)}"
            )
        finally:
            await github.close()

    async def _handle_search_repos(self, interaction_data: dict):
        """Handle the search repos subcommand"""
        github = GitHubAPI()
        try:
            query = interaction_data["data"]["options"][0]["options"][0]["options"][0]["value"]
            
            status, response = await github.search_repos(query)
            if status != 200:
                return await self.edit_response(
                    interaction_data,
                    content=f"Failed to search repositories: {response.get('message', 'Unknown error')}"
                )
                
            items = response.get("items", [])[:10]
            
            embed = EmbedBuilder()
            embed.set_title(f"GitHub Repository Search: {query}")
            embed.set_color(0x2b2d31)
            
            results = [
                f"• [{repo['full_name']}]({repo['html_url']})\n  ⭐ {repo.get('stargazers_count', 0)} - {repo.get('description', 'No description')}"
                for repo in items
            ]
            
            embed.set_description("\n".join(results) if results else "No repositories found")
            embed.set_footer(
                text=f"Total Results: {response.get('total_count', 0)}",
                icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            )
            
            return await self.edit_response(
                interaction_data,
                embeds=[embed.to_dict()]
            )
            
        except Exception as e:
            return await self.edit_response(
                interaction_data,
                content=f"Error searching repositories: {str(e)}"
            )
        finally:
            await github.close()

    async def _handle_user(self, interaction_data: dict):
        """Handle the user subcommand"""
        github = GitHubAPI()
        try:
            username = interaction_data["data"]["options"][0]["options"][0]["options"][0]["value"]
            
            status, user = await github.get_user(username)
            if status != 200:
                return await self.edit_response(
                    interaction_data,
                    content=f"Failed to fetch user: {user.get('message', 'Unknown error')}"
                )

            embed = EmbedBuilder()
            embed.set_title(user.get("name", username))
            embed.set_color(0x2b2d31)
            embed.set_thumbnail(user.get("avatar_url"))
            
            description = []
            if user.get("bio"):
                description.append(user["bio"])
            description.append(f"**Username:** [{username}]({user['html_url']})")
            
            for field, label in [
                ("company", "Company"),
                ("location", "Location"),
                ("email", "Email"),
                ("blog", "Website")
            ]:
                if user.get(field):
                    description.append(f"**{label}:** {user[field]}")
            
            embed.set_description("\n".join(description))
            
            for field, value in [
                ("Followers", user.get("followers", 0)),
                ("Following", user.get("following", 0)),
                ("Public Repos", user.get("public_repos", 0))
            ]:
                embed.add_field(field, str(value), True)
            
            embed.set_footer(
                text=f"Joined GitHub on {user['created_at'][:10]}",
                icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            )

            view = ActionRow(
                Button(
                    label="View Profile",
                    style=5,
                    url=user["html_url"]
                )
            )
            
            return await self.edit_response(
                interaction_data,
                embeds=[embed.to_dict()],
                components=[view.to_dict()]
            )
            
        except Exception as e:
            return await self.edit_response(
                interaction_data,
                content=f"Error fetching user: {str(e)}"
            )
        finally:
            await github.close()

    async def _handle_repo(self, interaction_data: dict):
        """Handle the repo subcommand"""
        github = GitHubAPI()
        try:
            username = interaction_data["data"]["options"][0]["options"][0]["options"][0]["value"]
            repo_name = interaction_data["data"]["options"][0]["options"][0]["options"][1]["value"]
            
            status, repo = await github.get_repo(username, repo_name)
            if status != 200:
                return await self.edit_response(
                    interaction_data,
                    content=f"Failed to fetch repository: {repo.get('message', 'Unknown error')}"
                )

            embed = EmbedBuilder()
            embed.set_title(repo.get("full_name"))
            embed.set_color(0x2b2d31)
            
            if avatar_url := repo.get("owner", {}).get("avatar_url"):
                embed.set_thumbnail(avatar_url)
            
            description = []
            if repo.get("description"):
                description.append(repo["description"])
            description.append(f"**Repository:** [{repo['full_name']}]({repo['html_url']})")
            if repo.get("homepage"):
                description.append(f"**Website:** {repo['homepage']}")
            
            embed.set_description("\n".join(description))
            
            for field, value in [
                ("Stars", repo.get("stargazers_count", 0)),
                ("Forks", repo.get("forks_count", 0)), 
                ("Open Issues", repo.get("open_issues_count", 0))
            ]:
                embed.add_field(field, str(value), True)
            
            if repo.get("language"):
                embed.add_field("Language", repo["language"], True)
            if license_name := repo.get("license", {}).get("name"):
                embed.add_field("License", license_name, True)
            
            embed.set_footer(
                text=f"Created on {repo['created_at'][:10]}",
                icon_url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            )

            buttons = []
            buttons.append(Button(
                label="View Repository",
                style=5,
                url=repo["html_url"]
            ))

            if repo.get("homepage"):
                buttons.append(Button(
                    label="Visit Website",
                    style=5,
                    url=repo["homepage"]
                ))

            view = ActionRow(*buttons)
            
            return await self.edit_response(
                interaction_data,
                embeds=[embed.to_dict()],
                components=[view.to_dict()]
            )
            
        except Exception as e:
            return await self.edit_response(
                interaction_data,
                content=f"Error fetching repository: {str(e)}"
            )
        finally:
            await github.close()