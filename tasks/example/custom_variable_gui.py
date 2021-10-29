# A demonstration of using a custom variable dialog
# Does not require any hardware except micropython board.
# The onboard LED will alternate between red and green at a specified frequency
# Either color can be enabled or disabled using checkboxes
# The frequency can be adjusted between 0.2 and 30 Hz, using the spin box

from pyControl.utility import *
from devices import *
from pyb import LED

red_LED = LED(1)
green_LED = LED(2)

# States and events.
states = ['green_off','red_off','green_on','red_on']
events = ['green_off_wait','red_off_wait']

initial_state = 'red_off'

# Variables 
v.blink_rate = 5 #Hz
v.green_enabled = True
v.red_enabled = True
v.green_count = 3
v.red_count = 1

v.current_count___ = 0

# Use custom variable GUI that is defined in gui/user_variable_GUIs/blink_gui.py
v.variable_gui = 'my_custom_gui' 

# Define behaviour. 
def red_off(event):
    if event == 'entry':
        if v.current_count___ < v.red_count:
            if v.red_enabled:
                timed_goto_state('red_on', 1.0/v.blink_rate * second)
            else:
                set_timer('red_off_wait', 1.0/v.blink_rate*second)
        else:
            timed_goto_state('green_off', 1.0/v.blink_rate * second)
            v.current_count___ = 0
    elif event == 'red_off_wait':
        if v.current_count___ < v.red_count:
            v.current_count___ += 1
            set_timer('red_off_wait', 1.0/v.blink_rate*second)
        else:
            timed_goto_state('green_off', 1.0/v.blink_rate * second)
            v.current_count___ = 0

def red_on(event):
    if event == 'entry':
        red_LED.on()
        v.current_count___ += 1
        if v.current_count___ < v.red_count:
            timed_goto_state('red_off', 1.0/v.blink_rate * second)
        else:
            timed_goto_state('green_off', 1.0/v.blink_rate * second)
            v.current_count___ = 0
    if event == 'exit':
        red_LED.off()

def green_off(event):
    if event == 'entry':
        if v.current_count___ < v.green_count:
            if v.green_enabled:
                timed_goto_state('green_on', 1.0/v.blink_rate * second)
            else:
                set_timer('green_off_wait', 1.0/v.blink_rate*second)
        else:
            timed_goto_state('red_off', 1.0/v.blink_rate * second)
            v.current_count___ = 0
    elif event == 'green_off_wait':
        if v.current_count___ < v.green_count:
            v.current_count___ += 1
            set_timer('green_off_wait', 1.0/v.blink_rate*second)
        else:
            timed_goto_state('red_off', 1.0/v.blink_rate * second)
            v.current_count___ = 0

def green_on(event):
    if event == 'entry':
        green_LED.on()
        v.current_count___ += 1
        if v.current_count___ < v.green_count:
            timed_goto_state('green_off', 1.0/v.blink_rate * second)
        else:
            timed_goto_state('red_off', 1.0/v.blink_rate * second)
            v.current_count___ = 0
    if event == 'exit':
        green_LED.off()


def run_end():  # Turn off hardware at end of run.
    red_LED.off()
    green_LED.off()