# coding: utf-8
#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Thu Apr 11 15:11:43 2019
#========================================
import sys
import os
import re
import imp
import math
import datetime
import glob
import fire
import subprocess
import progressbar
from PIL import Image, ImageDraw, ImageFont

if os.path.basename(sys.executable) == 'python.exe':
    Env = imp.load_source('Env', os.path.join(os.path.dirname(__file__), 'blasterEnv.py'))
else:
    Env = imp.load_source('Env', os.path.join(os.path.dirname(sys.executable), 'blasterEnv.py'))
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
def create_back_image(image):
    '''
    '''
    fore_image = Image.open(image)

    back_width, back_height = fore_image.width, fore_image.height + Env.MASK_HEIGHT*2
    back_width  = int(math.ceil(back_width  / 2.0) * 2)
    back_height = int(math.ceil(back_height / 2.0) * 2)

    back_image = Image.new('RGB', (back_width, back_height), Env.MASK_COLOR)
    back_image.paste(fore_image.resize((back_image.width, fore_image.height)), (0, Env.MASK_HEIGHT))
    fore_image.close()

    return back_image



def draw_text(image, pos, text, _font):
    '''
    '''
    draw = ImageDraw.Draw(image)
    draw.text(pos, text, font=_font, fill=Env.TEXT_COLOR)
    return True



def add_text(image_pattrn, camera, focal, artist):
    '''
    '''
    with open(Env.MOTD_FILE, 'r') as f:
        sys.stdout.write(f.read().decode('utf-8'))
    sys.stdout.write('\n')

    images = glob.glob(image_pattrn)
    for img in progressbar.progressbar(images):
        #- make background
        back_image = create_back_image(img)

        #- up - left
        _text = 'Cam: {0}'.format(camera)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_UL)
        _size = _font.getsize(_text)
        _pos  = (Env.TEXT_BOUND, Env.MASK_HEIGHT*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- up - middle
        # _text = '{0} x {1}'.format(fore_image.width, fore_image.height)
        # _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_UM)
        # _size = _font.getsize(_text)
        # _pos = ((back_image.width - _size[0]) / 2, Env.MASK_HEIGHT*0.5 - _size[1]*0.55)
        # draw_text(back_image, _pos, _text, _font)

        #- up - right
        _text = 'Focal: {0}'.format(focal)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_UR)
        _size = _font.getsize(_text)
        _pos = (back_image.width - _size[0] - Env.TEXT_BOUND, Env.MASK_HEIGHT*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- down - left
        _now = datetime.datetime.now()
        _text = 'Date: {0:0>4}-{1:0>2}-{2:0>2}'.format(_now.year, _now.month, _now.day)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_DL)
        _size = _font.getsize(_text)
        _pos = (Env.TEXT_BOUND, back_image.height - Env.MASK_HEIGHT*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- down - middle
        _text = 'Artist: {0}'.format(artist)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_DM)
        _size = _font.getsize(_text)
        _pos = ((back_image.width - _size[0]) / 2, back_image.height - Env.MASK_HEIGHT*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- down - right
        curt_frame = re.search('\.\d+\.', os.path.basename(img)).group()[1:-1]
        last_frame = re.search('\.\d+\.', os.path.basename(images[-1])).group()[1:-1]
        _text = 'Frame: {0:0>4}/{1:0>4}'.format(curt_frame, last_frame)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_DR)
        _size = _font.getsize(_text)        
        _pos = (back_image.width - _size[0] - Env.TEXT_BOUND, back_image.height - Env.MASK_HEIGHT*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- save images
        back_image.save(img)
        back_image.close()




def comp_to_video(image_pattrn, output, audio=None, view_output=False):
    '''
    '''
    with open(Env.MOTD_FILE, 'r') as f:
        sys.stdout.write(f.read().decode('utf-8'))
    sys.stdout.write('\n')

    sequence = image_pattrn
    if audio and os.path.isfile(audio):
        sequence = '[ {0} {1} ]'.format(image_pattrn, audio)

    commands = [Env.RVIO_BIN,
                sequence,
                '-outfps {0}'.format(Env.VIDEO_FPS),
                '-codec {0}'.format(Env.VIDEO_CODEC),
                '-outparams vcc:bf=0',
                '-quality 1.0',
                '-o {0}'.format(output),
                '-rthreads {0}'.format(Env.RV_R_THREADING),
                '-wthreads {0}'.format(Env.RV_W_TRHEADING),
                '-v']

    subprocess.check_call(' '.join(commands))

    #- view video
    if view_output:
        view_commands = [Env.RV_BIN, output]
        subprocess.Popen(' '.join(view_commands))



if __name__ == '__main__':
    fire.Fire({
        'add_text': add_text,
        'comp_to_video': comp_to_video
    })
