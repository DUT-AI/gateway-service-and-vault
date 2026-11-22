import os
import threading
import time

from dut_vault_sdk.store import InMemoryConfigStore


def test_in_memory_config_store_basic_operations():
    store = InMemoryConfigStore(inject_environ=False)
    assert store.get("NON_EXISTENT") is None

    store.update_bulk({"PORT": "8080", "ENV": "production"}, version=1)
    assert store.get("PORT") == "8080"
    assert store.get("ENV") == "production"
    assert store.version == 1
    assert store.get_all() == {"PORT": "8080", "ENV": "production"}


def test_in_memory_config_store_injects_into_environ():
    key = "TEST_DUT_VAULT_KEY_XYZ"
    if key in os.environ:
        del os.environ[key]

    store = InMemoryConfigStore(inject_environ=True)
    store.update_bulk({key: "value_123"})
    assert os.environ.get(key) == "value_123"

    store.clear()
    assert key not in os.environ


def test_in_memory_config_store_on_change_callbacks():
    store = InMemoryConfigStore(inject_environ=False)
    changes = []

    def handle_db_change(key: str, old_val: str | None, new_val: str):
        changes.append((key, old_val, new_val))

    store.on_change("DATABASE_URL", handle_db_change)

    # Initial set
    store.update_bulk({"DATABASE_URL": "postgresql://first"})
    assert changes == [("DATABASE_URL", None, "postgresql://first")]

    # Update value
    store.update_bulk({"DATABASE_URL": "postgresql://second"})
    assert changes == [
        ("DATABASE_URL", None, "postgresql://first"),
        ("DATABASE_URL", "postgresql://first", "postgresql://second"),
    ]

    # No change should not trigger callback
    store.update_bulk({"DATABASE_URL": "postgresql://second"})
    assert len(changes) == 2


def test_in_memory_config_store_thread_safety():
    store = InMemoryConfigStore(inject_environ=False)
    num_threads = 10
    updates_per_thread = 100

    def worker(worker_id: int):
        for i in range(updates_per_thread):
            store.update_bulk({f"KEY_{worker_id}": str(i)})
            time.sleep(0.0001)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    all_data = store.get_all()
    assert len(all_data) == num_threads
    for i in range(num_threads):
        assert all_data[f"KEY_{i}"] == str(updates_per_thread - 1)
