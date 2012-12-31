#!/usr/bin/env python
import select, socket, sys, cPickle, time, pygame
from protocolObjects import *
from pygame.locals import *
from socket import *


class gracz(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		if len(sys.argv) != 2:
	  		raise AttributeError("Incorrect number of arguments. You should pass ip:port as only argument.")
		host,port = sys.argv[1].split(':')

		self.port = int(port)
		self.host = host
		self.soc = socket(AF_INET, SOCK_STREAM)
		self.soc.connect((self.host, self.port))
		self.soc.setblocking(0)
		print "Connected to %s:%d" % (self.host, self.port)
		self.ID = None
		self.run = True
		self.resss = True
		self.map = pygame.image.load('map.png')
		self.mine = pygame.image.load('mine.png')
		self.plist = [pygame.image.load(str(x)+'.png') for x in range(1,3)]
  
  	def send(self,dane):
		_, toWrite, _ = select.select([], [self.soc], [])
		data = toWrite[0].sendall( cPickle.dumps( dane ) )
		if data: raise Exception("Problem with sending data to the socket: %s" %data)
  
  	def receive(self):
		toRead, _, _ = select.select([self.soc], [], [])
		rec = toRead[0].recv(4096)
		if len(rec) == 0:
	  		return None
		data = None
		while data == None:
	  		try:
				data = cPickle.loads( rec )
	  		except (EOFError, cPickle.UnpicklingError, ValueError):
				rec += toRead[0].recv(4096)
		return data
	
  	def draw(self,scr,i,pos):
  		os = self.plist[i].convert_alpha()
		scr.blit(os, pos)
	
  	def update(self):
		self.rect.centerx = self.x
		self.rect.centery = self.y

  	def start(self):
		clock = pygame.time.Clock()
		while self.run:
	  		clock.tick(15)
	  		data = self.receive()
	  		if data == None: continue
	  		if isinstance(data,Countdown):
				if data.number == 3:
		  			pygame.init()
		  			screen = pygame.display.set_mode((data.mapSize[0], data.mapSize[1]))
		  			self.ID = data.playerId
		  			pygame.display.set_caption("Player " + str(self.ID+1))
		  			font = pygame.font.Font(None, 72)
				tekst = font.render(str(data.number),True,(0,0,0))
				screen.fill((250,250,250))
				screen.blit(tekst,(300,200))
				time.sleep(1)
				PlayerAction.action = 'n'

	  		elif isinstance(data,Map):
				warstwa = pygame.image.load('map.png').convert_alpha()
				b = pygame.image.load('mine.png').convert_alpha()
				for i in data.mines:
		  			warstwa.blit(b,i.position)
				for i,pos in enumerate(data.playersPositions):
		  			self.draw(warstwa,i,(pos.x,pos.y))
				pressed_keys = pygame.key.get_pressed()
				for event in pygame.event.get():
		  			if event.type == QUIT:
						self.send('koniec')
						exit()
				if pressed_keys[K_LEFT]:
					PlayerAction.action = 'left'
				elif pressed_keys[K_RIGHT] :
					PlayerAction.action = 'right'
				elif pressed_keys[K_UP]:
					PlayerAction.action = 'up'
				elif pressed_keys[K_DOWN]:
					PlayerAction.action = 'down'
				elif pressed_keys[K_LCTRL]:
					PlayerAction.action = 'result'
				elif pressed_keys[K_SPACE]:
					PlayerAction.action = 'bomb'
				else:
					PlayerAction.action = 'none'
				screen.blit(warstwa,(0,0))
				self.send(PlayerAction.action)
	  
	  		elif isinstance(data,Result):
				tekst = font.render('Game Over',True, (30,100,200))
				tekst2 = font.render('Winner: Player ' + str(data.winners + 1), True, (0,0,0))
				tekst3 = font.render('Score: ' + str(data.scores), True, (0,0,0))
				screen.fill((250,250,250))
				screen.blit(tekst,(50,50))
				screen.blit(tekst2,(50,200))
				screen.blit(tekst3,(50,300))
				pygame.display.update()
				time.sleep(10)
				self.resss = False
				self.run = False
				break
	  		elif data == 'koniec':
				break
	  		pygame.display.update()
		if self.resss:
	  		self.send('koniec')
		self.soc.close()
		exit()

p = gracz()
p.start()