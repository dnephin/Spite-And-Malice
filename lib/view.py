"""
 Views for Spite and Malice game.
"""

from player import ConsolePlayer

class ConsoleView(object):
	
	def __init__(self, model):
		self.model = model
		self.players = [ConsolePlayer(1), ConsolePlayer(2)]

	def get_move(self):
		pass


	def show_error(self):
		pass
	

	def game_over(self):
		pass
