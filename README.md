# Minecraft Server

The setup of the hardcore Minecraft server I run with friends: if anyone dies, the world is deleted and everyone starts over.

## What's in here

- [`auto-death-restart.py`](auto-death-restart.py): starts the server and watches its log. When a player dies, it waits 30 seconds, stops the server, deletes the world and starts a fresh one.
- `mods/`: [Fabric API](https://modrinth.com/mod/fabric-api) and [Group Death](https://github.com/Ractouf/groupdeath), my mod that kills everyone when one player dies.
- Server settings (`server.properties`, whitelist, operators).
- [`commands.md`](commands.md): setup, start and firewall commands.

## Run it

Needs Java 25+ and Python 3.

```bash
# Download the Minecraft server and the Fabric loader
java -jar fabric-installer-1.1.1.jar server -mcversion 26.3 -loader 0.19.5 -downloadMinecraft

# Start with automatic world reset
./auto-death-restart.py
```

Type server commands in the console as usual. `stop` or Ctrl+C shuts down without resetting the world.
