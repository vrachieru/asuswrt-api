import sys
sys.path.append('../')

from asuswrt import AsusWRT

router = AsusWRT(url='http://192.168.1.1', username='admin', password='admin')
clients = router.get_online_clients()

for client in clients:
    for attribute in ['name', 'alias', 'mac', 'ip', 'interface', 'rssi']:
        print('%s: %s' % (attribute.capitalize(), getattr(client, attribute)))
    print()