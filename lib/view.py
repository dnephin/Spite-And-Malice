"""
 Views for Spite and Malice game.
"""

import pygame
from pygame.locals import *
from player import ConsolePlayer
from cardView import CardImages, CardGroup
from model import *
import logging

log = logging.getLogger('snm.view')

# TODO: highlight selected card


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

	def show_error(self, message):
		log.warn(message)
	
	def inform_game_over(self):
		log.warn("Game Over! Player %d won" % (self.model.active_player+1))


#TODO remote player
class RemotePlayer(Player):
	pass


class HumanPlayer(Player):
	" A human players interface to the game "

	screen = None
	window_size = (650,600)
	STD_FONT = './media/FreeSans.ttf'

	def __init__(self, model):
		# setup pygame 
		if not self.screen:
			pygame.init()
			self.screen = pygame.display.set_mode(HumanPlayer.window_size)
			pygame.display.set_caption('Spite and Malice!')

		self.background = pygame.Surface(self.screen.get_size()).convert()
		self.model = model

	def play_card(self, my_cards, opponents_cards, center_stacks):
		# make card group for cards in the deck
		self.select_group = CardGroup()
		self.target_group = CardGroup()
		# place the cards
		self._draw_board()

		card_selected = False
		# wait for move selection
		while True:
			for event in pygame.event.get():
				# quit
				if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
					return None
				# mouseclick to select target 
				if event.type == MOUSEBUTTONUP and card_selected:
					if self.target_group.findClick(event):
						log.info("Selected %s, %s" % self.target_group.getSelected())
						card, from_location = self.select_group.getSelected()
						to_location = self.target_group.getSelected()[1]
						return (card.model, from_location, to_location)

				# mouseclick to select card
				if event.type == MOUSEBUTTONUP:
					if self.select_group.findClick(event):
						card_selected = True
						log.info("Targeted %s, %s, " % self.select_group.getSelected())
						continue




	def _build_text(self, text, loc):
		" Add text to the screen "
		font = pygame.font.Font("./media/FreeSans.ttf", 18)
		text_surface = font.render(text, 1, (0,0,0))


	def _draw_board(self):
		" place the cards on the screen "
		# group for cards that can not be selected
		other_group = CardGroup()
		background = self.background
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
		player = self.model.players[self.model.active_player]
		for i in range(len(player[HAND])):
			card = self.select_group.makeCard(player[HAND][i], (HAND,None))
			card.place(background, card.get_rect(x=10 + card_layer_x * i, 
					y=background.get_rect().bottom - card_height))

		# place pay-off
		card = self.select_group.makeCard(player[PAY_OFF][-1], (PAY_OFF,None))
		card.place(background, card.get_rect(x=10, 
				centery=int(background.get_rect().height * 0.73)))
		card = other_group.makeCard(self.model.players[int(not self.model.active_player)][PAY_OFF][-1],
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
		opponent = self.model.players[int(not self.model.active_player)]
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
		text = "Player %d" % (self.model.active_player + 1)
		surf = font.render(text, True, (30, 30, 80))
		background.blit(surf, surf.get_rect(left=10, top=center + card_height / 2 + 10))
		#card.place(background, rect)

		self._refresh_view()


	def _refresh_view(self):
		" refresh the view "
		self.screen.blit(self.background, (0,0))
		pygame.display.flip()


	def show_error(self, message):
		# TODO:
		log.warn(message)
		print message
	
	def inform_game_over(self):
		log.warn("Game Over! Player %d won" % (self.model.active_player+1))
		print "Game Over! Player %d won" % (self.model.active_player+1)
		while True:
			for event in pygame.event.get():
				# quit
				if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
					return None

	def end_turn(self):
		" Blank the screen until a click happens "
		self.background.fill((30, 30, 30))
		self._refresh_view()
		while True:
			for event in pygame.event.get():
				if event.type == MOUSEBUTTONUP or event.type == KEYUP:
					return


class GameView(object):

	def __init__(self, model):
		# store model and players
		self.model = model
		self.players = [HumanPlayer(self.model), HumanPlayer(self.model)]

	def get_move(self):
		" Get a move from the player "
		current_view = self.model.build_view_for_player()
		return self.players[self.model.active_player].play_card(*current_view)

	def end_turn(self):
		" End the turn for the current player "
		self.players[self.model.active_player].end_turn()

	def game_over(self):
		" Inform the players the game is over "
		for player in self.players:
			player.inform_game_over()


	def show_error(self, message):
		" Report the error to the user "
		self.players[self.model.active_player].show_error(message)
