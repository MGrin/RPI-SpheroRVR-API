from flask_restful import Resource
import sys
import os
from waveshare_epd import epd2in13bc
from PIL import Image,ImageDraw,ImageFont
from flask import request, make_response
from datetime import datetime

fontsdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'fonts')
epd = epd2in13bc.EPD()
epd.init()

font20 = ImageFont.truetype(os.path.join(fontsdir, 'Font.ttc'), 20)
font18 = ImageFont.truetype(os.path.join(fontsdir, 'Font.ttc'), 18)

LAST_IMAGE = None

def Screen(is_mock):
    class ScreenR(Resource):
        def put(self):
            data = request.get_json(force=True)
            if 'text' not in data:
                return make_response({ 'message': 'No text provided' })

            message = data['text']
            font_size = data.get('size', 18)
            font = ImageFont.truetype(os.path.join(fontsdir, 'Font.ttc'), font_size)

            message_splitted = message.split(' ')

            LBlackimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
            LRYimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298

            drawblack = ImageDraw.Draw(LBlackimage)
            drawry = ImageDraw.Draw(LRYimage)

            idx = 0
            chars = 0
            lines = 0
            max_symbols = 124 / font_size

            for m in message_splitted:
                drawblack.text((2, lines * font_size + 2), m, font = font, fill = 0)
                lines += 1

            drawry.line((0, 276, 128, 278), fill=0)
            drawry.text((2, 280), datetime.now().strftime('HH:SS'), font=font18, fill = 0)

            LBlackimage = LBlackimage.rotate(180)
            LRYimage = LRYimage.rotate(180)

            LAST_IMAGE = LBlackimage
            
            if not is_mock:
                epd.display(epd.getbuffer(LBlackimage), epd.getbuffer(LRYimage))
            
            return { 'message': 'ok' }
    return ScreenR