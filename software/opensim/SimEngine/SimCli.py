#!/usr/bin/python

import sys
import threading
import logging
import binascii
import time

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class SimCli(threading.Thread):
    '''
    \brief Thread which handles CLI commands entered by the user.
    '''
    
    def __init__(self,engine):
    
        # record variables
        self.engine = engine
        
        # local variables
        self.commands = []
        
        # register commands
        self._registerCommand('boot',
                              'b',
                              'switch a mote on',
                              '<moterank>',
                              self._handleBoot)
        self._registerCommand('debugpins',
                              'dp',
                              'print the current state of the debug pins',
                              '<moterank>',
                              self._handleDebugpins)
        self._registerCommand('delay',
                              'd',
                              'introduce a delay between each event, in s',
                              '<delay_in_s>',
                              self._handleDelay)
        self._registerCommand('help', 
                              'h',
                              'print this menu',
                              '',
                              self._handleHelp)
        self._registerCommand('leds',
                              'l',
                              'print the current state of the leds',
                              '<moterank>',
                              self._handleLeds)
        self._registerCommand('nummotes',
                              'n',
                              'print the number of mote connected to the engine',
                              'nummotes',
                              self._handleNummotes)
        self._registerCommand('pause',
                              'p',
                              'pause the execution',
                              '',
                              self._handlePause)
        self._registerCommand('quit',
                              'q',
                              'quit this application',
                              '',
                              self._handleQuit)
        self._registerCommand('resume',
                              'r',
                              'resume the execution',
                              '',
                              self._handleResume)
        self._registerCommand('step',
                              's',
                              'execute a number of steps, then pause',
                              '<numsteps>',
                              self._handleStep)
        
        # logging
        self.log           = logging.getLogger('SimCli')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # set thread name
        self.setName('SimCli')
        
        # thread daemon mode
        self.setDaemon(False)
        
    def run(self):
        print 'OpenSim server\n'
        
        while True:
            
            params = raw_input('> ')
            
            self.log.debug('Following command entered:'+params)
            
            params = params.split()
            if len(params)<1:
                continue
                
            if len(params)==2 and params[1]=='?':
                if not self._printUsageFromName(params[0]):
                    if not self._printUsageFromAlias(params[0]):
                        print ' unknown command or alias \''+params[0]+'\''
                continue

            found = False
            for command in self.commands:
                if command['name']==params[0] or command['alias']==params[0]:
                    found = True
                    command['callback'](params[1:])
                    break
            
            if found==False:
                print ' unknown command or alias \''+params[0]+'\''
    
    #======================== private =========================================
    
    def _registerCommand(self,name,alias,description,usage,callback):
        self.commands.append({
                                'name':          name,
                                'alias':         alias,
                                'description':   description,
                                'usage':         usage,
                                'callback':      callback,
                             })
    
    def _printUsageFromName(self,commandname):
        for command in self.commands:
            if command['name']==commandname:
                print 'usage: '+commandname+' '+command['usage']
                return True
        return False
    
    def _printUsageFromAlias(self,commandalias):
        for command in self.commands:
            if command['alias']==commandalias:
                print 'usage: '+commandalias+' '+command['usage']
                return True
        return False
    
    #=== command handlers
   
    def _handleBoot(self,params):
        # usage
        if len(params)!=1:
            self._printUsageFromName('boot')
            return
        
        # filter errors
        try:
            rank = int(params[0])
        except ValueError:
            print 'invalid rank'
            return
        
        try:
            moteHandler = self.engine.getMoteHandler(rank)
        except IndexError:
            print 'invalid rank'
            return
        
        moteHandler.bspSupply.switchOn()
        
        print 'OK'
            
    def _handleDebugpins(self,params):
        # usage
        if len(params)!=1:
            self._printUsageFromName('debugpins')
            return
        
        # filter errors
        try:
            rank = int(params[0])
        except ValueError:
            print 'invalid rank'
            return
        
        try:
            moteHandler = self.engine.getMoteHandler(rank)
        except IndexError:
            print 'invalid rank'
            return
        pins        = moteHandler.bspDebugpins
        
        output  = ''
        output += '- frame: '+self._pinStateToString(pins.get_framePinHigh())+'\n'
        output += '- slot:  '+self._pinStateToString(pins.get_slotPinHigh())+'\n'
        output += '- fsm:   '+self._pinStateToString(pins.get_fsmPinHigh())+'\n'
        output += '- isr:   '+self._pinStateToString(pins.get_isrPinHigh())+'\n'
        output += '- radio: '+self._pinStateToString(pins.get_radioPinHigh())+'\n'
        print output
    
    def _handleDelay(self,params):
        # usage
        if len(params)!=1:
            self._printUsageFromName('delay')
            return
        
        # filter errors
        try:
            delay = float(params[0])
        except ValueError:
            print 'invalid delay'
            return
        
        # apply delay
        self.engine.setDelay(delay)
    
    def _handleHelp(self,params):
        # usage
        if len(params)!=0:
            self._printUsageFromName('help')
            return
        
        output  = '\n'
        output  = ' Available commands:\n'
        for command in self.commands:
            output += '   '+command['name']+' ('+command['alias']+')'+' - '+command['description']+'\n'
        output += ' Notes:\n'
        output += '  - type \'<command> ?\' to get the usage\n'
        print output
        
    def _handleLeds(self,params):
        # usage
        if len(params)!=1:
            self._printUsageFromName('leds')
            return
        
        # filter errors
        try:
            rank = int(params[0])
        except ValueError:
            print 'invalid rank'
            return
        
        try:
            moteHandler = self.engine.getMoteHandler(rank)
        except IndexError:
            print 'invalid rank'
            return
        leds        = moteHandler.bspLeds
        
        output  = ''
        output += '- error: '+self._ledStateToString(leds.get_errorLedOn())+'\n'
        output += '- radio: '+self._ledStateToString(leds.get_radioLedOn())+'\n'
        output += '- sync:  '+self._ledStateToString(leds.get_syncLedOn())+'\n'
        output += '- debug: '+self._ledStateToString(leds.get_debugLedOn())+'\n'
        print output
    
    def _handleNummotes(self,params):
        # usage
        if len(params)!=0:
            self._printUsageFromName('nummotes')
            return
        
        print self.engine.getNumMotes()
        
    def _handlePause(self,params):
        # usage
        if len(params)!=0:
            self._printUsageFromName('pause')
            return
        
        # pause the engine
        self.engine.pause()
    
    def _handleQuit(self,params):
        
        # usage
        if len(params)!=0:
            self._printUsageFromName('quit')
            return
        
        # this thread quits
        sys.exit(0)
    
    def _handleResume(self,params):
        # usage
        if len(params)!=0:
            self._printUsageFromName('resume')
            return
        
        # pause the engine
        self.engine.resume()
    
    def _handleStep(self,params):
        # usage
        if len(params)!=1:
            self._printUsageFromName('step')
            return
        
        # filter errors
        try:
            numsteps = int(params[0])
        except ValueError:
            print 'invalid numsteps'
            return
        
        # pause the engine
        self.engine.step(numsteps)
    
    #======================== helpers =========================================
    
    def _ledStateToString(self,state):
        if state:
            return 'ON'
        else:
            return 'OFF'
    
    def _pinStateToString(self,state):
        if state:
            return 'HIGH'
        else:
            return 'LOW'