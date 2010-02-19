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

	def __init__(self, view):
		self.view = view

	def play_card(self, my_cards, opponents_cards, center_stacks):
		card_selected = False
		# wait for move selection
		while True:
			for event in pygame.event.get():
				# quit
				if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
					return None
				# mouseclick to select target 
				if event.type == MOUSEBUTTONUP and card_selected:
					if self.view.target_group.findClick(event):
						print "Selected %s, %s" % self.view.target_group.getSelected()
						card, from_location = self.view.select_group.getSelected()
						to_location = self.view.target_group.getSelected()[1]
						return (card.model, from_location, to_location)

				# mouseclick to select card
				if event.type == MOUSEBUTTONUP:
					if self.view.select_group.findClick(event):
						card_selected = True
						print "Targeted %s, %s, " % self.view.select_group.getSelected()
						continue



class GameView(object):

	window_size = (650,600)

	def __init__(self, model):
		# setup pygame 
		pygame.init()
		self.screen = pygame.display.set_mode(GameView.window_size)
		pygame.display.set_caption('Spite and Malice!')
		self.background = pygame.Surface(self.screen.get_size()).convert()

		# store model and players
		self.model = model
		self.players = [HumanPlayer(self), HumanPlayer(self)]


	def get_move(self):
		" Get a move from the player "
		# make card group for cards in the deck
		self.select_group = CardGroup()
		self.target_group = CardGroup()
		# place the cards
		self.background.fill((80, 120, 80))
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
		# group for cards that can not be selected
		other_group = CardGroup()
		# defines for placement
		card_width = 75
		card_height = 100
		card_layer_x = 25
		card_layer_y = 20
		discard_left_x = 40 + card_width * 4
		center = self.background.get_rect().centery

		# place center stacks
		for i in range(len(self.model.center_stacks)):
			pile = self.model.center_stacks[i]
			if len(pile) < 1:
				card = self.target_group.makeBlank((CENTER, i))
			else:
				card = self.target_group.makeCard(pile[-1], (CENTER, i))
			card.place(self.background, card.get_rect(centery=center, x=10 + card_width * i))
		# place hand
		player = self.model.players[self.model.active_player]
		for i in range(len(player[HAND])):
			card = self.select_group.makeCard(player[HAND][i], (HAND,None))
			card.place(self.background, card.get_rect(x=10 + card_layer_x * i, 
					y=self.background.get_rect().bottom - card_height))
		#TODO: fliped over opponnts hand

		# place pay-off
		card = self.select_group.makeCard(player[PAY_OFF][-1], (PAY_OFF,None))
		card.place(self.background, card.get_rect(x=10, 
				centery=int(self.background.get_rect().height * 0.73)))
		card = other_group.makeCard(self.model.players[int(not self.model.active_player)][PAY_OFF][-1],
				None)
		card.place(self.background, card.get_rect(x=10, 
				centery=int(self.background.get_rect().height * 0.28)))

		# place player discard piles
		for pile_num in range(self.model.NUM_STACKS):
			for n in range(len(player[DISCARD][pile_num])):
				card = other_group.makeCard(player[DISCARD][pile_num][n], None)
				card.place(self.background, card.get_rect(
						top=20 + center + n * card_layer_y, x=discard_left_x + pile_num * card_width))
				if n == len(player[DISCARD][pile_num])-1:
					self.target_group.addCard(card, (DISCARD, pile_num))
					self.select_group.addCard(card, (DISCARD, pile_num))
			if not len(player[DISCARD][pile_num]):
				card = self.target_group.makeBlank((DISCARD, pile_num))
				card.place(self.background, card.get_rect(
						top=20 + center, x=discard_left_x + pile_num * card_width))

		# place opponents discard piles
		opponent = self.model.players[int(not self.model.active_player)]
		for pile_num in range(self.model.NUM_STACKS):
			for n in range(len(opponent[DISCARD][pile_num])):
				card = other_group.makeCard(opponent[DISCARD][pile_num][n], None)
				card.place(self.background, card.get_rect(
						bottom= center - 20 - n * card_layer_y, x=discard_left_x + pile_num * card_width))
			if not len(opponent[DISCARD][pile_num]):
				card = other_group.makeBlank(None)
				card.place(self.background, card.get_rect(
						bottom= -20 + center, x=discard_left_x + pile_num * card_width))

		# TODO: player text
		# print the players number of screen
		#text = self._build_text("Player %d" % (self.model.active_player + 1))
		#card.place(self.background, rect)


	def show_error(self, message):
		print message
	

	def game_over(self):
		pass
