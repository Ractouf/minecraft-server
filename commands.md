# Minecraft Server Commands

## Setup

```bash
# Download server.jar and generate fabric-server-launch.jar + libraries/
java -jar fabric-installer-1.1.1.jar server -mcversion 26.3 -loader 0.19.5 -downloadMinecraft
```

## Firewall

```bash
# Open firewall
sudo ufw allow 25565/tcp

# Close firewall
sudo ufw delete allow 25565/tcp
```

## Start

```bash
# Start vanilla server
java -Xmx6G -Xms2G -jar server.jar nogui

# Start modded server
java -Xmx6G -Xms2G -jar fabric-server-launch.jar nogui

# Start auto restart hardcore server
./auto-death-restart.py
```

## LAN IP

```bash
# Linux
ip -4 -br addr

# Mac (en0 is usually Wi-Fi, try en1 if empty)
ipconfig getifaddr en0
```
