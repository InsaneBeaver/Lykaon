#!usr/bin/env/python

import irclib, ircbot, TimeManager
irclib.DEBUG = True
from Werewolf import Game
from Werewolf import BaseClass
from threading import Thread
import traceback, sys, re
import Commands
from Tools import GameContainer
import Tools.config as config

if sys.version_info[0] == 3:
    import imp
    reload = imp.reload # I know, it's retarded, live with it.


# Dirty stuff, currently only supported by freenode.
csaccesslistsyntax = "\d (\S*) \+(\w*) \[.*]"
csaccesslistendsyntax = "End of #.* FLAGS listing. "

class Lykaon(ircbot.SingleServerIRCBot):

    Games = {} 

    def __init__(self):
        ircbot.SingleServerIRCBot.__init__(self, [(config.SERVER, 6667)],
                                           config.NICK,
                                           config.REALNAME)

        self.accesslisttracker = {"name":"", "flaglist":[], "function":None}
        self.nick = config.NICK # Yes, yes :^)
        if not "freenode" in config.SERVER:
            self.accesslisttracker = None
            sys.stdout.write("Warning: The chosen server isn't freenode. Thus, the bot won't be able to use /cs access chan LIST to list bot admins. ")

        print "LE: moo"
        try:
          self.start()
          
        except KeyboardInterrupt:
          self.connection.quit("Ctrl-C at console")
          
          
        except Exception, e:
          traceback.print_exc()
          self.connection.quit("%s: %s" % (e.__class__.__name__, e.args))
          raise

        except:
            traceback.print_exc()


        

    def on_welcome(self, serv, event):
        self.serv = serv
        serv.privmsg("nickserv", "identify incredible moo")
        self.alleventshandler = self.alleventshandler
        self.CommandClass = Commands.CommandClass(self.channels, serv)
        self.GameContainer = GameContainer.GameContainer(self.channels, serv)
        serv.TimeManager = TimeManager.TimeManager(serv, self.GameContainer)
        for chan in config.CHANS:
            serv.join(chan)

    def on_join(self, serv, event):
        
        chan = event.target()
        authorname = event.source().split('!')[0]
        if authorname == self.nick:
            self.GameContainer.createlobby(chan)
            return

        # TODO: Voice the player if Game

    def find_game(self, user):
        chan = self.GameContainer.find_game(user)
        if not chan:
            return
        
        namespace = self.GameContainer[chan]
        if not namespace:
            return
        
        if namespace.__class__ == GameContainer.Lobby:
            return # Nein

        return namespace
                
    def on_privmsg(self, serv, event):
        self.on_pubmsg(serv, event) # A bit hacky, but meh.

##    def on_privnotice(self, serv, event):
##        if event.source().split('!')[0] == "ChanServ":
##            msg = event.arguments()[0]
##            if re.match(csaccesslistsyntax, msg):
##
##                self.accesslisttracker["flaglist"].append(re.findall(csaccesslistsyntax, msg)[0])
##
##            elif re.match(csaccesslistendsyntax, msg):
##                self.accesslisttracker["function"](self.accesslisttracker)
##
    def call_handler(self, instance, event):
        # Used in alleventshandler
        for obj in dir(instance):
            if obj.startswith("on_"+event.eventtype()):
                if type(getattr(instance, obj)) != type(self.alleventshandler):
                    continue # Who knows ._____.
                
                try:
                    getattr(instance, obj)(event)

                except:
                    self.exception_handler(self.serv, event, sys.exc_info()[1])
                    

    def alleventshandler(self, event):
        # Sees if a player has an handler for datt
        for GameObj in self.GameContainer:
            if GameObj.channame == event.target():
                self.call_hander(GameObj, event)
            
        ply = event.source().split('!')[0]

        game = self.find_game(ply)
        if not game: return
        
        plyclass = game.PlayerList[ply]
        self.call_handler(plyclass, event)
                    
                
        
    def exception_handler(self, serv, event, exc):
        # Very weird class.
        # Re-raises the exception to catch it in the proper way
        # Probably terribly retarded, live with it.

        result = ""
        user = event.source().split('!')[0]

        try:
            raise exc[1]
        
        except Game.WerewolfException:
            result = str(sys.exc_info()[1])

        except:
            result = "Oops! Exception logged in console.  Please report this. "
            traceback.print_exc() 

        if event.eventtype() == "pubmsg":
            serv.privmsg(event.target(), user+': '+result)

        else:
            serv.notice(user, result)
        
    
    def on_pubmsg(self, serv, event):
        try:
            target = event.target()
            user = event.source().split('!')[0]
            if target[0] != "#":
                # Le query
                chan = self.find_game(user)
                if not chan:
                    return
                target = self.nick
                namespace = chan.PlayerList[user]
                
            else:
                namespace = self.GameContainer[target] # Must work
                if not user in namespace.players and namespace.__class__ == GameContainer.Game:
                    return

        
            text = event.arguments()[0]
            if text[0] == config.COMMANDCHAR:
                self.CommandClass.call_func(target, event.source(), namespace, text[1:])



        except:
            print(sys.exc_info())
            self.exception_handler(serv, event, sys.exc_info())
            traceback.print_exc()

    def on_nick(self, serv, event):
        lastnick = event.source().split('!')[0]
        newnick = event.target()

        if lastnick == self.nick:
            self.nick = newnick
            return

        chan = self.GameContainer.find_game(lastnick)
        if not chan:
            return # Nothing to change

        klass = self.GameContainer.container[chan]
        if klass.__class__.__name__ == "Lobby":
            klass.players.remove(lastnick)
            klass.players.append(newnick)

        else:
            klass.PlayerList[lastnick].name = newnick
        

#Lykaon = Lykaon()



sample = "%s!foo@bar"

def test():
    global Lykaon
    serv = Commands.FakeServ()
    Lykaon.start = lambda *args, **kw: None
    Lykaon = Lykaon()
    Lykaon.on_welcome(serv, None)
    event0 = irclib.Event("asdf", sample%"Lykaon", target="#asdf")
    Lykaon.on_join(serv, event0)

    
    
    


test()


while 1:
    try:
        data = raw_input("Enter da tingz: ").split(' ')
        source = data[0]
        target = data[1]
        arg = " ".join(data[2:])

        if target[0] != "#":
            target = sample%target
        
        Lykaon.on_pubmsg(Lykaon.serv, irclib.Event(None,
                                             sample%source,
                                             target,
                                             [arg]))

    except KeyboardInterrupt:
        while 1:
            try:
                exec raw_input('>> ')

            except:
                traceback.print_exc()

    except:
        traceback.print_exc()

