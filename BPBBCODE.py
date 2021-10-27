import logging
from colorama import Fore,Style
from colorama import init
init()

logging.basicConfig(level=logging.INFO, format=Style.BRIGHT+Fore.GREEN+'%(asctime)s' +Style.RESET_ALL+':' +Style.BRIGHT+Fore.CYAN+'%(funcName)s' +Style.RESET_ALL+':'+Style.BRIGHT+Fore.RED+'%(levelname)s'+Style.RESET_ALL+':'+Style.BRIGHT+Fore.YELLOW+'%(message)s'+Style.RESET_ALL)

import subprocess 

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

from pathlib import Path
import requests,json,base64
from pathlib import Path
import os,json,pprint,threading,re
import asyncio
import time
from pyrogram import Client,filters
from pyrogram.handlers import (
    MessageHandler,
    CallbackQueryHandler
)
from pyrogram.types import (
    Message
)

from BOTCONFIG import AUTH_CHANNEL,TG_BOT_TOKEN,APP_ID,API_HASH,MOVIEPATH,TVPATH,MAINPATH,REMOTE_NAME,OMDB_API,sleeptime,TMDB_API

def _link_match_filt_er(link_kw: str):
    def func(flt, client, message):
        if message and message.text:
            if flt.wok in message.text:
                leech_url = None
                custom_file_name = None
                for one_entity in message.entities:
                    if one_entity.type == "url":
                        leech_url = message.text[
                            one_entity.offset:one_entity.offset + one_entity.length
                        ]
                    elif one_entity.type == "text_link":
                        leech_url = one_entity.url
                    if leech_url and flt.wok in leech_url:
                        break
                if "|" in message.text:
                    _, custom_file_name = message.text.split("|")
                if leech_url:
                    message.leech_url = leech_url.strip()
                if custom_file_name:
                    message.custom_file_name = custom_file_name.strip()
                else:
                    message.custom_file_name = None
                return True
        return False
    # wok kwarg is accessed with flt.wok above
    return filters.create(func, wok=link_kw)

##---FUNCTION FOR LOOP---##

def find_files(root, extensions):
    for ext in extensions:
        yield from Path(root).glob(f'**/*.{ext}')

##---FUNCTION FOR MEDIAINFO AS TEXT---##
LanguageList = [
                ["en", "en", "eng", "English"],
                ["es", "es", "spa", "Castilian"],
                ["es-la", "es-la", "spa", "Spanish"],
                ["cat", "cat", "cat", "Catalan"],
                ["eu", "eu", "baq", "Basque"],
                ["fr", "fr", "fre", "French"],
                ["fr-bg", "fr-bg", "fre", "French (Belgium)"],
                ["fr-lu", "fr-lu", "fre", "French (Luxembourg)"],
                ["fr-ca", "fr-ca", "fre", "French (Canada)"],
                ["de", "de", "ger", "German"],
                ["it", "it", "ita", "Italian"],
                ["pt", "pt", "por", "Portuguese"],
                ["pt-br", "pt-br", "por", "Brazilian Portuguese"],
                ["pl", "pl", "pol", "Polish"],
                ["tr", "tr", "tur", "Turkish"],
                ["hy", "hy", "arm", "Armenian"],
                ["sv", "sv", "swe", "Swedish"],
                ["da", "da", "dan", "Danish"],
                ["fi", "fi", "fin", "Finnish"],
                ["nl", "nl", "dut", "Dutch"],
                ["nl-be", "nl-be", "dut", "Flemish"],
                ["no", "no", "nor", "Norwegian"],
                ["lv", "lv", "lav", "Latvian"],
                ["is", "is", "ice", "Icelandic"],
                ["ru", "ru", "rus", "Russian"],
                ["he", "he", "heb", "Hebrew"],
                ["ar", "ar", "ara", "Arabic"],
                ["fa", "fa", "per", "Persian"],
                ["ro", "ro", "rum", "Romanian"],
                ["mk", "mk", "mac", "Macedonian"],
                ["hi", "hi", "hin", "Hindi"],
                ["bn", "bn", "ben", "Bengali"],
                ["ur", "ur", "urd", "Urdu"],
                ["pa", "pa", "pan", "Punjabi"],
                ["ta", "ta", "tam", "Tamil"],
                ["te", "te", "tel", "Telugu"],
                ["mr", "mr", "mar", "Marathi"],
                ["kn", "kn", "kan", "Kannada (India)"],
                ["gu", "gu", "guj", "Gujarati"],
                ["ml", "ml", "mal", "Malayalam"],
                ["si", "si", "sin", "Sinhala"],
                ["as", "as", "asm", "Assamese"],
                ["mni", "mni", "mni", "Manipuri"],
                ["tl", "tl", "tgl", "Tagalog"],
                ["id", "id", "ind", "Indonesian"],
                ["ms", "ms", "may", "Malay"],
                ["fil", "fil", "fil", "Filipino"],
                ["vi", "vi", "vie", "Vietnamese"],
                ["th", "th", "tha", "Thai"],
                ["km", "km", "khm", "Khmer"],
                ["ko", "ko", "kor", "Korean"],
                ["zh", "zh", "chi", "Mandarin"],
                ["yue", "yue", "chi", "Cantonese"],
                ["zh-hans", "zh-hans", "chi", "Chinese (Simplified)"],
                ["zh-hant", "zh-hant", "chi", "Chinese (Traditional)"],
                ["zh-hk", "zh-hk", "chi", "Chinese (Simplified)"],
                ["zh-tw", "zh-tw", "chi", "Chinese (Traditional)"],
                ["zh-sg", "zh-sg", "chi", "Chinese (Singapore)"],
                ["ja", "ja", "jpn", "Japanese"],
                ["tlh", "tlh", "tlh", "Klingon"],
                ["zxx", "zxx", "zxx", "No Dialogue"],
                ]
                
