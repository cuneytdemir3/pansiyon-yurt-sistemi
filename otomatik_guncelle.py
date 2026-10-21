import subprocess
import sys

def run_command(command, description):
    print(f"\n[İŞLEM] {description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[HATA] {description} başarısız oldu!")
        print(result.stderr)
        return False
    else:
        print(f"[BAŞARILI] {description} tamamlandı.")
        if result.stdout.strip():
            print(result.stdout.strip())
        return True

def main():
    print("==================================================")
    print("   MEB PANSİYON SİSTEMİ - OTOMATİK GÜNCELLEME BOTU")
    print("==================================================")

    # 1. Adım: Yerel Build Testi
    if not run_command("npm run build", "Next.js üretim derlemesi (build) test ediliyor"):
        print("\n❌ Build hatası tespit edildi! Lütfen önce hataları giderin, bot durduruldu.")
        sys.exit(1)

    # 2. Adım: Git Add
    if not run_command("git add .", "Değişiklikler Git'e ekleniyor"):
        sys.exit(1)

    # 3. Adım: Git Commit
    commit_msg = input("\n📝 Bu güncelleme için bir açıklama (commit mesajı) yazın: ").strip()
    if not commit_msg:
        commit_msg = "Otomatik güncelleme botu ile güncellendi"
    
    if not run_command(f'git commit -m "{commit_msg}"', "Git commit oluşturuluyor"):
        sys.exit(1)

    # 4. Adım: Git Push (GitHub & Vercel)
    if not run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor (Push)"):
        sys.exit(1)

    print("\n🎉 TEBRİKLER! Tüm güncellemeler başarıyla GitHub'a gönderildi ve Vercel yayına aldı.")
    print("==================================================")

if __name__ == "__main__":
    main()