import sdl2
import sdl2.ext
sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK) #uncomment if you want joystick input
sdl2.SDL_JoystickOpen(0) #uncomment if you want joystick input

while True:
	sdl2.SDL_PumpEvents()
	for event in sdl2.ext.get_events() :
		if event.type==sdl2.SDL_KEYDOWN:
			print sdl2.SDL_GetKeyName(event.key.keysym.sym).lower()
		elif event.type==sdl2.SDL_JOYAXISMOTION:
			print [event.jaxis.axis,event.jaxis.value]

