#!/usr/bin/python
# Copyright (c) 2013, Ken Bannister.
# All rights reserved.
# 
# Released under the BSD 2-Clause license as published at the link below.
# http://opensource.org/licenses/BSD-2-Clause
import sys
import os

if __name__=="__main__":
    # Update pythonpath if running in in-tree development mode
    basedir  = os.path.dirname(__file__)
    confFile = os.path.join(basedir, "openvisualizer.conf")
    if os.path.exists(confFile):
        import pathHelper
        pathHelper.updatePath()

import logging
log = logging.getLogger('openVisualizerWeb')

try:
    from openvisualizer.moteState import moteState
except ImportError:
    # Debug failed lookup on first library import
    print 'ImportError: cannot find openvisualizer.moteState module'
    print 'sys.path:\n\t{0}'.format('\n\t'.join(str(p) for p in sys.path))

import json
import bottle
import random
import re
import threading
import signal
import functools
from bottle        import view

import openVisualizerApp
import openvisualizer.openvisualizer_utils as u
from openvisualizer.eventBus      import eventBusClient
from openvisualizer.SimEngine     import SimEngine
from openvisualizer.BspEmulator   import VcdLogger
from openvisualizer import ovVersion


from pydispatch import dispatcher

# add default parameters to all bottle templates
view = functools.partial(view, ovVersion='.'.join(list([str(v) for v in ovVersion.VERSION])))

