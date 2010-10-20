"""
 Models for games with playing cards.
 Note: these classes use unicode characters to display suits. Changing
 your default encoding to UTF-8 is recommended.
"""

import random



class Suits:
	"""
	Statics for the suits
	"""
	HEART = u'\u2660'
	DIAMOND = u'\u2666'
	CLUB = u'\u2663'
	SPADE = u'\u2666'

class Card:
	" Class to verify that a card is valid "
	values = "A234567890JQK"

	@staticmethod
	def is_valid(card):
		" Check if card is in a valid format, and represents a real card "
		if len(card) != 2:
			return False
		if card[1] not in (Suits.HEART, Suits.DIAMOND, Suits.CLUB, Suits.SPADE):
			return False
		if card[0] not in Card.values:
			return False
		return True

	@staticmethod
	def to_numeric_value(card):
		" convert the value of the card to an int "
		if not card:
			return 0
		value = card[0]
		if value == 'A':
			return 1
		if value == '0':
			return 10
		if value == 'J':
			return 11
		if value == 'Q':
			return 12
		if value == 'K':
			return 13
		if value == 'O':
			return 14
		return int(value)

class Deck(list):
	"""
	A deck of cards. Has the following actions:
	Deck(num_packs=1, jokers=False) - pack is 52 cards, jokers to include them
	shuffle() - shuffles the pack
	"""
	def __init__(self, num_packs=1, jokers=False):
		" create the deck of cards "
		list.__init__(self)
		for pack in range(num_packs):
			for suit in [Suits.HEART, Suits.DIAMOND, Suits.CLUB, Suits.SPADE]:
				values = Card.values
				for value in values:
					self.append(value + suit)
			if jokers:
				self.append('O' + Suits.SPADE)
				self.append('O' + Suits.DIAMOND)
		self.shuffle()

	def __repr__(self):
		return u' '.join(self)

	def shuffle(self):
		" shuffle the deck(s) of cards "
		random.shuffle(self)


class Pile(Deck):
	"""
	A pile of cards. Some can be visible.
	"""
	TOP = "top"
	BOTTOM = "bottom"
	RANDOM = "random"

	def __init__(self, cards):
		list.__init__(self, cards)
		self.visible_index = None

	def draw(self, num=1, cards_from="top"):
		" Draw a card from the pile "
		cards = []
		for i in range(num):
			if len(self) == 0:
				return cards
			if cards_from == Pile.TOP:
				cards.append(self.pop())
			elif cards_from == Pile.BOTTOM:
				cards.append(self.pop(0))
			elif cards_from == Pile.RANDOM:
				card = random.choice(self)
				self.remove(card)
				cards.append(card)
		return cards

	def add_cards(self, cards, cards_to="bottom"):
		" Add cards back to the pile "
		if cards_to == Pile.TOP:
			self.extend(cards)
		elif cards_to == Pile.BOTTOM:
			current_pile = list(self)
			self[:] = cards
			self.extend(current_pile)
		elif cards_to == Pile.RANDOM:
			#TODO: 
			self.extend(cards)
				
	def visible(self):
		" return the list of visible cards "
		if self.visible_index == None:
			return []
		return self[self.visible_index:]

	def flip(self, num_cards=1, all=False):
		" set this number of cards to the visible state "
		if self.visible_index == None:
			self.visible_index = 0
		self.visible_index -= num_cards
		if all:
			self.visible_index = 0
		return self.visible()

	def __repr__(self):
		if self.visible_index == None:
			visible = 0
		elif self.visible_index == 0:
			visible = -len(self)
		else:
			visible = self.visible_index
		return "xx " * (len(self) + visible) + " ".join(self.visible())


