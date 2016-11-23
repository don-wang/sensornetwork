# encoding=utf-8
from flask import render_template, session, jsonify, request
from flask import copy_current_request_context
from flask_socketio import emit
from app import app, socketio
# from app import socketio
from threading import Thread, current_thread
import csv
# import binascii
import datetime
import time

import json
import glob

# import converter
from converter import *
from ble import *
from mesh import *
from lora import *

# def scan():
#     return glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')

# sensor = '/dev/ttyUSB0'
clients = 0
fileList = []
senList = {}
oldData = {}
sensorConf = {""}
seqNums = [None] * 10
# choose from BLE, Mesh, LoRa, Test
module = "BLE"
# Data format
                # "time" : Data["time"][Data["num"]],
                # "groupId": Data["groupId"][Data["num"]],
                # "cmd": Data["cmd"][Data["num"]],
                # "seqNum": Data["seqNum"][Data["num"]],
                # "status": Data["status"][Data["num"]],
                # "temp": Data["temp"][Data["num"]],
                # "humi": Data["humi"][Data["num"]],
                # "light": Data["light"][Data["num"]],
                # "press": Data["press"][Data["num"]],
                # "sound": Data["sound"][Data["num"]],
                # "bat": Data["bat"][Data["num"]]
def scan():
    return glob.glob('/dev/ttyUSB*')

