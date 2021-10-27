# blackpearl-bbcode-bot
<p align="center">
Simple Telegram Bot for generating BlackPearl BBCode Templates Written in Pyrogram
</p>

## Features
-🎉 IMDB Info fetching from files

-🗃️ Both Movies and TV Supported

-⚙️ Mediainfo,Tags,Links,Size,Languages 

-🛠️ TMDB Posters For Movies

-📦 Everything Works on Mounted Gdrive, No local files needed

-🤘 Fetches Every files in folder

## To-do
- Changing Entire Script to Make Advanced Stuffs,Takes time...

## Installation

### Requirements

Install the following dependencies in the listed order. Ensure shaka-packager is added to the environment path.

1. [python], 3.6.0 or newer
2. [rclone], rclone.exe and rclone.config in same path or needed to be added in environment path
3. [mediainfo], mediainfo.exe same path or environment

### Steps
- Edit BOTCONFIG.py Add Your Credentials And Paths
- Install Requirements : `python -m pip install -r requirements.txt`
- Add Needed Files to Path : rclone.exe - mediainfo.exe - rclone.config
- Mount Your Drive using rclone : `rclone mount remote:foldername --vfs-cache-mode full s:' 
  Note : Make Sure U mounted the remote:folder mentioned in config file, You can change `s:` to your mounted drive name (not rclone name)
- Run Bot `python BPBBCODE.py`
- Open Telegram Send `/movie Foldername` or `/tv foldername`

