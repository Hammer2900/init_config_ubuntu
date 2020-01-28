#!/bin/bash

echo "................................................ Exa ................................................"
wget -P /tmp/ https://github.com/ogham/exa/releases/download/v0.9.0/exa-linux-x86_64-0.9.0.zip
unzip /tmp/exa-linux-x86_64-0.9.0.zip -d /tmp/
sudo cp /tmp/exa-linux-x86_64 /usr/bin/

echo "................................................ Bat ................................................"
wget -P /tmp/ https://github.com/sharkdp/bat/releases/download/v0.12.1/bat-v0.12.1-x86_64-unknown-linux-gnu.tar.gz
tar -xzvf /tmp/bat-v0.12.1-x86_64-unknown-linux-gnu.tar.gz -C /tmp
sudo cp /tmp/bat-v0.12.1-x86_64-unknown-linux-gnu/bat /usr/bin/

echo "............................................... Broot ..............................................."
wget -P /tmp/ https://github.com/Canop/broot/releases/download/v0.12.1/release.zip
unzip /tmp/release.zip -d /tmp/
sudo cp /tmp/build/x86_64-linux/broot /usr/bin/