def listening():
    # global newTask
    while True:
        dataSet = []

        if module == "BLE":

            node = 0
            returnedList = getBLEData()
            for sensors in returnedList:
                if sensors.btAddress == "EBF78C6BC38E":
                    node=1
                elif sensors.btAddress == "E2068C2BFF0C":
                    node=2
                elif sensors.btAddress == "DDBAB3016E8C":
                    node=3
                elif sensors.btAddress == "F8290B7902A5":
                    node=4
                elif sensors.btAddress == "C35799CED2EA":
                    node=5
                else:
                    break
                if seqNums[node] == sensors.seqNum:
                    print "repeated data, skip"
                    break
                elif seqNums[node] == None:
                    seqNums[node] = sensors.seqNum
                    print seqNums
                else:
                    seqNums[node] = sensors.seqNum

                sensorData = {
                    "time" : time.strftime("%Y-%m-%d %H:%M:%S"),
                    "groupId": sensors.gateway,
                    "nodeId": node,
                    "cmd": sensors.btAddress,
                    "seqNum": sensors.seqNum,
                    "status": sensors.flag_active,
                    "temp": sensors.val_temp,
                    "humi": sensors.val_humi,
                    "light": sensors.val_light,
                    "press": sensors.val_pressure,
                    "sound": sensors.val_noise,
                    "bat": sensors.val_battery
                }
                print sensorData

                socketio.emit('senList', json.dumps(sensorData), namespace='/main')
                socketio.emit('senList', json.dumps(sensorData), namespace='/node1')
                socketio.emit('senList', json.dumps(sensorData), namespace='/node3')
                socketio.emit('senList', json.dumps(sensorData), namespace='/node5')

                f = open('./ble.txt', 'a')
                f.write(json.dumps(sensorData) + '\n')
                f.close()

            time.sleep(1)
                # if sensors.btAddress != "EBF78C6BC38E" and sensors.btAddress != "DDBAB3016E8C" and sensors.btAddress != "C35799CED2EA" and sensors.btAddress !="E2068C2BFF0C" and sensors.btAddress != "F8290B7902A5":
                #     print sensors.btAddress
                #     print "not required sensor, pass"
                #     continue

                # sample = {"btAddress": sensors.btAddress, "id": "node" + str(node)}
                # if senList.has_key(sensors.btAddress) == False:                
                #     senList[sensors.btAddress] = sample
                #     namespace = "node" + str(node)
                #     seqNums[sensors.btAddress] = sensors.seqNum;

                #     f = open('./'+ sensors.btAddress +'.csv', 'a')
                #     writer = csv.writer(f, lineterminator='\n')
                #     line = ["'distance': "+ str(sensors.distance), "'val_pressure': "+ str(sensors.val_pressure) ," 'tick_register': " +str(sensors.tick_register) + " , 'seqNum':" +str(sensors.seqNum) ," 'val_di': " +str(sensors.val_di) ," 'val_ay': " +str(sensors.val_ay) ," 'val_ax': " + str(sensors.val_ax) ," 'val_heat': " +str(sensors.val_heat) ," 'val_humi': " +str(sensors.val_humi) ," 'sensor_type': '" +str(sensors.sensor_type) + "', 'btAddress': '" +str(sensors.btAddress) + "', 'val_battery': " +str(sensors.val_battery) ," 'val_light': " +str(sensors.val_light) ," 'gateway': '" +str(sensors.gateway) + "', 'rssi': " +str(sensors.rssi) ," 'flag_active': " +str(sensors.flag_active) ," 'val_az': " +str(sensors.val_az) ," 'val_temp': " +str(sensors.val_temp) ," 'val_noise': " +str(sensors.val_noise) ," 'tick_last_update': '" +str(sensors.tick_last_update) + "', 'val_uv': " +str(sensors.val_uv)]         
                #     lineData = {'distance':  str(sensors.distance), 'val_pressure':  str(sensors.val_pressure) , 'tick_register': str(sensors.tick_register) , 'seqNum': str(sensors.seqNum) , 'val_di': str(sensors.val_di) , 'val_ay': str(sensors.val_ay) , 'val_ax':  str(sensors.val_ax) , 'val_heat': str(sensors.val_heat) , 'val_humi': str(sensors.val_humi) , 'sensor_type': str(sensors.sensor_type), 'btAddress': str(sensors.btAddress), 'val_battery': str(sensors.val_battery) , 'val_light': str(sensors.val_light) , 'gateway': str(sensors.gateway), 'rssi': str(sensors.rssi) , 'flag_active': str(sensors.flag_active) , 'val_az': str(sensors.val_az) , 'val_temp': str(sensors.val_temp) , 'val_noise': str(sensors.val_noise) , 'tick_last_update': str(sensors.tick_last_update), 'val_uv': str(sensors.val_uv)}
                #     # line = json.dumps(sensors.__dict__)
                #     senList[sensors.btAddress]['data'] = json.dumps(lineData)
                #     oldData[sensors.btAddress] = lineData
                #     print line

                #     writer.writerow(line)
                #     f.close()
                #     print "new sensor data added"


                # else:
                #     namespace = senList[sensors.btAddress]['id']

                #     if seqNums[sensors.btAddress] != sensors.seqNum:
                #         seqNums[sensors.btAddress] = sensors.seqNum;
                #         f = open('./'+ sensors.btAddress +'.csv', 'a')
                #         writer = csv.writer(f, lineterminator='\n')
                #         line = ["'distance': "+ str(sensors.distance), "'val_pressure': "+ str(sensors.val_pressure) ," 'tick_register': " +str(sensors.tick_register) + " , 'seqNum':" +str(sensors.seqNum) ," 'val_di': " +str(sensors.val_di) ," 'val_ay': " +str(sensors.val_ay) ," 'val_ax': " + str(sensors.val_ax) ," 'val_heat': " +str(sensors.val_heat) ," 'val_humi': " +str(sensors.val_humi) ," 'sensor_type': '" +str(sensors.sensor_type) + "', 'btAddress': '" +str(sensors.btAddress) + "', 'val_battery': " +str(sensors.val_battery) ," 'val_light': " +str(sensors.val_light) ," 'gateway': '" +str(sensors.gateway) + "', 'rssi': " +str(sensors.rssi) ," 'flag_active': " +str(sensors.flag_active) ," 'val_az': " +str(sensors.val_az) ," 'val_temp': " +str(sensors.val_temp) ," 'val_noise': " +str(sensors.val_noise) ," 'tick_last_update': '" +str(sensors.tick_last_update) + "', 'val_uv': " +str(sensors.val_uv)]  
                #         lineData = {'distance':  str(sensors.distance), 'val_pressure':  str(sensors.val_pressure) , 'tick_register': str(sensors.tick_register) , 'seqNum': str(sensors.seqNum) , 'val_di': str(sensors.val_di) , 'val_ay': str(sensors.val_ay) , 'val_ax':  str(sensors.val_ax) , 'val_heat': str(sensors.val_heat) , 'val_humi': str(sensors.val_humi) , 'sensor_type': str(sensors.sensor_type), 'btAddress': str(sensors.btAddress), 'val_battery': str(sensors.val_battery) , 'val_light': str(sensors.val_light) , 'gateway': str(sensors.gateway), 'rssi': str(sensors.rssi) , 'flag_active': str(sensors.flag_active) , 'val_az': str(sensors.val_az) , 'val_temp': str(sensors.val_temp) , 'val_noise': str(sensors.val_noise) , 'tick_last_update': str(sensors.tick_last_update), 'val_uv': str(sensors.val_uv)}
                #         # line = json.dumps(sensors.__dict__)
                #         senList[sensors.btAddress]['data'] = json.dumps(lineData)
                #         oldData[sensors.btAddress] = lineData
                #         print line

                #         writer.writerow(line)
                        
                #         f.close()
                #         print "data updated"

                #     else:
                #         lineData = oldData[sensors.btAddress]
                #         print "data existed"
                #         print namespace

                # socketio.emit('push', json.dumps(lineData), namespace='/node' + str(node))
                # print "--------------------"
                # print "pushed to Namespace: "            
                # print 'node' + str(node)
                # print "--------------------"
                #     # socketio.emit('push', json.dumps(line), namespace='/' + namespace)            
                # # dataSet = {"btAd" : str(sensors.btAddress), "temp": str(sensors.val_temp)}
                # socketio.emit('senList', json.dumps(senList), namespace='/main')
                # print "pushed to main"
                # # socketio.emit('push', json.dumps(senList), namespace='/main')            
                # # senList.append(sample)
                # # print "current light is " + str(sensors.val_light)
                # print "current sequnce is " + str(sensors.seqNum)

        elif module == "Mesh":
            global procedureNum
            global meshList
            sensor = scan()[0]
            meshser = serial.Serial(sensor, 9600, timeout=None)
            time.sleep(3)
            Tx_GwStart()
            while  True:
                meshData = startMesh()
                if meshData != None:
                    print meshData
                    socketio.emit('senList', json.dumps(meshData), namespace='/main')
                    socketio.emit('senList', json.dumps(meshData), namespace='/node1')
                    socketio.emit('senList', json.dumps(meshData), namespace='/node3')
                    socketio.emit('senList', json.dumps(meshData), namespace='/node5')

                    f = open('./mesh.txt', 'a')
                    f.write(json.dumps(sensorData) + '\n')
                    f.close()

        elif module == "LoRa":
            global logFlag
            sensor = scan()[0]
            loraser = serial.Serial(sensor, 115200, timeout=None)
            time.sleep(3)
            startLoRa()
            while True:
                senData = loRaDataReceived()
                if senData != None:
                    print senData

                    socketio.emit('senList', json.dumps(senData), namespace='/main')
                    socketio.emit('senList', json.dumps(senData), namespace='/node1')
                    socketio.emit('senList', json.dumps(senData), namespace='/node3')
                    socketio.emit('senList', json.dumps(senData), namespace='/node5')
                time.sleep(5)



