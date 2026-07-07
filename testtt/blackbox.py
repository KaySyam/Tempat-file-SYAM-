import os
import subprocess
import sys
import time
import unittest
from pathlib import Path


class BlackboxTests(unittest.TestCase):
    def test_app_can_launch_and_be_seen_by_user(self):
        """Blackbox test: menjalankan aplikasi game dan membiarkannya tampil agar pengguna dapat melihat serta memainkan."""
        workspace_root = Path(__file__).resolve().parent.parent
        app_path = workspace_root / "simplepacman.py"

        self.assertTrue(app_path.exists(), f"File aplikasi tidak ditemukan: {app_path}")

        env = os.environ.copy()
        env["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
        env["SDL_VIDEODRIVER"] = "windows"

        print("\n[Blackbox] Membuka jendela game untuk dilihat dan dimainkan...")
        process = subprocess.Popen(
            [sys.executable, str(app_path)],
            cwd=str(workspace_root),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
        )

        try:
            self.assertIsNotNone(process.pid)
            time.sleep(10)
            self.assertIsNone(process.poll(), "Aplikasi seharusnya tetap berjalan sehingga pengguna dapat melihat dan memainkan")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)

            print("[Blackbox] Sesi pengamatan selesai.")


if __name__ == "__main__":
    unittest.main(verbosity=2)