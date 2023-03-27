# Mir Commander

The primary goal of this project is the creation of a graphical user interface (GUI) for scientific modelling
using [Mir](https://mir.vishnevskiy.group) language and [UNEX](https://unex.vishnevskiy.group) program.
UNEX is a well established software for molecular structure refinement.
Accordingly, Mir Commander will be able to visualize molecular structures as well as other types of numerical data.

Currently we are focused on the very basic functionality, allowing visualizing molecules from files in the standard XYZ format.

## Development

As a prerequisite you have to create a virtual environment and install the required packages (in the command line):
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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

