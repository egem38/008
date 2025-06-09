# Kütüphane Otomasyonu

Bu proje basit bir okul kütüphane otomasyonu örneğidir. Node.js ve Express kullanılarak REST API sağlanır ve `public/index.html` dosyası üzerinden temel bir web arayüzü sunulur.

### Çalıştırma

```bash
npm install
npm start
```

Sunucu çalıştıktan sonra `http://localhost:3000` adresinden arayüze erişebilirsiniz.

### Özellikler

- Kitap, üye ve işlem kayıtları için CRUD işlemleri
- Google Books ve OpenLibrary'den ISBN sorgulama
- Excel dosyalarından kitap, üye ve işlem içe aktarma
- İşlemleri teslim alarak iade durumunu güncelleme
- Mavi temalı arayüz ve sekmeler arasında geçiş animasyonları
