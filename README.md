# Portföy Optimizasyonu ve Risk Analizi

Bu proje, BIST hisse senetleri için portföy optimizasyonu ve risk analizi yapan bir Python uygulamasıdır.

## Özellikler

- Portföy optimizasyonu (Markowitz Modern Portföy Teorisi)
- Etkin sınır analizi
- Value at Risk (VaR) hesaplaması
- Conditional Value at Risk (CVaR) hesaplaması
- Portföy bileşimi görselleştirmesi
- Detaylı raporlama

## Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/kullaniciadi/portfolio-optimization.git
cd portfolio-optimization
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac için
# veya
.venv\Scripts\activate  # Windows için
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

## Kullanım

1. `portfolio_optimization.py` dosyasını çalıştırın:
```bash
python portfolio_optimization.py
```

2. Program otomatik olarak:
   - Belirtilen hisse senetlerinin verilerini çekecek
   - Portföyü optimize edecek
   - Grafikleri oluşturacak
   - Detaylı bir rapor oluşturacak

## Çıktılar

Program çalıştığında şu dosyalar oluşturulur:
- `portfolio_report.txt`: Detaylı portföy analizi raporu
- `efficient_frontier.png`: Etkin sınır grafiği
- `portfolio_composition.png`: Portföy bileşimi pasta grafiği

## Özelleştirme

Hisse senetlerini ve tarih aralığını değiştirmek için `main()` fonksiyonundaki parametreleri düzenleyebilirsiniz:

```python
symbols = ['THYAO', 'GARAN', 'ASELS', 'EREGL', 'KCHOL']
start_date = '2023-01-01'
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.
