import { SlashCommandBuilder } from "@discordjs/builders";
import {
    CommandInteraction,
    CommandInteractionOptionResolver,
} from "discord.js";
import { UserModel } from "../../models/User";
import axios from "axios";

const models = [
    { name: "Llama 3.1 8B Instant", value: "llama-3.1-8b-instant" },
    { name: "Llama Guard 3 8B", value: "llama-guard-3-8b" },
    {
        name: "Llama 3.2 90B Vision Preview",
        value: "llama-3.2-90b-vision-preview",
    },
    { name: "Distil Whisper Large V3 EN", value: "distil-whisper-large-v3-en" },
    { name: "Allam 2 7B", value: "allam-2-7b" },
    { name: "Gemma 2 9B IT", value: "gemma2-9b-it" },
    { name: "Llama 3.2 3B Preview", value: "llama-3.2-3b-preview" },
    { name: "Llama 3.3 70B Versatile", value: "llama-3.3-70b-versatile" },
    { name: "Qwen 2.5 32B", value: "qwen-2.5-32b" },
    { name: "Llama 3.3 70B SpecDec", value: "llama-3.3-70b-specdec" },
    {
        name: "DeepSeek R1 Distill Llama 70B",
        value: "deepseek-r1-distill-llama-70b",
    },
    {
        name: "DeepSeek R1 Distill Qwen 32B",
        value: "deepseek-r1-distill-qwen-32b",
    },
    { name: "Whisper Large V3 Turbo", value: "whisper-large-v3-turbo" },
    { name: "Whisper Large V3", value: "whisper-large-v3" },
    { name: "Mixtral 8x7B 32K", value: "mixtral-8x7b-32768" },
    { name: "Llama 3.2 1B Preview", value: "llama-3.2-1b-preview" },
    { name: "Llama 3 8B 8K", value: "llama3-8b-8192" },
    { name: "Qwen 2.5 Coder 32B", value: "qwen-2.5-coder-32b" },
    {
        name: "Llama 3.2 11B Vision Preview",
        value: "llama-3.2-11b-vision-preview",
    },
    { name: "Mistral SABA 24B", value: "mistral-saba-24b" },
    { name: "Llama 3 70B 8K", value: "llama3-70b-8192" },
    { name: "Qwen QWQ 32B", value: "qwen-qwq-32b" },
];

export const data = new SlashCommandBuilder()
    .setName("text")
    .setDescription("Generate text using a selected model")
    .addStringOption((option) =>
        option
            .setName("prompt")
            .setDescription("The prompt to generate text from")
            .setRequired(true),
    )
    .addStringOption((option) =>
        option
            .setName("model")
            .setDescription("Select the model to use for text generation")
            .setRequired(true)
            .addChoices(...models),
    )
    .addIntegerOption((option) =>
        option
            .setName("max_tokens")
            .setDescription(
                "Maximum number of tokens in the output (default: 100)",
            )
            .setMinValue(10)
            .setMaxValue(500),
    )
    .addNumberOption((option) =>
        option
            .setName("temperature")
            .setDescription("Controls randomness in generation (default: 0.7)")
            .setMinValue(0.1)
            .setMaxValue(2.0),
    );

export async function execute(interaction: CommandInteraction): Promise<void> {
    await interaction.deferReply();

    const options = interaction.options as CommandInteractionOptionResolver;
    const prompt = options.getString("prompt");
    const model = options.getString("model");
    const maxTokens = options.getInteger("max_tokens") || 100;
    const temperature = options.getNumber("temperature") || 0.7;

    if (!prompt) {
        await interaction.editReply("Please provide a prompt!");
        return;
    }

    const userId = interaction.user.id;

    try {
        let user = await UserModel.findOne({ userId });
        if (!user) {
            user = new UserModel({ userId });
            await user.save();
        }

        if (user.credits.text <= 0) {
            await interaction.editReply(
                "You have no credits left! Please purchase more credits to generate text.",
            );
            return;
        }

        user.credits.text -= 1;
        await user.save();

        const isChatModel = !model?.includes("whisper");

        let response;
        const chatData = {
            model: model,
            messages: [
                {
                    role: "user",
                    content: prompt,
                },
            ],
            max_tokens: maxTokens,
            temperature: temperature,
        };

        response = await axios.post(
            "https://api.groq.com/openai/v1/chat/completions",
            chatData,
            {
                headers: {
                    Authorization: `Bearer ${process.env.GROQ_API_KEY}`,
                    "Content-Type": "application/json",
                },
            },
        );

        if (response.status !== 200) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = response.data;
        let generatedText;

        if (isChatModel) {
            generatedText =
                result.choices[0]?.message?.content || "No text generated.";
        } else {
            generatedText = result.choices[0]?.text || "No text generated.";
        }

        await interaction.editReply({
            content: `-# (${user.credits.text} credits left) \n\n Generated text for prompt: **${prompt}**\n\n${generatedText}`,
        });
    } catch (error) {
        console.error(error);
        await interaction.editReply({
            content:
                "There was an error generating your text. Please try again later.",
        });
    }
}
