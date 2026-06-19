"""
views_supabase_example.py — Contoh Django views yang menggunakan Supabase.

File ini berisi contoh-contoh implementasi untuk referensi.
Tidak digunakan secara langsung, hanya untuk dokumentasi.
"""

import logging
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.shortcuts import render
from django.contrib import messages

from gbp.supabase_client import get_supabase_client

log = logging.getLogger("gbp.views")


# ══════════════════════════════════════════════════════════════════════
# CONTOH 1: Simple SELECT Query
# ══════════════════════════════════════════════════════════════════════

class SupabaseLocationsListView(View):
    """
    Contoh: Query semua locations dari Supabase dengan filtering.
    URL: /api/supabase/locations/?status=Verified&limit=20
    """
    
    def get(self, request):
        try:
            supabase = get_supabase_client()
            
            # Get query parameters
            status = request.GET.get('status')
            limit = int(request.GET.get('limit', 100))
            offset = int(request.GET.get('offset', 0))
            
            # Build query
            query = supabase.table('gbp_location_snapshot').select('*')
            
            # Apply filters
            if status:
                query = query.eq('status', status)
            
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            # Execute
            response = query.order('created_at', desc=True).execute()
            
            return JsonResponse({
                'success': True,
                'count': len(response.data),
                'data': response.data
            })
            
        except Exception as exc:
            log.exception("Error querying locations from Supabase")
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)


# ══════════════════════════════════════════════════════════════════════
# CONTOH 2: INSERT Data
# ══════════════════════════════════════════════════════════════════════

class SupabaseSaveLocationView(View):
    """
    Contoh: Save location snapshot ke Supabase.
    Method: POST
    Body: JSON dengan data location
    """
    
    def post(self, request):
        try:
            import json
            data = json.loads(request.body)
            
            supabase = get_supabase_client()
            
            # Prepare data
            location_data = {
                'run_id': data.get('run_id'),
                'store_code': data.get('store_code'),
                'business_name': data.get('business_name'),
                'status': data.get('status'),
                'address': data.get('address'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
            }
            
            # Insert to Supabase
            response = supabase.table('gbp_location_snapshot').insert(location_data).execute()
            
            return JsonResponse({
                'success': True,
                'message': 'Location saved successfully',
                'data': response.data
            })
            
        except Exception as exc:
            log.exception("Error saving location to Supabase")
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)


# ══════════════════════════════════════════════════════════════════════
# CONTOH 3: UPDATE Data
# ══════════════════════════════════════════════════════════════════════

class SupabaseUpdateLocationStatusView(View):
    """
    Contoh: Update status location di Supabase.
    URL: /api/supabase/location/<id>/update-status/
    Method: POST
    Body: {"status": "Verified"}
    """
    
    def post(self, request, location_id):
        try:
            import json
            data = json.loads(request.body)
            new_status = data.get('status')
            
            if not new_status:
                return JsonResponse({
                    'success': False,
                    'error': 'Status is required'
                }, status=400)
            
            supabase = get_supabase_client()
            
            # Update status
            response = supabase.table('gbp_location_snapshot')\
                .update({'status': new_status})\
                .eq('id', location_id)\
                .execute()
            
            if not response.data:
                return JsonResponse({
                    'success': False,
                    'error': 'Location not found'
                }, status=404)
            
            return JsonResponse({
                'success': True,
                'message': f'Status updated to {new_status}',
                'data': response.data
            })
            
        except Exception as exc:
            log.exception("Error updating location status")
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)


# ══════════════════════════════════════════════════════════════════════
# CONTOH 4: Complex Query dengan JOIN
# ══════════════════════════════════════════════════════════════════════

class SupabaseLocationWithRunView(View):
    """
    Contoh: Query location dengan data fetch run (JOIN).
    URL: /api/supabase/locations-with-run/
    """
    
    def get(self, request):
        try:
            supabase = get_supabase_client()
            
            # Query dengan join (menggunakan foreign key relationship)
            response = supabase.table('gbp_location_snapshot')\
                .select('*, gbp_fetch_run(id, started_at, total_records)')\
                .limit(50)\
                .order('created_at', desc=True)\
                .execute()
            
            return JsonResponse({
                'success': True,
                'count': len(response.data),
                'data': response.data
            })
            
        except Exception as exc:
            log.exception("Error querying with join")
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)


