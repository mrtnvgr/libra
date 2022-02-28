#!/bin/python3
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, math, os, sys, copy, json, zipfile
from natsort import natsorted

config = json.load(open("config.json"))

title = "Libra 2022.0228"

pygame.display.set_caption(title)
pygame.font.init()
pygame.mixer.init(44100)

size = (1200, 900)
screen = pygame.display.set_mode(size)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

font = pygame.font.SysFont('Arial', 25)
fontBold = pygame.font.SysFont('Arial', 25, bold=True)
fontScore = pygame.font.SysFont('Arial', 60)

def padding(score, max):
    ret = str(math.floor(score))
    ret = "0" * (max - len(ret)) + ret
    return ret

def parseMap(map):
    if os.path.exists("maps/"+map+"/map.osu")==True:
        mapdata = open("maps/"+map+"/map.osu", "r", encoding="utf-8").read().split("\n")
        type = "osu"
    mapdata = [value for value in mapdata if value]
    hitObjects = False
    converted = []
    for mapline in mapdata:
        if type=="osu":
            if hitObjects==True:
                splitted = mapline.split(",")
                if splitted[5].split(":")[0]=="0":
                    converted.append([int(splitted[2]), int((int(splitted[0])*4)/512)])
                else:
                    converted.append([int(splitted[2]), int((int(splitted[0])*4)/512), int(splitted[5].split(":")[0]), False, 0])
            else:
                if mapline=="[HitObjects]":
                    hitObjects = True
    return converted

