Q-Materialise Documentation
=============================

Welcome to the documentation for **Q‑Materialise**, an enhanced
Material Design stylesheet library for Qt applications.  This project
is a redesign of the original `qt‑material <https://github.com/UN-GCPDS/qt-material>`_
library developed by the UN‑GCPDS team.  Q‑Materialise retains the
spirit of the original while offering a simplified API, better
customisation and improved readability.  This guide will walk you
through installation, usage and customisation.  If you're new to
the library we recommend starting with the :doc:`installation` and
:doc:`usage` pages.

Why Q‑Materialise?
------------------

Q‑Materialise aims to make it trivial to add a modern, colourful and
responsive look to your Qt applications.  Beyond being a drop‑in
replacement for qt‑material it adds a number of benefits:

* **Cross‑binding support** – the same API works across PyQt5,
  PyQt6, PySide2 and PySide6.  The library automatically detects
  which binding is available at runtime and exports the appropriate
  ``QtCore``, ``QtGui`` and ``QtWidgets`` namespaces.
* **Rich colour palettes** – all primary Material Design swatches are
  included along with their lighter and darker variants.  You can
  generate your own palettes from just two colours or load a
  pre‑defined theme shipped with the package.
* **Dynamic theming** – switch between dark and light variants on
  the fly.  Styles are plain data objects, so it is easy to create
  multiple themes and apply them at runtime.
* **Runtime customisation** – pass an ``extra`` dictionary to
  :func:`q_materialise.inject_style` to override button colours, fonts,
  density scaling and more without touching the underlying JSON files.
* **Export to QSS** – write the generated stylesheet to a ``.qss``
  file using :func:`q_materialise.export_style` and apply it in Qt
  Designer or C++ projects.  This makes Q‑Materialise useful even if
  you are not writing your application in Python.

Throughout the following sections you will learn how to install
Q‑Materialise, apply and customise styles, generate your own themes
and explore the complete API.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   usage
   api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`