# ══════════════════════════════════════════════════════════════════════
# CONTOH 5: Aggregation Query
# ══════════════════════════════════════════════════════════════════════

class SupabaseStatusSummaryView(View):
    """
    Contoh: Get summary status dari Supabase (count by status).
    URL: /api/supabase/status-summary/
    """
    
    def get(self, request):
        try:
            supabase = get_supabase_client()
            
            # Query all snapshots from latest run
            # Note: Supabase doesn't support GROUP BY directly,
            # jadi kita perlu process di Python
            response = supabase.table('gbp_location_snapshot')\
                .select('status')\
                .execute()
            
            # Count by status
            from collections import Counter
            status_counts = Counter(item['status'] for item in response.data)
            
            summary = {
                'total': len(response.data),
                'by_status': dict(status_counts)
            }
            
            return JsonResponse({
                'success': True,
                'summary': summary
            })
            
        except Exception as exc:
            log.exception("Error getting status summary")
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)


# ══════════════════════════════════════════════════════════════════════
# CONTOH 6: Batch Insert (Bulk Insert)
# ══════════════════════════════════════════════════════════════════════

class SupabaseBulkSaveLocationsView(View):
    """
    Contoh: Bulk insert locations ke Supabase.
    Method: POST
    Body: {"locations": [{...}, {...}]}
    """
    
    def post(self, request):
        try:
            import json
            data = json.loads(request.body)
            locations = data.get('locations', [])
            
            if not locations:
                return JsonResponse({
                    'success': False,
                    'error': 'No locations provided'
                }, status=400)
            
            supabase = get_supabase_client()
            
            # Bulk insert (Supabase handles this efficiently)
            response = supabase.table('gbp_location_snapshot').insert(locations).execute()
            
            return JsonResponse({
                'success': True,
                'message': f'{len(response.data)} locations saved',
                'count': len(response.data)
            })
            
        except Exception as exc:
            log.exception("Error bulk saving locations")
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)


# ══════════════════════════════════════════════════════════════════════
# CONTOH 7: Search dengan LIKE/ILIKE
# ══════════════════════════════════════════════════════════════════════

class SupabaseSearchLocationsView(View):
    """
    Contoh: Search locations by name atau store code.
    URL: /api/supabase/search/?q=toko
    """
    
    def get(self, request):
        try:
            query_text = request.GET.get('q', '').strip()
            
            if not query_text:
                return JsonResponse({
                    'success': False,
                    'error': 'Query parameter "q" is required'
                }, status=400)
            
            supabase = get_supabase_client()
            
            # Search in business_name (case insensitive)
            response = supabase.table('gbp_location_snapshot')\
                .select('*')\
                .ilike('business_name', f'%{query_text}%')\
                .limit(50)\
                .execute()
            
            return JsonResponse({
                'success': True,
                'query': query_text,
                'count': len(response.data),
                'results': response.data
            })
            
        except Exception as exc:
            log.exception("Error searching locations")
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)


# ══════════════════════════════════════════════════════════════════════
# CONTOH 8: Delete Data
# ══════════════════════════════════════════════════════════════════════

class SupabaseDeleteLocationView(View):
    """
    Contoh: Delete location by ID.
    URL: /api/supabase/location/<id>/delete/
    Method: DELETE
    """
    
    def delete(self, request, location_id):
        try:
            supabase = get_supabase_client()
            
            # Delete location
            response = supabase.table('gbp_location_snapshot')\
                .delete()\
                .eq('id', location_id)\
                .execute()
            
            if not response.data:
                return JsonResponse({
                    'success': False,
                    'error': 'Location not found'
                }, status=404)
            
            return JsonResponse({
                'success': True,
                'message': 'Location deleted successfully'
            })
            
        except Exception as exc:
            log.exception("Error deleting location")
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)


