"""
supabase_client.py — Inisialisasi Supabase Client untuk GBP Monitor.
Menggunakan supabase-py library untuk koneksi ke Supabase PostgreSQL & Storage.
"""

import logging
from typing import Optional

from django.conf import settings
from supabase import create_client, Client

log = logging.getLogger("gbp.supabase")

# Global Supabase client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Mengembalikan Supabase client instance (singleton pattern).
    
    Returns:
        Client: Supabase client instance
        
    Raises:
        ValueError: Jika SUPABASE_URL atau SUPABASE_KEY tidak dikonfigurasi
    """
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = getattr(settings, "SUPABASE_URL", None)
        supabase_key = getattr(settings, "SUPABASE_KEY", None)
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL dan SUPABASE_KEY harus dikonfigurasi di settings.py. "
                "Pastikan variabel environment sudah diset di file .env"
            )
        
        try:
            _supabase_client = create_client(supabase_url, supabase_key)
            log.info(f"✅ Supabase client berhasil diinisialisasi: {supabase_url}")
        except Exception as exc:
            log.exception("❌ Gagal membuat Supabase client")
            raise RuntimeError(f"Gagal koneksi ke Supabase: {exc}") from exc
    
    return _supabase_client


def test_connection() -> bool:
    """
    Test koneksi ke Supabase dengan melakukan query sederhana.
    
    Returns:
        bool: True jika koneksi berhasil, False jika gagal
    """
    try:
        client = get_supabase_client()
        # Test query ke tabel pertama yang ada (atau bisa ganti dengan tabel spesifik)
        response = client.table("gbp_fetch_run").select("id").limit(1).execute()
        log.info(f"✅ Test koneksi Supabase berhasil. Response: {response}")
        return True
    except Exception as exc:
        log.error(f"❌ Test koneksi Supabase gagal: {exc}")
        return False


# Shortcut untuk akses langsung
supabase = get_supabase_client

