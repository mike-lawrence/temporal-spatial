########
#Important parameters
########
viewingDistance = 50 #units can be anything so long as they match those used in stimDisplayWidth below
stimDisplayWidth = 50  #units can be anything so long as they match those used in viewingDistance above
stimDisplayRes = (2560,1440) #pixel resolution of the stimDisplay

responseModality = 'trigger' #'key' or 'trigger'
triggerLeftAxis = 2
triggerRightAxis = 5
triggerCriterionValue = -(2**16/4)

targetIdentityList = ['square','diamond']
targetLocationList = ['left','right']
cueLocationList = ['left','right']

soaTypeList = ['random','fixed','mixed','namix']
fixedSoaList = [0.100,0.300,0.600,1.000]
naFixedSoaList = [
 0.100,0.100,0.100,0.100,0.100,0.100,0.100,0.100,
,0.300,0.300,0.300,0.300
,0.600,0.600
,1.000
]
cueDuration = .050
targetDuration = 1.000
ttoaMin = 2.000
ttoaMean = 3.00
ttoaMax = 10.00

blocksPerSoa = 3
repsPerBlock = len(naFixedSoaList)
trialsPerPractice = 5

instructionSizeInDegrees = 1.0
feedbackSizeInDegrees = .5

fixationSizeInDegrees = .5
fixationThicknessProportion = .1
offsetSizeInDegrees = 5
targetSizeInDegrees = .5
boxSizeInDegrees = 2.0
boxThicknessProportion = .1

trialsPerBlock = 10
numberOfBlocks = 2


########
# Import libraries
########
from PIL import Image #for image manipulation
from PIL import ImageFont
from PIL import ImageOps
import OpenGL.GL as gl
import math #for trig and other math stuff
import sys #for quitting
import random #for shuffling and random sampling
import os #for checking existing files
import shutil #for copying files
import hashlib #for encrypting
import time #for timing
import sdl2 #for input and display
import sdl2.ext #for input and display
import numpy #for image and display manipulation


########
# Initialize the timer and random seed
########
sdl2.SDL_Init(sdl2.SDL_INIT_TIMER)
seed = int(time.time()) #grab the time of the timer initialization to use as a seed and to sync with pyTracker
random.seed(seed) #use the time to set the random seed


########
# Initialize the gamepad if necessary
########
if responseModality!='key':
	sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
	gamepad = sdl2.SDL_JoystickOpen(0)


########
# Initialize the stimDisplay
########
byteify = lambda x, enc: x.encode(enc)
class stimDisplayClass:
	def __init__(self,stimDisplayRes):#,stimDisplayMirrorChild):
		self.stimDisplayRes = stimDisplayRes
		# self.stimDisplayMirrorChild = stimDisplayMirrorChild
		sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
		self.stimDisplayRes = stimDisplayRes
		self.Window = sdl2.video.SDL_CreateWindow(byteify('stimDisplay', "utf-8"),0,0,self.stimDisplayRes[0],self.stimDisplayRes[1],sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP | sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
		self.glContext = sdl2.SDL_GL_CreateContext(self.Window)
		gl.glMatrixMode(gl.GL_PROJECTION)
		gl.glLoadIdentity()
		gl.glOrtho(0, stimDisplayRes[0],stimDisplayRes[1], 0, 0, 1)
		gl.glMatrixMode(gl.GL_MODELVIEW)
		gl.glDisable(gl.GL_DEPTH_TEST)
		gl.glReadBuffer(gl.GL_FRONT)
		gl.glClearColor(0,0,0,1)
		start = time.time()
		while time.time()<(start+2):
			sdl2.SDL_PumpEvents()
		self.refresh()
		self.refresh()
	def refresh(self,clearColor=[0,0,0,1]):
		sdl2.SDL_GL_SwapWindow(self.Window)
		# self.stimDisplayMirrorChild.qTo.put(['frame',self.stimDisplayRes,gl.glReadPixels(0, 0, self.stimDisplayRes[0], self.stimDisplayRes[1], gl.GL_BGR, gl.GL_UNSIGNED_BYTE)])
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)


stimDisplay = stimDisplayClass(stimDisplayRes=stimDisplayRes)#,stimDisplayMirrorChild=stimDisplayMirrorChild)
sdl2.mouse.SDL_ShowCursor(0)


########
#Perform some calculations to convert stimulus measurements in degrees to pixels
########
stimDisplayWidthInDegrees = math.degrees(math.atan((stimDisplayWidth/2.0)/viewingDistance)*2)
PPD = stimDisplayRes[0]/stimDisplayWidthInDegrees #compute the pixels per degree (PPD)

