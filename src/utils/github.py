import os
from typing import Tuple, Dict, Any, List
from core.http import HTTPClient

class GitHubAPI(HTTPClient):
    """Handles GitHub API interactions"""
    def __init__(self):
        self.github_org = os.getenv("GITHUB_ORG", "coders-for-coders")
        headers = {
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
            "Accept": "application/vnd.github.v3+json", 
            "X-GitHub-Api-Version": "2022-11-28"
        }
        super().__init__(base_url="https://api.github.com", headers=headers)

    async def get_members(self) -> Tuple[int, List[Dict[str, Any]]]:
        """Get organization members
        
        Returns:
            Tuple of (status code, response data)
        """
        return await self.get(f"/orgs/{self.github_org}/members")

    async def invite_user(self, username: str) -> Tuple[int, Dict[str, Any]]:
        """Invite a user to the organization"""
        return await self.post(
            f"/orgs/{self.github_org}/invitations",
            json={"email": username, "role": "direct_member"}
        )

    async def get_repos(self, username: str = None) -> Tuple[int, List[Dict[str, Any]]]:
        """Get repositories for org or user"""
        owner = f"users/{username}" if username else f"orgs/{self.github_org}"
        return await self.get(f"/{owner}/repos")

    async def get_teams(self) -> Tuple[int, List[Dict[str, Any]]]:
        """Get organization teams"""
        return await self.get(f"/orgs/{self.github_org}/teams")

    async def get_user(self, username: str) -> Tuple[int, Dict[str, Any]]:
        """Get user information"""
        return await self.get(f"/users/{username}")

    async def get_repo(self, username: str, repo_name: str) -> Tuple[int, Dict[str, Any]]:
        """Get repository information"""
        return await self.get(f"/repos/{username}/{repo_name}")

    async def search_repos(self, query: str) -> Tuple[int, Dict[str, Any]]:
        """Search repositories"""
        return await self.get(f"/search/repositories?q={query}&sort=stars&order=desc")

    async def search_users(self, query: str) -> Tuple[int, Dict[str, Any]]:
        """Search users"""
        return await self.get(f"/search/users?q={query}&sort=followers&order=desc")
