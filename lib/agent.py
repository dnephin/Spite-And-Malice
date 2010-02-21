"""
 An AI agent to play (and win) Spite and Malice
"""

from model import *
from view import Player
import sys
import random


class StateNode(object):
	" A node in the search that represents a current state of the board "
	SELF = 1
	OTHER = 2

	def __init__(self, state, parent_node):
		self.state = state
		self.parent_node = parent_node
		self.child_nodes = []
		self.util_value = None
		self.player = self.SELF


class ComputerPlayer(Player):
	"""
	An AI player for Spite and Malice. This uses a modified version of minimax that
	checks each state to see which player is player, and evaluates accordingly.
	"""

	def __init__(self, model)
		" setup the ai ignoring the model, so it can't cheat "
		# list of moves stored up
		self.play_queue = []

	def play_card(self, my_cards, opponents_cards, center_stacks):
		"""
		my_cards: cards in their hand, the top card on their payoff stack, and their discard piles.
		opponents_cards: the top card of the opponents payoff stack, and their discard piles.
		center_stacks: the enter center stacks
		"""
		# play queued moves if we have some
		if len(self.play_queue) > 0:
			return self.play_queue.pop(0)

		# find the best possible move
		value = self._max_value(node)
		self._build_play_queue(node, value)
		return self.play_queue.pop()



	def _min_value(self, node):
		" return the minimum value of all the children of this node "
		pass


	def _max_value(self, node):
		" return the maximum value of all the children of this node "
		pass


	def _terminal_test(self, node):
		"""
		Check if this node is the last one in its path that we can use
		to considerg moves.
		"""
		# if no center stack plays terminate at discard

		# if center stacks were played, evaluate available opponent moves

		pass



	def _successors(self, node):
		"""
		Return a list of successor nodes for the current node. Each node is a valid move.
		"""
		pass

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


	def end_turn(self):
		" The players turn has ended, cleanup "
		pass

