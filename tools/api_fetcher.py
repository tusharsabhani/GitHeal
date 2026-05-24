import os
import sys
import json
import argparse
import requests
import jsonschema

API_URL = "http://127.0.0.1:8000/api/data"
SPEC_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "api_spec.json")

# --- BEGIN SELF-HEALING ZONE ---
def normalize_payload(raw_data: dict) -> dict:
    """
    Maps raw API response keys to the standardized schema.
    Self-healing agents or scripts can modify this function's mapping.
    """
    return {
        "user_id": raw_data.get("user_id"),
        "full_name": raw_data.get("full_name"),
        "account_status": raw_data.get("account_status")
    }
# --- END SELF-HEALING ZONE ---

def load_schema():
    with open(SPEC_PATH, "r") as f:
        return json.load(f)

def fetch_raw_data():
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}", file=sys.stderr)
        sys.exit(1)

def validate_data(normalized_data, schema):
    try:
        jsonschema.validate(instance=normalized_data, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, e.message

def run_self_healing(raw_data, schema):
    print("Initiating automatic healing...")
    
    # Analyze raw data keys vs expected schema properties
    expected_properties = schema.get("properties", {}).keys()
    
    # We want to map raw keys to expected schema keys
    # Let's map potential drifts (e.g. display_name -> full_name, account_state -> account_status)
    potential_mappings = {
        "full_name": ["display_name", "name", "full_name"],
        "account_status": ["account_state", "status", "account_status"],
        "user_id": ["id", "user_id"]
    }
    
    mapping_code_lines = []
    for prop in expected_properties:
        candidates = potential_mappings.get(prop, [prop])
        # Find which candidate is in the raw data
        found_key = prop
        for cand in candidates:
            if cand in raw_data:
                found_key = cand
                break
        
        # Build mapping python line
        if found_key == prop:
            mapping_code_lines.append(f'        "{prop}": raw_data.get("{prop}")')
        else:
            # Heal case: map drifted key or fallback to original
            mapping_code_lines.append(f'        "{prop}": raw_data.get("{found_key}") or raw_data.get("{prop}")')

    # Now read this file and replace the normalize_payload body
    this_file_path = __file__
    with open(this_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "# --- BEGIN SELF-HEALING ZONE ---"
    end_marker = "# --- END SELF-HEALING ZONE ---"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("Self-healing markers not found in tools/api_fetcher.py!", file=sys.stderr)
        return False

    new_zone = (
        f"{start_marker}\n"
        f"def normalize_payload(raw_data: dict) -> dict:\n"
        f'    """\n'
        f"    Maps raw API response keys to the standardized schema.\n"
        f"    Self-healing agents or scripts can modify this function's mapping.\n"
        f'    """\n'
        f"    return {{\n"
        f"{',\n'.join(mapping_code_lines)}\n"
        f"    }}\n"
    )
    
    updated_content = content[:start_idx] + new_zone + content[end_idx:]
    
    with open(this_file_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
        
    print("Self-healing mapping successfully updated in tools/api_fetcher.py")
    return True

def main():
    parser = argparse.ArgumentParser(description="GitHeal API Fetcher & Schema Validator")
    parser.add_argument("--validate", action="store_true", help="Perform schema validation on raw data")
    parser.add_argument("--heal", action="store_true", help="Auto-remediate schema drift if validation fails")
    args = parser.parse_args()

    schema = load_schema()
    raw_data = fetch_raw_data()
    
    print(f"Raw API Data fetched: {json.dumps(raw_data)}")
    
    normalized = normalize_payload(raw_data)
    print(f"Normalized Data: {json.dumps(normalized)}")
    
    success, err_msg = validate_data(normalized, schema)
    
    if success:
        print("SUCCESS: Data complies with api_spec.json schema.")
        sys.exit(0)
    else:
        print(f"VALIDATION FAILURE: {err_msg}", file=sys.stderr)
        if args.heal:
            heal_success = run_self_healing(raw_data, schema)
            if heal_success:
                print("Re-validating with updated mapping...")
                sys.exit(2)
            else:
                sys.exit(1)
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()
