# Changelog

## v0.2.0 – Enhanced UI and update notifications

### New Features

- Added automatic update checking to notify users of new releases

### UI Changes

- Refined context menu styling for improved visual consistency

### Improvements

- Enabled left mouse button click interaction for the header control block

### Plugins

#### Molecular visualizer

- Added "background color" option to Save Image dialog
- Added Appearance control block with "background color" option and style

## v0.1.1 – UI improvements and bug fixes

### UI Changes

- Changed button icon sizes (minimize, maximize, close) for program windows
- Unified TabBar widget styling
- Unified scrollbar styling
- Added ability to select built-in font and size
- Set "Fusion" theme from Qt

### Bug Fixes

- Fixed transparent area in program window for CartesianEditor plugin on Windows
- Fixed maximized window state not being cleared when closing a maximized program window (other windows would incorrectly become maximized)
- Fixed molecule jittering in molecule visualizer on first window resize
- Fixed molecule size in molecule visualizer in perspective projection when window is narrow

## v0.1 – Initial release with molecular visualization, coordinate editing, and multi-platform support

### Cross-Platform Support

Mir Commander is now available on all major operating systems with native builds.

- macOS (Apple Silicon ARM64)
- Linux (x86_64 and ARM64)
- Windows (x86_64)

### Molecular Visualizer

Advanced 3D visualization tool for molecular structures with interactive controls and multiple rendering modes.

- Multiple rendering styles: ball-and-stick, space-filling, wireframe, and more
- Atom labels in various formats: symbol with number, symbol only, or number only
- Selection and manipulation of individual atoms or groups
- Coordinate axes display with customizable colors, sizes, and labels
- Isosurface visualization from three-dimensional discrete scalar fields (voxels)
- High-resolution image export with customizable dimensions
- Batch operations on multiple visualizers simultaneously
- High-performance 3D rendering engine capable of visualizing hundreds of thousands of atoms

### Cartesian Editor

Powerful editor for manipulating atomic coordinates with precision and ease.

- Add new atoms with specified coordinates and element symbols
- Edit atom element symbols
- Direct editing of X, Y, and Z coordinates with high precision
- Modify atom index numbers
- Delete selected atoms
- Automatic synchronization of all changes with all open visualizers

### File Format Support

Import molecular data from a wide variety of computational chemistry and molecular modeling file formats.

- Import: XYZ, UNEX v1/v2, MDL Molfile V2000, Gaussian cube, Cfour, ADF, DALTON, Firefly, GAMESS, Gaussian, Jaguar, Molcas, Molpro, MOPAC, NBO, NWChem, ORCA, Psi4, Q-Chem, Turbomole
- Export: XYZ format

### Localization

Interface is available in multiple languages to make the software accessible to a wider audience.

- English language support
- Russian language support
