# coding: utf-8
#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Thu Apr 11 15:11:43 2019
#========================================
import sys, os, re, json, math, glob, datetime, subprocess
import yaml, numpy, progressbar, fire
from PIL import Image, ImageDraw, ImageFont

if os.path.basename(sys.executable) == 'python.exe':
    this_dir = os.path.dirname(__file__)

else:
    this_dir = os.path.dirname(sys.executable)

with open(os.path.join(this_dir, 'config.yml'), 'r') as f:
    config = yaml.load(f, Loader=yaml.Loader)   
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
def create_back_image(image):
    '''
    '''
    fore_image = Image.open(image)

    back_width, back_height = fore_image.width, fore_image.height + config['mask_height']*2
    back_width  = int(math.ceil(back_width  / 2.0) * 2)
    back_height = int(math.ceil(back_height / 2.0) * 2)

    back_image = Image.new('RGB', (back_width, back_height), tuple(config['mask_color']))
    back_image.paste(fore_image.resize((back_image.width, fore_image.height)), (0, config['mask_height']))
    fore_image.close()

    return back_image



def draw_text(image, pos, text, font, size, color):
    '''
    '''
    draw = ImageDraw.Draw(image)
    _font = ImageFont.truetype(font.format(this_dir), size)
    _size = _font.getsize(text)

    X = min(max(config['text_bound'], pos[0] - _size[0]/2), image.width  - config['text_bound']    - _size[0])
    Y = min(pos[1] + config['mask_height']/2 - _size[1]/2,  image.height - config['mask_height']/2 - _size[1]/2)
    draw.text((X, Y), text, font=_font, fill=tuple(color))

    return True



def comp_images(image_pattern, camera, focal, artist):
    '''
    '''
    images = glob.glob(image_pattern)

    date = datetime.datetime.now()
    info_data = {
        'camera': camera,
        'focal' : focal,
        'date'  : '{0:0>4}-{1:0>2}-{2:0>2}'.format(date.year, date.month, date.day),
        'artist': artist
    }

    for i, img in enumerate(progressbar.progressbar(images)):
        #- make background
        back_image = create_back_image(img)

        curt_frame = re.search('(?<=\.)\d+(?=\.)', os.path.basename(img))
        last_frame = re.search('(?<=\.)\d+(?=\.)', os.path.basename(images[-1]))
        if curt_frame:
            info_data['current_frame'] = curt_frame.group()
        else:
            info_data['current_frame'] = '{0:0>4}'.format(i+1)

        if last_frame:
            info_data['total_frame'] = last_frame.group()
        else:
            info_data['total_frame'] = '{0:0>4}'.format(len(images)+1)

        pos_y = numpy.linspace(0, back_image.height, 2)
        for column, cfg in enumerate(config['text'][0]):
            pos_x = numpy.linspace(0, back_image.width, len(config['text'][0]))
            draw_text(back_image, (pos_x[column], pos_y[0]), cfg['text'].format(**info_data), cfg['font'], cfg['size'], cfg['color'])

        for column, cfg in enumerate(config['text'][1]):
            pos_x = numpy.linspace(0, back_image.width, len(config['text'][1]))
            draw_text(back_image, (pos_x[column], pos_y[1]), cfg['text'].format(**info_data), cfg['font'], cfg['size'], cfg['color'])            

        #- save images
        back_image.save(img)
        back_image.close()




def rv_comp_video(image_pattern, output, audio=None):
    '''
    '''
    sequence = image_pattern.replace('?', '@')
    if audio and os.path.isfile(audio):
        sequence = u'[ {0} {1} ]'.format(sequence, audio)

    commands = [config['rvio_bin'],
                sequence,
                u'-outfps {0}'.format(config['fps']),
                u'-codec {0}'.format(config['codec']),
                u'-outparams vcc:bf=0',
                u'-quality 1.0',
                u'-o {0}'.format(output),
                u'-rthreads {0}'.format(config['rv_r_thread']),
                u'-wthreads {0}'.format(config['rv_w_thread']),
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

    commands = [config['ffmpeg_bin'].format(this_dir),
                '-start_number {0}'.format(start_frame),
                '-framerate {0}'.format(config['fps']),
                '-i {0}'.format(sequence),
                '{0}'.format(input_audio),
                '-vcodec {0}'.format(config['codec']),
                '-vf format=rgb24',
                '-pix_fmt yuv420p',
                '-profile:v main',
                '-crf 16',
                '-r {0}'.format(config['fps']),
                '-x264opts b_pyramid=0',
                '-y',
                output]

    subprocess.check_call(' '.join(commands).encode('gbk'))




def comp_blast_video(info_file, use_ffmpeg=True):
    '''
    '''
    with open(config['motd'].format(this_dir), 'r') as f:
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
