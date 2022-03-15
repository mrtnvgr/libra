#!/bin/python3
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, math, os, sys, requests, shutil, datetime, json, zipfile, colorsys
from natsort import natsorted, IGNORECASE
from random import randint

GIT_API_URL = "https://api.github.com/repos/mrtnvgr/libra/releases/latest"
GIT_RELEASE_URL = "https://github.com/mrtnvgr/libra/releases/latest/download/libra"
version = "2022.0315-3"
title = "Libra " + version
DEFAULT_CONFIG = """{
    "resolution": [1920,1080],
    "fullscreen": "true",
	"keybinds": {
        "notes": ["q","w","LEFTBRACKET", "RIGHTBRACKET"],
        "back": "ESCAPE",
        "randomMap": "F2",
        "reload": "F3",
        "toggleMapBackground": "F4",
        "toggleUserGameplayBackground": "F4",
        "toggleUserMapSelectionBackground": "F4"
    },
	"note": {
		"type": "bar",
		"speed": 1.9,
		"size": 0.95
	},
    "audioOffset": 0,
    "fps": 500,
    "mods": {
        "suddenDeath": "false",
        "hardrock": "false",
        "mirror": "false"
    },
    "saveScores": "true",
	"interface": {
		"gameplay": {
			"songName": {
				"state": "true",
                "color": [255,255,255]
			},
			"accuracy": {
				"state": "true",
                "color": [255,255,255]
			},
			"combo": {
				"state": "true",
                "color": [255,255,255]
			},
			"judgement": {
				"state": "true"
			},
			"judgementCounter": {
				"state": "true",
                "textColor": [255,255,255]
			},
			"hitOverlay": {
				"state": "true"
			},
			"score": {
				"state": "true",
                "color": [255,255,255]
			},
			"mods": {
				"state": "true",
                "color": [255,255,255]
			}
		},
        "mapSelection": {
            "maps": {
                "color": [255,255,255]
            },
            "search": {
                "color": [255,255,255]
            },
            "mapsHeader": {
                "color": [255,255,255]
            },
            "mapsLine": {
                "color": [255,255,255]
            }
        },
		"mainMenu": {
			"title": {
				"color": [255,255,255]
			},
			"options": {
				"color": [255,255,255]
			},
			"optionsLine": {
				"color": [255,255,255]
			},
			"version": {
				"color": [255,255,255]
			}
		},
        "title": {
            "color": [255,255,255]
        },
        "updateText": {
            "color": [255,255,255]
        },
        "mapParsing": {
            "color": [255,255,255]
        },
        "ranking": {
            "color": [255,255,255]
        },
		"aboutText": {
			"color": [255,255,255]
		}
	},
    "backgrounds": {
        "userBackgrounds": {
			"mapSelection": {
                "state": "false",
				"file": ""
			},
			"gameplay": {
                "state": "false",
				"file": ""
			}
        },
		"mapBackground": {
			"state": "true",
			"brightness": 40
		}
    },
	"hitwindow": [
        135,
        90,
        22
    ],
    "rgb": {
        "speed": 0.05,
        "saturation": 35,
        "value": 69
    },
    "hitColors": [
        [171,0,0],
        [171,170,0],
        [0,171,111],
        [0,167,171]
    ],
    "colors": [
        [171,171,171],
        "rgb",
		"rgb",
        [171,171,171]
    ],
    "autoUpdate": "true"
}"""
def configReload():
    while(1):
        try:
            config = json.load(open("config.json"))
            break
        except FileNotFoundError:
            print("Config does not exist. Writing default")
            open("config.json", "w").write(DEFAULT_CONFIG)
            continue
    if config["mods"]["hardrock"].lower()=="true":
        for i in range(len(config["hitwindow"])): config["hitwindow"][i] = config["hitwindow"][i]//1.5
    return config
config = configReload()

pygame.display.set_caption(title)
pygame.font.init()
pygame.mixer.init()
clock = pygame.time.Clock()

flags = 0
if config["fullscreen"].lower()=="true": flags = pygame.FULLSCREEN
screen = pygame.display.set_mode(tuple(config["resolution"]), flags)
pygame.mouse.set_visible(False)
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])

BLACK = (0, 0, 0)

font = pygame.font.SysFont('Arial', 25)
fontBold = pygame.font.SysFont('Arial', 25, bold=True)
fontScore = pygame.font.SysFont('Arial', 60)
fontMMTitle = pygame.font.SysFont('Arial', 80, bold=True)

