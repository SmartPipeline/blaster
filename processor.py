# coding: utf-8
#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Thu Apr 11 15:11:43 2019
#========================================
import sys, os, re, imp, json, math, glob, datetime, subprocess
import numpy, progressbar, fire
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



def draw_text(image, pos, text, size):
    '''
    '''
    draw = ImageDraw.Draw(image)
    _font = ImageFont.truetype(Env.TEXT_FONT, size)
    _size = _font.getsize(text)

    X = min(max(Env.TEXT_BOUND, pos[0] - _size[0]/2), image.width - Env.TEXT_BOUND - _size[0])
    Y = min(pos[1] + Env.MASK_HEIGHT/2 - _size[1]/2,  image.height - Env.MASK_HEIGHT/2 - _size[1]/2)
    draw.text((X, Y), text, font=_font, fill=Env.TEXT_COLOR)

    return True



def comp_images(image_pattern, camera, focal, artist):
    '''
    '''
    images = glob.glob(image_pattern)

    for i, img in enumerate(progressbar.progressbar(images)):
        #- make background
        back_image = create_back_image(img)

        text_pos_x = numpy.linspace(0, back_image.width,  3)
        text_pos_y = numpy.linspace(0, back_image.height, 2)

        #- up - left
        _text = u'Cam: {0}'.format(camera)
        draw_text(back_image, (text_pos_x[0], text_pos_y[0]), _text, Env.TEXT_SIZE_UL)

        #- up - middle
        # _text = u'{0} x {1}'.format(back_image.width, back_image.height - Env.MASK_HEIGHT*2)
        # draw_text(back_image, (text_pos_x[1], text_pos_y[0]), _text, Env.TEXT_SIZE_UM)

        #- up - right
        _text = u'Focal: {0}'.format(focal)
        draw_text(back_image, (text_pos_x[2], text_pos_y[0]), _text, Env.TEXT_SIZE_UR)

        #- down - left
        _now = datetime.datetime.now()
        _text = u'Date: {0:0>4}-{1:0>2}-{2:0>2}'.format(_now.year, _now.month, _now.day)
        draw_text(back_image, (text_pos_x[0], text_pos_y[1]), _text, Env.TEXT_SIZE_DL)

        #- down - middle
        _text = u'Artist: {0}'.format(artist)
        draw_text(back_image, (text_pos_x[1], text_pos_y[1]), _text, Env.TEXT_SIZE_DM)

        #- down - right
        curt_frame = re.search('(?<=\.)\d+(?=\.)', os.path.basename(img))
        last_frame = re.search('(?<=\.)\d+(?=\.)', os.path.basename(images[-1]))
        if curt_frame:
            curt_frame = curt_frame.group()
        else:
            curt_frame = '{0:0>4}'.format(i+1)

        if last_frame:
            last_frame = last_frame.group()
        else:
            last_frame = '{0:0>4}'.format(len(images)+1)

        _text = u'Frame: {0}/{1}'.format(curt_frame, last_frame)
        draw_text(back_image, (text_pos_x[2], text_pos_y[1]), _text, Env.TEXT_SIZE_DR)

        #- save images
        back_image.save(img)
        back_image.close()




def rv_comp_video(image_pattern, output, audio=None):
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




def ffmpeg_comp_video(image_pattern, output, audio=None):
    '''
    '''
    start_frame = re.search('(?<=\.)\d+(?=\.)', os.path.basename(glob.glob(image_pattern)[0])).group()
    sequence    = re.sub('\.\?+\.', '.%{0}d.'.format(len(start_frame)), image_pattern)

    if audio and os.path.isfile(audio):
        input_audio = '-i {0}'.format(audio)
    else:
        input_audio = ''

    commands = [Env.FFMPEG_BIN,
                '-start_number {0}'.format(start_frame),
                '-i {0}'.format(sequence),
                '{0}'.format(input_audio),
                '-vcodec {0}'.format(Env.VIDEO_CODEC),
                '-vf format=rgb24',
                '-pix_fmt yuv420p',
                '-profile:v main',
                '-crf 16',
                '-r {0}'.format(Env.VIDEO_FPS),
                '-x264opts b_pyramid=0',
                '-y',
                output]

    subprocess.check_call(' '.join(commands).encode('gbk'))




def comp_blast_video(info_file, use_ffmpeg=True):
    '''
    '''
    with open(Env.MOTD_FILE, 'r') as f:
        sys.stdout.write(f.read().decode('utf-8'))
    sys.stdout.write('\n')

    info_data = dict()
    with open(info_file, 'r') as f:
        info_data = json.load(f)

    comp_images(info_data['ImagePattern'], info_data['Camera'], info_data['Focal'], info_data['Artist'])
    if use_ffmpeg:
        ffmpeg_comp_video(info_data['ImagePattern'],  info_data['Output'], info_data['Audio'])
    else:
        rv_comp_video(info_data['ImagePattern'],  info_data['Output'], info_data['Audio'])



if __name__ == '__main__':
    fire.Fire({
        'comp_images': comp_images,
        'rv_comp_video': rv_comp_video,
        'ffmpeg_comp_video':ffmpeg_comp_video,
        'comp_blast_video': comp_blast_video
    })
