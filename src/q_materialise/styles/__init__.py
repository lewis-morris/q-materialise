"""Built‑in style package.

This package contains JSON files defining a selection of default
styles.  Additional styles can be added simply by dropping a
``*.json`` file into this directory.  Each file must contain a
mapping compatible with the :class:`q_materialise.style.Style`
constructor.

You shouldn't need to import anything from this module directly.
Instead use :func:`q_materialise.list_styles` and
:func:`q_materialise.get_style` to discover and load styles.
"""