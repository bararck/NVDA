# NVDA Stock Price Logger

Script sederhana untuk mengambil harga saham **NVIDIA (NVDA)** secara real-time menggunakan `yfinance`, lalu menyimpannya ke file CSV sebagai log.

## 📦 Fitur
- Mengambil data harga terbaru NVDA
- Menyimpan data ke file `nvda_prices.csv` (append, tidak overwrite)
- Menampilkan ringkasan di console
- Menyimpan data tambahan: `current_price`, `previous_close`, `day_high`, `day_low`, `volume`
- Mendukung scheduler otomatis (cek harga tiap N menit)

## ⚙️ Persyaratan
1. Pastikan sudah install **Python 3.9+**  
2. Clone / download project ini  
3. Install dependency dengan:
   ```bash
   python -m pip install -r requirements.txt

Cara Menjalankan
1. Sekali jalan (ambil data 1x)
python nvda_cekdataapi.py --once

2. Mode scheduler (otomatis tiap interval)

Jalankan script:

python nvda_cekdataapi.py


Default interval: 5 menit

Bisa ubah interval, contoh tiap 1 menit:

python nvda_cekdataapi.py --interval 1

3. Ganti simbol saham

Misalnya ambil data Apple (AAPL):

python nvda_cekdataapi.py --symbol AAPL --once

4. Hentikan program

Tekan CTRL + C di terminal.

📊 Output

Console: menampilkan ringkasan harga

CSV (nvda_prices.csv): menyimpan log dalam format:

timestamp,symbol,current_price,previous_close,day_high,day_low,volume
