import json
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        return super().default(obj)

def dumps_json(data: dict) -> str:
    return json.dumps(data, cls=CustomJSONEncoder, indent=2, ensure_ascii=False)
