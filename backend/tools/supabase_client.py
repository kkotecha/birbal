"""Supabase client helper"""

from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

def get_supabase_client() -> Client:
    """Get initialized Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)
