import fs from "fs";
import path from "path";
import { SlashCommandBuilder } from "@discordjs/builders";
import {
    CommandInteraction,
    CommandInteractionOptionResolver,
} from "discord.js";
import axios from "axios";

import { UserModel } from "../../models/User";

export const data = new SlashCommandBuilder()
    .setName("image")
    .setDescription("Generate an image using a selected model")
    .addStringOption((option) =>
        option
            .setName("prompt")
            .setDescription("The prompt to generate the image from")
            .setRequired(true),
    )
    .addStringOption((option) =>
        option
            .setName("model")
            .setDescription("Select the model to use for image generation")
            .setRequired(true)
            .addChoices(
                { name: "FLUX.1-dev", value: "black-forest-labs/FLUX.1-dev" },
                {
                    name: "Stable Diffusion 3.5 Large",
                    value: "stabilityai/stable-diffusion-3.5-large",
                },
                {
                    name: "FLUX.1-schnell",
                    value: "black-forest-labs/FLUX.1-schnell",
                },
                {
                    name: "Stable Diffusion XL Base 1.0",
                    value: "stabilityai/stable-diffusion-xl-base-1.0",
                },
                {
                    name: "Flux-Midjourney-Mix2-LoRA",
                    value: "strangerzonehf/Flux-Midjourney-Mix2-LoRA",
                },
                {
                    name: "Stable Diffusion v1.5",
                    value: "stable-diffusion-v1-5/stable-diffusion-v1-5",
                },
                { name: "Hyper-SD", value: "ByteDance/Hyper-SD" },
                {
                    name: "Stable Diffusion 3.5 Large Turbo",
                    value: "stabilityai/stable-diffusion-3.5-large-turbo",
                },
                { name: "CogView4-6B", value: "THUDM/CogView4-6B" },
                {
                    name: "Flux-RealismLora",
                    value: "XLabs-AI/flux-RealismLora",
                },
                {
                    name: "Flux-Lora-Eric-Cat",
                    value: "ginipick/flux-lora-eric-cat",
                },
                {
                    name: "Stable Diffusion 3.5 Medium",
                    value: "stabilityai/stable-diffusion-3.5-medium",
                },
                { name: "Claude Monet", value: "openfree/claude-monet" },
                {
                    name: "Flux-Lora-Korea-Palace",
                    value: "openfree/flux-lora-korea-palace",
                },
                { name: "Gamzekocc_Fluxx", value: "codermert/gamzekocc_fluxx" },
                {
                    name: "AngryPenguin_Claude",
                    value: "glif-loradex-trainer/angrypenguin_claude",
                },
                {
                    name: "Flux-Lora-Car-Rolls-Royce",
                    value: "seawolf2357/flux-lora-car-rolls-royce",
                },
                {
                    name: "Flux-Lora-Military-Artillery-K9",
                    value: "seawolf2357/flux-lora-military-artillery-k9",
                },
                { name: "Hanbok", value: "seawolf2357/hanbok" },
                { name: "NTower", value: "seawolf2357/ntower" },
            ),
    )
    .addStringOption((option) =>
        option
            .setName("dimensions")
            .setDescription(
                "Image dimensions in WIDTHxHEIGHT format (e.g., 120x120, default: 1024x1024)",
            ),
    )
    .addIntegerOption((option) =>
        option
            .setName("steps")
            .setDescription("Number of inference steps (default: 50)")
            .setMinValue(10)
            .setMaxValue(100),
    )
    .addNumberOption((option) =>
        option
            .setName("guidance_scale")
            .setDescription(
                "Guidance scale for the image generation (default: 7.5)",
            )
            .setMinValue(1.0)
            .setMaxValue(20.0),
    )
    .addIntegerOption((option) =>
        option
            .setName("seed")
            .setDescription("Seed for reproducibility (optional)"),
    );

export async function execute(interaction: CommandInteraction) {
    await interaction.deferReply();

    const options = interaction.options as CommandInteractionOptionResolver;
    const prompt = options.getString("prompt");
    const model = options.getString("model");
    const dimensions = options.getString("dimensions") || "512x512";
    const steps = options.getInteger("steps") || 50;
    const guidanceScale = options.getNumber("guidance_scale") || 7.5;
    const seed = options.getInteger("seed");

    if (!prompt) {
        return interaction.editReply("Please provide a prompt!");
    }

    let width, height;
    try {
        [width, height] = dimensions.split("x").map(Number);
        if (
            isNaN(width) ||
            isNaN(height) ||
            width < 256 ||
            height < 256 ||
            width > 1024 ||
            height > 1024
        ) {
            throw new Error("Invalid dimensions");
        }
    } catch (error) {
        return interaction.editReply(
            "Invalid dimensions format! Use WIDTHxHEIGHT (e.g., 120x120). Dimensions must be between 256 and 1024.",
        );
    }

    try {
        const userId = interaction.user.id;
        let user = await UserModel.findOne({ userId });
        if (!user) {
            user = new UserModel({ userId });
            await user.save();
        }

        if (user.credits.image <= 0) {
            return interaction.editReply(
                "You have no credits left. We need to maintain some limits. Please check back later.",
            );
        }
        user.credits.image -= 1;
        await user.save();

        const data = {
            inputs: prompt,
            parameters: {
                width,
                height,
                num_inference_steps: steps,
                guidance_scale: guidanceScale,
                seed: seed || undefined,
            },
        };

        const response = await axios.post(
            `https://router.huggingface.co/hf-inference/models/${model}`,
            data,
            {
                headers: {
                    Authorization: `Bearer ${process.env.HUGGINGFACE_API_KEY}`,
                    "Content-Type": "application/json",
                    "x-wait-for-model": "true",
                },
                responseType: "arraybuffer",
            },
        );

        if (response.status !== 200) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const timestamp = Date.now();
        const filename = `generated-image-${timestamp}.png`;
        const buffer = Buffer.from(response.data);
        const attachment = {
            files: [{ attachment: buffer, name: filename }],
        };

        await interaction.editReply({
            content: `-# (${user.credits.image} credits left) \n\n Generated image for prompt: **${prompt}**`,
            ...attachment,
        });
    } catch (error) {
        console.error(error);
        await interaction.editReply({
            content:
                "There was an error generating your image. Please try again later.",
        });
    }
}
