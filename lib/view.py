"""
 Views for Spite and Malice game.
"""

import pygame
from pygame.locals import *
from player import ConsolePlayer
from cardView import CardImages, CardGroup
from model import *


class Player(object):
	" interface definition for a player of Spite and Malice "
	
	def play_card(self, my_cards, opponents_cards, center_stacks):
		"""
		This method is called when it is time for the player to place a card.
		The player is given the two maps and a list of center stacks. The first map,
		my_cards, which includes: cards in their hand, the top card on their payoff
		stack, and their discard piles. The second map, opponents_cards, includes:
		the top card of the opponents payoff stack, and their discard piles. 

		The player should return a tuple of, the card they wish to play, the current location
		of the card, and the desired location of the card.
		"""
		pass


class HumanPlayer(Player):
	" A human player "

	def __init__(self):
		pass

	def play_card(self, my_cards, opponents_cards, center_stacks):
		# wait for move selection
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					return None
				elif event.type == MOUSEBUTTONDOWN:
					pass
		return (0,0,0)


class GameView(object):

	window_size = (800,600)

	def __init__(self, model):
		# setup pygame 
		pygame.init()
		screen = pygame.display.set_mode(GameView.window_size)
		pygame.display.set_caption('Spite and Malice!')
		
		background = pygame.Surface(screen.get_size()).convert()
		background.fill((80, 120, 80))

		screen.blit(background, (0,0))
		pygame.display.flip()
		self.screen = screen
		self.background = background

		# store model and players
		self.model = model
		self.players = [HumanPlayer(), HumanPlayer()]


	def get_move(self):
		" Get a move from the player "
		# make card group for cards in the deck
		self.select_group = CardGroup()
		self.target_group = CardGroup()
		# place the cards
		self._draw_board()

		# refresh the view
		self.screen.blit(self.background, (0,0))
		pygame.display.flip()

		# get move from player
		current_view = self.model.build_view_for_player()
		return self.players[self.model.active_player].play_card(*current_view)



	def _build_text(self, text, loc):
		" Add text to the screen "
		font = pygame.font.Font("./media/FreeSans.ttf", 18)
		text_surface = font.render(text, 1, (0,0,0))


	def _draw_board(self):
		" place the cards on the screen "
		# defines for placement
		card_width = 75
		card_height = 100
		card_layer_x = 25
		card_layer_y = 20
		center = self.background.get_rect().centery

		# place center stacks
		for i in range(len(self.model.center_stacks)):
			pile = self.model.center_stacks[i]
			if len(pile) < 1:
				card = self.target_group.makeBlank()
			else:
				card = self.target_group.makeCard(pile[-1])
			self.background.blit(card, card.get_rect(centery=center, x=10 + card_width * i))

		# TODO: player text
		# print the players number of screen
		#text = self._build_text("Player %d" % (self.model.active_player + 1))
		#self.background.blit(card, rect)

		# place hand
		player = self.model.players[self.model.active_player]
		for i in range(len(player[HAND])):
			card = self.select_group.makeCard(player[HAND][i])
			self.background.blit(card, card.get_rect(x=10 + card_layer_x * i, 
					y=self.background.get_rect().bottom - card_height))
		# place pay-off
		card = self.select_group.makeCard(player[PAY_OFF][-1])
		self.background.blit(card, card.get_rect(x=10, 
				centery=int(self.background.get_rect().height * 0.73)))
		card = self.select_group.makeCard(self.model.players[int(not self.model.active_player)][PAY_OFF][-1])
		self.background.blit(card, card.get_rect(x=10, 
				centery=int(self.background.get_rect().height * 0.28)))





	# then place the cards

		




	def show_error(self):
		pass
	

	def game_over(self):
		pass
