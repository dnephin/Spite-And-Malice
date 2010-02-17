"""
 Controller for the game Spite and Malice.
"""

from models import SpiteAndMaliceModle, InvalidMode, DISCARD, PAY_OFF
from view import ConsoleView
from cardmodels import Suits, Card


class SpiteAndMalice(object):
	" Controller class for the game "

	def __init__(self):
		self.model = SpiteAndMaliceModel()
		self.view = ConsoleView(self.model)

	def run(self):
		" Lets go. "
		# find out which player goes first
		if Card.to_numeric_value(self.model.player[0][PAY_OFF][-1]) > \
				Card.to_numeric_value(self.model.player[1][PAY_OFF][-1]):
			self.model.active_player = 0
		else:
			self.model.active_player = 1

		while True:
			# get the next move
			placement_tuple = self.view.get_move()
			# play the move
			try:
				self.model.place_card(*placement_tuple)
			except InvalidMode, inv:
				self.view.show_error(inv)
				continue
			# check for win
			if self.model.is_won():
				self.view.game_over()
				return
			# mix completed stacks back in
			self.model.mix_into_stack()
			# swap players if move was a discard
			if placement_tuple[3][1] == DISCARD:
				self.model.active_player = int(not self.model.active_player)



if __name__ == "__main__":
	game = SpiteAndMalice()
	game.run()

