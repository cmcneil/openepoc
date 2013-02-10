'''Authored by qdot, with changes by cmcneil.'''
import gevent

try:
    import pywinusb.hid as hid

    windows = True
except:
    windows = False

import os
from gevent.queue import Queue
from subprocess import check_output
from Crypto.Cipher import AES
from Crypto import Random

sensorBits = {
    'F3': [10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7],
    'FC5': [28, 29, 30, 31, 16, 17, 18, 19, 20, 21, 22, 23, 8, 9],
    'AF3': [46, 47, 32, 33, 34, 35, 36, 37, 38, 39, 24, 25, 26, 27],
    'F7': [48, 49, 50, 51, 52, 53, 54, 55, 40, 41, 42, 43, 44, 45],
    'T7': [66, 67, 68, 69, 70, 71, 56, 57, 58, 59, 60, 61, 62, 63],
    'P7': [84, 85, 86, 87, 72, 73, 74, 75, 76, 77, 78, 79, 64, 65],
    'O1': [102, 103, 88, 89, 90, 91, 92, 93, 94, 95, 80, 81, 82, 83],
    'O2': [140, 141, 142, 143, 128, 129, 130, 131, 132, 133, 134, 135, 120, 121],
    'P8': [158, 159, 144, 145, 146, 147, 148, 149, 150, 151, 136, 137, 138, 139],
    'T8': [160, 161, 162, 163, 164, 165, 166, 167, 152, 153, 154, 155, 156, 157],
    'F8': [178, 179, 180, 181, 182, 183, 168, 169, 170, 171, 172, 173, 174, 175],
    'AF4': [196, 197, 198, 199, 184, 185, 186, 187, 188, 189, 190, 191, 176, 177],
    'FC6': [214, 215, 200, 201, 202, 203, 204, 205, 206, 207, 192, 193, 194, 195],
    'F4': [216, 217, 218, 219, 220, 221, 222, 223, 208, 209, 210, 211, 212, 213]
}
sensor_ord = ['F3', 'FC5', 'AF3', 'F7', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8',
              'F8', 'AF4', 'FC6', 'F4', 'F8', 'AF4', 'F3', 'FC5', 'AF3']
quality_bits = [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112]

# These specify what percentages the battery bits signify. The first value
# is for 225, and the last is for 248.
# See https://github.com/qdot/emokit/blob/master/doc/emotiv_protocol.asciidoc
battery_vals = [0, 0.42, 0.88, 1.42, 2.05, 2.80, 3.63, 5.08, 12.37, 20.43,
                32.34, 45.93, 55.37, 61.92, 66.59, 71.54, 76.77, 81.89, 
                85.23, 89.45, 93.40, 97.02, 99.93, 100]

g_battery = 0
tasks = Queue()

class EmotivPacket(object):
    def __init__(self, data, sensors):
        global g_battery
        self.rawData = data
        self.counter = ord(data[0])
        self.battery = g_battery
        if(self.counter > 127):
            self.battery = self.counter
            g_battery = self.battery_percent()
            self.counter = 128
        self.sync = self.counter == 0xe9
        self.gyroX = ord(data[29]) - 106
        self.gyroY = ord(data[30]) - 105
        sensors['X']['value'] = self.gyroX
        sensors['Y']['value'] = self.gyroY
        for name, bits in sensorBits.items():
            value = self.get_level(self.rawData, bits)
            setattr(self, name, (value,))
            sensors[name]['value'] = value
        self.handle_quality(sensors)
        self.sensors = sensors

    def get_level(self, data, bits):
        level = 0
        for i in range(13, -1, -1):
            level <<= 1
            b, o = (bits[i] / 8) + 1, bits[i] % 8
            level |= (ord(data[b]) >> o) & 1
        return level

    def handle_quality(self, sensors):
        current_contact_quality = self.get_level(self.rawData, quality_bits) / 540
        sensor = ord(self.rawData[0])

        # Note: we currently don't know what the quality bits signal for
        # the sensor code between 16 and 63. Why isn't it the same
        # repeated pattern? According to qdot's docs it isn't.
        if not (16 <= sensor <= 63) and sensor < 127:
            sens_label = sensor_ord[sensor % 16]
            sensors[sens_label]['quality'] = current_contact_quality
        else:
            sensors['Unknown']['quality'] = current_contact_quality
            sensors['Unknown']['value'] = sensor
        return current_contact_quality

    def battery_percent(self):
        if self.battery > 248:
            return 100
        elif self.battery < 225:
            return 0
        else:
            return battery_vals[self.battery - 225]

    def __repr__(self):
        return 'EmotivPacket(counter=%i, battery=%i, gyroX=%i, gyroY=%i, F3=%i)' % (
            self.counter,
            self.battery,
            self.gyroX,
            self.gyroY,
            self.F3[0],
            )

