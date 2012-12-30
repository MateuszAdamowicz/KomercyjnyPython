#!/usr/bin/env python 
import select, socket, sys, cPickle, time
from protocolObjects import *
#dsadada
class Serwer(object):
	def __init__(self):
		if len(sys.argv) != 2:
			raise AttributeError("Incorrect number of arguments. You should pass ip:port as only argument.")
		host, port = sys.argv[1].split(":")
		self.host = host 
		self.port = int(port)
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		self.server.bind((self.host,self.port)) 
		self.server.listen(5)
		self.input = [self.server]
		Map.playersPositions = []
		Map.mines = []
		self.pkt = 0
		self.mapSize = 640,480
		self.odwiedzone = []

		self.run = True
		self.gracze = {}
		self.graczID = 0
		self.koniec = True
		self.resultat = False

	def send(self,dane,client):
		_, toWrite, _ = select.select([], [client], [])
		data = toWrite[0].sendall( cPickle.dumps( dane ) )
		if data: raise Exception("Problem z wyslaniem msg do socketu: %s" %data)
		
	def receive(self,client):
		toRead, _, _ = select.select([client], [], [])
		dane = toRead[0].recv(4096)
		if len(dane) == 0:
			return None
		data = None
		while data == None:
			try:
				data = cPickle.loads( dane )
			except (EOFError, cPickle.UnpicklingError, ValueError):
				dane += toRead[0].recv(4096)
		return data

	def odliczaj(self,i,id):
		if i == 0:
			obiekt=Countdown(3,self.mapSize,id)
			if id == 0:
				x = 5
				y = 5
			elif id == 1:
				x =605
				y =445
			Map.playersPositions.append(Position(y,x))
								
		if i == 1:
			obiekt=Countdown(2,self.mapSize,id)
		if i == 2:
			obiekt=Countdown(1,self.mapSize,id)
		if i == 3:
			obiekt=Map([],Map.playersPositions)
		return obiekt
	def fun_res(self,x,y):
		if (x, y) not in self.odwiedzone:
			(self.odwiedzone).append((x, y))
			if x >=0 and x<640 and y >= 0 and y < 480:
				self.dod = True
				for i in self.miny:
					if (x, y) == i.position:
						self.dod = False
				if self.dod:
					self.pkt += 1
					self.fun_res(x - 40, y)
					self.fun_res(x + 40, y)
					self.fun_res(x, y - 40)
					self.fun_res(x, y + 40)
	
	def akcja(self,id,data):
		x=(Map.playersPositions[id]).x
		y=(Map.playersPositions[id]).y
		if data == 'up':
			if y > 40:
				if (Position(y-40,x)) not in Map.playersPositions:
					Map.playersPositions[(id)] = Position(y-40,x)
				for i in self.miny:
					if (x,y-40) == i.position:
						k = (id + 1) % len(gracze)
						Result.winners = k
						Result.scores = 'max'
						return Result(Result.winners,Result.scores)
		elif data == 'down':
			if y < 440:
				if (Position(y+40,x)) not in Map.playersPositions:
					Map.playersPositions[(id)] = Position(y+40,x)
				for i in self.miny:
					if (x,y+40) == i.position:
						k = (id + 1) % len(gracze)
						Result.winners = k
						Result.scores = 'max'
						return Result(Result.winners,Result.scores)
		elif data == 'right':
			if x < 600:
				if (Position(y,x+40)) not in Map.playersPositions:
					Map.playersPositions[(id)] = Position(y,x+40)
				for i in self.miny:
					if (x+40,y) == i.position:
						k = (id + 1) % len(gracze)
						Result.winners = k
						Result.scores = 'max'
						return Result(Result.winners,Result.scores)
		elif data == 'left':
			if x > 40:
				if (Position(y,x-40)) not in Map.playersPositions:
					Map.playersPositions[(id)] = Position(y,x-40)
				for i in self.miny:
					if (x-40,y) == i.position:
						k = (id + 1) % len(gracze)
						Result.winners = k
						Result.scores = 'max'
						return Result(Result.winners,Result.scores)
		elif data == 'result':
			makss = (0,0)
			for client in gracze:
				self.pkt = 0
				self.odwiedzone = []
				xx = (Map.playersPositions[gracze[client]]).x
				yy = (Map.playersPositions[gracze[client]]).y
				self.fun_res(xx,yy)
				if makss[0] < self.pkt:
					makss = (self.pkt, gracze[client])
				elif makss[0] == self.pkt:
					k = (id + 1) % len(gracze)
					makss = (self.pkt, k)
				self.odwiedzone = []
			Result.winners = makss[1]
			Result.scores = makss[0]
			return Result(Result.winners,Result.scores)
		
		elif data == 'none':
			Map.playersPositions[(id)] = Position(y,x)
		elif data == 'koniec':
			for client in gracze:
				self.send('koniec',client)
			self.server.close()
		elif data == 'bomb':
			self.warunek = True
			if x%40 == 5 and y%40 == 5:
				for i in self.miny:
					if i.position == (x, y):
						self.warunek = False
				if self.warunek:
					bomba = Mine((x,y),id)
					Map.mines.append(bomba)
		self.miny= Map.mines
		return Map(Map.mines,Map.playersPositions)

	def start(self):
		while self.run:
			inputready,outputready,exceptready = select.select(self.input,[],[])
			for s in self.input:
				if s == self.server:
					while True:
						client,addr = self.server.accept()
						self.gracze[client] = self.graczID
						print ('Polaczono z ',addr)
						self.graczID += 1
						if self.graczID == 2:
							break
					for i in range(4):
						for client in self.gracze:
							self.send(self.odliczaj(i,self.gracze[client]),client)
							time.sleep(1)

					while 1:
						if self.koniec:
							for client in self.gracze:
								if self.resultat:
									data = self.receive(client)
									self.send(res,client)
									self.koniec = False
									break
								else:
									data = self.receive(client)
									k = self.akcja(self.gracze[client],data)
									if isinstance(k,Result):
										self.resultat = True
										res = k
									self.send(k,client)
						else:
							self.server.close()
							self.run = False
							break

				if s == sys.stdin:
					self.junk = sys.stdin.readline()
					self.run = False			

s = Serwer()
s.start()
