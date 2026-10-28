# 💰 Kişisel Finans Yöneticisi

Python ve CustomTkinter ile geliştirilmiş, kullanıcı dostu bir masaüstü kişisel finans takip uygulaması. Gelir-gider takibi, abonelik yönetimi, taksit hesaplama ve aylık raporlama özellikleri sunar.

## 🚀 Özellikler

- **Gelir Yönetimi:** Aylık gelir tanımlama ve güncelleme
- **Abonelik Takibi:** Netflix, Spotify gibi düzenli ödemeleri yönetme
- **Taksit Hesaplama:** Kredi ve taksitli alışverişleri takip etme
- **Gider Kayıtları:** Kategorilere ayrılmış harcama takibi
- **Detaylı Raporlama:** Aylık finansal durum analizi
- **Trend Grafikleri:** Gelir-gider trendlerini görselleştirme
- **Excel Dışa Aktarım:** Raporları Excel formatında kaydetme
- **Veri Yönetimi:** Verileri arşivleme ve sıfırlama

## 📋 Gereksinimler

- Python 3.8 veya üzeri
- `requirements.txt` dosyasındaki kütüphaneler (CustomTkinter, pandas, Matplotlib, openpyxl vb.)

## 🔧 Kurulum

Projeyi klonlayın:

```bash
git clone https://github.com/Gokturkunal/FinansalAsistan
cd FinansalAsistan
```

Sanal ortam oluşturun (önerilir):

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python -m venv venv
source venv/bin/activate
```

Gereksinimleri yükleyin:

```bash
pip install -r requirements.txt
```

## 🎮 Kullanım

Uygulamayı proje ana klasöründen başlatın:

```bash
python src/app.py
```

**İlk kullanım:**

1. **Gelir tanımlama:** Sol menüdeki "Gelir Ayarla" düğmesiyle aylık gelirinizi girin.
2. **Abonelik ekleme:** Düzenli ödemelerinizi (Netflix, Spotify vb.) ekleyin.
3. **Taksit ekleme:** Kredi veya taksitli alışverişlerinizi tanımlayın.
4. **Gider kaydetme:** Günlük harcamalarınızı kategorilere ayırarak kaydedin.
5. **Rapor görüntüleme:** Ana ekranda aylık finansal durumunuzu inceleyin.

## 📁 Proje Yapısı

```text
FinansalAsistan/
├── src/
│   ├── app.py                   # Uygulamayı başlatan dosya
│   ├── gui.py                   # Arayüz, grafikler ve uygulama akışı
│   └── database_managment.py    # SQLite veritabanı işlemleri
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

## 🎨 Tema ve Görünüm

Uygulama varsayılan olarak karanlık tema kullanır. Temayı ve renk paletini değiştirmek için `src/gui.py` dosyasının başındaki `set_appearance_mode` ve `set_default_color_theme` ayarlarını düzenleyin.

## 💾 Veritabanı

Uygulama tüm verileri bir SQLite veritabanında (`finans_yoneticisi.db`) otomatik olarak saklar. Bu dosya, uygulama ilk kez çalıştırıldığında uygulamanın çalıştırıldığı klasörde oluşturulur (yukarıdaki komutla proje ana klasöründe).

**Yedekleme:** `finans_yoneticisi.db` dosyasını düzenli olarak yedeklemeniz önerilir. Uygulamadaki "Veri Yönetimi" menüsünden arşivleme özelliğini de kullanabilirsiniz.

## 🚨 Sorun Giderme

| Sorun | Çözüm |
|---|---|
| `ModuleNotFoundError` | Tüm gereksinimlerin yüklendiğinden emin olun: `pip install -r requirements.txt` |
| Grafik veya Excel özellikleri çalışmıyor | `matplotlib`, `pandas` ve `openpyxl` kütüphanelerinin yüklü olduğunu kontrol edin. |
| Veritabanı hatası | Uygulamanın çalıştığı klasörde yazma izniniz olduğundan ve `finans_yoneticisi.db` dosyasının bozulmadığından emin olun. |

## 🤝 Katkıda Bulunma

1. Projeyi fork edin.
2. Yeni bir dal oluşturun: `git checkout -b feature/YeniOzellik`
3. Değişikliklerinizi commit edin: `git commit -m "Yeni özellik ekle"`
4. Dalınızı push edin: `git push origin feature/YeniOzellik`
5. Pull request açın.

## 📝 Lisans

Bu proje MIT lisansı ile lisanslanmıştır. Ayrıntılar için [LICENSE](LICENSE) dosyasına bakın.
