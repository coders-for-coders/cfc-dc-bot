import { GatewayIntentBits } from "discord.js";
import dotenv from "dotenv";
import mongoose from "mongoose";
import { ExtendedClient } from "./core/client.js";
import { UserModel } from "./models/User.js";
import cron from "node-cron";

dotenv.config();


mongoose.connect(process.env.MONGODB_URI || "mongodb://localhost:27017/cfc-dc-bot")
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));


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

cron.schedule('0 0 * * *', async () => {
    try {
        console.log('Running daily credits reset...');
        const result = await UserModel.updateMany(
            {}, 
            { 
                $set: { 
                    'credits.image': 3,
                    'credits.text': 10 
                } 
            }
        );
        console.log(`Credits reset complete. Updated ${result.modifiedCount} users.`);
    } catch (error) {
        console.error('Error resetting credits:', error instanceof Error ? error.message : String(error));
    }
});

client.init();
