# 🤖 KIM STORE - Discord Ticket & Transaksi Bot

Bot Discord berbasis [Nextcord](https://github.com/nextcord/nextcord) yang dirancang untuk toko digital seperti **KIM STORE**. Bot ini memiliki sistem **ticket support**, **formulir otomatis (modal)**, **logging tiket**, serta **sistem pencatatan transaksi** berbasis slash command.

---

## ✨ Fitur Utama

### 🎟️ Sistem Ticket Otomatis
- Panel interaktif dengan tombol untuk:
  - `Gamepass`
  - `Robux 5 Hari`
  - `Robux Instant`
  - `Bertanya`
- Modal form untuk input data dari pengguna.
- Channel tiket dibuat otomatis dengan permission privat.
- Logging tiket terbuka & tertutup ke channel log.

### 💰 Sistem Transaksi
- `/transaksi`: Tambahkan nominal transaksi ke pengguna tertentu. (Admin Only)
- `/total_transaksi`: Lihat total transaksi pengguna.

---

## ⚙️ Konfigurasi Awal

Edit variabel berikut di dalam file Python utama:

```python
GUILD_ID = [server_id]  # ID server Discord kamu
CATEGORY_ID = [category_channel_id]  # ID kategori tempat tiket dibuat
LOG_CHANNEL_IDS = [log_channel_id]  # ID channel log
MANAGE_TICKET_USER_IDS = [user_id_admin]  # ID admin yang dapat akses panel dan tutup tiket
```
