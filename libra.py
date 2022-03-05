#!/bin/python3
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, math, os, sys, requests, shutil, datetime, json, zipfile
from natsort import natsorted
from random import randint

GIT_API_URL = "https://api.github.com/repos/mrtnvgr/libra/releases/latest"
GIT_RELEASE_URL = "https://github.com/mrtnvgr/libra/releases/latest/download/libra"
version = "2022.0305-3"
title = "Libra " + version

def configReload():
    while True:
        try:
            config = json.load(open("config.json"))
            break
        except FileNotFoundError:
            print("Config does not exist. Writing default")
            data = """{
    "resolution": [1920,1080],
    "fullscreen": "false",
	"keybinds": [
        "q",
        "w",
        "LEFTBRACKET",
        "RIGHTBRACKET"
    ],
    "circleSpeed": 1.9,
    "circleSize": 1.1,
    "audioOffset": 0,
    "fps": 360,
    "mods": {
        "suddenDeath": "false",
        "hardrock": "false",
        "mirror": "false"
    },
    "scores": "true",
	"interface": {
		"gameplay": {
			"songName": {
				"state": "true"
			},
			"accuracy": {
				"state": "true"
			},
			"combo": {
				"state": "true"
			},
			"judgement": {
				"state": "true"
			},
			"judgementCounter": {
				"state": "true"
			},
			"hitOverlay": {
				"state": "true"
			},
			"score": {
				"state": "true"
			},
			"mods": {
				"state": "true"
			}
		}
	},
    "backgrounds": {
        "userBackgrounds": {
			"mapSelection": {
				"file": ""
			},
			"gameplay": {
				"file": ""
			}
        },
		"mapBackground": {
			"state": "true",
			"brightness": 80
		}
    },
	"hitwindow": [
        135,
        90,
        22
    ],
    "hitColors": [
        [255,0,0],
        [255,0,255],
        [100,255,100],
        [255,255,0]
    ],
    "colors": [
        [171,171,171],
        [3,116,170],
        [3,116,170],
        [171,171,171]
    ],
    "autoUpdate": "true"
}"""
            open("config.json", "w").write(data)
            continue
    if config["mods"]["hardrock"].lower()=="true":
        for i in range(len(config["hitwindow"])): config["hitwindow"][i] = config["hitwindow"][i]//1.5
    return config
config = configReload()

pygame.display.set_caption(title)
pygame.font.init()
pygame.mixer.init()

flags = 0
if config["fullscreen"].lower()=="true":
    flags = flags | pygame.FULLSCREEN
screen = pygame.display.set_mode(tuple(config["resolution"]), flags)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

font = pygame.font.SysFont('Arial', 25)
fontBold = pygame.font.SysFont('Arial', 25, bold=True)
fontScore = pygame.font.SysFont('Arial', 60)

# check updates
if config["autoUpdate"].lower()=="true":
    try:
        remote_version = requests.get(GIT_API_URL).json()["name"]
    except:
        print("No internet connection!")
        remote_version = version
    if remote_version!=version:
        screen.blit(fontBold.render(title, True, WHITE), (0,0))
        screen.blit(fontBold.render("Updating...", True, WHITE), (0,20))
        pygame.display.flip()
        if os.name=="nt":
            os_prefix = ".exe"
        else:
            os_prefix = ""
        open("libra("+remote_version+")"+os_prefix, "wb").write(requests.get(GIT_RELEASE_URL+os_prefix, stream=True).content)
        sys.exit(0)

def padding(score, max):
    ret = str(math.floor(score))
    return "0" * (max - len(ret)) + ret

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
            if config["backgrounds"]["mapBackground"]["state"].lower()=="true":
                if "png" in mapline or "jpg" in mapline or "jpeg" in mapline:
                    backgroundfile = mapline.split('"')[1]
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
    return natsorted(maps)

