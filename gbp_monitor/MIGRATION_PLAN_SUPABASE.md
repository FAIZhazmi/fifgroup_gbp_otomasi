# 🚀 Migration Plan: CSV Upload → Supabase Master Data

## 📊 Analisa Code Yang Ada

### ✅ **Yang Sudah Benar:**

1. **Tabel `gbp_master_location` sudah ada** di `supabase_schema.sql`
   - Sudah punya struktur yang tepat untuk simpan master data
   - Columns: store_code, network_name, business_name, current_status, dll

2. **Reconciliation service sudah ada**
   - `compare_master_to_api()` - Bisa compare master vs API
   - `update_master_statuses()` - Bisa update master di database
   - `save_reconciliation_job()` - Save hasil comparison

3. **UpdateStatusView sudah handle upload CSV**
   - Bisa baca CSV dari upload
   - Bisa compare dengan API
   - Bisa save hasil reconciliation

### ❌ **Yang Perlu Ditambah:**

1. **Simpan CSV ke Supabase** - Belum ada function untuk save CSV ke `gbp_master_location`
2. **Query master dari Supabase** - Belum ada opsi untuk ambil master data dari Supabase
3. **Add/Edit master data via web** - Belum ada form untuk add/edit titik baru
4. **Auto use Supabase** - Masih harus upload CSV manual tiap kali

---

## 🎯 Solusi: 3 Fitur yang Perlu Ditambahkan

### **Fitur 1: Import CSV ke Supabase (One-Time)**
```
Flow:
1. Upload CSV (form yang ada sekarang)
2. [BARU] Checkbox: "Simpan ke Supabase sebagai master data?"
3. [BARU] Jika checked → Save ke tabel gbp_master_location di Supabase
4. Next time → Ambil langsung dari Supabase
```

### **Fitur 2: Use Supabase as Master Source**
```
Flow:
1. [BARU] Opsi baru di form: "Ambil master dari Supabase"
2. Query dari gbp_master_location
3. Compare dengan API (existing logic)
4. Update ke Supabase (existing logic)
```

### **Fitur 3: CRUD Master Data via Web**
```
Flow:
1. [BARU] Page baru: Manage Master Locations
2. List semua master locations dari Supabase
3. Add/Edit/Delete titik
4. Search & filter
```

---

## 💻 Implementation

### **1. Service untuk Sync CSV → Supabase**

**File Baru: `gbp/services/master_data_service.py`**