instructionSize = int(instructionSizeInDegrees*PPD)
feedbackSize = int(feedbackSizeInDegrees*PPD)

fixationSize = int(fixationSizeInDegrees*PPD)
fixationThickness = int(fixationThicknessProportion*(fixationSizeInDegrees*PPD))

offsetSize = int(offsetSizeInDegrees*PPD)

targetSize = int(targetSizeInDegrees*PPD)

boxSize = int(boxSizeInDegrees*PPD)
boxThickness = int(boxThicknessProportion*(boxSizeInDegrees*PPD))


########
#Initialize the fonts
########
# sdl2.sdlttf.TTF_Init()
# feedbackFont = sdl2.sdlttf.TTF_OpenFont('_Stimuli/DejaVuSans.ttf', feedbackSize)
# instructionFont = sdl2.sdlttf.TTF_OpenFont('_Stimuli/DejaVuSans.ttf', instructionSize)
feedbackFontSize = 2
feedbackFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", feedbackFontSize)
feedbackHeight = feedbackFont.getsize('XXX')[1]
while feedbackHeight<feedbackSize:
	feedbackFontSize = feedbackFontSize + 1
	feedbackFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", feedbackFontSize)
	feedbackHeight = feedbackFont.getsize('XXX')[1]

feedbackFontSize = feedbackFontSize - 1
feedbackFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", feedbackFontSize)

instructionFontSize = 2
instructionFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", instructionFontSize)
instructionHeight = instructionFont.getsize('XXX')[1]
while instructionHeight<instructionSize:
	instructionFontSize = instructionFontSize + 1
	instructionFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", instructionFontSize)
	instructionHeight = instructionFont.getsize('XXX')[1]

instructionFontSize = instructionFontSize - 1
instructionFont = ImageFont.truetype ("_Stimuli/DejaVuSans.ttf", instructionFontSize)


########
# Create sprites for visual stimuli
########

# greyBoxPen = aggdraw.Pen((127,127,127,255),boxThickness)
# #box = aggdraw.Draw('RGBA',[boxSize*3,boxSize*3],(0,0,0,0))
# box = pyagg.canvas(width = boxSize*3, height=boxSize*3)
# #box.ellipse([boxSize,boxSize,boxSize*2,boxSize*2],greyBoxPen)
# box.draw_circle([boxSize,boxSize,boxSize*2,boxSize*2],fillcolor=(127,127,127,255))
# box = Image.fromstring(box.mode,box.size,box.tostring())
# box = numpy.asarray(box)

# whiteCuePen = aggdraw.Pen((255,255,255,255),boxThickness)
# cue = aggdraw.Draw('RGBA',[boxSize*3,boxSize*3],(0,0,0,0))
# cue.ellipse([boxSize,boxSize,boxSize*2,boxSize*2],whiteCuePen)
# cue = Image.fromstring(cue.mode,cue.size,cue.tostring())
# cue = numpy.asarray(cue)

# greyFixationPen = aggdraw.Pen((127,127,127,255),fixationThickness)
# fixation = aggdraw.Draw('RGBA',[fixationSize,fixationSize],(0,0,0,0))
# fixation.line([fixationSize/2,0,fixationSize/2,fixationSize],greyFixationPen)
# fixation.line([0,fixationSize/2,fixationSize,fixationSize/2],greyFixationPen)
# fixation = Image.fromstring(fixation.mode,fixation.size,fixation.tostring())
# fixation = numpy.asarray(fixation)

# greyBrush = aggdraw.Brush((127,127,127,255))
# square = aggdraw.Draw('RGBA',[targetSize,targetSize],(0,0,0,0))
# square.rectangle([0,0,targetSize,targetSize],greyBrush)
# square = Image.fromstring(square.mode,square.size,square.tostring())
# diamond = square.rotate(45,expand=1)
# diamond = numpy.asarray(diamond)
# square = numpy.asarray(square)

########
# Drawing functions
########

