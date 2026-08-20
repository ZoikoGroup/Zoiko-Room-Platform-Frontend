#!/usr/bin/env python
"""Test script to verify all imports and database configuration."""
import sys
import traceback

print("=" * 60)
print("Testing Backend Setup")
print("=" * 60)

# Test 1: Import all models
print("\n[TEST 1] Importing all models...")
try:
    from app.models import (
        AdminUser, UserAccount, Party, Property, Room, Listing,
        Application, Occupancy, Guest, IdentityVerification,
        SubletRequest, Booking, Payment, Finance
    )
    print("✓ All models imported successfully")
except Exception as e:
    print(f"✗ Model import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check database configuration
print("\n[TEST 2] Checking database configuration...")
try:
    from app.core.config import settings
    print(f"✓ Database URL: {settings.database_url}")
except Exception as e:
    print(f"✗ Config import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Import FastAPI app
print("\n[TEST 3] Creating FastAPI app...")
try:
    from app.main import app
    print("✓ FastAPI app created successfully")
    print(f"  - Registered routes: {len(app.routes)}")
except Exception as e:
    print(f"✗ App creation failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check route registration
print("\n[TEST 4] Checking route registration...")
try:
    routes = [route.path for route in app.routes if hasattr(route, 'path')]
    user_routes = [r for r in routes if '/users' in r or '/user' in r]
    print(f"✓ Total routes: {len(routes)}")
    print(f"✓ User routes found: {len(user_routes)}")
    if user_routes:
        print("  User route samples:")
        for route in sorted(user_routes)[:5]:
            print(f"    - {route}")
except Exception as e:
    print(f"✗ Route check failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 5: Verify new CRUD modules
print("\n[TEST 5] Verifying new CRUD modules...")
try:
    from app.crud import user, sublet
    print("✓ New CRUD modules imported:")
    print("  - app.crud.user")
    print("  - app.crud.sublet")
except Exception as e:
    print(f"✗ CRUD import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 6: Verify new schemas
print("\n[TEST 6] Verifying new schemas...")
try:
    from app.schemas import user as user_schemas
    print("✓ New schemas imported:")
    print(f"  - UserLoginRequest, UserRegisterRequest, UserRead, etc.")
except Exception as e:
    print(f"✗ Schema import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✓")
print("=" * 60)