```python
"""
master_data_service.py — Service untuk manage master data di Supabase
"""

import logging
import pandas as pd
from django.utils import timezone
from gbp.supabase_client import get_supabase_client

log = logging.getLogger("gbp.services.master_data_service")


def import_csv_to_supabase(csv_df: pd.DataFrame, source_label: str = "") -> dict:
    """
    Import CSV ke tabel gbp_master_location di Supabase.
    
    Returns:
        dict: {'imported': count, 'updated': count, 'errors': list}
    """
    supabase = get_supabase_client()
    
    imported = 0
    updated = 0
    errors = []
    
    for idx, row in csv_df.iterrows():
        try:
            # Mapping kolom CSV ke Supabase
            store_code = str(row.get('NETWORK ID UPDATED') or row.get('store_code') or '').strip()
            
            if not store_code:
                errors.append(f"Row {idx+1}: store_code kosong")
                continue
            
            data = {
                'store_code': store_code,
                'network_name': str(row.get('NAMA NETWORK') or row.get('network_name') or '').strip(),
                'business_name': str(row.get('BRANCH NAME') or row.get('business_name') or '').strip(),
                'current_status': str(row.get('STATUS VERIFIKASI') or row.get('status') or '').strip(),
                'address': str(row.get('address') or '').strip() or None,
                'area': str(row.get('area') or '').strip() or None,
                'network': str(row.get('NETWORK') or row.get('network') or '').strip() or None,
                'last_updated': timezone.now().isoformat(),
            }
            
            # Check if exists
            existing = supabase.table('gbp_master_location')\
                .select('id')\
                .eq('store_code', store_code)\
                .execute()
            
            if existing.data:
                # Update
                supabase.table('gbp_master_location')\
                    .update(data)\
                    .eq('store_code', store_code)\
                    .execute()
                updated += 1
            else:
                # Insert
                supabase.table('gbp_master_location')\
                    .insert(data)\
                    .execute()
                imported += 1
                
        except Exception as e:
            errors.append(f"Row {idx+1}: {str(e)}")
            log.error(f"Error importing row {idx+1}: {e}")
    
    log.info(f"Import selesai: {imported} new, {updated} updated, {len(errors)} errors")
    
    return {
        'imported': imported,
        'updated': updated,
        'errors': errors,
        'total': imported + updated
    }


def get_master_data_from_supabase() -> pd.DataFrame:
    """
    Ambil semua master data dari Supabase.
    
    Returns:
        pd.DataFrame dengan kolom yang sesuai untuk reconciliation
    """
    supabase = get_supabase_client()
    
    response = supabase.table('gbp_master_location')\
        .select('*')\
        .order('store_code')\
        .execute()
    
    if not response.data:
        return pd.DataFrame()
    
    df = pd.DataFrame(response.data)
    
    # Rename kolom agar sesuai dengan format CSV (untuk compatibility)
    df_renamed = df.rename(columns={
        'store_code': 'NETWORK ID UPDATED',
        'network_name': 'NAMA NETWORK',
        'business_name': 'BRANCH NAME',
        'current_status': 'STATUS VERIFIKASI',
        'network': 'NETWORK',
    })
    
    log.info(f"Loaded {len(df_renamed)} master records from Supabase")
    
    return df_renamed


def add_master_location(data: dict) -> dict:
    """
    Tambah location baru ke master data Supabase.
    
    Args:
        data: dict with keys: store_code, network_name, business_name, current_status, etc
    
    Returns:
        dict: newly created record
    """
    supabase = get_supabase_client()
    
    # Validate required fields
    if not data.get('store_code'):
        raise ValueError("store_code is required")
    
    # Check duplicate
    existing = supabase.table('gbp_master_location')\
        .select('id')\
        .eq('store_code', data['store_code'])\
        .execute()
    
    if existing.data:
        raise ValueError(f"store_code '{data['store_code']}' sudah ada")
    
    # Insert
    data['last_updated'] = timezone.now().isoformat()
    response = supabase.table('gbp_master_location').insert(data).execute()
    
    log.info(f"Added new master location: {data['store_code']}")
    
    return response.data[0] if response.data else {}


def update_master_location(store_code: str, data: dict) -> dict:
    """
    Update location di master data Supabase.
    
    Args:
        store_code: store_code yang akan diupdate
        data: dict with fields to update
    
    Returns:
        dict: updated record
    """
    supabase = get_supabase_client()
    
    data['last_updated'] = timezone.now().isoformat()
    
    response = supabase.table('gbp_master_location')\
        .update(data)\
        .eq('store_code', store_code)\
        .execute()
    
    if not response.data:
        raise ValueError(f"store_code '{store_code}' tidak ditemukan")
    
    log.info(f"Updated master location: {store_code}")
    
    return response.data[0] if response.data else {}


def delete_master_location(store_code: str) -> bool:
    """
    Hapus location dari master data Supabase.
    
    Args:
        store_code: store_code yang akan dihapus
    
    Returns:
        bool: True if success
    """
    supabase = get_supabase_client()
    
    response = supabase.table('gbp_master_location')\
        .delete()\
        .eq('store_code', store_code)\
        .execute()
    
    log.info(f"Deleted master location: {store_code}")
    
    return True


def get_master_stats() -> dict:
    """
    Get statistik master data dari Supabase.
    
    Returns:
        dict: {'total': int, 'by_status': {}, 'by_area': {}}
    """
    supabase = get_supabase_client()
    
    response = supabase.table('gbp_master_location')\
        .select('current_status, area')\
        .execute()
    
    if not response.data:
        return {'total': 0, 'by_status': {}, 'by_area': {}}
    
    df = pd.DataFrame(response.data)
    
    from collections import Counter
    status_counts = Counter(df['current_status'].dropna())
    area_counts = Counter(df['area'].dropna())
    
    return {
        'total': len(df),
        'by_status': dict(status_counts),
        'by_area': dict(area_counts)
    }
```

---

### **2. Update Form untuk Support Supabase**

**Update: `gbp/forms.py`**

Tambahkan opsi baru di `UpdateStatusForm`:

```python
SOURCE_SUPABASE = 'supabase'

source_type = forms.ChoiceField(
    choices=[
        (SOURCE_CSV, 'Upload CSV atau Path'),
        (SOURCE_SQLITE, 'SQLite Database'),
        (SOURCE_SUPABASE, 'Supabase Master Data'),  # NEW!
    ],
    initial=SOURCE_SUPABASE,  # Default ke Supabase
)

save_to_supabase = forms.BooleanField(
    required=False,
    initial=True,
    label='Simpan ke Supabase sebagai master data',
    help_text='CSV yang diupload akan disimpan ke Supabase untuk digunakan selanjutnya'
)
```

---

### **3. Update View untuk Handle Supabase**

**Update: `gbp/views.py` - UpdateStatusView.post()**

Ganti logic baca master data:

```python
# 2. Baca master data
source_type = form.cleaned_data["source_type"]
master_source_label = ""

if source_type == UpdateStatusForm.SOURCE_SUPABASE:
    # [BARU] Ambil dari Supabase
    from gbp.services import master_data_service
    master_df = master_data_service.get_master_data_from_supabase()
    master_source_label = "Supabase Master Data"
    
    if master_df.empty:
        messages.warning(request, "Master data di Supabase masih kosong. Upload CSV dulu untuk init.")
        return render(request, self.template_name, context)

elif source_type == UpdateStatusForm.SOURCE_CSV:
    master_file = form.cleaned_data.get("master_file")
    master_path = form.cleaned_data.get("master_path", "").strip()

    if master_file:
        master_df = pd.read_csv(master_file, dtype=str, keep_default_na=False)
        master_source_label = f"Upload: {master_file.name}"
        
        # [BARU] Save ke Supabase jika checkbox checked
        if form.cleaned_data.get("save_to_supabase"):
            from gbp.services import master_data_service
            import_result = master_data_service.import_csv_to_supabase(master_df, master_file.name)
            messages.success(
                request,
                f"✅ CSV disimpan ke Supabase: {import_result['imported']} new, "
                f"{import_result['updated']} updated"
            )
    else:
        master_df = pd.read_csv(master_path, dtype=str, keep_default_na=False)
        master_source_label = master_path
        
else:  # SQLite
    # ... existing code ...
```

