# import RPi.GPIO as GPIO
# from w1thermsensor import W1ThermSensor

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import shutil
import os
import threading
import time
from simple_pid import PID

# pin = 21

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(pin, GPIO.OUT)

active = True
thread_stop = False
on = False
temp = 0.0
pid = PID(1, 0.1, 0.05, sample_time=1, setpoint=130, output_limits=(0, 1), proportional_on_measurement=True)
graph_infos = []

class GraphInfo:
    def __init__(self, temp, on):
        self.temp = temp
        self.on = on

    def __repr__(self):
        return '{"temp": %f, "on": %s}' % (self.temp, "true" if self.on else "false")


def reset():
    global on
    global active
    global temp
    global pid
    global graph_infos

    active = True
    on = False
    temp = 0.0
    pid = PID(1, 0.1, 0.05, sample_time=1, setpoint=130, output_limits=(0, 1), proportional_on_measurement=True)
    graph_infos = []

def stop():
    turn_off()
    global active
    active = False

def turn_on():
    global on
    on = True
    # GPIO.output(pin, GPIO.HIGH)

def turn_off():
    global on
    on = False
    # GPIO.output(pin, GPIO.LOW)

def sensor_temp():
    # sensorCount = 0
    # totalTemp = 0.0

    # for sensor in W1ThermSensor.get_available_sensors():
        # sensorTemp = sensor.get_temperature(W1ThermSensor.DEGREES_F)
        # sensorCount += 1
        # totalTemp += sensorTemp

    # temp = totalTemp / sensorCount
    return temp

class S(BaseHTTPRequestHandler):
    def do_POST(self):
        data_string = ''
        if 'Content-Length' in self.headers:
            data_string = self.rfile.read(int(self.headers['Content-Length']))

        if self.path == '/on':
            turn_on()
            print on
        elif self.path == '/off':
            turn_off()
        elif self.path == '/temp':
            global temp
            temp = float(data_string)
        elif self.path == '/target':
            pid.setpoint = float(data_string)
        elif self.path == '/stop':
            stop()
        elif self.path == '/reset':
            reset()
        
        self.send_response(200)
        self.wfile.write('')

    def serve_file(self, relpath):
        try:
            here = os.path.dirname(os.path.realpath(__file__))
            filepath = os.path.join(here, relpath)
            f = open(filepath)

            try:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                shutil.copyfileobj(f, self.wfile)
            finally:
                f.close()
        except:
            self.send_response(404)
            self.end_headers()
            self.wfile.write('File not found\n')

    def do_GET(self):
        if self.path == '/':
            self.serve_file('web/index.html')
        elif self.path == '/index.js':
            self.serve_file('web/index.js')
        elif self.path == '/plotly.min.js':
            self.serve_file('web/plotly.min.js')
        elif self.path == '/target':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(str(pid.setpoint))
        elif self.path == '/info':
            temp = sensor_temp()
            on = "true" if on else "false"

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write('{"temp": %d, "on": %s}' % (temp, on))
        elif self.path == '/graph_info':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(str(graph_infos))


def run(server_class=HTTPServer, handler_class=S, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting server...'
    httpd.serve_forever()

def monitor_background():
    while not thread_stop:
        if active:
            global temp
            temp = sensor_temp()

            control = pid(temp)
            if control > 0:
                turn_on()
            else:
                turn_off()

        graph_infos.append(GraphInfo(temp, on))

        time.sleep(1)

if __name__ == '__main__':
    try:
        thread = threading.Thread(target=monitor_background, args=())
        thread.start()

        run()
    except KeyboardInterrupt:
        # GPIO.cleanup()
        print 'finishing up...'

        thread_stop = True
        thread.join()
        pass



