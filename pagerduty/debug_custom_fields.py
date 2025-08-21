#!/usr/bin/env python3
"""
Debug script to test custom fields API for a specific incident
"""
import requests
import yaml
import json

# Load API token from config
with open('PagerDuty.yaml', 'r') as file:
    config = yaml.safe_load(file)
    api_token = config['token']

# Setup headers
headers = {
    "Authorization": f"Token token={api_token}",
    "Accept": "application/vnd.pagerduty+json;version=2"
}

incident_id = "Q0T1E3P7D80BUF"
url = f"https://api.pagerduty.com/incidents/{incident_id}/custom_fields/values"

print(f"🔍 Testing custom fields API for incident: {incident_id}")
print(f"📡 URL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"📋 Response Data:")
        print(json.dumps(data, indent=2))
        
        custom_fields = data.get("custom_fields", [])
        print(f"\n🔍 Processing {len(custom_fields)} custom fields:")
        
        result = {'resolution': None, 'prelim_root_cause': None}
        
        for i, field in enumerate(custom_fields):
            field_name = field.get('name', '').lower()
            field_value = field.get('value')
            
            print(f"   Field {i+1}:")
            print(f"     Name: '{field_name}'")
            print(f"     Value: '{field_value}'")
            
            if field_name == 'resolution' and field_value:
                result['resolution'] = field_value.lower().strip()
                print(f"     ✅ Matched 'resolution' field")
            elif field_name == 'prelim_root_cause' and field_value:
                result['prelim_root_cause'] = field_value.lower().strip()
                print(f"     ✅ Matched 'prelim_root_cause' field")
        
        print(f"\n📈 Final result:")
        print(f"   Resolution: {result['resolution']}")
        print(f"   Prelim Root Cause: {result['prelim_root_cause']}")
        print(f"   CCOE Resolved: {result['resolution'] == 'ccoe'}")
        print(f"   Infrastructure Caused: {bool(result['prelim_root_cause'])}")
        
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")