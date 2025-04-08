"""The figure module contains the figure widget that uses matplotlib to draw figure on the screen."""
from typing import Callable
import matplotlib
from matplotlib.axes import Axes
from matplotlib.figure import Figure as _Fg
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pygame
from ..element import Element
from ..tooltip import Tooltip
from ...cursor import Cursor
from ..art import Art, Rectangle, transform
from .._master import Master
matplotlib.use('agg')

_original_ax_getattribute = Axes.__getattribute__

def _new_ax_gettattribute(self: Axes, name:str):
	attr = _original_ax_getattribute(self, name)
	if (name.startswith(('get', '_', 'set_visible', 'draw', 'stale_callback', 'apply_aspect'))
		or not isinstance(attr, Callable) or isinstance(attr, property)):
		return attr
	if (fig:=self.get_figure()) is not None:
		fig.notify_change()
	return attr

Axes.__getattribute__ = _new_ax_gettattribute

_original_ax_init = Axes.__init__

def _new_ax_init(self: Axes, fig, *args):
	_original_ax_init(self, fig, *args)
	self.patch.set_visible(False)

Axes.__init__ = _new_ax_init

class Figure(_Fg, Element):

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
			dpi = matplotlib.rcParams['figure.dpi']
		figsize = size[0]/dpi, size[1]/dpi
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

		Element.__init__(self, master, background, tooltip, cursor, False, False, None, False)
		self._last_im = None

		self.canvas = FigureCanvasAgg(self)

	def update(self, loop_duration):
		pass

	def make_surface(self):
		if not self.__is_blank_bg:
			# Use the art as background of the figure.
			arr = pygame.surfarray.pixels3d(self.background.get(None, **self.game.settings)).swapaxes(1, 0)
			if self._last_im:
				self._last_im.remove()
			self._last_im = self.figimage(arr, zorder=-1)
		self.canvas.draw()
		return pygame.image.frombytes(self.canvas.tostring_argb(), self.background.size, "ARGB")

	def end(self):
		self.clear()

	def start(self):
		pass