# Open new thread for Listening function
listen = Thread(target=listening,name="ListenSensor")
listen.daemon = True

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
        title = 'Sensing via Web')

@app.route('/setup')
def setup():
    return render_template("setup.html",
        title = 'Setup')

@app.route('/test')
def test():
    return render_template("test.html",
        title = 'Sensors test')

@socketio.on('newName', namespace='/main')
def change(data):
    senList[data['sensor']]['id'] = data['newName']
    print "name changed from " + senList[data['sensor']]['id'] + " to " + data['newName']

@socketio.on('connect', namespace='/node1')
def node1():
    print "start node1"
    print "\n"


@socketio.on('connect', namespace='/node2')
def node2():
    print "start node2"
    pass

@socketio.on('connect', namespace='/node3')
def node3():
    print "start node3"
    print "\n"


@socketio.on('connect', namespace='/node4')
def node4():
    print "start node4"
    pass

@socketio.on('connect', namespace='/node5')
def node5():
    print "start node5"
    print "\n"


@socketio.on('my event')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
        {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my broadcast event')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
        {'data': message['data'], 'count': session['receive_count']},
        broadcast=True)


@socketio.on('connect', namespace='/main')
def connect():
    global clients
    clients += 1
    print clients, "Clients Connected"
    emit('connect',1)
    # Start listening Thread if not exist
    # print listen.isAlive()
    # if listen.isAlive() == False:
    #     listen.start()
    #     print "Start listening to Sensor"
    # else:
    #     print "Listening Thread already started"
    #     emit('status', {'msg': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/main')
def disconnect():
    global clients
    clients -= 1
    if clients == 0:
        print 'No clients now'
    else:
        print 'Client disconnected, remain', clients

@socketio.on("my error event")
def on_my_event(data):
    raise RuntimeError()

@socketio.on_error_default
def default_error_handler(e):
    print(request.event["message"]) # "my error event"
    print(request.event["args"])    # (data,)

time.sleep(1)
listen.start()