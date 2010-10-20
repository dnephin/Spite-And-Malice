"""
 Color for terminals.
"""


class Color(object):
	" Colorize output "
	wrap = '\033[%sm'

	red =    '0;31'
	green =  '0;32'
	yellow = '1;33'
	blue =   '0;34'
	lblue =  '1;34'
	lred =   '1;31'
	white =  '1;37'
	lgray =  '0;37'

	color_on = True

	@staticmethod
	def make(color, str):
		if not Color.color_on:
			return str
		return Color.wrap % (color) + str + Color.wrap % ('')


