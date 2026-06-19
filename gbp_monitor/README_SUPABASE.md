# 🚀 Supabase Quick Start

## ⚡ TL;DR

```bash
# 1. Install
pip install supabase

# 2. Buat tabel (copy supabase_schema.sql ke Supabase SQL Editor)

# 3. Test
python manage.py test_supabase

# 4. Use in code
from gbp.supabase_client import get_supabase_client
supabase = get_supabase_client()
```

---

## 📝 Files Reference

| File | Purpose |
|------|---------|
| `SUPABASE_SUMMARY.md` | 📋 **START HERE** - Overview lengkap |
| `SUPABASE_SETUP.md` | 🔧 Setup guide step-by-step |
| `SUPABASE_INTEGRATION.md` | 📚 Full documentation + API reference |
| `SUPABASE_CHECKLIST.md` | ✅ Verification checklist |
| `supabase_schema.sql` | 🗄️ Database schema (copy ke Supabase) |
| `gbp/supabase_client.py` | 💻 Main Supabase client |
| `gbp/views_supabase_example.py` | 💡 10+ code examples |
| `gbp/management/commands/test_supabase.py` | 🧪 Test command |

---

## 🎯 Configuration

### ✅ Already Configured:

**File: `.env`**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key-here
```

**File: `settings.py`**
```python
SUPABASE_URL = env("SUPABASE_URL", default="")
SUPABASE_KEY = env("SUPABASE_KEY", default="")
```

**File: `views.py`**
```python
from gbp.supabase_client import get_supabase_client
```

**File: `requirements.txt`**
```
supabase>=2.0
```

---

## 🏃 Quick Commands

### Install
```bash
pip install supabase
```

### Test Connection
```bash
python manage.py test_supabase
python manage.py test_supabase --verbose  # More details
```

### Django Shell
```bash
python manage.py shell
```

In shell:
```python
from gbp.supabase_client import get_supabase_client
supabase = get_supabase_client()
response = supabase.table('gbp_fetch_run').select('*').limit(1).execute()
print(response.data)
```

---

## 💻 Code Examples

### Basic Query
```python
from gbp.supabase_client import get_supabase_client

supabase = get_supabase_client()
response = supabase.table('gbp_location_snapshot').select('*').limit(10).execute()
```

### Insert
```python
data = {'store_code': 'KS001', 'business_name': 'Toko A'}
response = supabase.table('gbp_location_snapshot').insert(data).execute()
```

### Update
```python
response = supabase.table('gbp_location_snapshot')\
    .update({'status': 'Verified'})\
    .eq('store_code', 'KS001')\
    .execute()
```

### Filter & Search
```python
response = supabase.table('gbp_location_snapshot')\
    .select('*')\
    .eq('status', 'Verified')\
    .ilike('business_name', '%toko%')\
    .order('created_at', desc=True)\
    .execute()
```

**More examples**: See `gbp/views_supabase_example.py` (10+ examples)

---

## 🗄️ Database Tables

Tables to create (run `supabase_schema.sql`):

- ✅ `gbp_fetch_run` - Fetch run tracking
- ✅ `gbp_location_snapshot` - Location snapshots
- ✅ `gbp_master_location` - Master data
- ✅ `gbp_reconciliation_job` - Reconciliation jobs
- ✅ `gbp_reconciliation_result` - Reconciliation results
- ✅ `gbp_master_data_history` - Audit trail

---

## ⚠️ TODO

1. [ ] `pip install supabase`
2. [ ] Run `supabase_schema.sql` in Supabase SQL Editor
3. [ ] `python manage.py test_supabase`
4. [ ] Start using in code!

---

## 📖 Full Documentation

- **Quick Start**: You're here! (`README_SUPABASE.md`)
- **Summary**: `SUPABASE_SUMMARY.md` ⭐ Read this next!
- **Setup Guide**: `SUPABASE_SETUP.md`
- **Full Docs**: `SUPABASE_INTEGRATION.md`
- **Checklist**: `SUPABASE_CHECKLIST.md`

---

## 🆘 Troubleshooting

### Connection Failed?
```bash
python manage.py test_supabase --verbose
```

Check:
- ✅ SUPABASE_URL correct?
- ✅ SUPABASE_KEY valid?
- ✅ Internet connection OK?
- ✅ Supabase project active?

### Table Not Found?
→ Run `supabase_schema.sql` in Supabase SQL Editor

### Import Error?
→ Run `pip install supabase`

---

## 🎉 That's It!

**Next**: Read `SUPABASE_SUMMARY.md` for complete overview.

**Ready to code?** Check examples in `gbp/views_supabase_example.py`

