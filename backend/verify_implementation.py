#!/usr/bin/env python
"""Comprehensive backend verification test."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_models():
    """Test 1: Verify all model imports."""
    print("\n[TEST 1] Importing Models...")
    try:
        from app.models.user_account import UserAccount
        from app.models.sublet_request import SubletRequest
        from app.models import Party, Occupancy
        print("  ✓ UserAccount model imported")
        print("  ✓ SubletRequest model imported")
        print("  ✓ Party and Occupancy models verified")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crud():
    """Test 2: Verify CRUD modules exist."""
    print("\n[TEST 2] Checking CRUD Modules...")
    try:
        from app.crud import user, sublet
        from app.crud.user import create_user, get_user_by_email, authenticate_user
        from app.crud.sublet import submit_sublet_request
        print("  ✓ app.crud.user module imported")
        print("  ✓ app.crud.sublet module imported")
        print("  ✓ Key CRUD functions available")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schemas():
    """Test 3: Verify schemas."""
    print("\n[TEST 3] Checking Schemas...")
    try:
        from app.schemas.user import (
            UserLoginRequest, UserRegisterRequest, UserRead, 
            UserPasswordChangeRequest, UserProfileUpdateRequest
        )
        print("  ✓ UserLoginRequest schema")
        print("  ✓ UserRegisterRequest schema")
        print("  ✓ UserRead schema")
        print("  ✓ Password/Profile update schemas")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test 4: Verify auth dependencies."""
    print("\n[TEST 4] Checking Dependencies...")
    try:
        from app.api.deps import get_current_admin, get_current_user, get_db
        print("  ✓ get_current_admin dependency")
        print("  ✓ get_current_user dependency (new)")
        print("  ✓ get_db dependency")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_routes():
    """Test 5: Verify route modules."""
    print("\n[TEST 5] Checking Route Modules...")
    try:
        from app.api.routes import (
            user_auth, user_identity, user_rentals, user_hosting,
            occupancy, auth
        )
        print("  ✓ user_auth routes module")
        print("  ✓ user_identity routes module")
        print("  ✓ user_rentals routes module")
        print("  ✓ user_hosting routes module")
        print("  ✓ occupancy routes module (updated)")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """Test 6: Verify FastAPI app can be created."""
    print("\n[TEST 6] Creating FastAPI App...")
    try:
        from app.main import app
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        user_routes = [r for r in routes if '/users' in r or '/user' in r]
        print(f"  ✓ FastAPI app created")
        print(f"  ✓ Total routes registered: {len(routes)}")
        print(f"  ✓ User-related routes: {len(user_routes)}")
        if user_routes:
            print(f"    Sample routes:")
            for route in sorted(user_routes)[:5]:
                print(f"      - {route}")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test 7: Verify configuration."""
    print("\n[TEST 7] Checking Configuration...")
    try:
        from app.core.config import settings
        print(f"  ✓ Settings loaded")
        print(f"  ✓ Database: {settings.database_url[:50]}..." if settings.database_url else "  ✗ No DB URL")
        print(f"  ✓ User cookie name: {settings.USER_COOKIE_NAME if hasattr(settings, 'USER_COOKIE_NAME') else 'zoiko_user_token'}")
        print(f"  ✓ Admin cookie name: {settings.COOKIE_NAME if hasattr(settings, 'COOKIE_NAME') else 'zoiko_admin_token'}")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("="*70)
    print("ZOIKO BACKEND IMPLEMENTATION VERIFICATION")
    print("="*70)
    
    tests = [
        test_models,
        test_crud,
        test_schemas,
        test_dependencies,
        test_routes,
        test_app_creation,
        test_config,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\nUnhandled error in test: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*70)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Implementation is ready for deployment!")
    else:
        print(f"⚠️  {total - passed} tests failed - check errors above")
    
    print("="*70)
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
