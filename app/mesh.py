# encoding=utf-8
import serial
import binascii
import glob
import time

meshHexStatic = {
    
    "HEADER" : binascii.a2b_hex("AA"),
    "END" : binascii.a2b_hex("55"),
# RegAddr
    "WR_GW_ADV": binascii.a2b_hex("D2"),
    "IN_DATA_1" : binascii.a2b_hex("70"),
    "INDEX" :  binascii.a2b_hex("A1"),
    "INDEX_CLR" : binascii.a2b_hex("A2"),

# Procedure 
    "NONE": binascii.a2b_hex("00"),
    "UPDATE": binascii.a2b_hex("01"),
    "P_INDEX": binascii.a2b_hex("04"),
    "IN_DATA": binascii.a2b_hex("05"),
    "INDEX_CLEAR"  : binascii.a2b_hex("06"), 

# FrameType
    "READ_REGISTER": binascii.a2b_hex("00"),
    "WRITE_REGISTER": binascii.a2b_hex("01"),
    "UPDATE_REGISTER": binascii.a2b_hex("02"),
    "ERROR": binascii.a2b_hex("03"),
    "WAKEUP": binascii.a2b_hex("04")
    }
procedureNum = binascii.a2b_hex("00")
maxConnect = 10
meshData = {
    "num" : 0,
    "enable" : [False] *  10,
    "nodeId": [binascii.a2b_hex("FF")] *  10,
    "time" : [""] *  10,
    "groupId": [0] *  10,
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

header = False
# sensor = '/dev/ttyUSB0'

def scan():
    return glob.glob('/dev/ttyUSB*')

def Make_TxFrame(inBuf):
    outBuf = [binascii.a2b_hex("FF")] *  (20 + len(inBuf))
    outBuf[16] = meshHexStatic["HEADER"]
    outBuf[17] = meshHexStatic["HEADER"]
    for x in xrange(0,len(inBuf)):
        outBuf[x +18] = inBuf[x]
    outBuf[len(inBuf) + 18] = meshHexStatic["END"]
    outBuf[len(inBuf) + 19] = meshHexStatic["END"]
    return outBuf

def Cmd_ReadRegister(addr):
    inBuf = [binascii.a2b_hex("FF")] * 2
    outBuf = [binascii.a2b_hex("FF")] * 22
    inBuf[0] = binascii.a2b_hex("00")
    inBuf[1] = addr
    outBuf = Make_TxFrame(inBuf)
    return outBuf

def Cmd_WriteRegister(addr, data):
    inBuf = [binascii.a2b_hex("FF")] * (len(data) + 4)
    outBuf = [binascii.a2b_hex("FF")] *  (20 + len(data) + 4)
    dataLen16 = hex(len(data))
    inBuf[0] = meshHexStatic["WRITE_REGISTER"]
    inBuf[1] = addr
    inBuf[2] = chr(len(data) & 0x00FF)
    inBuf[3] = chr(((len(data) >> 8) & 0x00FF))
    for x in xrange(0, len(data)):
        inBuf[x + 4] = data[x]
    outBuf = Make_TxFrame(inBuf)
    return outBuf;

def Tx_GwStart():
    txBuf = [binascii.a2b_hex("FF")] * 25
    data = binascii.a2b_hex("01")
    txBuf = Cmd_WriteRegister(meshHexStatic["WR_GW_ADV"] , data)
    meshser.write(bytearray(txBuf))
    print "Gate Way Start"

def Tx_ReadIndex():
    txBuf = [binascii.a2b_hex("FF")] * 22
    txBuf = Cmd_ReadRegister(meshHexStatic["INDEX"])
    meshser.write(bytearray(txBuf))
    print "read index"

def Tx_ReadInData(reg):
    txBuf = [binascii.a2b_hex("FF")] * 22
    txBuf = Cmd_ReadRegister(ord(meshHexStatic["IN_DATA_1"]) + reg -1)
    meshser.write((bytearray(txBuf)))
    print "read in-data"

def Tx_WriteIndexClear():
    txBuf = [binascii.a2b_hex("FF")] * 26
    data = [binascii.a2b_hex("FF"), binascii.a2b_hex("FE")]
    txBuf = Cmd_WriteRegister(meshHexStatic["INDEX_CLR"], data)
    meshser.write((bytearray(txBuf)))
    print "clear index"

def meshDataReceived():
    global procedureNum
    rxBuf = [binascii.a2b_hex("FF")] * 255
    count = 0;
    lenBuf = 2;
    timeout = False;
    header = False;
    end = False;
    cmd = 0
    rxBuf[0] = meshser.read(1)
    rxBuf[1] = meshser.read(1)

    # if meshser.inWaiting() > 4:

    if ((rxBuf[0] == meshHexStatic["HEADER"]) and (rxBuf[1] == meshHexStatic["HEADER"])):
        header = True

    if header == True:
        while timeout == False:
            while meshser.inWaiting() < 1:
                if count < 10000:
                    count = count + 1
                else:
                    timeout = True;
                    break
            if timeout == True:
                print "time out"
                break
            else:
                if lenBuf +1 >= len(rxBuf):
                    rxBuf.append(binascii.a2b_hex("FF"))
                rxBuf[lenBuf] = meshser.read(1);
                lenBuf = lenBuf + 1

        if (rxBuf[lenBuf - 2] == meshHexStatic["END"]) and (rxBuf[lenBuf - 1] == meshHexStatic["END"]):
            end = True

    if header == True and end == True:

        cmd = rxBuf[2]
        reg = rxBuf[3]

        if cmd == meshHexStatic["READ_REGISTER"]:
            # 読込応答
            print "Read Register"
            if reg == meshHexStatic["INDEX"]:
                procedureNum =  meshHexStatic["IN_DATA"]
                return [None, procedureNum]
            elif reg == meshHexStatic["IN_DATA_1"]:
                procedureNum = meshHexStatic["INDEX_CLEAR"]

                if ord(rxBuf[4]) != 50:
                    print "Data empty, read again"
                    procedureNum =  meshHexStatic["IN_DATA"]
                    return [None, procedureNum]
                addr = ord(rxBuf[11]) << 24 + ord(rxBuf[10]) << 16 +  ord(rxBuf[9]) << 8 + ord(rxBuf[8])
                flag = False
                for x in xrange(0, maxConnect):
                    if meshData["enable"][x] == True:
                        if addr == meshData["nodeId"][x]:
                            flag = True
                            meshData["num"]  = x
                if flag == False:
                    for x in xrange(0, maxConnect):
                        if meshData["enable"][x] == False:
                            meshData["num"] = x
                            meshData["enable"][x] == True
                            meshData["nodeId"][x] = addr
                            break

                meshData["time"][meshData["num"]] = time.strftime("%Y-%m-%d %H:%M:%S")
                meshData["groupId"][meshData["num"]] = ord(rxBuf[7]) << 8 + ord(rxBuf[6])
                meshData["cmd"][meshData["num"]] = ord(rxBuf[12])
                meshData["seqNum"][meshData["num"]] = ord(rxBuf[13])
                meshData["status"][meshData["num"]] = ord(rxBuf[15]) << 8 + ord(rxBuf[14])
                meshData["temp"][meshData["num"]] = float(((ord(rxBuf[17]) << 8) + ord(rxBuf[16]))) * 0.01
                meshData["humi"][meshData["num"]] = float(((ord(rxBuf[19]) << 8) + ord(rxBuf[18]))) * 0.01
                meshData["light"][meshData["num"]] = float((ord(rxBuf[21]) << 8) + ord(rxBuf[20]))
                meshData["press"][meshData["num"]] = float(((ord(rxBuf[24]) << 16) + (ord(rxBuf[23]) << 8) + ord(rxBuf[22]))) * 0.01
                meshData["sound"][meshData["num"]] = float(((ord(rxBuf[26]) << 8) + ord(rxBuf[25]))) * 0.01
                meshData["bat"][meshData["num"]] = float(((ord(rxBuf[54]) << 8) + ord(rxBuf[53]))) * 0.01

                sensorData = {
                    "time" : meshData["time"][meshData["num"]],
                    "groupId": meshData["groupId"][meshData["num"]],
                    "nodeId": meshData["nodeId"][meshData["num"]],
                    "cmd": meshData["cmd"][meshData["num"]],
                    "seqNum": meshData["seqNum"][meshData["num"]],
                    "status": meshData["status"][meshData["num"]],
                    "temp": meshData["temp"][meshData["num"]],
                    "humi": meshData["humi"][meshData["num"]],
                    "light": meshData["light"][meshData["num"]],
                    "press": meshData["press"][meshData["num"]],
                    "sound": meshData["sound"][meshData["num"]],
                    "bat": meshData["bat"][meshData["num"]]
                }
                # senList[meshData["num"]] = sensorData
                # print sensorData
                return [sensorData, procedureNum]

        elif cmd == meshHexStatic["WRITE_REGISTER"]:
            print "write cmd"
            if reg == meshHexStatic["INDEX_CLR"]:
                procedureNum = meshHexStatic["NONE"]
            return [None, procedureNum]
        elif cmd == meshHexStatic["UPDATE_REGISTER"]:
            print "update cmd"
            procedureNum = meshHexStatic["P_INDEX"]
            return [None, procedureNum]
        elif cmd == meshHexStatic["ERROR"]:
            print "error cmd"
            return [None, procedureNum]
        elif cmd == meshHexStatic["WAKEUP"]:
            print "wake up cmd"
            return [None, meshHexStatic["NONE"]]
        else:
            print "read failed"
            return [None, procedureNum]

def startMesh():
    global procedureNum
    result = meshDataReceived()
    meshList = None
    if result != None:
        meshList = result[0]
        procedureNum = result[1]
    if procedureNum == meshHexStatic["P_INDEX"]:
        Tx_ReadIndex()
    elif procedureNum == meshHexStatic["IN_DATA"]:
        Tx_ReadInData(1)
    elif procedureNum == meshHexStatic["INDEX_CLEAR"]:
        Tx_WriteIndexClear()
        if meshList != None:
            return meshList
    time.sleep(3)
    # else:
    #     Tx_WriteIndexClear()

sensors = scan()
if len(sensors) > 0:
    sensor = sensors[0]
    meshser = serial.Serial(sensor, 9600, timeout=None)

    # seq = map(ord, rxBuf)
    # print seq


# Tx_GwStart()
# while  True:
#     time.sleep(1)
#     result = meshDataReceived()
#     if result != None:
#         meshList = result[0]
#         procedureNum = result[1]
#     if procedureNum == meshHexStatic["P_INDEX"]:
#         Tx_ReadIndex()
#         continue
#     elif procedureNum == meshHexStatic["IN_DATA"]:
#         Tx_ReadInData(1)
#         continue
#     elif procedureNum == meshHexStatic["INDEX_CLEAR"]:
#         print meshList
#         Tx_WriteIndexClear()
#         time.sleep(5)
#         continue
