import pyb
from array import array
from . import framework as fw
from .utility import *

# ----------------------------------------------------------------------------------------
# State Machine
# ----------------------------------------------------------------------------------------

class State_machine():
    # State machine behaviour is defined by passing state machine description object smd to 
    # State_machine __init__(). smd is a module which defines the states, events and  
    # functionality of the state machine object that is created (see examples). 

    def __init__(self, smd):

        self.smd = smd # State machine definition.
        self.ID = None # Overwritten by fw.register_machine()
        self.tg_next_state = None # Overwritted by timed_goto_state.

        fw.register_machine(self)

        # Make dict mapping state names to state event handler functions.
        smd_methods = dir(self.smd) # List of methods of state machine instance.
        self.event_dispatch_dict = {}
        for state in list(self.smd.states) + ['all_states', 'run_start', 'run_end']:
            if state in smd_methods:
                self.event_dispatch_dict[state] = getattr(self.smd, state)
            else:
                self.event_dispatch_dict[state] = None

        # Attach user methods to discription object namespace, this allows the user
        # to write e.g. goto_state(state) in the task description to call 
        # State_machine.goto_state. 
        smd.goto_state       = self.goto_state
        smd.goto             = self.goto_state # For backwards compatibility with old tasks.
        smd.timed_goto_state = self.timed_goto_state
        smd.set_timer        = self.set_timer
        smd.disarm_timer     = self.disarm_timer
        smd.reset_timer      = self.reset_timer
        smd.print            = self.print 
        smd.data_print       = self.data_print
        smd.stop_framework   = self.stop_framework
        smd.publish_event    = self.publish_event

    # Methods called by user

    def goto_state(self, next_state):
        # Transition to next state, calling exit action of old state
        # and entry action of next state.
        self._process_event('exit')
        if self.tg_next_state: # Cancel timed_goto_state.
            self.tg_next_state = None
            fw.timer.disarm((fw.goto_evt, self.ID))    
        if fw.data_output:
            fw.data_output_queue.put((fw.states[next_state], fw.current_time))
        self.current_state = next_state
        self._process_event('entry')

    def timed_goto_state(self, next_state, interval):
        # Transition to next_state after interval milliseconds. timed_goto_state()
        # is cancelled if goto_state() occurs before interval elapses.
        fw.timer.set(int(interval), (fw.goto_evt, self.ID))
        self.tg_next_state = next_state

    def set_timer(self, event, interval):
        # Set a timer to return specified event after interval milliseconds.
        fw.timer.set(int(interval), (fw.events[event], fw.timer_evt))    

    def disarm_timer(self, event):
        # Disable all active timers due to return specified event.
        fw.timer.disarm((fw.events[event], fw.timer_evt))

    def reset_timer(self, event, interval):
        # Disable all active timers due to return specified event and set new timer
        # to return specified event after interval milliseconds.
        fw.timer.disarm((fw.events[event], fw.timer_evt))
        fw.timer.set(int(interval), (fw.events[event], fw.timer_evt))

    def print(self, print_string):
        # Used to output data print_string with timestamp.  print_string is stored and only
        #  printed to serial line once higher priority tasks have all been processed. 
        if fw.data_output:
            fw.data_output_queue.put((fw.print_evt, fw.current_time, print_string))

    def data_print(self, name, typecode, data_array):
        # Output data contained in data_array of type specified by typecode 
        if fw.data_output:
            fw.data_output_queue.put((fw.data_evt, fw.current_time, name, typecode, data_array))

    def publish_event(self, event):
        # Put event with specified name in the event queue.
        fw.event_queue.put((fw.events[event], fw.current_time))

    def stop_framework(self):
        fw.running = False

    # Methods called by pyControl framework.

    def _process_event(self, event):
        # Process event given event name by calling appropriate state event handler function.
        if self.event_dispatch_dict['all_states']:                      # If machine has all_states event handler function. 
            handled = self.event_dispatch_dict['all_states'](event)     # Evaluate all_states event handler function.
            if handled: return                                          # If all_states event handler returns True, don't evaluate state specific behaviour.
        if self.event_dispatch_dict[self.current_state]:                # If state machine has event handler function for current state.
            self.event_dispatch_dict[self.current_state](event)         # Evaluate state event handler function.

    def _process_timed_goto_state(self):
        # Called by framework when timed_goto_state timer elapses.
        self.goto_state(self.tg_next_state)

    def _start(self):
        # Called when run is started. Puts agent in initial state, and runs entry event.
        if self.event_dispatch_dict['run_start']:
            self.event_dispatch_dict['run_start']()
        self.current_state = self.smd.initial_state
        if fw.data_output:
            fw.data_output_queue.put((fw.states[self.current_state], fw.current_time))
        self._process_event('entry')

    def _stop(self):
        # Calls user defined stop function at end of run if function is defined.
        if self.event_dispatch_dict['run_end']:
            self.event_dispatch_dict['run_end']()





