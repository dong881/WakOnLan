# Wake-on-LAN Server on Raspberry Pi

此專案設置了一個簡易的 HTTP 伺服器，在接收到 GET 請求後會自動執行 Wake-on-LAN 指令來喚醒指定裝置，並發送通知請求。伺服器會持續在背景運行，並確保在崩潰或重新開機時自動重啟。

## 功能
- 監聽來自指定端口（80）的 GET 請求
- 執行 Wake-on-LAN 指令來喚醒指定 MAC 位址的裝置
- 發送通知請求並回應成功或失敗
- 支援實體按鈕觸發 WOL：接在 GPIO 21 (Pin 40) 的按鈕，當偵測到高電位時自動執行 Wake-on-LAN

## 樹莓派 GPIO 腳位接線說明

以下為 app.py 控制電燈與 WOL 按鈕所需的 GPIO 腳位配置：

| 功能 | GPIO (BCM) | 實體腳位 | 接線說明 |
|------|-----------|---------|---------|
| 電燈控制 | GPIO 18 | Pin 12 | 連接至繼電器模組的輸入端，用於控制電燈開關。繼電器的 VCC 接 5V (Pin 2/4)，GND 接地 (Pin 6/9/14/20/25/30/34/39) |
| WOL 按鈕 | GPIO 21 | Pin 40 | 連接至按鈕開關，另一端接 3.3V (Pin 1/17)。程式內部已設定下拉電阻，按下按鈕時偵測高電位觸發 WOL |
| 電源 (5V) | - | Pin 2 或 Pin 4 | 提供 5V 電源給繼電器模組 |
| 電源 (3.3V) | - | Pin 1 或 Pin 17 | 提供 3.3V 電源給按鈕開關 |
| 接地 (GND) | - | Pin 6/9/14/20/25/30/34/39 | 共用接地線 |

### 接線示意圖說明

#### 電燈控制電路 (GPIO 18)
```
Raspberry Pi Pin 12 (GPIO 18) ──> 繼電器模組 IN
Raspberry Pi Pin 2 (5V)       ──> 繼電器模組 VCC
Raspberry Pi Pin 6 (GND)      ──> 繼電器模組 GND
繼電器模組 COM                 ──> 電燈電源線
繼電器模組 NO (常開)           ──> 電燈負載線
```

#### WOL 按鈕電路 (GPIO 21)
```
Raspberry Pi Pin 40 (GPIO 21) ──> 按鈕開關一端
按鈕開關另一端                 ──> Raspberry Pi Pin 1 (3.3V)
```

**注意事項：**
- 使用 BCM 編號模式（Broadcom SOC channel）設定 GPIO
- 繼電器模組建議使用光耦隔離型，避免電氣干擾
- 按鈕開關建議使用帶防彈跳功能的開關，或在程式中已實作防彈跳延遲
- 控制高功率電燈時，請確保繼電器的額定負載足夠
- 接線時請先關閉樹莓派電源，避免短路損壞

## 系統需求
- Raspberry Pi (或其他 Linux 裝置)
- etherwake 工具
- curl 工具
- systemd 支援
- netcat (netcat-openbsd) 用於在指定的網路埠監聽請求

## 安裝步驟

### 1. 安裝所需工具
在 Raspberry Pi 上安裝 `etherwake`、`curl` 和 `netcat`：

```bash
sudo apt update
sudo apt install etherwake curl netcat-openbsd python3-venv
```

### 2. 建立並設定 Python 虛擬環境

在專案目錄下建立虛擬環境並安裝所需套件：

```bash
python3 -m venv dorm
source dorm/bin/activate
pip install -r requirements.txt
```

**注意：** 請務必先建立虛擬環境並安裝所需套件，才能正常運行此專案。

### 遵循安裝手冊完整安裝影像辨識開燈專案
```bash
cd ..
git clone https://github.com/dong881/VisionDetect_SmartDorm.git
```


### 3. 設定環境變數

在專案目錄下建立 .env 檔案，並加入以下內容來配置目標裝置的 MAC 位址和通知 URL：
```
[DEFAULT]
TARGET_MAC=<目標裝置的 MAC 位址，例如：xx:xx:xx:xx:xx:xx>
```
注意：為了安全性，.env 檔案不應該上傳至公開的版本控制系統，建議在專案目錄下新增 .gitignore 文件，並加入以下內容：

```
.env
```

### 4. 執行安裝腳本

在專案目錄中執行以下腳本，它將自動設置服務：
```
./setup_service.sh
```

### 5. 測試

從其他裝置發送 GET 請求以測試服務，例如：
```
curl http://<RaspberryPi_IP>
```
服務應回應 “Wake-on-LAN success” 或 “Wake-on-LAN failed”，並將通知請求發送至設定的 NOTIFY_URL。

### 故障排除

	•	若 systemctl 顯示服務啟動失敗，請檢查腳本的路徑和權限。
	•	確認 .env 文件中填入的 TARGET_MAC 和 NOTIFY_URL 正確無誤。
	•	若服務無法自動重啟，檢查 Restart=always 是否設定正確。

### License
```
MIT
```
