"""
 An AI agent to play (and win) Spite and Malice
"""

from model import *
from player import Player
import sys
import random
from copy import copy, deepcopy
from cardmodels import Card
from time import sleep
import logging

log = logging.getLogger("snm.agent")


class StateNode(object):
	" A node in the search that represents a current state of the board "
	SELF = "self"
	OTHER = "other"

	def __init__(self, state, action=None, parent_node=None, player="self"):
		self.state = state
		self.action = action
		self.parent_node = parent_node
		self.child_nodes = []
		self.util_value = 0
		self.player = player

	def __eq__(self, other):
		" Override equality so that we can remove duplicate states. "
		if other == None or type(other) != StateNode:
			return False
		if self.state == other.state and self.action == other.action:
			return True
		return False

	def __ne__(self, other):
		return not self.__eq__(other)

	def __str__(self):
		return "Node[%d](p:%s|%s,%s,childs:%d)" % (
				self.util_value, self.player, self.action, self.state, len(self.child_nodes))


class ComputerPlayer(Player):
	"""
	An AI player for Spite and Malice. This uses a modified version of minimax that
	checks each state to see which player is player, and evaluates accordingly.
	"""

	MIN_VALUE = -sys.maxint 
	MAX_VALUE = sys.maxint

	def __init__(self):
		" setup the ai "
		# list of moves stored up
		self.play_queue = []

	def play_card(self, game_state):
		"""
		my_cards: cards in their hand, the top card on their payoff stack, and their discard piles.
		opponents_cards: the top card of the opponents payoff stack, and their discard piles.
		center_stacks: the enter center stacks
		"""
		# play queued moves if we have some
		if len(self.play_queue) > 0:
			sleep(0.3)
			return self.play_queue.pop(0)

		# find the best possible move
		self.terminal_nodes = []
		node = StateNode(game_state)
		self._evaluate(node)

		self._build_play_queue()
		return self.play_queue.pop(0)


	def _evaluate(self, node):
		" Evaluate a node, and recurse if necessary "
		# no reason to get util for starting state
		if node.parent_node:
			node.util_value = self._utility(node)

		if self._terminal_test(node):
			log.info("Adding terminal %s" % node)
			self.terminal_nodes.append(node)
			return

		# evaluate all child nodes
		log.debug("Evaluating %d succcessor" % len(node.child_nodes))
		for child_node in node.child_nodes:
			self._evaluate(child_node)


	def _terminal_test(self, node):
		"""
		Check if this node is the last node in its path that can be evaluated. If
		it is not calls sucessors to populate the child nodes of the node.
		Returns True if this is a terminal node, False otherwise.
		"""
		# if nothing was done, can't be a terminal node
		if not node.action:
			node.child_nodes = self._successors(node)
			return False

		# if move is a pay_off for either player, it's a terminal node
		if node.action.from_pile == PAY_OFF:
			return True

		# node is a play for SELF
		if node.player == StateNode.SELF:
			# we emptied hand without a discard
			if not len(node.state.get_player()[HAND]) and node.action.to_pile != DISCARD:
				return True

			# discard is only move
			if node.action.to_pile == DISCARD and node.parent_node and not node.parent_node.action:
				return True

		# otherwise generate successors
		node.child_nodes = self._successors(node)

		# we've played center cards, so we want to see what the opponent can do
		if node.action.to_pile == DISCARD and node.player == StateNode.SELF:
			return False

		# we can't determine any more moves for either player
		if not node.child_nodes:
			return True

		return False


	def _successors(self, node):
		"""
		Return a list of successor nodes for the current node. Each node is a valid move.
		"""
		log.debug("Generating successors for %s" % node)
		node_list = []

		# opponent plays card on center
		if node.player == StateNode.OTHER or (node.action and node.action.to_pile == DISCARD):
			swap_player = (node.player == StateNode.SELF)
			for pile_name, pile_len in [(PAY_OFF,1), (DISCARD,4)]:
				for pile_id in range(pile_len):
					for action in self._get_center_move_from(node.state, pile_name, pile_id, swap_player):
						new_state = ComputerPlayer._new_state_from_action(node.state, action, swap_player)
						new_node = StateNode(new_state, action, node, player=StateNode.OTHER)
						node_list.append(new_node)
			return node_list

		# moves to center
		for pile_name, pile_len in [(HAND,1), (PAY_OFF,1), (DISCARD,4)]:
			for pile_id in range(pile_len):
				for action in self._get_center_move_from(node.state, pile_name, pile_id):
					new_state = ComputerPlayer._new_state_from_action(node.state, action)
					new_node = StateNode(new_state, action, node)
					node_list.append(new_node)

		# moves to discard
		for card in node.state.get_player()[HAND]:
			# can't discard kings
			if Card.to_numeric_value(card) == 13:
				continue
			# only create moves for different discard pile states
			discard_pile_values = []
			discard_pile_ids = []
			for i in range(len(node.state.get_player()[DISCARD])):
				value = None
				if len(node.state.get_player()[DISCARD][i]):
					value = Card.to_numeric_value(node.state.get_player()[DISCARD][i][-1])
				if value not in discard_pile_values:
					discard_pile_values.append(value)
					discard_pile_ids.append(i)
			# find the moves
			for pile_id in discard_pile_ids: 
				action = PlayerMove(card, from_pile=HAND, to_pile=DISCARD, to_id=pile_id)
				new_state = ComputerPlayer._new_state_from_action(node.state, action)
				new_node = StateNode(new_state, action, node)
				node_list.append(new_node)
		return node_list
	


	@staticmethod
	def _get_center_move_from(state, pile_name, pile_index, other_player=False):
		" Get all the valid center stack placements from a pile "
		moves = []

		# set pile to HAND or PAY_OFF stacks
		pile = state.get_player(other_player)[pile_name]
		# otherwise, set it to top of DISCARD
		if pile_name == DISCARD:
			if len(state.get_player(other_player)[pile_name][pile_index]) < 1:
				return moves
			pile = [state.get_player(other_player)[pile_name][pile_index][-1]]
		# only include center piles of different lengths
		center_lengths = []
		center_ids = []
		for i in range(len(state.center_stacks)):
			length = len(state.center_stacks[i])
			if length not in center_lengths:
				center_ids.append(i)
				center_lengths.append(length)
		# find the moves
		for i in range(len(pile)):
			card = pile[i]
			for center_id in center_ids:
				if state.can_place_card_in_center(state.center_stacks[center_id], card):
					moves.append(PlayerMove(card, from_pile=pile_name, from_id=pile_index,
							to_pile=CENTER, to_id=center_id))
		return moves

	
	@staticmethod
	def _new_state_from_action(state, action, swap_player=False):
		" Return a new state created from the previous state and the action "
		new_state = deepcopy(state)
		if swap_player:
			new_state.swap_players()
		new_state.place_card(action)
		return new_state

	class PointTracker(dict):
		"""
		dictionary wrapper class to keep track of which points are being used 
		for the final utility value.
		"""
		def __init__(self, d):
			dict.__init__(self, d)
			self.used = []
		def __getitem__(self, key):
			if key not in ['discard_common', 'op_dist_op', 'discard_least', 'card_in_discard']:
				self.used.append(key)
			return dict.__getitem__(self, key)

	def _utility(self, node):
		""" 
		Calculate the utility value for this state node.
		"""
		# FIXME: Balance points so that placing on center only when necesarry (discard full, or no closer to po for op)
		points = {
			# to discard pile
			DISCARD: (0, {
				'on_empty': 35,			# Discard on empty pile
				'on_same': 50,			# Discard on same value card
				'common_in_hand': 10,	# Each time the discard card occures in the hard
				'least_essential': 5,	# Discard least essential card
				'bury_least': 5,		# Discard buries the least essential card
			}),
			# to center
			CENTER: (30, {
				'op_dist_po': 10,		# Each point away the closest center is from opponents pay off (max +48)
				'pay_off': 400,			# Play the pay off card
			}),
			# from hand
			HAND: (20, {
				'empty_hand': 120,		# Empty hand without a discard
			}),
			# Opponent play
			StateNode.OTHER: (0, {
				'from_discard': -20,	# Opponent plays from discard
				'from_pay_off': -300,	# Opponent plays pay_off card
			})
		}

		# shortcut vars
		center_values = []
		for pile in node.state.center_stacks:
			center_values.append(len(pile))
		if node.player == StateNode.SELF:
			myself = node.state.get_player()
			other = node.state.get_player(True)
		else:
			myself = node.state.get_player(True)
			other = node.state.get_player()

		value = 0
		if node.player == StateNode.SELF:
			if node.action.to_pile == DISCARD:
				value += points[DISCARD][0]
				# discard on empty pile
				if len(myself[DISCARD][node.action.to_id]) == 1:
					value += points[DISCARD][1]['on_empty']
				# discard on same value card
				if len(myself[DISCARD][node.action.to_id]) > 1 \
						and Card.to_numeric_value(myself[DISCARD][node.action.to_id][-1]) == \
						Card.to_numeric_value(myself[DISCARD][node.action.to_id][-2]):
					value += points[DISCARD][1]['on_same']
				# each time the discard cards value ocurs in the hand
				value += points[DISCARD][1]['common_in_hand'] * \
						map(lambda c: Card.to_numeric_value(c), myself[HAND]).count(
						Card.to_numeric_value(node.action.card))
				# discard least essential card
				if 0 == self._find_least_essential_card(
						center_values, [node.action.card] + myself[HAND], myself[PAY_OFF][-1]):
					value += points[DISCARD][1]['least_essential']
				# discard buries least essential card
				if len(myself[DISCARD][node.action.to_id]) >= 1:
					discard_piles = self._build_pre_play_discard_piles(node)
					if node.action.to_id == self._find_least_essential_card(center_values,
							discard_piles, myself[PAY_OFF][-1]):
						value += points[DISCARD][1]['bury_least']
			elif node.action.to_pile == CENTER:
				value += points[CENTER][0]
				# each point away the closest center is from opponents pay off
				value += points[CENTER][1]['op_dist_po'] * self._distance_between_values(self._find_closest_center_stack_value(
						center_values, other[PAY_OFF][-1]), Card.to_numeric_value(other[PAY_OFF][-1]))
				# pay off played
				if node.action.from_pile == PAY_OFF:
					value += points[CENTER][1]['pay_off']

			if node.action.from_pile == HAND:
				value += points[HAND][0]
				# empty hand without a discard
				if len(myself[HAND]) == 0 and node.action.to_pile != DISCARD:
					value += points[HAND][1]['empty_hand']

		# opponents plays
		else:
			value += points[StateNode.OTHER][0]
			if node.action.from_pile == PAY_OFF:
				value += points[StateNode.OTHER][1]['from_pay_off']
			if node.action.from_pile == DISCARD:
				value += points[StateNode.OTHER][1]['from_discard']

		# cumulative utils
		log.debug("Util %d " % (value))
		return value + node.parent_node.util_value


	@staticmethod
	def _build_pre_play_discard_piles(node):
		" build a list of the pre play discard piles top cards "
		discard = node.state.get_player()[DISCARD]
		discard_piles = []
		for pile_id in range(len(discard)):
			pile = discard[pile_id]
			if len(pile) > 1 and node.action.to_id:
				discard_piles.append(pile[-2])
			elif len(pile) > 1:
				discard_piles.append(pile[-1])
			else:
				discard_piles.append(None)
		return discard_piles


	@staticmethod
	def _find_least_essential_card(center_values, pile, pay_off_card):
		"""
		Return the id in pile that is considered least essential relative to the
		pay off card.
		"""
		# TODO: broken, returns cards below value, should return highest outside range from center -> payoff,
		# for at least the case of discards, maybe this is used correctly elsewhere ?
		center_value = ComputerPlayer._find_closest_center_stack_value(center_values, pay_off_card)
		list_values = map(lambda c: ComputerPlayer._distance_between_values(
				center_value, Card.to_numeric_value(c)), pile)

		card = pile[list_values.index(max(list_values))]
		log.debug("Least essential card for center_values[%s] and pay_off[%s]: %s" % (
			"".join(map(str, center_values)), pay_off_card, card))
		return card


	@staticmethod
	def _find_closest_center_stack_value(center_values,  pay_off_card):
		"""
		return the value from the center stack that is closest available
		for playing the pay_off_card.
		"""
		po_value = Card.to_numeric_value(pay_off_card)
		return min(map(lambda v: ComputerPlayer._distance_between_values(v, po_value), center_values))


	@staticmethod
	def _distance_between_values(pile_card, play_card):
		" find the distance between the pile card, and the play card values"
		if pile_card == None:
			return play_card
		if play_card > pile_card:
			return play_card - pile_card
		if play_card == pile_card:
			return 12
		return 12 - pile_card + play_card

	def _build_play_queue(self):
		"""
		Find the best path, and build the play queue for this path.
		In the case of a tie, pick a random path
		"""
		log.info("Choosing from %d possible paths" % len(self.terminal_nodes))
		node = max(self.terminal_nodes, key=lambda s: s.util_value)

		chain = []
		# loop while there are still nodes in the chain
		while node:
			# skip any opponent nodes we have in the chain
			if node.player == StateNode.OTHER:
				node = node.parent_node
				continue
			chain.append(node.action)
			node = node.parent_node

		# remove the starting state, and reverse the list, so we can traverse the path
		chain.pop()
		chain.reverse()
		log.info("Chosing path: %s" % (" ".join(map(unicode, chain))))
		self.play_queue = chain


