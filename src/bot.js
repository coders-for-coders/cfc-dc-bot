import "dotenv/config";

import { Client, GatewayIntentBits } from "discord.js";
import { welcome } from "./features/welcome.js";

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessages,
  ],
});

client.on("guildMemberAdd", (message) => {
  welcome(message);
});

client.login(process.env.TOKEN_BOT_SECRET);
