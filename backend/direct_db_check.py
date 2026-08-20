#!/usr/bin/env python
"""Direct PostgreSQL check."""
import psycopg
import os

try:
    # Connection string from environment or hardcoded
    conn_str = "postgresql://zoiko:zoiko@localhost:5432/zoiko_rooms"
    
    print("Connecting to PostgreSQL...")
    conn = psycopg.connect(conn_str)
    cursor = conn.cursor()
    
    print("\n=== CHECKING DATABASE SCHEMA ===\n")
    
    # Get alembic version
    try:
        cursor.execute("SELECT version_num FROM alembic_version")
        version = cursor.fetchone()
        if version:
            print(f"✓ Current migration applied: {version[0]}")
        else:
            print("✗ No alembic version found")
    except Exception as e:
        print(f"⚠ Alembic version check failed: {e}")
    
    # Check for user_accounts table
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'user_accounts'
        )
    """)
    exists = cursor.fetchone()[0]
    print(f"\n✓ user_accounts table exists: {exists}")
    
    if exists:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='user_accounts'")
        cols = cursor.fetchall()
        print("  Columns:")
        for col in cols:
            print(f"    - {col[0]}")
    
    # Check for sublet_requests table
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'sublet_requests'
        )
    """)
    exists = cursor.fetchone()[0]
    print(f"\n✓ sublet_requests table exists: {exists}")
    
    # Check listings.party_id
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name='listings' AND column_name='party_id'
        )
    """)
    exists = cursor.fetchone()[0]
    print(f"\n✓ listings.party_id exists: {exists}")
    
    cursor.close()
    conn.close()
    print("\n=== DATABASE CHECK COMPLETE ===\n")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
