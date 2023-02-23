#!/usr/bin/env python
# coding=utf-8
"""
Test elements extra logic from svg xml lxml custom classes.
"""

from inkex.tester import TestCase, ComparisonMixin

from calligraphic_pen_typography_extension import CalligraphicPenTypographyExtension

import sys
sys.path.insert(0, '.')

class CalligraphicPenEffectExtensionComparisonsTestCase(ComparisonMixin, TestCase):
    """Test input and output variations"""
    effect_class = CalligraphicPenTypographyExtension
    comparisons = [
        ('--nib_size=90.0', '--units=px', '--ignore_nib_size=false', '--contrast=50.0', '--angle=45.0')
    ]
    compare_file = "svg/calligraphic_pen_input.svg"
