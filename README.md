# 👗 Gardırop Asistanı (Wardrobe Assistant)

Bu proje, kişisel kıyafet envanterini yönetmek, dijital ortamda kombinler oluşturmak ve gardırop analizi yapmak için geliştirilmiş bir **Python & Streamlit** uygulamasıdır. Veriler yerel veritabanında (SQLite) güvenli bir şekilde saklanır.

## Özellikler

- **CRUD İşlemleri:** Kıyafet ekleme, listeleme ve silme.
- **Dijital Kombinler:** Mevcut kıyafetlerden sürükle-bırak mantığıyla kombin oluşturma.
- **Akıllı Filtreleme:** Gardırobu renge, türe, kumaşa veya şıklık derecesine göre anlık filtreleme.
- **Veri Güvenliği:** Tüm veriler yerel `gardrop.db` SQLite veritabanında tutulur.

## Ekran Görüntüleri

### Gardırop Yönetimi

<img width="1900" height="857" alt="Ekran görüntüsü 2025-12-20 015750" src="https://github.com/user-attachments/assets/374013b8-ae7c-4220-a66b-cfc72d7081b1" />

### Kombin Oluşturma
<img width="1916" height="848" alt="Ekran görüntüsü 2025-12-20 015858" src="https://github.com/user-attachments/assets/87140e99-bb58-4b23-a4a7-2f9bc12a90ac" />

### Kombinleri görme
<img width="568" height="688" alt="Ekran görüntüsü 2025-12-20 020042" src="https://github.com/user-attachments/assets/f3546380-78e9-41fb-8049-1e68f08f8c2f" />

### Oluşturulan kombin parçalarının resimleri varsa onlar da kombin görme ekranından görülebilir
<img width="791" height="820" alt="Ekran görüntüsü 2025-12-20 020109" src="https://github.com/user-attachments/assets/99b6d2cc-79bd-4234-a286-41d935558290" />

### Filtreleme
<img width="1900" height="834" alt="Ekran görüntüsü 2025-12-20 015832" src="https://github.com/user-attachments/assets/46237aca-46ff-4623-b493-e706e443ac31" />
<img width="568" height="688" alt="Ekran görüntüsü 2025-12-20 020042" src="https://github.com/user-attachments/assets/25042c86-755d-4e88-9199-c366528aa2ad" />



## Kurulum ve Çalıştırma

Uygulamayı Local Hostta .bat dosyası olarak çalıştırıyorum. SQL tabanlı depolama yaparak kıyafet bilgilerini ve kombin bilgilerini, aynı zamanda resimlerini depoluyorum. 
