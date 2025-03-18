import { Events, GuildMember } from "discord.js";

const welcomeMessages = [
    "Hey {user}, welcome to our awesome community! 🎉",
    "Welcome aboard {user}! Great to have you here! 🚀", 
    "A wild {user} appeared! Welcome to the server! ✨",
    "Everyone give a warm welcome to {user}! 🎊",
    "Welcome to the family {user}! Make yourself at home! 🏠",
    "Look who just joined - it's {user}! Welcome! 🌟",
    "Glad you're here {user}! Let's make some memories! 🎈",
    "The party can start now that {user} is here! 🎸",
    "Welcome to our corner of Discord {user}! 💫",
    "A new friend has arrived! Welcome {user}! 🤝"
];

export default {
    name: Events.GuildMemberAdd,
    once: false,
    async execute(member: GuildMember) {
        const channel = member.guild.channels.cache.get('1303415571433525330');
        if (!channel?.isTextBased()) return;

        const randomMessage = welcomeMessages[Math.floor(Math.random() * welcomeMessages.length)]
            .replace('{user}', `<@${member.id}>`);

        await channel.send(randomMessage);
    }
};
