def cell_fit(self, w, h=0, txt='', border=0, ln=0, align='', fill=False, link='', scale=True, force=False):
    # Get string width
    str_width = self.get_string_width(txt)

    # Calculate ratio to fit cell
    if w == 0:
        w = self.w - self.r_margin - self.x
    ratio = (w - self.c_margin * 2) / str_width

    fit = ratio < 1 or (ratio > 1 and force)
    if fit:
        if scale:
            # Calculate horizontal scaling
            horiz_scale = ratio * 100.0
            # Set horizontal scaling
            self._out(f'BT {horiz_scale:.2f} Tz ET')
        else:
            # Calculate character spacing in points
            char_space = (w - self.c_margin * 2 - str_width) / max(len(txt) - 1, 1) * self.k
            # Set character spacing
            self._out(f'BT {char_space:.2f} Tc ET')
        # Override user alignment (since text will fill up cell)
        align = ''

    # Pass on to cell method
    self.cell(w, h, txt, border, ln, align, fill, link)

    # Reset character spacing/horizontal scaling
    if fit:
        self._out(f'BT {"100 Tz" if scale else "0 Tc"} ET')

# Cell with horizontal scaling only if necessary
def cell_fit_scale(self, w, h=0, txt='', border=0, ln=0, align='', fill=False, link=''):
    self.cell_fit(w, h, txt, border, ln, align, fill, link, True, False)

# Cell with horizontal scaling always
def cell_fit_scale_force(self, w, h=0, txt='', border=0, ln=0, align='', fill=False, link=''):
    self.cell_fit(w, h, txt, border, ln, align, fill, link, True, True)

# Cell with character spacing only if necessary
def cell_fit_space(self, w, h=0, txt='', border=0, ln=0, align='', fill=False, link=''):
    self.cell_fit(w, h, txt, border, ln, align, fill, link, False, False)