# ══════════════════════════════════════════════════════════════════════
# CONTOH 9: Transaction-like Batch Operations
# ══════════════════════════════════════════════════════════════════════

class SupabaseReconciliationView(View):
    """
    Contoh: Save reconciliation job + results dalam satu flow.
    Method: POST
    """
    
    def post(self, request):
        try:
            import json
            data = json.loads(request.body)
            
            supabase = get_supabase_client()
            
            # 1. Create reconciliation job
            job_data = {
                'source_type': data.get('source_type'),
                'source_label': data.get('source_label'),
                'total_master': data.get('total_master'),
                'total_api': data.get('total_api'),
                'summary': data.get('summary', {})
            }
            
            job_response = supabase.table('gbp_reconciliation_job').insert(job_data).execute()
            
            if not job_response.data:
                raise Exception("Failed to create reconciliation job")
            
            job_id = job_response.data[0]['id']
            
            # 2. Create reconciliation results (batch)
            results = data.get('results', [])
            
            if results:
                # Add job_id to each result
                for result in results:
                    result['job_id'] = job_id
                
                results_response = supabase.table('gbp_reconciliation_result').insert(results).execute()
                results_count = len(results_response.data)
            else:
                results_count = 0
            
            return JsonResponse({
                'success': True,
                'message': 'Reconciliation saved successfully',
                'job_id': job_id,
                'results_count': results_count
            })
            
        except Exception as exc:
            log.exception("Error saving reconciliation")
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)


# ══════════════════════════════════════════════════════════════════════
# CONTOH 10: Integration dengan Django Template View
# ══════════════════════════════════════════════════════════════════════

class SupabaseDashboardView(View):
    """
    Contoh: Render template dengan data dari Supabase.
    URL: /supabase-dashboard/
    """
    
    template_name = "gbp/supabase_dashboard.html"
    
    def get(self, request):
        try:
            supabase = get_supabase_client()
            
            # Get latest fetch runs
            runs_response = supabase.table('gbp_fetch_run')\
                .select('*')\
                .order('started_at', desc=True)\
                .limit(10)\
                .execute()
            
            # Get location counts by status
            locations_response = supabase.table('gbp_location_snapshot')\
                .select('status')\
                .execute()
            
            from collections import Counter
            status_counts = Counter(item['status'] for item in locations_response.data)
            
            context = {
                'runs': runs_response.data,
                'total_locations': len(locations_response.data),
                'status_summary': dict(status_counts),
                'supabase_connected': True
            }
            
            return render(request, self.template_name, context)
            
        except Exception as exc:
            log.exception("Error loading Supabase dashboard")
            messages.error(request, f"Failed to load data from Supabase: {exc}")
            
            context = {
                'supabase_connected': False,
                'error': str(exc)
            }
            
            return render(request, self.template_name, context)


# ══════════════════════════════════════════════════════════════════════
# TIPS & NOTES
# ══════════════════════════════════════════════════════════════════════

"""
💡 TIPS PENGGUNAAN SUPABASE:

1. Error Handling:
   - Selalu wrap query dalam try-except
   - Log error untuk debugging
   - Return meaningful error messages

2. Performance:
   - Gunakan .limit() untuk large datasets
   - Apply filters sebelum order/limit
   - Create indexes di Supabase untuk kolom yang sering diquery

3. Security:
   - Jangan expose SUPABASE_KEY di client-side
   - Gunakan Row Level Security (RLS) untuk production
   - Validate input data sebelum insert/update

4. Best Practices:
   - Gunakan .select('column1, column2') untuk hanya ambil kolom yang dibutuhkan
   - Batch insert untuk multiple records
   - Use views untuk complex queries yang sering dipakai

5. Debugging:
   - Check Supabase Dashboard > Logs untuk error details
   - Test query di Supabase SQL Editor dulu
   - Gunakan management command test_supabase untuk test koneksi

6. Migration:
   - Untuk migrate dari Django ORM ke Supabase, bisa dual-write dulu
   - Test thoroughly sebelum switch completely
   - Keep backup of SQLite data

COMMAND UNTUK TEST:
    python manage.py test_supabase
    python manage.py test_supabase --verbose
"""

