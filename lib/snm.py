"""
 Controller for the game Spite and Malice.
"""

from model import SpiteAndMaliceModel, InvalidMove, DISCARD, PAY_OFF, HAND
from view import GameView 
from cardmodels import Suits, Card
import logging
import logging.config
import time
from player import HumanPlayer
from agent import ComputerPlayer

log = logging.getLogger('snm.controller')


class SpiteAndMalice(object):
	" Controller class for the game "

	def __init__(self):
		self.model = SpiteAndMaliceModel()
		self.players = [HumanPlayer(), HumanPlayer()]
		self.view = GameView(self.model, self.players)

	def run(self):
		" Lets go. "
		# find out which player goes first
		if Card.to_numeric_value(self.model.players[0][PAY_OFF][-1]) > \
				Card.to_numeric_value(self.model.players[1][PAY_OFF][-1]):
			self.model.active_player = 0
		else:
			self.model.active_player = 1

		prev_active = None
		while True:
			active_player = self.model.active_player
			other_player = int(not self.model.active_player)

			# special case for both human players, blank the screen if it's a new players turn
			if type(self.players[active_player]) == type(self.players[other_player]) \
					== HumanPlayer and prev_active != active_player:
				self.view.wait_screen()
				prev_active = active_player

			# draw the board for the human player(s)
			if type(self.players[active_player]) == HumanPlayer:
				self.view.draw_board(active_player)
			elif type(self.players[other_player]) == HumanPlayer:
				self.view.draw_board(other_player)

			# get the next move
			if type(self.players[active_player]) == HumanPlayer:
				player_move = self.players[active_player].play_card(
						self.view.select_group, self.view.target_group)
			else:
				game_state = self.model.build_view_for_player()
				player_move = self.players[active_player].play_card(game_state)

			if player_move == None:
				return

			# play the move
			try:
				self.model.place_card(player_move)
			except InvalidMove, inv:
				self.view.show_error(inv)
				continue
			# check for win
			if self.model.is_won():
				self.view.game_over()
				return
			# mix completed stacks back in
			self.model.mix_into_stock()

			# fill player hand if empty, and not a discard
			hand = self.model.players[active_player][HAND]
			if player_move.to_pile != DISCARD and len(hand) == 0:
				self.model.fill_hand()

			# swap players if move was a discard
			if player_move.to_pile == DISCARD:
				# tell view and model to end the round
				self.model.swap_players()


if __name__ == "__main__":
	logging.config.fileConfig('./conf/logging.conf')
	game = SpiteAndMalice()
	game.run()

