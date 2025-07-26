Installation
============

Q‑Materialise is published on the Python Package Index and can be
installed with ``pip``.  The project itself is pure Python and does
not bundle any particular Qt binding – you choose which binding to
install.  Because Qt is provided by third‑party packages the library
declares a set of optional dependency groups which pull in the
appropriate binding for you.

Basic installation
------------------

The minimum requirement is Python 3.8 or newer.  To install the
library together with **PySide6** (Qt 6 bindings) run:

.. code-block:: bash

    python -m pip install "q-materialise"

Q‑Materialise will autodetect the available binding at
runtime and raise a clear error if none can be found.

.. code-block:: python

    >>> import q_materialise
    >>> from q_materialise import list_styles
    >>> print(list_styles())
    ['indigo_twilight', 'sapphire_day', ...]

If you encounter an ``ImportError`` complaining that no supported Qt
binding could be imported, install one of the bindings mentioned above.

Choosing a Qt binding
---------------------

Q‑Materialise supports all of the major Python Qt wrappers.  When you
import the package it searches for a binding in the following order:

#. PySide6 – the official Qt 6 bindings from Qt Company.
#. PyQt6 – Riverbank’s Qt 6 bindings.
#. PySide2 – the Qt 5.15 bindings from Qt Company.
#. PyQt5 – Riverbank’s Qt 5.15 bindings.

Whichever binding it finds first will be used throughout the library.
If you wish to target a specific binding ensure it is installed ahead
of the others.  On systems where multiple bindings are present the
order above determines the winner.  You can also bypass binding
detection entirely by importing from :mod:`q_materialise.binding`,
which re‑exports the ``QtCore``, ``QtGui`` and ``QtWidgets`` modules
from whichever binding was selected.

Uninstalling
------------

To remove Q‑Materialise simply uninstall it with pip:

.. code-block:: bash

    python -m pip uninstall q-materialise

The optional Qt binding packages can be uninstalled separately if
desired.