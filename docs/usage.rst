Usage
=====

Importing the library
---------------------

The main entry points to Q-Materialise live in the top‑level
:mod:`q_materialise` package.  Upon import the library will locate
a suitable Qt binding and provide a set of helper classes in
:mod:`q_materialise.binding` which mirror the public API of the
underlying binding.  In most cases you will not need to interact
directly with this module because widgets imported from your binding
will work transparently with the stylesheet.

Applying a style
----------------

To apply a style call :func:`~q_materialise.inject_style`
immediately after creating your :class:`~PyQt6.QtWidgets.QApplication`
instance.  You can pass either the name of a built‑in style or a
:class:`~q_materialise.style.Style` instance.

.. code-block:: python

    import sys
    from q_materialise import inject_style
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)
    # choose one of the built‑in styles, for example a light blue palette
    inject_style(app, style="sapphire_day")
    main_window = QtWidgets.QMainWindow()
    main_window.show()
    sys.exit(app.exec())

Listing styles
--------------

Use :func:`~q_materialise.list_styles` to get the names of all
available built‑in styles at runtime:

.. code-block:: python

    from q_materialise import list_styles

    print(list_styles())

Loading styles
--------------

To load one of the built‑in styles as a :class:`~q_materialise.style.Style`
instance call :func:`~q_materialise.get_style`:

.. code-block:: python

    from q_materialise import get_style

    twilight = get_style("indigo_twilight")
    print(twilight.primary)  # e.g. '#3f51b5'

Generating styles
-----------------

You can programmatically generate a new style from a small set of
inputs using :func:`~q_materialise.generate_style`.

.. code-block:: python

    from q_materialise import generate_style

    my_style = generate_style(
        name="my_dark_style",
        primary="#ff5722",
        secondary="#009688",
        is_dark=True,
    )

    print(my_style.to_dict())

Runtime extras
--------------

Additional colours and font settings can be supplied via the `extra`
argument of :func:`~q_materialise.inject_style`.  See the
documentation of that function for a list of recognised keys.  Unknown
keys will be silently ignored.

Exporting stylesheets
---------------------

To write the current style to a `.qss` file use
:func:`~q_materialise.export_style`.  This function accepts a
:class:`~q_materialise.style.Style` instance or a style name, a
destination path and the same optional extras accepted by
:func:`~q_materialise.inject_style`.