import { REST, Routes, Snowflake } from "discord.js";
import dotenv from "dotenv";
import * as fs from "fs";
import * as path from "path";

dotenv.config();

const commands: any[] = [];
const foldersPath: string = path.join(path.dirname("."), "src", "commands");
const commandFolders: string[] = fs.readdirSync(foldersPath);

export const deployCommands = async () => {
    for (const folder of commandFolders) {
        const commandsPath: string = path.join(foldersPath, folder);
        const commandFiles: string[] = fs
            .readdirSync(commandsPath)
            .filter((file) => file.endsWith(".ts"));

        for (const file of commandFiles) {
            const filePath: string = path.join(commandsPath, file);
            try {
                const commandModule = await import(filePath);
                const command = commandModule.default || commandModule;

                if ("data" in command && "execute" in command) {
                    commands.push(command.data.toJSON());
                } else {
                    console.log(
                        `[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`,
                    );
                }
            } catch (error) {
                console.error(
                    `[ERROR] Failed to load command at ${filePath}:`,
                    error,
                );
            }
        }
    }

    const rest: REST = new REST().setToken(process.env.DISCORD_TOKEN as string);

    try {
        console.log(
            `Started refreshing ${commands.length} application (/) commands.`,
        );

        const data: any = await rest.put(
            Routes.applicationGuildCommands(
                process.env.CLIENT_ID as Snowflake,
                process.env.GUILD_ID as Snowflake,
            ),
            { body: commands },
        );

        console.log(
            `Successfully reloaded ${data.length} application (/) commands.`,
        );
    } catch (error) {
        console.error(error);
    }
};

deployCommands();

