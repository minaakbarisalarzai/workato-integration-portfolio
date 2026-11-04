# Workato setup and schemas

This documentation describes the independently created demonstration recipes, not a portable Workato recipe export. Paste the relevant code into **Python snippets by Workato → Execute Python code**.

## 01 — Consolidated Python API recipe

**Name:** `API Integration — Consolidated Python Workflow (Optimized)`  
**Trigger:** Schedule, every 5 minutes (or use manual test without starting a recurring production recipe)  
**Step name:** Fetch and Validate Related API Resources  
**Python source:** [`../01-api-consolidation/optimized.py`](../01-api-consolidation/optimized.py)

Input schema (Workato field definition array):

```json
[
  {"name":"user_id","label":"User ID","type":"integer","optional":false},
  {"name":"post_id","label":"Post ID","type":"integer","optional":false},
  {"name":"expected_name","label":"Expected Name","type":"string","optional":false}
]
```

Test input: `user_id=1`, `post_id=1`, `expected_name=Leanne Graham`.

Output schema (minimal; nested summary can be extended through the Workato schema editor):

```json
[
  {"name":"success","type":"boolean"},
  {"name":"name_matches","type":"boolean"},
  {"name":"user_name","type":"string"},
  {"name":"posts_count","type":"integer"},
  {"name":"comments_count","type":"integer"},
  {"name":"todos_count","type":"integer"},
  {"name":"albums_count","type":"integer"},
  {"name":"completed_operations","type":"integer"},
  {"name":"error_count","type":"integer"},
  {"name":"error_message","type":"string"}
]
```

For fair monitoring comparisons, add an IF on `success=false` that routes to error reporting or fails/escalates the job as required. The actual one-step optimization screenshot does not include this branch.

## 02 — Customer webhook in both Base64 recipes

**Event name:** `customer_payload_received`.

Webhook object shape:

```json
{
  "payload": {
    "customer_id": 12345,
    "name": "Sara Khan",
    "email": "sara@example.com",
    "status": "active"
  }
}
```

Example parent object field definition (when Workato asks for an array `[]`):

```json
[
  {"name":"payload","label":"Payload","type":"object","optional":false,"properties":[
    {"name":"customer_id","label":"Customer ID","type":"integer"},
    {"name":"name","label":"Name","type":"string"},
    {"name":"email","label":"Email","type":"string"},
    {"name":"status","label":"Status","type":"string"}
  ]}
]
```

### Baseline — two Python actions

1. **Serialize JSON and Encode Base64**: schema above; use [`../02-native-formula/baseline_encoder.py`](../02-native-formula/baseline_encoder.py). Map webhook's `Payload` object into input `payload`; output schema:

```json
[{"name":"encoded_payload","label":"Encoded Payload","type":"string"}]
```

2. **Decode and Validate Base64 Payload**: use [`../02-native-formula/decoder.py`](../02-native-formula/decoder.py). Map the first Python step's `encoded_payload` into this step's encoded string field:

```json
[{"name":"encoded_data","label":"Encoded Data","type":"string","optional":false}]
```

### Optimized — one Python action

Use the **same decoder** and string input schema as above. Instead of using the first Python action, drag **Step 1 → Payload** into the input, switch to formula mode, and chain:

```ruby
.to_json.encode_base64
```

### Decoder output schema

```json
[
  {"name":"valid","type":"boolean"},
  {"name":"customer_id","type":"integer"},
  {"name":"customer_name","type":"string"},
  {"name":"email","type":"string"},
  {"name":"status","type":"string"},
  {"name":"decoded_payload","type":"object","properties":[
    {"name":"customer_id","type":"integer"},
    {"name":"name","type":"string"},
    {"name":"email","type":"string"},
    {"name":"status","type":"string"}
  ]},
  {"name":"message","type":"string"}
]
```

If your earlier Workato schema uses `payload` rather than `encoded_data` for the string input, the decoder supports either name. **Do not create both at the same time.**
