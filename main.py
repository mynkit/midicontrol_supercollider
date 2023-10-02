# Launch Control XLを接続すること
# TemplatesはFactoryを使用すること

import pygame.midi as m
from pythonosc import udp_client, osc_server


client_to_sc = udp_client.SimpleUDPClient('127.0.0.1', 57110)

m.init()            # MIDIデバイスを初期化
i_num=m.get_count() # MIDIデバイスの数
for i in range(i_num):
    print(m.get_device_info(i)) # MIDIデバイスの情報を表示


target_device_name = 'Launch Control XL'
target_device_id = 0
play = 0
octave_state = {i+1: 0 for i in range(8)}

for i in range(i_num):
    info = m.get_device_info(i)
    name = info[1]
    inputflag = info[2]
    if name == bytes(target_device_name, encoding='utf-8') and inputflag:
        target_device_id = i 


midi_input = m.Input(target_device_id)


def get_channel(midi_id):
    a = [13, 14, 15, 16, 17, 18, 19, 20]
    b = [29, 30, 31, 32, 33, 34, 35, 36]
    pan = [49, 50, 51, 52, 53, 54, 55, 56]
    vol = [77, 78, 79, 80, 81, 82, 83, 84]
    buttonTop = [41, 42, 43, 44, 57, 58, 59, 60]
    buttonBottom = [73, 74, 75, 76, 89, 90, 91, 92]
    if midi_id in a:
        return a.index(midi_id) + 1, 'A'
    elif midi_id in b:
        return b.index(midi_id) + 1, 'B'
    elif midi_id in pan:
        return pan.index(midi_id) + 1, 'Pan'
    elif midi_id in vol:
        return vol.index(midi_id) + 1, 'Vol'
    elif midi_id in buttonTop:
        return buttonTop.index(midi_id) + 1, 'ButtonTop'
    elif midi_id in buttonBottom:
        return buttonBottom.index(midi_id) + 1, 'ButtonBottom'
    else:
        print(f"midi_id: {midi_id}")
        return 0, None

def get_default_freq(num):
    freq = 440
    if num == 1:
        # e
        freq = 329.628
    elif num == 2:
        # fs
        freq = 369.994
    elif num == 3:
        # gs
        freq = 415.305
    elif num == 4:
        # a
        freq = 440.000
    elif num == 5:
        # b
        freq = 493.883
    elif num == 6:
        # cs
        freq = 277.183*2
    elif num == 7:
        # d
        freq = 293.665*2
    elif num == 8:
        # e
        freq = 329.628*2
    return freq


def play_sc(num, send_type, midi_value):
    freq = 440
    amp = 0
    
    freq = get_default_freq(num)

    if send_type == "ButtonTop" and midi_value==1:
        if octave_state[num] < 4:
            octave_state[num] += 1
        client_to_sc.send_message("/n_set", [
            num,
            "freq", freq * (2**octave_state[num])
        ])

    if send_type == "ButtonBottom" and midi_value==1:
        if octave_state[num] > -2:
            octave_state[num] -= 1
        client_to_sc.send_message("/n_set", [
            num,
            "freq", freq * (2**octave_state[num])
        ])
    
    if send_type == "A":
        client_to_sc.send_message("/n_set", [
            num,
            "parFreq", midi_value * 10
        ])
    if send_type == "B":
        client_to_sc.send_message("/n_set", [
            num,
            "pan2Freq", midi_value * 110
        ])
    if send_type == "Vol":
        client_to_sc.send_message("/n_set", [
            num,
            "amp", midi_value*1
        ])
    if send_type == "Pan":
        client_to_sc.send_message("/n_set", [
            num,
            "ice", midi_value*1
        ])


if not play:
    for i in range(8):
        num = i+1
        client_to_sc.send_message("/s_new", [
            "sine", num, 1, 0,
            "amp", 0.0,
            "freq", get_default_freq(num),
            "reverb", 0.7, "ice", 0
        ])
    play = 1
    

try:
    while True:
        if midi_input.poll(): # MIDIが受信されると１
            midi_events = midi_input.read(4) # 読み取る入力イベントの数　
            event = midi_events[0][0]
            midi_id = event[1]
            midi_value = event[2] / 127
            num, send_type = get_channel(midi_id)

            print(f"midi{num}{send_type}", midi_value)

            play_sc(num, send_type, midi_value)

except KeyboardInterrupt:
    midi_input.close()

    for i in range(8):
        num = i + 1
        client_to_sc.send_message("/n_free", num)