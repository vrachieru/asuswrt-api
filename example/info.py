import sys
sys.path.append('../')

from asuswrt import AsusWRT

router = AsusWRT(url='http://192.168.1.1', username='admin', password='admin')
sys = router.get_sys_info()

print('Model: %s' % sys['model'])
print('Firmware: %s' % sys['firmware'])
