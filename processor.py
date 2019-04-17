# coding: utf-8
#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Thu Apr 11 15:11:43 2019
#========================================
import sys, os, datetime, imp
import subprocess
import progressbar
from PIL import Image, ImageDraw, ImageFont
import fire
try:
    Env = imp.load_source('Env', os.path.join(os.path.dirname(__file__), 'blasterEnv.py'))
except:
    Env = imp.load_source('Env', os.path.join(os.path.dirname(sys.executable), 'blasterEnv.py'))
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
def get_mask_size(image):
    '''
    '''
    base_image = Image.open(image)
    size = base_image.width, base_image.height * Env.MASK_SCALE
    base_image.close()

    return size



def create_back_image(image):
    '''
    '''
    fore_image = Image.open(image)
    mask_size  = get_mask_size(image)

    back_image = Image.new('RGB', (fore_image.width, int(fore_image.height + mask_size[1]*2)), Env.MASK_COLOR)
    back_image.paste(fore_image, (0, int(mask_size[1])))
    fore_image.close()

    return back_image



def draw_text(image, pos, text, _font):
    '''
    '''
    draw = ImageDraw.Draw(image)
    draw.text(pos, text, font=_font, fill=Env.TEXT_COLOR)
    return True



def add_text(imageDir, camera, focal, artist, start_frame=1):
    '''
    '''
    if not os.path.isdir(imageDir):
        return False

    images = os.listdir(imageDir)
    frame  = start_frame
    for img in progressbar.progressbar(images):
        #- make background
        mask_size = get_mask_size(os.path.join(imageDir, img))
        back_image = create_back_image(os.path.join(imageDir, img))

        #- up - left
        _text = 'Cam: {0}'.format(camera)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_UL)
        _size = _font.getsize(_text)
        _pos  = (Env.TEXT_BOUND, mask_size[1]*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- up - middle
        # _text = '{0} x {1}'.format(fore_image.width, fore_image.height)
        # _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_UM)
        # _size = _font.getsize(_text)
        # _pos = ((back_image.width - _size[0]) / 2, mask_size[1]*0.5 - _size[1]*0.55)
        # draw_text(back_image, _pos, _text, _font)

        #- up - right
        _text = 'Focal: {0}'.format(focal)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_UR)
        _size = _font.getsize(_text)
        _pos = (back_image.width - _size[0] - Env.TEXT_BOUND, mask_size[1]*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- down - left
        _now = datetime.datetime.now()
        _text = 'Date: {0:0>4}-{1:0>2}-{2:0>2}'.format(_now.year, _now.month, _now.day)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_DL)
        _size = _font.getsize(_text)
        _pos = (Env.TEXT_BOUND, back_image.height - mask_size[1]*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- down - middle
        _text = 'Artist: {0}'.format(artist)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_DM)
        _size = _font.getsize(_text)
        _pos = ((back_image.width - _size[0]) / 2, back_image.height - mask_size[1]*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)

        #- down - right
        _text = 'Frame: {0:0>4}/{1:0>4}'.format(frame, len(images) + start_frame - 1)
        _font = ImageFont.truetype(Env.TEXT_FONT, Env.TEXT_SIZE_DR)
        _size = _font.getsize(_text)        
        _pos = (back_image.width - _size[0] - Env.TEXT_BOUND, back_image.height - mask_size[1]*0.5 - _size[1]*0.55)
        draw_text(back_image, _pos, _text, _font)
        frame += 1

        #- save images
        back_image.save(os.path.join(imageDir, img))
        back_image.close()




def comp_to_video(image_sequence, output, audio=None, view_output=False):
    '''
    '''
    sequence = image_sequence

    if audio and os.path.isfile(audio):
        sequence = '[ {0} {1} ]'.format(image_sequence, audio)

    commands = [Env.RVIO_BIN,
                sequence,
                '-o {0}'.format(output),
                '-outfps {0}'.format(Env.VIDEO_FPS),
                '-codec {0}'.format(Env.VIDEO_CODEC),
                '-quality 1.0',
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
