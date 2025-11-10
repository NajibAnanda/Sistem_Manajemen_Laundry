from . import storage_service
from . import service_controller 
from . import receipt_generator # <-- IMPOR BARU
from datetime import datetime, time

# --- Library BARU untuk PDF Laporan ---
try:
    from fpdf import FPDF
except ImportError:
    print("PERINGATAN: Library FPDF tidak terinstall. Fitur 'Cetak Laporan' tidak akan berfungsi.")
    print("Jalankan: pip install fpdf2")
    FPDF = None

def tambah_pesanan_baru(nama, berat_str, layanan_nama, no_hp):
    # (Fungsi ini tidak berubah)
    if not nama or not berat_str or not layanan_nama or not no_hp:
        return False, "Semua kolom wajib diisi."
    try:
        berat = float(berat_str)
        if berat <= 0:
            raise ValueError("Berat harus lebih dari 0")
    except ValueError:
        return False, "Berat harus angka positif."
    layanan_obj = service_controller.get_layanan_by_nama(layanan_nama)
    if not layanan_obj:
        return False, f"Jenis layanan '{layanan_nama}' tidak valid."
    harga_per_kg = layanan_obj["harga_per_kg"]
    total_harga = berat * harga_per_kg
    pesanan_baru = {
        "nama": nama, "no_hp": no_hp, "layanan": layanan_nama,
        "berat": berat, "total_harga": total_harga,
        "tanggal_masuk": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    storage_service.simpan_pesanan_baru(pesanan_baru)
    return True, "Pesanan berhasil ditambahkan."

def get_semua_pesanan():
    # (Fungsi ini tidak berubah)
    return storage_service.muat_semua_pesanan()

def tandai_pesanan_selesai(id_pesanan):
    # (Fungsi ini tidak berubah)
    sukses = storage_service.update_status_pesanan(id_pesanan, "Selesai")
    if sukses: return True, "Status pesanan berhasil diubah."
    else: return False, "Gagal mengubah status, ID tidak ditemukan."

def hapus_pesanan(id_pesanan):
    # (Fungsi ini tidak berubah)
    sukses = storage_service.hapus_pesanan_by_id(id_pesanan)
    if sukses: return True, "Pesanan berhasil dihapus."
    else: return False, "Gagal menghapus, ID tidak ditemukan."

def get_laporan_by_tanggal(tgl_mulai, tgl_selesai):
    # (Fungsi ini tidak berubah)
    print(f"[CONTROLLER] Membuat laporan dari {tgl_mulai} s/d {tgl_selesai}...")
    semua_pesanan = storage_service.muat_semua_pesanan()
    pesanan_terfilter = []
    total_pendapatan = 0.0
    dt_mulai = datetime.combine(tgl_mulai, time.min)
    dt_selesai = datetime.combine(tgl_selesai, time.max)
    
    for pesanan in semua_pesanan:
        try:
            dt_pesanan = datetime.strptime(pesanan["tanggal_masuk"], "%Y-%m-%d %H:%M:%S")
            if dt_mulai <= dt_pesanan <= dt_selesai:
                pesanan_terfilter.append(pesanan)
                total_pendapatan += pesanan["total_harga"]
        except ValueError:
            print(f"Warning: Format tanggal salah untuk pesanan {pesanan.get('id', 'N/A')}")
            
    total_pesanan = len(pesanan_terfilter)
    return total_pesanan, total_pendapatan, pesanan_terfilter

def buat_laporan_pdf(tgl_mulai_str, tgl_selesai_str, daftar_pesanan, total_pesanan_str, total_pendapatan_str):
    # (Fungsi ini tidak berubah)
    if FPDF is None:
        raise ImportError("Library FPDF tidak ditemukan. Gagal mencetak PDF.")
        
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Laporan Pendapatan Laundry", 0, 1, "C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Periode: {tgl_mulai_str} s/d {tgl_selesai_str}", 0, 1, "C")
    pdf.ln(5) 
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, total_pesanan_str, 0, 1, "L")
    pdf.cell(0, 8, total_pendapatan_str, 0, 1, "L")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(15, 10, "ID", 1, 0, "C")
    pdf.cell(30, 10, "Tanggal", 1, 0, "C")
    pdf.cell(55, 10, "Nama Pelanggan", 1, 0, "C") 
    pdf.cell(20, 10, "Layanan", 1, 0, "C")      
    pdf.cell(30, 10, "No. HP", 1, 0, "C")
    pdf.cell(40, 10, "Total Harga", 1, 1, "C")
    pdf.set_font("Arial", "", 8) 
    for pesanan in daftar_pesanan:
        tanggal = datetime.strptime(pesanan["tanggal_masuk"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
        pdf.cell(15, 8, pesanan["id"], 1, 0, "C")
        pdf.cell(30, 8, tanggal, 1, 0, "C")
        pdf.cell(55, 8, pesanan["nama"], 1, 0, "C")
        pdf.cell(20, 8, pesanan["layanan"], 1, 0, "C")
        pdf.cell(30, 8, pesanan.get("no_hp", "-"), 1, 0, "C")
        pdf.cell(40, 8, f"Rp {pesanan['total_harga']:,.0f}", 1, 1, "C")
    nama_file = f"Laporan_Laundry_{tgl_mulai_str}_sd_{tgl_selesai_str}.pdf"
    pdf.output(nama_file)
    print(f"[CONTROLLER] Laporan PDF disimpan sebagai: {nama_file}")
    
    return nama_file

# --- FUNGSI BARU UNTUK CETAK STRUK ---
def handle_cetak_struk(id_pesanan):
    """
    Mencari data pesanan dan memanggil generator PDF untuk struk.
    """
    print(f"[CONTROLLER] Menerima permintaan cetak struk untuk: {id_pesanan}")
    
    # --- DIUBAH: Memanggil fungsi baru di storage ---
    data_pesanan = storage_service.get_pesanan_by_id(id_pesanan)

    if data_pesanan is None:
        return False, "Gagal cetak: Data pesanan tidak ditemukan."
    
    try:
        nama_file = receipt_generator.buat_struk_pdf(data_pesanan)
        if nama_file:
            return True, f"Struk berhasil disimpan sebagai:\n{nama_file}"
        else:
            return False, "Gagal membuat PDF."
    except ImportError as e:
         print(f"Error cetak PDF: {e}")
         return False, "Error: Library 'fpdf2' tidak terinstall. Jalankan 'pip install fpdf2'."
    except Exception as e:
        print(f"Error cetak PDF: {e}")
        return False, f"Terjadi error saat mencetak: {e}"