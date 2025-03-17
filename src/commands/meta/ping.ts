import { EmbedBuilder, SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";

export default {
    data: new SlashCommandBuilder()
        .setName("ping")
        .setDescription("shows the latency of the bot"),
    async execute(interaction: CommandInteraction) {
        // const embed = new EmbedBuilder()
        //     .setDescription(`Latency: ${interaction.client.ws.ping}ms`)
        // await interaction.reply({ embeds: [embed] });
        await interaction.reply(`Latency: ${interaction.client.ws.ping}ms`);
    },
};
