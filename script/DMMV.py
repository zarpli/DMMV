# DMM Viewer
# Alejandro Zárate 11062015
# zarpli.com

import socket
import sys
import time
import tkinter
import os

from prefixed import Float

DMM_IP = "10.10.10.20"
DMM_PORT = 3490
DMM_MODEL = "8846A"

DMM_MSGLEN = 32
DMM_UNIT = "Ω"

print("Opening connection on %s port %s" % (DMM_IP, DMM_PORT))

try:
    conn=socket.create_connection((DMM_IP,DMM_PORT),timeout=30)
except socket.timeout:
    print("Connection error: timeout")
    exit(-1)
except:
    print("Connection error: unknown")
    exit(-1)

print("Connection succeed")

def dmm_cmd(cmd):
    cmd = cmd + '\r'
    i = 0
    while i < len(cmd):
        sent = conn.send(cmd[i:].encode())
        if sent == 0:
            raise RuntimeError("socket connection broken")
        i = i + sent

def dmm_read():
    chunks = []
    bytes_recv = 0
    while bytes_recv < DMM_MSGLEN:
        chunk = conn.recv(1)
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recv += 1
        if chunk == b',':
            chunks = []
            bytes_recv = 0
        if chunk == b'\n':
            break
    return b''.join(chunks)[:-2]

def dmm_func():
    dmm_cmd('func?')
    val_recv = dmm_read().decode()

    global DMM_UNIT
    match val_recv:
        case '"VOLT"':
            DMM_UNIT = "V±"
        case '"VOLT:AC"':
            DMM_UNIT = "V~"
        case '"CURR"':
            DMM_UNIT = "A±"
        case '"CURR:AC"':
            DMM_UNIT = "A~"
        case '"RES"':
            DMM_UNIT = "Ω"
        case '"CONT"':
            DMM_UNIT = ""
        case '"DIOD"':
            DMM_UNIT = ""
        case '"FREQ"':
            DMM_UNIT = "Hz"
        case '"PER"':
            DMM_UNIT = "s"
        case '"CAP"':
            DMM_UNIT = "F"
        case '"TEMP:RTD"':
            DMM_UNIT = "°C"
        case '"TEMP:FRTD"':
            DMM_UNIT = "°C"
        case _:
            DMM_UNIT = "UNK"

    print(f'current unit: {DMM_UNIT}')
    root.after(100, dmm_meas)

def dmm_meas():
    dmm_cmd('read?')
    val_recv = dmm_read()
    print(val_recv)
    dmm_disp.set(f'{Float(val_recv):.4h}' + DMM_UNIT)
    root.after(100, dmm_meas)

def dmm_quit():
    dmm_cmd('system:local')
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
    root.destroy()

def key_press(event):
    global DMM_UNIT
    if event.char == 'v':
        print('sets the meter to: DCV')
        dmm_cmd('func "volt:dc"')
        DMM_UNIT = "V±"
    if event.char == 'V':
        print('sets the meter to: ACV')
        dmm_cmd('func "volt:ac"')
        DMM_UNIT = "V~"
    if event.char == 'i':
        print('sets the meter to: DCI')
        dmm_cmd('func "curr:dc"')
        DMM_UNIT = "A±"
    if event.char == 'I':
        print('sets the meter to: ACI')
        dmm_cmd('func "curr:ac"')
        DMM_UNIT = "A~"
    if event.char == 'r':
        print('sets the meter to: Resistance')
        dmm_cmd('func "res"')
        DMM_UNIT = "Ω"
    if event.char == 'c':
        print('sets the meter to: Continuity')
        dmm_cmd('func "cont"')
        DMM_UNIT = ""
    if event.char == 'd':
        print('sets the meter to: Diode')
        dmm_cmd('func "diod"')
        DMM_UNIT = ""
    if event.char == 'f':
        print('sets the meter to: Frequency')
        dmm_cmd('func "freq"')
        DMM_UNIT = "Hz"
    if event.char == 'p':
        print('sets the meter to: Period')
        dmm_cmd('func "per"')
        DMM_UNIT = "s"
    if event.char == 'C':
        print('sets the meter to: Capacitance')
        dmm_cmd('func "cap"')
        DMM_UNIT = "F"
    if event.char == 't':
        print('sets the meter to: Temperature 2-wire')
        dmm_cmd('func "temp:rtd"')
        DMM_UNIT = "°C"
    if event.char == 'T':
        print('sets the meter to: Temperature 4-wire')
        dmm_cmd('func "temp:frtd"')
        DMM_UNIT = "°C"

root = tkinter.Tk()

abs_dir_path = os.path.dirname(os.path.realpath(__file__))
abs_img_path = os.path.join(abs_dir_path, 'F.png')
img_ico = tkinter.PhotoImage(file=abs_img_path)

root.tk.call('wm', 'iconphoto', root._w, img_ico)
root.title(DMM_MODEL)
root.geometry("600x100")
root.configure(bg='black')

dmm_disp = tkinter.StringVar()
label = tkinter.Label(root, textvariable = dmm_disp)
label.configure(bg='black', fg='SeaGreen1', font=('Arial', 30))
label.pack(fill="both", expand=True)

dmm_cmd('system:remote')

root.protocol("WM_DELETE_WINDOW", dmm_quit)
root.bind("<KeyPress>", key_press)
root.after(0, dmm_func)
root.mainloop()