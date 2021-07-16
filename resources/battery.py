from sphero_sdk import SpheroRvrObserver
import time
from datetime import datetime
from flask_restful import Resource
from uuid import uuid4

values = {}

CACHE_TTL = 120

CACHED_VALUE = None
CACHED_TIME = None
def get_battery_percentage(tnx):
    global CACHED_VALUE
    global CACHED_TIME
    global CACHE_TTL

    if CACHED_VALUE is not None and (datetime.now() - CACHED_TIME).seconds < CACHE_TTL:
        return CACHED_VALUE

    rvr = SpheroRvrObserver()

    def battery_percentage_handler(battery_percentage):
        values[tnx] = { 'battery': battery_percentage }

    rvr.wake()
    time.sleep(1)
    rvr.get_battery_percentage(handler=battery_percentage_handler)
    
    while tnx not in values:
        time.sleep(0.5)
    
    rvr.close()
    CACHED_VALUE = values[tnx]
    CACHED_TIME = datetime.now()
    return CACHED_VALUE

def Battery(is_mock):
    class BatteryR(Resource):
        def get(self):
            tnx = uuid4()
            result = get_battery_percentage(tnx)
            if tnx in values:
                del values[tnx]
            return result
    return BatteryR