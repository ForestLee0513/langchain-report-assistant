import json


def error_json(message: str) -> str:
    return json.dumps({"error": message}, ensure_ascii=False)