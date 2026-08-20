#!/usr/bin/env python
"""Run migrations with verbose output and error handling."""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("ALEMBIC MIGRATION RUNNER")
print("=" * 80)

# Step 1: Check current status
print("\n[STEP 1] Checking current migration status...")
result = subprocess.run(
    [sys.executable, "-m", "alembic", "current"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✓ Current migration status:")
    # Find the first line with revision
    for line in result.stdout.split('\n'):
        if 'Rev:' in line and 'head' in line:
            print(f"  {line.strip()}")
            break
else:
    print(f"✗ Error checking status:")
    print(result.stderr)

# Step 2: Try to run upgrade
print("\n[STEP 2] Running migration upgrade...")
print("Command: alembic upgrade head")
print("-" * 80)

result = subprocess.run(
    [sys.executable, "-m", "alembic", "upgrade", "head"],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)

if result.returncode == 0:
    print("\n✅ MIGRATION SUCCESSFUL")
else:
    print(f"\n❌ MIGRATION FAILED (exit code: {result.returncode})")
    print("\nTroubleshooting suggestions:")
    print("1. Check if user_accounts table already exists in database")
    print("2. Check if database connection is working")
    print("3. Review the error message above for specific issues")

# Step 3: Verify final status
print("\n[STEP 3] Verifying final migration status...")
result = subprocess.run(
    [sys.executable, "-m", "alembic", "current"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    for line in result.stdout.split('\n'):
        if 'Rev:' in line and 'head' in line:
            print(f"✓ Final status: {line.strip()}")
            break

print("\n" + "=" * 80)
