## Program that play the song "secret base〜君がくれたもの〜"
## A youtube link for reference "https://www.youtube.com/watch?v=4CFfSd3toUs"
## Note: the raspberry pi pico was placed on the 11th row of the bread board

from machine import Pin
import utime
from rp2 import PIO, StateMachine, asm_pio

# This is essential for the function song_player
#
# Reference for how to set rp2.asm_pio and rp2.StateMachine
# https://docs.micropython.org/en/latest/library/rp2.html
# https://docs.micropython.org/en/latest/library/rp2.StateMachine.html
#
# Reference for making the square wave for the buzzer
# https://www.onetransistor.eu/2021/02/rpi-pico-pio-state-machine-square-wave.html
#
# note: you can add 2 seperated line of nop() after the set(pins) in order to reduce the frequency of square wave by half
@asm_pio(set_init=PIO.OUT_LOW)
def square():
    wrap_target()
    set(pins, 1)
    set(pins, 0) 
    wrap()

# The song player
# The sheet music is in the form of array, containing the key/frequency and
# the number of quater note, assumed to be 1
# TODO: can set up a class for the song
def song_player(sheet_music, BPM, buzzer_io_gpio, button_gpio=None,\
                frequency_list=[], led_pin_list=[]):
    if button_gpio==None:
        button_gpio = buzzer_io_gpio
    
    # the frequency for evey key.
    # C is the double high C. hCs stands for high C sharp
    # P means pause
    P=0
    Cs = 2217
    D = 2349
    Ds = 2489
    E = 2637
    F = 2794
    Fs = 2960
    G = 3136
    Gs = 3322
    A = 3520
    As = 3729
    B = 3951
    hC = 4186
    hCs = 4435
    
    def close_all_led(led_pin_list):
        for i in led_pin_list:
            Pin(i,Pin.OUT).value(0)
    
    def mute_buzzer(buzzer_io_gpio):
        # set the i/o to high for short period of time, to pause the sound, to give the feeling of releasing the keyboard
        # or to hold it in high to mute the buzzeer
        Pin(buzzer_io_gpio, Pin.OUT).value(1)

    def k(frequency, frequency_list=[], led_pin_list=[]):
        # k means key

        # if it is a pause(0Hz) on the sheet music, then pause, or else, set the square wave signal to that frequency
        if frequency==0:
            Pin(buzzer_io_gpio, Pin.OUT).value(1)
            print("#N/A")
        else:
            StateMachine(0, square, freq=frequency, set_base=Pin(buzzer_io_gpio)).active(1)
            print(frequency, " Hz")
        
        # light up the corresponding led    
        try:
            pin_gpio = led_pin_list[frequency_list.index(frequency)]
            Pin(pin_gpio,Pin.OUT).value(1)
        except:
            pass
    
    # record when the song start, in micro second
    start_time = utime.ticks_us()
    
    # the delay second, so the function won't detect the button before this delay_sec has passed
    delay_sec = 0.5
    
    # before the protection time, pressing the button won't stop the song player function
    protection_time = int(utime.ticks_add(utime.ticks_us(), int(delay_sec*1000*1000)))
    
    # start
    print("start")
    
    # play the note one by one, check if the button is pressed
    for i in sheet_music:
        # define how long the note will last for
        if len(i)>1:
            sec=60/BPM*0.5*i[1]
        else:
            sec=60/BPM*0.5
        
        # reset all led light to off
        close_all_led(led_pin_list)
        
        # if it is a pause on the sheet music, then pause, or else, set the square wave signal to that frequency
        k(i[0],frequency_list, led_pin_list)
        
        # keep check if the button is pressed, if so then break the song playing loop
        break_outer_loop_boolean = 0
        key_deadline = int(utime.ticks_add(utime.ticks_us(), int(sec*1000*1000)))
        
        while utime.ticks_diff(key_deadline, utime.ticks_us()) > 0:
            # if the button is pressed, break the for-loop that plays the song
            if utime.ticks_diff(protection_time, utime.ticks_us()) < 0 and \
               Pin(button_gpio,Pin.IN,Pin.PULL_DOWN).value():
                print("break")
                close_all_led(led_pin_list)
                mute_buzzer(buzzer_io_gpio)
                utime.sleep(delay_sec) # preventing the program to read this button pressing as the instruction of playing the song
                break_outer_loop_boolean = 1
                break
        
        if break_outer_loop_boolean:
            break
        
        # set the i/o to high for short period of time, to pause the sound, to give the feeling of releasing the keyboard
        mute_buzzer(buzzer_io_gpio)

    mute_buzzer(buzzer_io_gpio)
    close_all_led(led_pin_list)

def main():  
    # gpio for the buzzer
    buzzer_io_gpio = 16

    #gpio for the button
    button_gpio = 15

    # gpio for led
    blue=21
    white=0
    green=14
    red=3
    yellow=22
    led_pin_list = [blue,white,green,red,yellow] # the order of led on our bread board
    
    # the frequency list, correspond to the led, \
    # so the led will light if the above frequency is played
    P = 0
    Cs = 2217
    D = 2349
    Ds = 2489
    E = 2637
    F = 2794
    Fs = 2960
    G = 3136
    Gs = 3322
    A = 3520
    As = 3729
    B = 3951
    hC = 4186
    hCs = 4435
    frequency_list = [Cs,Fs,Gs,As,hCs]

    # control the speed of the song. BPM means beat per minute
    BPM = 90 *134/120
    
    # Sheet Music
    Secret_Base = [
    [Cs,2/4],[Fs],[Gs,2/4],\
    [Gs],[As,2/4],[As],[As,2/4],[As],[As,2/4],[P],\
    [As,6/4],[Gs,2/4],[Gs],[Gs,2/4],[Gs],[Gs,2/4],[P],\
    [Gs,6/4],[Fs,2/4],[Fs],[Fs,2/4],[Fs],[Fs,6/4],\
    [Fs,6/4],[Cs,2/4],[Cs],[Cs,2/4],[P],[Cs,2/4],[Fs],[Gs,2/4],\
    [Gs],[As,2/4],[As],[As,2/4],[As],[As,2/4],[As],[hCs,2/4],[P],\
    [As,2/4],[As],[As,2/4],[As],[As,2/4],[Gs],[Fs,2/4],\
    [Gs,6/4],[As],[As,31/4],[P,1/4],\
    [Gs],[As,2/4],[Gs],[Fs,2/4],[Fs],[Fs,31/4],[P,1/4],\
    [Gs],[As,2/4],[Gs],[Fs,2/4],[Fs],[F,1/4],[Fs,33/4]\
    ]
    
    while True:
        if Pin(button_gpio,Pin.IN,Pin.PULL_DOWN).value():
            song_player(Secret_Base,BPM,buzzer_io_gpio,button_gpio,frequency_list,led_pin_list)
    
main()
