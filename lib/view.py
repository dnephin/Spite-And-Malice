"""
 Views for Spite and Malice game.
"""

import pygame
from pygame.locals import *
from cardView import CardGroup
from model import *
from player import HumanPlayer
import logging

log = logging.getLogger('snm.view')

# TODO: highlight selected card


class GameView(object):
	" The local visual display of the game for human players "

	screen = None
	window_size = (650,600)
	STD_FONT = './media/FreeSans.ttf'

	def __init__(self, model, players):
		# store model and players
		self.model = model
		self.players = players 

		# setup pygame 
		if not self.screen:
			pygame.init()
			self.screen = pygame.display.set_mode(self.window_size)
			pygame.display.set_caption('Spite and Malice!')
		self.background = pygame.Surface(self.screen.get_size()).convert()


	def wait_screen(self):
		" blank the screen and wait for the next player to be ready "
		self.background.fill((0, 0, 0))
		font = pygame.font.Font(self.STD_FONT, 40)
		text = "Player %d" % (self.model.active_player + 1)
		surf = font.render(text, True, (255, 80, 80))
		bg_rect = self.background.get_rect()
		self.background.blit(surf, surf.get_rect(centery=bg_rect.centery,
				centerx=bg_rect.centerx))
		self._refresh_view()
		while True:
			for event in pygame.event.get():
				if event.type == MOUSEBUTTONUP or event.type == KEYUP:
					return

	def game_over(self):
		" Inform the players the game is over "
		log.warn("Game Over! Player %d won" % (self.model.active_player+1))
		print "Game Over! Player %d won" % (self.model.active_player+1)
		while True:
			for event in pygame.event.get():
				# quit
				if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
					return None


	def show_error(self, message):
		" Report the error to the user "
		# TODO: show moves in a box on the screen
		print message


	def draw_board(self, player_id):
		" place the cards on the screen for the view of player_id "
		# group for cards for selection
		self.select_group = CardGroup()
		self.target_group = CardGroup()
		other_group = CardGroup()
		background = self.background
		# other player
		other_id = int(not player_id)

		# defines for placement
		card_width = 75
		card_height = 100
		card_layer_x = 25
		card_layer_y = 20
		discard_left_x = 40 + card_width * 4
		center = background.get_rect().centery

		# clear the background
		background.fill((80, 120, 80))
		# place center stacks
		for i in range(len(self.model.center_stacks)):
			pile = self.model.center_stacks[i]
			if len(pile) < 1:
				card = self.target_group.makeBlank((CENTER, i))
			else:
				card = self.target_group.makeCard(pile[-1], (CENTER, i))
			card.place(background, card.get_rect(centery=center, x=10 + card_width * i))
			# put a number on kings
			if card.model and card.model[0] == 'K':
				font = pygame.font.Font(self.STD_FONT, 20)
				text = str(Card.values[len(pile)-1])
				surf = font.render(text, True, (50, 50, 120), (0xFF, 0xFF, 0xFF))
				background.blit(surf, surf.get_rect(left=card.loc.left+2, top=card.loc.top+2))
				
		# place hand
		player = self.model.players[player_id]
		for i in range(len(player[HAND])):
			card = self.select_group.makeCard(player[HAND][i], (HAND,None))
			card.place(background, card.get_rect(x=10 + card_layer_x * i, 
					y=background.get_rect().bottom - card_height))

		# place pay-off
		card = self.select_group.makeCard(player[PAY_OFF][-1], (PAY_OFF,None))
		card.place(background, card.get_rect(x=10, 
				centery=int(background.get_rect().height * 0.73)))
		card = other_group.makeCard(self.model.players[other_id][PAY_OFF][-1],
				None)
		card.place(background, card.get_rect(x=10, 
				centery=int(background.get_rect().height * 0.28)))

		# place player discard piles
		for pile_num in range(self.model.NUM_STACKS):
			for n in range(len(player[DISCARD][pile_num])):
				card = other_group.makeCard(player[DISCARD][pile_num][n], None)
				card.place(background, card.get_rect(
						top=20 + center + n * card_layer_y, x=discard_left_x + pile_num * card_width))
				if n == len(player[DISCARD][pile_num])-1:
					self.target_group.addCard(card, (DISCARD, pile_num))
					self.select_group.addCard(card, (DISCARD, pile_num))
			if not len(player[DISCARD][pile_num]):
				card = self.target_group.makeBlank((DISCARD, pile_num))
				card.place(background, card.get_rect(
						top=20 + center, x=discard_left_x + pile_num * card_width))

		# place opponents discard piles
		opponent = self.model.players[other_id]
		for pile_num in range(self.model.NUM_STACKS):
			for n in range(len(opponent[DISCARD][pile_num])):
				card = other_group.makeCard(opponent[DISCARD][pile_num][n], None)
				card.place(background, card.get_rect(
						bottom= center - 20 - n * card_layer_y, x=discard_left_x + pile_num * card_width))
			if not len(opponent[DISCARD][pile_num]):
				card = other_group.makeBlank(None)
				card.place(background, card.get_rect(
						bottom= -20 + center, x=discard_left_x + pile_num * card_width))

		# fliped over opponnts hand
		for i in range(len(opponent[HAND])):
			card = other_group.makeBack(None)
			card.place(background, card.get_rect(x=10 + card_layer_x * i,
					top=background.get_rect().top + 2))

		# player text
		font = pygame.font.Font(self.STD_FONT, 25)
		text = "Player %d" % (player_id + 1)
		surf = font.render(text, True, (30, 30, 80))
		background.blit(surf, surf.get_rect(left=10, top=center + card_height / 2 + 10))

		self._refresh_view()


	def _refresh_view(self):
		" refresh the view "
		self.screen.blit(self.background, (0,0))
		pygame.display.flip()

