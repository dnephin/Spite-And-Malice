"""
 Player classees for human players local and remote.
 Receives player input from event loops, and builts PlayerMove objects.
"""

import pygame
from pygame.locals import *
from model import PlayerMove
import logging

log = logging.getLogger('snm.view')

class Player(object):
	" interface definition for a player of Spite and Malice "
	
	def play_card(self, *args):
		"""
		This method is called when it is time for the player to place a card.
		The player is given the two maps and a list of center stacks. The first map,
		my_cards, which includes: cards in their hand, the top card on their payoff
		stack, and their discard piles. The second map, opponents_cards, includes:
		the top card of the opponents payoff stack, and their discard piles. 

		The player should return a PlayerMove object.
		"""
		pass


class HumanPlayer(Player):
	" A human players interface to the game "

	def play_card(self, select_group, target_group):
		card_selected = False
		# wait for move selection
		while True:
			for event in pygame.event.get():
				# quit
				if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
					return None
				# mouseclick to select target 
				if event.type == MOUSEBUTTONUP and card_selected:
					if target_group.findClick(event):
						log.info("Selected %s, %s" % target_group.getSelected())
						card, from_location = select_group.getSelected()
						to_location = target_group.getSelected()[1]
						return PlayerMove(card.model, from_location, to_location)

				# mouseclick to select card
				if event.type == MOUSEBUTTONUP:
					if select_group.findClick(event):
						card_selected = True
						log.info("Targeted %s, %s, " % select_group.getSelected())
						continue

#TODO remote player
class RemotePlayer(HumanPlayer):
	pass