def main():
    maps = []
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
    curScore = 0.0
    hitCount = {
        'perfect': 0,
        'good': 0,
        'bad': 0,
        'miss': 0
    }
    hit = ""
    hitMarker = 0
    files = os.listdir('maps/')
    for dir in files:
        if ".osz" in dir:
            oszfile = zipfile.ZipFile(os.path.join('maps/', dir))
            for diff in oszfile.namelist():
                if ".osu" in diff:
                    oszfile.extract(diff, "maps/"+diff[:-4])
                    try:
                        os.rename("maps/"+diff[:-4]+"/"+diff, "maps/"+diff[:-4]+"/map.osu")
                    except FileExistsError: # windows fix bruh
                        pass
                    osufile = open("maps/"+diff[:-4]+"/map.osu", encoding="utf-8").read().split("\n")
                    for osuline in osufile:
                        if "AudioFilename" in osuline:
                            audiofile = osuline.replace("AudioFilename:", "")
                            if audiofile[0]==" ": audiofile = audiofile[1:]
                            oszfile.extract(audiofile, "maps/"+diff[:-4]+"/")
            os.remove(os.path.join('maps/', dir))
    files = os.listdir('maps/')
    for dir in files:
        if os.path.isdir(os.path.join('maps/', dir)):
            maps.append(dir)
    maps = natsorted(maps) 
    while True:
        screen.fill(BLACK)
        
        for i in range(len(keysPressed)):
            keysPressed[i] = False
            keysReleased[i] = False
        
        if selectingMaps!="":
            if selectingMapsCooldown==10:
                if selectingMaps=="down":
                    selectedMapIndex += 1
                elif selectingMaps=="up":
                    selectedMapIndex -= 1
                if selectedMapIndex==-1:
                    selectedMapIndex = len(maps) - 1
                elif selectedMapIndex==len(maps):
                    selectedMapIndex = 0
                selectingMapsCooldown = 0
            else:
                selectingMapsCooldown+=1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    if isPlaying:
                        isPlaying = False
                        pygame.mixer.music.stop()
                        combo = 0
                    else:
                        pygame.quit()
                        sys.exit(0)
                if event.key == pygame.K_DOWN and not isPlaying:
                    selectingMaps = "down"
                elif event.key == pygame.K_UP and not isPlaying:
                    selectingMaps = "up"
                elif event.key == pygame.K_RETURN and not isPlaying:
                    if os.path.exists("maps/"+maps[selectedMapIndex]+"/map.osu"):
                        for line in open("maps/"+maps[selectedMapIndex]+"/map.osu", encoding="utf-8").read().split("\n"):
                            if "AudioFilename" in line:
                                songfile = line.replace("AudioFilename:", "")
                                if songfile[0]==" ": songfile = songfile[1:]
                    pygame.mixer.music.load("maps/"+maps[selectedMapIndex]+"/"+songfile)
                    pygame.mixer.music.play()
                    pygame.mixer.music.pause()
 
                    loadedMap = parseMap(maps[selectedMapIndex])
                    curScore = 0.0
                    hitCount = dict.fromkeys(hitCount, 0)
                    keysDown = [False, False, False, False]
                    keysPressed = [False, False, False, False]
                    keysReleased = [False, False, False, False]
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
                if (event.key==pygame.K_DOWN or event.key==pygame.K_UP) and not isPlaying:
                    selectingMaps = ""
                for i in range(len(config["keybinds"])):
                    if event.key == eval(f'pygame.K_{config["keybinds"][i]}') and isPlaying:
                        keysDown[i] = False
                        keysReleased[i] = True
        
        for i in range(len(keysDown)):
            if isPlaying:
                if keysDown[i]:
                    pygame.draw.circle(screen, config["colors"][i], (390 + i * 140, 800), 60, 5)
                    pygame.draw.circle(screen, config["colors"][i], (390 + i * 140, 800), 60) 
                else:
                    pygame.draw.circle(screen, WHITE, (390 + i * 140, 800), 60, 5)
        if isPlaying and playingFrame + 1000 < pygame.time.get_ticks():
            if len(loadedObjects) == 0:
                isPlaying = False
                combo = 0
                pygame.mixer.music.stop()
            unloadedObjects = copy.deepcopy(loadedObjects)
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
                        pygame.draw.circle(screen, config["colors"][obj[1]], (390 + obj[1] * 140, 800 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["ar"]), 60 )
                    pygame.draw.circle(screen, config["colors"][obj[1]], (390 + obj[1] * 140, 800 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["ar"]), 60 )
                    rect1 = 330 + obj[1] * 140
                    rect2 = 800 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["ar"]
                    rect3 = 120
                    if not obj[3]:
                        rect4 = (800 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["ar"]) - rect2
                    else:
                        rect4 = (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["ar"]
                    pygame.draw.rect(screen, config["colors"][obj[1]], pygame.Rect(rect1, rect2, rect3, rect4))
                    
                    if 800 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["ar"] > 960:
                        hit = "miss"
                        hitMarker = pygame.time.get_ticks()
                        hitCount[hit] += 1
                        unloadedObjects.remove(obj)
                        if len(loadedMap) != 0:
                            unloadedObjects.append(loadedMap.pop(0))
                else:
                    pygame.draw.circle(screen, tuple(config["colors"][obj[1]]), (390 + obj[1] * 140, 800 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["ar"]), 60 )

                    # if the circle passes the visible point
                    if 800 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config["ar"] > 960:
                        hit = "miss"
                        hitMarker = pygame.time.get_ticks()
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
                            hitMarker = pygame.time.get_ticks()
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
                            hitMarker = pygame.time.get_ticks()
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

            
            if hit != "":
                hitWidth = 0.39*35*len(hit)
                if hit=="miss":
                    hitColor = copy.deepcopy(config["hitColors"][0])
                elif hit=="bad":
                    hitColor = copy.deepcopy(config["hitColors"][1])
                elif hit=="good":
                    hitColor = copy.deepcopy(config["hitColors"][2])
                elif hit=="perfect":
                    hitColor = copy.deepcopy(config["hitColors"][3])
                for i in range(len(hitColor)):
                    hitColor[i] = max(min(hitColor[i] * (1 - ((pygame.time.get_ticks() - hitMarker) / config["hitFadeTime"])), 255), 0)
                screen.blit(fontBold.render(hit, True, hitColor), (580 - hitWidth / 2, 640))
            loadedObjects = unloadedObjects

        if isPlaying and playingFrame + 2000 + config["noteOffset"] < pygame.time.get_ticks():
            pygame.mixer.music.unpause()
        
        if isPlaying==True:
            screen.blit(fontBold.render("Perfect: ", True, config["hitColors"][3]), (950, 625))
            screen.blit(fontBold.render("Good: ", True, config["hitColors"][2]), (973, 650))
            screen.blit(fontBold.render("Bad: ", True, config["hitColors"][1]), (990, 675))
            screen.blit(fontBold.render("Miss: ", True, config["hitColors"][0]), (981, 700))
            screen.blit(font.render(f"{padding(hitCount['perfect'], 4)}", True, WHITE), (1050, 625))
            screen.blit(font.render(f"{padding(hitCount['good'], 4)}", True, WHITE), (1050, 650))
            screen.blit(font.render(f"{padding(hitCount['bad'], 4)}", True, WHITE), (1050, 675))
            screen.blit(font.render(f"{padding(hitCount['miss'], 4)}", True, WHITE), (1050, 700))
            screen.blit(font.render('Score', True, WHITE), (920, 850))
            screen.blit(fontScore.render(padding(curScore, 7), True, WHITE), (920, 800))
            screen.blit(fontScore.render(str(combo), True, WHITE), (0,800))
            screen.blit(font.render('Combo', True, WHITE), (0, 850))
            screen.blit(font.render(maps[selectedMapIndex], True, WHITE), (0,0))
            totalObjects = hitCount['miss']+hitCount['bad']+hitCount['good']+hitCount['perfect']
            if totalObjects!=0:
                accuracy = int(100*((50*hitCount['bad'])+(100*hitCount['good'])+(300*(hitCount['perfect']+totalObjects)) )/( 300*(hitCount['bad']+hitCount['good']+hitCount['perfect']+hitCount["miss"]+totalObjects)))
            else:
                accuracy = "100"
            screen.blit(fontScore.render(str(accuracy)+"%", True, WHITE), (0, 30))
            screen.blit(font.render("Accuracy", True, WHITE), (0, 80))
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