def text2numpy(myText,myFont,fg=[255,255,255,255],bg=[0,0,0,0]):
	glyph = myFont.getmask(myText,mode='L')
	a = numpy.asarray(glyph)#,dtype=numpy.uint8)
	b = numpy.reshape(a,(glyph.size[1],glyph.size[0]),order='C')
	c = numpy.zeros((glyph.size[1],glyph.size[0],4))#,dtype=numpy.uint8)
	# c[:,:,0][b>0] = b[b>0]
	# c[:,:,1][b>0] = b[b>0]
	# c[:,:,2][b>0] = b[b>0]
	# c[:,:,3][b>0] = b[b>0]
	c[:,:,0][b>0] = fg[0]*b[b>0]/255.0
	c[:,:,1][b>0] = fg[1]*b[b>0]/255.0
	c[:,:,2][b>0] = fg[2]*b[b>0]/255.0
	c[:,:,3][b>0] = fg[3]*b[b>0]/255.0
	c[:,:,0][b==0] = bg[0]
	c[:,:,1][b==0] = bg[1]
	c[:,:,2][b==0] = bg[2]
	c[:,:,3][b==0] = bg[3]
	return c.astype(dtype=numpy.uint8)


def blitNumpy(numpyArray,xLoc,yLoc,xCentered=True,yCentered=True):
	gl.glEnable(gl.GL_BLEND)
	gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
	ID = gl.glGenTextures(1)
	gl.glBindTexture(gl.GL_TEXTURE_2D, ID)
	gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE);
	gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
	gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
	gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
	gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
	gl.glTexImage2D( gl.GL_TEXTURE_2D , 0 , gl.GL_RGBA , numpyArray.shape[1] , numpyArray.shape[0] , 0 , gl.GL_RGBA , gl.GL_UNSIGNED_BYTE , numpyArray )
	gl.glEnable(gl.GL_TEXTURE_2D)
	gl.glBindTexture(gl.GL_TEXTURE_2D, ID)
	gl.glBegin(gl.GL_QUADS)
	x1 = xLoc + 1.5 - 0.5
	x2 = xLoc + numpyArray.shape[1] - 0.0 + 0.5
	y1 = yLoc + 1.0 - 0.5
	y2 = yLoc + numpyArray.shape[0] - 0.5 + 0.5
	if xCentered:
		x1 = x1 - numpyArray.shape[1]/2.0
		x2 = x2 - numpyArray.shape[1]/2.0
	if yCentered:
		y1 = y1 - numpyArray.shape[0]/2.0
		y2 = y2 - numpyArray.shape[0]/2.0
	gl.glTexCoord2f( 0 , 0 )
	gl.glVertex2f( x1 , y1 )
	gl.glTexCoord2f( 1 , 0 )
	gl.glVertex2f( x2 , y1 )
	gl.glTexCoord2f( 1 , 1)
	gl.glVertex2f( x2 , y2 )
	gl.glTexCoord2f( 0 , 1 )
	gl.glVertex2f( x1, y2 )
	gl.glEnd()
	gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
	gl.glDeleteTextures([ID])
	del ID
	gl.glDisable(gl.GL_TEXTURE_2D)
	return None


def drawText( myText , myFont , textWidth , xLoc , yLoc , fg=[255,255,255,255] , bg=[0,0,0,0] , xCentered=True , yCentered=True , lineSpacing=1.2):
	lineHeight = myFont.getsize('Tj')[0]*lineSpacing
	paragraphs = myText.splitlines()
	renderList = []
	for thisParagraph in paragraphs:
		words = thisParagraph.split(' ')
		if len(words)==1:
			renderList.append(words[0])
			if (thisParagraph!=paragraphs[len(paragraphs)-1]):
				renderList.append(' ')
		else:
			thisWordIndex = 0
			while thisWordIndex < (len(words)-1):
				lineStart = thisWordIndex
				lineWidth = 0
				while (thisWordIndex < (len(words)-1)) and (lineWidth <= textWidth):
					thisWordIndex = thisWordIndex + 1
					lineWidth = myFont.getsize(' '.join(words[lineStart:(thisWordIndex+1)]))[0]
				if thisWordIndex < (len(words)-1):
					#last word went over, paragraph continues
					renderList.append(' '.join(words[lineStart:(thisWordIndex-1)]))
					thisWordIndex = thisWordIndex-1
				else:
					if lineWidth <= textWidth:
						#short final line
						renderList.append(' '.join(words[lineStart:(thisWordIndex+1)]))
					else:
						#full line then 1 word final line
						renderList.append(' '.join(words[lineStart:thisWordIndex]))
						renderList.append(words[thisWordIndex])
					#at end of paragraph, check whether a inter-paragraph space should be added
					if (thisParagraph!=paragraphs[len(paragraphs)-1]):
						renderList.append(' ')
	numLines = len(renderList)
	for thisLineNum in range(numLines):
		if renderList[thisLineNum]==' ':
			pass
		else:
			thisRender = text2numpy( renderList[thisLineNum] , myFont , fg=fg , bg=bg )
			if xCentered:
				x = xLoc - thisRender.shape[1]/2.0
			else:
				x = xLoc
			if yCentered:
				y = yLoc - numLines*lineHeight/2.0 + thisLineNum*lineHeight
			else:
				y = yLoc + thisLineNum*lineHeight
			blitNumpy(numpyArray=thisRender,xLoc=x,yLoc=y,xCentered=False,yCentered=False)
	return None