def getMediaInfo(FILEPATH,FILENAME):
	logging.info("Getting Media Info Of Path")
	MEDIAINFO = subprocess.check_output(['mediainfo', FILEPATH]).decode().strip('\n')
	MEDIAINFO = MEDIAINFO.replace("\n","")
	MEDIAINFO = MEDIAINFO.replace(FILEPATH,FILENAME)
	logging.info("Fetched MediaInfo")
	return MEDIAINFO

##-----FUNCTION FOR FETCHING OMDB----##
def getTags(IMDB,Language,FILENAME):
	TAGS = ''
	try:
		GENRE = ''
		GENRE = IMDB['Genre']
		if GENRE!='N/A':
			TAGS+=f"{GENRE},"
	except KeyError:
		print("No Genre Found From OMDB")
	if not Language=='English':
		TAGS+=f"{Language},"
	QUALITY_TAGS = ['1080p','2160p','720p','480p','4k']
	DDPTAGS =['DDP5.1','DD+5.1','DDP 5.1','DD+ 5.1','ddp 5.1']
	DVTAGS = ['DV','DoVi','Dolby Vision']
	AMZNTAGS = ['AMZN']
	NFTAG =['NF']
	DSNPTAG = ['DSNP','HS','HOTSTAR','DSNY+']
	APPLETAG= ['APPLETV','ATVP','APTV','AppleTv']
	BLURAYTAG = ['Blu-Ray','Bluray','BD','BLURAY','bluray','blu ray','Blu Ray']
	HDRTAG = ['HDR','hdr']
	DDP_TAGS =['DDP2.0','DD+2.0','DDP 2.0','DD+ 2.0','DDP.2.0']
	AACTAGS =['AAC5.1','AAC 5.1','AAC.5.1']
	AAC_TAGS =['AAC2.0','AAC 2.0','AAC.2.0']
	HEVCTAG = ['HEVC','H.265','H265','x265']
	H264TAG = ['H.264','H264','AVC','x264']
	INDIANTAGS = ['Hindi','Tamil','Gujarati','Malayalam','Telugu','Kannada','Punjabi']
	for i in INDIANTAGS:
		if i in Language:
			TAGS+="indian,"		
	for i in APPLETAG:
		if i in FILENAME:
			TAGS+="atvp,web-dl,"
	for i in BLURAYTAG:
		if i in FILENAME:
			TAGS+="blu-ray,"
	for i in H264TAG:
		if i in FILENAME:
			TAGS+="h264,"
	for i in HEVCTAG:
		if i in FILENAME:
			TAGS+="hevc,h265,"
	for i in HDRTAG:
		if i in FILENAME:
			TAGS+="hdr,"
	for i in DSNPTAG:
		if i in FILENAME:
			TAGS+="dsnp,web-dl,"
	for i in NFTAG:
		if i in FILENAME:
			TAGS+=f"nf web-dl,"
	for i in AMZNTAGS:
		if i in FILENAME:
			TAGS+=f"amzn web-dl,"
	for i in DVTAGS:
		if i in FILENAME:
			TAGS+=f"dolby vision,"
	for i in QUALITY_TAGS:
		if i in FILENAME:
			TAGS+=f"{i},"
	for i in DDPTAGS:
		if i in FILENAME:
			TAGS+="ddp 5.1,"
	for i in DDP_TAGS:
		if i in FILENAME:
			TAGS+="ddp 2.0,"
	for i in AACTAGS:
		if i in FILENAME:
			TAGS+="aac 5.1,"
	for i in AAC_TAGS:
		if i in FILENAME:
			TAGS+="aac 2.0,"
	return TAGS

