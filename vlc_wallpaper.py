#!/usr/bin/env python3w
import argparse
import os
import random
import subprocess
import shutil
from urllib.parse import urlparse

from yt_dlp import YoutubeDL
import fleep

DEFAULT_VIDEO_DIR = "~/Videos/VideoWallpapers"

# TODO Check these paths
# "C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
# "C:/Users/Bryce/scoop/shims/vlc.exe"

# TODO
# - switch to another video after a set amount of time
# - figure out how to more seamlessly determine the output file extension



def launchWithoutConsole(*args):
    """Launches 'command' windowless and waits until finished"""
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.Popen(args, startupinfo=startupinfo).wait()


def play_specific_video(video_path):
    video_path = os.path.expanduser(video_path)
    if video_path is not None and os.path.isfile(video_path):
        launchWithoutConsole('vlc', '--video-wallpaper', '--loop', video_path)
        return


def random_video_wallpaper(video_dir):
    # Define the directory where the videos are stored
    video_dir = os.path.expanduser(video_dir)

    # Get the list of all files in the directory
    file_list = os.listdir(video_dir)

    # Filter the list to include only .mp4 files
    file_list = [
        file for file in file_list
        if any(map(file.endswith, ['.mp4', '.webm']))
    ]

    # Select a random file from the list
    random_file = random.choice(file_list)
    print(random_file)

    # Full path to the random video file
    video_file = os.path.join(video_dir, random_file)

    launchWithoutConsole('vlc', '--video-wallpaper', '--loop', video_file)


def main():
    my_parser = argparse.ArgumentParser(description='Play a video')
    my_parser.add_argument(
       'video',
       metavar='video',
       type=str,
       nargs='?',
       help='the path to the video',
       default=None
    )
    my_parser.add_argument(
        '--format',
    )
    # --no-audio
    # --audio

    args = my_parser.parse_args()

    # XXX add option to specify video directory for download
    if args.video is None:
        video_dir = DEFAULT_VIDEO_DIR
    else:
        video_dir = args.video

    video_a_url = is_url(args.video)

    if args.format:
        ytdlp_format = ["-f", args.format]
    else:
        ytdlp_format = []
    if is_url(args.video):
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(args.video, download=False)

        yt_command = ["yt-dlp", *ytdlp_format, "-o", "-", args.video]
        _filename = subprocess.getoutput(f'yt-dlp --print filename {args.video}')
        def removesuffix(s):
            return s[:s.rfind(".")]
        # XXX the format from print filename is not the same as the format for piping
        # How do I determine the filetype from the piped output?
        filename = removesuffix(_filename)

        vlc_command = [
            "vlc.exe",
            "-",
            # too many brackets
            # "--sout=#duplicate{dst=display,{dst=standard{access=file,dst='out.mp4'}}}"
            "--sout=#duplicate{dst=display,{dst=standard{access=file,dst='" + filename + "'}}}"
            # "--sout=#duplicate{dst=display}"
        ]
        print(yt_command)
        print(vlc_command)
        yt_proc = subprocess.Popen(yt_command, stdout=subprocess.PIPE, shell=True)
        vlc_proc = None
        try:
            vlc_proc = subprocess.Popen(vlc_command, stdin=yt_proc.stdout, shell=True)
        finally:
            if vlc_proc:
                vlc_proc.communicate()
            if os.path.exists(filename):
                print(f"file written to {filename}")

            # if not os.path.exists(filename):
            #     with open(filename, "rb") as file:
            #         info = fleep.get(file.read(128))
            #         extension = info.extension
            #         final_filename = os.path.join(DEFAULT_VIDEO_DIR, filename + "." + extension)
            #         shutil.move(filename, final_filename)
            # else:
            #     print("No extension found")
            #     final_filename = filename
            # print(f"file written to {final_filename}")
    elif args.video:
        play_specific_video(args.video)
    else:
        print("No video specified, playing a random video")
        random_video_wallpaper(video_dir)
# yt-dlp.exe -f 22 -o - "https://www.youtube.com/watch?v=CRnmDu6vCIQ"  |


def is_url(s):
    # Not comprehensive
    if urlparse(s).netloc:
        return True
    if s.startswith("www."):
        return True
    # At this point it could start checking if the file exists
    if s.endswith(".com"):
        return True
    return False


# Calling the function
if __name__ == "__main__":
    main()
