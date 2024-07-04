"""A text flag is a set of flags for the display of texts."""

from dataclasses import dataclass

@dataclass()
class TextFlags:
    
    bold: bool = False
    italic: bool = False
    underline: bool = False
    antialias: bool = True

    def with_bold(self, bold: bool = True):
        return TextFlags(bold, self.italic, self.underline, self.antialias)

    def with_italic(self, italic: bool = True):
        return TextFlags(self.bold, italic, self.underline, self.antialias)
    
    def with_underline(self, underline: bool = True):
        return TextFlags(self.bold, self.italic, underline, self.antialias)
    
    def with_antialias(self, antialias: bool = True):
        return TextFlags(self.bold, self.italic, self.underline, antialias)