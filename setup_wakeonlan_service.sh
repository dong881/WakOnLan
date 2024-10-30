#!/bin/bash

# Automatically get the current script directory
SCRIPT_DIR=$(dirname "$(realpath "$0")")
SERVICE_FILE="/etc/systemd/system/wakeonlan.service"

# Step 1: Create the systemd service file with dynamic paths
echo "Creating $SERVICE_FILE..."

sudo bash -c "cat > $SERVICE_FILE" << EOL
[Unit]
Description=Wake On LAN Listener Service
After=network.target

[Service]
ExecStart=$SCRIPT_DIR/wake_on_request.sh
WorkingDirectory=$SCRIPT_DIR
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOL

# Step 2: Reload systemd, enable, and start the service
echo "Reloading systemd, enabling and starting the wakeonlan service..."

sudo systemctl daemon-reload
sudo systemctl enable wakeonlan.service
sudo systemctl start wakeonlan.service

# Step 3: Display the service status
echo "Displaying the status of the wakeonlan service..."
sudo systemctl status wakeonlan.service
