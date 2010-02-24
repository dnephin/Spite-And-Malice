"""
 An AI agent to play (and win) Spite and Malice
"""

from model import *
from view import Player
import sys
import random
from copy import copy, deepcopy
from cardmodels import Card
import logging

log = logging.getLogger("snm.agent")


class StateNode(object):
	" A node in the search that represents a current state of the board "
	SELF = 1
	OTHER = 2

	def __init__(self, state, action=None, parent_node=None):
		self.state = state
		self.action = action
		self.parent_node = parent_node
		self.child_nodes = []
		self.util_value = 0
		self.player = self.SELF

	def __eq__(self, other):
		" Override equality so that we can remove duplicate states. "
		if other == None or type(other) != StateNode:
			return False
		if self.state == other.state and self.action == self.action:
			return True
		return False

	def __ne__(self, other):
		return not self.__eq__(other)


class ComputerPlayer(Player):
	"""
	An AI player for Spite and Malice. This uses a modified version of minimax that
	checks each state to see which player is player, and evaluates accordingly.
	"""

	MIN_VALUE = -sys.max_int 
	MAX_VALUE = sys.maxint

	def __init__(self, model)
		" setup the ai ignoring the model, so it can't cheat "
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
			return self.play_queue.pop(0)

		# find the best possible move
		self.terminal_nodes = []
		node = StateNode(game_state)
		self._evaluate(node)

		self._build_play_queue(terminal_nodes)
		return self.play_queue.pop()


	def _evaluate(self, node):
		" Evaluate a node, and recurse if necessary "
		# no reason to get util for starting state
		if node.parent:
			node.util_value = self._utility(node)

		if self._terminal_test(node):
			log.info("Adding terminal state %s" % node)
			self.terminal_nodes.append(node)
			return

		# evaluate all child nodes
		for child_node in node.child_nodes:
			self._evaluate(child_node)



	def _terminal_test(self, node):
		"""
		Check if this node is the last one in its path that we can use
		to considerg moves. Calls sucessors to populate the child
		nodes of the node.
		"""
		# follow path and check if any CENTER moves were made 
		discard_only = True
		cur_node = node
		while cur_node:
			if cur_node.action and cur_node.action.to_pile != DISCARD:
				discard_only = False
				log.info("Found a center move in %s" % (cur_node))
				break
			cur_node = cur_node.parent_node

		# discard is only move
		if node.action and node.action.to_pile == DISCARD and discard_only:
			return True

		# emptied hand without a discard
		if node.action and len(node.state.get_player()[HAND]):
			return True

		# otherwise generate successors
		node.child_nodes = self._successors(node)

		# we've played center cards, so we want to see what the opponent can do
		if node.action and node.action.to_pile == DISCARD and node.player == StateNode.SELF:
			return False

		# we can't determine any more moves for the other player
		if node.player == StateNode.OTHER and not node.child_nodes:
			return True

		return False


	def _successors(self, node):
		"""
		Return a list of successor nodes for the current node. Each node is a valid move.
		"""
		log.info("Generating successors for %s" % node)
		node_list = []
		# moves for the computer player
		if node.player == StateNode.SELF and (not node.parent_node or \
				node.parent_node.action.from_pile != DISCARD):

			# moves to center
			for pile_name, pile_len in [(HAND,1), (PAYOFF,1), (DISCARD,4)]:
				for id in range(pile_len):
					for action in self._get_center_move_from(node.state, pile_name, id):
						new_state = ComputerPlayer._new_state_from_action(node.state, action)
						new_node = StateNode(new_state, action, node)
						if new_node not in node_list:
							node_list.append(new_node)

			# moves to discard
			for card in node.state.get_player()[HAND]
				for pile_id in len(node.state.get_player()[DISCARD]):
					action = PlayerMove(card, from_pile=HAND, to_pile=DISCARD, to_id=pile_id)
					new_state = ComputerPlayer._new_state_from_action(node.state, action)
					new_node = StateNode(new_state, action, node)
					if new_node not in node_list:
						node_list.append(new_node)

			return node_list
	
		# TODO: assume apponent will always play pay_off if they can, do i need min/max ?
		# opponent plays card on center
		for pile_name, pile_len in [(PAYOFF,1), (DISCARD,4)]:
			for id in range(pile_len):
				for action in self._get_center_move_from(node.state, pile_name, id, True):
					new_state = ComputerPlayer._new_state_from_action(node.state, action, True)
					new_node = StateNode(new_state, action, node)
					if new_node not in node_list:
						node_list.append(new_node)


	@staticmethod
	def _get_center_move_from(state, pile_name, pile_index, new_player=False):
		" Get all the valid center stack placements from a pile "
		moves = []

		pile = state.get_player(new_player)[pile_name]
		if pile_name == DISCARD and not new_player:
			pile = [state.get_player(new_player)[pile_name][id][-1]]

		for i in range(len(pile)):
			card = pile[i]
			for center_id in range(len(state.center_stacks)):
				if state.can_place_card_in_center(
						state.center_stacks[center_id], card):
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


	def _utility(self, node):
		""" 
		Calculate the utility value for this state node.
		Points:
		+400	Play pay_off card
		+120	Empty hand without a discard
		+32		Discard on same value card
		+10		Each time the discard card occures in the hard
		+4		Each point away the closest center is from opponents pay off (max +48)
		+2		Discard buries the least essential card
		+1		Discard least essential card
		-3		Each card in hand
		-80	Opponent plays pay_off card
		"""
		# shortcut vars
		center_values = []
		for pile in node.state.center_stacks:
			if not pile:
				center_values.append(0)
				continue
			center_values.append(Card.to_numeric_value(pile[-1]))
		if node.player == StateNode.SELF:
			myself = node.state.get_player()
			other = node.state.get_player(True)
		else:
			myself = node.state.get_player(True)
			other = node.state.get_player()

		value = 0
		if node.player == StateNode:
			# pay off played
			if node.action.from_pile == PAY_OFF:
				value += 400
			# empty hand without a discard
			if len(myself[HAND]) == 0 and node.action.to_pile != DISCARD:
				value += 120
			# each time the discard cards value ocurs in the hand
			if node.action.to_pile == DISCARD:
				value += 10 * map(lambda c: Card.to_numeric_value(c), myself[HARD]).count(
						Card.to_numeric_value(node.action.card))
			# discard on same value card
			if node.action.to_pile == DISCARD and \
					len(myself[DISCARD][node.action.to_id]) > 1 and \
					Card.to_numeric_value(myself[DISCARD][node.action.to_id][-1]) == \
					Card.to_numeric_value(myself[DISCARD][node.action.to_id][-2]):
				value += 32
			# discad buries least essential card
			elif node.action.to_pile == DISCARD:
				discard_piles = []
				for pile_id in len(range(myself[DISCARD])):
					pile = myself[DISCARD][pile_id]
					if len(pile) > 1 and node.action.to_id:
						discard_piles.append(pile[-2])
					elif len(pile) > 1:
						discard_piles.append(pile[-1])
					else:
						discard_piles.append(None)
				if node.action.to_id == self._find_least_essential_card(center_values,
						discard_piles, myself[PAY_OFF][-1]):
					value += 2
			# discard least essential card
			if node.action.to_pile == DISCARD and 0 == self.find_least_essential_card(
					center_values, [node.action.card] + myself[HAND], myself[PAY_OFF][-1]):
				value += 1
			
			# each point away the closest center is from opponents pay off
			value += 4 * self._distance_between_values(self._find_closest_center_stack_value(
					center_values, other[PAY_OFF][-1]))

			# each card in hand
			value -= 3 * len(myself[HAND])

		else:
			# opponent plays pay_off
			if node.action.from_pile == PAY_OFF:
				value -= 80

		# cummulative utils
		return value + node.parent_node.util_value


	@staticmethod
	def _find_least_essential_card(center_values, pile, pay_off_card):
		"""
		Return the id in pile that is considered least essential relative to the
		pay off card.
		"""
		center_value = self._find_closest_center_stack_value(center_values, pay_off_card)
		list_values = map(lambda c: self._distance_between_values(c, pay_off_card), center_values)

		return list_values.index(min(list_values))


	@staticmethod
	def _find_closest_center_stack_value(center_stacks,  pay_off_card):
		"""
		return the value from the center stack that is closest available
		for playing the pay_off_card.
		"""
		po_value = Card.to_numeric_value(pay_off_card)
		return min(map(lambda c: self._distance_between(Card.to_numeric_value(c), po_value), center_stacks))
#		distance = ComputerPlayer.MAX_VALUE
#		closest_value = None
#		for stack_id in range(len(center_stacks)):
#			card = center_stacks[stack_id]
#			new_dist = self._distance_between(Card.to_numeric_value(card), po_value)
#			if new_dist < distance:
#				distance = new_dist
#				closest_value = stack_id
#		return closest_value


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

	def _build_play_queue(self, node)
		"""
		Given a node, build the play queue from the child node with the given
		value to the discard move, and store it.  If moves share a util
		value (somehow), chose a random node from them.
		"""
		# loop while there are still nodes in the chain
		# TODO: fix this for new code
		while node:
			possible_paths = []
			# for each child, find the path with the desired value
			for child in node.child_nodes:
				if child.util_value == value:
					possible_paths.append(child)
			if len(possible_paths) == 0:
				return
			node = random.choice(possible_paths)
			self.play_queue.append(node.state)
			if node.state[2][0] == DISCARD:
				return


