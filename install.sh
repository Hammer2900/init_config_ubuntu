#!/bin/bash

echo "................................................ Exa ................................................"
wget -P /tmp/ https://github.com/ogham/exa/releases/download/v0.9.0/exa-linux-x86_64-0.9.0.zip
unzip /tmp/exa-linux-x86_64-0.9.0.zip -d /tmp/
sudo cp /tmp/exa-linux-x86_64 /usr/bin/exa

echo "................................................ Bat ................................................"
wget -P /tmp/ https://github.com/sharkdp/bat/releases/download/v0.12.1/bat-v0.12.1-x86_64-unknown-linux-gnu.tar.gz
tar -xzvf /tmp/bat-v0.12.1-x86_64-unknown-linux-gnu.tar.gz -C /tmp
sudo cp /tmp/bat-v0.12.1-x86_64-unknown-linux-gnu/bat /usr/bin/

echo "............................................... Broot ..............................................."
wget -P /tmp/ https://github.com/Canop/broot/releases/download/v0.12.1/release.zip
unzip /tmp/release.zip -d /tmp/
sudo cp /tmp/build/x86_64-linux/broot /usr/bin/

echo "............................................... Ctop ..............................................."
wget -P /tmp/ https://github.com/bcicen/ctop/releases/download/v0.7.3/ctop-0.7.3-linux-amd64
sudo chmod +x /tmp/ctop-0.7.3-linux-amd64
sudo cp /tmp/ctop-0.7.3-linux-amd64 /usr/bin/ctop

echo "................................................ Lf ................................................"
wget -P /tmp/ https://github.com/gokcehan/lf/releases/download/r13/lf-linux-amd64.tar.gz
tar -xzvf /tmp/lf-linux-amd64.tar.gz -C /tmp
sudo cp /tmp/lf /usr/bin/lf

echo "............................................... Micro ..............................................."
wget -P /tmp/ https://github.com/zyedidia/micro/releases/download/nightly/micro-2.0.0-rc3.dev.30-linux64.tar.gz
tar -xzvf /tmp/micro-2.0.0-rc3.dev.30-linux64.tar.gz -C /tmp
sudo cp /tmp/micro-2.0.0-rc3.dev.30/micro /usr/bin/micro