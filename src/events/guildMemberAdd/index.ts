import { Events, GuildMember } from "discord.js";

export default {
    name: Events.GuildMemberAdd,
    once: false,
    execute(member: GuildMember) {
        console.log(`Welcome ${member.guild.name} ${member.user}!`);
    }
};