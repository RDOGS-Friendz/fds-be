from datetime import date, datetime
import fastapi


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat() + 'Z'


def SuccessResponse():
    return fastapi.responses.JSONResponse(content={"detail": "Success"})
