import streamlit as st
import mysql.connector
import pandas as pd

# Fungsi untuk menghubungkan ke database
def create_db_connection():
    return mysql.connector.connect(
        host="154.26.133.67",
        user="remotex",
        password="84pUcAHV",
        database="DUDI"
    )

# Fungsi untuk memuat data dari Excel
@st.cache_data
def load_data():
    file_path = 'Data Dukung DUDI 2024 Baru.xlsx'
    df = pd.read_excel(file_path, sheet_name=1)
    df['Kab/Kota'] = df['Kab/Kota'].str.upper()
    df['NIK'] = df['NIK'].astype(str)  # Pastikan NIK berbentuk string
    df['Nama Purnawidya'] = df['Nama Purnawidya'].str.strip()  # Bersihkan spasi tambahan
    return df

# Fungsi untuk mengecek NIK yang belum terdaftar di database
def check_unregistered_nik_and_names(kabupaten, df):
    conn = create_db_connection()
    cursor = conn.cursor()
    
    # Ambil semua NIK dan Nama dari Excel berdasarkan kabupaten yang dipilih
    filtered_df = df[df['Kab/Kota'] == kabupaten]
    nik_and_names_from_excel = filtered_df[['NIK', 'Nama Purnawidya']].values.tolist()
    nik_from_excel = [item[0] for item in nik_and_names_from_excel]
    
    # Query untuk mengambil NIK yang sudah terdaftar di database
    query = "SELECT NIK FROM data_peserta WHERE Kabupaten = %s"
    cursor.execute(query, (kabupaten,))
    registered_nik = [str(row[0]) for row in cursor.fetchall()]
    
    # Mencari NIK dan Nama yang belum terdaftar
    unregistered_data = [
        {"NIK": item[0], "Nama": item[1]}
        for item in nik_and_names_from_excel
        if item[0] not in registered_nik
    ]
    
    cursor.close()
    conn.close()
    
    return unregistered_data

# Fungsi untuk mencari nama yang sama (duplikat) per kabupaten
def find_duplicates_by_kabupaten(df, kabupaten):
    filtered_df = df[df['Kab/Kota'] == kabupaten]
    duplicates = (
        filtered_df[filtered_df.duplicated(subset=['Nama Purnawidya'], keep=False)]
        .sort_values(by=['Nama Purnawidya'])
    )
    return duplicates['Nama Purnawidya'].unique()

# Load data
df = load_data()
kabupaten_list = df['Kab/Kota'].unique()

# HEADER
st.header("Aplikasi Pendataan DUDI")

# Sidebar untuk navigasi menu
menu = st.sidebar.radio("Pilih Menu", ["Cek NIK dan Nama yang Belum Terdaftar", "Cari Nama Yang Sama per Kabupaten"])

if menu == "Cek NIK dan Nama yang Belum Terdaftar":
    st.subheader("Cek NIK dan Nama yang Belum Terdaftar")
    
    # Dropdown untuk Kabupaten
    kabupaten_choice = st.selectbox("Pilih Kabupaten", kabupaten_list, key="kabupaten_choice")
    
    # Tombol untuk mengecek NIK dan Nama yang belum terdaftar
    cek_nik_button = st.button("Cek NIK dan Nama yang Belum Terdaftar")
    if cek_nik_button:
        unregistered_data = check_unregistered_nik_and_names(kabupaten_choice, df)
        
        if unregistered_data:
            # Urutkan berdasarkan nama (A-Z)
            unregistered_data_sorted = sorted(unregistered_data, key=lambda x: x['Nama'])
            
            st.write(f"NIK dan Nama yang belum terdaftar di database untuk Kabupaten {kabupaten_choice}:")
            for item in unregistered_data_sorted:
                st.write(f"- {item['NIK']} || {item['Nama']}")
        else:
            st.write(f"Semua NIK sudah terdaftar di database untuk Kabupaten {kabupaten_choice}.")

elif menu == "Cari Nama Yang Sama per Kabupaten":
    st.subheader("Cari Nama Yang Sama per Kabupaten")
    
    # Dropdown untuk Kabupaten
    kabupaten_choice = st.selectbox("Pilih Kabupaten", kabupaten_list, key="kabupaten_duplikat")
    
    # Tombol untuk mencari nama yang sama (duplikat)
    cari_duplikat_button = st.button("Cari Nama Duplikat")
    if cari_duplikat_button:
        duplicates = find_duplicates_by_kabupaten(df, kabupaten_choice)
        
        if duplicates.size > 0:
            st.write(f"Nama yang sama (duplikat) ditemukan di Kabupaten {kabupaten_choice}:")
            for name in duplicates:
                st.write(f"- {name}")
        else:
            st.write(f"Tidak ada nama duplikat di Kabupaten {kabupaten_choice}.")

