from . import storage_service

def get_semua_layanan():
    """ Mengambil semua data layanan untuk ditampilkan """
    return storage_service.muat_semua_layanan()

def get_layanan_by_nama(nama_layanan):
    """ Mencari satu objek layanan berdasarkan namanya """
    return storage_service.get_layanan_by_nama(nama_layanan)

def tambah_layanan_baru(nama, harga_str):
    """ Logika untuk menambah layanan baru """
    if not nama or not harga_str:
        return False, "Nama layanan dan harga tidak boleh kosong."
        
    try:
        harga = float(harga_str)
        if harga <= 0:
            return False, "Harga harus angka positif."
    except ValueError:
        return False, "Harga harus berupa angka."
        
    if storage_service.cek_layanan_duplikat(nama, harga):
        return False, f"Gagal: Layanan '{nama}' dengan harga '{harga:,.0f}' sudah ada."
        
    storage_service.simpan_layanan_baru(nama, harga)
    return True, f"Layanan '{nama}' berhasil ditambahkan."

def update_layanan(id_layanan, nama, harga_str):
    """ Logika untuk memperbarui layanan """
    if not nama or not harga_str or not id_layanan:
        return False, "Semua data wajib diisi."
        
    try:
        harga = float(harga_str)
        if harga <= 0:
            return False, "Harga harus angka positif."
    except ValueError:
        return False, "Harga harus berupa angka."
        
    if storage_service.cek_layanan_duplikat(nama, harga, id_untuk_diabaikan=id_layanan):
        return False, f"Gagal: Layanan lain dengan nama '{nama}' dan harga '{harga:,.0f}' sudah ada."
        
    sukses = storage_service.update_layanan(id_layanan, nama, harga)
    if sukses:
        return True, "Layanan berhasil diperbarui."
    else:
        return False, "Gagal memperbarui, ID layanan tidak ditemukan."

def hapus_layanan(id_layanan):
    """ Logika untuk menghapus layanan """
    if not id_layanan:
        return False, "Tidak ada layanan yang dipilih."
        
    sukses = storage_service.hapus_layanan(id_layanan)
    if sukses:
        return True, "Layanan berhasil dihapus."
    else:
        return False, "Gagal menghapus, ID layanan tidak ditemukan."