def getOMDB(FILENAME):
	IMDB_NAME =''
	IMDB_YEAR =''
	TITLE =''
	
	if IMDB_NAME =='':
		try:
			logging.info("Looking For Year From File Name")
			IMDB_YEAR = '&y=' + re.findall(r'(19\d{2}|20\d{2})', FILENAME)[-1]
			logging.info(f"Found YEAR : {IMDB_YEAR}")
		except:
			IMDB_YEAR=''
			logging.info("Year Not Found From File")
	logging.info("Getting OMDB Name From File Name")
	TITLE = re.sub('[^a-zA-Z0-9]', '+', os.path.basename(FILENAME)).split('+' + IMDB_YEAR.replace('&y=', '') + '+')[0].split('+S0')[0].split('+S1')[0].split('+S2')[0].split('+1080p')[0].split('+2160p')[0].split('+UHD')[0].split('+REPACK')[0].split('+HYBRID')[0].split('+EXTENDED')[0]
	logging.info(f"Found Title : {TITLE}")
	
	return TITLE,IMDB_YEAR
def getLANG(FILEPATH):
	mediainfo_output = subprocess.Popen(["Mediainfo", "--Output=JSON", "-f", FILEPATH],stdout=subprocess.PIPE)
	mediainfo = json.load(mediainfo_output.stdout)
	for m in mediainfo["media"]["track"]:
		if m["@type"] == "Audio":
			if m['StreamKindID']=="0":
				try:
					LanG = m["Language"]
				except KeyError:
					LanG = 'en'
				for i in LanguageList:
					Language = "English"
					if LanG in i:
						Language = i[3]
						logging.info(f"Found Language : {Language}")
						return Language
		
	
