from sphero_sdk import SpheroRvrObserver
import time
from datetime import datetime
from flask import request, make_response
from flask_restful import Resource
from math import sqrt

ACTIVE_MOVEMENT = None
GLOBAL_STOP = False
MAX_MOVEMENT_OPERATIONS = 20


# This wrapper function implements a simple way to send a drive to position command
# and then wait for the move to complete
def drive_wait_to_complete(rvr, yaw, speed):
    rvr.drive_rc_si_units(
        linear_velocity=speed,     # Valid velocity values are in the range of [-2..2] m/s
        yaw_angular_velocity=yaw, # RVR will spin at up to 624 degrees/s.  Values outside of [-624..624] will saturate internally.
        flags=0
    )
    
    time.sleep(1.05)

def Movement(is_mock):
    class MovementR(Resource):
        def get(self):
            global ACTIVE_MOVEMENT
            if ACTIVE_MOVEMENT:
                return ACTIVE_MOVEMENT
            return make_response({ 'message': 'No active movement' }, 404)

        def delete(self):
            global ACTIVE_MOVEMENT
            global GLOBAL_STOP

            if ACTIVE_MOVEMENT is None:
                return make_response({ 'message': 'No active movement' }, 404)
            
            GLOBAL_STOP = True

        def post(self):
            global ACTIVE_MOVEMENT

            if ACTIVE_MOVEMENT is not None:
                return make_response({ 'message': 'RVR is already moving, wait for your turn!' }, 400)

            data = request.get_json(force=True)
            if not isinstance(data, list):
                return make_response({ 'message': 'Wrong movement format' }, 400)
            
            if len(data) > MAX_MOVEMENT_OPERATIONS:
                return make_response({ 'message': 'Too many commands, max is ' + str(MAX_MOVEMENT_OPERATIONS) }, 400)

            for move in data:
                if 'yaw' not in move or 'speed' not in move:
                    return make_response({ 'message': 'Wrongs movement format: ' + str(move) }, 400)

            start = datetime.now()

            if is_mock:
                time.sleep(10)
                return make_response({ 'seconds': (datetime.now() - start).seconds})

            try:
                rvr = SpheroRvrObserver()
                rvr.wake()
                time.sleep(2)

                rvr.reset_yaw()
                time.sleep(.1)

                rvr.set_custom_control_system_timeout(command_timeout=1000)

                for move in data:
                    if GLOBAL_STOP:
                        break

                    ACTIVE_MOVEMENT = move
                    drive_wait_to_complete(rvr, ACTIVE_MOVEMENT['yaw'], ACTIVE_MOVEMENT['speed'])

                ACTIVE_MOVEMENT = None
                rvr.close()

                return make_response({ 'seconds': (datetime.now() - start).seconds})
            except Exception as err:
                rvr.close()
                return make_response({ 'exception': str(err)}, 500)

                
    return MovementR