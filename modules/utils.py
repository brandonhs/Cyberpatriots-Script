import json

def format_json(obj):
    return json.dumps(obj, indent=4, separators=(',', ': '))
