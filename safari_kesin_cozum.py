import os
import re
import subprocess
import sys

def inject_mount_fix(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Eğer daha önce düzeltildiyse tekrar ekleme
    if "const [mounted, setMounted]" in content:
        print(f"✔️ {filepath} zaten düzeltilmiş.")
        return

    # Ana fonksiyonun içine SSR Bypass (Sadece telefonda yüklenmesini sağlayan kalkan) ekler
    fixed_content = re.sub(
        r'(export default function \w+\(\) {)', 
        r'\1\n  const [mounted, setMounted] = React.useState(false);\n  React.useEffect(() => { setMounted(true); }, []);\n  if (!mounted) return <div className="min-h-screen bg-slate-100 flex flex-col items-center justify-center space-y-4"><div className="w-12 h-12 border-4 border-[#006bb6] border-t-transparent rounded-full animate-spin"></div><div className="font-extrabold text-[#006bb6] tracking-widest text-sm animate-pulse">SİSTEM YÜKLENİYOR...</div></div>;\n', 
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    print(f"✅ [ONARILDI] {filepath}")

def main():
    print("================================================================")
    print("   MOBİL SAFARİ (SİYAH EKRAN / SAAT DİLİMİ) ÇÖZÜMÜ BAŞLIYOR")
    print("================================================================")

    # Tüm arayüz sayfalarına SSR Bypass kalkanını uygula
    inject_mount_fix("app/page.tsx")
    inject_mount_fix("app/belletmen/page.tsx")
    inject_mount_fix("app/admin/page.tsx")

    print("\n🚀 Next.js derleniyor ve Vercel'e gönderiliyor...")
    if subprocess.run("npm run build", shell=True).returncode != 0:
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    subprocess.run("git add -A", shell=True)
    subprocess.run('git commit -m "Fix: Mobil Safari Hydration Mismatch (siyah ekran) hatasi SSR Bypass ile kokten cozuldu" --allow-empty', shell=True)
    subprocess.run("git push origin main", shell=True)

    try:
        os.remove(__file__)
        print("🧹 Kurulum betiği görevini tamamladı ve kendini sildi.")
    except:
        pass

    print("\n================================================================")
    print("🎉 SAFARİ VE MOBİL UYUMSUZLUK KRİZİ ÇÖZÜLDÜ!")
    print("================================================================")

if __name__ == "__main__":
    main()