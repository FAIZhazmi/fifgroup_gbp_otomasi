# Integrasi Supabase - GBP Monitor

## 📋 Overview

Dokumen ini menjelaskan cara menggunakan Supabase client yang sudah diintegrasikan ke dalam GBP Monitor Django application.

## 🔧 Setup

### 1. Install Dependencies

Pastikan package supabase-py sudah terinstall:

```bash
pip install supabase
```

### 2. Konfigurasi Environment Variables

Edit file `.env` dan tambahkan:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
```

### 3. Verifikasi Konfigurasi

File yang sudah dikonfigurasi:
- ✅ `.env` - Environment variables
- ✅ `settings.py` - Django settings dengan SUPABASE_URL dan SUPABASE_KEY
- ✅ `supabase_client.py` - Supabase client initialization
- ✅ `views.py` - Import supabase_client

## 📝 Struktur Tabel Supabase

Pastikan tabel-tabel berikut sudah dibuat di Supabase SQL Editor:

```sql
-- Contoh tabel yang mungkin dibutuhkan
CREATE TABLE IF NOT EXISTS gbp_fetch_run (
    id BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    total_records INT,
    status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS gbp_location_snapshot (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT REFERENCES gbp_fetch_run(id),
    store_code VARCHAR(255),
    business_name VARCHAR(500),
    location_name VARCHAR(500),
    status VARCHAR(100),
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tambahkan index untuk performa
CREATE INDEX idx_snapshot_run_id ON gbp_location_snapshot(run_id);
CREATE INDEX idx_snapshot_store_code ON gbp_location_snapshot(store_code);
CREATE INDEX idx_snapshot_status ON gbp_location_snapshot(status);
```

## 🚀 Cara Penggunaan

### 1. Import Supabase Client

```python
from gbp.supabase_client import get_supabase_client
```

### 2. Contoh Query - SELECT

```python
# Get Supabase client
supabase = get_supabase_client()

# Select semua data dari tabel
response = supabase.table('gbp_fetch_run').select('*').execute()
data = response.data

# Select dengan filter
response = supabase.table('gbp_location_snapshot')\
    .select('*')\
    .eq('status', 'Verified')\
    .limit(10)\
    .execute()
```

### 3. Contoh Query - INSERT

```python
supabase = get_supabase_client()

# Insert single record
data = {
    'store_code': 'KS001',
    'business_name': 'Toko ABC',
    'status': 'Verified'
}
response = supabase.table('gbp_location_snapshot').insert(data).execute()

# Insert multiple records
data_list = [
    {'store_code': 'KS001', 'business_name': 'Toko A'},
    {'store_code': 'KS002', 'business_name': 'Toko B'},
]
response = supabase.table('gbp_location_snapshot').insert(data_list).execute()
```

### 4. Contoh Query - UPDATE

```python
supabase = get_supabase_client()

# Update by ID
response = supabase.table('gbp_location_snapshot')\
    .update({'status': 'Verified'})\
    .eq('id', 123)\
    .execute()

# Update multiple records
response = supabase.table('gbp_location_snapshot')\
    .update({'status': 'Need Verification'})\
    .eq('store_code', 'KS001')\
    .execute()
```

### 5. Contoh Query - DELETE

```python
supabase = get_supabase_client()

# Delete by ID
response = supabase.table('gbp_location_snapshot')\
    .delete()\
    .eq('id', 123)\
    .execute()
```

### 6. Contoh Query dengan JOIN dan Filter Kompleks

```python
supabase = get_supabase_client()

# Query dengan filter kompleks
response = supabase.table('gbp_location_snapshot')\
    .select('*, gbp_fetch_run(started_at)')\
    .eq('status', 'Verified')\
    .gte('created_at', '2024-01-01')\
    .order('created_at', desc=True)\
    .limit(100)\
    .execute()

data = response.data
```

### 7. Contoh di Django View

```python
from django.http import JsonResponse
from django.views import View
from gbp.supabase_client import get_supabase_client
import logging

log = logging.getLogger("gbp.views")

class SupabaseExampleView(View):
    """Contoh view yang menggunakan Supabase"""
    
    def get(self, request):
        try:
            supabase = get_supabase_client()
            
            # Query data dari Supabase
            response = supabase.table('gbp_location_snapshot')\
                .select('store_code, business_name, status')\
                .eq('status', 'Verified')\
                .limit(10)\
                .execute()
            
            data = response.data
            
            return JsonResponse({
                'success': True,
                'count': len(data),
                'data': data
            })
            
        except Exception as exc:
            log.exception("Error querying Supabase")
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)
```

## 🧪 Test Koneksi

Untuk test koneksi Supabase, buat management command:

```python
# gbp/management/commands/test_supabase.py
from django.core.management.base import BaseCommand
from gbp.supabase_client import test_connection, get_supabase_client

class Command(BaseCommand):
    help = 'Test koneksi ke Supabase'

    def handle(self, *args, **options):
        self.stdout.write("Testing Supabase connection...")
        
        if test_connection():
            self.stdout.write(self.style.SUCCESS('✅ Koneksi Supabase berhasil!'))
            
            # Coba query sederhana
            try:
                supabase = get_supabase_client()
                response = supabase.table('gbp_fetch_run').select('id').limit(1).execute()
                self.stdout.write(self.style.SUCCESS(f'✅ Query test berhasil: {response.data}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Query test gagal: {e}'))
        else:
            self.stdout.write(self.style.ERROR('❌ Koneksi Supabase gagal!'))
```

Jalankan dengan:
```bash
python manage.py test_supabase
```

## 🔍 Filter Operators

Supabase mendukung berbagai filter operators:

```python
# Equals
.eq('column', 'value')

# Not equals
.neq('column', 'value')

# Greater than
.gt('column', 100)

# Greater than or equal
.gte('column', 100)

# Less than
.lt('column', 100)

# Less than or equal
.lte('column', 100)

# Like (case sensitive)
.like('column', '%pattern%')

# iLike (case insensitive)
.ilike('column', '%pattern%')

# In array
.in_('column', ['value1', 'value2'])

# Is null
.is_('column', 'null')

# Is not null
.not_.is_('column', 'null')
```

## 📊 Best Practices

1. **Error Handling**: Selalu wrap query Supabase dalam try-except block
2. **Logging**: Log semua error untuk debugging
3. **Connection Pooling**: Supabase client sudah handle connection pooling
4. **Rate Limiting**: Perhatikan rate limit dari Supabase plan Anda
5. **Security**: Jangan expose SUPABASE_KEY di client-side code
6. **Pagination**: Gunakan `.limit()` dan `.offset()` untuk data besar

## 🔗 Resources

- [Supabase Python Docs](https://supabase.com/docs/reference/python/introduction)
- [Supabase Query API](https://supabase.com/docs/reference/python/select)
- [Django Settings](https://docs.djangoproject.com/en/stable/ref/settings/)

## 📝 Notes

- Supabase client menggunakan singleton pattern, jadi hanya dibuat satu instance
- Client akan auto-reconnect jika koneksi terputus
- Untuk production, gunakan Service Role Key untuk operasi admin
- Untuk client-side, gunakan Anon Key dengan Row Level Security (RLS)

