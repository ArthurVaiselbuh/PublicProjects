import subprocess
import os

#lazy, non required params (specific for me)
DEFAULT_VIDEO_FOLDER = r"D:\Fraps\Movies"
DEFAULT_OUTPUT_PATH = r"D:\Fraps\Movies\Encoded"

DEFAULT_FFMPEG_PATH = r"D:\Programs\ffmpeg\bin\ffmpeg.exe"

def encode(fpath, outpath, qscale=5):
    """
    Encode video in fpath to a new video outpath with quality qscale(0-31).
    """
    assert 0<= qscale <32
    COMMAND = '{ffmpeg} -i "{video}" -vcodec msmpeg4v2 -qscale {qscale} "{output}"'
    command = COMMAND.format(ffmpeg=DEFAULT_FFMPEG_PATH, video=fpath, qscale=qscale, output=outpath)
    try:
        result = subprocess.call(command)
    except Exception as e:
        print("Something went wrong. Error is:")
        print(e)
    return result

def build_menu():
    _, _, fnames = next(os.walk(DEFAULT_VIDEO_FOLDER))
    fnames = filter(lambda x:x.endswith(".avi"), fnames)
    menu = "Which file to convert?\n"
    for i, name in enumerate(fnames):
        menu += "{}. {}\n".format(i, name)
    return fnames, menu

def get_outpath():
    while True:
        print("File will be created in {}.".format(DEFAULT_OUTPUT_PATH))
        name = raw_input("File name?\n")
        name = name if name.endswith(".avi") else name + ".avi"
        path = os.path.join(DEFAULT_OUTPUT_PATH, name)
        if os.path.exists(path):
            result = raw_input("File exists. Overwrite?(y/n)\n")
            if result.lower() == 'y':
                return path
            continue
        return path

def main():
    fnames, menu_string = build_menu()
    choice = int(raw_input(menu_string))
    fpath = os.path.join(DEFAULT_VIDEO_FOLDER, fnames[choice])
    outpath = get_outpath()
    result = encode(fpath, outpath)
    if result != 0:
        print("An error occured:{}. returning.".format(result))
    else:
        answer = raw_input("Remove original file?(y/n)\n")
        if answer.lower() == 'y':
            os.remove(fpath)




if __name__ == "__main__":
    main()