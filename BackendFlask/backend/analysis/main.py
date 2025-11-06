from predict import assess_child_growth

def main():
    print("=== Aplikasi Penilaian Status Gizi Anak ===")
    
    # Input data anak
    sex = input("Jenis kelamin (L/P): ").strip().upper()
    age_months = int(input("Umur (bulan): "))
    weight_kg = float(input("Berat badan (kg): "))
    height_cm = float(input("Tinggi badan (cm): "))
    
    # Opsional
    head_circ = input("Lingkar kepala (cm) [kosongkan jika tidak ada]: ")
    arm_circ = input("Lingkar lengan atas (cm) [kosongkan jika tidak ada]: ")
    head_circ = float(head_circ) if head_circ else None
    arm_circ = float(arm_circ) if arm_circ else None

    # Panggil fungsi utama
    hasil = assess_child_growth(
        sex=sex,
        age_months=age_months,
        weight_kg=weight_kg,
        height_cm=height_cm,
        head_circ=head_circ,
        arm_circ=arm_circ
    )

    print("\n=== HASIL PENILAIAN ===")
    for kategori, data in hasil.items():
        print(f"\n{kategori}:")
        for k, v in data.items():
            print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
