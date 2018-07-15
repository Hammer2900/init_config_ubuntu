#!/bin/bash

echo "....................................... Init git information ......................................."
git config --global user.name "Tsybulskyi Evhenyi"
git config --global user.email etsy2900@gmail.com
git config --global core.editor nano

echo "....................................... Install all programms ......................................."
sudo apt install mc fish ranger rofi compton git i3-wm i3lock i3blocks jq i3lock-fancy pcmanfm htop sakura feh python-pip lxappearance vim sublime-text skypeforlinux telegram-desktop python-dev -y
pip install pipenv

echo "...................................... Copy configs to folder ......................................"
cp -r i3/ ~/.config/
ranger --copy-config=all