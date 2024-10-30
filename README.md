# Wake-on-LAN Server on Raspberry Pi

此專案設置了一個簡易的 HTTP 伺服器，在接收到 GET 請求後會自動執行 Wake-on-LAN 指令來喚醒指定裝置，並發送通知請求。伺服器會持續在背景運行，並確保在崩潰或重新開機時自動重啟。

## 功能
- 監聽來自指定端口（80）的 GET 請求
- 執行 Wake-on-LAN 指令來喚醒指定 MAC 位址的裝置
- 發送通知請求並回應成功或失敗

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
sudo apt install etherwake curl netcat-openbsd
```

### 2. 設定環境變數

在專案目錄下建立 .env 檔案，並加入以下內容來配置目標裝置的 MAC 位址和通知 URL：
```
TARGET_MAC=<目標裝置的 MAC 位址，例如：xx:xx:xx:xx:xx:xx>
NOTIFY_URL=<通知 URL，例如：https://script.google.com/macros/xxx>
```
注意：為了安全性，.env 檔案不應該上傳至公開的版本控制系統，建議在專案目錄下新增 .gitignore 文件，並加入以下內容：

```
.env
```

### 3. 執行安裝腳本

在專案目錄中執行以下腳本，它將自動設置服務：
```
./setup_service.sh
```

### 4. 測試

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
