import { Client, Events } from "discord.js";

export default {
    name: Events.ClientReady,
    once: true,
    execute(client: Client) {
        console.log(`Logged in: ${client.user?.tag}`);
        client.user?.presence.set(
            {
                status: "online",
                activities: [
                    {
                        name: "with my code",
                        type: 0
                    }
                ]
            }
        )
    }
}