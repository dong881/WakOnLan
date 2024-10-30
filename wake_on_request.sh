#!/bin/bash

# 讀取設定檔
source "$(dirname "$0")/.env"

# 使用設定檔中的 MAC 位址和通知 URL
while true; do
    { echo -ne "HTTP/1.1 200 OK\r\nContent-Length: 15\r\n\r\nProcessing..."; } | nc -l -p 80 -q 1
    if [[ $? -eq 0 ]]; then
        etherwake "$TARGET_MAC"
        if [[ $? -eq 0 ]]; then
            RESPONSE="Wake-on-LAN success"
        else
            RESPONSE="Wake-on-LAN failed"
        fi
    else
        RESPONSE="Error: Connection Failed"
    fi
    echo -ne "HTTP/1.1 200 OK\r\nContent-Length: ${#RESPONSE}\r\n\r\n$RESPONSE" | nc -l -p 80 -q 1
done