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
from __future__ import division, absolute_import

from six.moves import zip

import numpy as np

import pytest

from numpy.testing import (assert_equal, assert_almost_equal)

import MDAnalysis as mda
from MDAnalysisTests.datafiles import (
    PDB, PSF, CRD, DCD, GRO, XTC, TRR, PDB_small, PDB_closed, atom_gro, atom_0,
    atom_1, atom_2, atom_single_frame, atom_0_dcd)

from pkg_resources import resource_filename
single_frames = [
    resource_filename(__name__, '../data/chainreader/parts_sf_{}.dcd'.format(i))
    for i in range(10)
]
allframes = resource_filename(__name__, '../data/chainreader/all.dcd')
frames34 = resource_filename(__name__, '../data/chainreader/parts_34.dcd')
frames4567 = resource_filename(__name__, '../data/chainreader/parts_4567.dcd')



class TestChainReader(object):
    prec = 3

    @pytest.fixture()
    def universe(self):
        return mda.Universe(PSF, [DCD, CRD, DCD, CRD, DCD, CRD, CRD])

    def test_next_trajectory(self, universe):
        universe.trajectory.rewind()
        universe.trajectory.next()
        assert_equal(universe.trajectory.ts.frame, 1, "loading frame 2")

    def test_n_atoms(self, universe):
        assert_equal(universe.trajectory.n_atoms, 3341,
                     "wrong number of atoms")

    def test_n_frames(self, universe):
        assert_equal(universe.trajectory.n_frames, 3 * 98 + 4,
                     "wrong number of frames in chained dcd")

    def test_iteration(self, universe):
        for ts in universe.trajectory:
            pass  # just forward to last frame
        assert_equal(universe.trajectory.n_frames - 1, ts.frame,
                     "iteration yielded wrong number of frames ({0:d}), "
                     "should be {1:d}".format(ts.frame,
                                              universe.trajectory.n_frames))

    def test_jump_lastframe_trajectory(self, universe):
        universe.trajectory[-1]
        assert_equal(universe.trajectory.ts.frame + 1,
                     universe.trajectory.n_frames,
                     "indexing last frame with trajectory[-1]")

    def test_slice_trajectory(self, universe):
        frames = [ts.frame for ts in universe.trajectory[5:17:3]]
        assert_equal(frames, [5, 8, 11, 14], "slicing dcd [5:17:3]")

    def test_full_slice(self, universe):
        trj_iter = universe.trajectory[:]
        frames = [ts.frame for ts in trj_iter]
        assert_equal(frames, np.arange(universe.trajectory.n_frames))

    def test_frame_numbering(self, universe):
        universe.trajectory[98]  # index is 0-based and frames are 0-based
        assert_equal(universe.trajectory.frame, 98, "wrong frame number")

    def test_frame(self, universe):
        universe.trajectory[0]
        coord0 = universe.atoms.positions.copy()
        # forward to frame where we repeat original dcd again:
        # dcd:0..97 crd:98 dcd:99..196
        universe.trajectory[99]
        assert_equal(universe.atoms.positions, coord0,
                     "coordinates at frame 1 and 100 should be the same!")

    def test_time(self, universe):
        universe.trajectory[30]  # index and frames 0-based
        assert_almost_equal(
            universe.trajectory.time, 30.0, 5, err_msg="Wrong time of frame")

    def test_write_dcd(self, universe, tmpdir):
        """test that ChainReader written dcd (containing crds) is correct
        (Issue 81)"""
        outfile = str(tmpdir) + "chain-reader.dcd"
        with mda.Writer(outfile, universe.atoms.n_atoms) as W:
            for ts in universe.trajectory:
                W.write(universe)
        universe.trajectory.rewind()
        u = mda.Universe(PSF, outfile)
        for (ts_orig, ts_new) in zip(universe.trajectory, u.trajectory):
            assert_almost_equal(
                ts_orig._pos,
                ts_new._pos,
                self.prec,
                err_msg="Coordinates disagree at frame {0:d}".format(
                    ts_orig.frame))


