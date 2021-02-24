#!/bin/sh

updates=$(curl -s "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5" | jq '.[0].buy |tonumber');
echo "usd: $updates "

