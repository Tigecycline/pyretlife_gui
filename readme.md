# How to use the GUI
The GUI is implemented with PySide6.
According to the website of PySide (https://doc.qt.io/qtforpython/quickstart.html), it is recommended to run the GUI in a virtual environment.
```
python3 -m venv gui_env
source gui_env/bin/activate
```
The required packages can be installed using `requirements.txt`.
```
pip install -r requirements.txt
```
After installing all required packages, run the gui with
```
python gui.py
```

# Possibility to add more options
In `constants.py`, the options available for various settings can be modified.
These include the gas species, the prior distributions of the parameters, the P-T profile parameterization, the opacity line specifications and the flux unit.
