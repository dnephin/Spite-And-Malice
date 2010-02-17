"""
 A model of the spite and malice game. 
 Limits the moves to only those that are possible according to the rules.
"""

from cardmodels import Deck, Pile, Card
from copy import deepcopy

PAY_OFF = 'pay_off'
HAND = 'hand'
DISCARD = 'discard'
CENTER = 'center'


class InvalidMove(ValueError): 
	" thrown when a player attempts an invalid move "
	pass


class SpiteAndMaliceModel(object):

	NUM_STACKS = 4

	def __init__(self):
		" Initialize the game to a starting state "
		# shuffle two packs together
		all_cards = Pile(Deck(num_packs=2))

		# id of the active player
		self.active_player = None
		self.players = [{}, {}]
		for player in self.players:
			# deal 20 cards to each players pay-off pile
			player[PAY_OFF] = Pile(all_cards.draw(num=20))
			player[PAY_OFF].flip()
			# deal 5 cards to each players hard
			player[HAND] = Pile(all_cards.draw(num=5))
			player[HAND].flip(all=True)
			# four discard stacks
			player[DISCARD] = []
			for i in range(self.NUM_STACKS):
				pile = Pile([])
				pile.flip(all=True)
				player[DISCARD].append(pile)

		# rest of cards go to the stock
		self.stock = all_cards

		# create 4 empty center stacks
		self.center_stacks = []
		for i in range(self.NUM_STACKS):
			pile = Pile([])
			pile.flip(all=True)
			self.center_stacks.append(pile)


	def build_view_for_player(self):
		" Return a copy of the current view of the board for the player. "
		player_id = self.active_player
		# copy of the visible cards for player
		player = self.players[player_id]
		player_cards = {
			HAND: deepcopy(player[HAND]),
			PAY_OFF: player[PAY_OFF].visible()[-1],
			DISCARD: deepcopy(player[DISCARD])
			}
		# copy of visible cards of his opponent
		opponent = self.players[int(not player_id)]
		opponent_cards = {
			PAY_OFF: opponent[PAY_OFF].visible()[-1],
			DISCARD: deepcopy(opponent[DISCARD])
			}
		# the top card from the center stacks
		center_stacks = []
		for pile in self.center_stacks:
			if len(pile) > 0:
				center_stacks.append(pile.visible()[-1])
			else:
				center_stacks.append(None)
		return (player_cards, opponent_cards, center_stacks)


	def can_place_card_in_center(self, center_id, card):
		"""
		Determins if card can be played on the center stack center_id. 
		Returns true if it can be placed, false otherwise.
		"""
		pile = self.center_stacks[center_id]
		value = card[0]
		# king can be placed on anything
		if value == 'K':
			return True
		# ace can be played on empty piles
		if value == 'A':
			return (len(pile) == 0)

		# convert letters into numeric values
		value = Card.to_numeric_value(card)
		top_value = len(pile)
		return (value - top_value == 1)


	def place_card(self, card, from_location, to_location):
		"""
		Place a card onto a stack. Inputs are:
		card is the card to be placed
		from_location is a tuple of the pile (HAND, DISCARD or PAY_OFF) and the id of the pile
		to_location is a tuple of the pile (DISCARD or CENTER), and the id of the pile

		Returns the id of the player who gets to play next.
		"""
		if not Card.is_valid(card):
			raise InvalidMove("Unknown card %s." % (card))
		if len(from_location) != 2 or from_location[0] not in (HAND, DISCARD, PAY_OFF):
			raise InvalidMove("from_location of incorrect size or location: %s." % (from_location))
		if len(to_location) != 2 or to_location[0] not in (DISCARD, CENTER) or \
				to_location[1] < 0 or to_location[1] >= self.NUM_STACKS:
			raise InvalidMove("to_location of incorrect size or location: %s." % (to_location))
		if to_location[0] == CENTER and not self.can_place_card_in_center(to_location[1], card):
			raise InvalidMove("Can not place card(%s) on center stack %s." % (card, to_location[1]))
		
		# remove it from old location
		player = self.players[self.current_player]
		if from_location[0] == HAND and card in player[HAND]:
			player[HAND].remove(card)
		elif from_location[0] == DISCARD and card in player[DISCARD][from_location[1]]:
			player[DISCARD][from_location[1]].remove(card)
		elif from_location[0] == PAY_OFF and card == player[PAY_OFF][-1]:
			player[PAY_OFF].pop()
		else:
			raise InvalidMove("Could not find card(%s) in %s." % (card, from_location))

		# place it in new location
		if to_location[0] == CENTER:
			self.center_stacks[to_location[1]].append(card)
		elif to_location[0] == DISCARD:
			player[DISCARD][to_location[1]].append(card)


	def mix_into_stock(self):
		""" 
		Search each of the center stacks for completion, and re-add the completed 
		center pile into the bottom of the stock.
		"""
		for pile in self.center_stacks:
			if len(pile) == 12:
				pile.shuffle()
				self.stock.add_cards(pile.draw(num=12), cards_to=Pile.BOTTOM)


	def is_won(self):
		" Check if the game has been won "
		return (len(self.players[self.active_player][PAY_OFF]) == 0)