class Emotiv(object):
    def __init__(self, displayOutput=False, headsetId=0, research_headset=True):
        self._goOn = True
        self.packets = Queue()
        self.packetsReceived = 0
        self.packetsProcessed = 0
        self.battery = 0
        self.displayOutput = displayOutput
        self.headsetId = headsetId
        self.research_headset = research_headset
        self.sensors = {
            'F3': {'value': 0, 'quality': 0},
            'FC6': {'value': 0, 'quality': 0},
            'P7': {'value': 0, 'quality': 0},
            'T8': {'value': 0, 'quality': 0},
            'F7': {'value': 0, 'quality': 0},
            'F8': {'value': 0, 'quality': 0},
            'T7': {'value': 0, 'quality': 0},
            'P8': {'value': 0, 'quality': 0},
            'AF4': {'value': 0, 'quality': 0},
            'F4': {'value': 0, 'quality': 0},
            'AF3': {'value': 0, 'quality': 0},
            'O2': {'value': 0, 'quality': 0},
            'O1': {'value': 0, 'quality': 0},
            'FC5': {'value': 0, 'quality': 0},
            'X': {'value': 0, 'quality': 0},
            'Y': {'value': 0, 'quality': 0},
            'Unknown': {'value': 0, 'quality': 0}
        }

    def setup(self, headsetId=0):
        if windows:
            self.setupWin()
        else:
            self.setupPosix()

    def updateStdout(self):
        while self._goOn:
            if self.displayOutput:
                if windows:
                    os.system('cls')
                else:
                    os.system('clear')
                print "Packets Received: %s Packets Processed: %s" % (self.packetsReceived, self.packetsProcessed)
                print('\n'.join("%s Reading: %s Strength: %s" % (k[1], self.sensors[k[1]]['value'],self.sensors[k[1]]['quality']) for k in enumerate(self.sensors)))
                print "Battery: %i" % g_battery
            gevent.sleep(1)

    def getLinuxSetup(self):
        rawinputs = []
        for filename in os.listdir("/sys/class/hidraw"):
            realInputPath = check_output(["realpath", "/sys/class/hidraw/" + filename])
            sPaths = realInputPath.split('/')
            s = len(sPaths)
            s = s - 4
            i = 0
            path = ""
            while s > i:
                path = path + sPaths[i] + "/"
                i += 1
            rawinputs.append([path, filename])
        hiddevices = []
        #TODO: Add support for multiple USB sticks? make a bit more elegant
        for input in rawinputs:
            try:
                with open(input[0] + "/manufacturer", 'r') as f:
                    manufacturer = f.readline()
                    f.close()
                if "Emotiv Systems Inc." in manufacturer:
                    with open(input[0] + "/serial", 'r') as f:
                        serial = f.readline().strip()
                        f.close()
                    print "Serial: " + serial + " Device: " + input[1]
                    #Great we found it. But we need to use the second one...
                    hidraw = input[1]
                    id_hidraw = int(hidraw[-1])
                    #The dev headset might use the first device, or maybe if more than one are connected they might.
                    id_hidraw += 1
                    hidraw = "hidraw" + id_hidraw.__str__()
                    print "Serial: " + serial + " Device: " + hidraw + " (Active)"
                    return [serial, hidraw, ]
            except IOError as e:
                print "Couldn't open file: %s" % e

    def setupWin(self):
        devices = []
        try:
            for device in hid.find_all_hid_devices():
                if device.vendor_id != 0x21A1:
                    continue
                if device.product_name == 'Brain Waves':
                    devices.append(device)
                    device.open()
                    self.serialNum = device.serial_number
                    device.set_raw_data_handler(self.handler)
                elif device.product_name == 'EPOC BCI':
                    devices.append(device)
                    device.open()
                    self.serialNum = device.serial_number
                    device.set_raw_data_handler(self.handler)
                elif device.product_name == '00000000000':
                    devices.append(device)
                    device.open()
                    self.serialNum = device.serial_number
                    device.set_raw_data_handler(self.handler)
            gevent.spawn(self.setupCrypto, self.serialNum)
            gevent.spawn(self.updateStdout)
            while self._goOn:
                try:
                    gevent.sleep(0)
                except KeyboardInterrupt:
                    self._goOn = False
                    for device in devices:
                        device.close()
        finally:
            for device in devices:
                device.close()

    def handler(self, data):
        assert data[0] == 0
        tasks.put_nowait(''.join(map(chr, data[1:])))
        self.packetsReceived += 1
        return True

    def setupPosix(self):
        _os_decryption = False
        if os.path.exists('/dev/eeg/raw'):
            #The decrpytion is handled by the Linux epoc daemon. We don't need to handle it there.
            _os_decryption = True
            self.hidraw = open("/dev/eeg/raw")
        else:
            setup = self.getLinuxSetup()
            self.serialNum = setup[0]
            if os.path.exists("/dev/" + setup[1]):
                self.hidraw = open("/dev/" + setup[1])
            else:
                self.hidraw = open("/dev/hidraw4")
            gevent.spawn(self.setupCrypto, self.serialNum)
            gevent.spawn(self.updateStdout)
        while self._goOn:
            try:
                data = self.hidraw.read(32)
                if data != "":
                    if _os_decryption:
                        self.packets.put_nowait(EmotivPacket(data))
                    else:
                        #Queue it!
                        self.packetsReceived += 1
                        tasks.put_nowait(data)
                        gevent.sleep(0)
            except KeyboardInterrupt:
                self._goOn = False
        return True

    def setupCrypto(self, sn):
        type = 0 #feature[5]
        type &= 0xF
        type = 0
        #I believe type == True is for the Dev headset, I'm not using that. That's the point of this library in the first place I thought.
        k = ['\0'] * 16
        k[0] = sn[-1]
        k[1] = '\0'
        k[2] = sn[-2]
        if type:
            k[3] = 'H'
            k[4] = sn[-1]
            k[5] = '\0'
            k[6] = sn[-2]
            k[7] = 'T'
            k[8] = sn[-3]
            k[9] = '\x10'
            k[10] = sn[-4]
            k[11] = 'B'
        else:
            k[3] = 'T'
            k[4] = sn[-3]
            k[5] = '\x10'
            k[6] = sn[-4]
            k[7] = 'B'
            k[8] = sn[-1]
            k[9] = '\0'
            k[10] = sn[-2]
            k[11] = 'H'
        k[12] = sn[-3]
        k[13] = '\0'
        k[14] = sn[-4]
        k[15] = 'P'
        #It doesn't make sense to have more than one greenlet handling this as data needs to be in order anyhow. I guess you could assign an ID or something
        #to each packet but that seems like a waste also or is it? The ID might be useful if your using multiple headsets or usb sticks.
        key = ''.join(k)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_ECB, iv)
        for i in k: print "0x%.02x " % (ord(i))
        while self._goOn:
            while not tasks.empty():
                task = tasks.get()
                data = cipher.decrypt(task[:16]) + cipher.decrypt(task[16:])
                self.lastPacket = EmotivPacket(data, self.sensors)
                self.packets.put_nowait(self.lastPacket)
                self.packetsProcessed += 1
                gevent.sleep(0)
            gevent.sleep(0)

    def dequeue(self):
        try:
            return self.packets.get()
        except Exception, e:
            print e

    def close(self):
        if windows:
            self.device.close()
        else:
            self._goOn = False
            self.hidraw.close()

if __name__ == "__main__":
    try:
        a = Emotiv()
        a.setup()
    except KeyboardInterrupt:
        a.close()
        gevent.shutdown()


