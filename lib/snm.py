"""
 Controller for the game Spite and Malice.
"""

from model import SpiteAndMaliceModel, InvalidMove, DISCARD, PAY_OFF, HAND
from view import GameView 
from cardmodels import Suits, Card
import logging
import logging.config

log = logging.getLogger('snm.controller')


class SpiteAndMalice(object):
	" Controller class for the game "

	def __init__(self):
		self.model = SpiteAndMaliceModel()
		self.view = GameView(self.model)

	def run(self):
		" Lets go. "
		# find out which player goes first
		if Card.to_numeric_value(self.model.players[0][PAY_OFF][-1]) > \
				Card.to_numeric_value(self.model.players[1][PAY_OFF][-1]):
			self.model.active_player = 0
		else:
			self.model.active_player = 1

		while True:
			# get the next move
			placement_tuple = self.view.get_move()
			if placement_tuple == None:
				return
			# play the move
			try:
				self.model.place_card(*placement_tuple)
			except InvalidMove, inv:
				self.view.show_error(inv)
				continue
			except TypeError, err:
				log.warn("Unexpected return from view: %s" % (str(placement_tuple)))
				continue
			# check for win
			if self.model.is_won():
				self.view.game_over()
				return
			# mix completed stacks back in
			self.model.mix_into_stock()

			# fill player hand if empty, and not a discard
			hand = self.model.players[self.model.active_player][HAND]
			if placement_tuple[2][0] != DISCARD and len(hand) == 0:
				self.model.fill_hand()

			# swap players if move was a discard
			if placement_tuple[2][0] == DISCARD:
				self.model.active_player = int(not self.model.active_player)
				# fill next players hand
				self.model.fill_hand()



if __name__ == "__main__":
	logging.config.fileConfig('./conf/logging.conf')
	game = SpiteAndMalice()
	game.run()

