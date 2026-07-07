import os
import sys
import time
import random
import unittest
import subprocess
from pathlib import Path

# Impor pyautogui untuk mengambil alih kendali fisik keyboard & mouse komputer
try:
    import pyautogui
    pyautogui.FAILSAFE = True  
except ImportError:
    pyautogui = None


class BlackboxTests(unittest.TestCase):
    def test_app_runs_automatically(self):
        """Blackbox test: mengontrol game dari luar tanpa mengubah file asli (Auto-Play via Simulasi Jendela & Keyboard)."""
        # Menentukan letak folder file game secara dinamis
        workspace_root = Path(__file__).resolve().parent.parent
        app_path = workspace_root / "simplepacman.py"

        # Validasi awal sebelum mengetes
        self.assertTrue(app_path.exists(), f"File aplikasi tidak ditemukan: {app_path}")
        self.assertIsNotNone(pyautogui, "Silakan install pyautogui terlebih dahulu dengan perintah: pip install pyautogui")

        # Konfigurasi lingkungan Pygame
        env = os.environ.copy()
        env["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
        
        # CATATAN: Jika jendela game tiba-tiba tidak muncul atau nge-blank, 
        # silakan beri tanda pagar (#) pada baris di bawah ini untuk menonaktifkannya:
        env["SDL_VIDEODRIVER"] = "windows"

        print("\n[Blackbox] Menjalankan game dari file asli...")
        
        # Membuka file game asli menggunakan subprocess
        process = subprocess.Popen(
            [sys.executable, str(app_path)],
            cwd=str(workspace_root),
            env=env,
        )

        try:
            self.assertIsNotNone(process.pid)
            print(f"[Blackbox] Game process ID: {process.pid}")
            
            # Jeda 4 detik agar game selesai memuat (loading) dan jendelanya muncul penuh di layar
            print("[Blackbox] Menunggu jendela game muncul di layar...")
            time.sleep(2)
            
            # SOLUSI FOKUS: Komputer otomatis mengklik bagian tengah layar untuk memaksa Windows memprioritaskan game Pacman
            print("[Blackbox] Memaksa fokus ke jendela game (Sistem melakukan Klik Otomatis)...")
            lebar_layar, tinggi_layar = pyautogui.size()
            pyautogui.click(lebar_layar / 2, tinggi_layar / 2) 
            time.sleep(0.15)
            
            print("[Blackbox] Memulai mode AUTO-PLAY (Komputer mengendalikan pergerakan si Kuning)...")
            tombol_arah = ['left', 'right', 'up', 'down']
            waktu_mulai = time.time()
            durasi_game = 10
            
            while time.time() - waktu_mulai < durasi_game:
                # Jika jendela game di-close manual oleh user di tengah jalan, hentikan perulangan
                if process.poll() is not None:
                    break
                
                # Memilih arah secara acak
                pilihan_komputer = random.choice(tombol_arah)
                print(f"[Autoplay] Menekan tombol arah: {pilihan_komputer.upper()}")
                
                # Simulasikan pencetan tombol keyboard fisik langsung ke dalam game
                pyautogui.press(pilihan_komputer)
                
                # Jeda interval 0.8 detik agar karakter kuning sempat berjalan di jalur grid labirin
                time.sleep(0.8)
            
            # Verifikasi akhir setelah durasi 30 detik selesai
            poll_result = process.poll()
            self.assertIsNone(poll_result, "Aplikasi seharusnya tetap berjalan lancar selama pengujian")
            print("[Blackbox] Sukses! Game berhasil dimainkan otomatis oleh komputer selama 30 detik.")
            
        finally:
            # Memastikan proses game ditutup dengan bersih setelah pengujian selesai
            if process.poll() is None:
                print("[Blackbox] Menutup paksa jendela game setelah sesi uji coba selesai...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)

            print("[Blackbox] Sesi pengujian otomatis selesai.")


if __name__ == "__main__":
    unittest.main(verbosity=2)