def drawFeedback(feedbackText,feedbackColor=(127,127,127,255)):
	feedbackArray = text2numpy(feedbackText,feedbackFont,fg=feedbackColor,bg=[0,0,0,0])
	blitNumpy(feedbackArray,stimDisplayRes[0]/2,stimDisplayRes[1]/2,xCentered=True,yCentered=True)


def drawDot(size,xOffset=0,grey=False):
	if grey:
		gl.glColor3f(.25,.25,.25)
	else:
		gl.glColor3f(.5,.5,.5)
	gl.glBegin(gl.GL_POLYGON)
	for i in range(360):
		gl.glVertex2f( stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*size/2 , stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*size/2)
	gl.glEnd()


def drawRing(xOffset,size,thickness,color=.5):
	outer = size/2
	inner = size/2-thickness
	gl.glColor3f(color,color,color)
	gl.glBegin(gl.GL_QUAD_STRIP)
	for i in range(360):
		gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*outer,stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*outer)
		gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(i*math.pi/180)*inner,stimDisplayRes[1]/2 + math.cos(i*math.pi/180)*inner)
	gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(360*math.pi/180)*outer,stimDisplayRes[1]/2 + math.cos(360*math.pi/180)*outer)
	gl.glVertex2f(stimDisplayRes[0]/2+xOffset + math.sin(360*math.pi/180)*inner,stimDisplayRes[1]/2 + math.cos(360*math.pi/180)*inner)
	gl.glEnd()


def drawSquare(xOffset,size):
	gl.glColor3f(.5,.5,.5)
	outer = size
	xOffset = stimDisplayRes[0]/2+xOffset
	yOffset = stimDisplayRes[1]/2
	gl.glBegin(gl.GL_TRIANGLES)
	gl.glVertex2f( xOffset-outer/2 , yOffset-outer/2 )
	gl.glVertex2f( xOffset-outer/2 , yOffset+outer/2 )
	gl.glVertex2f( xOffset+outer/2 , yOffset+outer/2 )
	gl.glEnd()
	gl.glBegin(gl.GL_TRIANGLES)
	gl.glVertex2f( xOffset-outer/2 , yOffset-outer/2 )
	gl.glVertex2f( xOffset+outer/2 , yOffset-outer/2 )
	gl.glVertex2f( xOffset+outer/2 , yOffset+outer/2 )
	gl.glEnd()


def drawDiamond(xOffset,size):
	gl.glColor3f(.5,.5,.5)
	outer = math.sqrt((size**2)*2)
	xOffset = stimDisplayRes[0]/2 + xOffset
	yOffset = stimDisplayRes[1]/2
	gl.glBegin(gl.GL_TRIANGLES)
	gl.glVertex2f( xOffset , yOffset-outer/2 )
	gl.glVertex2f( xOffset-outer/2 , yOffset )
	gl.glVertex2f( xOffset , yOffset+outer/2 )
	gl.glEnd()
	gl.glBegin(gl.GL_TRIANGLES)
	gl.glVertex2f( xOffset , yOffset-outer/2 )
	gl.glVertex2f( xOffset+outer/2 , yOffset )
	gl.glVertex2f( xOffset , yOffset+outer/2 )
	gl.glEnd()

########
# Drawing and helper functions
########


#define a function that gets the time or the time of a provided event
def getTime(eventTimestamp=None):
	if eventTimestamp==None:
		return sdl2.SDL_GetTicks()/1000.0
	else:
		return eventTimestamp/1000.0#*1.0/sdl2.SDL_GetPerformanceFrequency()


#define a function that waits for a given duration to pass
def simpleWait(duration):
	start = getTime()
	while getTime() < (start + duration):
		sdl2.SDL_PumpEvents()


#define a function that will kill everything safely
def exitSafely():
	try:
		dataFile.close()
	except:
		pass
	sdl2.ext.quit()
	sys.exit()



