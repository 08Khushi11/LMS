import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Ensure TCL_LIBRARY and TK_LIBRARY are set properly for Windows Tkinter initialization
tcl_dir = os.path.join(sys.base_prefix, 'tcl', 'tcl8.6')
tk_dir = os.path.join(sys.base_prefix, 'tcl', 'tk8.6')
if os.path.exists(tcl_dir):
    os.environ['TCL_LIBRARY'] = tcl_dir
if os.path.exists(tk_dir):
    os.environ['TK_LIBRARY'] = tk_dir
