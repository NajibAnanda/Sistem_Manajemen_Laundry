import tkinter as tk
from tkinter import ttk, messagebox
from . import laundry_controller
from . import service_controller
from datetime import datetime 

try:
    from tkcalendar import DateEntry
except ImportError:
    print("PERINGATAN: Library tkcalendar tidak terinstall. Filter tanggal tidak akan berfungsi.")
    print("Jalankan: pip install tkcalendar")
    DateEntry = None

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Manajemen Laundry v1.0")
        self.root.geometry("900x550") 

        print("[INFO] GUI View Dimuat...")
        
        self.selected_service_id = None
        
        self.laporan_total_pesanan_var = tk.StringVar(value="Total Pesanan: 0")
        self.laporan_total_pendapatan_var = tk.StringVar(value="Total Pendapatan: Rp 0")
        
        self.laporan_data_terfilter = []
        self.laporan_tgl_mulai_str = ""
        self.laporan_tgl_selesai_str = ""

        # --- TEMA & WARNA ---
        self.style = ttk.Style()
        self.style.theme_use('clam') 
        
        self.bg_main = "#f0f0f0" 
        self.bg_frame_light = "#e0e0e0" 
        self.bg_accent = "#d0e0f0" 
        self.text_color_primary = "#333333" 
        self.text_color_accent = "#005f99" 
        self.btn_bg = "#007bff" 
        self.btn_fg = "white" 

        self.root.configure(bg=self.bg_main)
        
        self.style.configure('TFrame', background=self.bg_main)
        self.style.configure('TNotebook', background=self.bg_main, borderwidth=0)
        self.style.configure('TNotebook.Tab', background=self.bg_frame_light, foreground=self.text_color_primary, padding=[10, 5])
        self.style.map('TNotebook.Tab', background=[('selected', self.bg_accent)], foreground=[('selected', self.text_color_accent)])
        
        self.style.configure('TLabel', background=self.bg_main, foreground=self.text_color_primary)
        self.style.configure('TLabelframe', background=self.bg_frame_light, foreground=self.text_color_primary)
        self.style.configure('TLabelframe.Label', background=self.bg_frame_light, foreground=self.text_color_primary, font=('Arial', 10, 'bold'))
        
        self.style.configure('TEntry', fieldbackground="white", foreground=self.text_color_primary)
        self.style.configure('TCombobox', fieldbackground="white", foreground=self.text_color_primary)
        
        self.style.configure('TButton', 
                             background=self.btn_bg, 
                             foreground=self.btn_fg, 
                             font=('Arial', 10, 'bold'),
                             borderwidth=0,
                             focusthickness=3,
                             focuscolor='none')
        self.style.map('TButton', 
                       background=[('active', '#0056b3')], 
                       foreground=[('active', self.btn_fg)])
                       
        self.style.configure("Treeview",
                             background="white",
                             foreground=self.text_color_primary,
                             rowheight=25,
                             fieldbackground="white")
        self.style.map('Treeview', background=[('selected', self.bg_accent)])
        self.style.configure("Treeview.Heading",
                             background=self.bg_accent,
                             foreground=self.text_color_accent,
                             font=('Arial', 10, 'bold'))
        # --- AKHIR TEMA & WARNA ---


        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab1_pesanan = ttk.Frame(self.notebook, padding=10)
        self.tab2_layanan = ttk.Frame(self.notebook, padding=10)
        self.tab3_laporan = ttk.Frame(self.notebook, padding=10)
        
        self.tab1_pesanan.configure(style='TFrame')
        self.tab2_layanan.configure(style='TFrame')
        self.tab3_laporan.configure(style='TFrame')
        
        self.notebook.add(self.tab1_pesanan, text="Pesanan")
        self.notebook.add(self.tab2_layanan, text="Layanan")
        self.notebook.add(self.tab3_laporan, text="Laporan")
        
        self._buat_tab_pesanan(self.tab1_pesanan)
        self._buat_tab_layanan(self.tab2_layanan)
        self._buat_tab_laporan(self.tab3_laporan)

        self._muat_ulang_data_treeview_pesanan() 
        self._muat_layanan_combobox()
        self._muat_ulang_data_treeview_layanan()
        
        self.notebook.bind("<<TtkNotebookTabChanged>>", self._on_tab_changed)
        
        if DateEntry is not None:
            print("[INFO] Memuat laporan harian awal...")
            self._tombol_tampilkan_laporan()

    # ===================================================================
    # --- BAGIAN 1: PEMBUATAN TAB PESANAN ---
    # ===================================================================

    def _buat_tab_pesanan(self, parent_tab):
        left_frame = ttk.Frame(parent_tab, width=280)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        right_frame = ttk.Frame(parent_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._buat_form_pesanan(left_frame)
        self._buat_aksi_pesanan(left_frame)
        self._buat_list_pesanan(right_frame)

    def _buat_form_pesanan(self, parent):
        form_frame = ttk.LabelFrame(parent, text="Formulir Pesanan")
        form_frame.pack(fill=tk.X, pady=(0, 10)) 
        form_frame.columnconfigure(0, weight=1)
        
        ttk.Label(form_frame, text="Nama Pelanggan:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_nama = ttk.Entry(form_frame) 
        self.entry_nama.grid(row=1, column=0, sticky="we", padx=10, pady=(0,5))
        
        ttk.Label(form_frame, text="No. HP:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entry_no_hp = ttk.Entry(form_frame) 
        self.entry_no_hp.grid(row=3, column=0, sticky="we", padx=10, pady=(0,5))
        
        ttk.Label(form_frame, text="Berat (Kg):").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.entry_berat = ttk.Entry(form_frame)
        self.entry_berat.grid(row=5, column=0, sticky="we", padx=10, pady=(0,5))
        
        ttk.Label(form_frame, text="Jenis Layanan:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        self.layanan_var = tk.StringVar()
        self.combo_layanan = ttk.Combobox(form_frame, textvariable=self.layanan_var, state="readonly") 
        self.combo_layanan.grid(row=7, column=0, sticky="we", padx=10, pady=(0,5))
        
        btn_tambah = ttk.Button(form_frame, text="Tambah Pesanan", command=self._tombol_tambah_pesanan)
        btn_tambah.grid(row=8, column=0, sticky="we", padx=10, pady=10)

    def _buat_aksi_pesanan(self, parent):
        action_frame = ttk.LabelFrame(parent, text="Aksi Pesanan")
        action_frame.pack(fill=tk.X, pady=10)
        
        btn_tandai_selesai = ttk.Button(action_frame, text="Tandai Selesai", command=self._tombol_selesai_pesanan) 
        btn_tandai_selesai.pack(fill=tk.X, padx=10, pady=5)
        
        btn_hapus = ttk.Button(action_frame, text="Hapus Pesanan", command=self._tombol_hapus_pesanan)
        btn_hapus.pack(fill=tk.X, padx=10, pady=5)
        
        # --- TOMBOL BARU DITAMBAHKAN ---
        btn_cetak = ttk.Button(action_frame, text="Cetak Struk", command=self._tombol_cetak_struk)
        btn_cetak.pack(fill=tk.X, padx=10, pady=(10, 5))
        # -------------------------------

    def _buat_list_pesanan(self, parent):
        list_frame = ttk.LabelFrame(parent, text="Daftar Pesanan")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "nama", "no_hp", "layanan", "berat", "total_harga", "status")
        self.tree_pesanan = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.tree_pesanan.heading("id", text="ID")
        self.tree_pesanan.heading("nama", text="Nama Pelanggan")
        self.tree_pesanan.heading("no_hp", text="No. HP") 
        self.tree_pesanan.heading("layanan", text="Layanan")
        self.tree_pesanan.heading("berat", text="Berat (Kg)")
        self.tree_pesanan.heading("total_harga", text="Total Harga")
        self.tree_pesanan.heading("status", text="Status")
        
        self.tree_pesanan.column("id", width=50, anchor=tk.CENTER)
        self.tree_pesanan.column("nama", width=140, anchor=tk.CENTER) 
        self.tree_pesanan.column("no_hp", width=100, anchor=tk.CENTER) 
        self.tree_pesanan.column("layanan", width=80, anchor=tk.CENTER)
        self.tree_pesanan.column("berat", width=60, anchor=tk.CENTER) 
        self.tree_pesanan.column("total_harga", width=100, anchor=tk.CENTER) 
        self.tree_pesanan.column("status", width=80, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_pesanan.yview)
        self.tree_pesanan.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_pesanan.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ===================================================================
    # --- BAGIAN 2: PEMBUATAN TAB LAYANAN ---
    # ===================================================================

    def _buat_tab_layanan(self, parent_tab):
        left_frame = ttk.Frame(parent_tab, width=280)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        right_frame = ttk.Frame(parent_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self._buat_crud_layanan_form(left_frame)
        self._buat_crud_layanan_list(right_frame)

    def _buat_crud_layanan_form(self, parent):
        form_frame = ttk.LabelFrame(parent, text="Formulir Layanan", padding=10)
        form_frame.pack(fill=tk.X, pady=(0, 10)) 
        form_frame.columnconfigure(0, weight=1)
        
        ttk.Label(form_frame, text="Nama Layanan:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_layanan_nama = ttk.Entry(form_frame)
        self.entry_layanan_nama.grid(row=1, column=0, sticky="we", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Harga per Kg:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_layanan_harga = ttk.Entry(form_frame)
        self.entry_layanan_harga.grid(row=3, column=0, sticky="we", padx=5, pady=5)
        
        btn_tambah = ttk.Button(form_frame, text="Tambah", command=self._tombol_layanan_tambah)
        btn_tambah.grid(row=4, column=0, sticky="we", padx=5, pady=10)
        
        btn_update = ttk.Button(form_frame, text="Update", command=self._tombol_layanan_update)
        btn_update.grid(row=5, column=0, sticky="we", padx=5, pady=5)
        
        btn_hapus = ttk.Button(form_frame, text="Hapus", command=self._tombol_layanan_hapus)
        btn_hapus.grid(row=6, column=0, sticky="we", padx=5, pady=5)
        
        btn_clear = ttk.Button(form_frame, text="Clear Form", command=self._clear_form_layanan)
        btn_clear.grid(row=7, column=0, sticky="we", padx=5, pady=10)

    def _buat_crud_layanan_list(self, parent):
        list_frame = ttk.LabelFrame(parent, text="Daftar Layanan", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "nama", "harga")
        self.tree_layanan = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.tree_layanan.heading("id", text="ID")
        self.tree_layanan.heading("nama", text="Nama Layanan")
        self.tree_layanan.heading("harga", text="Harga per Kg")
        
        self.tree_layanan.column("id", width=50, anchor=tk.CENTER)
        self.tree_layanan.column("nama", width=200, anchor=tk.CENTER)
        self.tree_layanan.column("harga", width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_layanan.yview)
        self.tree_layanan.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_layanan.pack(fill=tk.BOTH, expand=True)
        self.tree_layanan.bind("<<TreeviewSelect>>", self._saat_layanan_dipilih)
        
    # ===================================================================
    # --- BAGIAN 3: PEMBUATAN TAB LAPORAN ---
    # ===================================================================
    
    def _buat_tab_laporan(self, parent_tab):
        left_frame = ttk.Frame(parent_tab, width=280)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        right_frame = ttk.Frame(parent_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        if DateEntry is None:
            ttk.Label(left_frame, text="Error: 'tkcalendar' tidak terinstall.", foreground="red").pack(padx=10, pady=10)
            self.entry_tgl_mulai = ttk.Entry(left_frame)
            self.entry_tgl_selesai = ttk.Entry(left_frame)
        else:
            filter_frame = ttk.LabelFrame(left_frame, text="Filter Laporan", padding=10)
            filter_frame.pack(fill=tk.X, pady=(0, 10))
            filter_frame.columnconfigure(1, weight=1)
            
            ttk.Label(filter_frame, text="Tanggal Mulai:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
            self.entry_tgl_mulai = DateEntry(filter_frame, date_pattern='yyyy-mm-dd', width=15, 
                                            background=self.bg_accent, foreground=self.text_color_primary,
                                            normalbackground='white', borderwidth=2) 
            self.entry_tgl_mulai.grid(row=0, column=1, padx=5, pady=10, sticky="we")
            
            ttk.Label(filter_frame, text="Tanggal Selesai:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
            self.entry_tgl_selesai = DateEntry(filter_frame, date_pattern='yyyy-mm-dd', width=15,
                                             background=self.bg_accent, foreground=self.text_color_primary,
                                             normalbackground='white', borderwidth=2) 
            self.entry_tgl_selesai.grid(row=1, column=1, padx=5, pady=10, sticky="we")
            
            btn_laporan = ttk.Button(filter_frame, text="Tampilkan Laporan", command=self._tombol_tampilkan_laporan)
            btn_laporan.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="we")

        summary_frame = ttk.LabelFrame(left_frame, text="Ringkasan & Aksi", padding=10)
        summary_frame.pack(fill=tk.X, pady=10)
        
        lbl_total_pesanan = ttk.Label(summary_frame, textvariable=self.laporan_total_pesanan_var, 
                                     font=("Arial", 12, "bold"), foreground=self.text_color_accent, 
                                     background=self.bg_frame_light)
        lbl_total_pesanan.pack(padx=10, pady=5, anchor="w")
        
        lbl_total_pendapatan = ttk.Label(summary_frame, textvariable=self.laporan_total_pendapatan_var, 
                                        font=("Arial", 12, "bold"), foreground=self.text_color_accent, 
                                        background=self.bg_frame_light)
        lbl_total_pendapatan.pack(padx=10, pady=5, anchor="w")
        
        self.btn_cetak_pdf = ttk.Button(summary_frame, text="Cetak Laporan ke PDF", command=self._tombol_cetak_laporan, state="disabled")
        self.btn_cetak_pdf.pack(fill=tk.X, padx=10, pady=10)

        list_frame = ttk.LabelFrame(right_frame, text="Daftar Transaksi (Hasil Laporan)")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "tanggal", "nama", "layanan", "no_hp", "total")
        self.tree_laporan = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree_laporan.heading("id", text="ID")
        self.tree_laporan.heading("tanggal", text="Tanggal Masuk")
        self.tree_laporan.heading("nama", text="Nama Pelanggan")
        self.tree_laporan.heading("layanan", text="Layanan")
        self.tree_laporan.heading("no_hp", text="No. HP")
        self.tree_laporan.heading("total", text="Total Harga")
        
        self.tree_laporan.column("id", width=40, anchor=tk.CENTER)
        self.tree_laporan.column("tanggal", width=120, anchor=tk.CENTER)
        self.tree_laporan.column("nama", width=150, anchor=tk.CENTER)
        self.tree_laporan.column("layanan", width=80, anchor=tk.CENTER)
        self.tree_laporan.column("no_hp", width=100, anchor=tk.CENTER)
        self.tree_laporan.column("total", width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_laporan.yview)
        self.tree_laporan.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_laporan.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    # ===================================================================
    # --- BAGIAN 4: FUNGSI HANDLER UNTUK SEMUA TAB ---
    # ===================================================================

    # --- Handler untuk Tab 1 (Pesanan) ---
    def _muat_layanan_combobox(self):
        try:
            data_layanan = service_controller.get_semua_layanan()
            nama_layanan_list = [layanan["nama_layanan"] for layanan in data_layanan]
            self.combo_layanan['values'] = nama_layanan_list
            if nama_layanan_list:
                self.combo_layanan.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data layanan: {e}")
            
    def _get_selected_pesanan_id(self):
        try:
            selected_item = self.tree_pesanan.selection()[0] 
            item_values = self.tree_pesanan.item(selected_item, "values")
            return item_values[0]
        except IndexError:
            messagebox.showwarning("Tidak Ada Pilihan", "Silakan pilih satu pesanan dari tabel terlebih dahulu.")
            return None

    def _tombol_tambah_pesanan(self):
        nama = self.entry_nama.get()
        no_hp = self.entry_no_hp.get()
        berat = self.entry_berat.get()
        layanan = self.combo_layanan.get()
        try:
            sukses, pesan = laundry_controller.tambah_pesanan_baru(nama, berat, layanan, no_hp)
            if sukses:
                messagebox.showinfo("Sukses", pesan)
                self.entry_nama.delete(0, tk.END)
                self.entry_no_hp.delete(0, tk.END)
                self.entry_berat.delete(0, tk.END)
                if self.combo_layanan['values']: 
                    self.combo_layanan.current(0)
                self._muat_ulang_data_treeview_pesanan()
            else:
                messagebox.showwarning("Gagal", pesan)
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")

    def _tombol_selesai_pesanan(self):
        id_pesanan = self._get_selected_pesanan_id()
        if id_pesanan:
            sukses, pesan = laundry_controller.tandai_pesanan_selesai(id_pesanan)
            if sukses:
                messagebox.showinfo("Sukses", pesan)
                self._muat_ulang_data_treeview_pesanan()
            else:
                messagebox.showerror("Gagal", pesan)

    def _tombol_hapus_pesanan(self):
        id_pesanan = self._get_selected_pesanan_id()
        if id_pesanan:
            if messagebox.askyesno("Konfirmasi Hapus", f"Apakah Anda yakin ingin menghapus pesanan {id_pesanan}?"):
                sukses, pesan = laundry_controller.hapus_pesanan(id_pesanan)
                if sukses:
                    messagebox.showinfo("Sukses", pesan)
                    self._muat_ulang_data_treeview_pesanan()
                else:
                    messagebox.showerror("Gagal", pesan)

    def _muat_ulang_data_treeview_pesanan(self):
        for item in self.tree_pesanan.get_children():
            self.tree_pesanan.delete(item)
        daftar_pesanan = laundry_controller.get_semua_pesanan()
        for pesanan in daftar_pesanan:
            self.tree_pesanan.insert("", tk.END, values=(
                pesanan["id"],
                pesanan["nama"],
                pesanan.get("no_hp", "-"), 
                pesanan["layanan"],
                f"{pesanan['berat']:.1f}", 
                f"Rp {pesanan['total_harga']:,.0f}", 
                pesanan["status"]
            ))

    # --- HANDLER BARU UNTUK CETAK STRUK ---
    def _tombol_cetak_struk(self):
        print("[INFO] Tombol Cetak Struk ditekan.")
        id_pesanan = self._get_selected_pesanan_id()
        if not id_pesanan:
            return # Pesan error sdh ditangani
            
        try:
            sukses, pesan = laundry_controller.handle_cetak_struk(id_pesanan)
            if sukses:
                messagebox.showinfo("Sukses", pesan)
            else:
                messagebox.showerror("Gagal Cetak", pesan)
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")

    # --- Handler untuk Tab 2 (Layanan) ---
    def _muat_ulang_data_treeview_layanan(self):
        for item in self.tree_layanan.get_children():
            self.tree_layanan.delete(item)
        daftar_layanan = service_controller.get_semua_layanan()
        for layanan in daftar_layanan:
            self.tree_layanan.insert("", tk.END, values=(
                layanan["id_layanan"],
                layanan["nama_layanan"],
                f"Rp {layanan['harga_per_kg']:,.0f}"
            ))
        self._clear_form_layanan()
    def _saat_layanan_dipilih(self, event):
        try:
            selected_item = self.tree_layanan.selection()[0]
            item_data = self.tree_layanan.item(selected_item, "values")
            self.selected_service_id = item_data[0]
            self.entry_layanan_nama.delete(0, tk.END)
            self.entry_layanan_nama.insert(0, item_data[1])
            harga_str = item_data[2].replace("Rp ", "").replace(",", "")
            self.entry_layanan_harga.delete(0, tk.END)
            self.entry_layanan_harga.insert(0, harga_str)
        except IndexError:
            self._clear_form_layanan()
    def _clear_form_layanan(self):
        self.selected_service_id = None
        self.entry_layanan_nama.delete(0, tk.END)
        self.entry_layanan_harga.delete(0, tk.END)
        if self.tree_layanan.selection():
            self.tree_layanan.selection_remove(self.tree_layanan.selection()[0])
    def _tombol_layanan_tambah(self):
        nama = self.entry_layanan_nama.get()
        harga_str = self.entry_layanan_harga.get()
        sukses, pesan = service_controller.tambah_layanan_baru(nama, harga_str)
        if sukses:
            messagebox.showinfo("Sukses", pesan)
            self._muat_ulang_data_treeview_layanan() 
            self._muat_layanan_combobox()           
        else:
            messagebox.showwarning("Gagal", pesan) 
    def _tombol_layanan_update(self):
        if not self.selected_service_id:
            messagebox.showwarning("Gagal", "Pilih layanan dari tabel untuk di-update.")
            return
        nama = self.entry_layanan_nama.get()
        harga_str = self.entry_layanan_harga.get()
        sukses, pesan = service_controller.update_layanan(self.selected_service_id, nama, harga_str)
        if sukses:
            messagebox.showinfo("Sukses", pesan)
            self._muat_ulang_data_treeview_layanan() 
            self._muat_layanan_combobox()           
        else:
            messagebox.showwarning("Gagal", pesan) 
    def _tombol_layanan_hapus(self):
        if not self.selected_service_id:
            messagebox.showwarning("Gagal", "Pilih layanan dari tabel untuk dihapus.")
            return
        if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus layanan {self.selected_service_id}?"):
            sukses, pesan = service_controller.hapus_layanan(self.selected_service_id)
            if sukses:
                messagebox.showinfo("Sukses", pesan)
                self._muat_ulang_data_treeview_layanan() 
                self._muat_layanan_combobox()           
            else:
                messagebox.showwarning("Gagal", pesan)
                
    # ===================================================================
    # --- BAGIAN 5: HANDLER TAB 3 (LAPORAN) ---
    # ===================================================================
                
    def _on_tab_changed(self, event):
        try:
            selected_tab_index = self.notebook.index(self.notebook.select())
        except tk.TclError:
            return 

        if selected_tab_index == 2:
            print("[INFO] Tab Laporan diaktifkan, memuat ulang laporan...")
            self._tombol_tampilkan_laporan()
            
    def _muat_ulang_data_treeview_laporan(self, data_terfilter):
        for item in self.tree_laporan.get_children():
            self.tree_laporan.delete(item)
        
        for pesanan in data_terfilter:
            tanggal = datetime.strptime(pesanan["tanggal_masuk"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
            
            self.tree_laporan.insert("", tk.END, values=(
                pesanan["id"],
                tanggal,
                pesanan["nama"],
                pesanan["layanan"],
                pesanan.get("no_hp", "-"),
                f"Rp {pesanan['total_harga']:,.0f}"
            ))

    def _tombol_tampilkan_laporan(self):
        if DateEntry is None:
            messagebox.showerror("Error", "Library 'tkcalendar' belum di-install.")
            return
            
        try:
            tgl_mulai = self.entry_tgl_mulai.get_date()
            tgl_selesai = self.entry_tgl_selesai.get_date()
            
            if tgl_mulai > tgl_selesai:
                messagebox.showwarning("Input Salah", "Tanggal Mulai tidak boleh lebih akhir dari Tanggal Selesai.")
                return

            total_pesanan, total_pendapatan, data_terfilter = laundry_controller.get_laporan_by_tanggal(tgl_mulai, tgl_selesai)
            
            self.laporan_data_terfilter = data_terfilter
            self.laporan_tgl_mulai_str = tgl_mulai.strftime("%Y-%m-%d")
            self.laporan_tgl_selesai_str = tgl_selesai.strftime("%Y-%m-%d")
            
            self.laporan_total_pesanan_var.set(f"Total Pesanan: {total_pesanan}")
            self.laporan_total_pendapatan_var.set(f"Total Pendapatan: Rp {total_pendapatan:,.0f}")
            
            self._muat_ulang_data_treeview_laporan(data_terfilter)
            
            if total_pesanan > 0:
                self.btn_cetak_pdf.config(state="normal")
            else:
                self.btn_cetak_pdf.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat laporan: {e}")
            
    def _tombol_cetak_laporan(self):
        print("[INFO] Mencetak laporan ke PDF...")
        
        try:
            nama_file = laundry_controller.buat_laporan_pdf(
                self.laporan_tgl_mulai_str,
                self.laporan_tgl_selesai_str,
                self.laporan_data_terfilter,
                self.laporan_total_pesanan_var.get(),
                self.laporan_total_pendapatan_var.get()
            )
            
            messagebox.showinfo("Sukses", f"Laporan berhasil disimpan sebagai:\n{nama_file}")
            
        except ImportError as e:
             messagebox.showerror("Error", f"Gagal cetak PDF: {e}\nPastikan Anda sudah menjalankan 'pip install fpdf2'.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mencetak laporan: {e}")