#define a function that waits for a response
def waitForResponse():
	# sdl2.SDL_FlushEvents()
	done = False
	while not done:
		sdl2.SDL_PumpEvents()
		for event in sdl2.ext.get_events():
			if event.type==sdl2.SDL_KEYDOWN:
				if sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()=='escape':
					exitSafely()
				else:
					done = True
			elif event.type==sdl2.SDL_JOYAXISMOTION:
				# print event.jaxis.axis
				done = True
	# sdl2.SDL_FlushEvents()
	return None



#define a function that prints a message on the stimDisplay while looking for user input to continue. The function returns the total time it waited
def showMessage(myText):
	messageViewingTimeStart = getTime()
	stimDisplay.refresh()
	drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
	simpleWait(0.500)
	stimDisplay.refresh()
	waitForResponse()
	stimDisplay.refresh()
	simpleWait(0.500)
	messageViewingTime = getTime() - messageViewingTimeStart
	return messageViewingTime


#define a function that requests user input
def getInput(getWhat):
	getWhat = getWhat
	textInput = ''
	stimDisplay.refresh()
	simpleWait(0.500)
	myText = getWhat+textInput
	drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
	stimDisplay.refresh()
	done = False
	while not done:
		sdl2.SDL_PumpEvents()
		for event in sdl2.ext.get_events():
			if event.type==sdl2.SDL_KEYDOWN:
				response = sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()
				if response=='q':
					exitSafely()
				elif response == 'backspace':
					if textInput!='':
						textInput = textInput[0:(len(textInput)-1)]
						myText = getWhat+textInput
						drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
						stimDisplay.refresh()
				elif response == 'return':
					done = True
				else:
					textInput = textInput + response
					myText = getWhat+textInput
					drawText( myText , instructionFont , stimDisplayRes[0] , xLoc=stimDisplayRes[0]/2 , yLoc=stimDisplayRes[1]/2 , fg=[200,200,200,255] )
					stimDisplay.refresh()
	stimDisplay.refresh()
	return textInput



#define a function that obtains subject info via user input
def getSubInfo():
	year = time.strftime('%Y')
	month = time.strftime('%m')
	day = time.strftime('%d')
	hour = time.strftime('%H')
	minute = time.strftime('%M')
	sid = getInput('ID (\'test\' to demo): ')
	if sid != 'test':
		sex = getInput('Sex (m or f): ')
		age = getInput('Age (2-digit number): ')
		handedness = getInput('Handedness (r or l): ')
	else:
		sex = 'test'
		age = 'test'
		handedness = 'test'
	subInfo = [ sid , year , month , day , hour , minute , sex , age , handedness ]
	return subInfo


def getTrials():
	trialList = []
	for cueLocation in cueLocationList:
		for targetLocation in targetLocationList:
			for targetIdentity in targetIdentityList:
				for i in range(repsPerBlock):
					trialList.append([cueLocation,targetLocation,targetIdentity])
	random.shuffle(trialList)
	return trialList


def getTtoa():
	temp = ttoaMax
	while temp>=ttoaMax:
		temp = ttoaMin + random.expovariate(1.0/(ttoaMean-ttoaMin))
	return temp



def drawCueFunc(cueLocation=None):
	if cueLocation=='left':
		drawRing(xOffset=-offsetSize,size=boxSize,thickness=boxThickness,color=1)
	else:
		drawRing(xOffset=offsetSize,size=boxSize,thickness=boxThickness,color=1)
	return None


def drawTargetFunc(targetLocation=None,targetIdentity=None):
	if targetLocation=='left':
		if targetIdentity=='square':
			drawSquare(xOffset=-offsetSize,size=targetSize)
		else:
			drawDiamond(xOffset=-offsetSize,size=targetSize)
	else:
		if targetIdentity=='square':
			drawSquare(xOffset=offsetSize,size=targetSize)
		else:
			drawDiamond(xOffset=offsetSize,size=targetSize)
	return None


