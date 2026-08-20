#!/usr/bin/env python
"""Check database schema and migration state."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

try:
    print("=" * 70)
    print("DATABASE SCHEMA CHECK")
    print("=" * 70)
    
    # Connect to database
    engine = create_engine(settings.database_url)
    conn = engine.connect()
    
    # Check for alembic version
    try:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).fetchone()
        if version:
            print(f"\n✓ Current migration: {version[0]}")
        else:
            print("\n✗ No alembic_version found (migrations not initialized)")
    except Exception as e:
        print(f"\n✗ Alembic version table error: {e}")
    
    # Check for user_accounts table
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n✓ Total tables: {len(tables)}")
    
    # Check specific tables we created
    new_tables = ['user_accounts', 'sublet_requests']
    print("\nNew tables status:")
    for tbl in new_tables:
        if tbl in tables:
            print(f"  ✓ {tbl} exists")
            # Get columns
            cols = inspector.get_columns(tbl)
            for col in cols:
                print(f"    - {col['name']}: {col['type']}")
        else:
            print(f"  ✗ {tbl} NOT FOUND")
    
    # Check if listings has party_id
    if 'listings' in tables:
        cols = inspector.get_columns('listings')
        col_names = [col['name'] for col in cols]
        if 'party_id' in col_names:
            print(f"  ✓ listings.party_id exists")
        else:
            print(f"  ✗ listings.party_id NOT FOUND")
    
    conn.close()
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
