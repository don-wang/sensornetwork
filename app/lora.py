# encoding=utf-8
import serial
import binascii
import glob
import time

loraHexStatic = {

    "ASCII_Next": binascii.a2b_hex("3E"),
    "ASCII_EX_MARK": binascii.a2b_hex("21"),
    "ASCII_t": binascii.a2b_hex("74"),
    "ASCII_SP": binascii.a2b_hex("20"),
    "ASCII_EQ": binascii.a2b_hex("3D"),
    "ASCII_LF": binascii.a2b_hex("0A"),
    "ASCII_CR": binascii.a2b_hex("0D"),
    "ASCII_COMMA": binascii.a2b_hex("2C"),

    }

loraData = {
    "num" : 0,
    "enable" : [False] *  10,
    "rssi": [0] *  10,
    "groupId": [0] *  10,
    "nodeId": [binascii.a2b_hex("FF")] *  10,
    "time" : [""] *  10,
    "seqNum": [0] *  10,
    "cmd": [0] *  10,
    "status": [binascii.a2b_hex("FF")] *  10,
    "temp": [0] *  10,
    "humi": [0] *  10,
    "light": [0] *  10,
    "press": [0] *  10,
    "sound": [0] *  10,
    "bat": [0] *  10
}
sensorData = {}
logFlag = False
initFlag = False
# sensor = '/dev/ttyUSB0'

def scan():
    return glob.glob('/dev/ttyUSB*')

def tsbCmdI_Click():
    print "send i"
    loraser.write("i")

def tsbStart_Click():
    print "send start"
    loraser.write("s");

def tsbCmd1_Click():
    print "send 1"
    txBufLoRa = [binascii.a2b_hex("31"), binascii.a2b_hex("0D")]
    loraser.write(bytearray(txBufLoRa))


