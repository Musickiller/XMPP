# threading imports
import threading, time, sys
from tkinter import Tk, Canvas, Button, LEFT, RIGHT, NORMAL, DISABLED

import logging

import bot

# globals
# empty

# settings
# Logging level of the main app.
# options: logging.DEBUG, logging.INFO, etc.
main_logging_level = logging.DEBUG

default_logging_format = '%(levelname)-8s %(message)s'

# variables
#nrunners = len(colors) # количество дополнительных потоков

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)-8s %(message)s')




def run(n):
    """Программа бега n-го участника (потока)"""
    global champion
    while 1:
        for i in range(2000): # интенсивные вычисления
            pass
        graph_lock.acquire()
        positions[n] += 1 # передвижение на шаг
        if positions[n] == distance: # если уже финиш
            if champion is None: # и чемпион еще не определен,
                champion = colors[n] # назначается чемпион
            graph_lock.release()
            break
        graph_lock.release()
        
def ready_steady_go():
    """Инициализация начальных позиций и запуск потоков"""
    graph_lock.acquire()
    for i in range(nrunners):
        positions[i] = 0
        threading.Thread(target=run, args=[i,]).start()
    graph_lock.release()
    
def update_positions():
    """Обновление позиций"""
    graph_lock.acquire()
    for n in range(nrunners):
        c.coords(rects[n], 0, n*h, positions[n], n*h+h2)
    tk.update_idletasks() # прорисовка изменений
    graph_lock.release()
    
def quit():
    """Выход из программы"""
    tk.quit()
    sys.exit(0)
# Прорисовка окна
tk = Tk()
tk.title("XMPP chat bot")
c = Canvas(tk, width=400, height=600, bg="White")
c.pack()
go_b = Button(text="Start", command=tk.quit)
go_b.pack(side=LEFT)
quit_b = Button(text="Stop", command=quit)
quit_b.pack(side=RIGHT)
# Замок, регулирующий доступ к функции пакета Tk
graph_lock = threading.Lock()

while 1:
    go_b.config(state=NORMAL), quit_b.config(state=NORMAL)
    tk.mainloop() # Ожидание нажатия клавиш
    champion = None
    ready_steady_go()
    go_b.config(state=DISABLED), quit_b.config(state=DISABLED)
    # Главный поток ждет финиша всех участников
    while sum(positions) < distance*nrunners:
        update_positions()
    update_positions()
    go_b.config(bg=champion) # Кнопка окрашивается в цвет победителя
    tk.update_idletasks()