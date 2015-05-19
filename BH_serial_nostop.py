#!/usr/bin/env python

"""
Arithmetic calculation task in block paradigm
Author: Cameron Craddock
modification of code by: Zhi Yang

There are 5 blocks (can be adjusted in "NUM_EVENTS",
the total LENGTH can be adjusted in "LENGTH") of
arithmetic calculation, each of which is randomized
between 32 and 34 secs in LENGTH (can be adjusted in
"DURATION_EVENT" variable). Arithmetic problems are
presented with 4 answers (can be adjusted in "NUM_CHOICE".
The subject is required to choose the correct one as soon
and accurate as possible. The problems are in the form of
"A - B = ?", and A is randomly chosen from 13 to 17, B from
4 to A-4 (can be adjusted in "RANGE_A" and "OFFSET_B").
The answers are four numbers neighor to the correct answer,
but the position of the correct answer is randomized.
event here is generalized as one session of stimulus,
either in event-related or block paradigm; image here
is generalized as one screen display

"""

#================= Parameter Inputs: often modified ============================

R = 0
G = 1
In = 2
Out = 3 
Deep = 4
H1 = 5
H2 = 6
H3 = 7
H4 = 8
H5 = 9
H6 = 10

TASK_SEQUENCE = ( R, G, In, Out, Deep, H1, H2, H3, H4, H5, H6,
                  R, G, In, Out, Deep, H1, H2, H3, H4, H5, H6,
                  R, G, In, Out, Deep, H1, H2, H3, H4, H5, H6,
                  R, G, In, Out, Deep, H1, H2, H3, H4, H5, H6,
                  R, G, In, Out, Deep, H1, H2, H3, H4, H5, H6,
                  R, G, In, Out, Deep, H1, H2, H3, H4, H5, H6,
                  R, G, In, Out, Deep, H1, H2, H3, H4, H5, H6 )
TASK_TIMING =   (10, 2,  2,   2,    2,  2.5,  2.5,  2.5,  2.5,  2.5,  2.5,
                 10, 2,  2,   2,    2,  2.5,  2.5,  2.5,  2.5,  2.5,  2.5,
                 10, 2,  2,   2,    2,  2.5,  2.5,  2.5,  2.5,  2.5,  2.5,
                 10, 2,  2,   2,    2,  2.5,  2.5,  2.5,  2.5,  2.5,  2.5,
                 10, 2,  2,   2,    2,  2.5,  2.5,  2.5,  2.5,  2.5,  2.5,
                 10, 2,  2,   2,    2,  2.5,  2.5,  2.5,  2.5,  2.5,  2.5,
                 10, 2,  2,   2,    2,  2.5,  2.5,  2.5,  2.5,  2.5,  2.5 )
TR = 3

# define the responses
key_response = range (10)
# button box
key_response[0] = 'r' # red
key_response[1] = 'g' # yellow
key_response[2] = 'y' # green
key_response[3] = 'b' # blue
# for keyboard
key_response[4] = 'j' # red
key_response[5] = 'k' # yellow
key_response[6] = 'l' # green
key_response[7] = 'SEMICOLON' # blue
key_response[8] = 'ESCAPE' # Esc key to quit
key_response[9] = 't' # trigger key

## form the response event name
for i in range (len (key_response)):
	key_response[i] = 'pygame.locals.K_'+key_response[i]

#===============================================================================

#================================ Import libraries =============================

from VisionEgg import *
start_default_logging(); watch_exceptions()

from VisionEgg.Core import *
#from VisionEgg.FlowControl import Presentation, FunctionController
from VisionEgg.Textures import *
from VisionEgg.MoreStimuli import *
from random import *
from VisionEgg.Text import *
#from VisionEgg.ResponseControl import *
#from VisionEgg.DaqKeyboard import *
from string import *
import Image, ImageDraw
import OpenGL.GL as gl
import os, sys
import time
import pygame
import serial

#===============================================================================


#========================== check usage and input profile ======================
#================== modify to adapt different form of profile input ============

if len (sys.argv) != 1:
	print "\nIncorrect number of input! Quit...\nUsage: arith_BK filename"
	sys.exit ()

#===============================================================================

#===============  CREATE SERIAL ==================#
ser = serial.Serial(0, 19200, timeout=1)

#=================== Generate the display sequence =============================
#================== Usually need modifying according to paradigm ===============

## set screen parameters
screen = VisionEgg.Core.Screen(size=(1024,768),fullscreen=True)
#screen = get_default_screen ()
screen.parameters.bgcolor = (0.0, 0.0, 0.0, 1.0)

## create intro
tStim = Text (text="Breath Holding Task",color=(255,239,213),
	position=(screen.size[0]/2, screen.size[1]*0.6),
	font_size=60, anchor='center')

hStim = FixationCross(on = True, position=(320,304),size=(64,64))

hStim = FilledCircle (anchor   = 'center',
  			 position = (screen.size[0]/2.0, screen.size[1]/2.0+62.5),
  			 radius   = 64.0,
  			 color    = (255, 0, 0)) # Draw it in red

# create viewpoint
viewport = Viewport (screen=screen, stimuli=[tStim])
#===============================================================================

#======================== user-loop ============================================
#==================== Pay attention to the event handling ======================

