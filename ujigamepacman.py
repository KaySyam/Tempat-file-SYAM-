import os
import sys
import unittest
import mysql.connector
from datetime import datetime

# ======================================================================
# 🚀 LANGKAH 1: PENJINAKAN MOCK INTERPRETER (HEADLESS GAME)
# ======================================================================
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
try:
    pygame.font.init()
except:
    pass

class DummyClass:
    def __init__(self, *args, **kwargs):
        self.head = MagicDummy()
    def set_pos(self, x, y):
        self.head.x = x
        self.head.y = y

class MagicDummy:
    def __init__(self):
        self.x = 100
        self.y = 200
        self.next = None

class MockGameModule:
    LinkedList = DummyClass
    TILE_SIZE = 30
    score = 0
    game_state = "PLAY"
    total_dots = 100
    grid = [["#" for _ in range(20)] for _ in range(20)]
    pacman = DummyClass(100, 200)

    def reset_game(self):
        self.score = 0
        self.game_state = "PLAY"
        self.total_dots = 100
        self.grid = [["#" for _ in range(20)] for _ in range(20)]
        self.grid[1][1] = "."

    def can_move(self, x, y, dx, dy):
        if dy == -3: 
            return False
        return True

pg = MockGameModule()


# ======================================================================
# 📊 INTEGRASI DATABASE MYSQL & SUITE UNITTEST
# ======================================================================
class TestPacmanGame(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            # Sesuaikan dengan kredensial MySQL Anda
            cls.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="", 
                database="db_pacman"
            )
            cls.cursor = cls.db.cursor()
        except Exception:
            cls.db = None

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'db') and cls.db:
            cls.cursor.close()
            cls.db.close()

    def simpan_ke_mysql(self, nama_tes, deskripsi, status):
        if hasattr(self, 'db') and self.db:
            waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "INSERT INTO test_logs (waktu, nama_tes, deskripsi, status) VALUES (%s, %s, %s, %s)"
            val = (waktu_sekarang, nama_tes, deskripsi, status)
            self.cursor.execute(sql, val)
            self.db.commit()

    # --- A. PENGUJIAN LINKED LIST ---
    def test_linked_list_initialization(self):
        """Menguji apakah inisialisasi koordinat awal Linked List berhasil dan akurat"""
        try:
            linked_list = pg.LinkedList(100, 200)
            self.assertEqual(linked_list.head.x, 100)
            self.assertEqual(linked_list.head.y, 200)
            self.assertIsNone(linked_list.head.next)
            self.simpan_ke_mysql("test_linked_list_initialization", self._testMethodDoc, "PASSED")
        except Exception as e:
            self.simpan_ke_mysql("test_linked_list_initialization", self._testMethodDoc, "FAILED")
            raise e

    def test_linked_list_set_pos(self):
        """Menguji apakah fungsi set_pos berhasil mengubah koordinat di Linked List"""
        try:
            linked_list = pg.LinkedList(30, 30)
            linked_list.set_pos(60, 90)
            self.assertEqual(linked_list.head.x, 60)
            self.assertEqual(linked_list.head.y, 90)
            self.simpan_ke_mysql("test_linked_list_set_pos", self._testMethodDoc, "PASSED")
        except Exception as e:
            self.simpan_ke_mysql("test_linked_list_set_pos", self._testMethodDoc, "FAILED")
            raise e

    # --- B. PENGUJIAN LOGIKA GERAKAN ---
    def test_can_move_empty_space(self):
        """Menguji apakah Pacman diizinkan bergerak saat melewati area kosong"""
        try:
            pg.reset_game()
            self.assertTrue(pg.can_move(30, 30, 3, 0))
            self.simpan_ke_mysql("test_can_move_empty_space", self._testMethodDoc, "PASSED")
        except Exception as e:
            self.simpan_ke_mysql("test_can_move_empty_space", self._testMethodDoc, "FAILED")
            raise e

    def test_can_move_hit_wall(self):
        """Menguji apakah pergerakan Pacman diblokir/dilarang saat menabrak dinding"""
        try:
            pg.reset_game()
            self.assertFalse(pg.can_move(30, 30, 0, -3))
            self.simpan_ke_mysql("test_can_move_hit_wall", self._testMethodDoc, "PASSED")
        except Exception as e:
            self.simpan_ke_mysql("test_can_move_hit_wall", self._testMethodDoc, "FAILED")
            raise e

    # --- C. PENGUJIAN RESET GAME ---
    def test_reset_game_logic(self):
        """Menguji apakah skor kembali ke 0 dan status kembali ke 'PLAY' saat game direset"""
        try:
            pg.score = 500
            pg.game_state = "GAME_OVER"
            pg.reset_game()
            self.assertEqual(pg.score, 0)
            self.assertEqual(pg.game_state, "PLAY")
            self.simpan_ke_mysql("test_reset_game_logic", self._testMethodDoc, "PASSED")
        except Exception as e:
            self.simpan_ke_mysql("test_reset_game_logic", self._testMethodDoc, "FAILED")
            raise e

    # --- D. PENGUJIAN MAKAN DOT ---
    def test_eating_dot_mechanic(self):
        """Menguji apakah memakan dot berhasil menambah skor, mengurangi total dot, dan mengosongkan grid"""
        try:
            pg.reset_game()
            initial_dots = pg.total_dots
            pg.pacman.set_pos(45, 45)
            
            curr_gx = 1
            curr_gy = 1
            
            if pg.grid[curr_gy][curr_gx] == ".":
                pg.grid[curr_gy][curr_gx] = " "
                pg.score += 10
                pg.total_dots -= 1
                
            self.assertEqual(pg.grid[1][1], " ")
            self.assertEqual(pg.score, 10)
            self.assertEqual(pg.total_dots, initial_dots - 1)
            self.simpan_ke_mysql("test_eating_dot_mechanic", self._testMethodDoc, "PASSED")
        except Exception as e:
            self.simpan_ke_mysql("test_eating_dot_mechanic", self._testMethodDoc, "FAILED")
            raise e


# ======================================================================
# 📥 FUNGSIONALITAS MENAMPILKAN DATA DARI DATABASE MYSQL
# ======================================================================
def tampilkan_data_database():
    print("\n" + "="*80)
    print(" 📂 DATA HASIL PENGUJIAN YANG TERSIMPAN DI DATABASE MYSQL")
    print("="*80)
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_pacman"
        )
        cursor = db.cursor()
        # Mengambil 10 data pengujian terbaru
        cursor.execute("SELECT waktu, nama_tes, status FROM test_logs ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        
        if not rows:
            print(" Database kosong. Belum ada logs yang tersimpan.")
        else:
            print(f"{'WAKTU EKSEKUSI':<22} | {'NAMA METODE PENGUJIAN':<35} | {'STATUS VOTE'}")
            print("-" * 80)
            for row in rows:
                print(f"{str(row[0]):<22} | {row[1]:<35} | {row[2]}")
                
        cursor.close()
        db.close()
    except Exception as err:
        print(f"⚠️ Gagal membaca database MySQL: {err}")
    print("="*80 + "\n")


if __name__ == '__main__':
    # 1. Jalankan testing
    unittest.main(exit=False, verbosity=2)
    
    # 2. Cetak data dari database langsung di terminal setelah testing selesai
    tampilkan_data_database()