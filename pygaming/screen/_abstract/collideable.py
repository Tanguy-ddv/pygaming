from typing import Optional
from .placeable import Placeable
from ..hitbox import Hitbox
from ...inputs import Click
from .master import Master

class Collideable(Placeable):

    def __init__(self, master: Master, update_if_invisible: bool, hitbox: Hitbox | None, **kwargs):
        super().__init__(master=master, update_if_invisible=update_if_invisible, **kwargs)
        if hitbox is None:
            hitbox = Hitbox(0, 0, *self.size)
        self.hitbox = hitbox

    def begin(self, **kwargs):
        self.hitbox.load(self.game.settings)
        super().begin(**kwargs)
    
    def finish(self):
        super().finish()
        self.hitbox.unload()
    
    def is_contact(self, pos: Optional[Click | tuple[int, int]]):
        """Return whether the position, relative to the top left of the master of this element, is in contact with the element."""
        if pos is None or not self.on_master:
            return False
        ck = Click(*pos).make_local_click(self.absolute_left, self.absolute_top, self.master.wc_ratio)
        return self.hitbox.is_contact((ck.x, ck.y))
