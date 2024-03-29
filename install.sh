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
wget -P /tmp/ https://github.com/Canop/broot/releases/download/v1.6.2/broot_1.6.2.zip
unzip /tmp/broot_1.6.2.zip -d /tmp/
sudo cp /tmp/build/x86_64-linux/broot /usr/bin/

echo "............................................... Ctop ..............................................."
wget -P /tmp/ https://github.com/bcicen/ctop/releases/download/v0.7.3/ctop-0.7.3-linux-amd64
sudo chmod +x /tmp/ctop-0.7.3-linux-amd64
sudo cp /tmp/ctop-0.7.3-linux-amd64 /usr/bin/ctop

echo "................................................ Lf ................................................"
wget -P /tmp/ https://github.com/gokcehan/lf/releases/download/r17/lf-linux-amd64.tar.gz
tar -xzvf /tmp/lf-linux-amd64.tar.gz -C /tmp
sudo cp /tmp/lf /usr/bin/lf

echo "............................................... Micro ..............................................."
wget -P /tmp/ https://github.com/zyedidia/micro/releases/download/v2.0.10/micro-2.0.10-linux64.tar.gz
tar -xzvf /tmp/micro-2.0.10-linux64.tar.gz -C /tmp
sudo cp /tmp/micro-2.0.10/micro /usr/bin/micro

echo "............................................. Alacritty ............................................."
wget -P /tmp/ https://github.com/alacritty/alacritty/releases/download/v0.4.1/Alacritty-v0.4.1-ubuntu_18_04_amd64.tar.gz
tar -xzvf /tmp/v0.4.1/Alacritty-v0.4.1-ubuntu_18_04_amd64.tar.gz -C /tmp
sudo cp /tmp/alacritty /usr/bin/alacritty

echo "........................................... Disc utility ..........................................."
wget -P /tmp/ https://github.com/muesli/duf/releases/download/v0.5.0/duf_0.5.0_linux_amd64.deb
sudo dpkg -i /tmp/duf_0.5.0_linux_amd64.deb

echo ".............................................. Zenith .............................................."
wget -P /tmp/ https://github.com/bvaisvil/zenith/releases/download/0.11.0/zenith.x86_64-unknown-linux-musl.tgz
tar -xzvf /tmp/zenith.x86_64-unknown-linux-musl.tgz -C /tmp
sudo cp /tmp/zenith /usr/bin/zenith

echo "................................................ Fzf ................................................"
wget -P /tmp/ https://github.com/junegunn/fzf/releases/download/0.38.0/fzf-0.38.0-linux_amd64.tar.gz
tar -xzf /tmp/fzf-0.38.0-linux_amd64.tar.gz -C /tmp/
cp /tmp/fzf /usr/bin/fzf
rm /tmp/fzf-0.38.0-linux_amd64.tar.gz
rm /tmp/fzf

echo "............................................... Navi ................................................"
wget -P /tmp/ https://github.com/denisidoro/navi/releases/download/v2.20.1/navi-v2.20.1-x86_64-unknown-linux-musl.tar.gz
tar -xzf /tmp/navi-v2.20.1-x86_64-unknown-linux-musl.tar.gz -C /tmp/
cp /tmp/navi /usr/bin/navi
rm /tmp/navi-v2.20.1-x86_64-unknown-linux-musl.tar.gz
rm /tmp/navi

echo "............................................... Dive ..............................................."
wget -P /tmp/ https://github.com/wagoodman/dive/releases/download/v0.10.0/dive_0.10.0_linux_amd64.deb
dpkg -i /tmp/dive_0.10.0_linux_amd64.deb
rm /tmp/dive_0.10.0_linux_amd64.deb