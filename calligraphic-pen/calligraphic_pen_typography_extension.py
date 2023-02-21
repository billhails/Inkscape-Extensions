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
Apply the calligraphic pen stroke to all GlyphLayer-* layers,
preserving a backup of each in Original-GL-* layers
that will be used subsequently.
"""

import inkex
import math
from inkex.paths import CubicSuperPath, Path
from inkex.transforms import Transform
from inkex.styles import Style
from inkex import (
    Group,
    Anchor,
    Switch,
    NamedView,
    Defs,
    Metadata,
    ForeignObject,
    ClipPath,
    Use,
    SvgDocumentElement,
    Layer,
)
import datetime

import calligraphic_pen_effect

NULL_TRANSFORM = Transform([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])


class CalligraphicPenTypographyExtension(calligraphic_pen_effect.CalligraphicPenEffect):
    """
    Apply the calligraphic pen stroke to all GlyphLayer-* layers,
    preserving a backup of each in Original-GL-* layers
    that will be used subsequently.
    """

    def effect(self):
        scale, angle, nib_size = self.get_args()
        originals = {}
        glyphs = {}
        all_names = {}
        for group in self.svg.findall("svg:g"):
            if group.label.startswith("GlyphLayer-"):
                label = group.label[len("GlyphLayer-"):]
                if len(label) > 0:
                    glyphs[label] = group
                    all_names[label] = True
            elif group.label.startswith("Original-GL-"):
                label = group.label[len("Original-GL-"):]
                if len(label) > 0:
                    originals[label] = group
                    all_names[label] = True
        for name in all_names:
            if name in glyphs:
                if name in originals:
                    self.unlink_glyphlayer(glyphs[name])
                else:
                    self.backup_glyphlayer(name, glyphs[name])
                    originals[name] = glyphs[name]
            new_layer = self.copy_glyphlayer(name, originals[name])
            new_layer = self.perform_inlining(new_layer)
            for item in new_layer.iterchildren():
                self.modify_stroke(item, nib_size=nib_size, scale=scale, angle=angle)

    def unlink_glyphlayer(self, layer):
        layer.getparent().remove(layer)

    def backup_glyphlayer(self, suffix, layer):
        self.message(f"backup_glyphlayer {layer.label}")
        layer.getparent().remove(layer)
        layer.label = f'Original-GL-{suffix}'
        self.document.getroot().append(layer)

    def copy_glyphlayer(self, suffix, layer):
        self.message(f"copy_glyphlayer {layer.label}")
        new_layer = Layer.new(f'GlyphLayer-{suffix}')
        new_layer.set("style", "display:none")
        new_layer.append(layer.copy())
        self.document.getroot().append(new_layer)
        return new_layer

    def perform_inlining(self, layer):
        self.message(f"perform_inlining {layer.label}")
        self.flatten(layer)
        self.objects_to_paths(layer)
        return layer

    def objects_to_paths(self, layer):
        for child in layer.iterchildren():
            path = child.to_path_element()
            child.replace_with(path)

    # Flatten a group into same z-order as parent, propagating attribs
    def _ungroup(self, node):
        for child in reversed(list(node)):
            if not isinstance(child, inkex.BaseElement):
                continue

            self.message(f'_ungroup({self.label(node)}) -> {self.label(child)}')
            child.transform = node.transform @ child.transform
            self.message(f'_ungroup({self.label(node)}) -> {self.label(child)} after transform')
            node.getparent().insert(list(node.getparent()).index(node), child)

        node.getparent().remove(node)

    def _ungroup_use(self, use):
        self.message(f'_ungroup_use({self.label(use)})')
        parent = use.getparent()
        uncloned = use.unlink() # also removes from parent and applies transforms

        if isinstance(uncloned, inkex.BaseElement):
            self.message(f'_ungroup_use({self.label(use)}) processing {self.label(uncloned)}')
            parent.append(uncloned)
        else:
            self.message(f'_ungroup_use({self.label(use)}) skipping {self.label(uncloned)}')

        return uncloned

    def deep_ungroup(self, node):
        queue = [node]
        while queue:
            self.message(f'queue {[self.label(x) for x in queue]}')
            node = queue.pop()
            if isinstance(node, (NamedView, Defs, Metadata, ForeignObject)):
                pass
            elif isinstance(node, Use):
                queue.append(self._ungroup_use(node))
            elif isinstance(node, Group):
                if list(node):
                    for child in node.iterchildren():
                        self.message(f'queue.append({self.label(child)})')
                        queue.append(child)
                if node.getparent() is not None:
                    self._ungroup(node)

    def flatten(self, group):
        for child in group.iterchildren():
            self.deep_ungroup(child)


if __name__ == '__main__':
    CalligraphicPenTypographyExtension().run()
