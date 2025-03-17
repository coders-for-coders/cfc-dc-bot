import {
    Client,
    Collection,
    REST,
    Routes,
    SlashCommandBuilder,
} from "discord.js";
import fs from "fs";
import path from "path";

const isProduction = process.env.NODE_ENV === "production";

export class ExtendedClient extends Client {
    public commands: Collection<string, any>;

    constructor(options: ConstructorParameters<typeof Client>[0]) {
        super(options);

        this.commands = new Collection();
    }

    public async init() {
        try {
            await this.loadEvents();
            await this.loadCommands();
            // await this.registerCommands();

            await this.login(process.env.DISCORD_TOKEN);
        } catch (err) {
            console.error("Failed to initialize bot:", err);
        }
    }

    private async loadCommands() {
        const basePath = isProduction 
        ?  path.resolve(__dirname, "..") 
        : path.join(process.cwd(), "src");
        const foldersPath = path.join(basePath, "commands");

        const slashCommands: SlashCommandBuilder[] = [];
        const commandFolders = fs.readdirSync(foldersPath);

        for (const folder of commandFolders) {
            const commandsPath = path.join(foldersPath, folder);

            const commandFiles = fs.readdirSync(commandsPath);

            for (const file of commandFiles) {
                try {
                    const filePath = path.join(commandsPath, file);
                    const commandModule = await import(filePath);
                    const command = commandModule.default || commandModule;

                    if ("data" in command && "execute" in command) {
                        this.commands.set(command.data.name, command);
                        slashCommands.push(command.data);
                        console.log(
                            `Loaded command: ${command.data.name} from ${folder}/${file}`,
                        );
                    } else {
                        console.log(
                            `[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`,
                        );
                    }
                } catch (err) {
                    console.error(
                        `Failed to load command file: ${folder}/${file}`,
                        err,
                    );
                }
            }
        }

        const rest = new REST({ version: "10" }).setToken(
            process.env.DISCORD_TOKEN as string,
        );

        try {
            const data = await rest.put(
                Routes.applicationCommands(process.env.CLIENT_ID as string),
                {
                    body: slashCommands.map((command) => command.toJSON()),
                },
            );
            console.log(
                `Successfully loaded ${
                    (data as any[]).length
                } slash command(s)`,
            );
        } catch (err) {
            console.error("Failed to register slash commands:", err);
        }
    }

    private async loadEvents() {
        const basePath = isProduction
            ?  path.resolve(__dirname, "..")
            : path.join(process.cwd(), "src");
        
        const eventsPath = path.join(basePath, "events");

        for (const folder of fs.readdirSync(eventsPath)) {
            const folderPath = path.join(eventsPath, folder);

            const eventFiles = fs.readdirSync(folderPath);

            for (const file of eventFiles) {
                try {
                    const eventPath = path.join(folderPath, file);
                    const eventModule = await import(eventPath);
                    const event = eventModule.default || eventModule;

                    if (!event.name || typeof event.execute !== "function") {
                        console.warn(
                            `Invalid event file: ${file} in ${folder}`,
                        );
                        continue;
                    }

                    if (event.once) {
                        this.once(event.name, (...args) =>
                            event.execute(...args),
                        );
                    } else {
                        this.on(event.name, (...args) =>
                            event.execute(...args),
                        );
                    }

                    console.log(
                        `Loaded event: ${event.name} from ${folder}/${file}`,
                    );
                } catch (err) {
                    console.error(
                        `Failed to load event file: ${folder}/${file}`,
                        err,
                    );
                }
            }
        }
    }
}
