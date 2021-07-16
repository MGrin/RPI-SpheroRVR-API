import time
from flask_restful import Resource
from flask import request, make_response
from sphero_sdk import SpheroRvrObserver
from sphero_sdk import Colors
from sphero_sdk import RvrLedGroups

def LEDs(is_mock):
    class LEDsR(Resource):
        def get(self):
            leds = []
            colors = []

            for led in RvrLedGroups:
                leds.append(led.name)

            for color in Colors:
                colors.append(color.name)

            return {
                'leds': leds,
                'colors': colors
            }

        def put(self):
            data = request.get_json(force=True)
            if 'leds' not in data or 'colors' not in data:
                return make_response({ 'message': 'Wrong body format' })

            if len(data['leds']) != len(data['colors']):
                return make_response({ 'message': 'Wrong body format' })

            if is_mock:
                time.sleep(5)
                return { 'message': 'ok' }

            try:
                rvr = SpheroRvrObserver()
                rvr.wake()
                time.sleep(2)

                leds = []
                for led in data['leds']:
                    leds.append(RvrLedGroups[led])

                colors = []
                for color in data['colors']:
                    colors.append(Colors[color])
                
                rvr.led_control.set_multiple_leds_with_enums(
                    leds=leds,
                    colors=colors
                )
                time.sleep(1)
                rvr.close()
                return { 'message': 'ok' }
            except Exception as err:
                rvr.close()
                
                return make_response({ 'exception': str(err)}, 500)

    return LEDsR