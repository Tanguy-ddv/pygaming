"""The figure module contains the figure widget that uses matplotlib to draw figure on the screen."""
from typing import Callable
from matplotlib import rcParams
from matplotlib.axes import Axes
from matplotlib.figure import Figure as _Fg
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pygame
from .._abstract import Placeable
from ..art import Art, Rectangle, transform
from ..frame import Frame

_initial_fig_update = _Fg.update

_Fg.set_master = lambda self, master: None
_Fg.set_update_if_invisible = lambda self, update_if_invisible: None


_original_ax_getattribute = Axes.__getattribute__

def _new_ax_gettattribute(self: Axes, name: str):
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

class Figure(Placeable, _Fg):
	"""
	A Figure is a widget and a matplotlib figure.
	It can be used as any matplotlib figure and will be integrated into the game's window.
	"""

	def __init__(
		self,
		master: Frame,
		background: Art = None,
		size: tuple[int, int] = None,
		dpi: int = rcParams['figure.dpi'],
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
		"""
		figure
		"""
		if background is None and size is None:
			size = rcParams['figure.figsize'][0]*dpi, rcParams['figure.figsize'][1]*dpi
			background = Rectangle((255, 255, 255, 255), size[0], size[1])
			self.__is_blank_bg = True
		elif background is not None and size is None:
			size = background.size
			self.__is_blank_bg = False
		elif background is None and size is not None:
			background = Rectangle((255, 255, 255, 255), size[0], size[1])
			self.__is_blank_bg = True
		else:
			background.transform(transform.Resize(size, smooth_rescaling))
			self.__is_blank_bg = False
		
		self._height = background.height
		self._width = background.width
		
		if dpi is None:
			dpi = rcParams['figure.dpi']
		figsize = size[0]/dpi, size[1]/dpi

		super().__init__(
			master=master,
			figsize=figsize,
			dpi=dpi,
			facecolor=facecolor,
			edgecolor=edgecolor,
			linewidth=linewidth,
			frameon=frameon,
			subplotpars=subplotpars,
			tight_layout=tight_layout,
			constrained_layout=constrained_layout,
			update_if_invisible=False,
			layout=layout,
			**kwargs
		)

		self._last_bg_artist = None
		self.canvas = FigureCanvasAgg(self)
		self.canvas.figure.set_size_inches(figsize)
		self.canvas.figure.set_dpi(dpi)
		self._background = background

	@property
	def width(self):
		return self._width

	@property
	def height(self):
		return self._height
	
	def update_(self, props):
		"""original matplotlib update method."""
		_initial_fig_update(self, props)

	def loop(self, dt):
		if not self.__is_blank_bg and (self.is_visible() or self._update_if_invisible):
			has_changed = self._background.update(dt)
			if has_changed:
				self.notify_change()
		super().loop(dt)

	def make_surface(self):
		if not self.__is_blank_bg:
			# Use the art as background of the figure.
			arr = pygame.surfarray.pixels3d(self._background.get(None, **self.game.settings)).swapaxes(1, 0)
			if self._last_bg_artist is not None:
				self._last_bg_artist.remove()
			self._last_bg_artist = self.figimage(arr, zorder=-1)
		self.canvas.draw()
		print(self.canvas.get_width_height(physical=True), self.size)
		return pygame.image.frombytes(self.canvas.tostring_argb(), self.canvas.get_width_height(physical=True), "ARGB")

	def finish(self):
		super().finish()
		self.clear()
