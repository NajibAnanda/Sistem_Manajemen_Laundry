import json
import os
from datetime import datetime

# --- LOKASI FILE ---
PESANAN_FILE = "data/pesanan.json"
LAYANAN_FILE = "data/layanan.json"

# --- DATABASE PESANAN (DI MEMORI) ---
_database_pesanan = []
_id_pesanan_terakhir = 0

# --- DATABASE LAYANAN (DI MEMORI) ---
_database_layanan = []
_id_layanan_terakhir = 0

def _init_pesanan_data():
    """ Memuat data PESANAN dari file JSON """
    global _database_pesanan, _id_pesanan_terakhir
    os.makedirs(os.path.dirname(PESANAN_FILE), exist_ok=True)
    try:
        with open(PESANAN_FILE, "r") as f:
            _database_pesanan = json.load(f)
        if _database_pesanan:
            _id_pesanan_terakhir = max(int(p["id"][3:]) for p in _database_pesanan)
        print(f"[STORAGE] Berhasil memuat {_id_pesanan_terakhir} data pesanan.")
    except (FileNotFoundError, json.JSONDecodeError):
        _database_pesanan = []
        _id_pesanan_terakhir = 0
        print(f"[STORAGE] File {PESANAN_FILE} tidak ditemukan.")

def _init_layanan_data():
    """ Memuat data LAYANAN dari file JSON """
    global _database_layanan, _id_layanan_terakhir
    os.makedirs(os.path.dirname(LAYANAN_FILE), exist_ok=True)
    try:
        with open(LAYANAN_FILE, "r") as f:
            _database_layanan = json.load(f)
        if _database_layanan:
            # Pastikan ada data sebelum mencari max
            ids = [int(p["id_layanan"][3:]) for p in _database_layanan if p["id_layanan"].startswith("SRV")]
            if ids:
                _id_layanan_terakhir = max(ids)
        print(f"[STORAGE] Berhasil memuat {len(_database_layanan)} data layanan.")
    except (FileNotFoundError, json.JSONDecodeError):
        _database_layanan = []
        _id_layanan_terakhir = 0
        print(f"[STORAGE] File {LAYANAN_FILE} tidak ditemukan.")

def _simpan_pesanan_ke_file():
    """ Menyimpan data PESANAN ke file JSON """
    global _database_pesanan
    try:
        with open(PESANAN_FILE, "w") as f:
            json.dump(_database_pesanan, f, indent=4)
        print(f"[STORAGE] Data pesanan berhasil disimpan.")
    except IOError as e:
        print(f"[STORAGE] GAGAL menyimpan data pesanan: {e}")

def _simpan_layanan_ke_file():
    """ Menyimpan data LAYANAN ke file JSON """
    global _database_layanan
    try:
        with open(LAYANAN_FILE, "w") as f:
            json.dump(_database_layanan, f, indent=4)
        print(f"[STORAGE] Data layanan berhasil disimpan.")
    except IOError as e:
        print(f"[STORAGE] GAGAL menyimpan data layanan: {e}")


# --- FUNGSI PUBLIK (PESANAN) ---

def muat_semua_pesanan():
    return _database_pesanan

def get_pesanan_by_id(id_pesanan):
    """ BARU: Mencari satu pesanan berdasarkan ID-nya """
    return next((p for p in _database_pesanan if p["id"] == id_pesanan), None)

def simpan_pesanan_baru(pesanan_dict):
    global _id_pesanan_terakhir, _database_pesanan
    _id_pesanan_terakhir += 1
    id_baru = f"LND{_id_pesanan_terakhir:03d}"
    pesanan_dict["id"] = id_baru
    pesanan_dict["status"] = "Diterima"
    _database_pesanan.append(pesanan_dict)
    _simpan_pesanan_ke_file()
    return pesanan_dict

def update_status_pesanan(id_pesanan, status_baru):
    pesanan_ditemukan = False
    for pesanan in _database_pesanan:
        if pesanan["id"] == id_pesanan:
            pesanan["status"] = status_baru
            pesanan_ditemukan = True
            break
    if pesanan_ditemukan:
        _simpan_pesanan_ke_file()
        return True
    return False

def hapus_pesanan_by_id(id_pesanan):
    pesanan_untuk_dihapus = next((p for p in _database_pesanan if p["id"] == id_pesanan), None)
    if pesanan_untuk_dihapus:
        _database_pesanan.remove(pesanan_untuk_dihapus)
        _simpan_pesanan_ke_file()
        return True
    return False

# --- FUNGSI PUBLIK (LAYANAN) ---

def muat_semua_layanan():
    return _database_layanan

def get_layanan_by_nama(nama_layanan):
    return next((s for s in _database_layanan if s["nama_layanan"] == nama_layanan), None)

def get_layanan_by_id(id_layanan):
    return next((s for s in _database_layanan if s["id_layanan"] == id_layanan), None)

def cek_layanan_duplikat(nama, harga, id_untuk_diabaikan=None):
    global _database_layanan
    for layanan in _database_layanan:
        if layanan["id_layanan"] == id_untuk_diabaikan:
            continue
        if layanan["nama_layanan"].lower() == nama.lower() and layanan["harga_per_kg"] == harga:
            return True
    return False

def simpan_layanan_baru(nama_layanan, harga_per_kg):
    global _id_layanan_terakhir, _database_layanan
    _id_layanan_terakhir += 1
    id_baru = f"SRV{_id_layanan_terakhir:03d}"
    
    layanan_baru = {
        "id_layanan": id_baru,
        "nama_layanan": nama_layanan,
        "harga_per_kg": harga_per_kg
    }
    _database_layanan.append(layanan_baru)
    _simpan_layanan_ke_file()
    return layanan_baru

def update_layanan(id_layanan, nama_layanan, harga_per_kg):
    layanan = get_layanan_by_id(id_layanan)
    if layanan:
        layanan["nama_layanan"] = nama_layanan
        layanan["harga_per_kg"] = harga_per_kg
        _simpan_layanan_ke_file()
        return True
    return False

def hapus_layanan(id_layanan):
    layanan = get_layanan_by_id(id_layanan)
    if layanan:
        _database_layanan.remove(layanan)
        _simpan_layanan_ke_file()
        return True
    return False

# --- INISIALISASI DATA ---
_init_pesanan_data()
_init_layanan_data()