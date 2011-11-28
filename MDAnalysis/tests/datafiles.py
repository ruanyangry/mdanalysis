# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# MDAnalysis --- http://mdanalysis.googlecode.com
# Copyright (c) 2006-2011 Naveen Michaud-Agrawal,
#               Elizabeth J. Denning, Oliver Beckstein,
#               and contributors (see website for details)
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
#     N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and
#     O. Beckstein. MDAnalysis: A Toolkit for the Analysis of
#     Molecular Dynamics Simulations. J. Comput. Chem. 32 (2011), 2319--2327,
#     doi:10.1002/jcc.21787
#

"""
Location of data files for the MDAnalysis unit tests
====================================================

Real MD simulation data, used for examples and the unit tests::

  from MDAnalysis.tests.datafiles import *

.. Note::

   The actual files are contained in the separate
   :mod:`MDAnalysisTestData` package which must be downloaded from
   http://code.google.com/p/mdanalysis/downloads/list and installed.
"""

try:
    from MDAnalysisTestData.datafiles import *
except ImportError:
    print "*** ERROR ***"
    print "In order to run the MDAnalysis test cases you must install the"
    print "MDAnalysisTestData package (which has been separated from the "
    print "library code itself since release 0.7.4). Go to "
    print
    print "     http://code.google.com/p/mdanalysis/downloads/list"
    print
    print "and download and install the `MDAnalysisTestData-x.y.z.tar.gz'"
    print "which matches your MDAnalysis release or is smaller."
    raise ImportError("MDAnalysisTestData package not installed.")
