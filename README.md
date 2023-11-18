[//]: # (Template: https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
# MGY Bot

Discord Bot in python. <br/>
Includes music playing, moderation tools, games, trolls, user and level management using a postgres database.

Be aware that this started a few years ago as a small, personal and troll project that eventually grew a bit, there wasn't much planning, actually there wasn't any thinking involved at all. I did refactor it recently so it is somewhat readable, be careful and good luck.

Bot language is in PT-BR


## How to add bot to my server

This bot is not publically available. <br/>
I do run a private instance, feel free to message me or run your own<br/>

Use *mgy* prefix to run commands. Example:
> mgy help

## Getting Started
- Clone the repo
- Copy .env.example, rename it to .env and update the variables with your credentials
- Install dependencies

```bash
pip install -r poetry
poetry install
```

Run bot
```bash
poetry run python main.py
```

### Prerequisites

* Git
* Python ^3.11
* Postgres database
* [Dicord bot token](https://discord.com/developers/applications) 
* [Spotify token](https://developer.spotify.com/)
* YouTube API token - You need to create a GCP account for this and enable the YouTube Data v3 API. [Here](https://developers.google.com/youtube/v3/getting-started) is a guide on how to do it
* YouTube cookies.txt - optional file. Can help avoid errors in age restricted videos
* [FFMpeg](https://ffmpeg.org/download.html) - Make sure you have FFMPeg
* Everything else in: *pyproject.toml*

## Built With

* [Python](https://www.python.org/) - Python 3.11
* [DiscordPy](https://github.com/Rapptz/discord.py) - discord.py 2.2
* [yt-dlp](https://github.com/yt-dlp/yt-dlp) - yt-dlp (always up to date)
* [ruff](https://github.com/astral-sh/ruff) - Ruff for linting and code styling

### TODOs
* There is a lot of TODO tags in code
* Fix styling and variable/classes/method/logs names
* reddit module
* twitch module
* markov module
* optimizations
* Make every module optional and give warnings instead of errors
* Fix spotipy - Randomly gives errors 403 - Support more links
* Fix dropbox mashups
* Automate deploy
* Anything you want

## Authors

* **Ulf** - *everything* - [Ulf881](https://github.com/ulf881)
* **Max** - *crappyDungeonCrawlerForPython* - https://www.youtube.com/channel/UCzyiiswVM6UyCD_G6A7ee2g

See also the list of [contributors](https://github.com/ulf881/mgy-bot/graphs/contributors) who participated in this project.

## Acknowledgments

* Template by [PurpleBooth](https://github.com/PurpleBooth/a-good-readme-template)

## Extras
Level up table and rules

| level 	| xp      	| next   	| increment (10%) 	|
|-------	|---------	|--------	|-----------------	|
| 1     	| 0       	| 1000   	| 100             	|
| 2     	| 1000    	| 1100   	| 110             	|
| 3     	| 2100    	| 1210   	| 121             	|
| 4     	| 3310    	| 1331   	| 133             	|
| 5     	| 4641    	| 1464   	| 146             	|
| 6     	| 6105    	| 1610   	| 161             	|
| 7     	| 7715    	| 1771   	| 177             	|
| 8     	| 9487    	| 1948   	| 194             	|
| 9     	| 11435   	| 2143   	| 214             	|
| 10    	| 13579   	| 2357   	| 235             	|
| 11    	| 15937   	| 2593   	| 259             	|
| 12    	| 18531   	| 2853   	| 285             	|
| 13    	| 21384   	| 3138   	| 313             	|
| 14    	| 24522   	| 3452   	| 345             	|
| 15    	| 27974   	| 3797   	| 379             	|
| 16    	| 31772   	| 4177   	| 417             	|
| 17    	| 35949   	| 4594   	| 459             	|
| 18    	| 40544   	| 5054   	| 505             	|
| 19    	| 45599   	| 5559   	| 555             	|
| 20    	| 51159   	| 6115   	| 611             	|
| 21    	| 57274   	| 6727   	| 672             	|
| 22    	| 64002   	| 7400   	| 740             	|
| 23    	| 71402   	| 8140   	| 814             	|
| 24    	| 79543   	| 8954   	| 895             	|
| 25    	| 88497   	| 9849   	| 984             	|
| 26    	| 98347   	| 10834  	| 1083            	|
| 27    	| 109181  	| 11918  	| 1191            	|
| 28    	| 121099  	| 13109  	| 1310            	|
| 29    	| 134209  	| 14420  	| 1442            	|
| 30    	| 148630  	| 15863  	| 1586            	|
| 31    	| 164494  	| 17449  	| 1744            	|
| 32    	| 181943  	| 19194  	| 1919            	|
| 33    	| 201137  	| 21113  	| 2111            	|
| 34    	| 222251  	| 23225  	| 2322            	|
| 35    	| 245476  	| 25547  	| 2554            	|
| 36    	| 271024  	| 28102  	| 2810            	|
| 37    	| 299126  	| 30912  	| 3091            	|
| 38    	| 330039  	| 34003  	| 3400            	|
| 39    	| 364043  	| 37404  	| 3740            	|
| 40    	| 401447  	| 41144  	| 4114            	|
| 41    	| 442592  	| 45259  	| 4525            	|
| 42    	| 487851  	| 49785  	| 4978            	|
| 43    	| 537636  	| 54763  	| 5476            	|
| 44    	| 592400  	| 60240  	| 6024            	|
| 45    	| 652640  	| 66264  	| 6626            	|
| 46    	| 718904  	| 72890  	| 7289            	|
| 47    	| 791795  	| 80179  	| 8017            	|
| 48    	| 871974  	| 88197  	| 8819            	|
| 49    	| 960172  	| 97017  	| 9701            	|
| 50    	| 1057189 	| 106718 	| 10671           	|
| 51+   	| 1281299 	| -      	| -               	|