def loRaDataReceived():
    global logFlag, initFlag, sensorData
    rxBufLoRa = [binascii.a2b_hex("FF")] * 2000
    count = 0
    lenBuf = 0
    logStringData2 = ""
    timeout = False
    while timeout == False:
        count = 0
        while loraser.inWaiting()  < 1:
            if count < 10000:
                count = count + 1
            else:
                timeout = True;
                break
        if timeout == True:
            break
        else:
            if lenBuf + 1 >= len(rxBufLoRa):
                # rxBufLoRa.pop(0)
                rxBufLoRa.append([binascii.a2b_hex("FF")])
                # lenBuf = lenBuf -1
            rxBufLoRa[lenBuf] = loraser.read(1);
            lenBuf = lenBuf + 1

    if lenBuf > 4:

        if initFlag == False:
            if rxBufLoRa[lenBuf -1] == loraHexStatic["ASCII_Next"]:
                if rxBufLoRa[lenBuf - 3] == loraHexStatic["ASCII_EX_MARK"]:
                    logStringData1 = rxBufLoRa[(lenBuf - 16):]
                    logStringData2 = "Initial Messege over, waiting for command";
                    logFlag = True
                elif rxBufLoRa[lenBuf - 3] == loraHexStatic["ASCII_t"]:
                    logStringData1 = rxBufLoRa[(lenBuf - 14):]
                    logStringData2 = "waiting for command"
                    logFlag = True
                else:
                    pass

            elif rxBufLoRa[lenBuf -1] == loraHexStatic["ASCII_SP"]:
                if rxBufLoRa[lenBuf - 2] == loraHexStatic["ASCII_EQ"]:
                    logStringData1 = rxBufLoRa[5:(lenBuf - 3 + 5)]
                    logStringData2 = "querying"
                    logFlag = True
                else:
                    pass
            elif rxBufLoRa[lenBuf -1] == loraHexStatic["ASCII_LF"]:
                if rxBufLoRa[lenBuf - 2] == loraHexStatic["ASCII_CR"]:
                    logStringData1 = rxBufLoRa[(lenBuf-10): lenBuf-10 + 6]
                    logStringData2 = "System Start"
                    initFlag = True
                else:
                    pass
        else:
            loraData["num"] = 0
            rssiString = ""
            if rxBufLoRa[3] == loraHexStatic["ASCII_COMMA"]:
                loraData["time"][loraData["num"]] = time.strftime("%Y-%m-%d %H:%M:%S")
                rssiString = rxBufLoRa[0:3]
                # seq = map(ord, rssiString)
                # rssiString = ''.join(chr(i) for i in seq)
                # loraData["rssi"][loraData["num"]] = int(rssiString)
                loraData["groupId"][loraData["num"]] = ord(rxBufLoRa[5]) << 8 + ord(rxBufLoRa[4])
                loraData["nodeId"][loraData["num"]] = ord(rxBufLoRa[9]) << 24 + ord(rxBufLoRa[8]) << 16 +  ord(rxBufLoRa[7]) << 8 + ord(rxBufLoRa[6])
                loraData["cmd"][loraData["num"]] = ord(rxBufLoRa[10])
                loraData["seqNum"][loraData["num"]] = ord(rxBufLoRa[11])
                loraData["status"][loraData["num"]] = ord(rxBufLoRa[13]) << 8 + ord(rxBufLoRa[12])
                loraData["temp"][loraData["num"]] = float(((ord(rxBufLoRa[15]) << 8) + ord(rxBufLoRa[14]))) * 0.01
                loraData["humi"][loraData["num"]] = float(((ord(rxBufLoRa[17]) << 8) + ord(rxBufLoRa[16]))) * 0.01
                loraData["light"][loraData["num"]] = float((ord(rxBufLoRa[19]) << 8) + ord(rxBufLoRa[18]))
                loraData["press"][loraData["num"]] = float(((ord(rxBufLoRa[22]) << 16) + (ord(rxBufLoRa[21]) << 8) + ord(rxBufLoRa[20]))) * 0.01
                loraData["sound"][loraData["num"]] = float(((ord(rxBufLoRa[24]) << 8) + ord(rxBufLoRa[23]))) * 0.01
                loraData["bat"][loraData["num"]] = float(((ord(rxBufLoRa[52]) << 8) + ord(rxBufLoRa[51]))) * 0.01
            else:
                loraData["time"][loraData["num"]] = time.strftime("%Y-%m-%d %H:%M:%S")
                rssiString = rxBufLoRa[0:4]
                # seq = map(ord, rssiString)
                # rssiString = ''.join(chr(i) for i in seq)
                # loraData["rssi"][loraData["num"]] = int(rssiString)
                loraData["groupId"][loraData["num"]] = ord(rxBufLoRa[6]) << 8 + ord(rxBufLoRa[5])
                loraData["nodeId"][loraData["num"]] = ord(rxBufLoRa[10]) << 24 + ord(rxBufLoRa[9]) << 16 +  ord(rxBufLoRa[8]) << 8 + ord(rxBufLoRa[7])
                loraData["cmd"][loraData["num"]] = ord(rxBufLoRa[11])
                loraData["seqNum"][loraData["num"]] = ord(rxBufLoRa[12])
                loraData["status"][loraData["num"]] = ord(rxBufLoRa[14]) << 8 + ord(rxBufLoRa[13])
                loraData["temp"][loraData["num"]] = float(((ord(rxBufLoRa[16]) << 8) + ord(rxBufLoRa[15]))) * 0.01
                loraData["humi"][loraData["num"]] = float(((ord(rxBufLoRa[18]) << 8) + ord(rxBufLoRa[17]))) * 0.01
                loraData["light"][loraData["num"]] = float((ord(rxBufLoRa[20]) << 8) + ord(rxBufLoRa[19]))
                loraData["press"][loraData["num"]] = float(((ord(rxBufLoRa[23]) << 16) + (ord(rxBufLoRa[22]) << 8) + ord(rxBufLoRa[21]))) * 0.01
                loraData["sound"][loraData["num"]] = float(((ord(rxBufLoRa[25]) << 8) + ord(rxBufLoRa[24]))) * 0.01
                loraData["bat"][loraData["num"]] = float(((ord(rxBufLoRa[53]) << 8) + ord(rxBufLoRa[52]))) * 0.01

            logStringData1 = ""
            logStringData2 = "receiving data"
            logFlag = True
            dgvFlag = True

            sensorData = {
                "time" : loraData["time"][loraData["num"]],
                "groupId": loraData["groupId"][loraData["num"]],
                "nodeId": loraData["nodeId"][loraData["num"]],
                "cmd": loraData["cmd"][loraData["num"]],
                "seqNum": loraData["seqNum"][loraData["num"]],
                "status": loraData["status"][loraData["num"]],
                "temp": loraData["temp"][loraData["num"]],
                "humi": loraData["humi"][loraData["num"]],
                "light": loraData["light"][loraData["num"]],
                "press": loraData["press"][loraData["num"]],
                "sound": loraData["sound"][loraData["num"]],
                "bat": loraData["bat"][loraData["num"]]
            }
            # senList[Data["num"]] = sensorData
            # print senList
        print logStringData2
        return sensorData

def startLoRa():
    global sensorData
    print "please press reset button"
    while logFlag == False:
        loRaDataReceived()
        time.sleep(1)

    tsbCmdI_Click()
    loRaDataReceived()
    time.sleep(1)
    tsbCmd1_Click()
    loRaDataReceived()
    time.sleep(1)
    tsbStart_Click()
    loRaDataReceived()
    time.sleep(1)

sensors = scan()
if len(sensors) > 0:
    sensor = sensors[0]
    loraser = serial.Serial(sensor, 115200, timeout=None)
# sensor = scan()[0]


# print "please press reset button"
# while logFlag == False:
#     print "not yet"
#     dataReceived()
#     time.sleep(1)

# tsbCmdI_Click()
# dataReceived()
# time.sleep(1)
# tsbCmd1_Click()
# dataReceived()
# time.sleep(1)
# tsbStart_Click()
# dataReceived()
# time.sleep(1)
# while True:
#     dataReceived()
# rcv = loraser.read(10)
# print rcv
# seq = map(ord, rcv)
# print seq
