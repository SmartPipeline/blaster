# coding: utf-8
#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Thu Apr 11 15:11:43 2019
#========================================
import sys, os, datetime, imp
import subprocess
from PIL import Image, ImageDraw, ImageFont
import fire
try:
    Env = imp.load_source('Env', os.path.join(os.path.dirname(__file__), 'blasterEnv.py'))
except:
    Env = imp.load_source('Env', os.path.join(os.path.dirname(sys.executable), 'blasterEnv.py'))
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+


def draw_text(draw, pos, text, text_font):
    '''
    '''
    draw.text(pos, text, font=text_font, fill=Env.TEXT_COLOR)


def add_text(imageDir, camera, focal, artist, start_frame=1):
    '''
    '''
    if not os.path.isdir(imageDir):
        return False

    images = os.listdir(imageDir)
    i = start_frame
    for img in images:
        #- make background
        foreground_image = Image.open(os.path.join(imageDir, img))
        background_image = Image.new('RGB', (foreground_image.size[0], int(foreground_image.size[1] * 1.2)), Env.MASK_COLOR)

        #- paste foreground
        background_image.paste(foreground_image, (0, int(foreground_image.size[1] * 0.1)))

        #- draw text
        text_font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE)
        background_draw = ImageDraw.Draw(background_image)

        #- up - left
        _text = 'Cam: {0}'.format(camera)
        camera_font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE * 2)
        text_size   = camera_font.getsize(_text)
        _pos  = (Env.TEXT_BOUND, foreground_image.size[1] * 0.05 - text_size[1] * 0.6)
        draw_text(background_draw, _pos, _text, camera_font)

        #- up - middle
        #_text = '{0} x {1}'.format(foreground_image.size[0], foreground_image.size[1])
        #text_size = text_font.getsize(_text)
        #_pos = ((background_image.size[0] - text_size[0]) / 2, foreground_image.size[1] * 0.05 - text_size[1] * 0.6)
        #draw_text(background_draw, _pos, _text, text_font)

        #- up - right
        _text = 'Focal: {0}'.format(focal)
        text_size = text_font.getsize(_text)
        _pos = (background_image.size[0] - text_size[0] - Env.TEXT_BOUND, foreground_image.size[1] * 0.05 - text_size[1] * 0.6)
        draw_text(background_draw, _pos, _text, text_font)

        #- down - left
        _now = datetime.datetime.now()
        _text = 'Date: {0:0>4}-{1:0>2}-{2:0>2}'.format(_now.year, _now.month, _now.day)
        text_size = text_font.getsize(_text)
        _pos = (Env.TEXT_BOUND, background_image.size[1] - foreground_image.size[1] * 0.05 - text_size[1] * 0.6)
        draw_text(background_draw, _pos, _text, text_font)

        #- down - middle
        _text = 'Atrist: {0}'.format(artist)
        text_size = text_font.getsize(_text)
        _pos = ((background_image.size[0] - text_size[0]) / 2, background_image.size[1] - foreground_image.size[1] * 0.05 - text_size[1] * 0.6)
        draw_text(background_draw, _pos, _text, text_font)

        #- down - right
        _text = 'Frame: {0:0>4}/{1:0>4}'.format(i, len(images) + start_frame - 1)
        framne_font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE * 2)
        text_size   = framne_font.getsize(_text)        
        _pos = (background_image.size[0] - text_size[0] - Env.TEXT_BOUND, background_image.size[1] - foreground_image.size[1] * 0.05 - text_size[1] * 0.6)
        draw_text(background_draw, _pos, _text, framne_font)
        i += 1

        #- save images
        background_image.save(os.path.join(imageDir, img))
        sys.stdout.write('{0}\n'.format(img))



def comp_to_video(image_sequence, output, audio=None, view_output=False):
    '''
    '''
    sequence = image_sequence

    if audio and os.path.isfile(audio):
        sequence = '[ {0} {1} ]'.format(image_sequence, audio)

    commands = [Env.RVIO_BIN, sequence, '-o {0}'.format(output) , '-fps {0}'.format(Env.VIDEO_FPS) , '-codec {0}'.format(Env.VIDEO_CODEC), '-v']
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
