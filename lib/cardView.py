"""
 View of the cards, image loading, etc.
"""

import pygame 
from pygame.locals import *
from cardmodels import Suits, Card
							 
class CardImages(object):
	" Loads card images "

	image_dir = './media/cards'
	
	cardImages = {}
	backImage = None
	suit_to_let = {Suits.SPADE: 's', Suits.CLUB: 'c', Suits.DIAMOND: 'd', Suits.HEART: 'h'}

	def __init__(self):
		for suit in self.suit_to_let.keys():
			for value in Card.values:
				self.cardImages[value + suit] = pygame.image.load("%s/%s%s.gif" % (
						self.image_dir, value.lower(), self.suit_to_let[suit])).convert()

		self.backImage = pygame.image.load("%s/b.gif" % (self.image_dir))

	def getCard(self, card):
		" get a cards image "
		return self.cardImages[card]

	def getBack(self):
		return self.backImage


class CardGroup(list):
	" A group of cards to capture clicks "

	def __init__(self):
		self.card_images = CardImages()
		list.__init__(self)


	def makeCard(self, card):
		" Make a card, and add it to this group "
		card = self.card_images.getCard(card)
		self.append(card)
		return card


	def makeBlank(self):
		# TODO: new image for blank
		return self.makeBack()


	def makeBack(self):
		card = self.card_images.getBack()
		self.append(card)
		return card