def processInput(responseMade,responses,rts,triggerData,lastLeftTrigger,lastRightTrigger):
	sdl2.SDL_PumpEvents()
	for event in sdl2.ext.get_events() :
		if event.type == sdl2.SDL_JOYAXISMOTION:
			side = 'other'
			if event.jaxis.axis==triggerLeftAxis:
				side = 'left'
				lastThisSide = lastLeftTrigger
				lastLeftTrigger = event.jaxis.value
			elif event.jaxis.axis==triggerRightAxis:
				side = 'right'
				lastThisSide = lastRightTrigger
				lastRightTrigger = event.jaxis.value
			if (side=='left') or (side=='right'):
				#print [event.jaxis.axis,event.jaxis.value,triggerCriterionValue]
				eventTime = getTime(event.jaxis.timestamp)
				triggerData.append([side,eventTime,event.jaxis.value])
				if event.jaxis.value>=triggerCriterionValue:
					if lastThisSide<triggerCriterionValue:
						responseMade = True
						responses.append(side)
						rts.append(eventTime)
		elif event.type == sdl2.SDL_KEYDOWN :
			responseMade = True
			responses.append(sdl2.SDL_GetKeyName(event.key.keysym.sym).lower())
			rts.append(getTime(event.key.timestamp))
	return [responseMade,responses,rts,triggerData,lastLeftTrigger,lastRightTrigger]

def addTrial(cueOnTimeList,cueOffTimeList,targetOnTimeList,targetOffTimeList):
	cueOnTimeList.append(targetOffTimeList[0]+feedbackDuration+fixationDuration)
	cueOffTimeList.append(cueOnTimeList[-1]+cueDuration)
	targetOnTimeList.append(cueOnTimeList[-1]+soa)
	targetOffTimeList.append(targetOnTimeList[-1]+targetDuration)
	return [cueOnTimeList,cueOffTimeList,targetOnTimeList,targetOffTimeList]



