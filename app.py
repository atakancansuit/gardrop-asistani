import streamlit as st
import sqlite3
import os

# ==========================================
# AYARLAR VE SABİTLER
# ==========================================
# Resimlerin kaydedileceği klasör kontrolü. 
# Eğer yoksa oluşturuyoruz ki dosya kaydederken hata almayalım.
UPLOAD_FOLDER = "images"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Arayüzdeki seçim kutularında (SelectBox/MultiSelect) kullanılacak sabit listeler.
# Veri tutarlılığını sağlamak için bunları kod tarafında sabit tuttum.
TUR_LISTESI = ["Pantolon", "Tişört", "Gömlek", "Kazak", "Ceket", "Mont", "Kaban", "Ayakkabı/Bot", "Aksesuar"]
RENK_LISTESI = ["Siyah", "Beyaz", "Gri", "Mavi", "Lacivert", "Yeşil", "Kırmızı", "Bej/Krem", "Kahverengi","Haki","Sarı","Turuncu","Mor","Pembe","Taba"]
KUMAS_LISTESI = ["Keten", "Kot", "Pamuklu", "Kumaş","Pileli", "Triko","Kışlık", "İnce", "Kalın", "Deri", "Süet"]
SIKLIK_LISTESI = ["Günlük/Rahat", "Günlük Şık", "Şık/Resmi", "Gece/Davet"]

# ==========================================
# VERİTABANI BAĞLANTISI
# ==========================================
def get_db_connection():
    """
    SQLite veritabanına bağlantı oluşturur.
    row_factory kullanılarak verilerin sütun isimleriyle (dict benzeri) 
    erişilebilir olmasını sağlıyoruz.
    """
    conn = sqlite3.connect('gardrop.db')
    conn.row_factory = sqlite3.Row 
    return conn

# ==========================================
# ARAYÜZ YAPILANDIRMASI
# ==========================================
st.set_page_config(page_title="Akıllı Gardırop", page_icon="👗", layout="centered")
st.title("👗 Akıllı Gardırop Asistanı")

# Sol taraftaki navigasyon menüsü
menu = st.sidebar.selectbox("Menü", ["Kıyafet Ekle", "Gardırobum", "Kombin Yap", "Kombinlerim"])

# ==========================================
# 1. SAYFA: KIYAFET EKLE (CREATE)
# ==========================================
if menu == "Kıyafet Ekle":
    st.header("Yeni Parça Ekle")

    # Kullanıcıdan veri girişi
    tur = st.selectbox("Tür", TUR_LISTESI)
    renk = st.selectbox("Renk", RENK_LISTESI)
    kumas = st.selectbox("Kumaş", KUMAS_LISTESI)
    uploaded_file = st.file_uploader("Kıyafetin Fotoğrafını Yükle", type=["jpg", "jpeg", "png"])

    if st.button("Kaydet"):
        file_path = None 
        # Eğer resim yüklendiyse yerel klasöre kaydet
        if uploaded_file is not None:
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        # Veriyi veritabanına ekle (INSERT işlemi)
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO kiyafetler (tur, renk, kumas, foto_yolu) VALUES (?, ?, ?, ?)",
                  (tur, renk, kumas, file_path))
        conn.commit()
        conn.close()
        st.success(f"✅ {renk} {tur} başarıyla eklendi!")

