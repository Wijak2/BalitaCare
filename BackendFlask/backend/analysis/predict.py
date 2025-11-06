import os
import pandas as pd
import numpy as np

def hitung_zscore(nilai, umur, sex, jenis):
    base_dir = os.path.join(os.path.dirname(__file__), 'LMS')

    nama_file = {
        ('bb', 'Laki-Laki'): 'Standar Percintiles WHO Berat Badan_Balita_0-5 Tahun_Laki-Laki.xlsx',
        ('bb', 'Perempuan'): 'Standar Percintiles WHO Berat Badan_Balita_0-5 Tahun_Perempuan.xlsx',
        ('tb', 'Laki-Laki'): 'Standar Percintiles WHO Tinggi Badan_Balita_0-5 Tahun_Laki-Laki.xlsx',
        ('tb', 'Perempuan'): 'Standar Percintiles WHO Tinggi Badan_Balita_0-5 Tahun_Perempuan.xlsx',
        ('lk', 'Laki-Laki'): 'Standar Percintiles WHO Lingkar Kepala_Balita_0-5 Tahun_Laki-Laki.xlsx',
        ('lk', 'Perempuan'): 'Standar Percintiles WHO Lingkar Kepala_Balita_0-5 Tahun_Perempuan.xlsx',
        ('lila', 'Laki-Laki'): 'Standar Percintiles WHO Lingkar Lengan_Balita_0-5 Tahun_Laki-Laki.xlsx',
        ('lila', 'Perempuan'): 'Standar Percintiles WHO Lingkar Lengan_Balita_0-5 Tahun_Perempuan.xlsx',
        ('imt', 'Laki-Laki'): 'Standar Percintiles WHO IMT_Balita_0-5 Tahun_Laki-Laki.xlsx',    
        ('imt', 'Perempuan'): 'Standar Percintiles WHO IMT_Balita_0-5 Tahun_Perempuan.xlsx'      
    }

    file_path = os.path.join(base_dir, nama_file.get((jenis, sex)))
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File LMS tidak ditemukan: {file_path}")

    df = pd.read_excel(file_path)
    df = df.sort_values(by="Month")

    if umur < df["Month"].min() or umur > df["Month"].max():
        return None  # umur di luar batas WHO

    row_bawah = df[df["Month"] <= umur].iloc[-1]
    row_atas = df[df["Month"] >= umur].iloc[0]

    if row_bawah["Month"] == row_atas["Month"]:
        L, M, S = row_bawah["L"], row_bawah["M"], row_bawah["S"]
    else:
        ratio = (umur - row_bawah["Month"]) / (row_atas["Month"] - row_bawah["Month"])
        L = row_bawah["L"] + ratio * (row_atas["L"] - row_bawah["L"])
        M = row_bawah["M"] + ratio * (row_atas["M"] - row_bawah["M"])
        S = row_bawah["S"] + ratio * (row_atas["S"] - row_bawah["S"])

    z = ((nilai / M) ** L - 1) / (L * S)
    return round(z, 2)


def kategori_zscore(z):
    """Mengembalikan kategori WHO berdasarkan nilai Z-score"""
    if z is None:
        return "-"
    if z < -3:
        return "Sangat Kurang"
    elif -3 <= z < -2:
        return "Kurang"
    elif -2 <= z <= 2:
        return "Normal"
    else:
        return "Lebih"


def assess_child_growth(sex, age_months, weight_kg, height_cm, head_circ=None, arm_circ=None):
    """
    Fungsi utama untuk menilai pertumbuhan anak berdasarkan standar WHO.
    sex: 'L' atau 'P'
    age_months: umur anak dalam bulan
    weight_kg, height_cm, head_circ, arm_circ: nilai pengukuran
    """

    hasil = {}

    # Normalisasi jenis kelamin
    sex = "Laki-Laki" if sex in ["L", "l", "Laki-Laki"] else "Perempuan"

    # Berat Badan per Umur
    z_bb = hitung_zscore(weight_kg, age_months, sex, 'bb')
    hasil['BB/U'] = {"z_score": z_bb, "kategori": kategori_zscore(z_bb)}

    # Tinggi Badan per Umur
    z_tb = hitung_zscore(height_cm, age_months, sex, 'tb')
    hasil['TB/U'] = {"z_score": z_tb, "kategori": kategori_zscore(z_tb)}

    # ✅ IMT per Umur (BMI-for-age)
    imt = weight_kg / ((height_cm / 100) ** 2) if height_cm > 0 else None
    if imt:
        z_imt = hitung_zscore(imt, age_months, sex, 'imt')
        hasil['IMT/U'] = {"z_score": z_imt, "kategori": kategori_zscore(z_imt)}
    else:
        hasil['IMT/U'] = {"z_score": None, "kategori": "-"}

    # Lingkar Kepala (opsional)
    if head_circ is not None:
        z_lk = hitung_zscore(head_circ, age_months, sex, 'lk')
        hasil['LK/U'] = {"z_score": z_lk, "kategori": kategori_zscore(z_lk)}

    # Lingkar Lengan (opsional)
    if arm_circ is not None:
        z_lila = hitung_zscore(arm_circ, age_months, sex, 'lila')
        hasil['LILA/U'] = {"z_score": z_lila, "kategori": kategori_zscore(z_lila)}

    return hasil