# check updates
if config["autoUpdate"].lower()=="true":
    try:
        remote_version = requests.get(GIT_API_URL).json()["name"]
    except:
        print("No internet connection!")
        remote_version = version
    if remote_version!=version:
        screen.blit(fontBold.render(title, True, tuple(config["interface"]["title"]["color"])), (0,0))
        screen.blit(fontBold.render("Updating...", True, tuple(config["interface"]["updateText"]["color"])), (0,20))
        pygame.display.flip()
        if os.name=="nt":
            os_prefix = ".exe"
        else:
            os_prefix = ""
        open("libra-"+remote_version+os_prefix, "wb").write(requests.get(GIT_RELEASE_URL+os_prefix, stream=True).content)
        sys.exit(0)

def padding(score, max):
    ret = str(math.floor(score))
    return "0" * (max - len(ret)) + ret

def hsv2rgb(h,s,v):
    return [round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v)]

def parseMap(map, config):
    if os.path.exists("maps/"+map+"/map.osu")==True:
        mapdata = open("maps/"+map+"/map.osu", "r", encoding="utf-8").read().split("\n")
        type = "osu"
    mapdata = [value for value in mapdata if value]
    hitObjects = False
    background = ""
    converted = []
    for mapline in mapdata:
        if type=="osu":
            if ("png" in mapline or "jpg" in mapline or "jpeg" in mapline) and mapline[0]=="0":
                backgroundfile = mapline.split(",")[2].replace('"', "")
                if os.path.exists("maps/"+map+"/"+backgroundfile): background = backgroundfile
            if hitObjects==True:
                splitted = mapline.split(",")
                noteRow = int((int(splitted[0])*4)/512)
                if config["mods"]["mirror"].lower()=="true": noteRow = abs(noteRow-3)
                try:
                    if int(splitted[5].split(":")[0])<2:
                        converted.append([int(splitted[2]), noteRow])
                    else:
                        converted.append([int(splitted[2]), noteRow, int(splitted[5].split(":")[0]), False, 0])
                except ValueError:
                    return [[], []]
            else:
                if mapline=="[HitObjects]":
                    hitObjects = True
    return [converted, background]

def reloadMaps():
    files = os.listdir('maps/')
    maps = []
    for dir in files:
        if os.path.isdir(os.path.join('maps/', dir)):
            maps.append(dir)
    return natsorted(maps, alg=IGNORECASE)

def importMaps():
    files = os.listdir('maps/')
    newMaps = []
    for dir in files:
            if ".osz" in dir:
                screen.fill(BLACK)
                screen.blit(fontBold.render(title, True, tuple(config["interface"]["title"]["color"])), (0,0))
                screen.blit(fontBold.render("Unzipping...", True, tuple(config["interface"]["mapParsing"]["color"])), (0,20))
                pygame.display.flip()
                oszfile = zipfile.ZipFile(os.path.join('maps/', dir))
                for diff in oszfile.namelist():
                    if ".osu" in diff:
                        oszfile.extract(diff, "maps/"+diff[:-4])
                        newMaps.append(diff[:-4])
                        try:
                            os.rename("maps/"+diff[:-4]+"/"+diff, "maps/"+diff[:-4]+"/map.osu")
                        except FileExistsError:
                            pass
                        osufile = open("maps/"+diff[:-4]+"/map.osu", encoding="utf-8").read().split("\n")
                        for osuline in osufile:
                            if "AudioFilename" in osuline:
                                audiofile = osuline.replace("AudioFilename:", "")
                                if audiofile[0]==" ": audiofile = audiofile[1:]
                                try:
                                    oszfile.extract(audiofile, "maps/"+diff[:-4]+"/")
                                except KeyError:
                                    pass
                            elif "jpg" in osuline or "png" in osuline or "jpeg" in osuline:
                                try:
                                    oszfile.extract(osuline.split(",")[2].replace('"', ""), "maps/"+diff[:-4]+"/")
                                except KeyError or IndexError:
                                    pass
                oszfile.close()
                os.remove(os.path.join('maps/', dir))
    return newMaps

