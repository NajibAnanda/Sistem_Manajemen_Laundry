try:
    from fpdf import FPDF
except ImportError:
    print("PERINGATAN: Library FPDF tidak terinstall. Fitur 'Cetak Struk' tidak akan berfungsi.")
    print("Jalankan: pip install fpdf2")
    FPDF = None
    
from datetime import datetime

class PDFStruk(FPDF):
    """
    Class turunan FPDF untuk membuat struk thermal 80mm.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_pesanan = "N/A" # Untuk menyimpan status

    def header(self):
        # Set font
        self.set_font('Arial', 'B', 14)
        # Judul
        self.cell(0, 8, 'LAUNDRY KITA', 0, 1, 'C')
        # Font Arial Italic 9
        self.set_font('Arial', '', 9)
        self.cell(0, 5, 'Jl. Raya Pajang No. 333, Surakarta', 0, 1, 'C')
        self.cell(0, 5, 'Telp: (021) 12345678', 0, 1, 'C')
        # Garis putus-putus
        self.set_font('Courier', '', 10)
        self.cell(0, 5, '-' * 45, 0, 1, 'C')
        self.ln(1) # Spasi

    def footer(self):
        # Posisi 2 cm dari bawah
        self.set_y(-20)
        # Garis putus-putus
        self.set_font('Courier', '', 10)
        self.cell(0, 5, '-' * 45, 0, 1, 'C')
        # Font Arial Italic 9
        self.set_font('Arial', 'I', 9)
        self.cell(0, 5, '--- Terima Kasih ---', 0, 1, 'C')
        # Status
        self.set_font('Arial', 'B', 9)
        self.cell(0, 5, f'Status Pesanan: {self.status_pesanan}', 0, 1, 'C')

    def buat_konten(self, data_pesanan):
        """
        Membuat isi konten dari struk.
        """
        self.add_page()
        # Set font ke Courier agar bisa rata kiri-kanan
        self.set_font('Courier', '', 10)
        
        # Simpan status untuk footer
        self.status_pesanan = data_pesanan.get('status', 'N/A')
        
        # --- Detail Pesanan ---
        # Menggunakan lebar halaman efektif (80mm - 10mm margin = 70mm)
        lebar_halaman = self.w - self.l_margin - self.r_margin
        
        try:
            tgl = datetime.strptime(data_pesanan["tanggal_masuk"], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        except ValueError:
            tgl = data_pesanan["tanggal_masuk"]

        self.cell(lebar_halaman * 0.3, 5, 'ID Pesanan', 0, 0)
        self.cell(0, 5, f": {data_pesanan['id']}", 0, 1)
        
        self.cell(lebar_halaman * 0.3, 5, 'Tanggal', 0, 0)
        self.cell(0, 5, f": {tgl}", 0, 1)

        self.cell(lebar_halaman * 0.3, 5, 'Pelanggan', 0, 0)
        self.cell(0, 5, f": {data_pesanan['nama']}", 0, 1)
        
        self.cell(lebar_halaman * 0.3, 5, 'No. HP', 0, 0)
        self.cell(0, 5, f": {data_pesanan.get('no_hp', '-')}", 0, 1)

        # --- Tabel Item ---
        self.ln(5)
        self.set_font('Courier', 'B', 10)
        self.cell(0, 5, 'ITEM', 0, 0, 'L')
        self.cell(0, 5, 'TOTAL', 0, 1, 'R')
        self.cell(0, 5, '-' * 45, 0, 1, 'C')
        
        self.set_font('Courier', '', 10)
        
        # Baris 1: Nama Layanan
        self.cell(0, 5, data_pesanan['layanan'], 0, 1, 'L')
        
        # Baris 2: Detail Harga
        # Hitung harga/kg (jika berat 0, hindari error)
        if data_pesanan['berat'] > 0:
            harga_per_kg = data_pesanan['total_harga'] / data_pesanan['berat']
        else:
            harga_per_kg = 0
            
        teks_detail = f"  {data_pesanan['berat']:.1f} Kg x Rp {harga_per_kg:,.0f}"
        teks_harga = f"Rp {data_pesanan['total_harga']:,.0f}"
        
        self.cell(0, 5, teks_detail, 0, 0, 'L')
        self.cell(0, 5, teks_harga, 0, 1, 'R')
        
        self.cell(0, 5, '-' * 45, 0, 1, 'C')
        self.ln(3)

        # --- Total ---
        self.set_font('Courier', 'B', 12)
        self.cell(0, 6, 'TOTAL BAYAR', 0, 0, 'L')
        self.cell(0, 6, f"Rp {data_pesanan['total_harga']:,.0f}", 0, 1, 'R')


def buat_struk_pdf(data_pesanan):
    """
    Fungsi utama yang dipanggil oleh controller untuk membuat PDF.
    """
    if FPDF is None:
        raise ImportError("Library FPDF tidak ditemukan.")
        
    if not data_pesanan:
        return None
        
    # --- PERUBAHAN UTAMA: Ukuran Kertas ---
    # Ukuran custom 80mm (lebar) x 200mm (tinggi)
    pdf = PDFStruk('P', 'mm', (80, 200))
    
    # Set margin (5mm kiri, 10mm atas, 5mm kanan)
    pdf.set_margins(5, 10, 5)
    pdf.set_auto_page_break(True, 25) # Margin bawah 2.5cm
    
    pdf.buat_konten(data_pesanan)
    
    nama_file = f"struk_{data_pesanan['id']}.pdf"
    pdf.output(nama_file)
    return nama_file