---

### **4. View Baru: Manage Master Data**

**File Baru: Tambah di `gbp/views.py`**

```python
class ManageMasterDataView(View):
    """Halaman untuk manage master data di Supabase"""
    template_name = "gbp/manage_master_data.html"
    
    def get(self, request):
        from gbp.services import master_data_service
        
        # Get master data
        master_df = master_data_service.get_master_data_from_supabase()
        master_list = master_df.to_dict('records') if not master_df.empty else []
        
        # Get stats
        stats = master_data_service.get_master_stats()
        
        context = {
            'master_locations': master_list,
            'stats': stats,
            'total': len(master_list),
        }
        
        return render(request, self.template_name, context)


class AddMasterLocationView(View):
    """API untuk tambah master location baru"""
    
    def post(self, request):
        try:
            import json
            from gbp.services import master_data_service
            
            data = json.loads(request.body)
            result = master_data_service.add_master_location(data)
            
            return JsonResponse({
                'success': True,
                'data': result
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class UpdateMasterLocationView(View):
    """API untuk update master location"""
    
    def post(self, request, store_code):
        try:
            import json
            from gbp.services import master_data_service
            
            data = json.loads(request.body)
            result = master_data_service.update_master_location(store_code, data)
            
            return JsonResponse({
                'success': True,
                'data': result
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class DeleteMasterLocationView(View):
    """API untuk delete master location"""
    
    def post(self, request, store_code):
        try:
            from gbp.services import master_data_service
            
            master_data_service.delete_master_location(store_code)
            
            return JsonResponse({
                'success': True,
                'message': f'Location {store_code} deleted'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
```

---

### **5. Update URLs**

**Update: `gbp/urls.py`**

```python
urlpatterns = [
    # ... existing URLs ...
    
    # Master Data Management
    path('master/', ManageMasterDataView.as_view(), name='manage_master'),
    path('api/master/add/', AddMasterLocationView.as_view(), name='api_add_master'),
    path('api/master/<str:store_code>/update/', UpdateMasterLocationView.as_view(), name='api_update_master'),
    path('api/master/<str:store_code>/delete/', DeleteMasterLocationView.as_view(), name='api_delete_master'),
]
```

---

## 🎯 Flow Lengkap Setelah Implementation

### **Skenario 1: Pertama Kali (Init Master Data)**

```
1. User upload CSV
2. ✅ Checkbox "Simpan ke Supabase" → Checked
3. Submit → CSV tersimpan ke Supabase
4. Comparison berjalan normal
```

### **Skenario 2: Fetch Berikutnya (No New Titik)**

```
1. User pilih "Ambil master dari Supabase" (default)
2. Submit langsung (tanpa upload CSV!)
3. Fetch API → Compare dengan Supabase
4. Update status di Supabase
```

### **Skenario 3: Ada Titik Baru**

```
Option A: Via Web
1. User pergi ke /master/
2. Klik "Add Location"
3. Fill form → Submit
4. Titik baru tersimpan di Supabase

Option B: Via CSV
1. User upload CSV baru (dengan titik tambahan)
2. ✅ Checkbox "Simpan ke Supabase" → Checked
3. Submit → Titik baru ter-insert, yang lama ter-update
```

---

## ✅ Checklist Implementation

### Yang Perlu Dibuat:
- [ ] `gbp/services/master_data_service.py`
- [ ] Update `gbp/forms.py` - add SOURCE_SUPABASE & save_to_supabase
- [ ] Update `gbp/views.py` - UpdateStatusView logic
- [ ] Add `ManageMasterDataView` di `views.py`
- [ ] Add API views (Add/Update/Delete) di `views.py`
- [ ] Update `gbp/urls.py` - add new routes
- [ ] Create template `gbp/templates/gbp/manage_master_data.html`

### Yang Sudah Ada (Ready to Use):
- ✅ Tabel `gbp_master_location` di Supabase
- ✅ `supabase_client.py` untuk koneksi
- ✅ Reconciliation service
- ✅ UpdateStatusView base structure

---

## 📝 Kesimpulan

**Code Anda sudah 70% siap!** Yang perlu ditambah:

1. **Service baru** untuk handle Supabase CRUD operations
2. **Update form** untuk add opsi Supabase
3. **Update view logic** untuk support flow baru
4. **Add management page** (optional tapi recommended)

**Benefit:**
- ✅ No more manual CSV upload every time
- ✅ Master data centralized di Supabase
- ✅ Easy to add/edit titik via web
- ✅ Automatic sync

Mau saya buatkan file-file yang dibutuhkan?

