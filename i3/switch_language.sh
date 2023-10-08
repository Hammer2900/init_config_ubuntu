#!/bin/bash
# i3config.sh

previous_window_id=""
previous_window_properties=""

i3-msg -t subscribe -m '[ "window", "focus" ]' | while read -r event; do
    current_window_id=$(i3-msg -t get_tree | jq '.. | select(.focused?) | .id')
    current_window_properties=$(i3-msg -t get_tree | jq '.. | select(.focused?)')

    if [[ "$previous_window_id" != "$current_window_id" ]] && \
       [[ "$previous_window_properties" == "$current_window_properties" ]]; then
        echo "Same properties, do not change language."
    else
        echo "Set language to en."
        setxkbmap us
    fi

    previous_window_id="$current_window_id"
    previous_window_properties="$current_window_properties"
done
