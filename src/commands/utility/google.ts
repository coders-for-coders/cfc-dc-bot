import { EmbedBuilder, SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction, AutocompleteInteraction } from "discord.js";
import axios from "axios";
import { console } from "inspector";

export const data = new SlashCommandBuilder()
    .setName("google")
    .setDescription("Searches Google")
    .addStringOption((option) =>
        option
            .setName("query")
            .setDescription("The query to search for")
            .setRequired(true)
            .setAutocomplete(true),
    )
    .addIntegerOption((option) =>
        option
            .setName("results")
            .setDescription("Number of results to show (1-10)")
            .setMinValue(1)
            .setMaxValue(10)
            .setRequired(false),
    )
    .addBooleanOption((option) =>
        option
            .setName("details")
            .setDescription(
                "Whether to show detailed results (including descriptions)",
            )
            .setRequired(false),
    )
    .addStringOption((option) =>
        option
            .setName("language")
            .setDescription(
                "Language of the search results (e.g., 'en' for English)",
            )
            .setRequired(false),
    )
    .addBooleanOption((option) =>
        option
            .setName("safesearch")
            .setDescription("Enable safe search (filters explicit content)")
            .setRequired(false),
    );

export async function autocomplete(interaction: AutocompleteInteraction) {
    const focusedValue = interaction.options.getFocused() as string;
    console.log(`autocomplete triggered for: "${focusedValue}"`);

    if (!focusedValue || focusedValue.trim() === "") {
        await interaction.respond([]);
        return;
    }

    try {
        console.log(`Autocomplete triggered for: "${focusedValue}"`);

        const url = `https://suggestqueries.google.com/complete/search?client=firefox&q=${encodeURIComponent(
            focusedValue,
        )}`;

        const response = await axios.get(url);
        console.log(
            "Google suggest API response:",
            JSON.stringify(response.data),
        );

        const suggestions = response.data[1];

        if (!suggestions || suggestions.length === 0) {
            console.log("No suggestions found");
            await interaction.respond([
                { name: "No suggestions found", value: focusedValue },
            ]);
            return;
        }

        const formattedSuggestions = suggestions
            .slice(0, 5)
            .map((suggestion: string) => ({
                name: suggestion,
                value: suggestion,
            }));

        console.log("Sending suggestions:", formattedSuggestions);
        await interaction.respond(formattedSuggestions);
    } catch (error) {
        console.error("Error fetching autocomplete suggestions:", error);
        await interaction.respond([
            { name: "Error fetching suggestions", value: focusedValue },
        ]);
    }
}

export async function execute(interaction: CommandInteraction) {
    await interaction.deferReply();

    const query = interaction.options.get("query")?.value as string;
    const numResults =
        (interaction.options.get("results")?.value as number) || 5;
    const showDetails =
        (interaction.options.get("details")?.value as boolean) || false;
    const language =
        (interaction.options.get("language")?.value as string) || "en";
    const safeSearch =
        (interaction.options.get("safesearch")?.value as boolean) || false;

    try {
        const apiKey = process.env.GOOGLE_SEARCH_API_KEY as string;
        const cx = process.env.GOOGLE_SEARCH_CX as string;

        const url = `https://www.googleapis.com/customsearch/v1?key=${apiKey}&cx=${cx}&q=${encodeURIComponent(
            query,
        )}&num=${numResults}&lr=lang_${language}&safe=${
            safeSearch ? "active" : "off"
        }`;

        const response = await axios.get(url);
        const results = response.data.items;

        if (!results || results.length === 0) {
            await interaction.editReply("No results found.");
            return;
        }

        interface SearchResult {
            title: string;
            link: string;
            snippet?: string;
            pagemap?: {
                cse_image?: Array<{ src: string }>;
                metatags?: Array<Record<string, string>>;
            };
        }

        const embed = new EmbedBuilder()
            .setColor(0x2b2d31)
            .setTitle(`Search results for: ${query}`);

        if (numResults === 1) {
            const result = results[0] as SearchResult;

            const imageUrl = result.pagemap?.cse_image?.[0]?.src || null;

            const metaTags = result.pagemap?.metatags?.[0];
            const keywords = metaTags?.["keywords"] || "No keywords available";

            embed.setDescription(
                `[${result.title}](${result.link})\n\n_${
                    result.snippet || "No description available"
                }_`,
            );

            if (imageUrl) {
                embed.setImage(imageUrl);
            }

            embed.addFields(
                { name: "Keywords", value: keywords, inline: true },
                {
                    name: "Link",
                    value: `[Visit Page](${result.link})`,
                    inline: true,
                },
            );
        } else {
            if (showDetails) {
                embed.setDescription(
                    (results as SearchResult[])
                        .map(
                            (result: SearchResult, i: number) =>
                                `${i + 1}. [${result.title}](${
                                    result.link
                                })\n_${
                                    result.snippet || "No description available"
                                }_`,
                        )
                        .join("\n\n"),
                );
            } else {
                embed.setDescription(
                    (results as SearchResult[])
                        .map(
                            (result: SearchResult, i: number) =>
                                `${i + 1}. [${result.title}](${result.link})`,
                        )
                        .join("\n"),
                );
            }
        }

        await interaction.editReply({ embeds: [embed] });
    } catch (error) {
        console.error("Error fetching Google search results:", error);
        await interaction.editReply("An error occurred while searching.");
    }
}
