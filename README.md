# Arpspoof-Docker
Adding ability to block internet connection for network devices

```
version: "3.7"

services:

  arpspoof:
    image: techblog/arpspoof-docker
 #   build: https://github.com/t0mer/broadlinkmanager-docker.git
    network_mode: host #Network mode must be set to host
    container_name: arpspoof
    restart: unless-stopped
    labels:
      - "com.ouroboros.enable=true"
    volumes:
      - ./arpspoof/arpspoof.py:/opt/arpspoof/arpspoof.py
    environment:
      - ROUTER_IP= #Required Router IP
      - INTERFACE_NAME= #Required Interface name, can use this command to get it: ip route get 8.8.8.8 | sed -nr 's/.*dev ([^\ ]+).*/\1/p'
```