def importMaps():
    files = os.listdir('maps/')
    for dir in files:
            if ".osz" in dir:
                screen.blit(fontBold.render(title, True, WHITE), (0,0))
                screen.blit(fontBold.render("Unzipping...", True, WHITE), (0,20))
                pygame.display.flip()
                oszfile = zipfile.ZipFile(os.path.join('maps/', dir))
                for diff in oszfile.namelist():
                    if ".osu" in diff:
                        oszfile.extract(diff, "maps/"+diff[:-4])
                        try:
                            os.rename("maps/"+diff[:-4]+"/"+diff, "maps/"+diff[:-4]+"/map.osu")
                        except FileExistsError:
                            pass
                        osufile = open("maps/"+diff[:-4]+"/map.osu", encoding="utf-8").read().split("\n")
                        for osuline in osufile:
                            if "AudioFilename" in osuline:
                                audiofile = osuline.replace("AudioFilename:", "")
                                if audiofile[0]==" ": audiofile = audiofile[1:]
                                oszfile.extract(audiofile, "maps/"+diff[:-4]+"/")
                            elif "jpg" in osuline or "png" in osuline or "jpeg" in osuline:
                                oszfile.extract(osuline.split(",")[2].replace('"', ""), "maps/"+diff[:-4]+"/")
                oszfile.close()
                os.remove(os.path.join('maps/', dir))

def saveScore(name, curScore, hitCount, accuracy, maxCombo, config):
    mods = []
    for i in config["mods"]:
        if config["mods"][i].lower()=="true":
            mods.append(i)
    if mods==[]: mods = ""
    time = datetime.datetime.today().strftime('%Y-%m-%d(%H:%M)')
    data = f"""{name}
{time}
Mods: {' '.join(mods)}
Perfect: {hitCount['perfect']} 
Good: {hitCount['good']}
Bad: {hitCount['bad']}
Miss: {hitCount['miss']}
Accuracy: {accuracy}
Combo: {maxCombo}
Score: {padding(curScore, 7)}"""
    try:
        os.listdir('scores')
    except FileNotFoundError:
        os.mkdir("scores")
    open("scores/"+name+f" ({time}).scr", "w").write(data)

