"""
 A model of the spite and malice game. 
 Limits the moves to only those that are possible according to the rules.
"""

from cardmodels import Deck, Pile, Card
from copy import deepcopy
import logging

log = logging.getLogger('snm.model')

PAY_OFF = 'pay_off'
HAND = 'hand'
DISCARD = 'discard'
CENTER = 'center'


class InvalidMove(ValueError): 
	" thrown when a player attempts an invalid move "
	pass


class PlayerMove(object):
	" A data transfer object for plaers moves. "
	def __init__(self, card, from_location=None, to_location=None,
			from_pile=None, from_id=None, to_pile=None, to_id=None):
		self.card = card
		# set from 
		if from_location and len(from_location) == 2:
			self.from_pile = from_location[0]
			self.from_id = from_location[1]
		elif from_pile:
			self.from_pile = from_pile
			self.from_id = from_id
		else:
			raise InvalidMove("Could not find a from location.")

		# set to
		if to_location and len(to_location) == 2:
			self.to_pile = to_location[0]
			self.to_id = to_location[1]
		elif to_pile and to_id != None:
			self.to_pile = to_pile
			self.to_id = to_id
		else:
			raise InvalidMove("Could not find a to location.")

	def __str__(self):
		" String representation of this dto "
		from_id = self.from_id
		to_id = self.to_id
		if self.from_id == None or self.from_pile in [HAND, PAY_OFF]:
			from_id = ''
		if self.to_id == None:
			to_id = ''
		return "Move(%s %s[%s] -> %s %s)" % (self.from_pile, from_id, self.card,
				self.to_pile, to_id)

	def __eq__(self, other):
		if other == None or type(other) != PlayerMove:
			return False
		if self.from_pile == other.from_pile and \
				self.from_id == other.from_id and \
				self.to_pile == other.to_pile and \
				self.to_id == other.to_id and \
				self.card == other.card:
			return True
		return False

	def __ne__(self, other):
		return not self.__eq__(other)
		


class SpiteAndMaliceModel(object):

	NUM_STACKS = 4
	HAND_SIZE = 5

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
			player[HAND] = Pile(all_cards.draw(num=self.HAND_SIZE))
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


	def swap_players(self):
		" Change the active players "
		self.active_player = int(not self.active_player)

	def get_player(self, other=False):
		" Return a players cards "
		if not other:
			return self.players[self.active_player]
		return self.players[int(not self.active_player)]

	def build_view_for_player(self):
		" Return a copy of the current view as a GameState object for the player. "
		return GameState(self)


	@classmethod
	def can_place_card_in_center(cls, pile, card):
		"""
		Determins if card can be played on the center stack pile. 
		Returns true if it can be placed, false otherwise.
		"""
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


	def place_card(self, player_move):
		"""
		Place a card onto a stack. Inputs are:
		card is the card to be placed
		from_location is a tuple of the pile (HAND, DISCARD or PAY_OFF) and the id of the pile
		to_location is a tuple of the pile (DISCARD or CENTER), and the id of the pile

		Returns the id of the player who gets to play next.
		"""
		card = player_move.card
		if not Card.is_valid(card):
			raise InvalidMove("Unknown card %s." % (card))
		if player_move.from_pile not in (HAND, DISCARD, PAY_OFF):
			raise InvalidMove("from_location incorrect: %s " % (player_move.from_pile))
		if player_move.to_pile not in (DISCARD, CENTER) or player_move.to_id < 0 \
				or player_move.to_id >= self.NUM_STACKS:
			raise InvalidMove("to_location incorrect: %s." % (player_move.to_pile))
		if player_move.to_pile == CENTER and \
				not self.can_place_card_in_center(self.center_stacks[player_move.to_id], card):
			raise InvalidMove("Can not place card(%s) on center stack %s." % (card, player_move.to_id))
		
		# can not discard kings
		if card[0] == 'K' and player_move.to_pile == DISCARD:
			raise InvalidMove("Can not DISCARD card(%s)" % (card))

		# can not move from discard to discard
		if player_move.to_pile == player_move.from_pile:
			raise InvalidMove("Can not move to same pile %s" % player_move.to_pile)

		# remove it from old location
		player = self.players[self.active_player]
		if player_move.from_pile == HAND and card in player[HAND]:
			player[HAND].remove(card)
		elif player_move.from_pile == DISCARD and card in player[DISCARD][player_move.from_id]:
			player[DISCARD][player_move.from_id].remove(card)
		elif player_move.from_pile == PAY_OFF and card == player[PAY_OFF][-1]:
			if player_move.to_pile != CENTER:
				raise InvalidMove("Can not move PAY_OFF to %s" % player_move.to_pile)
			else:
				player[PAY_OFF].pop()
		else:
			raise InvalidMove("Could not find card(%s) in %s." % (card, player_move.from_pile))

		# place it in new location
		if player_move.to_pile == CENTER:
			self.center_stacks[player_move.to_id].append(card)
		elif player_move.to_pile == DISCARD:
			player[DISCARD][player_move.to_id].append(card)


	def mix_into_stock(self):
		""" 
		Search each of the center stacks for completion, and re-add the completed 
		center pile into the bottom of the stock.
		"""
		for pile in self.center_stacks:
			if len(pile) == 12:
				pile.shuffle()
				self.stock.add_cards(pile.draw(num=12), cards_to=Pile.BOTTOM)


	def fill_hand(self):
		" Fill the active players hand "
		hand = self.players[self.active_player][HAND]
		num_cards = self.HAND_SIZE - len(hand)
		hand.add_cards(self.stock.draw(num=num_cards))

	def is_won(self):
		" Check if the game has been won "
		return (len(self.players[self.active_player][PAY_OFF]) == 0)



class GameState(SpiteAndMaliceModel):
	" A copy of the visible game state for a player "
	def __init__(self, game):
		self.active_player = game.active_player
		self.players = [{}, {}]

		# copy of the visible cards for player
		a_id = self.active_player
		self.players[a_id] = {
			HAND: deepcopy(game.players[a_id][HAND]),
			PAY_OFF: [game.players[a_id][PAY_OFF].visible()[-1]],
			DISCARD: deepcopy(game.players[a_id][DISCARD]),
		}
		# copy of visible cards of his opponent
		o_id = int(not a_id)
		self.players[o_id] = {
			PAY_OFF: [game.players[o_id][PAY_OFF].visible()[-1]],
			DISCARD: deepcopy(game.players[o_id][DISCARD]),
			HAND: []
		}
		# center stacks
		self.center_stacks = deepcopy(game.center_stacks)

	def __eq__(self, other):
		if other == None or type(other) != GameState:
			return False
		for pile in self.get_player().keys():
			if self.get_player()[pile] != other.get_player()[pile]:
				return False
		return True

	def __ne__(self, other):
		return not self.__eq__(other)

	def __str__(self):
		s = self.get_player()
		o = self.get_player(True)
		sd = []
		od = []
		cs = []
		if len(s[PAY_OFF]):
			s_po = s[PAY_OFF][-1]
		else:
			s_po = ''
		if len(o[PAY_OFF]):
			o_po = o[PAY_OFF][-1]
		else:
			o_po = ''

		for p, pd in ((s[DISCARD],sd), (o[DISCARD],od), (self.center_stacks, cs)):
			for pile in p:
				if len(pile) > 0:
					pd.append(pile[-1])
				else:
					pd.append('')
		return "State(po[%s]hand[%s]disc[%s],[%s]disc[%s],center[%s])" % (
				s_po, ''.join(s[HAND]), ''.join(sd), o_po, ''.join(od), ''.join(cs))

	#TODO: make other functions not callable