def runBlock(block,soaType,soa=None):
	trialList = getTrials()
	if block==0:
		trialList = trialList[0:trialsPerPractice]

	cueList = [trialInfo[0] for trialInfo in trialList]
	targetList = [trialInfo[1:3] for trialInfo in trialList]
	feedback = '000'

	drawFeedback(feedback)
	drawRing(xOffset=-offsetSize,size=boxSize,thickness=boxThickness,color=.1)
	drawRing(xOffset=offsetSize,size=boxSize,thickness=boxThickness,color=.1)
	stimDisplay.refresh() #should not block
	drawFeedback(feedback)
	drawRing(xOffset=-offsetSize,size=boxSize,thickness=boxThickness,color=.1)
	drawRing(xOffset=offsetSize,size=boxSize,thickness=boxThickness,color=.1)
	stimDisplay.refresh() #should block until it's actually drawn
	
	#get the trial start time 
	blockStartTime = getTime()-(1.000/60.0)

	#compute stim times
	targetOnTimeList = [blockStartTime+getTtoa()]
	if soaType=='random':
		cueOnTimeList = [getTtoa()]
		for i in range(len(trialList)-1):
			cueOnTimeList.append(cueOnTimeList[-1]+getTtoa())
			targetOnTimeList.append(targetOnTimeList[-1]+getTtoa())
	elif soaType=='fixed':
		cueOnTimeList = [targetOnTimeList[0]-soa]
		for i in range(len(trialList)-1):
			targetOnTimeList.append(targetOnTimeList[-1]+getTtoa())
			cueOnTimeList.append(targetOnTimeList[-1]-soa)
	elif soaType=='mixed':
		cueOnTimeList = [targetOnTimeList[0]-random.choice(fixedSoaList)]
		for i in range(len(trialList)-1):
			targetOnTimeList.append(targetOnTimeList[-1]+getTtoa())
			cueOnTimeList.append(targetOnTimeList[-1]-random.choice(fixedSoaList))
	elif soaType=='namixed':
		cueOnTimeList = [targetOnTimeList[0]-random.choice(naFixedSoaList)]
		for i in range(len(trialList)-1):
			targetOnTimeList.append(targetOnTimeList[-1]+getTtoa())
			cueOnTimeList.append(targetOnTimeList[-1]-random.choice(naFixedSoaList))


	cueOnErrorList = []
	cueOffErrorList = []
	targetOnErrorList = []
	targetOnTimeListToWrite = []
	cueOnTimeListToWrite = []

	lastLeftTrigger = -1
	lastRightTrigger = -1
	triggerData = []

	responses = []
	rts = []
	responseMade = False

	drawCue = False
	getCueOnError = False
	getCueOffError = False
	drawTarget = False
	getTargetOnError = False
	drawUpdate = False
	lastTargetOnTime = 0

	while (len(cueOffTimeList)>0)|(len(targetOffTimeList)>0):
		responseMade,responses,rts,triggerData,lastLeftTrigger,lastRightTrigger = processInput(responseMade,responses,rts,triggerData,lastLeftTrigger,lastRightTrigger)
		now = getTime()
		if len(cueOnTimeList)>0:
			if now>=cueOnTimeList[0]:
				drawUpdate = True
				drawCue = True
				getCueOnError = True
				lastCueOnTime = cueOnTimeList[0]
				cueOnTimeList.pop(0)
				cueOnTimeListToWrite.append(lastCueOnTime)
		if len(cueOffTimeList)>0:
			if now>=cueOffTimeList[0]:
				drawUpdate = True
				drawCue = False
				getCueOffError = True
				lastCueOffTime = cueOffTimeList[0]
				cueOffTimeList.pop(0)
				cueList.pop(0)
		if len(targetOnTimeList)>0:
			if now>=targetOnTimeList[0]:
				drawUpdate = True
				drawTarget = True
				getTargetOnError = True
				lastTargetOnTime = targetOnTimeList[0]
				targetOnTimeList.pop(0)
				targetOnTimeListToWrite.append(lastTargetOnTime)
		if len(targetOffTimeList)>0:
			if now>=targetOffTimeList[0]:
				drawUpdate = True
				drawTarget = False
				targetOffTimeList.pop(0)
				targetList.pop(0)
				feedback = 'XXX'
				responses.append('NA')
				rts.append('NA')
		if responseMade:
			responseMade = False
			drawUpdate = True
			if responses[-1] == 'escape':
				exitSafely()
			else:
				if (rts[-1]>lastTargetOnTime)&(rts[-1]<(lastTargetOnTime+targetDuration)):
					feedback = str(int((rts[-1]-lastTargetOnTime)*1000))
					drawUpdate = True
					drawTarget = False
					targetOffTimeList.pop(0)
					targetList.pop(0)
				else:
					feedback = 'XXX'
		if drawUpdate:
			drawUpdate = False
			drawFeedback(feedback)
			drawRing(xOffset=-offsetSize,size=boxSize,thickness=boxThickness,color=.1)
			drawRing(xOffset=offsetSize,size=boxSize,thickness=boxThickness,color=.1)
			if drawCue:
				drawCueFunc(cueList[0])
			if drawTarget:
				drawTargetFunc(targetList[0][0],targetList[0][1])
			stimDisplay.refresh() #should not block
			drawFeedback(feedback)
			drawRing(xOffset=-offsetSize,size=boxSize,thickness=boxThickness,color=.1)
			drawRing(xOffset=offsetSize,size=boxSize,thickness=boxThickness,color=.1)
			if drawCue:
				drawCueFunc(cueList[0])
			if drawTarget:
				drawTargetFunc(targetList[0][0],targetList[0][1])
			stimDisplay.refresh() #should block
			drawTime = getTime()-(1000/60.0)
			if getCueOnError:
				getCueOnError = False
				cueOnErrorList.append(drawTime-lastCueOnTime)
			if getCueOffError:
				getCueOffError = False
				cueOffErrorList.append(drawTime-lastCueOffTime)
			if getTargetOnError:
				getTargetOnError = False
				targetOnErrorList.append(drawTime-lastTargetOnTime)
	start = getTime()
	while getTime() < (start + 2.00):
	# while (lastLeftTrigger>(-(2**16)/2)) & (lastRightTrigger>(-(2**16)/2)):
		sdl2.SDL_PumpEvents()
		responseMade,responses,rts,triggerData,lastLeftTrigger,lastRightTrigger = processInput(responseMade,responses,rts,triggerData,lastLeftTrigger,lastRightTrigger)
	dataFile.write('\t'.join(map(str,trialList))+'\n')
	dataFile.write('\t'.join(map(str,cueOnTimeListToWrite))+'\n')
	dataFile.write('\t'.join(map(str,targetOnTimeListToWrite))+'\n')
	dataFile.write('\t'.join(map(str,responses))+'\n')
	dataFile.write('\t'.join(map(str,rts))+'\n')
	dataFile.write('\t'.join(map(str,cueOnErrorList))+'\n')
	dataFile.write('\t'.join(map(str,cueOffErrorList))+'\n')
	dataFile.write('\t'.join(map(str,targetOnErrorList))+'\n')
	dataFile.write('\t'.join(['\t'.join(map(str,i)) for i in triggerData])+'\n')

########
# Start the experiment by getting subject info
########
subInfo = getSubInfo()


########
# Initialize data files
########
if not os.path.exists('_Data'):
	os.mkdir('_Data')
if subInfo[0]=='test':
	filebase = 'test'
