#!/usr/bin/env python3w
import argparse
import os
import random
import subprocess
import time
import shutil
from urllib.parse import urlparse

from yt_dlp import YoutubeDL
import fleep
import pygetwindow as gw
import win32gui
import win32con

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
    popen_ret = subprocess.Popen(args, startupinfo=startupinfo)
    import time
    time.sleep(0.75)
    window_seq = gw.getWindowsWithTitle('VLC media player')
    print(window_seq)
    window = window_seq[0]
    win32gui.SetWindowPos(window._hWnd, win32con.HWND_BOTTOM, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
    hide_window(window._hWnd)
    return popen_ret


def hide_window(hwnd):
   # Get the current window style
   style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
   # Add the WS_EX_TOOLWINDOW style
   style |= win32con.WS_EX_TOOLWINDOW
   # Set the new window style
   win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)


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
       'video_or_url',
       metavar='video_or_url',
       type=str,
       nargs='?',
       help='the path to the video',
       default=None
    )
    my_parser.add_argument(
        "--dir", "--directory",
        # TODO implement this
    )
    my_parser.add_argument(
        '--format',
    )

    my_parser.add_argument(
        "--ytargs",
    )
    # --no-audio
    # --audio

    args = my_parser.parse_args()

    # XXX add option to specify video directory for download
    if args.video_or_url is None:
        video_dir = DEFAULT_VIDEO_DIR
    else:
        video_dir = args.video_or_url

    video_a_url = is_url(args.video_or_url)

    import shlex
    ytdlp_format = []
    if args.format:
        ytdlp_format.extend(["-f", args.format])
    if args.ytargs:
        ytdlp_format.extend(shlex.split(args.ytargs))
    if is_url(args.video_or_url):
        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(args.video_or_url, download=False)

        yt_command = ["yt-dlp", *ytdlp_format, "-o", "-", args.video_or_url]
        _filename = subprocess.getoutput(f'yt-dlp --print filename {args.video_or_url}')
        def removesuffix(s):
            return s[:s.rfind(".")]
        # XXX is format from print filename is not the same as the format for piping
        # How do I determine the filetype from the piped output?

        # For some reason, vlc will output an invalid file if the extension is not mp4
        # this may be due to an issue with the format of the piped output versus
        # the format given by --print filename
        filename = removesuffix(_filename).replace(" ", "_").replace(":", "_").replace("/", "_").replace("\\", "_").replace("?", "_").replace("*", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_").replace(",", "_")

        vlc_command = [
            "vlc.exe",
            "-",
            "--video-wallpaper",
            "--loop",
            # too many brackets
            # still audio is not preserved
            "--sout=#duplicate{dst=std{access=file,acode=aac,mux=mp4,dst='" + filename + ".mp4'},dst=display}"
            # "--sout=#duplicate{dst=display,{dst=standard{access=file,dst='out.mp4'}}}"
            # "--sout=#duplicate{dst=display,{dst=standard{access=file,dst='" + filename + "'}}}"
            # "--sout=#duplicate{dst=display}"
        ]
        # How do I check if the clip has ended?
        # Idea: check if the file size has changed
        # Idea: check if the file has been modified
        # Idea: check if the file has been modified in the last 5 seconds
        # Idea: Generate a vlc playlist and play it
        print(yt_command)
        print(vlc_command)
        yt_proc = subprocess.Popen(yt_command, stdout=subprocess.PIPE, shell=True)
        vlc_proc = None
        try:
            vlc_proc = subprocess.Popen(vlc_command, stdin=yt_proc.stdout, shell=True)
        finally:
            # while True:
            #     timejjj.sleep(0.1)
            # TODO move filename to video dir directory
            if vlc_proc:
                vlc_proc.communicate()
            if os.path.exists(filename + ".mp4"):
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
    elif args.video_or_url:
        play_specific_video(args.video_or_url)
    else:
        print("No video specified, playing a random video")
        random_video_wallpaper(video_dir)
# yt-dlp.exe -f 22 -o - "https://www.youtube.com/watch?v=CRnmDu6vCIQ"  |


def is_url(s):
    if not s:
        return False
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
