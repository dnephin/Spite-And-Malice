"""
  Unit test for model.py
"""

# TODO: fix path in run script
import sys
sys.path.extend(['../lib', '/home/daniel/media/code/dnlib'])

from model import *
from cardmodels import *

snm = SpiteAndMaliceModel()
print "Players: ", snm.players
print 

for i in range(2):
	snm.active_player = i
	print "View for %d: %s\n" % (i, snm.build_view_for_player())


a = 'A' + Suits.DIAMOND
k = 'K' + Suits.HEART
four = '4' + Suits.CLUB
six= '6' + Suits.HEART
seven = '7' + Suits.HEART
eight = '8' + Suits.HEART

pile = snm.center_stacks[0]
print "%s on pile(%s): %s" % (a, pile, snm.can_place_card_in_center(0, a) == True)
print "%s on pile(%s): %s" % (k, pile, snm.can_place_card_in_center(0, k) == True)
print "%s on pile(%s): %s" % (four, pile, snm.can_place_card_in_center(0, four) == False)

pile.extend([a,k,k])
print "%s on pile(%s): %s" % (four, pile, snm.can_place_card_in_center(0, four) == True)
pile.extend([k,k])
print "%s on pile(%s): %s" % (four, pile, snm.can_place_card_in_center(0, four) == False)
print "%s on pile(%s): %s" % (a, pile, snm.can_place_card_in_center(0, a) == False)
print "%s on pile(%s): %s" % (k, pile, snm.can_place_card_in_center(0, k) == True)
pile.append(six)
print "%s on pile(%s): %s" % (seven, pile, snm.can_place_card_in_center(0, seven) == True)
pile.append(seven)
print "%s on pile(%s): %s" % (eight, pile, snm.can_place_card_in_center(0, eight) == True)

pile = snm.center_stacks[1]
pile.extend([k,k,k])
print "%s on pile(%s): %s" % (four, pile, snm.can_place_card_in_center(1, four) == True)
print 


snm.stock.flip(all=True)
print snm.stock
# TODO: mix into
# TODO: place_card
