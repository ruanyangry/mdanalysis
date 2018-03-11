.. _loading_gromacs: 

###################################
Loading Gromacs files in MDAnalysis
###################################

MDAnalysis is able to read most files used by Gromacs with the exception
of the TNG format which is currently in development.
The TPR file provides a wide variety of topology attributes
and should be used where possible,
however it is also possible to use either a GRO or similar ASCII file.
For the trajectory either an XTC or TRR file can be used,
with the latter also providing velocities and forces if these were saved.

.. seealso::
   `Loading PDB files <load_databank>`
   `Loading XYZ flies <load_xyz>`
   

.. _load_tpr:

TPR files
---------

The :mod:`~MDAnalysis.topology.TPRParser` module allows reading of a
Gromacs_ portable run input file (a `TPR file`_). Because
the file format of the TPR file is changing rapidly, not all versions
are currently supported. The known working versions and the
approximate Gromacs release numbers are listed in the table
:ref:`TPR format versions <TPR-format-table>`.

.. _`TPR-format-table`:

.. table:: TPR format versions and generations read by :func:`MDAnalysis.topology.TPRParser.parse`.

   ========== ============== ==================== =====
   TPX format TPX generation Gromacs release      read
   ========== ============== ==================== =====
   ??         ??             3.3, 3.3.1           no

   58         17             4.0, 4.0.2, 4.0.3,   yes
                             4.0.4, 4.0.5, 4.0.6,
                             4.0.7

   73         23             4.5.0, 4.5.1, 4.5.2, yes
                             4.5.3, 4.5.4, 4.5.5

   83         24             4.6, 4.6.1           yes

   100        26             5.0, 5.0.1, 5.0.2,   yes
                             5.0.3,5.0.4, 5.0.5

   103        26             5.1                  yes

   110        26             2016                 yes
   ========== ============== ==================== =====

For further discussion and notes see `Issue 2`_. Please *open a new issue* in
the `Issue Tracker`_ when a new or different TPR file format version should be
supported.

Bonded interactions available in Gromacs are described in table 5.5 of the
`Gromacs manual`_. The following ones are used to build the topology (see
`Issue 463`_):

* bonds: regular bonds (type 1), G96 bonds (type 2), Morse (type 3),
  cubic bonds (type 4), connections (type 5), harmonic potentials (type 6),
  FENE bonds (type 7), restraint potentials (type 10),
  tabulated potential with exclusion/connection (type 8),
  tabulated potential without exclusion/connection (type 9), constraints with
  exclusion/connection (type 1), constraints without exclusion/connection (type
  2)
* angles: regular angles (type 1), G96 angles (type 2), cross bond-bond
  (type3), cross-bond-angle (type 4), Urey-Bradley (type 5), quartic angles
  (type 6), restricted bending potential (type 10), tabulated angles (type 8)
* dihedrals: proper dihedrals (type 1 and type 9), Ryckaert-Bellemans dihedrals
  (type 3), Fourier dihedrals (type 5), restricted dihedrals (type 10),
  combined bending-torsion potentials (type 11), tabulated dihedral (type 8)
* impropers: improper dihedrals (type 2), periodic improper dihedrals (type 4)

.. _load_gro:


Reading GRO files
-----------------

Stuff about the GRO format specifically

When used as a topology file in a Universe, MDAnalysis will read
``names``, ``ids``, ``resids`` and ``resnames``,
and guess ``masses`` and ``types`` based on the names of atoms.
The ``segid`` for of all atoms is set to "``SYSTEM``".

For implementation details see
:mod:`MDAnalysis.topology.GROParser`.


Writing GRO files
^^^^^^^^^^^^^^^^^

MDAnalysis can also write GRO files, for example using the
:meth:`~MDAnalysis.core.groups.AtomGroup.write` method.
It will attempt to use the ``name``, ``resname`` and ``resid`` attribute
from atoms if available, otherwise default values of "``X``", "``UNK``"
and "``1``" respectively will be used.
If the provided atoms have velocities these will also be written,
otherwise only the positions will be written.
The precision is limited to three decimal places.

By default any written GRO files will renumber the atom ids to move sequentially
from 1.  This can be disabled, and instead the original atom ids kept, by
using the ``reindex=False`` keyword argument.  This is useful when writing a
subsection of a larger Universe while wanting to preserve the original
identities of atoms.

For example::

   >>> u = mda.Universe()`

   >>> u.atoms.write('out.gro', reindex=False)

   # OR
   >>> with mda.Writer('out.gro', reindex=False) as w:
   ...     w.write(u.atoms)




.. Links
.. _Gromacs: http://www.gromacs.org
.. _`Gromacs manual`: http://manual.gromacs.org/documentation/5.1/manual-5.1.pdf
.. _TPR file: http://manual.gromacs.org/current/online/tpr.html
.. _`Issue Tracker`: https://github.com/MDAnalysis/mdanalysis/issues
.. _`Issue 2`: https://github.com/MDAnalysis/mdanalysis/issues/2
.. _`Issue 463`: https://github.com/MDAnalysis/mdanalysis/pull/463
.. _TPRReaderDevelopment: https://github.com/MDAnalysis/mdanalysis/wiki/TPRReaderDevelopment

.. _load_trr:

TRR and XTC files
-----------------


Writing TRR and XTC files
^^^^^^^^^^^^^^^^^^^^^^^^^

Anything interesting about writing these files
