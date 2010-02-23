"""
 An AI agent to play (and win) Spite and Malice
"""

from model import *
from view import Player
import sys
import random
from copy import copy, deepcopy


class StateNode(object):
	" A node in the search that represents a current state of the board "
	SELF = 1
	OTHER = 2

	def __init__(self, state, action=None, parent_node=None):
		self.state = state
		self.action = action
		self.parent_node = parent_node
		self.child_nodes = []
		self.util_value = None
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
		node = StateNode(game_state)
		value = self._max_value(node)
		self._build_play_queue(node, value)
		return self.play_queue.pop()



	def _min_value(self, node):
		" return the minimum value of all the children of this node "
		if self._terminal_test(node):
			return self.utility(node)

		value = self.MAX_VALUE
		for child_node in node.child_nodes:
			if child_node.player == self.SELF:
				value = value = min(value, self._max_value(child_node))
			else:
				value = value = min(value, self._min_value(child_node))
		return value


	def _max_value(self, node):
		" return the maximum value of all the children of this node "
		if self._terminal_test(node):
			return self.utility(node)

		value = self.MIN_VALUE
		for child_node in node.child_nodes:
			if child_node.player == self.SELF:
				value = value = max(value, self._max_value(child_node))
			else:
				value = value = max(value, self._min_value(child_node))
		return value


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
				break
			cur_node = cur_node.parent_node

		# discard is only move
		if node.action and node.action.to_pile == DISCARD and discard_only:
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
		
		# opponent plays card on center
		# TODO: swap active in state if this is the first play for the opponent, or do it in _new_state_from_action ? 



	@staticmethod
	def _get_center_move_from(state, pile_name, pile_index):
		" Get all the valid center stack placements from a pile "
		moves = []
		pile = state.get_player()[pile_name]
		if pile_name == DISCARD:
			pile = [state.players[state.active_player][pile_name][id][-1]]
		for i in range(len(pile)):
			card = pile[i]
			for center_id in range(len(state.center_stacks)):
				if state.can_place_card_in_center(
						state.center_stacks[center_id], card):
					moves.append(PlayerMove(card, from_pile=pile_name, from_id=pile_index,
							to_pile=CENTER, to_id=center_id))
		return moves

	
	@staticmethod
	def _new_state_from_action(state, action):
		" Return a new state created from the previous state and the action "
		# TODO: what about when its the start of the opponents turn ?
		new_state = deepcopy(state)
		new_state.place_card(action)
		return new_state


	def _utility(self, node):
		" Calculate the utility value for this state node "
		# list priorities from highest to lowest, assign values for each case

		# place cards to prevent the opponent from playing their discard!

		pass


	def _build_play_queue(self, node, value)
		"""
		Given a node, build the play queue from the child node with the given
		value to the discard move, and store it.  If moves share a util
		value (somehow), chose a random node from them.
		"""
		# loop while there are still nodes in the chain
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


