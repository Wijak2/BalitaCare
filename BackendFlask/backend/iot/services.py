from ..extensions import db
from ..models import Pengukuran
from datetime import date

# Simpan pengukuran baru (versi batch lama)
def save_pengukuran(data):
    peng = Pengukuran(
        id_anak=int(data['id_anak']),
        id_perawat=int(data['id_perawat']) if data.get('id_perawat') else None,
        tanggal=date.today()
    )
    db.session.add(peng)
    db.session.commit()
    return peng

# Update pengukuran tertentu (satu kolom per request)
def update_pengukuran(id_pengukuran, data):
    peng = Pengukuran.query.get(id_pengukuran)
    if not peng:
        return None

    # Update hanya kolom yang dikirim
    for key, value in data.items():
        if hasattr(peng, key):
            setattr(peng, key, float(value) if key not in ["id_anak","id_perawat"] else int(value))
    db.session.commit()
    return peng
