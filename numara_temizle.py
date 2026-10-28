import os
import subprocess

def clean_phone_numbers(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. API'deki "eğer boşsa bu numarayı ata" kodlarını silip boş string ('') yapar
    content = content.replace("|| '05416571469'", "|| ''")
    
    # 2. Örnek verilerdeki sabit numaraları siler
    content = content.replace("'05416571469'", "''")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ [TEMİZLENDİ] {filepath}")

def main():
    print("================================================================")
    print("   OTOMATİK NUMARA ATAMA İPTAL EDİLİYOR")
    print("================================================================")

    clean_phone_numbers("app/api/pansiyon/route.ts")
    clean_phone_numbers("app/admin/page.tsx")

    print("\n🚀 Değişiklikler Vercel'e gönderiliyor...")
    subprocess.run("npm run build", shell=True)
    subprocess.run("git add app/api/pansiyon/route.ts app/admin/page.tsx", shell=True)
    subprocess.run('git commit -m "Bos gecilen veli numaralarina otomatik numara atama sorunu kaldirildi" --allow-empty', shell=True)
    subprocess.run("git push origin main", shell=True)

    print("\n🎉 GÜNCELLEME TAMAMLANDI!")

if __name__ == "__main__":
    main()