class StringMixin(object):
    def __repr__(self):
        classname  = self.__class__.__name__
        attributes = ', '.join('%s: %s' % item for item in sorted(vars(self).items()))
        return '%s { %s }' % (classname, attributes)

class Client(StringMixin):
    def __init__(self, data):
        self.mac = data.get('mac')
        self.ip = data.get('ip')
        self.interface = data.get('interface', 'wired')
        self.rssi = data.get('rssi')
        self.name = data.get('name')
        self.alias = data.get('alias')