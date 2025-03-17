import { GatewayIntentBits } from "discord.js";
import dotenv from "dotenv";
import { ExtendedClient } from "./core/client.js";
dotenv.config();

// Create an instance of ExtendedClient
const client = new ExtendedClient({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
        GatewayIntentBits.GuildPresences,
        GatewayIntentBits.GuildVoiceStates,
        GatewayIntentBits.GuildMessageReactions,
    ],
});

client.init();