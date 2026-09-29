# Minecraft Server Commands

## Setup

```bash
# Download server.jar and generate fabric-server-launch.jar + libraries/
java -jar fabric-installer-1.1.1.jar server -mcversion 26.3 -loader 0.19.5 -downloadMinecraft
```

## Start

```bash
# Open firewall
sudo ufw allow 25565/tcp

# Start vanilla server
java -Xmx6G -Xms2G -jar server.jar nogui

# Start modded server
java -Xmx6G -Xms2G -jar fabric-server-launch.jar nogui

## Change RAM

# Xmx -> max
# Xms -> min
```

## Stop

```bash
# Close firewall
sudo ufw delete allow 25565/tcp
```
