# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDAnalysis --- https://www.mdanalysis.org
# Copyright (c) 2006-2017 The MDAnalysis Development Team and contributors
# (see the file AUTHORS for the full list of names)
#
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
# R. J. Gowers, M. Linke, J. Barnoud, T. J. E. Reddy, M. N. Melo, S. L. Seyler,
# D. L. Dotson, J. Domanski, S. Buchoux, I. M. Kenney, and O. Beckstein.
# MDAnalysis: A Python package for the rapid analysis of molecular dynamics
# simulations. In S. Benthall and S. Rostrup editors, Proceedings of the 15th
# Python in Science Conference, pages 102-109, Austin, TX, 2016. SciPy.
#
# N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and O. Beckstein.
# MDAnalysis: A Toolkit for the Analysis of Molecular Dynamics Simulations.
# J. Comput. Chem. 32 (2011), 2319--2327, doi:10.1002/jcc.21787
#

from __future__ import print_function, absolute_import

import pytest
from numpy.testing import assert_equal

import MDAnalysis as mda
from MDAnalysis.lib import NeighborSearch

from MDAnalysisTests.datafiles import PSF, DCD



@pytest.fixture
def universe():
    u = mda.Universe(PSF, DCD)
    u.atoms.translate([100, 100, 100])
    u.atoms.dimensions = [200, 200, 200, 90, 90, 90]
    return u


def test_search(universe):
    """simply check that for a centered protein in a large box pkdtree
    and kdtree return the same result"""
    ns = NeighborSearch.AtomNeighborSearch(universe.atoms)
    pns = NeighborSearch.AtomNeighborSearch(universe.atoms,
                                            universe.atoms.dimensions)

    ns_res = ns.search(universe.atoms[20], 20)
    pns_res = pns.search(universe.atoms[20], 20)
    assert_equal(ns_res, pns_res)