def mmLoop():
    mmIndex = 0
    mmElements = ["Singleplayer", "About", "Exit"]
    while(1):
        clock.tick(config["fps"])
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_UP and mmIndex>0:
                    mmIndex -= 1
                elif event.key==pygame.K_DOWN and mmIndex<len(mmElements)-1:
                    mmIndex += 1
                elif event.key==eval(f"pygame.K_{config['keybinds']['back']}"):
                    return 0
                elif event.key==pygame.K_RETURN:
                    if mmIndex==0:
                        return "GAME"
                    elif mmIndex==1:
                        return "ABOUT"
                    elif mmIndex==2:
                        return "EXIT"
            elif event.type==pygame.QUIT:
                return 0
        text = fontMMTitle.render("L18RA", True, tuple(config["interface"]["mainMenu"]["title"]["color"]))
        text_rect = text.get_rect(center=(config["resolution"][0]/2, 100))
        screen.blit(text, text_rect)
        position = 300
        for i in range(len(mmElements)):
            screen.blit(fontBold.render(mmElements[i], True, tuple(config["interface"]["mainMenu"]["options"]["color"])), (30,position))
            if mmIndex==i:
                pygame.draw.rect(screen, tuple(config["interface"]["mainMenu"]["optionsLine"]["color"]), pygame.Rect(0, position, 15, 29))
            position += 30
        screen.blit(fontBold.render("Build: " + version, True, tuple(config["interface"]["mainMenu"]["version"]["color"])), (0,config["resolution"][1]-50))
        pygame.display.flip()

def aboutLoop():
    while(1):
        clock.tick(config["fps"])
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==eval(f"pygame.K_{config['keybinds']['back']}") or event.key==pygame.K_RETURN:
                    return
            elif event.type==pygame.QUIT:
                return 0
        abouttext = """
L18RA(Libra) - customizable VSRG client"""
        for i, l in enumerate(abouttext.splitlines()):
                    screen.blit(fontBold.render(l, True, tuple(config["interface"]["aboutText"]["color"])), (0, 25*i))
        pygame.display.flip()

