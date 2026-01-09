"""
Quick validation script for Freshservice connector.
Can be run without pytest to do basic smoke testing.

Usage:
    python3 sources/freshservice/test/validate_connector.py
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sources.freshservice.freshservice import LakeflowConnect


def load_config(config_path):
    """Load configuration from JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)


def validate_connector():
    """Run basic validation tests."""
    print("=" * 80)
    print("Freshservice Connector Validation")
    print("=" * 80)
    
    # Load config
    parent_dir = Path(__file__).parent.parent
    config_path = parent_dir / "configs" / "dev_config.json"
    
    print(f"\n1. Loading configuration from: {config_path}")
    try:
        config = load_config(config_path)
        if not config.get("api_key") or not config.get("domain"):
            print("   ❌ ERROR: Please fill in api_key and domain in dev_config.json")
            return False
        print(f"   ✅ Configuration loaded (domain: {config['domain']})")
    except Exception as e:
        print(f"   ❌ ERROR: Failed to load config: {e}")
        return False
    
    # Initialize connector
    print("\n2. Initializing connector...")
    try:
        connector = LakeflowConnect(config)
        print("   ✅ Connector initialized successfully")
    except Exception as e:
        print(f"   ❌ ERROR: Failed to initialize: {e}")
        return False
    
    # Test list_tables
    print("\n3. Testing list_tables()...")
    try:
        tables = connector.list_tables()
        print(f"   ✅ Found {len(tables)} tables")
        print(f"   Tables: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")
    except Exception as e:
        print(f"   ❌ ERROR: list_tables failed: {e}")
        return False
    
    # Test get_table_schema for one table
    print("\n4. Testing get_table_schema() for 'tickets'...")
    try:
        schema = connector.get_table_schema("tickets", {})
        print(f"   ✅ Schema retrieved ({len(schema.fields)} fields)")
        print(f"   Sample fields: {', '.join([f.name for f in schema.fields[:5]])}...")
    except Exception as e:
        print(f"   ❌ ERROR: get_table_schema failed: {e}")
        return False
    
    # Test read_table_metadata
    print("\n5. Testing read_table_metadata() for 'tickets'...")
    try:
        metadata = connector.read_table_metadata("tickets", {})
        print(f"   ✅ Metadata retrieved")
        print(f"   Primary keys: {metadata.get('primary_keys')}")
        print(f"   Ingestion type: {metadata.get('ingestion_type')}")
        print(f"   Cursor field: {metadata.get('cursor_field', 'N/A')}")
    except Exception as e:
        print(f"   ❌ ERROR: read_table_metadata failed: {e}")
        return False
    
    # Test read_table (fetch small amount)
    print("\n6. Testing read_table() for 'tickets' (limited to 1 page)...")
    try:
        records_iter, offset = connector.read_table(
            "tickets",
            {},
            {"per_page": "10", "max_pages_per_batch": "1"}
        )
        records = list(records_iter)
        print(f"   ✅ Read completed: {len(records)} records")
        if records:
            print(f"   Sample record keys: {', '.join(list(records[0].keys())[:5])}...")
        print(f"   Offset: {offset}")
    except Exception as e:
        print(f"   ❌ ERROR: read_table failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test a snapshot table
    print("\n7. Testing snapshot table 'groups'...")
    try:
        schema = connector.get_table_schema("groups", {})
        metadata = connector.read_table_metadata("groups", {})
        records_iter, offset = connector.read_table(
            "groups",
            {},
            {"per_page": "10", "max_pages_per_batch": "1"}
        )
        records = list(records_iter)
        print(f"   ✅ Groups table: {len(records)} records")
    except Exception as e:
        print(f"   ❌ ERROR: groups table failed: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✅ All validation tests passed!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = validate_connector()
    sys.exit(0 if success else 1)

