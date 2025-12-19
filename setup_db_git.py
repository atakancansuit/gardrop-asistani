import sqlite3

def create_db():
    conn = sqlite3.connect('gardrop.db')
    c = conn.cursor()

    # Kıyafetler Tablosu
    c.execute('''
        CREATE TABLE IF NOT EXISTS kiyafetler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tur TEXT,
            renk TEXT,
            kumas TEXT,
            foto_yolu TEXT
        )
    ''')

    # Kombinler Tablosu
    c.execute('''
        CREATE TABLE IF NOT EXISTS kombinler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT,
            siklik TEXT,
            kombin_foto_yolu TEXT
        )
    ''')

    # İlişki Tablosu (Hangi kombinde hangi kıyafet var?)
    c.execute('''
        CREATE TABLE IF NOT EXISTS kombin_detay (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kombin_id INTEGER,
            kiyafet_id INTEGER,
            FOREIGN KEY(kombin_id) REFERENCES kombinler(id),
            FOREIGN KEY(kiyafet_id) REFERENCES kiyafetler(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Veritabanı (gardrop.db) başarıyla oluşturuldu/güncellendi!")

if __name__ == "__main__":
    create_db()