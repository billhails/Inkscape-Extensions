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
Apply a calligraphic stroke to a path
"""

import inkex
from inkex.paths import CubicSuperPath, Path
from inkex.transforms import Transform, Vector2d
from inkex.styles import Style
import datetime


class CalligraphicPenEffect(inkex.EffectExtension):
    """Apply a calligraphic stroke to a path"""

    NULL_TRANSFORM = Transform([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

    debugging = False

    def add_arguments(self, pars):
        pars.add_argument("--nib_size", type=float, default=20.0, help="Nib size in pixels")
        pars.add_argument("--ignore_nib_size", type=inkex.Boolean, default=False, help="Do not use nib size")
        pars.add_argument("--contrast", type=float, default=50.0, help="Amount of contrast")
        pars.add_argument("--angle", type=float, default=0.0, help="Nib Angle")
        pars.add_argument("--units", type=str, default="px", help="Nib Size Units")
        pars.add_argument("--test_path_id", type=str, default="none", help="Path ID for testing")

    def get_args(self):
        scale = 1 - self.options.contrast / 100.0
        nib_size = 0 if self.options.ignore_nib_size else self.options.nib_size
        return scale, self.options.angle, nib_size, self.options.units

    def effect(self):
        raise Exception('child class must implenent effect')

    def modify_stroke(self, elem, *, nib_size, scale, angle, units):
        self.dbg(f"modify_stroke {elem.get_id()}")
        # transfer the elements transform to its points
        if elem.transform:
            self.transform_points(elem, elem.transform)
            elem.transform = self.NULL_TRANSFORM
        start = self.start_point(elem)
        self.dbg(f"modify_stroke {elem.get_id()} start: {start}")
        # transform the points of the path, leaving the stroke width unchanged
        self.transform_points(elem, self.stretch_transform(scale, angle))
        # set the stroke_width
        self.set_nib_size(elem, nib_size, units)
        # inverse transform the path and stroke
        elem.transform = self.shrink_transform(scale, angle)
        end = self.start_point(elem)
        self.dbg(f"modify_stroke {elem.get_id()} end: {end}")

    def stretch_transform(self, scale=1, angle=0):
        return inkex.Transform(scale=(1 / scale, 1)) * inkex.Transform(rotate=(-angle,))

    def shrink_transform(self, scale=1, angle=0):
        return inkex.Transform(rotate=(angle,)) * inkex.Transform(scale=(scale, 1))

    def set_nib_size(self, elem, nib_size, units):
        if nib_size > 0:
            stroke_width = self.svg.unittouu(f'{nib_size}{units}')
            if 'style' in elem.attrib:
                style = dict(Style.parse_str(elem.attrib.get('style')))
            else:
                style = dict()
            style['stroke-width'] = str(stroke_width)
            elem.attrib['style'] = Style(style).to_str()

    def transform_points(self, elem, transform=NULL_TRANSFORM):
        if 'd' in elem.attrib:
            d = elem.get('d')
            p = CubicSuperPath(d)
            p = Path(p).to_absolute().transform(transform)
            elem.set('d', str(Path(CubicSuperPath(p).to_path())))

    def dbg(self, msg):
        if self.debugging:
            with open('./calligraphic_pen.log', 'a') as fh:
                fh.write(f'{datetime.datetime.now()} {msg}\n')
                fh.close()

    def label(self, elem):
        name = elem.__class__.__name__
        if elem.transform:
            transform = elem.transform
        else:
            transform = None
        if elem.label:
            return f'{name} "{elem.label}" transform: {transform}'
        else:
            return f'{name} "{elem.get_id()}"  transform: {transform}'

    def start_point(self, elem):
        return elem.path.to_absolute()[0].end_point(None, Vector2d())