class TestChainReaderCommonDt(object):
    common_dt = 100.0
    prec = 3

    @pytest.fixture()
    def trajectory(self):
        universe = mda.Universe(
            PSF, [DCD, CRD, DCD, CRD, DCD, CRD, CRD], dt=self.common_dt)
        return universe.trajectory

    def test_time(self, trajectory):
        # We test this for the beginning, middle and end of the trajectory.
        for frame_n in (0, trajectory.n_frames // 2, -1):
            trajectory[frame_n]
            assert_almost_equal(
                trajectory.time,
                trajectory.frame * self.common_dt,
                5,
                err_msg="Wrong time for frame {0:d}".format(frame_n))


class TestChainReaderFormats(object):
    """Test of ChainReader with explicit formats (Issue 76)."""

    def test_set_all_format_tuples(self):
        universe = mda.Universe(GRO, [(PDB, 'pdb'), (XTC, 'xtc'), (TRR,
                                                                   'trr')])
        assert universe.trajectory.n_frames == 21
        assert_equal(universe.trajectory.filenames, [PDB, XTC, TRR])

    def test_set_one_format_tuple(self):
        universe = mda.Universe(PSF, [(PDB_small, 'pdb'), DCD])
        assert universe.trajectory.n_frames == 99

    def test_set_all_formats(self):
        universe = mda.Universe(PSF, [PDB_small, PDB_closed], format='pdb')
        assert universe.trajectory.n_frames == 2


# single frame doesn't work with xtc! NEED TO ACCOUND FOR THAT IN TESTING

class TestChainReaderContinuous(object):
    # description of the frame patterns to test are in comments as lists
    @pytest.fixture
    def top(self):
        return atom_gro

    @pytest.fixture
    def trajs(self):
        return [atom_0, atom_1, atom_2]

    # [0 1 2 3 4 5 6 7 8 9] [0 1 2 4]
    def test_last_frames(self, top):
        # TODO check only one trajectory is used
        u = mda.Universe(top, [allframes, atom_0], continuous=True)
        assert u.trajectory.n_frames == 10
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time, decimal=4)

    # [0 1 2 4] [0 1 2 3 4 5 6 7 8 9]
    def test_last_traj_complete(self, top):
        # TODO check only one trajectory is used
        u = mda.Universe(top, [atom_0, allframes], continuous=True)
        assert u.trajectory.n_frames == 10
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time, decimal=4)

    # [0 1 2 3] [2] [3] [2 3 4 5 6] [5 6 7 8 9]
    def test_middle_frames(self, top):
        # TODO check only one trajectory is used
        u = mda.Universe(top, [atom_0, single_frames[2], single_frames[3], atom_1, atom_2], continuous=True)
        assert u.trajectory.n_frames == 10
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time)

    # [0 1 2 3] [3] [2] [2 3 4 5 6] [5 6 7 8 9]
    def test_middle_frames_order(self, top):
        # TODO check only one trajectory is used
        u = mda.Universe(top, [atom_0, single_frames[3], single_frames[2], atom_1, atom_2], continuous=True)
        assert u.trajectory.n_frames == 10
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time)

    # [0 1 2 3] [2 3 4 5 6] [5 6 7 8 9]
    def test_length(self, top, trajs):
        u = mda.Universe(top, trajs, continuous=True)
        assert u.trajectory.n_frames == 10
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time)

    # [5 6 7 8 9] [2 3 4 5 6] [0 1 2 3]
    def test_reorder(self, top, trajs):
        u = mda.Universe(top, trajs[::-1], continuous=True)
        assert u.trajectory.n_frames == 10
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time)

    # [0 1 2 3] [5 6 7 8 9]
    def test_missing_frame(self, top, trajs):
        with pytest.raises(RuntimeError):
            mda.Universe(top, [trajs[0], trajs[-1]], continuous=True)

    # [0 1 2 3] [4] [5 6 7 8 9]
    def test_single_frame_needed(self, top, trajs):
        u = mda.Universe(top, [trajs[0], single_frames[4], trajs[-1]],
                         continuous=True)
        assert u.trajectory.n_frames == 10

    # [0] [0 1 2 3], [0] [0] [0 1 2 3], [0] [0] [0] [0 1 2 3]
    @pytest.mark.parametrize('frame', ([atom_single_frame, ],
                                       [atom_single_frame, ] * 2,
                                       [atom_single_frame, ] * 3))
    def test_exclude_frame(self, top, frame):
        u = mda.Universe(top, frame + [atom_0_dcd, ], continuous=True)
        assert u.trajectory.n_frames == 4
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time)


    # [0 1 2 3] [1]
    def test_more_excludes(self, top):
        u = mda.Universe(top,  [single_frames[1], atom_0_dcd], continuous=True)
        assert u.trajectory.n_frames == 4
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time)

    # [0 1 2 3] [3]
    def test_last_sinle(self, top):
        u = mda.Universe(top,  [single_frames[3], atom_0_dcd], continuous=True)
        assert u.trajectory.n_frames == 4
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time)
        u.trajectory[3]
        assert u.trajectory.active_reader == u.trajectory.readers[-1]

    # [0 1 2 3] [2 3 4 5 6] [5 6 7 8 9] [4] [8]
    def test_length_with_exclude(self, top, trajs):
        u = mda.Universe(top, trajs + [single_frames[4], single_frames[8]], continuous=True)
        assert u.trajectory.n_frames == 10
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time)

    # repeated [0 1 2 3]
    @pytest.mark.parametrize('number', [1, 2, 3])
    def test_length_same_same(self, top, number):
        u = mda.Universe(top, [atom_0, ] * number, continuous=True)
        assert u.trajectory.n_frames == 4

    # make reader out of single frames
    @pytest.mark.parametrize('frames', (slice(None, None, None),
                                        slice(None, None, -1),
                                        [3,4,2,5,1,0,8,6,9,7]))
    def test_single_frames(self, top, frames):
        u = mda.Universe(top, np.array(single_frames)[frames].tolist(), continuous=True)
        assert u.trajectory.n_frames == 10
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time)

    # [0 1 2 3] [3 4] [4 5 6 7]
    def test_1(self, top):
        u = mda.Universe(top, [atom_0, frames34, frames4567], continuous=True)
        assert u.trajectory.n_frames == 8
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time)

    # [0 1 2 3] [3] [4 5 6 7]
    def test_2(self, top):
        u = mda.Universe(top, [atom_0, single_frames[3], frames4567], continuous=True)
        assert u.trajectory.n_frames == 8
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time)

    # [0 1 2 3] [3] [3 4] [4 5 6 7]
    def test_3(self, top):
        u = mda.Universe(top, [atom_0, single_frames[3], frames34, frames4567], continuous=True)
        assert u.trajectory.n_frames == 8
        for i, ts in enumerate(u.trajectory):
            assert_almost_equal(i, ts.time)


@pytest.mark.parametrize('l', ([(0, 3), (3, 3), (4, 7)],
                               [(0, 9), (0, 4)],
                               [(0, 3), (2, 2), (3, 3), (2, 6), (5, 9)]))
def test_multilevel_arg_sort(l):
    indices = mda.coordinates.chain.multi_level_argsort(l)
    sl = np.array(l)[indices]
    assert_equal(sl, sorted(l))
