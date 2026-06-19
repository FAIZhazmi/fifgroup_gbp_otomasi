"""
test_supabase.py — Management command untuk test koneksi Supabase.

Usage:
    python manage.py test_supabase
    python manage.py test_supabase --verbose
"""

from django.core.management.base import BaseCommand
from gbp.supabase_client import test_connection, get_supabase_client


class Command(BaseCommand):
    help = 'Test koneksi ke Supabase dan coba query sederhana'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Tampilkan informasi detail',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        
        self.stdout.write(self.style.NOTICE('=' * 60))
        self.stdout.write(self.style.NOTICE('🧪 Testing Supabase Connection'))
        self.stdout.write(self.style.NOTICE('=' * 60))
        
        # Test basic connection
        self.stdout.write('\n1️⃣ Testing basic connection...')
        
        try:
            supabase = get_supabase_client()
            self.stdout.write(self.style.SUCCESS('   ✅ Supabase client initialized'))
            
            if verbose:
                from django.conf import settings
                self.stdout.write(f'   📍 URL: {settings.SUPABASE_URL}')
                self.stdout.write(f'   🔑 Key: {settings.SUPABASE_KEY[:20]}...')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Failed to initialize client: {e}'))
            return
        
        # Test connection
        self.stdout.write('\n2️⃣ Testing connection with query...')
        
        if test_connection():
            self.stdout.write(self.style.SUCCESS('   ✅ Connection test passed'))
        else:
            self.stdout.write(self.style.ERROR('   ❌ Connection test failed'))
            self.stdout.write(self.style.WARNING('   💡 Pastikan tabel "gbp_fetch_run" sudah dibuat di Supabase'))
            return
        
        # Test query to all tables
        self.stdout.write('\n3️⃣ Testing queries to tables...')
        
        tables = [
            'gbp_fetch_run',
            'gbp_location_snapshot',
            'gbp_master_location',
            'gbp_reconciliation_job',
            'gbp_reconciliation_result',
        ]
        
        for table in tables:
            try:
                response = supabase.table(table).select('*').limit(1).execute()
                count = len(response.data)
                self.stdout.write(self.style.SUCCESS(f'   ✅ {table}: Query berhasil (sample: {count} rows)'))
                
                if verbose and count > 0:
                    self.stdout.write(f'      Sample data: {response.data[0]}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'   ⚠️  {table}: {str(e)}'))
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ Supabase integration test completed!'))
        self.stdout.write(self.style.NOTICE('=' * 60))
        
        # Tips
        self.stdout.write('\n💡 Tips:')
        self.stdout.write('   - Pastikan semua tabel sudah dibuat di Supabase SQL Editor')
        self.stdout.write('   - Gunakan Service Role Key untuk admin operations')
        self.stdout.write('   - Aktifkan Row Level Security (RLS) untuk production')
        self.stdout.write('   - Check logs di Supabase Dashboard jika ada error')