else:
	filebase = '_'.join(subInfo[0:6])
if not os.path.exists('_Data/'+filebase):
	os.mkdir('_Data/'+filebase)

shutil.copy(sys.argv[0], '_Data/'+filebase+'/'+filebase+'_code.py')

dataFile = open('_Data/'+filebase+'/'+filebase+'_data.txt','w')
dataFile.write(str(seed)+'\n')
dataFile.write('\t'.join(map(str,subInfo))+'\n')

if subInfo[0]=='test':
	soaTypeList = [soaTypeList[0],soaTypeList[1]]
	fixedSoaList = fixedSoaList
else:
	if int(subInfo[0])%12==0:
		soaTypeList = [soaTypeList[0],soaTypeList[1]]
		fixedSoaList = [fixedSoaList[0],fixedSoaList[1],fixedSoaList[2]]
	elif int(subInfo[0])%12==1:	
		soaTypeList = [soaTypeList[1],soaTypeList[0]]
		fixedSoaList = [fixedSoaList[0],fixedSoaList[1],fixedSoaList[2]]
	elif int(subInfo[0])%12==2:
		soaTypeList = [soaTypeList[0],soaTypeList[1]]
		fixedSoaList = [fixedSoaList[0],fixedSoaList[2],fixedSoaList[1]]
	elif int(subInfo[0])%12==3:	
		soaTypeList = [soaTypeList[1],soaTypeList[0]]
		fixedSoaList = [fixedSoaList[0],fixedSoaList[2],fixedSoaList[1]]
	elif int(subInfo[0])%12==4:
		soaTypeList = [soaTypeList[0],soaTypeList[1]]
		fixedSoaList = [fixedSoaList[1],fixedSoaList[0],fixedSoaList[2]]
	elif int(subInfo[0])%12==5:	
		soaTypeList = [soaTypeList[1],soaTypeList[0]]
		fixedSoaList = [fixedSoaList[1],fixedSoaList[0],fixedSoaList[2]]
	elif int(subInfo[0])%12==6:
		soaTypeList = [soaTypeList[0],soaTypeList[1]]
		fixedSoaList = [fixedSoaList[1],fixedSoaList[2],fixedSoaList[0]]
	elif int(subInfo[0])%12==7:	
		soaTypeList = [soaTypeList[1],soaTypeList[0]]
		fixedSoaList = [fixedSoaList[1],fixedSoaList[2],fixedSoaList[0]]
	elif int(subInfo[0])%12==8:
		soaTypeList = [soaTypeList[0],soaTypeList[1]]
		fixedSoaList = [fixedSoaList[2],fixedSoaList[0],fixedSoaList[1]]
	elif int(subInfo[0])%12==9:	
		soaTypeList = [soaTypeList[1],soaTypeList[0]]
		fixedSoaList = [fixedSoaList[2],fixedSoaList[0],fixedSoaList[1]]
	elif int(subInfo[0])%12==10:
		soaTypeList = [soaTypeList[0],soaTypeList[1]]
		fixedSoaList = [fixedSoaList[2],fixedSoaList[1],fixedSoaList[0]]
	elif int(subInfo[0])%12==11:	
		soaTypeList = [soaTypeList[1],soaTypeList[0]]
		fixedSoaList = [fixedSoaList[2],fixedSoaList[1],fixedSoaList[12]]



########
# Run blocks
########

messageViewingTime = showMessage('Press any key to begin practice.')			
for soaType in soaTypeList:
	for soa in fixedSoaList:
		for block in range(blocksPerSoa):
			runBlock(block=block,soaType=soaType,soa=soa)
			if block==0:
				messageViewingTime = showMessage('Practice is complete.\nWhen you are ready to begin the experiment, press any key.')
			else:
				if block<(blocksPerSoa-1):
					messageViewingTime = showMessage('Take a break!\nWhen you are ready to resume the experiment, press any key.')
		if soa!=fixedSoaList[-1]:
			if soaType=='fixed':
				messageViewingTime = showMessage('The timing will now change slightly.\n\nPress any key to begin practice with this new timing')
			else:
				messageViewingTime = showMessage('Take a break!\nWhen you are ready to resume the experiment, press any key.')
	if soa!=soaTypeList[-1]:
		messageViewingTime = showMessage('The timing will now change slightly.\n\nPress any key to begin practice with this new timing')			

messageViewingTime = showMessage('You\'re all done!\nPlease alert the person conducting this experiment that you have finished.')

exitSafely()
