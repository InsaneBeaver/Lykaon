import Werewolf.Game
from Werewolf.Game import Game
from Werewolf.Lobby import Lobby

import json # :Oooo


userdict = json.loads(open("Config/UserDict.txt").read())

    


class GameContainer:
    # Contains all the games objects (Lobby/Game)
    stasisdicts = {}
    quiets = {}

    def __init__(self, channels, serv):
        self.channels, self.serv = channels, serv
        self.container = {}
        self.modebank = {}

    def __iter__(self):
        return iter(self.container.values())
        
    def __getitem__(self, item):
        return self.container[item]

    
        
    def find_game(self, ply):
        # Will browse in all the games to find the one in which ply is participating :oooo

        for chan in self.container.keys():
            print self.container[chan].players
            if ply in self.container[chan].players:
                return chan

        return None

    def save_config(self):
        open("Config/UserDict.txt", "w").write(json.dumps(userdict))

    def createlobby(self, chan):
        self.create_config(chan)
        if chan in self.quiets.keys():
            tounquietlist = []
            # Mass unquiets
            for user in self.quiets[chan]:
                tounquietlist.append(user)

                if len(tounquietlist) == 5:
                    self.serv.mode(chan, "-qqqqq "+" ".join(tounquietlist))
                    tounquietlist = []

            # Unquiet what's left
            self.serv.mode(chan, "-q"*len(tounquietlist)+' '+' '.join(tounquietlist))
            
        self.container[chan] = Lobby(self.channels,
                                     self.serv,
                                     chan,
                                     self.start_game,
                                     userdict[chan],
                                     self.container)

    def kill(self, chan, target):
        for user in self.channels[chan].voiced():
            if user.startswith(target):
                break

        user = user.split('!')[1].split('@')[1]
            
        self.quiets[chan].append(user)
        self.serv.mode(chan, "-v+q "+target+' '+target)

    def create_config(self, chan):
        if chan in userdict.keys():
            return # Nothing to do here

        userdict[chan] = {"stasisdict": {} , "adminlist": []}

    def stopgame(self, chan):
        for ply in self.modebank[chan]:
            self.serv.mode(chan, "-q "+target)

        self.serv.mode(chan, "-m")

    def start_game(self, chan):
        self.quiets[chan] = []
        plylist = self.container[chan].players
        del self.container[chan]
        self.serv.privmsg(chan, Werewolf.Game.msgs["GAMESTARTMSG"].format(", ".join(plylist)))
        self.serv.mode(chan, "+m")
        self.container[chan] = Game(plylist,
                                    self.serv,
                                    self.createlobby,
                                    lambda target: self.kill(chan, target),
                                    chan)


        
        
