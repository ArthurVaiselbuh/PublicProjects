import platform

if platform.system() == "Linux":
    from linux_handler import keylistener, start
elif platform.system() == "Windows":
    from win_handler import keylistener, start