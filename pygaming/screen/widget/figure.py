"""The figure module contains the figure widget that uses matplotlib to draw figure on the screen."""
from typing import Callable
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure as _Fg
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pygame
from ..element import Element
from ..tooltip import Tooltip
from ...cursor import Cursor
from ..art import Art, Rectangle, transform
from .._master import Master

_original_ax_getattribute = Axes.__getattribute__

def _new_ax_gettattribute(self: Axes, name:str):
	attr = _original_ax_getattribute(self, name)
	if ((isinstance(attr, Callable) and not isinstance(attr, property))
	 	and not name.startswith(('get', '_', 'draw', 'stale_callback', 'apply_aspect'))
		and (fig:=_original_ax_getattribute(self, 'figure')) is not None
	):
		fig.notify_change()
	return attr

Axes.__getattribute__ = _new_ax_gettattribute

_original_ax_init = Axes.__init__

def _new_ax_init(self: Axes, fig, *args):
	_original_ax_init(self, fig, *args)
	self.patch.set_visible(False)

Axes.__init__ = _new_ax_init

class Figure(_Fg, Element):
	"""
	A Figure is a widget and a matplotlib figure.
	It can be used as any matplotlib figure and will be integrated into the game's window.
	"""

	def __init__(
		self,
		master: Master,
		size: tuple[int, int] = None,
		background: Art = None,
		dpi=None,
		tooltip: Tooltip = None,
		cursor: Cursor = None,
		*,
		smooth_rescaling=True,
		facecolor=None,
		edgecolor=None,
		linewidth=0.0,
		frameon=None,
		subplotpars=None,
		tight_layout=None,
		constrained_layout=None,
		layout=None,
		**kwargs
	):
		if background is None and size is None:
			raise ValueError("Either background or size must be given, got none of them.")
		elif background is not None and size is None:
			size = background.size
			self.__is_blank_bg = False
		elif background is None and size is not None:
			background = Rectangle((255, 255, 255, 255), size[0], size[1])
			self.__is_blank_bg = True
		else:
			background.transform(transform.Resize(size, smooth_rescaling))
			self.__is_blank_bg = False
		
		if dpi is None:
			dpi = rcParams['figure.dpi']
		figsize = size[0]/dpi, size[1]/dpi

		Element.__init__(self, master, background, tooltip, cursor, False, False, None, False)

		_Fg.__init__(self,
			figsize,
			dpi,
			facecolor=facecolor,
			edgecolor=edgecolor,
			linewidth=linewidth,
			frameon=frameon,
			subplotpars=subplotpars,
			tight_layout=tight_layout,
			constrained_layout=constrained_layout,
			layout=layout,
			**kwargs
		)
		
		self._last_gb_artist = None

		self.canvas = FigureCanvasAgg(self)

	def update(self, loop_duration):
		pass

	def make_surface(self):
		if not self.__is_blank_bg:
			# Use the art as background of the figure.
			arr = pygame.surfarray.pixels3d(self.background.get(None, **self.game.settings)).swapaxes(1, 0)
			if self._last_gb_artist:
				self._last_gb_artist.remove()
			self._last_gb_artist = self.figimage(arr, zorder=-1)
		self.canvas.draw()
		return pygame.image.frombytes(self.canvas.tostring_argb(), self.background.size, "ARGB")

	def end(self):
		self.clear()

	def start(self):
		pass