IoTLabUIDList = {"m3-1":"a182",
		"m3-2":"9982",
		"m3-3":"b868",
		"m3-4":"9176",
		"m3-5":"a176",
		"m3-6":"a682",
		"m3-7":"9883",
		"m3-8":"9983",
		"m3-9":"2162",
		"m3-10":"8772",
		"m3-11":"9971",
		"m3-12":"a869",
		"m3-13":"a569",
		"m3-14":"9869",
		"m3-15":"c280",
		"m3-16":"a269",
		"m3-17":"a172",
		"m3-18":"b679",
		"m3-19":"9969",
		"m3-20":"b077",
		"m3-21":"b382",
		"m3-22":"9171",
		"m3-23":"a669",
		"m3-24":"8971",
		"m3-25":"9071",
		"m3-26":"9469",
		"m3-27":"b778",
		"m3-28":"a882",
		"m3-29":"0662",
		"m3-30":"c168",
		"m3-31":"b377",
		"m3-32":"a482",
		"m3-33":"b482",
		"m3-34":"b968",
		"m3-35":"a581",
		"m3-36":"b568",
		"m3-37":"0562",
		"m3-38":"a181",
		"m3-39":"c078",
		"m3-40":"a978",
		"m3-41":"b980",
		"m3-42":"a476",
		"m3-43":"b480",
		"m3-44":"c181",
		"m3-45":"a872",
		"m3-46":"9278",
		"m3-47":"b776",
		"m3-48":"a780",
		"m3-49":"b683",
		"m3-50":"8576",
		"m3-51":"9472",
		"m3-52":"8770",
		"m3-53":"a068",
		"m3-54":"c180",
		"m3-55":"9878",
		"m3-56":"8677",
		"m3-57":"8577",
		"m3-58":"b357",
		"m3-59":"b780",
		"m3-60":"a579",
		"m3-61":"b678",
		"m3-62":"8372",
		"m3-63":"a169",
		"m3-64":"8777",
		"m3-65":"8778",
		"m3-66":"b680",
		"m3-67":"c268",
		"m3-68":"a983",
		"m3-69":"9682",
		"m3-70":"9067",
		"m3-71":"a779",
		"m3-72":"8972",
		"m3-73":"8771",
		"m3-74":"a171",
		"m3-75":"8981",
		"m3-76":"9177",
		"m3-77":"1462",
		"m3-78":"a382",
		"m3-79":"b976",
		"m3-80":"9476",
		"m3-81":"a676",
		"m3-82":"8767",
		"m3-83":"a575",
		"m3-84":"9769",
		"m3-85":"a271",
		"m3-86":"a471",
		"m3-87":"9277",
		"m3-88":"a475",
		"m3-89":"9882",
		"m3-90":"a878",
		"m3-91":"1662",
		"m3-92":"b078",
		"m3-93":"3960",
		"m3-94":"2960",
		"m3-95":"a770",
		"m3-96":"b468",
		"m3-97":"b179",
		"m3-98":"b069",
		"m3-99":"b277",
		"m3-100":"b080",
		"m3-101":"9181",
		"m3-102":"a881",
		"m3-103":"9881",
		"m3-104":"a775",
		"m3-105":"b576",
		"m3-106":"9382",
		"m3-107":"a072",
		"m3-108":"8477",
		"m3-109":"1062",
		"m3-110":"a071",
		"m3-111":"9172",
		"m3-112":"a578",
		"m3-113":"a671",
		"m3-114":"a879",
		"m3-115":"8471",
		"m3-116":"8969",
		"m3-117":"2262",
		"m3-118":"9376",
		"m3-119":"a468",
		"m3-120":"a469",
		"m3-121":"8572",
		"m3-122":"a180",
		"m3-123":"c276",
		"m3-124":"9772",
		"m3-125":"9672",
		"m3-126":"b269",
		"m3-127":"8671",
		"m3-128":"9980",
		"m3-129":"9783",
		"m3-130":"a272",
		"m3-131":"9369",
		"m3-132":"a369",
		"m3-133":"2360",
		"m3-134":"a069",
		"m3-135":"1761",
		"m3-136":"9669",
		"m3-137":"9371",
		"m3-138":"b169",
		"m3-139":"a778",
		"m3-140":"b483",
		"m3-141":"8579",
		"m3-142":"a783",
		"m3-143":"9779",
		"m3-144":"c069",
		"m3-145":"9680",
		"m3-146":"a668",
		"m3-147":"9380",
		"m3-148":"9976",
		"m3-149":"9683",
		"m3-150":"b676",
		"m3-151":"9576",
		"m3-152":"b769",
		"m3-153":"b081",
		"m3-154":"a279",
		"m3-155":"3160",
		"m3-156":"1861",
		"m3-157":"a380",
		"m3-158":"a781",
		"m3-159":"a081",
		"m3-160":"9880",
		"m3-161":"9582",
		"m3-162":"8775",
		"m3-163":"9276",
		"m3-164":"b281",
		"m3-165":"9478",
		"m3-166":"9671",
		"m3-167":"1862",
		"m3-168":"8475",
		"m3-169":"a276",
		"m3-170":"c076",
		"m3-171":"9379",
		"m3-172":"9678",
		"m3-173":"9381",
		"m3-174":"a179",
		"m3-175":"a870",
		"m3-176":"9572",
		"m3-177":"3061",
		"m3-178":"a281",
		"m3-179":"a776",
		"m3-180":"0762",
		"m3-181":"b583",
		"m3-182":"9968",
		"m3-183":"9169",
		"m3-184":"9168",
		"m3-185":"9978",
		"m3-186":"8979",
		"m3-187":"9571",
		"m3-188":"9072",
		"m3-189":"9480",
		"m3-190":"b882",
		"m3-191":"8872",
		"m3-192":"b579",
		"m3-193":"a376",
		"m3-194":"a375",
		"m3-195":"a670",
		"m3-196":"a768",
		"m3-197":"a972",
		"m3-198":"a383",
		"m3-199":"8569",
		"m3-200":"c376",
		"m3-201":"8476",
		"m3-202":"a183",
		"m3-203":"9584",
		"m3-204":"b877",
		"m3-205":"8967",
		"m3-206":"9979",
		"m3-207":"a379",
		"m3-208":"9076",
		"m3-209":"b379",
		"m3-210":"c081",
		"m3-211":"8875",
		"m3-212":"b280",
		"m3-213":"8472",
		"m3-214":"9567",
		"m3-215":"9175",
		"m3-216":"b369",
		"m3-217":"9871",
		"m3-218":"b582",
		"m3-219":"b481",
		"m3-220":"2160",
		"m3-221":"9981",
		"m3-222":"3860",
		"m3-223":"b768",
		"m3-224":"b180",
		"m3-225":"c068",
		"m3-226":"b268",
		"m3-227":"9377",
		"m3-228":"9283",
		"m3-229":"b068",
		"m3-230":"3861",
		"m3-231":"8779",
		"m3-232":"a372",
		"m3-233":"8881",
		"m3-234":"9481",
		"m3-235":"2362",
		"m3-236":"a677",
		"m3-237":"1562",
		"m3-238":"a083",
		"m3-239":"b876",
		"m3-240":"3761",
		"m3-241":"8371",
		"m3-242":"9077",
		"m3-243":"a678",
		"m3-244":"9579",
		"m3-245":"9269",
		"m3-246":"b881",
		"m3-247":"a982",
		"m3-248":"b383",
		"m3-249":"9583",
		"m3-250":"a483",
		"m3-251":"9876",
		"m3-252":"b580",
		"m3-253":"c277",
		"m3-254":"8982",
		"m3-255":"b168",
		"m3-256":"1660",
		"m3-257":"b668",
		"m3-258":"1860",
		"m3-259":"a580",
		"m3-260":"a478",
		"m3-261":"9483",
		"m3-262":"a481",
		"m3-263":"8470",
		"m3-264":"9575",
		"m3-265":"a470",
		"m3-266":"c369",
		"m3-267":"b182",
		"m3-268":"9681",
		"m3-269":"b477",
		"m3-270":"b380",
		"m3-271":"a980",
		"m3-272":"2861",
		"m3-273":"9279",
		"m3-274":"a880",
		"m3-275":"9771",
		"m3-276":"9482",
		"m3-277":"c176",
		"m3-278":"a968",
		"m3-279":"9780",
		"m3-280":"b381",
		"m3-281":"a582",
		"m3-282":"a283",
		"m3-283":"b781",
		"m3-284":"9875",
		"m3-285":"a583",
		"m3-286":"a969",
		"m3-287":"b982",
		"m3-288":"1162",
		"m3-289":"c370",
		"m3-290":"a078",
		"m3-291":"9975",
		"m3-292":"9183",
		"m3-293":"9475",
		"m3-294":"8669",
		"m3-295":"9467",
		"m3-296":"9069",
		"m3-297":"a079",
		"m3-298":"b569",
		"m3-299":"1362",
		"m3-300":"8876",
		"m3-301":"a675",
		"m3-302":"9271",
		"m3-303":"a370",
		"m3-304":"8877",
		"m3-305":"8871",
		"m3-306":"9479",
		"m3-307":"a082",
		"m3-308":"b083",
		"m3-309":"c368",
		"m3-310":"c169",
		"m3-311":"a570",
		"m3-312":"9782",
		"m3-313":"9082",
		"m3-314":"9580",
		"m3-315":"8882",
		"m3-316":"0862",
		"m3-317":"b276",
		"m3-318":"8370",
		"m3-319":"a577",
		"m3-320":"a477",
		"m3-321":"9879",
		"m3-322":"b282",
		"m3-323":"a777",
		"m3-324":"a782",
		"m3-325":"9776",
		"m3-326":"a480",
		"m3-327":"0962",
		"m3-328":"9282",
		"m3-329":"b177",
		"m3-330":"b082",
		"m3-331":"a282",
		"m3-332":"8578",
		"m3-333":"a178",
		"m3-334":"b782",
		"m3-335":"a472",
		"m3-336":"9468",
		"m3-337":"b279",
		"m3-338":"9668",
		"m3-339":"9477",
		"m3-340":"a479",
		"m3-341":"b983",
		"m3-342":"b079",
		"m3-343":"a568",
		"m3-344":"c082",
		"m3-345":"9167",
		"m3-346":"b669",
		"m3-347":"b368",
		"m3-348":"9868",
		"m3-349":"2553",
		"m3-350":"8570",
		"m3-351":"9781",
		"m3-352":"8870",
		"m3-353":"9267",
		"m3-354":"9367",
		"m3-355":"b479",
		"m3-356":"a681",
		"m3-357":"8672",
		"m3-358":"9378",
		"m3-359":"c171",
		"m3-360":"3360",
		"m3-361":"8667",
		"m3-362":"a976",
		"m3-363":"b883",
		"m3-364":"1661",
		"m3-365":"3561",
		"m3-366":"3060",
		"m3-367":"b469",
		"m3-368":"2953",
		"m3-369":"8567",
		"m3-370":"a075",
		"m3-371":"c077",
		"m3-372":"9775",
		"m3-373":"1762",
		"m3-374":"8575",
		"m3-375":"2254",
		"m3-376":"a175",
		"m3-377":"9484",
		"m3-378":"c071",
		"m3-379":"3460",
		"m3-380":"a979"
}
def findiotlabuid(iotlabuid):
    	for myID in IoTLabUIDList:
    		if  IoTLabUIDList[myID]==iotlabuid:
    			return myID
    	return iotlabuid
    
