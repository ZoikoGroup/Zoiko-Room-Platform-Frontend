#!/usr/bin/env python
"""
Migration recovery script - helps debug and fix migration issues.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

def check_database_state():
    """Analyze current database state."""
    print("\n" + "="*80)
    print("DATABASE STATE ANALYSIS")
    print("="*80)
    
    try:
        engine = create_engine(settings.database_url)
        conn = engine.connect()
        
        # Check alembic_version
        print("\n[1] Alembic Migration Status:")
        try:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            versions = result.fetchall()
            if versions:
                print(f"    Current revision: {versions[-1][0]}")
                print(f"    Total migrations applied: {len(versions)}")
                for v in versions[-3:]:  # Show last 3
                    print(f"      - {v[0]}")
            else:
                print("    ✗ No migration history found")
        except Exception as e:
            print(f"    ✗ Error: {e}")
        
        # Check for partial tables
        print("\n[2] Table Status:")
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        
        # Check new tables
        for tbl in ['user_accounts', 'sublet_requests']:
            if tbl in tables:
                cols = inspector.get_columns(tbl)
                indexes = inspector.get_indexes(tbl)
                print(f"    ✓ {tbl}")
                print(f"      Columns: {len(cols)}")
                if indexes:
                    print(f"      Indexes: {len(indexes)}")
                    for idx in indexes:
                        print(f"        - {idx['name']}")
            else:
                print(f"    ✗ {tbl} - NOT FOUND")
        
        # Check column additions
        print("\n[3] Column Modifications:")
        if 'listings' in tables:
            cols = {col['name'] for col in inspector.get_columns('listings')}
            if 'party_id' in cols:
                print(f"    ✓ listings.party_id - EXISTS")
            else:
                print(f"    ✗ listings.party_id - MISSING")
        
        # Check user_accounts columns
        if 'user_accounts' in tables:
            cols = inspector.get_columns('user_accounts')
            print(f"    ✓ user_accounts columns:")
            for col in cols:
                print(f"      - {col['name']}: {col['type']}")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Database error: {e}")
        import traceback
        traceback.print_exc()

def show_recovery_steps():
    """Show possible recovery options."""
    print("\n" + "="*80)
    print("RECOVERY OPTIONS")
    print("="*80)
    
    print("""
If migrations are stuck, try these options:

OPTION 1: Skip to migration status (if all tables already exist)
  └─ Run: alembic stamp head
     This marks all migrations as applied without running them
     Use ONLY if all tables are already in the database

OPTION 2: Reset migrations completely (DESTRUCTIVE - requires database recreation)
  └─ Run: 
     1. Delete all tables from database (or drop/recreate database)
     2. alembic stamp base  (resets alembic tracking)
     3. alembic upgrade head  (run all migrations fresh)
     WARNING: This will delete all data!

OPTION 3: Verify migrations work before applying
  └─ Run: python validate_implementation.py
     This checks if models, routes, and schemas are correct

OPTION 4: Check database state
  └─ Run: python migration_recovery.py
     This script shows detailed database state analysis

For the current error about duplicate index:
  └─ The fixed migrations now check if tables exist before creating
  └─ Run: alembic upgrade head
     Should skip already-existing tables
""")

def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║               ZOIKO MIGRATION RECOVERY & DEBUGGING TOOL                    ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    check_database_state()
    show_recovery_steps()
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
1. Review the database state analysis above
2. Try running the migration again:
   alembic upgrade head

3. If migration still fails, check error message:
   - "relation already exists" → Table/index already there (fixed migration should handle)
   - "column already exists" → Column already there (fixed migration should handle)
   - Other error → Report with full error message

4. If needed, try recovery options above

For more help, run:
  python validate_implementation.py   (verify code structure)
  python run_migrations.py             (run migrations with detailed output)
  python migration_recovery.py         (this script)
    """)

if __name__ == "__main__":
    main()
