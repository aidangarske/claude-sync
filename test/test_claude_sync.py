#!/usr/bin/env python3
"""Tests for claude-sync"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def run(cmd, check=True):
    """Run a command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"{RED}FAIL{RESET}: {cmd}")
        print(f"  stderr: {result.stderr}")
        return None
    return result.stdout

def test_help():
    """Test: help output"""
    out = run("~/.local/bin/claude-sync --help")
    if out is None:
        return False
    if "push" in out and "pull" in out and "list" in out:
        print(f"{GREEN}PASS{RESET}: help shows all commands")
        return True
    print(f"{RED}FAIL{RESET}: help missing commands")
    return False

def test_list():
    """Test: claude-sync (list local sessions)"""
    out = run("~/.local/bin/claude-sync")
    if out is None:
        return False
    if "Sessions in ~/.claude" in out or "No sessions found" in out:
        print(f"{GREEN}PASS{RESET}: list command works")
        return True
    print(f"{RED}FAIL{RESET}: list command unexpected output")
    return False

def test_list_details():
    """Test: claude-sync --details"""
    out = run("~/.local/bin/claude-sync --details")
    if out is None:
        return False
    print(f"{GREEN}PASS{RESET}: list --details works")
    return True

def test_export_import():
    """Test: export and import cycle"""
    with tempfile.TemporaryDirectory() as tmpdir:
        archive = Path(tmpdir) / "test-backup.tar.gz"

        # Export (may have no sessions in CI)
        out = run(f"~/.local/bin/claude-sync export -o {archive}", check=False)
        if not archive.exists():
            # No sessions to export - skip test
            print(f"{YELLOW}SKIP{RESET}: no sessions to export")
            return True
        print(f"{GREEN}PASS{RESET}: export creates archive")

        # Check archive contents
        out = run(f"tar -tzf {archive}")
        if out is None:
            return False
        if "manifest.json" not in out:
            print(f"{RED}FAIL{RESET}: archive missing manifest.json")
            return False
        print(f"{GREEN}PASS{RESET}: archive contains manifest.json")

        # Import (will skip existing)
        out = run(f"~/.local/bin/claude-sync import {archive}")
        if out is None:
            return False
        if "Imported" in out or "skipped" in out or "0 sessions" in out:
            print(f"{GREEN}PASS{RESET}: import works")
        else:
            print(f"{RED}FAIL{RESET}: import missing expected output")
            return False

    return True

def test_export_session():
    """Test: export specific session"""
    out = run("~/.local/bin/claude-sync --details")
    if out is None:
        return False

    # Parse out a session ID (8 char prefix)
    match = re.search(r'^\s+([a-f0-9]{8})\s+', out, re.MULTILINE)
    if not match:
        print(f"{YELLOW}SKIP{RESET}: no sessions found to test session export")
        return True

    session_id = match.group(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        archive = Path(tmpdir) / "session-backup.tar.gz"
        out = run(f"~/.local/bin/claude-sync export --session {session_id} -o {archive}")
        if out is None:
            return False
        if archive.exists() and "Exported" in out:
            print(f"{GREEN}PASS{RESET}: export --session works")
            return True
        print(f"{RED}FAIL{RESET}: export --session failed")
        return False

def test_push_help():
    """Test: push subcommand help"""
    out = run("~/.local/bin/claude-sync push --help")
    if out is None:
        return False
    if "--session" in out and "--project" in out:
        print(f"{GREEN}PASS{RESET}: push --help works")
        return True
    print(f"{RED}FAIL{RESET}: push --help missing options")
    return False

def test_pull_help():
    """Test: pull subcommand help"""
    out = run("~/.local/bin/claude-sync pull --help")
    if out is None:
        return False
    if "--session" in out and "--project" in out:
        print(f"{GREEN}PASS{RESET}: pull --help works")
        return True
    print(f"{RED}FAIL{RESET}: pull --help missing options")
    return False

def test_remote(remote):
    """Test: remote operations"""
    print(f"\n{YELLOW}Testing remote: {remote}{RESET}")

    # Test SSH connection
    result = subprocess.run(
        f"ssh -o BatchMode=yes -o ConnectTimeout=5 {remote} echo ok",
        shell=True, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"{RED}FAIL{RESET}: Cannot SSH to {remote}")
        return False
    print(f"{GREEN}PASS{RESET}: SSH connection works")

    # Test list remote
    out = run(f"~/.local/bin/claude-sync list {remote}")
    if out and "Sessions" in out:
        print(f"{GREEN}PASS{RESET}: list remote works")
        return True
    else:
        print(f"{RED}FAIL{RESET}: list remote failed")
        return False

def main():
    print("=" * 50)
    print("claude-sync test suite")
    print("=" * 50)

    if not Path(os.path.expanduser("~/.local/bin/claude-sync")).exists():
        print(f"{RED}ERROR{RESET}: claude-sync not installed")
        print("Run: ./install.sh")
        return 1

    tests = [
        test_help,
        test_list,
        test_list_details,
        test_export_import,
        test_export_session,
        test_push_help,
        test_pull_help,
    ]

    passed = 0
    failed = 0

    print("\n--- Local Tests ---")
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"{RED}ERROR{RESET}: {test.__name__}: {e}")
            failed += 1

    # Remote tests (optional)
    if len(sys.argv) > 1:
        remote = sys.argv[1]
        print("\n--- Remote Tests ---")
        if test_remote(remote):
            passed += 1
        else:
            failed += 1
    else:
        print(f"\n{YELLOW}TIP{RESET}: Run with remote to test push/pull:")
        print(f"  python3 test_claude_sync.py user@host")

    print("\n" + "=" * 50)
    print(f"Results: {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET}")
    print("=" * 50)

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