# ==========================================
# 2. SAYFA: GARDIROBUM (READ, DELETE & FILTER)
# ==========================================
elif menu == "Gardırobum":
    st.header("Gardırobumdaki Parçalar")
    
    # Filtreleme Alanı (Genişletilebilir Panel)
    with st.expander("🔍 Detaylı Filtreleme", expanded=False):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            f_tur = st.multiselect("Tür Seç", TUR_LISTESI)
        with col_f2:
            f_renk = st.multiselect("Renk Seç", RENK_LISTESI)
        with col_f3:
            f_kumas = st.multiselect("Kumaş Seç", KUMAS_LISTESI)
    
    # --- Dinamik SQL Sorgusu Oluşturma ---
    # Kullanıcının seçtiği filtrelere göre WHERE koşullarını dinamik olarak ekliyoruz.
    sorgu = "SELECT * FROM kiyafetler WHERE 1=1"
    parametreler = []

    if f_tur:
        sorgu += f" AND tur IN ({','.join(['?']*len(f_tur))})"
        parametreler.extend(f_tur)
    if f_renk:
        sorgu += f" AND renk IN ({','.join(['?']*len(f_renk))})"
        parametreler.extend(f_renk)
    if f_kumas:
        sorgu += f" AND kumas IN ({','.join(['?']*len(f_kumas))})"
        parametreler.extend(f_kumas)
    
    sorgu += " ORDER BY id DESC"

    # Veriyi çek ve listele
    conn = get_db_connection()
    kiyafetler = conn.execute(sorgu, parametreler).fetchall()
    conn.close()

    st.write(f"Toplam **{len(kiyafetler)}** parça bulundu.")
    if kiyafetler:
        for k in kiyafetler:
            col1, col2 = st.columns([1, 3])
            with col1:
                # Resim var mı ve dosya yolu geçerli mi kontrolü
                if k['foto_yolu'] and os.path.exists(k['foto_yolu']):
                    st.image(k['foto_yolu'], width=100)
                else:
                    st.info("Resim Yok")
            with col2:
                st.subheader(f"{k['renk']} - {k['tur']}")
                st.write(f"**Kumaş:** {k['kumas']}")
                
                # SİLME İŞLEMİ (DELETE)
                # Her butona unique key veriyoruz.
                if st.button("🗑️ Sil", key=f"sil_kiyafet_{k['id']}"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    # 1. Kıyafeti ana tablodan sil
                    c.execute("DELETE FROM kiyafetler WHERE id = ?", (k['id'],))
                    # 2. İlişkisel bütünlüğü korumak için kombin detay tablosundan da temizle
                    c.execute("DELETE FROM kombin_detay WHERE kiyafet_id = ?", (k['id'],))
                    conn.commit()
                    conn.close()
                    st.success("Kıyafet silindi!")
                    st.rerun() # UI'ı güncelle
                
                st.divider()
    else:
        st.warning("Bu kriterlere uygun kıyafet bulunamadı.")

# ==========================================
# 3. SAYFA: KOMBİN YAP (TRANSACTIONAL INSERT)
# ==========================================
elif menu == "Kombin Yap":
    st.header("Yeni Kombin Oluştur")

    # Mevcut kıyafetleri çekiyoruz
    conn = get_db_connection()
    kiyafetler = conn.execute('SELECT * FROM kiyafetler').fetchall()
    conn.close()

    # ID eşleştirmesi için sözlük yapısı
    kiyafet_listesi = {f"{k['renk']} {k['tur']} (ID:{k['id']})": k['id'] for k in kiyafetler}
    
    with st.form("kombin_formu"):
        st.write("Kombin Detaylarını Giriniz:")
        
        col_a, col_b = st.columns(2)
        with col_a:
            kombin_adi = st.text_input("Kombin Adı", placeholder="Örn: Pazartesi Ofis...")
        with col_b:
            siklik = st.selectbox("Şıklık Derecesi", SIKLIK_LISTESI)
        
        kombin_fotosu = st.file_uploader("Kombin Fotosu", type=["jpg", "jpeg", "png"])
        secilen_isimler = st.multiselect("Kıyafetleri Seç", list(kiyafet_listesi.keys()))
        
        st.write("") 
        st.write("---") 
        submitted = st.form_submit_button("✅ Kombini Kaydet")

        if submitted:
            if secilen_isimler:
                kayit_ismi = kombin_adi if kombin_adi else "İsimsiz Kombin"
                
                # Kombin fotoğrafını kaydet
                kombin_foto_yolu = None
                if kombin_fotosu is not None:
                    kombin_foto_yolu = os.path.join(UPLOAD_FOLDER, "kombin_" + kombin_fotosu.name)
                    with open(kombin_foto_yolu, "wb") as f:
                        f.write(kombin_fotosu.getbuffer())

                conn = get_db_connection()
                c = conn.cursor()
                
                # 1. Adım: Kombin başlığını 'kombinler' tablosuna ekle
                c.execute("INSERT INTO kombinler (isim, siklik, kombin_foto_yolu) VALUES (?, ?, ?)", 
                          (kayit_ismi, siklik, kombin_foto_yolu))
                yeni_kombin_id = c.lastrowid # Yeni oluşan ID'yi al

                # 2. Adım: Seçilen parçaları 'kombin_detay' (Junction Table) tablosuna ekle
                for isim in secilen_isimler:
                    secilen_kiyafet_id = kiyafet_listesi[isim]
                    c.execute("INSERT INTO kombin_detay (kombin_id, kiyafet_id) VALUES (?, ?)", 
                              (yeni_kombin_id, secilen_kiyafet_id))
                
                conn.commit()
                conn.close()
                st.success(f"✅ '{kayit_ismi}' başarıyla oluşturuldu!")
            else:
                st.warning("⚠️ Lütfen en az bir kıyafet seçin.")

# ==========================================
# 4. SAYFA: KOMBİNLERİM (COMPLEX JOIN & AGGREGATION)
# ==========================================
elif menu == "Kombinlerim":
    st.header("Kayıtlı Kombinlerim")

    # Filtreleme Seçenekleri
    with st.expander("🔍 Kombin Ara & Filtrele", expanded=False):
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            filtre_siklik = st.multiselect("Şıklık Derecesi", SIKLIK_LISTESI)
            filtre_tur = st.multiselect("İçindeki Parça Türü", TUR_LISTESI)
        with col_k2:
            filtre_renk = st.multiselect("İçindeki Renk", RENK_LISTESI)
            filtre_kumas = st.multiselect("İçindeki Kumaş", KUMAS_LISTESI)

    conn = get_db_connection()
    # 3 Tabloyu Birleştiren SQL Sorgusu (JOIN Operasyonu)
    sorgu = """
        SELECT 
            k.id as kombin_id, k.isim as kombin_adi, k.siklik, k.kombin_foto_yolu,
            ky.tur, ky.renk, ky.foto_yolu as parca_foto, ky.kumas
        FROM kombinler k
        JOIN kombin_detay kd ON k.id = kd.kombin_id
        JOIN kiyafetler ky ON kd.kiyafet_id = ky.id
        ORDER BY k.id DESC
    """
    veriler = conn.execute(sorgu).fetchall()
    conn.close()

    # Gelen düz veriyi (Flat Data) Kombin ID'sine göre grupluyoruz (Aggregation)
    kombinler_sozlugu = {}
    for satir in veriler:
        kid = satir['kombin_id']
        if kid not in kombinler_sozlugu:
            kombinler_sozlugu[kid] = {
                "ad": satir['kombin_adi'],
                "siklik": satir['siklik'],
                "ana_foto": satir['kombin_foto_yolu'],
                "parcalar": []
            }
        kombinler_sozlugu[kid]["parcalar"].append(satir)

    # --- PYTHON TARAFINDA FİLTRELEME MANTIĞI ---
    # SQL yerine uygulama katmanında filtreleme yaparak esneklik sağlıyoruz.
    gosterilecek_kombinler = []

    for kid, detay in kombinler_sozlugu.items():
        # 1. Şıklık Filtresi
        if filtre_siklik and detay['siklik'] not in filtre_siklik: continue

        # 2. İçerik Filtreleri (Tür, Renk, Kumaş)
        # Kombinin içindeki herhangi bir parça kriteri sağlıyorsa kombini getir.
        if filtre_tur:
            parca_turleri = [p['tur'] for p in detay['parcalar']]
            if not any(t in filtre_tur for t in parca_turleri): continue

        if filtre_renk:
            parca_renkleri = [p['renk'] for p in detay['parcalar']]
            if not any(r in filtre_renk for r in parca_renkleri): continue

        if filtre_kumas:
            parca_kumaslari = [p['kumas'] for p in detay['parcalar']]
            if not any(k in filtre_kumas for k in parca_kumaslari): continue

        gosterilecek_kombinler.append((kid, detay))

    # Sonuçları Listeleme
    st.write(f"Filtreye uygun **{len(gosterilecek_kombinler)}** kombin bulundu.")

    if not gosterilecek_kombinler:
        st.info("Aradığınız kriterlere uygun kombin bulunamadı.")
    else:
        for kid, detay in gosterilecek_kombinler:
            with st.expander(f"🧥 {detay['ad']} ({detay['siklik']})", expanded=True):
                
                parca_sayisi = len(detay['parcalar'])
                cols = st.columns(parca_sayisi + 1)
                
                # --- SOL KISIM: KOMBİN FOTOSU VE UPDATE İŞLEMİ ---
                with cols[0]:
                    if detay['ana_foto'] and os.path.exists(detay['ana_foto']):
                        st.image(detay['ana_foto'], caption="Kombin", width=150)
                    else:
                        st.info("Fotoğraf Yok")
                    
                    # Fotoğraf Güncelleme (UPDATE)
                    yeni_foto = st.file_uploader("📸 Ekle/Değiştir", type=["jpg", "png"], key=f"upl_{kid}")
                    
                    if yeni_foto is not None:
                        dosya_adi = f"kombin_sonradan_{kid}_{yeni_foto.name}"
                        kayit_yolu = os.path.join(UPLOAD_FOLDER, dosya_adi)
                        with open(kayit_yolu, "wb") as f:
                            f.write(yeni_foto.getbuffer())
                        
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("UPDATE kombinler SET kombin_foto_yolu = ? WHERE id = ?", (kayit_yolu, kid))
                        conn.commit()
                        conn.close()
                        st.success("Güncellendi!")
                        st.rerun()

                # --- SAĞ KISIM: PARÇALAR (Popover ile detay gösterimi) ---
                current_col_idx = 1
                for parca in detay['parcalar']:
                    if current_col_idx < len(cols):
                        with cols[current_col_idx]:
                            foto_var = (parca['parca_foto'] and os.path.exists(parca['parca_foto']))
                            buton_metni = f"{parca['renk']}\n{parca['tur']}"
                            
                            if foto_var:
                                with st.popover(f"**{buton_metni}**"): 
                                    st.image(parca['parca_foto'], caption=parca['kumas'])
                            else:
                                st.write(buton_metni)
                        current_col_idx += 1
                
                # --- KOMBİNİ VERİTABANINDAN SİLME ---
                st.write("")
                if st.button("🗑️ Bu Kombini Sil", key=f"sil_kombin_{kid}"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    # Önce alt tablodaki (child) kayıtları siliyoruz (Cascade Delete mantığı)
                    c.execute("DELETE FROM kombin_detay WHERE kombin_id = ?", (kid,))
                    # Sonra ana kaydı siliyoruz
                    c.execute("DELETE FROM kombinler WHERE id = ?", (kid,))
                    conn.commit()
                    conn.close()
                    st.success("Kombin silindi!")
                    st.rerun()