"""
Starts the GUI
"""

from database import initialize_database

if __name__ == '__main__':
    initialize_database()
    # then launch PySide6 window
