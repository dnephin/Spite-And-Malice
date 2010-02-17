"""
 Player classes which accumulate input for Spite and Malice.
"""



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



class ConsolePlayer(Player):

	def play_card(self, my_cards, opponents_cards, center_stacks):
		pass




