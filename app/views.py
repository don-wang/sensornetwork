# encoding=utf-8
from flask import render_template, session, jsonify
from flask import copy_current_request_context
from app import app
from flask_socketio import send, emit
from app import socketio
from threading import Thread, current_thread
import csv
# from lirc.lirc import Lirc
# import binascii
import datetime
import time

import json
import glob

# import converter
from converter import *
from sns import *

# def scan():
#     return glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')

# sensor = '/dev/ttyUSB0'
clients = 0
seqNums = {}
fileList = []
senList = {}
oldData = {}
sensorConf = {""}
# sv = open('./test.csv', 'a')
# writer = csv.writer(sv, lineterminator='\n')
# writer.writerow(["ab",123,"cd"])
# sv.close()
# writer.writerows(array2d)
# data = json.load(data_file, "utf-8")
# newTask = {"update": False}
# Sensor1   ebf78c6bc38e
# Sensor2   e2068c2bff0c
# Sensor3   ddbab3016e8c
# Sensor4   f8290b7902a5
# Sensor5   c113561ce09e
# Sensor6   c35799ced2ea
# [{'distance': 0.07960338788268398, 'val_pressure': 1012.4, 'tick_register': '2016-07-07 17:06:43.626720', 'seqNum': 47, 'val_di': 72.59154084, 'val_ay': 309.8, 'val_ax': -455.1, 'val_heat': 22.523545108041947, 'val_humi': 61.34, 'sensor_type': 'IM', 'btAddress': 'E2068C2BFF0C', 'val_battery': 2910.0, 'val_light': 3, 'gateway': 'creatoPi1', 'rssi': -43, 'flag_active': True, 'val_az': -815.7, 'val_temp': 24.74, 'val_noise': 35.28, 'tick_last_update': '2016-07-07 17:06:43.626720', 'val_uv': 0.02}]
#    flag_active = False
#    sensor_type = SENSOR_TYPE
#    gateway = GATEWAY
def listening():
    # global newTask
    while True:
        node =1
        dataSet = []
        returnedList = getData()
        for sensors in returnedList:
            sample = {"btAddress": sensors.btAddress, "id": "node" + str(node)}
            if senList.has_key(sensors.btAddress) == False:                
                senList[sensors.btAddress] = sample
                namespace = "node" + str(node)
                seqNums[sensors.btAddress] = sensors.seqNum;

                f = open('./'+ sensors.btAddress +'.csv', 'a')
                writer = csv.writer(f, lineterminator='\n')
                line = ["'distance': "+ str(sensors.distance), "'val_pressure': "+ str(sensors.val_pressure) ," 'tick_register': " +str(sensors.tick_register) + " , 'seqNum':" +str(sensors.seqNum) ," 'val_di': " +str(sensors.val_di) ," 'val_ay': " +str(sensors.val_ay) ," 'val_ax': " + str(sensors.val_ax) ," 'val_heat': " +str(sensors.val_heat) ," 'val_humi': " +str(sensors.val_humi) ," 'sensor_type': '" +str(sensors.sensor_type) + "', 'btAddress': '" +str(sensors.btAddress) + "', 'val_battery': " +str(sensors.val_battery) ," 'val_light': " +str(sensors.val_light) ," 'gateway': '" +str(sensors.gateway) + "', 'rssi': " +str(sensors.rssi) ," 'flag_active': " +str(sensors.flag_active) ," 'val_az': " +str(sensors.val_az) ," 'val_temp': " +str(sensors.val_temp) ," 'val_noise': " +str(sensors.val_noise) ," 'tick_last_update': '" +str(sensors.tick_last_update) + "', 'val_uv': " +str(sensors.val_uv)]         
                lineData = {'distance':  str(sensors.distance), 'val_pressure':  str(sensors.val_pressure) , 'tick_register': str(sensors.tick_register) , 'seqNum': str(sensors.seqNum) , 'val_di': str(sensors.val_di) , 'val_ay': str(sensors.val_ay) , 'val_ax':  str(sensors.val_ax) , 'val_heat': str(sensors.val_heat) , 'val_humi': str(sensors.val_humi) , 'sensor_type': str(sensors.sensor_type), 'btAddress': str(sensors.btAddress), 'val_battery': str(sensors.val_battery) , 'val_light': str(sensors.val_light) , 'gateway': str(sensors.gateway), 'rssi': str(sensors.rssi) , 'flag_active': str(sensors.flag_active) , 'val_az': str(sensors.val_az) , 'val_temp': str(sensors.val_temp) , 'val_noise': str(sensors.val_noise) , 'tick_last_update': str(sensors.tick_last_update), 'val_uv': str(sensors.val_uv)}
                # line = json.dumps(sensors.__dict__)
                senList[sensors.btAddress]['data'] = json.dumps(lineData)
                oldData[sensors.btAddress] = lineData
                print line

                writer.writerow(line)
                f.close()
                print "new sensor data added"


            else:
                namespace = senList[sensors.btAddress]['id']

                if seqNums[sensors.btAddress] != sensors.seqNum:
                    seqNums[sensors.btAddress] = sensors.seqNum;
                    f = open('./'+ sensors.btAddress +'.csv', 'a')
                    writer = csv.writer(f, lineterminator='\n')
                    line = ["'distance': "+ str(sensors.distance), "'val_pressure': "+ str(sensors.val_pressure) ," 'tick_register': " +str(sensors.tick_register) + " , 'seqNum':" +str(sensors.seqNum) ," 'val_di': " +str(sensors.val_di) ," 'val_ay': " +str(sensors.val_ay) ," 'val_ax': " + str(sensors.val_ax) ," 'val_heat': " +str(sensors.val_heat) ," 'val_humi': " +str(sensors.val_humi) ," 'sensor_type': '" +str(sensors.sensor_type) + "', 'btAddress': '" +str(sensors.btAddress) + "', 'val_battery': " +str(sensors.val_battery) ," 'val_light': " +str(sensors.val_light) ," 'gateway': '" +str(sensors.gateway) + "', 'rssi': " +str(sensors.rssi) ," 'flag_active': " +str(sensors.flag_active) ," 'val_az': " +str(sensors.val_az) ," 'val_temp': " +str(sensors.val_temp) ," 'val_noise': " +str(sensors.val_noise) ," 'tick_last_update': '" +str(sensors.tick_last_update) + "', 'val_uv': " +str(sensors.val_uv)]  
                    lineData = {'distance':  str(sensors.distance), 'val_pressure':  str(sensors.val_pressure) , 'tick_register': str(sensors.tick_register) , 'seqNum': str(sensors.seqNum) , 'val_di': str(sensors.val_di) , 'val_ay': str(sensors.val_ay) , 'val_ax':  str(sensors.val_ax) , 'val_heat': str(sensors.val_heat) , 'val_humi': str(sensors.val_humi) , 'sensor_type': str(sensors.sensor_type), 'btAddress': str(sensors.btAddress), 'val_battery': str(sensors.val_battery) , 'val_light': str(sensors.val_light) , 'gateway': str(sensors.gateway), 'rssi': str(sensors.rssi) , 'flag_active': str(sensors.flag_active) , 'val_az': str(sensors.val_az) , 'val_temp': str(sensors.val_temp) , 'val_noise': str(sensors.val_noise) , 'tick_last_update': str(sensors.tick_last_update), 'val_uv': str(sensors.val_uv)}
                    # line = json.dumps(sensors.__dict__)
                    senList[sensors.btAddress]['data'] = json.dumps(lineData)
                    oldData[sensors.btAddress] = lineData
                    print line

                    writer.writerow(line)
                    
                    f.close()
                    print "data updated"

                else:
                    lineData = oldData[sensors.btAddress]
                    print "data existed"
                    print namespace



            socketio.emit('push', json.dumps(lineData), namespace='/node' + str(node))
            socketio.emit('newData', json.dumps(lineData), namespace='/main')
            print "--------------------"
            print "pushed to Namespace: "            
            print 'node' + str(node)
            print "--------------------"
            node = node + 1
                # socketio.emit('push', json.dumps(line), namespace='/' + namespace)            
            # dataSet = {"btAd" : str(sensors.btAddress), "temp": str(sensors.val_temp)}
            socketio.emit('senList', json.dumps(senList), namespace='/main')
            # socketio.emit('push', json.dumps(senList), namespace='/main')            
            # senList.append(sample)
            # print "current light is " + str(sensors.val_light)
            print "current sequnce is " + str(sensors.seqNum)

            # time.sleep(1.5)




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
    pass

@socketio.on('connect', namespace='/node2')
def node2():
    pass

@socketio.on('connect', namespace='/node3')
def node3():
    pass

@socketio.on('connect', namespace='/node4')
def node4():
    pass

@socketio.on('connect', namespace='/node5')
def node5():
    pass

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
    # emit('connect',1)
    # Start listening Thread if not exist
    # print listen.isAlive()
    # if listen.isAlive() == False:
    #     listen.start()
    #     print "Start listening to Sensor"
    # else:
    #     print "Listening Thread already started"
        # emit('status', {'msg': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/main')
def disconnect():
    global clients
    clients -= 1
    if clients == 0:
        print 'No clients now'
    else:
        print 'Client disconnected, remain', clients

@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print e


listen.start()