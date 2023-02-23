#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2023 Bill Hails
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Apply a calligraphic stroke to a selected path
"""

import inkex
import calligraphic_pen_effect

def path_by_id(id):
    return lambda x: x.id == id


class CalligraphicPenEffectExtension(calligraphic_pen_effect.CalligraphicPenEffect):
    """Apply a calligraphic stroke to a selected path"""

    def effect(self):
        scale, angle, nib_size, units = self.get_args()
        selection = self.svg.selection.filter(inkex.PathElement) if self.options.test_path_id == "none" else self.svg.xpath('//*[@id="' + self.options.test_path_id + '"]')
        for elem in selection:
            self.modify_stroke(elem, nib_size=nib_size, scale=scale, angle=angle, units=units)


if __name__ == '__main__':
    CalligraphicPenEffectExtension().run()
