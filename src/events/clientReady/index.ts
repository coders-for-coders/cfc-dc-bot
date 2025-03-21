import { Client, Events, ActivityType } from "discord.js";

export default {
    name: Events.ClientReady,
    once: true,
    execute(client: Client) {
        console.log(`Logged in: ${client.user?.tag}`);
        client.user?.setPresence({
            status: "online",
            activities: [{
                name: "with my code",
                type: ActivityType.Playing
            }]
        });
    }
}