import { EmbedBuilder, SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import axios, { AxiosError } from "axios";

interface GitHubRepo {
    name: string;
    html_url: string;
    description: string | null;
    stargazers_count: number;
    forks_count: number;
    updated_at: string;
    language: string | null;
    open_issues_count: number;
    owner: {
        login: string;
        avatar_url: string;
    };
}

interface GitHubUser {
    login: string;
    html_url: string;
    avatar_url: string;
    name: string | null;
    bio: string | null;
    followers: number;
    following: number;
    public_repos: number;
    location: string | null;
    company: string | null;
    blog: string | null;
    created_at: string;
}

export default {
    data: new SlashCommandBuilder()
        .setName("github")
        .setDescription("Searches GitHub for repositories or users")
        .addStringOption((option) =>
            option
                .setName("query")
                .setDescription(
                    "The GitHub repository (owner/repo) or username to search for"
                )
                .setRequired(true)
        )
        .addStringOption((option) =>
            option
                .setName("type")
                .setDescription(
                    "Type of search: 'repo' for repository, 'user' for user profile"
                )
                .setChoices(
                    { name: "Repository", value: "repo" },
                    { name: "User", value: "user" }
                )
                .setRequired(false)
        )
        .addStringOption((option) =>
            option
                .setName("sort")
                .setDescription(
                    "Sort repositories by stars, forks, or updated date (only for type=repo)"
                )
                .setChoices(
                    { name: "Stars", value: "stars" },
                    { name: "Forks", value: "forks" },
                    { name: "Updated", value: "updated" }
                )
                .setRequired(false)
        )
        .addStringOption((option) =>
            option
                .setName("order")
                .setDescription(
                    "Sort order: ascending or descending (default: desc)"
                )
                .setChoices(
                    { name: "Ascending", value: "asc" },
                    { name: "Descending", value: "desc" }
                )
                .setRequired(false)
        )
        .addIntegerOption((option) =>
            option
                .setName("limit")
                .setDescription("Number of results to show (1-10, default: 5)")
                .setMinValue(1)
                .setMaxValue(10)
                .setRequired(false)
        ),

    async execute(interaction: CommandInteraction) {
        await interaction.deferReply();

        const query = interaction.options.get("query")?.value as string;
        const type = (interaction.options.get("type")?.value as string) || "repo";
        const sort = (interaction.options.get("sort")?.value as string) || "stars";
        const order = (interaction.options.get("order")?.value as string) || "desc";
        const limit = (interaction.options.get("limit")?.value as number) || 5;

        try {
            const apiKey = process.env.GITHUB_API_KEY;
            let headers: Record<string, string> = {
                "Accept": "application/vnd.github.v3+json"
            };
            if (apiKey) {
                headers.Authorization = `token ${apiKey}`;
            }

            if (type === "repo") {
                await handleRepoSearch(interaction, query, sort, order, limit, headers);
            } else if (type === "user") {
                await handleUserSearch(interaction, query, limit, headers);
            }
        } catch (error) {
            await handleError(interaction, error);
        }
    },
};

async function handleRepoSearch(
    interaction: CommandInteraction, 
    query: string, 
    sort: string, 
    order: string, 
    limit: number, 
    headers: Record<string, string>
) {
    // Determine if this is a direct repository fetch (owner/repo format) or a search
    const isDirectRepo = /^[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/.test(query);
    
    let repos: GitHubRepo[];
    
    if (isDirectRepo) {
        // Direct repository fetch
        const url = `https://api.github.com/repos/${query}`;
        const { data } = await axios.get<GitHubRepo>(url, { headers });
        repos = [data];
    } else {
        // Repository search
        const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(
            query
        )}&sort=${sort}&order=${order}&per_page=${limit}`;
        const { data } = await axios.get(url, { headers });
        repos = data.items.slice(0, limit);
    }

    if (!repos || repos.length === 0) {
        await interaction.editReply("No repositories found.");
        return;
    }

    const embed = new EmbedBuilder()
        .setColor(0x0099ff)
        .setTitle(isDirectRepo ? `GitHub Repository: ${query}` : `Top GitHub Repositories for: ${query}`)
        .setFooter({
            text: isDirectRepo 
                ? `Repository information` 
                : `Showing ${repos.length} results | Sorted by ${sort} (${order})`
        })
        .setTimestamp();

    if (repos[0]?.owner?.avatar_url) {
        embed.setThumbnail(repos[0].owner.avatar_url);
    }

    repos.forEach((repo, index) => {
        const updatedDate = new Date(repo.updated_at).toLocaleDateString();
        
        embed.addFields({
            name: isDirectRepo ? repo.name : `${index + 1}. ${repo.name}`,
            value: `
                _${repo.description || "No description available"}_
                ⭐ Stars: ${repo.stargazers_count} | 🍴 Forks: ${repo.forks_count} | ⚠️ Issues: ${repo.open_issues_count}
                ${repo.language ? `🔤 Language: ${repo.language} | ` : ''}📅 Updated: ${updatedDate}
                👤 Owner: [${repo.owner.login}](https://github.com/${repo.owner.login})
                🔗 [View on GitHub](${repo.html_url})
            `,
            inline: false,
        });
    });

    await interaction.editReply({ embeds: [embed] });
}

async function handleUserSearch(
    interaction: CommandInteraction, 
    query: string, 
    limit: number, 
    headers: Record<string, string>
) {
    const isDirectUser = /^[a-zA-Z0-9_-]+$/.test(query) && !query.includes(" ");
    
    let users: Array<{ url: string; html_url: string; login: string }>;
    
    if (isDirectUser) {
        const url = `https://api.github.com/users/${query}`;
        try {
            const { data } = await axios.get(url, { headers });
            const userData = {
                url,
                html_url: data.html_url,
                login: data.login
            };
            users = [userData];
        } catch (error) {
            if ((error as AxiosError).response?.status === 404) {
                await interaction.editReply(`User '${query}' not found.`);
                return;
            }
            throw error;
        }
    } else {
        const url = `https://api.github.com/search/users?q=${encodeURIComponent(query)}&per_page=${limit}`;
        const { data } = await axios.get(url, { headers });
        users = data.items.slice(0, limit);
    }

    if (!users || users.length === 0) {
        await interaction.editReply("No users found.");
        return;
    }

    const embed = new EmbedBuilder()
        .setColor(0x0099ff)
        .setTitle(isDirectUser ? `GitHub User: ${query}` : `Top GitHub Users for: ${query}`)
        .setFooter({ 
            text: isDirectUser ? `User information` : `Showing ${users.length} results` 
        })
        .setTimestamp();

    const userDetailsPromises = users.map(user => 
        axios.get<GitHubUser>(user.url, { headers })
    );
    
    const userDetailsResults = await Promise.allSettled(userDetailsPromises);
    
    userDetailsResults.forEach((result, index) => {
        if (result.status === 'fulfilled') {
            const userData = result.value.data;
            
            if (index === 0 && userData.avatar_url) {
                embed.setThumbnail(userData.avatar_url);
            }
            
            const createdDate = new Date(userData.created_at).toLocaleDateString();
            
            embed.addFields({
                name: isDirectUser ? userData.login : `${index + 1}. ${userData.login}`,
                value: `
                    ${userData.name ? `**${userData.name}**` : ''}
                    ${userData.bio ? `_${userData.bio}_\n` : ''}
                    👥 Followers: ${userData.followers} | 👤 Following: ${userData.following}
                    📦 Repositories: ${userData.public_repos} | 📅 Joined: ${createdDate}
                    ${userData.location ? `📍 Location: ${userData.location}\n` : ''}
                    ${userData.company ? `🏢 Company: ${userData.company}\n` : ''}
                    ${userData.blog ? `🔗 Website: [Link](${userData.blog})\n` : ''}
                    🔗 [View Profile](${userData.html_url})
                `,
                inline: false,
            });
        } else {
            embed.addFields({
                name: `${index + 1}. ${users[index].login}`,
                value: `[View Profile](${users[index].html_url})
                        *Could not fetch detailed information*`,
                inline: false,
            });
        }
    });

    await interaction.editReply({ embeds: [embed] });
}

async function handleError(interaction: CommandInteraction, error: unknown) {
    console.error(
        "Error fetching GitHub data:",
        (error as AxiosError).response?.data || (error as Error).message
    );

    const axiosError = error as AxiosError;
    
    if (axiosError.response?.status === 404) {
        await interaction.editReply("Repository or user not found.");
    } else if (axiosError.response?.status === 403) {
        await interaction.editReply(
            "Rate limit exceeded. Please try again later or configure a GitHub API key."
        );
    } else if (axiosError.response?.status === 401) {
        await interaction.editReply(
            "Authentication error. Please check your GitHub API key."
        );
    } else {
        await interaction.editReply(
            "An error occurred while fetching data from GitHub. Please try again later."
        );
    }
}