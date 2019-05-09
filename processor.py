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
import json
import math
import glob
import fire
import datetime
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



def comp_images(image_pattern, camera, focal, artist):
    '''
    '''
    images = glob.glob(image_pattern)
    for img in progressbar.progressbar(images):
        #- make background
        back_image = create_back_image(img)

        #- up - left
        _text = u'Cam: {0}'.format(camera)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_UL)
        _size = _font.getsize(_text)
        _pos  = (Env.TEXT_BOUND, Env.MASK_HEIGHT*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- up - middle
        # _text = u'{0} x {1}'.format(fore_image.width, fore_image.height)
        # _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_UM)
        # _size = _font.getsize(_text)
        # _pos = ((back_image.width - _size[0]) / 2, Env.MASK_HEIGHT*0.5 - _size[1]*0.55)
        # draw_text(back_image, _pos, _text, _font)

        #- up - right
        _text = u'Focal: {0}'.format(focal)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_UR)
        _size = _font.getsize(_text)
        _pos = (back_image.width - _size[0] - Env.TEXT_BOUND, Env.MASK_HEIGHT*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- down - left
        _now = datetime.datetime.now()
        _text = u'Date: {0:0>4}-{1:0>2}-{2:0>2}'.format(_now.year, _now.month, _now.day)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_DL)
        _size = _font.getsize(_text)
        _pos = (Env.TEXT_BOUND, back_image.height - Env.MASK_HEIGHT*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- down - middle
        _text = u'Artist: {0}'.format(artist)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_DM)
        _size = _font.getsize(_text)
        _pos = ((back_image.width - _size[0]) / 2, back_image.height - Env.MASK_HEIGHT*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- down - right
        curt_frame = re.search('\.\d+\.', os.path.basename(img)).group()[1:-1]
        last_frame = re.search('\.\d+\.', os.path.basename(images[-1])).group()[1:-1]
        _text = u'Frame: {0}/{1}'.format(curt_frame, last_frame)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_DR)
        _size = _font.getsize(_text)        
        _pos = (back_image.width - _size[0] - Env.TEXT_BOUND, back_image.height - Env.MASK_HEIGHT*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- save images
        back_image.save(img)
        back_image.close()




def comp_video(image_pattern, output, audio=None):
    '''
    '''
    sequence = image_pattern.replace('?', '@')
    if audio and os.path.isfile(audio):
        sequence = u'[ {0} {1} ]'.format(sequence, audio)

    commands = [Env.RVIO_BIN,
                sequence,
                u'-outfps {0}'.format(Env.VIDEO_FPS),
                u'-codec {0}'.format(Env.VIDEO_CODEC),
                u'-outparams vcc:bf=0',
                u'-quality 1.0',
                u'-o {0}'.format(output),
                u'-rthreads {0}'.format(Env.RV_R_THREADING),
                u'-wthreads {0}'.format(Env.RV_W_TRHEADING),
                u'-v']

    subprocess.check_call(' '.join(commands).encode('utf-8'))




def comp_blast_video(info_file):
    '''
    '''
    with open(Env.MOTD_FILE, 'r') as f:
        sys.stdout.write(f.read().decode('utf-8'))
    sys.stdout.write('\n')

    info_data = dict()
    with open(info_file, 'r') as f:
        info_data = json.load(f)

    comp_images(info_data['ImagePattern'], info_data['Camera'], info_data['Focal'], info_data['Artist'])
    comp_video(info_data['ImagePattern'],  info_data['Output'], info_data['Audio'])



if __name__ == '__main__':
    fire.Fire({
        'comp_images': comp_images,
        'comp_video': comp_video,
        'comp_blast_video': comp_blast_video
    })
