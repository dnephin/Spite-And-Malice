"""
 View of the cards, image loading, etc.
"""

import pygame 
from pygame.locals import *
from cardmodels import Suits, Card
							 

class CardView(object):
	
	def __init__(self, img_surface, model):
		self.surface = img_surface
		self.loc = img_surface.get_rect()
		self.model = model

	def place(self, surface, rect):
		" Blit the card onto the surface, and save the location "
		self.loc = rect
		surface.blit(self.surface, rect)

	def getLocRect(self):
		pass

	def get_rect(self, *args, **kwargs):
		return self.surface.get_rect(*args, **kwargs)

	def __repr__(self):
		return repr(self.model)


class CardImages(object):
	" A Factory for CardView objects "

	image_dir = './media/cards'
	
	cardImages = {}
	backImage = None
	blankImage = None
	suit_to_let = {Suits.SPADE: 's', Suits.CLUB: 'c', Suits.DIAMOND: 'd', Suits.HEART: 'h'}

	def __init__(self):
		for suit in self.suit_to_let.keys():
			for value in Card.values:
				self.cardImages[value + suit] = pygame.image.load("%s/%s%s.gif" % (
						self.image_dir, value.lower(), self.suit_to_let[suit])).convert()

		self.backImage = pygame.image.load("%s/b.png" % (self.image_dir))
		self.blankImage = pygame.image.load("%s/blank.gif" % (self.image_dir))

	def getCard(self, card):
		" get a cards image "
		return CardView(self.cardImages[card], card)

	def getBack(self):
		return CardView(self.backImage, None)

	def getBlank(self):
		return CardView(self.blankImage, None)

class CardGroup(list):
	" A group of cards to capture clicks "

	def __init__(self):
		self.card_images = CardImages()
		self.selected_id = None
		list.__init__(self)


	def makeCard(self, card, location):
		" Make a card, and add it to this group "
		card = self.card_images.getCard(card)
		self.append((card, location))
		return card


	def makeBlank(self, location):
		card = self.card_images.getBlank()
		self.append((card, location))
		return card


	def makeBack(self, location):
		card = self.card_images.getBack()
		self.append((card, location))
		return card

	def findClick(self, event):
		" Find if the click was on a card in this CardGroup "
		for index in range(len(self)-1,-1,-1):
			rect = self[index][0].loc
			print "index[%s] card(%s) mouse(%s,%s)" % (index, rect, event.pos[0], event.pos[1])
			if rect.collidepoint(event.pos[0], event.pos[1]):
			 	self.selected_id = index
				return True
		return False

	def getSelected(self):
		" return the selected entry "
		return self[self.selected_id]

	def addCard(self, card, location):
		" Add an already created card to group "
		self.append((card, location))

