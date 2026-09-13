# 📚 Kelime Widget - İngilizce-Türkçe Kelime Öğrenme Uygulaması

Masaüstünüzde çalışan, otomatik kelime gösteren şık bir öğrenme aracı!

##  Özellikler

- 🎯 **Otomatik Kelime Gösterimi**: Belirlediğiniz aralıklarla yeni kelimeler gösterir
- 🎨 **14 Farklı Tema**: Modern Koyu, Neon, Matrix, Gece Mavisi ve daha fazlası
- 🎬 **11 Animasyon Efekti**: Daktilo, Tırmanma, Süzülme, Patlama vb.
- 📝 **Hazır Kelime Listeleri**: A1, A2, TOEFL, IELTS seviyeleri
- ➕ **Kendi Kelimelerinizi Ekleyin**: CSV import/export desteği
-  **Quiz Modu**: Öğrendiklerinizi test edin
- 🖥️ **Sistem Tepsisi**: Arka planda çalışır, çift tıklayarak açın
-  **Akıllı Metin Sığdırma**: `font.measure()` ile kesin piksel hesaplaması - taşma yok!

## 📥 İndirme

[**Windows EXE İndir**](https://github.com/ERKANONER23/KelimeWidget/releases/download/v1/KelimeWidget.exe)

## 🚀 Kullanım

### İlk Çalıştırma

1. `KelimeWidget.exe` dosyasını çalıştırın
2. Widget masaüstünüzde belirecek
3. Sağ tıklayarak ayarları açın

### Temel Kullanım

- **Sağ Tık** → Ayarlar menüsü
- **Sürükle-Bırak** → Widget'ı istediğiniz yere taşıyın
- **Çift Tık** (sistem tepsisi) → Widget'ı aç/kapat

## ⚙️ Ayarlar

### Genel & Görünüm
- **Bildirim Aralığı**: 5 dakika - 1 saat arası
- **Ekranda Kalma Süresi**: 10-30 saniye
- **Animasyon**: 11 farklı efekt
- **Tema**: 14 farklı renk teması
- **Şeffaflık**: %30-100 arası
- **Boyut**: 400x160 ile 900x360 arası (2.5:1 oran sabit)

### Kelime Listeleri
- **Aktif Listeler**: Hangi listelerden kelime gösterilecek
- **Yeni Liste Ekle**: Kendi listenizi oluşturun
- **Kelime Sayıları**: Her listede kaç kelime olduğunu görün

### Kelimeler
- **Ekle/Düzenle/Sil**: Kelime yönetimi
- **CSV İçe/Dışa Aktar**: Toplu kelime ekleme/çıkarma
- **Arama**: Hızlı kelime bulma
- **Filtre**: Liste bazlı filtreleme

## 📋 CSV Formatı

Kendi kelimelerinizi eklemek için CSV dosyası:

```csv
en,tr,sentence,sentence_tr,list
apple,elma,I eat an apple.,Bir elma yerim.,Kullanıcı Listesi
book,kitap,She reads a book.,O kitap okur.,Kullanıcı Listesi
```

Sütunlar:
en: İngilizce kelime
tr: Türkçe anlamı
sentence: İngilizce örnek cümle (opsiyonel)
sentence_tr: Türkçe örnek cümle (opsiyonel)
list: Liste adı
