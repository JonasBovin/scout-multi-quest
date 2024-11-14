import time
import sys
import pyttsx3
import json
import datetime
import os
from expiring_dict import ExpiringDict

def main():
    minTime = 120
    cards = {'0005269927': 1,
        '0005264120': 2,
        '0005253090': 3,
        '0005322773': 4,
        '0005275274': 5
    }
    teams = {'1': 'Frodo',
             '2': 'Gandalf',
             '3': 'Legolas',
             '4': 'Gimli',
             '5': 'Samwise'
        }
    dict_ttl = ExpiringDict(minTime)
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    #change_voice(engine, "en_US", "VoiceGenderFemale")
    rate = engine.getProperty('rate')   # getting details of current speaking rate
    print (rate)                        #printing current voice rate
    #engine.setProperty('rate', 150)     # setting up new voice rate
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path +'/../db/quests.json', 'r') as openfile:
        # Reading from json file
        posts = json.load(openfile)
    for item in posts: 
        print(item["id"], item["name"])
    log = []
    
    while True:
        for line in sys.stdin:
            card_id = line.strip()
            if card_id:
                if cards[card_id]:
                    teamNo = cards[card_id]
                    if str(teamNo) in dict_ttl:
                        engine.say('Please go to ' + dict_ttl[str(teamNo)])
                        engine.runAndWait()
                    else:    
                        print('Welcome team ' + teams[str(teamNo)])
                        engine.say('Welcome team ' + teams[str(teamNo)] )
                        engine.runAndWait()
                        next = findBestPost(log, posts, teamNo)
                        
                        if not next:
                            engine.say('Return to checkin team ' + teams[str(teamNo)])
                            engine.runAndWait()
                        else:
                            #println next
                            logEntry(log, next["id"], teamNo)
                            dict_ttl[str(teamNo)] = next["name"]
                            engine.say('Please go to ' + next["name"])
                            engine.runAndWait()
        
    engine.stop()

def change_voice(engine, language, gender='VoiceGenderFemale'):
    for voice in engine.getProperty('voices'):
        if language in voice.languages and gender == voice.gender:
            engine.setProperty('voice', voice.id)
            return True

    raise RuntimeError("Language '{}' for gender '{}' not found".format(language, gender))

def findBestPost(log, posts, teamNo):
    if not log:
        logEntry(log, posts[0]["id"], teamNo)
        return posts[0]
    busyPosts = dict()
    completedPosts = []
    uncompletedPost = None
    for entry in log:
        if entry["teamNo"] == teamNo:
            if "endTime" in entry:
                completedPosts.append(entry["postId"])
            else:
                uncompletedPost = entry["postId"]
        if not "endTime" in entry:
           if not entry["postId"] in busyPosts:
                busyPosts[entry["postId"]] = 1
           else:
                busyPosts[entry["postId"]] = busyPosts[entry["postId"]] + 1
    candidate = None
    candidateCount = 100
    for post in posts:
        if post["id"] not in completedPosts:
            if post["id"] not in busyPosts:
                candidateCount = 0
                candidate = post
            else:
                if candidateCount > busyPosts[post["id"]]:
                    candidateCount = busyPosts[post["id"]]
                    candidate = post
                
    if uncompletedPost:
        logEntry(log, uncompletedPost, teamNo)
    if candidate == None:
        return
    if uncompletedPost == candidate["id"]:
        return
    return candidate
                    
def logEntry(log, postId, teamNo):
    entry = findLog(log, postId, teamNo)
    if not entry:
        entry = {"startTime": datetime.datetime.now().timestamp(), "postId": postId, "teamNo": teamNo, "event": "start"}
        log.append(entry)
    else:
        entry["endTime"] = datetime.datetime.now().timestamp()
        
def findLog(log, postId, teamNo):
    for entry in log:
        if entry["postId"] == postId and entry["teamNo"] == teamNo:
            return entry
    return
    
if __name__ == "__main__":
    main()
 
    