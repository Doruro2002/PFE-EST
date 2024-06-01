from tkinter import *
from tkinter import ttk
import sys
gui=Tk()
gui.title('Loading...')
gui.geometry('300x200')
def StartProgress():
    progress_var.start(18000)
def StopProgress():
    progress_var.stop()
    sys.exit(-1)
progress_var=ttk.Progressbar(gui,orient=HORIZONTAL,length=400,mode='determinate')
progress_var.pack(pady=30)
btn2=Button(gui,text='stop',command=StopProgress)
btn2.pack(pady=30)
btn=Button(gui,text='progress',command=StartProgress)
btn.pack(pady=30)
btn.invoke()