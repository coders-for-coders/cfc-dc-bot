export const welcome = (message) => {
    const welcome_ChannelId = process.env.CHANNEL_ID;
    const channel = message.guild.channels.cache.get(welcome_ChannelId);
  
    const avatarURL = message.user.displayAvatarURL({
      size: 512,
      dynamic: true,
    });

  
    channel.send({
      embeds: [
        {
          color: 3447003,
          thumbnail: {
            url: avatarURL,
          },
          title: `${message.user.displayName}, welcome to coders for coders official server!`,
          description: "**Here we value you.**",
          fields: [
            {
              name: "",
              value:
                "Please make sure to read [Rules](https://discord.com/channels/1321441981628551248/1321475345798402158) and get started your journey with us!",
              inline: false,
            },
          ],
          timestamp: new Date(),
        },
      ],
    });
  };