def getLINK(FILEPATH,TYPE):
	logging.info("Getting Link And Size From Drive")
	LINKPATH = FILEPATH.replace(MAINPATH,'')
	LINK =''
	if TYPE=='MOVIE':
		LINK = LINKPATH
	if TYPE=='TVSHOW':
		LINK = LINKPATH.split('/')[0]+"/"+LINKPATH.split("/")[1]
		logging.info("Requesting Season Folder Link And Size")
		###---REQUESTS--SIZE--FROM--DRIVE--###
	SIZECMD = f"rclone size \"{REMOTE_NAME}{LINK}\""
	SIZE =""
	SIZEFETCH = subprocess.Popen(SIZECMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out,err =  SIZEFETCH.communicate()
	SIZE = out.decode().strip()
	q = err.decode().strip()
	SIZE = SIZE.split("Total size: ")[1]
	sizes = None
	if "GB" or "GiB" in SIZE:
		sizes ="GB"
	if "MB" in SIZE:
		sizes = "MB"
	if "KB" in SIZE:
		sizes = "KB"
	if not sizes:
		sizes="GB"
	SIZE = SIZE.split(" ")[0]
	SIZE = SIZE[:-1]+sizes
	###---REQUESTS--LINK--FROM--DRIVE---##
	LINKCMD = f"rclone link \"{REMOTE_NAME}{LINK}\""
	LINK = subprocess.Popen(LINKCMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out,err =  LINK.communicate()
	LINK = out.decode().strip()
	q = err.decode().strip()
	LINK = str(LINK)
	logging.info(f"File Size : {SIZE}")
	GDLINK = str(LINK)
	logging.info(f"Fetched Link : {GDLINK}")
	LINK = f"[HIDEREACTSCORE=20][HIDEREACT=1,2,3,4,5,6,7,8][DOWNCLOUD]{LINK}[/DOWNCLOUD][/HIDEREACT][/HIDEREACTSCORE]"	
	return LINK,GDLINK,SIZE						

def getBBCODE(IMDB,MEDIAINFO,LINK):
	logging.info("Merging Everything to BBCODE")
	BBCODE=''
	IMDBPoster =''
	Backdrop = None
	try:
	    TMDB = requests.get(f"https://api.themoviedb.org/3/find/{IMDB['imdbID']}?api_key={TMDB_API}&external_source=imdb_id").json()
	    if len(TMDB['movie_results']) != 0:
	        TMDB = TMDB['movie_results'][0]
	        TMDB['type'] = 'movie'
	    elif len(TMDB['tv_results']) != 0:
	        TMDB = TMDB['tv_results'][0]
	        TMDB['type'] = 'tv'
	    else:
	        TMDB = None
	    if TMDB is not None:
	        logging.info(f"TMDB Link: 'https://www.themoviedb.org/{TMDB['type']}/{TMDB['id']}'")
	        IMDBPoster = f"https://image.tmdb.org/t/p/original{TMDB['poster_path']}"
	        Backdrop = f"https://image.tmdb.org/t/p/original{TMDB['backdrop_path']}"
	        BBCODE = f"[CENTER][URL='{IMDBPoster}'][IMG WIDTH='350px']{IMDBPoster}[/IMG][/URL][/CENTER]\n"
	except Exception as e:
                #logging.error(f"Issue In TMDB : {e}")
		#logging.info("Poster Not Found In TMDB")
		if ('Poster' in IMDB and IMDB['Poster'] != 'N/A'):
			IMDBPoster = re.sub('_V1_SX\d+.jpg', '_V1_SX1000.png', IMDB['Poster'])
			logging.info("Attaching Poster From OMDB")
			BBCODE = f"[CENTER][URL='{IMDBPoster}'][IMG WIDTH='350px']{IMDBPoster}[/IMG][/URL][/CENTER]\n"
	BBCODE += f"[CENTER][URL='https://blackpearl.biz/search/1/?q={IMDB['imdbID']}&o=date'][FORUMCOLOR][B][SIZE=6]{IMDB['Title']} ({IMDB['Year'][0:4]})[/SIZE][/B][/FORUMCOLOR][/URL][/CENTER]\n"
	BBCODE += f"[CENTER][URL='https://imdb.com/title/{IMDB['imdbID']}'][IMG WIDTH='46px']https://ia.media-imdb.com/images/M/MV5BMTk3ODA4Mjc0NF5BMl5BcG5nXkFtZTgwNDc1MzQ2OTE@.png[/IMG][/URL][/CENTER]"
	BBCODE += f"[HR][/HR][INDENT][SIZE=6][FORUMCOLOR][B]Plot Summary :[/B][/FORUMCOLOR][/SIZE]\n\n[JUSTIFY]{IMDB['Plot']}[/JUSTIFY][/INDENT]" if ('Plot' in IMDB and IMDB['Plot'] != 'N/A') else ''
	if ('Type' in IMDB and IMDB['Type'] == 'movie'):
		IMDB['Type'] = 'Movie'
	elif ('Type' in IMDB and IMDB['Type'] == 'series'):
	 	IMDB['Type'] = 'TV Show'
	else:
	 	IMDB['Type'] = 'IMDb'
	 #
	BBCODE += f"[HR][/HR][INDENT][SIZE=6][FORUMCOLOR][B]{IMDB['Type']} Info :[/B][/FORUMCOLOR][/SIZE][/INDENT]\n[LIST]"
	BBCODE += f"[*][FORUMCOLOR][B]IMDb :[/B][/FORUMCOLOR] {IMDB['imdbRating']} ({IMDB['imdbVotes']})\n" if ('imdbRating' in IMDB and IMDB['imdbRating'] != 'N/A' and 'imdbVotes' in IMDB and IMDB['imdbVotes'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Rated :[/B][/FORUMCOLOR] {IMDB['Rated']}\n" if ('Rated' in IMDB and IMDB['Rated'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Genres :[/B][/FORUMCOLOR] {IMDB['Genre']}\n" if ('Genre' in IMDB and IMDB['Genre'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Awards :[/B][/FORUMCOLOR] {IMDB['Awards']}\n" if ('Awards' in IMDB and IMDB['Awards'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Runtime :[/B][/FORUMCOLOR] {IMDB['Runtime']}\n" if ('Runtime' in IMDB and IMDB['Runtime'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Starring :[/B][/FORUMCOLOR] {IMDB['Actors']}\n" if ('Actors' in IMDB and IMDB['Actors'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Countries :[/B][/FORUMCOLOR] {IMDB['Country']}\n" if ('Country' in IMDB and IMDB['Country'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Languages :[/B][/FORUMCOLOR] {IMDB['Language']}\n" if ('Language' in IMDB and IMDB['Language'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Written By :[/B][/FORUMCOLOR] {IMDB['Writer']}\n" if ('Writer' in IMDB and IMDB['Writer'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Directed By :[/B][/FORUMCOLOR] {IMDB['Director']}\n" if ('Director' in IMDB and IMDB['Director'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Release Date :[/B][/FORUMCOLOR] {IMDB['Released']}\n" if ('Released' in IMDB and IMDB['Released'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Production By :[/B][/FORUMCOLOR] {IMDB['Production']}\n" if ('Production' in IMDB and IMDB['Production'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]DVD Release Date:[/B][/FORUMCOLOR] {IMDB['DVD']}\n" if ('DVD' in IMDB and IMDB['DVD'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Official Website :[/B][/FORUMCOLOR] {IMDB['Website']}\n" if ('Website' in IMDB and IMDB['Website'] != 'N/A') else ''
	BBCODE += f"[*][FORUMCOLOR][B]Box Office Collection :[/B][/FORUMCOLOR] {IMDB['BoxOffice']}[/LIST]" if ('BoxOffice' in IMDB and IMDB['BoxOffice'] != 'N/A') else '[/LIST]'
	BBCODE = BBCODE.replace('[HR][/HR][INDENT][SIZE=6][FORUMCOLOR][B]IMDb Info :[/B][/FORUMCOLOR][/SIZE][/INDENT]\n[LIST][/LIST]', '')
	BBCODE += '[HR][/HR][INDENT][SIZE=6][FORUMCOLOR][B]Media Info :[/B][/FORUMCOLOR][/SIZE][/INDENT]'
	logging.info("Attaching Media Info")
	BBCODE += f"[SPOILER='Media Info'][CODE TITLE='Media Info']{MEDIAINFO}[/CODE][/SPOILER]\n"
	logging.info("Attaching Download Link")
	BBCODE += f'[HR][/HR][INDENT][SIZE=6][FORUMCOLOR][B]Download Link :[/B][/FORUMCOLOR][/SIZE][/INDENT]\n[CENTER]{LINK}[/CENTER]'
	return BBCODE,Backdrop
	#										
										

async def BPMV(client, message):
  reply_to_id = message.message_id
  user_id = message.from_user.id
  u_id = message.message_id
  logging.info("STARTING BLACKPEARL BBCODE GENERATOR By D.Luffy")
  logging.info("Selected Mode : MOVIE")
  IMDBID=''
  IMDBURL =''
  IMDB =''
  LINK =''
  SIZE =''
  logging.info("Starting Looping Files For Template")
  
  #FINDFILES THROUGH LOOP
  MOVIESPATH = MOVIEPATH[:-1]
  mvpath = str(message.text)
  
  MVPATH = mvpath.replace("/movie ","")
  if not MVPATH =="":
  	MOVIESPATH = MAINPATH +MVPATH
  	logging.info(f"Checking Files For Manual Path : {MOVIESPATH}")	

  logging.info("Fetching Movie Files")
  for MOVIES in find_files(MOVIESPATH , [ 'mkv','mp4','avi','mov']):
  	TYPE ='MOVIE'
  	time.sleep(1)
  	MOVIE_PATH = str(MOVIES)
  	MOVIE_PATH = MOVIE_PATH.replace("\\","/")
  	logging.info(f"Running Generator For - {MOVIE_PATH}")
  	MOVIE_NAME= MOVIE_PATH.replace(MOVIESPATH+"/",'')
  	msgtxt = f"Started Fetching BBCODE\nTitle : <code>{MOVIE_NAME}</code>"
  	status_message = await message.reply_text(msgtxt)
  	time.sleep(1)
  	MEDIAINFO = getMediaInfo(MOVIE_PATH,MOVIE_NAME)
  	time.sleep(1)
  	TITLE,YEAR = getOMDB(MOVIE_NAME)
  	LINK,GDLINK,SIZE = getLINK(MOVIE_PATH,TYPE)
  	Language = getLANG(MOVIE_PATH)
  	###---DOING--OMDB--REQUEST--###
  	logging.info("Requesting OMDB")
  	IMDB = requests.get(f'http://www.omdbapi.com/?t={TITLE}{YEAR}&apikey={OMDB_API}&r=json').json()
  	if IMDB['Response'] == 'False':
  		logging.info("IMDB INFO Not Found From Response")
  		logging.info("Sending IMDB Request to Bot")
  		status = await message.reply_text(f"SEND IMDB Link Within {sleeptime}sec")	
  		await asyncio.sleep(sleeptime)
  		for i in range(0,sleeptime):
  			u_id = status.message_id + 1
  			m = await client.get_messages(message.chat.id ,u_id)
  			if m.text is not None and m.from_user.id == user_id:
  			    IMDBURL= str(m.text)
  			    logging.info(f"Fetched IMDB URL : {IMDBURL}")
  			    await status_message.delete()
  			    await status_message.reply_text(f"<b>Fetching INFO</b>\nIMDB : <i>{IMDBURL}</i>")
  			    IMDBID = IMDBURL.split("/tt")[1]
  			    logging.info(f"Requesting OMDB Again With IMDB ID : {IMDBID}")
  			    IMDB = requests.get(f'http://www.omdbapi.com/?i=tt{IMDBID}&apikey={OMDB_API}&r=json').json()
  			    break					
  				
  	BBCODE =''
  	if IMDB['Response'] == 'True':
  		logging.info("OMDB response is Success")
  		BBCODE,Backdrop = getBBCODE(IMDB,MEDIAINFO,LINK)
  		if os.path.exists("BBCODE.txt"):
  			logging.info("Old BBCODE exists in folder")
  			os.remove("BBCODE.txt")
  			logging.info("Old BBCODE file removed")
  		with open("BBCODE.txt",'w',encoding='UTF-8') as f:
  			logging.info("Saving BBCODE to txt")
  			f.write(BBCODE)
  			logging.info("BBCODE Saved")
  			
  		#print(BBCODE)
  			
  		TITLES = MOVIE_NAME.replace(".mkv",'') +f" [{SIZE}]"
  		TAGS = getTags(IMDB,Language,MOVIE_NAME)
  		if not Language=="English":
  			TITLES = f"[{Language}] {TITLES}"
  		TITLES = f"<b>TITLE</b> : <code>{TITLES}</code>\n\n<b>TAGS</b> : <code>{TAGS}</code>\n<b>Poster</b> : <a href='{Backdrop}'>Link</a>"
  		time.sleep(1)
  		if os.path.exists("BBCODE.txt"):
  			await status_message.delete()
  			await client.send_document(
  			chat_id=message.chat.id,
  			document="BBCODE.txt",
  			caption=TITLES,
  			reply_to_message_id=reply_to_id
  			)
  			logging.info(f"Done Generating : {TITLES}")
  		else:
  			await status_message.delete()
  			msgfail = f"Failed To Fetch BBCODE\nTitle : <code>{MOVIE_NAME}</code>"
  			logging.info("Failed To Fetch Info")
  			status_message = await message.reply_text(msgfail)
  
async def BPTV(client, message):
  ####--PARSER-FOR-TVSHOW--####
  reply_to_id = message.message_id
  user_id = message.from_user.id
  u_id = message.message_id
  logging.info("STARTING BLACKPEARL BBCODE GENERATOR By D.Luffy")
  logging.info("Selected Mode : TV SHOW")
  IMDBID=''
  IMDBURL =''
  IMDB =''
  LINK =''
  SIZE =''
  logging.info("Starting Looping Files For Template")
  
  #FINDFILES THROUGH LOOP
  MOVIESPATH = TVPATH[:-1]
  mvpath = str(message.text)
  
  MVPATH = mvpath.replace("/tv ","")
  if not MVPATH =="":
  	MOVIESPATH = MAINPATH +MVPATH
  	logging.info(f"Checking Files : {MVPATH}")	

  logging.info("Fetching Movie Files")
  for MOVIES in find_files(MOVIESPATH , [ 'mkv','mp4','avi','mov']):
  	TYPE ='TVSHOW'
  	time.sleep(1)
  	MOVIE_PATH = str(MOVIES)
  	MOVIE_PATH = MOVIE_PATH.replace("\\","/")
  	if "E01" in MOVIE_PATH:
  		#ONLY-TAKES-FIRSTEPISODE#
	  	logging.info(f"Running Generator For - {MOVIE_PATH}")
	  	MOVIE_NAME= MOVIE_PATH.replace(MOVIESPATH,'')
	  	seriesnames = MOVIE_NAME.split("/")[1]
	  	msgtxt = f"Started Fetching BBCODE\nTitle : <code>{seriesnames}</code>"
	  	status_message = await message.reply_text(msgtxt)
	  	time.sleep(1)
	  	MEDIAINFO = getMediaInfo(MOVIE_PATH,MOVIE_NAME)
	  	time.sleep(1)
	  	Language = getLANG(MOVIE_PATH)
	  	TITLE,YEAR = getOMDB(MOVIE_NAME)
	  	LINK,GDLINK,SIZE = getLINK(MOVIE_PATH,TYPE)
	  	###---DOING--OMDB--REQUEST--###
	  	logging.info("Requesting OMDB")
	  	IMDB = requests.get(f'http://www.omdbapi.com/?t={TITLE}{YEAR}&apikey={OMDB_API}&r=json').json()
	  	if IMDB['Response'] == 'False':
	  		logging.info("IMDB INFO Not Found From Response")
	  		logging.info("Sending IMDB Request to Bot")
	  		status = await message.reply_text(f"Send IMDB Link within {sleeptime}sec")
	  		await asyncio.sleep(sleeptime)
	  		for i in range(0,sleeptime):
	  			u_id = status.message_id + 1
	  			m = await client.get_messages(message.chat.id ,u_id)
	  			if m.text is not None and m.from_user.id == user_id:
	  			    IMDBURL= str(m.text)
	  			    logging.info(f"Fetched IMDB URL : {IMDBURL}")
	  			    await status_message.delete()
	  			    await status_message.reply_text(f"<b>Fetching INFO</b>\nIMDB : <i>{IMDBURL}</i>")
	  			    IMDBID = IMDBURL.split("/tt")[1]
	  			    logging.info(f"Requesting OMDB Again With IMDB ID : {IMDBID}")
	  			    IMDB = requests.get(f'http://www.omdbapi.com/?i=tt{IMDBID}&apikey={OMDB_API}&r=json').json()
	  			    break					
	  				
	  	BBCODE =''
	  	if IMDB['Response'] == 'True':
	  		logging.info("OMDB response is Success")
	  		BBCODE,Backdrop = getBBCODE(IMDB,MEDIAINFO,LINK)
	  		if os.path.exists("BBCODE.txt"):
	  			logging.info("Old BBCODE exists in folder")
	  			os.remove("BBCODE.txt")
	  			logging.info("Old BBCODE file removed")
	  		with open("BBCODE.txt",'w',encoding='UTF-8') as f:
	  			logging.info("Saving BBCODE to txt")
	  			f.write(BBCODE)
	  			logging.info("BBCODE Saved")
	  		#print(BBCODE)
	  		TAGS = getTags(IMDB,Language,seriesnames)
	  		TITLES = seriesnames +f" [{SIZE}]"
	  		if not Language=="English":
	  			TITLES = f"[{Language}] {TITLES}"		
	  		TITLES = f"<b>TITLE</b> : <code>{TITLES}</code>\n\n<b>TAGS</b> : <code>{TAGS}</code>\n<b>Poster</b> : <a href='{Backdrop}'>Link</a>"
	  		time.sleep(1)
	  		if os.path.exists("BBCODE.txt"):
	  			await status_message.delete()
	  			await client.send_document(
	  			chat_id=message.chat.id,
	  			document="BBCODE.txt",
	  			caption=TITLES,
	  			reply_to_message_id=reply_to_id
	  			)
	  			logging.info(f"Done Generating : {TITLES}")
	  		else:
	  			await status_message.delete()
	  			msgfail = f"Failed To Fetch BBCODE\nTitle : <code>{MOVIE_NAME}</code>"
	  			status_message = await message.reply_text(msgfail)
	  			logging.info("Failed To Fetch Info")
	  			##--END--##




if __name__ == "__main__" :
 app2 = Client(
        "himessage",
        bot_token=TG_BOT_TOKEN,
        api_id=APP_ID,
        api_hash=API_HASH
    )


bpmvbot = MessageHandler(BPMV,
 filters=filters.chat(chats=AUTH_CHANNEL) & _link_match_filt_er("/movie"))
bptvbot = MessageHandler(BPTV,
 filters=filters.chat(chats=AUTH_CHANNEL) & _link_match_filt_er("/tv"))
 
app2.add_handler(bpmvbot)
app2.add_handler(bptvbot)
app2.run()
