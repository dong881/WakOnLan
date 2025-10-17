from flask import Flask, jsonify, send_file, request
import RPi.GPIO as GPIO
import subprocess
import os
import configparser
import logging
from logging.handlers import RotatingFileHandler
import time
import threading

app = Flask(__name__)

# 設定日誌
logging.basicConfig(
    handlers=[RotatingFileHandler('/var/log/dorm-control.log', maxBytes=10000, backupCount=3)],
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# 讀取設定檔
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '.env'))
TARGET_MAC = config.get('DEFAULT', 'TARGET_MAC')
TARGET_IP = "140.118.216.35"
TARGET_PORT = 3389

# GPIO 設定
GPIO_PIN = 18
BUTTON_PIN = 21  # GPIO 21 (Physical Pin 40)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # 預設接低電位

# 初始狀態
current_state = "AUTO"

# 定時器設定
scheduled_time = None
timer_enabled = False

def check_connection():
    try:
        response = subprocess.run(['nc', '-zv', '-w', '1', TARGET_IP, str(TARGET_PORT)],
                                 capture_output=True, check=False)
        return response.returncode == 0
    except Exception as e:
        logging.error(f"Connection check failed: {e}")
        return False

def control_service(action):
    try:
        subprocess.run(['sudo', 'systemctl', action, 'visiondorm.service'], check=True)
        logging.info(f"Service control: {action} successful")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Service control failed: {e}")
        return False

def control_gpio(state):
    try:
        if state == "ON":
            GPIO.output(GPIO_PIN, GPIO.HIGH)
        else:
            GPIO.output(GPIO_PIN, GPIO.LOW)
        logging.info(f"GPIO set to {state}")
    except Exception as e:
        logging.error(f"GPIO control failed: {e}")

def wake_on_lan():
    try:
        result = subprocess.run(['sudo', 'etherwake', '-i', 'eth0', TARGET_MAC], check=True, capture_output=True)
        logging.info("Wake-on-LAN signal sent successfully")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Wake-on-LAN failed: {e}")
        return False

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/state/<state>', methods=['POST'])
def set_state(state):
    global current_state
    if state not in ["ON", "OFF", "AUTO"]:
        return jsonify({"error": "Invalid state"}), 400
    current_state = state
    if state == "AUTO":
        control_service("start")
        control_gpio("OFF")
    else:
        control_service("stop")
        control_gpio(state)
    return jsonify({"status": "success", "state": state})

@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify({
        "state": current_state,
        "pc_status": check_connection()
    })

@app.route('/api/wol', methods=['POST'])
def trigger_wol():
    success = wake_on_lan()
    return jsonify({
        "status": "success" if success else "error",
        "message": "Wake-on-LAN signal sent" if success else "Wake-on-LAN failed",
        "pc_status": check_connection()
    })

@app.route('/api/status', methods=['GET'])
def check_status():
    return jsonify({
        "pc_status": check_connection()
    })

# 新增定時器路由
@app.route('/api/timer', methods=['POST'])
def set_timer():
    global scheduled_time, timer_enabled
    data = request.get_json()
    scheduled_time = data.get('time')  # e.g. "HH:MM"
    timer_enabled = data.get('enabled', False)
    return jsonify({"status": "success", "scheduled_time": scheduled_time, "timer_enabled": timer_enabled})

@app.route('/api/timer', methods=['GET'])
def get_timer():
    return jsonify({"scheduled_time": scheduled_time, "timer_enabled": timer_enabled})

# 背景執行緒，用於定時檢查時間
def schedule_checker():
    while True:
        if timer_enabled and scheduled_time:
            now = time.strftime("%H:%M")
            if now == scheduled_time:
                wake_on_lan()
                # 等待 60 秒避免在同一分鐘內多次觸發
                time.sleep(60)
        time.sleep(1)

# 背景執行緒，用於監控實體按鈕
def button_monitor():
    last_button_state = GPIO.LOW
    debounce_time = 0.05  # 50ms 防彈跳時間
    
    while True:
        button_state = GPIO.input(BUTTON_PIN)
        
        # 檢測到高電位（按鈕按下）
        if button_state == GPIO.HIGH and last_button_state == GPIO.LOW:
            time.sleep(debounce_time)  # 防彈跳延遲
            # 再次確認狀態，確保不是雜訊
            if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                logging.info("Button pressed - triggering Wake-on-LAN")
                wake_on_lan()
                # 等待按鈕釋放，避免重複觸發
                while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                    time.sleep(0.1)
        
        last_button_state = button_state
        time.sleep(0.01)  # 10ms 掃描間隔

if __name__ == '__main__':
    try:
        threading.Thread(target=schedule_checker, daemon=True).start()
        threading.Thread(target=button_monitor, daemon=True).start()
        app.run(host='0.0.0.0', port=80)
    finally:
        GPIO.cleanup()