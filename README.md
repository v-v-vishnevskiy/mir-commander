# Mir Commander

The primary goal of this project is the creation of a graphical user interface (GUI) for scientific modelling
using [Mir](https://mir.vishnevskiy.group) language and [UNEX](https://unex.vishnevskiy.group) program.
UNEX is a well established software for molecular structure refinement.
Accordingly, Mir Commander will be able to visualize molecular structures as well as other types of numerical data.

Currently we are focused on the very basic functionality, allowing visualizing molecules from files in the standard XYZ format.

## Development

### Linux/Mac
As a prerequisite you have to create a virtual environment and install the required packages (in the command line):
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

The development version of Mir Commander can now be started in the virtual environment as
```
PYTHONPATH=. python3 mir_commander
```

Exiting from the virtual environment can be done by calling the function
```
deactivate
```

In the following the `dev_run.sh` script can be used for fast starting of Mir Commander.

### Windows
In Windows you may need first to install Python3 and Git.
Then in a similar manner as for Linux, it is best to work in a virtual environment.
So the first steps are (run in `cmd` from the top level directory of the repository)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

Mir Commander can now be started from the `cmd` command line in the virtual environment as
```
cmd /V /C "set "PYTHONPATH=." && python mir_commander"
```

To exit from the virtual environment run
```
.venv\Scripts\deactivate
```

When all the required packages are installed it is possible to start Mir Commander by running the batch script `dev_run.cmd`.

### Translation

For generation of translation ts-file(s) run `generate_i18n.sh` (in Linux/macOS).
If at least one of ts-files was updated, you need to generate binary translation qm-files using `ts_to_qm.sh` (in Linux/macOS) or `ts_to_qm.cmd` (in Windows).
