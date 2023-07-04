import json
import websocket
import requests

class jmriConnector():
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.ws = websocket.WebSocket()
        url = ("ws://" + str(self.server_address) + 
                        ":" + str(self.server_port) +
                        "/json/")
        self.ws.connect(url)
        # The "hello" connection response. Receive it here to pull it off the queue.
        response = self.ws.recv_data()
        
    def __del__(self):
        self.ws.close()

    #############################################################################
    # Below, we have methods for Websockets. It seems like some of the JMRI API
    # is websockets only (throttles), and other parts of the API are via 
    # HTTP / JSON only (listing things). Unfortunately that means we're implementing
    # both.
    #############################################################################

    """
    _wsSend sends a websocket request, receives the response, and returns json.

    jmri_type is the type of request going to JMRI - e.g. "throttle" or "reporter"
    data is a map with details about the request
    method is how the data will be uploaded; usually "post" if there's data
    See the JMRI jquery.jmri.js file for usage examples; _sendBuilder is structured after
    the jmri.socket.send function that's called in that file.
    Also, jmri.socket.send is defined in jquery.websocket.js around line 41.

    type is the JMRI object type 
    name is the JMRI object name
    See https://www.jmri.org/help/en/html/web/JsonServlet.shtml
    See https://www.jmri.org/JavaDoc/doc/jmri/server/json/package-summary.html
    See jmri.server.json classes in https://www.jmri.org/JavaDoc/doc/
    See http://localhost:12080/json/type
    """
    def _wsSend(self, jmri_type, data=None, method=None):
        s = self._sendBuilder(jmri_type, data, method)
        err = self.ws.send(s)
        #TODO: check error code

        r = self.ws.recv_data()
        #print(r)
        if r[1]:
            r_json = json.loads(r[1])
            return r_json
        else:
            return None

    def _sendBuilder(self, jmri_type, data=None, method=None):
        m = {"type" : jmri_type}
        if data:
            m["data"] = data
        if method:
            m["method"] = method
        return json.dumps(m)
    
    """ notes on what string we should "send":
    from jquery.websocket.js:
    
    ws.send = function (type, data, method) {
                    var m = { type: type, method: method };
                    m = $.extend(true, m, $.extend(true, {}, settings.options, m));
                    if (data) m['data'] = data;
                    return this._send(JSON.stringify(m));
    """


    #############################################################################
    # Below, we have methods for HTTP / JSON. It seems like some of the JMRI API
    # is websockets only (throttles), and other parts of the API are via 
    # HTTP / JSON only (listing things). Unfortunately that means we're implementing
    # both.
    #############################################################################
    
    # _httpSend is typically used for listing things (e.g. reporters) in JMRI.
    # When listing, 'data' typically isn't used. To list a specific object, use
    # the 'name' key in data or use the websocket approach instead.
    def _httpSend(self, jmri_type, data=None, method=None):
        if data:
            r = requests.get(self._urlBuilder(jmri_type, data["name"]))
        else:
            r = requests.get(self._urlBuilder(jmri_type))
        return r.json()

    # _urlBuilder creates a HTTP url for JMRI json endpoints. See above in the
    # websocket section for links on the appropriate jmri_type and jmri_name values.
    def _urlBuilder(self, jmri_type, jmri_name=None):
        url = "http://" + str(self.server_address) + ":" + str(self.server_port) + "/"
        url += "json/"
        url += str(jmri_type)
        if jmri_name:
            url += "/"
            url += str(jmri_name)
        return url

    #############################################################################
    # Reporters
    #############################################################################

    def list_reporters(self):
        return self._httpSend("reporter")
    
    def get_reporter_state(self, reporter_name):
        data = {"name" : reporter_name}
        return self._wsSend("reporter", data) # method="post"
    
    #############################################################################
    # Throttles
    #############################################################################
    """
    See https://groups.io/g/jmriusers/topic/how_to_request_a_throttle_by/78533852?p=
    See https://github.com/JMRI/JMRI/pull/9182
    See web/js/jquery.jmri.js (jmri.setThrottle) in the main JMRI github repo for usage
       examples. https://github.com/JMRI/JMRI/blob/master/web/js/jquery.jmri.js
    Note that in the jquery.jmri.js example above, most of the methods have both
    routines for websockets and http / json. However, getThrottle() returns False for
    JSON and only has websocket support.
    """
    def run_train(self, engine_address, engine_speed, engine_direction):
        throttle_name = "mycoolthrottle"
        
        data = {"name": throttle_name, 
                "address" : engine_address}
        r = self._wsSend("throttle", data)
        print('')
        print("Run train: select throttle")
        print(str(data))
        print(str(r))
        
        forward = 1
        if not engine_direction == "forward":
            forward = 0
        data = {"throttle": throttle_name, 
                "speed" : engine_speed, 
                "forward": forward}
        r = self._wsSend("throttle", data, 'post')
        print('')
        print("Run train: set throttle speed")
        print(str(data))
        print(str(r))

        return

    