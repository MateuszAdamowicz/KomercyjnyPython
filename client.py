#!/usr/bin/env python 
import pygame, select, cPickle
from pygame.locals import *
from sys import exit
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
  
  def send(self,dane):
    _, toWrite, _ = select.select([], [self.soc], [])
    data = toWrite[0].sendall( cPickle.dumps( dane ) )
    if data: raise Exception("Problem z wyslaniem msg do socketu: %s" %data)
  
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
    i += 1
    if i == 1:
      os = pygame.image.load('gr.png').convert_alpha()
    else:
      os = pygame.image.load('gr2.png').convert_alpha()
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
          self.ID = data.playerID
          pygame.display.set_caption("gracz " + str(self.ID+1))
          font = pygame.font.Font("CatShop.ttf", 72)