import threading as thr

x = 0
con = thr.Condition() 
# lck = thr.Lock()

# class summer:
    # def __init__(self, x):
        # x += 1

def proc():
    global x
    con.acquire()
    while not x == 0:
        print (thr.current_thread(), "is waiting")
        con.wait()
    x += 1
    con.notify()
    print (thr.current_thread(), "notification is sent")
    con.release()
    print (thr.current_thread(), x)

def minus():
    global x
    con.acquire()
    while x == 0:
        print (thr.current_thread(), "is waiting")
        con.wait()
    x -= 1
    con.notify()
    print (thr.current_thread(), "notification is sent")
    con.release()
    print (thr.current_thread(), x)
    
def super(needed):
    global x
    con.acquire()
    print (thr.current_thread(), "acquired")
    while x == needed:
        print (thr.current_thread(), "is waiting")
        con.wait()
    print (thr.current_thread(), "needs", needed, "has", x)
    if x > needed:
        x -= 1
    elif x < needed:
        x += 1
    else:
        print (ERR887)
    con.notify()
    print (thr.current_thread(), "notification is sent")
    con.release()
    print (thr.current_thread(), "released, result is", x)
    
for i in range(100):
    p1 = thr.Thread(None, super, None, [3])
    p2 = thr.Thread(None, super, None, [-3])
    p1.start()
    p2.start()
# p1 = thr.Thread(None, proc, 1)
# p2 = thr.Thread(None, proc, 2)
# p1.start()
# p2.start()