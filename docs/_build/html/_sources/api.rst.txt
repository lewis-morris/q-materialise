API Reference
=============

This section describes the main modules and functions available to
developers using Q‑Materialise.  The high‑level API lives in
``q_materialise`` and exposes helpers to list, load, generate and
apply styles, as well as export them to QSS for use outside of
Python.  The :mod:`~q_materialise.style` module defines the
``Style`` data class, which encapsulates all colour and contrast
information for a palette; you can construct these manually, read
them from JSON or derive them using
:func:`~q_materialise.generate_style`.

The package is organised into a small number of modules:

* :mod:`q_materialise` – the high‑level API.  Import from this module
  to apply a style (:func:`inject_style`), list built‑in themes
  (:func:`list_styles`), load a theme (:func:`get_style`), generate a
  new theme (:func:`generate_style`) or export a stylesheet to QSS
  (:func:`export_style`).  It also re‑exports the most common Qt
  classes from the selected binding (``QtCore``, ``QtGui``,
  ``QtWidgets``).
* :mod:`q_materialise.style` – defines the :class:`~q_materialise.style.Style`
  data class.  Styles encapsulate a complete palette of colours and
  provide methods for serialisation and introspection.
* :mod:`q_materialise.utils` – utility functions for converting
  between hex and RGB, lightening and darkening colours, computing
  perceived brightness and choosing contrast colours.  These are
  pure functions with no dependencies on Qt.
* :mod:`q_materialise.colors` – a dictionary of base colours drawn
  from the Material Design specification.  Use these names when
  generating your own palettes.

The automatically generated API reference below documents all public
classes and functions in each of these modules.  Refer to the
:doc:`usage` page for a hands‑on guide to applying and customising
styles.

Utility functions for working with colours (RGB/hex conversion,
lightening, darkening and computing contrast) live in
:mod:`~q_materialise.utils`.  If you need to manipulate palettes
programmatically these helpers are invaluable.  Finally, the
:mod:`~q_materialise.colors` module contains some curated sets of
colours used by the palette generator.  When browsing the API below
remember that many functions accept an ``extra`` mapping; see the
documentation for :func:`~q_materialise.inject_style` for details on
how to override fonts, density and special button classes at run time.

.. automodule:: q_materialise
    :members:
    :undoc-members:
    :imported-members:
    :show-inheritance:

.. automodule:: q_materialise.style
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: q_materialise.utils
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: q_materialise.colors
    :members:
    :undoc-members:
    :show-inheritance: