# QMaterialise

QMaterialise is a modern Material Design stylesheet library for Qt
applications written in Python. It is a ground‑up redesign of the
[qt‑material](https://github.com/UN‑GCPDS/qt‑material) library by UN‑GCPDS, and we’re
grateful for their original work. It draws inspiration from the
Material Design specification and provides a clean and flexible
implementation with:

* **Cross‑binding support** – works with PyQt5, PyQt6, PySide2 and
  PySide6. At runtime the library automatically selects whichever
  binding is installed.
* **Comprehensive colour palettes** – more Material Design colours
  are built in, including all of the primary swatches and their
  tints/shades.
* **Easy customisation** – generate new styles from a few colours or
  load predefined styles shipped with the package. Styles are
  expressed as JSON dictionaries, making them easy to edit and share.
* **Dynamic theming** – apply a new style to a running application
  without restarting it and switch between dark and light variants on
  the fly.
* **Runtime extras** – override button colours, fonts, density scale
  and more by passing an extra dictionary to the inject_style
  function.
* **Export to QSS** – write the generated stylesheet to a `.qss`
  file so it can be used directly in Qt Designer or C++ projects.

Material Design is a design system created by Google. QMaterialise
provides a coherent set of colours and styles that conform to the
specification while still giving you freedom to customise the look and
feel of your application.

## Installation

QMaterialise can be installed from PyPI. Depending on which Qt
binding you intend to use you should also install the corresponding
optional dependency:

```bash
# Install the core library
pip install "q-materialise"

```


## Quick start

The simplest way to style your application is to call
`inject_style()` after you create your `QApplication` instance. This
function accepts either the name of one of the built‑in styles or a
custom `Style` object:

```python
import sys
from q_materialise import inject_style, list_styles

try:
    # Try to import your preferred Qt binding
    from PySide6 import QtWidgets
except ImportError:
    from q_materialise.binding import QtWidgets  # internal helper

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()

# Print the available built‑in styles
print(list_styles())

inject_style(app, style="indigo_twilight")
window.setWindowTitle("QMaterialise Example")
window.resize(480, 320)
window.show()
sys.exit(app.exec())
```

To customise individual aspects of the style, pass an extra
dictionary. For example, to change the colours of different classes
of `QPushButton`:

```python
extra = {
    "danger": "#dc3545",
    "warning": "#ffc107",
    "success": "#198754",
    "info": "#0d6efd",
    "font_family": "Roboto",
    "font_size": "14px",
    "density_scale": 0,
}

inject_style(app, style="sapphire_day", extra=extra)
```

Button classes are attached by setting the `class` property on the
widget:

```python
push_button.setProperty("class", "danger")
```

## Generating custom styles

To create a completely new style programmatically, use the
`generate_style()` function. Pass your primary and secondary base
colours and indicate whether the style should be dark or light. The
function returns a `Style` instance with sensible tints and shades
computed for you:

```python
from q_materialise import generate_style, inject_style

my_style = generate_style(
    name="my_custom_dark",
    primary="#9c27b0",  # purple
    secondary="#ffeb3b",  # yellow
    is_dark=True,
)

inject_style(app, style=my_style)
```

Styles are plain data classes and can be serialised to and from JSON.
For example:

```python
import json

json_string = my_style.to_json(indent=4)
with open("my_style.json", "w", encoding="utf-8") as f:
    f.write(json_string)

# Later
from q_materialise import Style

with open("my_style.json", encoding="utf-8") as f:
    other_style = Style.from_json(f.read())
```

## Listing styles

Built‑in styles are stored as JSON files in the package. You can list
them at runtime with `list_styles()` and load one with
`get_style(name)`:

```python
from q_materialise import list_styles, get_style

print(list_styles())
indigo_style = get_style("indigo_twilight")
```

## Exporting a stylesheet

If you want to use the generated stylesheet outside of Python you can
export it to a `.qss` file. The `export_style()` function takes the
name of the style, the destination file and optional extras:

```python
from q_materialise import export_style

export_style(style="indigo_twilight", qss_path="indigo_twilight.qss")
```

## Documentation

Full documentation is published online and can be accessed at:

[https://lewis-morris.github.io/qmaterialise](https://lewis-morris.github.io/qmaterialise)


## Contributing

Contributions are welcome! If you find a bug or have an idea for a
feature, please open an issue or submit a pull request. Feel free to
add new styles by placing a JSON file in the
`src/q_materialise/styles` directory.

> **Note:** q-materialise is as a redesign of the
> [qt‑material](https://github.com/UN‑GCPDS/qt‑material) project—
> thanks to the UN‑GCPDS team.