# save time
frame_timer = VisionEgg.Core.FrameTimer()

quit_now = 0
start = False
flag_start_event = True
flag_start_presentation = True

cur_block = 0
trig_count = 0
stim_count = 0

while not quit_now:
	for event in pygame.event.get():
		if event.type == pygame.locals.QUIT:
			quit_now = True
		elif event.type == pygame.locals.KEYDOWN:
			if event.key == eval (key_response[-2]):
				quit_now = True
			elif event.key == eval (key_response[-1]):
				stim_count=stim_count+1
				trig_count=trig_count+1
				start = True
	if start is False:

		xx=''

		xx=ser.read()

		if xx:

			print "received: ",xx

		if xx == '5':

			start=True

	if start is True:
		current_time = VisionEgg.time_func()

		# save the time on the begining of presentation
		if flag_start_presentation is True:
			start_time = current_time
			flag_start_presentation = False


		# if we are done with the current block, go to
		# the next one
		if (current_time - start_time) >= TASK_TIMING[ cur_block ]:
			start_time = current_time
			cur_block = cur_block + 1

		screen.clear()
		if cur_block < len( TASK_SEQUENCE ):
			if TASK_SEQUENCE[ cur_block ] == R:
				tStim.parameters.text = "Rest"
				viewport.parameters.stimuli = [tStim]
			elif TASK_SEQUENCE[ cur_block ] == G:
				tStim.parameters.text = "Get Ready"
				viewport.parameters.stimuli = [tStim]
			elif TASK_SEQUENCE[ cur_block ] == In:
				tStim.parameters.text = "Breath In"
				viewport.parameters.stimuli = [tStim]
			elif TASK_SEQUENCE[ cur_block ] == Out:
				tStim.parameters.text = "Breath Out"
				viewport.parameters.stimuli = [tStim]
			elif TASK_SEQUENCE[ cur_block ] == Deep:
				tStim.parameters.text = "Deep Breath and Hold"
				viewport.parameters.stimuli = [tStim]
			elif TASK_SEQUENCE[ cur_block ] == H1:
				hStim.parameters.radius=64
				hStim.parameters.color=(255,0,0)
				viewport.parameters.stimuli = [hStim]
			elif TASK_SEQUENCE[ cur_block ] == H2:
				hStim.parameters.color=(192,64,0)
				hStim.parameters.radius=56
				viewport.parameters.stimuli = [hStim]
			elif TASK_SEQUENCE[ cur_block ] == H3:
				hStim.parameters.color=(128,128,64)
				hStim.parameters.radius=48
				viewport.parameters.stimuli = [hStim]
			elif TASK_SEQUENCE[ cur_block ] == H4:
				hStim.parameters.color=(64,255,128)
				hStim.parameters.radius=40
				viewport.parameters.stimuli = [hStim]
			elif TASK_SEQUENCE[ cur_block ] == H5:
				hStim.parameters.color=(0,0,255)
				hStim.parameters.radius=32
				viewport.parameters.stimuli = [hStim]
			elif TASK_SEQUENCE[ cur_block ] == H6:
				hStim.parameters.color=(0,255,0)
				hStim.parameters.radius=24
				viewport.parameters.stimuli = [hStim]
		else:
                        #screen.clear()
                        #tStim.parameters.text = "Rest"
                        #viewport.parameters.stimuli = [tStim]
                        quit_now=1
                        #viewport.draw()
                        #swap_buffers ()

		viewport.draw()
	else: # is start is true
		screen.clear()
		viewport.draw()
                

	swap_buffers ()
	frame_timer.tick ()
##=====  HANG AROUND A WHILE... ===============

##screen.clear()
#viewport.draw()
quit_now = 0

screen.clear()
tStim.parameters.text = "Rest"
viewport.parameters.stimuli = [tStim]
viewport.draw()
swap_buffers ()
frame_timer.tick ()

while not quit_now:
	for event in pygame.event.get():
		if event.type == pygame.locals.QUIT:
			quit_now = True
		elif event.type == pygame.locals.KEYDOWN:
			if event.key == eval (key_response[-2]):
				quit_now = True
			elif event.key == eval (key_response[-1]):
				stim_count=stim_count+1
				trig_count=trig_count+1
				start = True
                
print "Received %d triggers" % trig_count
#===============================================================================

#=============================== File logging ==================================

#print response, rt

#log = open (filename,'w')
#counter = 0
#for i in range (len (sequence)):
#	if sequence[i] == -1:
#		log.write ("-1\n")
#	else:
		#          item   A   B   ans ans_pos onset resp    rt   correct
#		log.write ("%3d\t%2d\t%2d\t%2d\t%d\t\t%5.3f\t%5.3f\t%5.3f\t%d\n" % (
#			counter+1, profile[0][counter], profile[1][counter],
#			profile[3][counter], profile[4][counter], image_begin_time[counter],
#			response[counter], rt[counter], 1 and (response[counter]==profile[4][counter])))
#		counter = counter + 1
#log.close ()


# write the paradigm 1D file
#filename = '_'.join (['1D_math_', filename])
#log = open (filename, 'w')
#for i in range (len (paradigm1D)):
#	log.write ("%d\n" % paradigm1D[i])
#log.close ()
#===============================================================================
