import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import os
import sys
from gui import ModernFinanceGUI

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        os.chdir(application_path)

    app = ModernFinanceGUI()
    app.run()