def main():
    loadedMap = []
    loadedObjects = []
    selectedMapIndex = 0
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
    try:
        os.listdir('maps/')
    except FileNotFoundError:
        os.mkdir('maps')
    importMaps()
    maps = reloadMaps()
    config = configReload()
    background = ""
    if config["backgrounds"]["userBackgrounds"]["mapSelection"]["file"]!="":
        mapSelectionBg = pygame.image.load(config["backgrounds"]["userBackgrounds"]["mapSelection"]['file']).convert()
    if config["backgrounds"]["userBackgrounds"]["gameplay"]["file"]!="":
        gameplayBg = pygame.image.load(config["backgrounds"]["userBackgrounds"]["gameplay"]["file"]).convert()
    while True:
        screen.fill(BLACK)
        if config["backgrounds"]["userBackgrounds"]["mapSelection"]["file"]!="" and isPlaying==False:
            screen.blit(mapSelectionBg, mapSelectionBg.get_rect())
        elif config["backgrounds"]["userBackgrounds"]["gameplay"]["file"]!="" and isPlaying:
            screen.blit(gameplayBg, gameplayBg.get_rect())
        if config["backgrounds"]["mapBackground"]["state"]=="true" and background!="" and isPlaying:
            screen.blit(backgroundBg, backgroundBg.get_rect())
        for i in range(len(keysPressed)):
            keysPressed[i] = False
            keysReleased[i] = False
        if selectedMapIndex<0:
            selectedMapIndex = len(maps)-1
        elif selectedMapIndex==len(maps):
            selectedMapIndex = 0
        if selectingMaps!="":
            if selectingMapsCooldown==(config["fps"]//12):
                if selectingMaps=="down":
                    selectedMapIndex += 1
                elif selectingMaps=="up":
                    selectedMapIndex -= 1
            else:
                selectingMapsCooldown += 1
        
        if config["mods"]["suddenDeath"].lower()=="true" and hitCount["miss"]>0:
            isPlaying = False
            loadedObjects = []
            keysDown = [False, False, False, False]
            keysPressed = [False, False, False, False]
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
            pygame.mixer.music.stop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    if isPlaying:
                        isPlaying = False
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
                    else:
                        pygame.quit()
                        sys.exit(0)
                if (event.key == pygame.K_DOWN or event.key==pygame.K_s) and not isPlaying:
                    selectedMapIndex += 1
                    selectingMaps = "down"
                elif (event.key == pygame.K_UP or event.key==pygame.K_w) and not isPlaying:
                    selectedMapIndex -= 1
                    selectingMaps = "up"
                elif event.key==pygame.K_DELETE and not isPlaying:
                    shutil.rmtree("maps/"+maps[selectedMapIndex], ignore_errors=True)
                    maps = reloadMaps()
                elif event.key==pygame.K_r:
                    importMaps()
                    maps = reloadMaps()
                    config = configReload()
                elif event.key==pygame.K_F2:
                    selectedMapIndex = randint(0, len(maps))
                elif event.key == pygame.K_RETURN and not isPlaying:
                    if maps==[]: continue 
                    if os.path.exists("maps/"+maps[selectedMapIndex]+"/map.osu"):
                        for line in open("maps/"+maps[selectedMapIndex]+"/map.osu", encoding="utf-8").read().split("\n"):
                            if "AudioFilename" in line:
                                songfile = line.replace("AudioFilename:", "")
                                if songfile[0]==" ": songfile = songfile[1:]
                    pygame.mixer.music.load("maps/"+maps[selectedMapIndex]+"/"+songfile)
                    pygame.mixer.music.play()
                    pygame.mixer.music.pause()
 
                    loadedFile = parseMap(maps[selectedMapIndex], config)
                    if loadedFile[0]==[]: continue
                    loadedMap = loadedFile[0]
                    background = loadedFile[1]
                    if background!="":
                        backgroundBg = pygame.transform.scale(pygame.image.load("maps/"+maps[selectedMapIndex]+"/"+background).convert(), tuple(config["resolution"]))
                        backgroundBg.set_alpha(config["backgrounds"]["mapBackground"]["brightness"])
                    for i in range(20):
                        loadedObjects.append(loadedMap.pop(0))
                    isPlaying = True
                    playingFrame = pygame.time.get_ticks()
                else:
                    for i in range(len(config["keybinds"])):
                        if event.key == eval(f"pygame.K_{config['keybinds'][i]}") and isPlaying:
                            keysDown[i] = True
                            keysPressed[i] = True
                
            elif event.type == pygame.KEYUP:
                if (event.key==pygame.K_DOWN or event.key==pygame.K_UP or event.key==pygame.K_w or event.key==pygame.K_s) and not isPlaying:
                    selectingMapsCooldown = 0
                    selectingMaps = ""
                for i in range(len(config["keybinds"])):
                    if event.key == eval(f'pygame.K_{config["keybinds"][i]}') and isPlaying:
                        keysDown[i] = False
                        keysReleased[i] = True
        
        for i in range(len(keysDown)):
            if isPlaying:
                if keysDown[i]:
                    pygame.draw.circle(screen, config["colors"][i], ((config["resolution"][0]/2)-250 + i * int(140*config["circleSize"]), config["resolution"][1]-100), int(60*config["circleSize"]), 5)
                    pygame.draw.circle(screen, config["colors"][i], ((config["resolution"][0]/2)-250 + i * int(140*config["circleSize"]), config["resolution"][1]-100), int(60*config["circleSize"]))
                else:
                    pygame.draw.circle(screen, WHITE, ((config["resolution"][0]/2)-250 + i * int(140*config["circleSize"]), config["resolution"][1]-100), int(60*config["circleSize"]), 5)
        if isPlaying and playingFrame + 1000 < pygame.time.get_ticks():
            if len(loadedObjects) == 0:
                isPlaying = False
                if config["scores"].lower()=="true":
                    saveScore(maps[selectedMapIndex], curScore, hitCount, accuracy, maxCombo, config)
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
                    if not obj[3]:
                        pygame.draw.circle(screen, config["colors"][obj[1]], ((config["resolution"][0]/2)-250 + obj[1] * int(140*config["circleSize"]),config["resolution"][1]-100 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["circleSpeed"]), int(60*config["circleSize"]) )
                    pygame.draw.circle(screen, config["colors"][obj[1]], ((config["resolution"][0]/2)-250 + obj[1] * int(140*config["circleSize"]),config["resolution"][1]-100 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["circleSpeed"]), int(60*config["circleSize"]) )
                    if int(config["circleSize"])==0: 
                        circleOffset = abs(int(config["circleSize"]*10)-10)*6
                    else:
                        circleOffset = -int(config["circleSize"]%1*60)
                    rect1 = (config["resolution"][0]/2)-310+circleOffset + obj[1] * int(140*config["circleSize"])
                    rect2 = config["resolution"][1]-100 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["circleSpeed"]
                    rect3 = (120*config["circleSize"])
                    if not obj[3]:
                        rect4 = (config["resolution"][1]-100 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["circleSpeed"]) - rect2
                    else:
                        rect4 = (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["circleSpeed"]
                    pygame.draw.rect(screen, config["colors"][obj[1]], pygame.Rect(rect1, rect2, rect3, rect4))
                    
                    if config["resolution"][1]-100 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["circleSpeed"] > config["resolution"][0]-300:
                        hit = "miss"
                        hitCount[hit] += 1
                        unloadedObjects.remove(obj)
                        if len(loadedMap) != 0:
                            unloadedObjects.append(loadedMap.pop(0))
                else:
                    pygame.draw.circle(screen, tuple(config["colors"][obj[1]]), ((config["resolution"][0]/2)-250 + obj[1] * int(140*config["circleSize"]), config["resolution"][1]-100 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["circleSpeed"]), int(60*config["circleSize"]) )

                    # if the circle passes the visible point
                    if config["resolution"][1]-100 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["circleSpeed"] > config["resolution"][0]-300:
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
                            unObj = unloadedObjects[unloadedObjects.index(loadedLaneObjects[i][0])]
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
                screen.blit(fontBold.render(hit, True, hitColor), ((config["resolution"][0]/2)-50 - hitWidth / 2, config["resolution"][1]-280))
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
                screen.blit(font.render(f"{padding(hitCount['perfect'], 4)}", True, WHITE), (config["resolution"][0]-80, config["resolution"][1]-295))
                screen.blit(font.render(f"{padding(hitCount['good'], 4)}", True, WHITE), (config["resolution"][0]-80, config["resolution"][1]-270))
                screen.blit(font.render(f"{padding(hitCount['bad'], 4)}", True, WHITE), (config["resolution"][0]-80, config["resolution"][1]-245))
                screen.blit(font.render(f"{padding(hitCount['miss'], 4)}", True, WHITE), (config["resolution"][0]-80, config["resolution"][1]-220))
            
            if config["interface"]["gameplay"]["score"]["state"].lower()=="true": screen.blit(fontScore.render(padding(curScore, 7), True, WHITE), (config["resolution"][0]-230, 0))
            
            if config["interface"]["gameplay"]["combo"]["state"].lower()=="true": screen.blit(fontScore.render(str(combo)+"x", True, WHITE), (0,config["resolution"][1]-85))
            
            if config["interface"]["gameplay"]["songName"]["state"].lower()=="true": screen.blit(font.render(maps[selectedMapIndex], True, WHITE), (0,0))
            
            totalObjects = hitCount['miss']+hitCount['bad']+hitCount['good']+hitCount['perfect']
            if totalObjects!=0:
                accuracy = int(100*((50*hitCount['bad'])+(100*hitCount['good'])+(300*(hitCount['perfect']+totalObjects)) )/( 300*(hitCount['bad']+hitCount['good']+hitCount['perfect']+hitCount["miss"]+totalObjects)))
            else:
                accuracy = "100"
            if config["interface"]["gameplay"]["accuracy"]["state"].lower()=="true": screen.blit(fontScore.render(str(accuracy)+"%", True, WHITE), (0, 20))
            
            if config["interface"]["gameplay"]["mods"]["state"].lower()=="true":
                mods = []
                length = 0
                for i in config["mods"]:
                    if config["mods"][i].lower()=="true":
                        mods.append(i)
                        length = length+len(i)
                if mods!=[]: screen.blit(font.render("Mods: " + ' '.join(mods), True, WHITE), (config["resolution"][0]-(length*25), 60))
                
            if config["interface"]["gameplay"]["hitOverlay"]["state"].lower()=="true":
                for i in range(len(keysDown)):
                    if keysDown[i]==True:
                        pygame.draw.rect(screen, WHITE, pygame.Rect(config["resolution"][0]-20,config["resolution"][1]-25-i*25,20,20))

        else:
            screen.blit(fontBold.render(title, True, WHITE), (0,0))
            screen.blit(fontBold.render("Maps:", True, WHITE), (0,20))
            pygame.draw.rect(screen, WHITE, pygame.Rect(0, 63, 15, 29))
            for i in range(len(maps[selectedMapIndex:])):
                screen.blit(font.render(maps[selectedMapIndex:][i], False, WHITE), (30, 65 + i * 25))


        pygame.display.flip()
        pygame.time.Clock().tick(config["fps"])

if __name__ == "__main__":
    main()
