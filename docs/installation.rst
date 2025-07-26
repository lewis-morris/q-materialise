Installation
============

`q-materialise` is distributed on PyPI.  To install the core
library along with your preferred Qt binding use one of the optional
dependency groups defined in the package metadata.  For example, to
install the library together with **PySide6** run:

.. code-block:: bash

    pip install "q-materialise[pyside6]"

Alternatively you can install `PyQt5`, `PyQt6` or `PySide2` by
specifying the corresponding extras:

.. code-block:: bash

    pip install "q-materialise[pyqt6]"

If you prefer to install from a local checkout clone the repository and
install in editable mode:

.. code-block:: bash

    git clone https://github.com/your-user/q-materialise.git
    cd q-materialise
    pip install -e .[pyside6]

The library itself is pure Python and does not require any particular
Qt binding at runtime.  At import time it will attempt to find a
binding in the order PySide6 → PyQt6 → PySide2 → PyQt5 and raise a
meaningful error if none of these are available.  The optional
dependencies in :mod:`pyproject.toml` exist solely to make it easy to
install the binding of your choice.