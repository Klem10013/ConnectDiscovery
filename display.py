import os
import time
import math

def round_down(x):
    fr = math.floor(x)
    if x-fr > 0.5:
        return math.ceil(x)
    return fr 

tl = "╭" #Top left
tr = "╮" #Top right
hr = "─" #Horizontal
vr = "│" #Vertical
bl = "╰" #Bottom left
br = "╯" #Bottom right
cl = "├" #Cross left
cc = "┼" #Cross center
cr = "┤" #Cross right
ct = "┬" #Cross top
cb = "┴" #Cross bottom

        #screen += tl + hr + self.name + hr * ((self.size.columns - 3) - len(self.name)) + tr + "\n"
        #for i in range(self.size.lines - 2):
            #if (self.size.lines - 2 - i) <= len(self.lines):
            #    print()
            #    line = self.lines[len(self.lines) - (self.size.lines - 2 - i)]
            #    if len(line) > self.size.columns - 2:
            #        line = line[:self.size.columns - 5] + "..."
            #    screen += vr + line + " " * (self.size.columns - 2 - len(line)) + vr + "\n"
            #else :
            #    screen += vr + " " * (self.size.columns - 2) + vr + "\n"
        #screen += bl + hr * (self.size.columns - 2) + br

class screen:
    def __init__(self,size=None,name:str="",ratio : tuple[float,float] = (1,1)):
        if name != "":
            name = f"[ {name} ]"
        self.name = name
        self.ratio = ratio
        self.lines : list[str] = []
        self.line_changed = False
        self.split_screens : tuple[screen,screen,str] = None
        self.size_old = None
        self.size = size
        if self.size != None:
            self.change_size(size)

    def split_horizontally(self,ratio : float):
        self.split_screens = screen(self.size,"",(1,ratio)),screen(self.size,"",(1,1-ratio)),"h"

    def split_vertical(self,ratio : float):
        self.split_screens = screen(self.size,"",(ratio,1)),screen(self.size,"",(1-ratio,1)),"v"
    
    def change_size(self,size,cut=None,sp=""):
        rc = round_down(size.columns*self.ratio[0])
        rl = round_down(size.lines  *self.ratio[1])
        if cut is not None:
            if sp == "v" and cut[0]+rc == size.columns:
                rc = round_down(size.columns*self.ratio[0]-1)
            if sp == "h" and cut[1]+rl == size.lines:
                rl = round_down(size.lines  *self.ratio[1]-1)
        self.size = os.terminal_size((rc,rl))
        if self.split_screens != None:
            res1 = self.split_screens[0].change_size(self.size)
            self.split_screens[1].change_size(self.size,res1,self.split_screens[2])
        return (rc,rl)

    def change_lines(self,lines : list[str]):
        self.lines = lines
    
    def append(self,message:str):
        self.line_changed = True
        self.lines.append(message)
    
    def clear(self):
        self.line_changed = True
        self.lines.clear()

    def rewwrite_last_line(self,message:str):
        self.line_changed = True
        if len(self.lines) == 0:
            self.lines.append(message)
        else:
            self.lines[-1] = message

    def get_screen(self,indice : int):
        if 0 <= indice < 2:
            return self.split_screens[indice]
        else:
            raise IndexError

    def get_terminal_screen(self,no_top : bool = False, no_bot : bool = False,no_left : bool = False, no_right : bool = False , to_list : bool = False) -> str:
        if self.size is None:
            return "BAD SIZE"
        screen = []
        number_line = self.size.lines - (2 - int(no_top) - int(no_bot))
        if self.split_screens == None:
            if not no_top:
                screen.append((hr if no_left else tl) + hr * (self.size.columns - 2) + (hr if no_right else tr))
            for i in range(number_line):
                line = ""
                if (number_line - i) <= len(self.lines):
                    line = self.lines[len(self.lines) - (number_line - i)]
                    if len(line) > self.size.columns - 2:
                        line = line[:self.size.columns - 5] + "..."
                screen.append((" " if no_left else vr) + line + " " * (self.size.columns - 2 - len(line)) + (" " if no_right else vr))
            if not no_bot:
                screen.append((hr if no_left else bl) + hr * (self.size.columns - 2) + (hr if no_right else br))
            if to_list:
                return screen
            else:
                return "\n".join(screen)

        screen1 = self.split_screens[0]
        screen2 = self.split_screens[1]
        if self.split_screens[2] == "h":
            top_screen_str = screen1.get_terminal_screen(no_top,True, no_left, no_right,True)
            bottom_screen_str = screen2.get_terminal_screen(True,no_bot,no_left, no_right,True)
            screen += top_screen_str
            li = (hr if no_left else cl)
            for i in range(1,self.size.columns - 1):
                if top_screen_str[-1][i] == vr and bottom_screen_str[0][i] == vr:
                    li += cc
                elif top_screen_str[-1][i] == vr and bottom_screen_str[0][i] != vr:
                    li += cb
                elif top_screen_str[-1][i] != vr and bottom_screen_str[0][i] == vr:
                    li += ct
                else:
                    li += hr
            li += (hr if no_right else cr)
            screen.append(li)
            screen += bottom_screen_str
        
        if self.split_screens[2] == "v":
            left_screen_str = screen1.get_terminal_screen(no_top,no_bot, no_left, True , True)
            right_screen_str = screen2.get_terminal_screen(no_top, no_bot, True,no_right, True)
            screen.append(left_screen_str[0] + (vr if no_top else ct) + right_screen_str[0])
            if len(left_screen_str) != len(right_screen_str):
                raise ValueError("Left and Right screen have different heights")
            for i in range(1,len(left_screen_str)-1):
                md = vr
                if left_screen_str[i][-1] == hr and right_screen_str[i][0] == hr:
                    md = cc
                elif left_screen_str[i][-1] == hr and right_screen_str[i][0] != hr:
                    md = cr
                elif left_screen_str[i][-1] != hr and right_screen_str[i][0] == hr:
                    md = cl
                screen.append(left_screen_str[i] + md + right_screen_str[i])
            screen.append(left_screen_str[-1] + (vr if no_bot else cb) + right_screen_str[-1])

        if to_list:
            return screen

        if len(screen) != self.size.lines - 1:
            screen = ["\n"] + screen
        return "\n".join(screen)

    def need_refresh(self,main_fraim:bool = False) -> bool:
        size = os.get_terminal_size()
        if main_fraim and self.size_old != size:
            self.size_old = size
            self.change_size(size)
            return True
        if self.line_changed:
            self.line_changed = False
            return True
        return False if self.split_screens is None else (self.get_screen(1).need_refresh() or self.get_screen(0).need_refresh())


    def draw_terminal_screen(self):
        if self.need_refresh(True):
            os.sys.stdout.write("\n"+self.get_terminal_screen())
            os.sys.stdout.flush()


#if __name__ == "__main__":
#    l = ["a"]
#    size = None
#    name = "Display"
#    sc = screen(name=name)
#    sc.split_horizontally(0.8)
#    while True:
#            sc.draw_terminal_screen()