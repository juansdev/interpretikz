import glob, uuid
import moviepy.editor as mpy

id = str(uuid.uuid4())
input_png_list = glob.glob("./source/*.jpg")
input_png_list.sort()
clips = [mpy.ImageClip(i).set_duration(.1)
            for i in input_png_list]
concat_clip = mpy.concatenate_videoclips(clips, method="compose")
concat_clip.write_gif("./test.gif", fps=2,logger=True)