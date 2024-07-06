from func import *
import threading

fu = func()

t1 = threading.Thread(target=fu.ui)
t1.start()