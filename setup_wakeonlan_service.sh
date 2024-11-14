#!/bin/bash

# Automatically get the current script directory
SCRIPT_DIR=$(dirname "$(realpath "$0")")
SERVICE_FILE="/etc/systemd/system/dorm-control.service"

# Step 1: Create the systemd service file with dynamic paths
echo "Creating $SERVICE_FILE..."

sudo bash -c "cat > $SERVICE_FILE" << EOL
[Unit]
Description=Smart Dorm Control Service
After=network.target

[Service]
WorkingDirectory=/root/WakOnLan
ExecStart=/bin/bash -c "source ../VisionDetect_SmartDorm/dorm/bin/activate && python3 ./app.py"
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

# Step 2: Reload systemd, enable, and start the service
echo "Reloading systemd, enabling and starting the dorm-control service..."

sudo systemctl daemon-reload
sudo systemctl enable dorm-control.service
sudo systemctl start dorm-control.service

# Step 3: Display the service status
echo "Displaying the status of the dorm-control service..."
sudo systemctl status dorm-control.service
