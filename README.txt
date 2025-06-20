💰 Kişisel Finans Yöneticisi

Modern ve kullanıcı dostu bir kişisel finans takip uygulaması. Gelir-gider takibi, abonelik yönetimi, taksit hesaplama ve detaylı raporlama özellikleri sunar.

🚀 ÖZELLİKLER
Gelir Yönetimi: Aylık gelir tanımlama ve güncelleme

Abonelik Takibi: Netflix, Spotify gibi düzenli ödemeleri yönetme

Taksit Hesaplama: Kredi ve taksitli alışverişleri takip etme

Gider Kayıtları: Kategorize edilmiş harcama takibi

Detaylı Raporlama: Aylık finansal durum analizi

Trend Grafikleri: Gelir-gider trendlerini görselleştirme

Excel Dışa Aktarım: Raporları Excel formatında kaydetme

Veri Yönetimi: Verileri arşivleme ve sıfırlama

📋 GEREKSİNİMLER
Python 3.8 veya üzeri

requirements.txt dosyasında listelenen kütüphaneler (CustomTkinter, Pandas, Matplotlib vb.)

🔧 KURULUM
Projeyi klonlayın veya indirin:
git clone https://github.com/Gokturkunal/FinansalAsistan
cd finansal_asistan

Sanal ortam oluşturun (önerilir):

Windows için
python -m venv venv
venv\Scripts\activate

Linux/macOS için
python -m venv venv
source venv/bin/activate

Gereksinimleri requirements.txt dosyasından yükleyin:
pip install -r requirements.txt

🎮 KULLANIM
Uygulamayı başlatmak için src klasöründeki app.py dosyasını çalıştırın:
python src/app.py

İlk Kullanım:

Gelir Tanımlama: Sol menüden "Gelir Ayarla" butonuna tıklayarak aylık gelirinizi girin.

Abonelik Ekleme: Düzenli ödemelerinizi (Netflix, Spotify vb.) ekleyin.

Taksit Ekleme: Kredi veya taksitli alışverişlerinizi tanımlayın.

Gider Kaydetme: Günlük harcamalarınızı kategorilere ayırarak kaydedin.

Rapor Görüntüleme: Ana ekranda aylık finansal durumunuzu inceleyin.

📁 PROJE YAPISI
finansal_asistan/
│
├── src/
│   ├── app.py                  # Ana uygulama ve GUI mantığı
│   └── database_managment.py     # Veritabanı işlemleri sınıfı
│
├── .gitignore                  # Git tarafından izlenmeyecek dosyalar
├── LICENSE                     # Proje lisansı
├── requirements.txt            # Gerekli kütüphaneler
└── README.md                   # Bu dosya

🎨 TEMA VE GÖRÜNÜM
Uygulama varsayılan olarak karanlık tema kullanır. Temayı ve renk paletini değiştirmek için src/app.py dosyasının başındaki ayarları düzenleyin.

💾 VERİTABANI
Uygulama, tüm verileri otomatik olarak kaydetmek için bir SQLite veritabanı (finans_yoneticisi.db) kullanır. Bu dosya, uygulama ilk kez çalıştırıldığında proje ana dizininde oluşturulur.

Yedekleme:
Veritabanı dosyasını (finans_yoneticisi.db) düzenli olarak yedeklemeniz önerilir. Ayrıca, uygulama içindeki "Veri Yönetimi" menüsünden arşivleme özelliğini de kullanabilirsiniz.

🚨 SORUN GİDERME
ModuleNotFoundError hatası:
Tüm gereksinimlerin yüklendiğinden emin olun: pip install -r requirements.txt

Grafik veya Excel özellikleri çalışmıyor:
matplotlib, pandas ve openpyxl kütüphanelerinin requirements.txt içinde olduğundan ve doğru yüklendiğinden emin olun.

Veritabanı hatası:
Uygulamanın çalıştığı klasörde yazma izninizin olduğundan ve finans_yoneticisi.db dosyasının bozulmadığından emin olun.

🤝 KATKIDA BULUNMA
Projeyi fork edin.

Feature branch oluşturun (git checkout -b feature/AmazingFeature).

Değişikliklerinizi commit edin (git commit -m 'Add some AmazingFeature').

Branch'inizi push edin (git push origin feature/AmazingFeature).

Pull Request açın.

📝 LİSANS
Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için LICENSE dosyasına bakın.