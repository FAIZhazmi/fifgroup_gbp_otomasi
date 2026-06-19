# ✅ Supabase Integration Checklist

Quick reference untuk memastikan setup Supabase sudah lengkap.

---

## 📦 Files Created/Modified

### ✅ File Baru Dibuat:
- [x] `gbp/supabase_client.py` - Supabase client initialization
- [x] `gbp/management/commands/test_supabase.py` - Test connection command
- [x] `supabase_schema.sql` - Database schema SQL
- [x] `views_supabase_example.py` - Contoh implementasi (10+ examples)
- [x] `SUPABASE_INTEGRATION.md` - Dokumentasi integrasi
- [x] `SUPABASE_SETUP.md` - Setup guide
- [x] `SUPABASE_CHECKLIST.md` - This file

### ✅ File Dimodifikasi:
- [x] `.env` - Added SUPABASE_URL dan SUPABASE_KEY
- [x] `settings.py` - Added Supabase configuration
- [x] `views.py` - Added import supabase_client
- [x] `requirements.txt` - Added supabase>=2.0

---

## 🔧 Setup Steps

### 1. Environment Variables
```bash
# Edit .env file
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key-here
```

Status: 
- [x] SUPABASE_URL sudah diset
- [x] SUPABASE_KEY sudah diset

### 2. Install Dependencies
```bash
pip install supabase
# atau
pip install -r requirements.txt
```

Status:
- [ ] Package `supabase` terinstall

### 3. Create Tables in Supabase
```bash
# Copy supabase_schema.sql ke Supabase SQL Editor
# Run script
```

Status:
- [ ] Tabel `gbp_fetch_run` created
- [ ] Tabel `gbp_location_snapshot` created
- [ ] Tabel `gbp_master_location` created
- [ ] Tabel `gbp_reconciliation_job` created
- [ ] Tabel `gbp_reconciliation_result` created
- [ ] Tabel `gbp_master_data_history` created
- [ ] Indexes created
- [ ] Triggers created

### 4. Test Connection
```bash
python manage.py test_supabase
```

Status:
- [ ] Connection test PASSED
- [ ] Query test PASSED

---

## 📝 Quick Commands

### Test Koneksi
```bash
python manage.py test_supabase
python manage.py test_supabase --verbose
```

### Run Django Server
```bash
python manage.py runserver
```

### Django Shell Test
```bash
python manage.py shell
```

Dalam shell:
```python
from gbp.supabase_client import get_supabase_client

# Get client
supabase = get_supabase_client()

# Test query
response = supabase.table('gbp_fetch_run').select('*').limit(1).execute()
print(response.data)
```

---

## 🔍 Verification Checklist

### Configuration
- [x] `.env` file exists
- [x] SUPABASE_URL configured in .env
- [x] SUPABASE_KEY configured in .env
- [x] settings.py imports and uses env variables
- [x] supabase_client.py created

### Database
- [ ] Supabase project created
- [ ] Database tables created (run supabase_schema.sql)
- [ ] Indexes created
- [ ] Triggers configured

### Code Integration
- [x] supabase_client.py imported in views.py
- [x] get_supabase_client() function available
- [x] Error handling implemented
- [x] Logging configured

### Testing
- [ ] test_supabase command runs successfully
- [ ] Can query tables from Supabase
- [ ] Can insert data to Supabase
- [ ] Can update data in Supabase

### Documentation
- [x] SUPABASE_SETUP.md created
- [x] SUPABASE_INTEGRATION.md created
- [x] Example views documented
- [x] SQL schema documented

---

## 🚀 Next Actions

### Immediate (Required):
1. [ ] Install supabase package: `pip install supabase`
2. [ ] Create tables: Run `supabase_schema.sql` in Supabase SQL Editor
3. [ ] Test connection: `python manage.py test_supabase`
4. [ ] Verify all tables exist in Supabase Dashboard

### Optional (Recommended):
5. [ ] Setup Row Level Security (RLS) policies
6. [ ] Create additional indexes for performance
7. [ ] Configure backup strategy
8. [ ] Setup monitoring & alerts
9. [ ] Implement data migration from SQLite (if needed)
10. [ ] Add Supabase storage for file uploads (if needed)

---

## 📊 Usage Examples

### In Views
```python
from gbp.supabase_client import get_supabase_client

def my_view(request):
    supabase = get_supabase_client()
    response = supabase.table('gbp_location_snapshot').select('*').execute()
    return JsonResponse({'data': response.data})
```

### In Services
```python
from gbp.supabase_client import get_supabase_client

def save_location(location_data):
    supabase = get_supabase_client()
    response = supabase.table('gbp_location_snapshot').insert(location_data).execute()
    return response.data
```

### In Management Commands
```python
from gbp.supabase_client import get_supabase_client
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        supabase = get_supabase_client()
        # Your logic here
```

---

## 🔗 Resources

- **Supabase Python Docs**: https://supabase.com/docs/reference/python
- **Django Environ**: https://django-environ.readthedocs.io/
- **Project Files**:
  - Setup Guide: `SUPABASE_SETUP.md`
  - Integration Docs: `SUPABASE_INTEGRATION.md`
  - Examples: `views_supabase_example.py`
  - Schema: `supabase_schema.sql`

---

## ✨ Status Summary

| Component | Status |
|-----------|--------|
| Files Created | ✅ Done |
| Configuration | ✅ Done |
| Dependencies | ⏳ Pending (pip install) |
| Database Tables | ⏳ Pending (run SQL script) |
| Testing | ⏳ Pending (test_supabase) |
| Documentation | ✅ Done |

**Next Step**: Install `supabase` package dan buat tables!

```bash
pip install supabase
python manage.py test_supabase
```

