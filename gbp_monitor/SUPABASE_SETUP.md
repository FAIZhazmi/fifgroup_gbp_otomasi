# 🚀 Supabase Setup Guide - GBP Monitor

Panduan lengkap untuk setup dan integrasi Supabase ke GBP Monitor.

---

## 📋 Prerequisites

- [x] Akun Supabase (gratis di https://supabase.com)
- [x] Project Supabase sudah dibuat
- [x] Python 3.11+ dan pip terinstall

---

## 🔧 Langkah Setup

### 1️⃣ Install Dependencies

```bash
cd gbp_monitor
pip install -r requirements.txt
```

Atau install manual:
```bash
pip install supabase
```

### 2️⃣ Get Supabase Credentials

1. Buka **Supabase Dashboard** → Pilih project Anda
2. Pergi ke **Settings** → **API**
3. Copy:
   - **Project URL** (contoh: `https://xxxxx.supabase.co`)
   - **anon public** key ATAU **service_role** key (untuk admin operations)

**⚠️ Penting:**
- Gunakan `anon` key untuk operasi read yang aman
- Gunakan `service_role` key hanya di backend untuk admin operations (jangan expose ke client!)

### 3️⃣ Konfigurasi Environment Variables

Edit file `.env` di folder `gbp_monitor`:

```env
# ── Supabase Config ───────────────────────────────────────
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
```

**Contoh lengkap:**
```env
# ── Django Core ──────────────────────────────────────────
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ── Database ─────────────────────────────────────────────
# Untuk dev, bisa pakai SQLite dulu
DATABASE_URL=sqlite:///db.sqlite3

# Atau langsung pakai Supabase PostgreSQL
# DATABASE_URL=postgresql://postgres:[PASSWORD]@db.your-project.supabase.co:5432/postgres

# ── Supabase ─────────────────────────────────────────────
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key-here
```

### 4️⃣ Buat Tabel di Supabase

1. Buka **Supabase Dashboard** → **SQL Editor**
2. Copy seluruh isi file `supabase_schema.sql`
3. Paste ke SQL Editor
4. Klik **RUN** atau tekan `Ctrl+Enter`

File `supabase_schema.sql` akan membuat tabel:
- ✅ `gbp_fetch_run` - Master table untuk tracking fetch runs
- ✅ `gbp_location_snapshot` - Snapshot lokasi per fetch
- ✅ `gbp_master_location` - Master data lokasi
- ✅ `gbp_reconciliation_job` - Job rekonsiliasi
- ✅ `gbp_reconciliation_result` - Detail hasil rekonsiliasi
- ✅ `gbp_master_data_history` - Audit trail

### 5️⃣ Test Koneksi

Jalankan management command untuk test koneksi:

```bash
python manage.py test_supabase
```

**Expected output:**
```
============================================================
🧪 Testing Supabase Connection
============================================================

1️⃣ Testing basic connection...
   ✅ Supabase client initialized

2️⃣ Testing connection with query...
   ✅ Connection test passed

3️⃣ Testing queries to tables...
   ✅ gbp_fetch_run: Query berhasil
   ✅ gbp_location_snapshot: Query berhasil
   ✅ gbp_master_location: Query berhasil
   ...

============================================================
✅ Supabase integration test completed!
============================================================
```

Untuk debug lebih detail:
```bash
python manage.py test_supabase --verbose
```

---

## 📚 Cara Menggunakan Supabase Client

### Basic Usage

```python
from gbp.supabase_client import get_supabase_client

# Get client instance
supabase = get_supabase_client()

# SELECT query
response = supabase.table('gbp_location_snapshot').select('*').limit(10).execute()
data = response.data

# INSERT
new_record = {
    'store_code': 'KS001',
    'business_name': 'Toko ABC',
    'status': 'Verified'
}
response = supabase.table('gbp_location_snapshot').insert(new_record).execute()

# UPDATE
response = supabase.table('gbp_location_snapshot')\
    .update({'status': 'Verified'})\
    .eq('store_code', 'KS001')\
    .execute()

# DELETE
response = supabase.table('gbp_location_snapshot')\
    .delete()\
    .eq('id', 123)\
    .execute()
```

### Dalam Django View

```python
from django.views import View
from django.http import JsonResponse
from gbp.supabase_client import get_supabase_client
import logging

log = logging.getLogger(__name__)

class MySupabaseView(View):
    def get(self, request):
        try:
            supabase = get_supabase_client()
            
            response = supabase.table('gbp_location_snapshot')\
                .select('*')\
                .eq('status', 'Verified')\
                .limit(50)\
                .execute()
            
            return JsonResponse({
                'success': True,
                'data': response.data
            })
            
        except Exception as exc:
            log.exception("Error querying Supabase")
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)
```

---

## 🔍 Troubleshooting

### Error: "SUPABASE_URL dan SUPABASE_KEY harus dikonfigurasi"

**Solusi:**
- Pastikan file `.env` ada di folder `gbp_monitor/`
- Cek variabel `SUPABASE_URL` dan `SUPABASE_KEY` sudah diset
- Restart Django server setelah edit `.env`

### Error: "Failed to connect to Supabase"

**Solusi:**
- Cek internet connection
- Pastikan SUPABASE_URL benar (format: `https://xxx.supabase.co`)
- Pastikan SUPABASE_KEY valid (copy dari Supabase Dashboard)
- Cek Supabase project status di dashboard (harus active)

### Error: "relation gbp_fetch_run does not exist"

**Solusi:**
- Tabel belum dibuat di Supabase
- Jalankan script `supabase_schema.sql` di SQL Editor
- Verify tabel sudah ada di **Database** → **Tables**

### Query terlalu lambat

**Solusi:**
- Add indexes di Supabase (sudah ada di `supabase_schema.sql`)
- Gunakan `.limit()` untuk batasi hasil
- Filter data dengan `.eq()`, `.gt()`, dll sebelum `.execute()`
- Check query performance di Supabase Dashboard → Logs

---

## 📖 Dokumentasi Lengkap

Baca dokumentasi detail di:
- `SUPABASE_INTEGRATION.md` - Panduan lengkap integrasi
- `views_supabase_example.py` - 10+ contoh views yang menggunakan Supabase

---

## 🔐 Security Best Practices

### ✅ DO's:
- Gunakan `service_role` key hanya di backend
- Set environment variables di `.env` (jangan commit!)
- Enable Row Level Security (RLS) untuk production
- Validate input sebelum insert/update
- Log semua error untuk debugging

### ❌ DON'Ts:
- ❌ JANGAN commit file `.env` ke git
- ❌ JANGAN expose `service_role` key di client-side
- ❌ JANGAN skip input validation
- ❌ JANGAN hardcode credentials di code

---

## 📊 Monitoring & Logs

### Check Logs di Supabase Dashboard

1. Pergi ke **Logs** → **API Logs**
2. Filter by error/warning
3. Check query performance

### Django Logs

Logs akan tersimpan di:
- Console output
- File: `gbp_monitor/logs/django.log`

---

## 🚀 Next Steps

Setelah setup berhasil:

1. ✅ Migrate data dari SQLite ke Supabase (jika ada)
2. ✅ Setup Row Level Security (RLS) policies
3. ✅ Create indexes untuk optimize query
4. ✅ Setup backup & recovery plan
5. ✅ Monitor usage & performance

---

## 📞 Support

Jika ada masalah:
1. Check error logs di Supabase Dashboard
2. Check Django logs di `logs/django.log`
3. Lihat contoh di `views_supabase_example.py`
4. Baca docs: https://supabase.com/docs/reference/python

---

## 🎉 Selamat!

Supabase sudah terintegrasi ke GBP Monitor! 🚀

Gunakan `get_supabase_client()` di views/services untuk akses database.