def gameLoop():
    loadedMap = []
    loadedObjects = []
    selectedMapIndex = 0
    oldIndex = 0
    selectingMaps = ""
    selectingMapsCooldown = 0
    keysDown = [False, False, False, False]
    keysPressed = [False, False, False, False]
    keysReleased = [False, False, False, False]
    isPlaying = False
    playingFrame = 0
    combo = 0
    maxCombo = 0
    curScore = 0.0
    hitCount = {
        'perfect': 0,
        'good': 0,
        'bad': 0,
        'miss': 0
    }
    hit = ""
    searchtext = ""
    rgbHue = 0
    try:
        os.listdir('maps/')
    except FileNotFoundError:
        os.mkdir('maps')
    newMaps = importMaps()
    maps = reloadMaps()
    if newMaps!=[]:
        for newMap in newMaps:
            if newMap in maps:
                maps.remove(newMap)
                maps = [newMap] + maps # новые песни в начало списка
    oldmaps = maps
    config = configReload()
    background = ""
    if config["backgrounds"]["userBackgrounds"]["mapSelection"]["state"].lower()=="true":
        mapSelectionBg = pygame.image.load(config["backgrounds"]["userBackgrounds"]["mapSelection"]['file']).convert()
    if config["backgrounds"]["userBackgrounds"]["gameplay"]["state"].lower()=="true":
        gameplayBg = pygame.image.load(config["backgrounds"]["userBackgrounds"]["gameplay"]["file"]).convert()
    rgbColorsStates = []
    for i in range(4):
        if config["colors"][i]=="rgb":
            rgbColorsStates.append(True)
        else:
            rgbColorsStates.append(False)
    while(1):
        clock.tick(config["fps"])
        screen.fill(BLACK)
        if not isPlaying and loadedObjects!=[]:
            loadedObjects = []
            keysDown = [False, False, False, False]
            keysPressed = [False, False, False, False]
            keysReleased = [False, False, False, False]
            maxCombo = 0
            combo = 0
            curScore = 0.0
            hitCount = {
                "perfect": 0,
                "good": 0,
                "bad": 0,
                "miss": 0
            }
            hit = ""
        if config["backgrounds"]["mapBackground"]["state"]=="true" and background!="" and isPlaying:
            screen.blit(backgroundBg, backgroundBg.get_rect())
        if config["backgrounds"]["userBackgrounds"]["mapSelection"]["state"].lower()=="true" and isPlaying==False:
            screen.blit(mapSelectionBg, mapSelectionBg.get_rect())
        elif config["backgrounds"]["userBackgrounds"]["gameplay"]["state"].lower()=="true" and isPlaying:
            screen.blit(gameplayBg, gameplayBg.get_rect())
        for i in range(len(keysPressed)):
            keysPressed[i] = False
            keysReleased[i] = False
        if selectedMapIndex<0:
            selectedMapIndex = len(maps)-1
        elif selectedMapIndex==len(maps):
            selectedMapIndex = 0
        if selectingMaps!="" and not isPlaying:
            if selectingMapsCooldown==(config["fps"]//12):
                if selectingMaps=="down":
                    selectedMapIndex += 1
                elif selectingMaps=="up":
                    selectedMapIndex -= 1
            else:
                selectingMapsCooldown += 1
        
        if config["mods"]["suddenDeath"].lower()=="true" and hitCount["miss"]>0:
            isPlaying = False
            pygame.mixer.music.stop()

        # rgb logic
        if rgbHue==360: rgbHue = 0
        rgbHue += config["rgb"]["speed"]
        rgbColor = hsv2rgb(rgbHue/360,config["rgb"]["saturation"]/100,config["rgb"]["value"]/100)
        for i in range(4):
            if rgbColorsStates[i]==True:
                config["colors"][i] = rgbColor

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return 0
            if event.type == pygame.KEYDOWN:
                if event.key==eval(f"pygame.K_{config['keybinds']['back']}"):
                    if isPlaying:
                        selectingMaps = ""
                        isPlaying = False
                        pygame.mixer.music.stop()
                    else:
                        return
                if event.key==eval(f"pygame.K_{config['keybinds']['toggleMapBackground']}"):
                    config["backgrounds"]["mapBackground"]["state"] = 'true' if config["backgrounds"]["mapBackground"]["state"] == 'false' else 'false'
                elif event.key==eval(f"pygame.K_{config['keybinds']['toggleUserGameplayBackground']}"):
                    config["backgrounds"]["userBackgrounds"]["gameplay"]["state"] = 'true' if config["backgrounds"]["userBackgrounds"]["gameplay"]["state"] == 'false' else 'false'
                elif event.key==eval(f"pygame.K_{config['keybinds']['toggleUserMapSelectionBackground']}"):
                    config["backgrounds"]["userBackgrounds"]["mapSelection"]["state"] = 'true' if config["backgrounds"]["userBackgrounds"]["mapSelection"]["state"] == 'false' else 'false'
                if event.key == pygame.K_DOWN and not isPlaying:
                    selectedMapIndex += 1
                    selectingMaps = "down"
                elif event.key == pygame.K_UP and not isPlaying:
                    selectedMapIndex -= 1
                    selectingMaps = "up"
                elif event.key==pygame.K_DELETE and not isPlaying:
                    shutil.rmtree("maps/"+maps[selectedMapIndex], ignore_errors=True)
                    maps = reloadMaps()
                    if newMaps!=[]:
                        for newMap in newMaps:
                            if newMap in maps:
                                maps.remove(newMap)
                                maps = [newMap] + maps # новые песни в начало списка
                    oldmaps = maps
                elif event.key==eval(f"pygame.K_{config['keybinds']['reload']}") and not isPlaying:
                    newMaps = importMaps()
                    maps = reloadMaps()
                    if newMaps!=[]:
                        for newMap in newMaps:
                            if newMap in maps:
                                maps.remove(newMap)
                                maps = [newMap] + maps # новые песни в начало списка
                    oldmaps = maps
                    config = configReload()
                elif event.key==eval(f"pygame.K_{config['keybinds']['randomMap']}") and not isPlaying:
                    selectedMapIndex = randint(0, len(maps))
                elif event.key == pygame.K_RETURN and not isPlaying:
                    if maps==[]: continue 
                    if os.path.exists("maps/"+maps[selectedMapIndex]+"/map.osu"):
                        for line in open("maps/"+maps[selectedMapIndex]+"/map.osu", encoding="utf-8").read().split("\n"):
                            if "AudioFilename" in line:
                                songfile = line.replace("AudioFilename:", "")
                                if songfile[0]==" ": songfile = songfile[1:]
                    try:
                        pygame.mixer.music.load("maps/"+maps[selectedMapIndex]+"/"+songfile)
                    except pygame.error:
                        continue
                    pygame.mixer.music.play()
                    pygame.mixer.music.pause()
 
                    loadedFile = parseMap(maps[selectedMapIndex], config)
                    if loadedFile[0]==[]: continue
                    loadedMap = loadedFile[0]
                    background = loadedFile[1]
                    if background!="":
                        backgroundBg = pygame.transform.scale(pygame.image.load("maps/"+maps[selectedMapIndex]+"/"+background).convert(), tuple(config["resolution"]))
                        backgroundBg.set_alpha(config["backgrounds"]["mapBackground"]["brightness"])
                    for i in range(100):
                        try:
                            loadedObjects.append(loadedMap.pop(0))
                        except IndexError:
                            break
                    isPlaying = True
                    playingFrame = pygame.time.get_ticks()
                else:
                    if isPlaying:
                        for i in range(len(config["keybinds"]["notes"])):
                            if event.key == eval(f"pygame.K_{config['keybinds']['notes'][i]}"):
                                keysDown[i] = True
                                keysPressed[i] = True
                    else:
                        if event.type==pygame.KEYDOWN:
                            if searchtext=="":
                                oldIndex = selectedMapIndex
                            if event.key==pygame.K_BACKSPACE and searchtext!="":
                                searchtext = searchtext[:-1]
                                maps = oldmaps
                                selectedMapIndex = 0
                            if len(pygame.key.name(event.key))<2:
                                searchtext = searchtext + pygame.key.name(event.key)
                                selectedMapIndex = 0
                            elif event.key==pygame.K_SPACE:
                                searchtext = searchtext + " "
                                selectedMapIndex = 0
                            searchmaps = []
                            for i in maps:
                                if searchtext.lower() in i.lower(): searchmaps.append(i)
                            maps = searchmaps
                            if searchtext=="":
                                selectedMapIndex = oldIndex
                            
            elif event.type == pygame.KEYUP:
                if (event.key==pygame.K_DOWN or event.key==pygame.K_UP) and not isPlaying:
                    selectingMapsCooldown = 0
                    selectingMaps = ""
                if isPlaying:
                    for i in range(len(config["keybinds"]["notes"])):
                        if event.key == eval(f'pygame.K_{config["keybinds"]["notes"][i]}'):
                            keysDown[i] = False
                            keysReleased[i] = True
                            
        for i in range(len(keysDown)):
            if isPlaying:
                if config["note"]["type"]=="circle":
                    pygame.draw.circle(screen, config["colors"][i], ((config["resolution"][0]/2)-220*config["note"]["size"] + i * int(140*config["note"]["size"]), config["resolution"][1]-100), int(60*config["note"]["size"]), 5)
                    if keysDown[i]:
                        pygame.draw.circle(screen, config["colors"][i], ((config["resolution"][0]/2)-220*config["note"]["size"] + i * int(140*config["note"]["size"]), config["resolution"][1]-100), int(60*config["note"]["size"]))
                elif config["note"]["type"]=="bar":
                    pygame.draw.rect(screen, config["colors"][i], pygame.Rect(config["resolution"][0]/2-286*config["note"]["size"] + i * int(140*config["note"]["size"]), config["resolution"][1]-101, int(120*config["note"]["size"]), 50), 5)
                    if keysDown[i]:
                        pygame.draw.rect(screen, config["colors"][i], pygame.Rect(config["resolution"][0]/2-286*config["note"]["size"] + i * int(140*config["note"]["size"]), config["resolution"][1]-101, int(120*config["note"]["size"]),50))

        if isPlaying and playingFrame + 1000 < pygame.time.get_ticks():
            if len(loadedObjects) == 0:
                isPlaying = False
                mods = []
                for i in config["mods"]:
                    if config["mods"][i].lower()=="true":
                        mods.append(i)
                if mods==[]: mods = ""
                time = datetime.datetime.today().strftime('%Y-%m-%d(%H:%M)')
                data = f"""{maps[selectedMapIndex]}
{time}
Mods: {' '.join(mods)}
Perfect: {hitCount['perfect']} 
Good: {hitCount['good']}
Bad: {hitCount['bad']}
Miss: {hitCount['miss']}
Accuracy: {accuracy}
Combo: {maxCombo}
Score: {padding(curScore, 8)}"""
                if config["saveScores"].lower()=="true":
                    try:
                        os.listdir('scores')
                    except FileNotFoundError:
                        os.mkdir("scores")
                    open("scores/"+maps[selectedMapIndex]+f" ({time}).scr", "w").write(data)
                screen.fill(BLACK)
                screen.blit(fontBold.render(title, True, tuple(config["interface"]["title"]["color"])), (0,0))
                for i, l in enumerate(data.splitlines()):
                    screen.blit(font.render(l, True, tuple(config["interface"]["ranking"]["color"])), (0, 25 + 25*i))
                pygame.display.flip()
                while True:
                    event = pygame.event.wait()
                    if event.type==pygame.QUIT:
                        return 0
                    elif (event.type==pygame.KEYDOWN and event.key==eval(f"pygame.K_{config['keybinds']['back']}")):
                        return
                    elif event.type==pygame.KEYDOWN and event.key==pygame.K_RETURN: break
                loadedObjects = []
                keysDown = [False, False, False, False]
                keysPressed = [False, False, False, False]
                keysReleased = [False, False, False, False]
                combo = 0
                maxCombo = 0
                curScore = 0.0
                hitCount = {
                    "perfect": 0,
                    "good": 0,
                    "bad": 0,
                    "miss": 0
                }
                hit = ""
                pygame.mixer.music.stop()
                continue
            unloadedObjects = loadedObjects
            loadedLaneObjects = [[], [], [], []]
            for obj in loadedObjects:
                for i in range(len(keysPressed)):
                    if keysPressed[i] or keysReleased[i]:
                        if obj[1] == i:
                            if obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame) < 500:
                                loadedLaneObjects[i].append(obj)
                                break
                if len(obj) == 5:
                    if config["note"]["type"]=="circle":
                        if not obj[3]:
                            pygame.draw.circle(screen, config["colors"][obj[1]], ((config["resolution"][0]/2)-220*config["note"]["size"] + obj[1] * int(140*config["note"]["size"]),config["resolution"][1]-100 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["note"]["speed"]), int(60*config["note"]["size"]) )
                        pygame.draw.circle(screen, config["colors"][obj[1]], ((config["resolution"][0]/2)-220*config["note"]["size"] + obj[1] * int(140*config["note"]["size"]),config["resolution"][1]-100 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["note"]["speed"]), int(60*config["note"]["size"]) )
                    elif config["note"]["type"]=="bar":
                        if not obj[3]:
                            pygame.draw.rect(screen, config["colors"][obj[1]], pygame.Rect(config["resolution"][0]/2-286*config["note"]["size"] + obj[1] * int(140*config["note"]["size"]), config["resolution"][1]-101 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["note"]["speed"], int(120*config["note"]["size"]),50))
                        pygame.draw.rect(screen, config["colors"][obj[1]], pygame.Rect(config["resolution"][0]/2-286*config["note"]["size"] + obj[1] * int(140*config["note"]["size"]), config["resolution"][1]-101 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["note"]["speed"], int(120*config["note"]["size"]),50))

                    if config["note"]["type"]=="circle":
                        rect1 = (config["resolution"][0]/2)-280*config["note"]["size"] + obj[1] * int(140*config["note"]["size"])
                    elif config["note"]["type"]=="bar":
                        rect1 = config["resolution"][0]/2-286*config["note"]["size"] + obj[1] * int(140*config["note"]["size"])
                    rect2 = config["resolution"][1]-100 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["note"]["speed"]
                    rect3 = (120*config["note"]["size"])
                    if not obj[3]:
                        rect4 = (config["resolution"][1]-100 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["note"]["speed"]) - rect2
                    else:
                        rect4 = (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["note"]["speed"]
                    pygame.draw.rect(screen, config["colors"][obj[1]], pygame.Rect(rect1, rect2, rect3, rect4))
                    
                    if config["resolution"][1]-100 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["note"]["speed"] > config["resolution"][0]-300:
                        hit = "miss"
                        hitCount[hit] += 1
                        unloadedObjects.remove(obj)
                        if len(loadedMap) != 0:
                            unloadedObjects.append(loadedMap.pop(0))
                else:
                    if config["note"]["type"]=="circle":
                        pygame.draw.circle(screen, tuple(config["colors"][obj[1]]), ((config["resolution"][0]/2)-220*config["note"]["size"] + obj[1] * int(140*config["note"]["size"]), config["resolution"][1]-100 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["note"]["speed"]), int(60*config["note"]["size"]) )
                    elif config["note"]["type"]=="bar":
                        pygame.draw.rect(screen, tuple(config["colors"][obj[1]]), pygame.Rect(config["resolution"][0]/2-286*config["note"]["size"] + obj[1] * int(140*config["note"]["size"]), config["resolution"][1]-101 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["note"]["speed"], int(120*config["note"]["size"]),50))


                    if config["resolution"][1]-100 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["note"]["speed"] > config["resolution"][0]-300:
                        hit = "miss"
                        hitCount[hit] += 1
                        unloadedObjects.remove(obj)
                        if len(loadedMap) != 0:
                            unloadedObjects.append(loadedMap.pop(0))

            for i in range(len(keysPressed)):
                if keysPressed[i]:
                    if len(loadedLaneObjects[i]) != 0:
                        obj = loadedLaneObjects[i][0]
                        if len(obj) == 5:
                            try:
                                unObj = unloadedObjects[unloadedObjects.index(loadedLaneObjects[i][0])]
                            except ValueError: # ultra rare error
                                pass
                            unObj[3] = True
                            unObj[4] = abs(obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame))
                        else:
                            hitDifference = abs(obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame))
                            if hitDifference > config["hitwindow"][0]:
                                hit = "miss"
                                combo = 0
                            elif hitDifference > config["hitwindow"][1]:
                                curScore +=  50+(50*(combo)/25)
                                hit = "bad"
                                combo += 1
                            elif hitDifference > config["hitwindow"][2]:
                                curScore += 100+(100*(combo)/25)
                                hit = "good"
                                combo += 1
                            else:
                                curScore += 300+(300*(combo)/25)
                                hit = "perfect"
                                combo += 1
                            hitCount[hit] += 1

                            if obj in unloadedObjects:
                                unloadedObjects.remove(obj)
                                if len(loadedMap) != 0:
                                    unloadedObjects.append(loadedMap.pop(0))
            
            for i in range(len(keysReleased)):
                if keysReleased[i]:
                    if len(loadedLaneObjects[i]) != 0:
                        obj = loadedLaneObjects[i][0]

                        if len(obj) == 5 and obj[3]:
                            hitDifference = max(obj[4], abs(obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)))
                            if hitDifference > config["hitwindow"][0]:
                                hit = "miss"
                                combo = 0
                            elif hitDifference > config["hitwindow"][1]:
                                curScore += 50+(50*(combo)/25) 
                                hit = "bad"
                                combo += 1
                            elif hitDifference > config["hitwindow"][2]:
                                curScore += 100+(100*(combo)/25)
                                hit = "good"
                                combo += 1
                            else:
                                curScore += 300+(300*(combo)/25)
                                hit = "perfect"
                                combo += 1
                            hitCount[hit] += 1
                            if obj in unloadedObjects:
                                unloadedObjects.remove(obj)
                                if len(loadedMap) != 0:
                                    unloadedObjects.append(loadedMap.pop(0))

            
            if hit != "" and config["interface"]["gameplay"]["judgement"]["state"].lower()=="true":
                hitWidth = 0.39*35*len(hit)
                if hit=="miss":
                    hitColor = config["hitColors"][0]
                elif hit=="bad":
                    hitColor = config["hitColors"][1]
                elif hit=="good":
                    hitColor = config["hitColors"][2]
                elif hit=="perfect":
                    hitColor = config["hitColors"][3]
                screen.blit(fontBold.render(hit, True, hitColor), ((config["resolution"][0]/2) - hitWidth / 2, config["resolution"][1]-280))
            loadedObjects = unloadedObjects
        
        if isPlaying and playingFrame + 2000 + config["audioOffset"] < pygame.time.get_ticks():
            pygame.mixer.music.unpause()

        if maxCombo<combo: maxCombo = combo

        if isPlaying==True:
            if config["interface"]["gameplay"]["judgementCounter"]["state"].lower()=="true":
                screen.blit(fontBold.render("Perfect: ", True, config["hitColors"][3]), (config["resolution"][0]-180, config["resolution"][1]-295))
                screen.blit(fontBold.render("Good: ", True, config["hitColors"][2]), (config["resolution"][0]-157, config["resolution"][1]-270))
                screen.blit(fontBold.render("Bad: ", True, config["hitColors"][1]), (config["resolution"][0]-140, config["resolution"][1]-245))
                screen.blit(fontBold.render("Miss: ", True, config["hitColors"][0]), (config["resolution"][0]-149, config["resolution"][1]-220))
                screen.blit(font.render(f"{padding(hitCount['perfect'], 4)}", True, tuple(config["interface"]["gameplay"]["judgementCounter"]["textColor"])), (config["resolution"][0]-80, config["resolution"][1]-295))
                screen.blit(font.render(f"{padding(hitCount['good'], 4)}", True, tuple(config["interface"]["gameplay"]["judgementCounter"]["textColor"])), (config["resolution"][0]-80, config["resolution"][1]-270))
                screen.blit(font.render(f"{padding(hitCount['bad'], 4)}", True, tuple(config["interface"]["gameplay"]["judgementCounter"]["textColor"])), (config["resolution"][0]-80, config["resolution"][1]-245))
                screen.blit(font.render(f"{padding(hitCount['miss'], 4)}", True, tuple(config["interface"]["gameplay"]["judgementCounter"]["textColor"])), (config["resolution"][0]-80, config["resolution"][1]-220))
            
            if config["interface"]["gameplay"]["score"]["state"].lower()=="true": screen.blit(fontScore.render(padding(curScore, 8), True, tuple(config["interface"]["gameplay"]["score"]["color"])), (config["resolution"][0]-265, 0))
            
            if config["interface"]["gameplay"]["combo"]["state"].lower()=="true": screen.blit(fontScore.render(str(combo)+"x", True, tuple(config["interface"]["gameplay"]["accuracy"]["color"])), (0,config["resolution"][1]-85))
            
            if config["interface"]["gameplay"]["songName"]["state"].lower()=="true": screen.blit(font.render(maps[selectedMapIndex], True, tuple(config["interface"]["gameplay"]["songName"]["color"])), (0,0))
            
            totalObjects = hitCount['miss']+hitCount['bad']+hitCount['good']+hitCount['perfect']
            if totalObjects!=0:
                accuracy = int(100*((50*hitCount['bad'])+(100*hitCount['good'])+(300*(hitCount['perfect']+totalObjects)) )/( 300*(hitCount['bad']+hitCount['good']+hitCount['perfect']+hitCount["miss"]+totalObjects)))
            else:
                accuracy = "100"
            if config["interface"]["gameplay"]["accuracy"]["state"].lower()=="true": screen.blit(fontScore.render(str(accuracy)+"%", True, tuple(config["interface"]["gameplay"]["accuracy"]["color"])), (0, 20))
            
            if config["interface"]["gameplay"]["mods"]["state"].lower()=="true":
                mods = []
                length = 0
                for i in config["mods"]:
                    if config["mods"][i].lower()=="true":
                        mods.append(i)
                        length = length+len(i)
                if mods!=[]: screen.blit(font.render("Mods: " + ' '.join(mods), True, tuple(config["interface"]["gameplay"]["mods"]["color"])), (config["resolution"][0]-(length*25), 60))
                
            if config["interface"]["gameplay"]["hitOverlay"]["state"].lower()=="true":
                for i in range(len(keysDown)):
                    if keysDown[i]==True:
                        overlayBorder = 25
                    else:
                        overlayBorder = 2
                    pygame.draw.rect(screen, config["colors"][i], (config["resolution"][0]-20,config["resolution"][1]-25-i*25,20,20), overlayBorder)

        else:
            #screen.blit(fontBold.render(title, True, tuple(config["interface"]["title"]["color"])), (0,0))
            screen.blit(fontBold.render("Maps:", True, tuple(config["interface"]["mapSelection"]["mapsHeader"]["color"])), (0,0))
            pygame.draw.rect(screen, tuple(config["interface"]["mapSelection"]["mapsLine"]["color"]), pygame.Rect(0, 43, 15, 29))
            if searchtext!="":
                screen.blit(fontBold.render("Search: "+searchtext, True, tuple(config["interface"]["mapSelection"]["search"]["color"])), (0,20))
            rendermaps = maps[selectedMapIndex:selectedMapIndex+(config["resolution"][1]-75)//25]
            for i in range(len(rendermaps)):
                screen.blit(font.render(rendermaps[i], True, tuple(config["interface"]["mapSelection"]["maps"]["color"])), (30, 45 + i * 25))

        pygame.display.flip()

while(1):
    if __name__ == "__main__":
        exitcode = mmLoop()
        if exitcode==0 or exitcode=="EXIT": break
        elif exitcode=="ABOUT":
            exitcode = aboutLoop()
            if exitcode==0: break
        elif exitcode=="GAME":
            exitcode = gameLoop()
            if exitcode==0: break
pygame.quit()
sys.exit(0)
