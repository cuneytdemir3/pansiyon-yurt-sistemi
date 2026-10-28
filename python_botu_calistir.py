import os
import subprocess
import time

def kill_old_processes():
    print("🧹 Eski bağlantılar temizleniyor...")
    subprocess.run("taskkill /F /IM node.exe", shell=True, capture_output=True)
    subprocess.run("taskkill /F /IM cloudflared.exe", shell=True, capture_output=True)
    time.sleep(1)

def start_bot_and_tunnel():
    kill_old_processes()
    
    log_file = "tunnel.log"
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
        except:
            pass

    print("🚀 WhatsApp Tüneli Açılıyor...")
    # Tüneli başlat
    os.system('start "WHATSAPP_TUNELI" /MIN cmd /c "cloudflared.exe tunnel --url http://127.0.0.1:3001 > tunnel.log 2>&1"')
    
    time.sleep(3) # Tünelin log dosyasını oluşturması için kısa bir süre bekle
    
    print("🤖 WhatsApp Botu Başlatılıyor...")
    # Botu başlat
    os.system('start "WHATSAPP_BOTU" cmd /k "node whatsapp-bot.js"')
    
    print("\n✅ İŞLEM TAMAM!")
    print("Siyah CMD ekranında 'WhatsApp Bildirim Sunucusu Hazır' yazısını gördüğünüzde giriş yapabilirsiniz.")

if __name__ == "__main__":
    start_bot_and_tunnel()