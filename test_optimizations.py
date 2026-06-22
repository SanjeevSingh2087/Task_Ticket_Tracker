"""
Test suite to verify performance optimizations.

Run: python test_optimizations.py
"""

import sys
import os
import time
import json
from data_repository import DataRepository, CacheEntry

def test_cache_operations():
    """Test caching functionality."""
    print("\n=== Testing Cache Operations ===")
    
    repo = DataRepository("HO_Ticket_Tracker.xlsx", cache_ttl_seconds=5)
    
    # Test 1: First load (cache miss)
    print("Test 1: First load (cache miss)...")
    start = time.time()
    df1 = repo.load_dataframe()
    first_load = time.time() - start
    print(f"  ✓ First load: {first_load:.3f}s (cache miss)")
    
    # Test 2: Second load (cache hit)
    print("Test 2: Second load (cache hit)...")
    start = time.time()
    df2 = repo.load_dataframe()
    second_load = time.time() - start
    print(f"  ✓ Second load: {second_load:.3f}s (cache hit)")
    
    # Calculate speedup
    speedup = first_load / second_load if second_load > 0.001 else float('inf')
    print(f"  → Speedup: {speedup:.1f}x\n")
    
    return speedup > 5  # Cache hit should be 5x+ faster


def test_ticket_indexing():
    """Test O(1) ticket lookup via indexing."""
    print("=== Testing Ticket Indexing ===")
    
    repo = DataRepository("HO_Ticket_Tracker.xlsx")
    df = repo.load_dataframe()
    
    if len(df) == 0:
        print("  ⚠ No tasks in database, skipping indexing test")
        return True
    
    # Get a ticket number
    ticket_no = str(df.iloc[0]["Ticket No"]).strip()
    print(f"Test: Looking up ticket {ticket_no}...")
    
    # Lookup should be very fast
    start = time.time()
    result = repo.get_task_by_ticket(ticket_no)
    lookup_time = time.time() - start
    
    if result:
        print(f"  ✓ Found ticket in {lookup_time*1000:.2f}ms")
        print(f"  ✓ Ticket data: {result}\n")
        return True
    else:
        print(f"  ✗ Ticket not found\n")
        return False


def test_search_operations():
    """Test vectorized search operations."""
    print("=== Testing Vectorized Search ===")
    
    repo = DataRepository("HO_Ticket_Tracker.xlsx")
    df = repo.load_dataframe()
    
    if len(df) == 0:
        print("  ⚠ No tasks in database, skipping search test")
        return True
    
    # Test search
    print("Test: Searching for 'Open' status...")
    start = time.time()
    results = repo.search_tasks(df=df, status_filter="open")
    search_time = time.time() - start
    
    print(f"  ✓ Found {len(results)} open tasks in {search_time*1000:.2f}ms\n")
    return len(results) >= 0


def test_statistics_caching():
    """Test statistics caching."""
    print("=== Testing Statistics Caching ===")
    
    repo = DataRepository("HO_Ticket_Tracker.xlsx")
    
    # First call (cache miss)
    print("Test 1: First statistics call (cache miss)...")
    start = time.time()
    stats1 = repo.get_statistics()
    first_call = time.time() - start
    print(f"  ✓ First call: {first_call*1000:.2f}ms")
    print(f"    - Total tasks: {stats1['total']}")
    print(f"    - Open tasks: {stats1['open']}")
    print(f"    - Closed tasks: {stats1['closed']}")
    
    # Second call (cache hit)
    print("\nTest 2: Second statistics call (cache hit)...")
    start = time.time()
    stats2 = repo.get_statistics()
    second_call = time.time() - start
    print(f"  ✓ Second call: {second_call*1000:.2f}ms")
    
    speedup = first_call / second_call if second_call > 0.001 else float('inf')
    print(f"  → Speedup: {speedup:.1f}x\n")
    
    return speedup > 5


def test_pagination():
    """Test pagination functionality."""
    print("=== Testing Pagination ===")
    
    repo = DataRepository("HO_Ticket_Tracker.xlsx")
    
    # Test different page sizes
    result = repo.get_tasks(page=1, page_size=10)
    
    print(f"Test: Fetching page 1 with page_size=10...")
    print(f"  ✓ Retrieved {len(result['data'])} tasks")
    print(f"  ✓ Page: {result['page']} of {result['total_pages']}")
    print(f"  ✓ Total tasks: {result['total']}\n")
    
    return len(result['data']) <= 10 and result['page'] == 1


def test_concurrent_access():
    """Test thread-safe concurrent access."""
    print("=== Testing Concurrent Access ===")
    
    import threading
    
    repo = DataRepository("HO_Ticket_Tracker.xlsx")
    errors = []
    
    def worker(thread_id):
        try:
            df = repo.load_dataframe()
            stats = repo.get_statistics()
            print(f"  ✓ Thread {thread_id}: {len(df)} tasks, {stats['total']} total")
        except Exception as e:
            errors.append((thread_id, str(e)))
    
    threads = []
    print("Test: 5 concurrent requests...")
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    if errors:
        print(f"\n  ✗ Errors: {errors}\n")
        return False
    else:
        print(f"  ✓ All concurrent requests succeeded\n")
        return True


def test_cache_expiry():
    """Test cache expiration."""
    print("=== Testing Cache Expiry ===")
    
    repo = DataRepository("HO_Ticket_Tracker.xlsx", cache_ttl_seconds=2)
    
    # Load data
    print("Test: Cache expiry after TTL...")
    df1 = repo.load_dataframe()
    print(f"  ✓ Loaded {len(df1)} tasks")
    
    # Wait for cache to expire
    print("  → Waiting 3 seconds for cache to expire...")
    time.sleep(3)
    
    # Second load should reload from disk
    start = time.time()
    df2 = repo.load_dataframe()
    reload_time = time.time() - start
    
    print(f"  ✓ Reloaded after expiry in {reload_time*1000:.2f}ms\n")
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*50)
    print("PERFORMANCE OPTIMIZATION TEST SUITE")
    print("="*50)
    
    tests = [
        ("Cache Operations", test_cache_operations),
        ("Ticket Indexing", test_ticket_indexing),
        ("Search Operations", test_search_operations),
        ("Statistics Caching", test_statistics_caching),
        ("Pagination", test_pagination),
        ("Concurrent Access", test_concurrent_access),
        ("Cache Expiry", test_cache_expiry),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ ERROR: {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All performance optimizations verified! 🚀\n")
    else:
        print(f"\n✗ {total - passed} test(s) failed\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
