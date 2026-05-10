import random

class Node:
    def __init__(self, name, desc, enemy=None, item=None, weapon=None):
        self.name = name
        self.desc = desc
        self.enemy = enemy  # {'name': str, 'hp': int, 'exp': int}
        self.item = item    # {'name': str, 'heal': int}
        self.weapon = weapon # {'name': str, 'atk': int}
        self.next = None

class AdventureGame:
    def __init__(self):
        self.head = None
        self.hp = 100
        self.max_hp = 100
        self.level = 1
        self.exp = 0
        self.atk_bonus = 10
        self.weapon_name = "Tangan Kosong"

    def add_location(self, name, desc, enemy=None, item=None, weapon=None):
        new_node = Node(name, desc, enemy, item, weapon)
        if not self.head:
            self.head = new_node
        else:
            curr = self.head
            while curr.next:
                curr = curr.next
            curr.next = new_node

    def check_level_up(self):
        if self.exp >= (self.level * 50):
            self.level += 1
            self.exp = 0
            self.max_hp += 20
            self.hp = self.max_hp
            self.atk_bonus += 5
            print(f"✨ LEVEL UP! Sekarang Level {self.level}. HP & ATK meningkat!")

    def battle(self, enemy):
        print(f"⚠️ Musuh muncul: {enemy['name']} (HP: {enemy['hp']})")
        e_hp = enemy['hp']
        while e_hp > 0 and self.hp > 0:
            act = input(f"[{self.weapon_name}] Ketik 'a' untuk serang: ").lower()
            if act == 'a':
                dmg = random.randint(10, 20) + self.atk_bonus
                e_hp -= dmg
                print(f"💥 Kamu menyerang {dmg} damage!")
                if e_hp > 0:
                    e_dmg = random.randint(5, 15)
                    self.hp -= e_dmg
                    print(f"🩸 {enemy['name']} membalas! HP-mu: {self.hp}/{self.max_hp}")
        
        if self.hp > 0:
            print(f"✅ {enemy['name']} kalah! +{enemy['exp']} EXP.")
            self.exp += enemy['exp']
            self.check_level_up()
            return True
        return False

    def play(self):
        curr = self.head
        print("=== THE HERO'S JOURNEY: RPG EDITION ===")
        while curr and self.hp > 0:
            print(f"\n📍 {curr.name}\n{curr.desc}")
            
            if curr.weapon:
                print(f"⚔️ Kamu menemukan {curr.weapon['name']} (ATK +{curr.weapon['atk']})!")
                self.weapon_name = curr.weapon['name']
                self.atk_bonus += curr.weapon['atk']
            
            if curr.item:
                print(f"🧪 Kamu menemukan {curr.item['name']}! Pulih {curr.item['heal']} HP.")
                self.hp = min(self.max_hp, self.hp + curr.item['heal'])
            
            if curr.enemy:
                if not self.battle(curr.enemy):
                    print("💀 GAME OVER. Perjalanan terhenti.")
                    break
            
            curr = curr.next
            if curr: input("\nLanjut ke lokasi berikutnya... [Enter]")
        
        if self.hp > 0:
            print("\n🏆 Selamat! Kamu mencapai akhir legenda!")

# Inisialisasi Game
game = AdventureGame()
game.add_location("Hutan Mulai", "Tempat damai.", item={"name": "Ramuan Kecil", "heal": 20})
game.add_location("Gua Terang", "Ada pedang berkarat di pojok.", weapon={"name": "Pedang Karat", "atk": 15})
game.add_location("Jembatan Troll", "Troll besar menghalangi jalan.", enemy={"name": "Troll", "hp": 50, "exp": 60})
game.add_location("Kuil Tua", "Tempat sakral untuk memulihkan diri.", item={"name": "Mega Potion", "heal": 50})
game.add_location("Istana Terlarang", "Raja Iblis menunggumu!", enemy={"name": "Raja Iblis", "hp": 120, "exp": 200})

game.play()