class OpenVisualizerWeb(eventBusClient.eventBusClient):
    '''
    Provides web UI for OpenVisualizer. Runs as a webapp in a Bottle web
    server.
    '''
    
    def __init__(self,app,websrv):
        '''
        :param app:    OpenVisualizerApp
        :param websrv: Web server
        '''
        log.info('Creating OpenVisualizerWeb')
        
        # store params
        self.app             = app
        self.engine          = SimEngine.SimEngine()
        self.websrv          = websrv
        
        self._defineRoutes()
        
        # To find page templates
        bottle.TEMPLATE_PATH.append('{0}/web_files/templates/'.format(self.app.datadir))
        
        # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'OpenVisualizerWeb',
            registrations         =  [],
        )
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _defineRoutes(self):
        '''
        Matches web URL to impelementing method. Cannot use @route annotations
        on the methods due to the class-based implementation.
        '''
        self.websrv.route(path='/',                                       callback=self._showMoteview)
        self.websrv.route(path='/moteview',                               callback=self._showMoteview)
        self.websrv.route(path='/moteview/:moteid',                       callback=self._showMoteview)
        self.websrv.route(path='/motedata/:moteid',                       callback=self._getMoteData)
        self.websrv.route(path='/toggleDAGroot/:moteid',                  callback=self._toggleDAGroot)
        self.websrv.route(path='/eventBus',                               callback=self._showEventBus)
        self.websrv.route(path='/routing',                                callback=self._showRouting)
        self.websrv.route(path='/routing/dag',                            callback=self._showDAG)
        self.websrv.route(path='/eventdata',                              callback=self._getEventData)
        self.websrv.route(path='/wiresharkDebug/:enabled',                callback=self._setWiresharkDebug)
        self.websrv.route(path='/gologicDebug/:enabled',                  callback=self._setGologicDebug)
        self.websrv.route(path='/topology',                               callback=self._topologyPage)
        self.websrv.route(path='/topology/data',                          callback=self._topologyData)
        self.websrv.route(path='/topology/motes',         method='POST',  callback=self._topologyMotesUpdate)
        self.websrv.route(path='/topology/connections',   method='PUT',   callback=self._topologyConnectionsCreate)
        self.websrv.route(path='/topology/connections',   method='POST',  callback=self._topologyConnectionsUpdate)
        self.websrv.route(path='/topology/connections',   method='DELETE',callback=self._topologyConnectionsDelete)
        self.websrv.route(path='/topology/route',         method='GET',   callback=self._topologyRouteRetrieve)
        self.websrv.route(path='/static/<filepath:path>',                 callback=self._serverStatic)
    
    @view('moteview.tmpl')
    def _showMoteview(self, moteid=None):
        '''
        Collects the list of motes, and the requested mote to view.
        
        :param moteid: 16-bit ID of mote (optional)
        '''
        log.debug("moteview moteid parameter is {0}".format(moteid));
        
        motelist = []
        motelistIL = []
        for ms in self.app.moteStates:
            addr = ms.getStateElem(moteState.moteState.ST_IDMANAGER).get16bAddr()
            if addr:
            	iotlabuid= ''.join(['%02x'%b for b in addr])
            	iotlabID=findiotlabuid(iotlabuid)
            	motelist.append( iotlabuid )
            	motelistIL.append( iotlabuid+" : "+iotlabID )
            else:
                motelist.append(ms.moteConnector.serialport)
                motelistIL.append(ms.moteConnector.serialport)
        
        tmplData = {
            'motelist'       : motelist,
            'motelistIL'       : motelistIL,
            'requested_mote' : moteid if moteid else 'none',
        }
        return tmplData
    
    def _serverStatic(self, filepath):
        return bottle.static_file(filepath, 
                                  root='{0}/web_files/static/'.format(self.app.datadir))
    
    def _toggleDAGroot(self, moteid):
        '''
        Triggers toggle DAGroot state, via moteState. No real response. Page is
        updated when next retrieve mote data.
        
        :param moteid: 16-bit ID of mote
        '''
        log.info('Toggle root status for moteid {0}'.format(moteid))
        ms = self.app.getMoteState(moteid)
        if ms:
            log.debug('Found mote {0} in moteStates'.format(moteid))
            ms.triggerAction(ms.TRIGGER_DAGROOT)
            return '{"result" : "success"}'
        else:
            log.debug('Mote {0} not found in moteStates'.format(moteid))
            return '{"result" : "fail"}'
    
    def _getMoteData(self, moteid):
        '''
        Collects data for the provided mote.
        
        :param moteid: 16-bit ID of mote
        '''
        log.debug('Get JSON data for moteid {0}'.format(moteid))
        ms = self.app.getMoteState(moteid)
        if ms:
            log.debug('Found mote {0} in moteStates'.format(moteid))
            states = {
                ms.ST_IDMANAGER   : ms.getStateElem(ms.ST_IDMANAGER).toJson('data'),
                ms.ST_ASN         : ms.getStateElem(ms.ST_ASN).toJson('data'),
                ms.ST_ISSYNC      : ms.getStateElem(ms.ST_ISSYNC).toJson('data'),
                ms.ST_MYDAGRANK   : ms.getStateElem(ms.ST_MYDAGRANK).toJson('data'),
                ms.ST_KAPERIOD    : ms.getStateElem(ms.ST_KAPERIOD).toJson('data'),
                ms.ST_OUPUTBUFFER : ms.getStateElem(ms.ST_OUPUTBUFFER).toJson('data'),
                ms.ST_BACKOFF     : ms.getStateElem(ms.ST_BACKOFF).toJson('data'),
                ms.ST_MACSTATS    : ms.getStateElem(ms.ST_MACSTATS).toJson('data'),
                ms.ST_SCHEDULE    : ms.getStateElem(ms.ST_SCHEDULE).toJson('data'),
                ms.ST_QUEUE       : ms.getStateElem(ms.ST_QUEUE).toJson('data'),
                ms.ST_NEIGHBORS   : ms.getStateElem(ms.ST_NEIGHBORS).toJson('data'),
            }
        else:
            log.debug('Mote {0} not found in moteStates'.format(moteid))
            states = {}
        return states
    
    def _setWiresharkDebug(self, enabled):
        '''
        Selects whether eventBus must export debug packets.
        
        :param enabled: 'true' if enabled; any other value considered false
        '''
        log.info('Enable wireshark debug : {0}'.format(enabled))
        self.app.eventBusMonitor.setWiresharkDebug(enabled == 'true')
        return '{"result" : "success"}'
    
    def _setGologicDebug(self, enabled):
        log.info('Enable GoLogic debug : {0}'.format(enabled))
        VcdLogger.VcdLogger().setEnabled(enabled == 'true')
        return '{"result" : "success"}'
    
    @view('eventBus.tmpl')
    def _showEventBus(self):
        '''
        Simple page; data for the page template is identical to the data 
        for periodic updates of event list.
        '''
        return self._getEventData()
    
    def _showDAG(self):
        states,edges = self.app.topology.getDAG()  
        return { 'states': states, 'edges': edges }
    
    @view('routing.tmpl')
    def _showRouting(self, moteid=None):
        motelist = []
        motelistIL = []
        for ms in self.app.moteStates:
            addr = ms.getStateElem(moteState.moteState.ST_IDMANAGER).get16bAddr()
            if addr:
            	iotlabuid= ''.join(['%02x'%b for b in addr])
            	iotlabID=findiotlabuid(iotlabuid)
            	motelist.append( iotlabuid )
            	motelistIL.append( iotlabuid+" : "+iotlabID )
            else:
                motelist.append(ms.moteConnector.serialport)
                motelistIL.append(ms.moteConnector.serialport)
        
        tmplData = {
            'motelist'       : motelist,
            'motelistIL'       : motelistIL,
            'requested_mote' : moteid if moteid else 'none',
        }
        return tmplData
        
    @view('topology.tmpl')
    def _topologyPage(self):
        '''
        Retrieve the HTML/JS page.
        '''
        
        return {}
    
    def _topologyData(self):
        '''
        Retrieve the topology data, in JSON format.
        '''
        
        # motes
        motes = []
        rank  = 0
        while True:
            try:
                mh            = self.engine.getMoteHandler(rank)
                id            = mh.getId()
                (lat,lon)     = mh.getLocation()
                motes += [
                    {
                        'id':    id,
                        'lat':   lat,
                        'lon':   lon,
                    }
                ]
                rank+=1
            except IndexError:
               break
        
        # connections
        connections = self.engine.propagation.retrieveConnections()
        
        data = {
            'motes'          : motes,
            'connections'    : connections,
        }
        
        return data
    
    def _topologyMotesUpdate(self):
        
        motesTemp = {}
        for (k,v) in bottle.request.forms.items():
            m = re.match("motes\[(\w+)\]\[(\w+)\]", k)
            assert m
            index  = int(m.group(1))
            param  =     m.group(2)
            try:
                v  = int(v)
            except ValueError:
                try:
                    v  = float(v)
                except ValueError:
                    pass
            if index not in motesTemp:
                motesTemp[index] = {}
            motesTemp[index][param] = v
        
        for (_,v) in motesTemp.items():
            mh = self.engine.getMoteHandlerById(v['id'])
            mh.setLocation(v['lat'],v['lon'])
    
    def _topologyConnectionsCreate(self):
        
        data = bottle.request.forms
        assert sorted(data.keys())==sorted(['fromMote', 'toMote'])
        
        fromMote = int(data['fromMote'])
        toMote   = int(data['toMote'])
        
        self.engine.propagation.createConnection(fromMote,toMote)
    
    def _topologyConnectionsUpdate(self):
        data = bottle.request.forms
        assert sorted(data.keys())==sorted(['fromMote', 'toMote', 'pdr'])
        
        fromMote = int(data['fromMote'])
        toMote   = int(data['toMote'])
        pdr      = float(data['pdr'])
        
        self.engine.propagation.updateConnection(fromMote,toMote,pdr)
    
    def _topologyConnectionsDelete(self):
        
        data = bottle.request.forms
        assert sorted(data.keys())==sorted(['fromMote', 'toMote'])
        
        fromMote = int(data['fromMote'])
        toMote   = int(data['toMote'])
        
        self.engine.propagation.deleteConnection(fromMote,toMote)
    
    def _topologyRouteRetrieve(self):
        
        data = bottle.request.query
        
        assert data.keys()==['destination']
        
        detination_eui = [0x14,0x15,0x92,0xcc,0x00,0x00,0x00,int(data['destination'])]
        
        route = self._dispatchAndGetResult(
            signal       = 'getSourceRoute', 
            data         = detination_eui,
        )
        
        route = [r[-1] for r in route]
        
        data = {
            'route'          : route,
        }
        
        return data
    
    def _getEventData(self):
        response = {
            'isDebugPkts' : 'true' if self.app.eventBusMonitor.wiresharkDebugEnabled else 'false',
            'stats'       : self.app.eventBusMonitor.getStats(),
        }
        return response

