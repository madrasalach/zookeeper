import pyvisa as visa

COMMON_CMDS = [
    ('reset', '*RST'),
    ('init', 'INIT'),
    ('clear', '*CLS')
    ]

class Property(object):
    
    def __init__(self, instrument, attr):
        self.__instrument = instrument
        self.attr = attr.upper()
        
    def __getattr__(self, attr):
        """
        Recursively construct the query or write directive
        by joining parts of the request with :
        """
        return Property(
            self.__instrument,
            ':'.join((self.attr, attr.upper()))
            )
    
    def __call__(self, value=None):
        """
        Properties are either queries or write requests.
        
        Terminate hierarchial queries with ?
        and write directive with their corresponding value
        """
        if value is None:
            return self.__instrument.query(self.attr + '?')
        else:
            if not isinstance(value, str):
                value = str(value)
                
        return self.__instrument.write(self.attr + ' ' + value)

class Instrument():
    """
    A SCPI (skippy) instrument
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    
    def __init__(self, port=None, backend='', **resource_params):
        """
        Initialises member variables, but does not immediately connect
        to instrument. User calls connect() method explicitly
        
        backend : pyvisa backend (@py for RPi, @sim for dev mode)
        port : port to which instrument is bound to
        instrument : a pyvisa device object used for communication
        resource_params: device specific settings
        """
        self.__backend = backend
        self.__rm = visa.ResourceManager(backend)
        self.__instrument = None
        self.__port = port
        self.__resource_params = resource_params
    
    def __del__(self):
        """
        Object cleanup
        """
        if self.conected:
            self.disconnect()
            
        del self.__instrument
        del self.__rm
    
    def __getattr__(self, attr):
        """
        Dunder method to allow for pythonic commands
        """
        # case 1 - common query
        
        # case 2 - common write
        
        # finally, just deal with it as device specific
        return Property(self, attr)
    
    def __repr__(self):
        ret = []
        ret.append(f"SCPI (skippy) Instrument")
        ret.append("~~~~~~~~~~~~~~~~~~~~~~~~")
        ret.append(f"Backend: {self.__backend}")
        ret.append(f"Port: {self.__port}")
        if self.connected:
            ret.append(f"Instrument connected")
            ret.append(f"Manufacturer ID: {self.id}")
        return '\n'.join([r for r in ret])
    
    # getter and setter methods
    @property
    def backend(self):
        return self.__backend
    
    @property
    def instrument(self):
        return self.__instrument
    
    @property
    def resource_params(self):
        return self.__resource_params
    
    @property
    def id(self):
        """
        Queries the lab instrument for the manufacturer ID
        """
        return self.query('*IDN?')
    
    @property
    def port(self):
        return self.__port
    
    @port.setter
    def port(self, port):
        """
        Disconnect and update port

        """
        if self.__instrument is not None:
            self.disconnect()
        
        self.__port = port
        
    @property
    def connected(self):
        """
        True if the instrument has been connected
        i.e connect() method called and not yet disconnected
        """
        if self.__instrument is None:
            return False
        
        try:
            self.__instrument.session
            return True
        except visa.InvalidSession:
            return False
        
    # session connect/disconnect methods
    
    def connect(self):
        """
        Connects the lab instrument on the Instrument's port
        using PyVisa.
        
        The resource is bound to the member instrument variable
        """
        if self.__instrument is None:
            self.__instrument = self.__rm.open_resource(self.__port)
            
            for param, val in self.__resource_params.items():
                setattr(self.__instrument, param, val)
        
        else:
            self.__instrument.open()
            
        return self.id
    
    def disconnect(self):
        """
        Disconnect the resource from the Instrument port
        """
        if self.__instrument is not None:
            self.__instrument.close()
    
    # Read, Write, and Read/Write (query) commands
            
    def write(self, msg):
        """
        Performs a SCPI write operation on the resource
        msg : write value
        """
        if self.__instrument is None:
            raise Exception( 'Can not write, instrument not connected.' )
            return
            
        return self.__instrument.write(msg)
            
            
    def read(self):
        """
        Performs a SCPI read operation on the resource
        """
        if self.__instrument is None:
            raise Exception( 'Can not read, instrument not connected' )
            return
            
        return self.__instrument.read()
    
    
    def query(self, msg):
        """
        Performs a SCPI read/write query operation on the resource
        msg : write value
        ret : read value from resource
        """
        if self.__instrument is None:
            raise Exception( 'Can not query, instrument not connected' )
        
        return self.__instrument.query(msg)
            
    