import os
import subprocess

def main():
    print("================================================================")
    print("   SİSTEMİ STABİL VE HATASIZ HALİNE GETİRME")
    print("================================================================")

    # next.config.mjs dosyasını temizle (varsayılan haline getir)
    if os.path.exists("next.config.mjs"):
        os.remove("next.config.mjs")
        print("🧹 next.config.mjs kaldırıldı.")

    subprocess.run("git add -A", shell=True)
    subprocess.run('git commit -m "Reset: Kararsiz yapilandirmalar kaldirildi" --allow-empty', shell=True)
    subprocess.run("git push origin main", shell=True)

    print("✅ Temizlik tamamlandı. Lütfen Vercel'in yeniden derlemesini bekleyin.")

if __name__ == "__main__":
    main()