#============================ main ============================================
from argparse       import ArgumentParser

def _addParserArgs(parser):
    '''Adds arguments specific to web UI.'''
    
    parser.add_argument('-H', '--host',
        dest       = 'host',
        default    = '0.0.0.0',
        action     = 'store',
        help       = 'host address'
    )
    
    parser.add_argument('-p', '--port',
        dest       = 'port',
        default    = 8080,
        action     = 'store',
        help       = 'port number'
    )

webapp = None
if __name__=="__main__":
    parser   =  ArgumentParser()
    _addParserArgs(parser)
    argspace = parser.parse_known_args()[0]
    
    # log
    log.info(
        'Initializing OpenVisualizerWeb with options: \n\t{0}'.format(
            '\n    '.join(
                [
                    'host = {0}'.format(argspace.host),
                    'port = {0}'.format(argspace.port)
                ]
            )
        )
    )
    
    #===== start the app
    app      = openVisualizerApp.main(parser)
    
    #===== add a web interface
    websrv   = bottle.Bottle()
    webapp   = OpenVisualizerWeb(app, websrv)
    
    # start web interface in a separate thread
    webthread = threading.Thread(
        target = websrv.run,
        kwargs = {
            'host'          : argspace.host,
            'port'          : argspace.port,
            'quiet'         : not app.debug,
            'debug'         : app.debug,
        }
    )
    webthread.start()
    
    #===== add a cli (minimal) interface
    
    banner  = []
    banner += ['OpenVisualizer']
    banner += ['web interface started at {0}:{1}'.format(argspace.host,argspace.port)]
    banner += ['enter \'q\' to exit']
    banner  = '\n'.join(banner)
    print banner
    
    while True:
        input = raw_input('> ')
        if input=='q':
            print 'bye bye.'
            app.close()
            os.kill(os.getpid(), signal.SIGTERM)
