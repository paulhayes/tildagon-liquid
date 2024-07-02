import app
import math
import imu
from events.input import Buttons, BUTTON_TYPES
from tildagonos import tildagonos
from system.eventbus import eventbus
from system.patterndisplay.events import PatternDisable
from app_components import clear_background

class Liquid(app.App):
    def __init__(self):
        eventbus.emit(PatternDisable())
        self.button_states = Buttons(self)
        self.current=self.imuToScreen( self.normalize(imu.acc_read()) )
        self.angular_speed = 0

    def update(self,delta):
        delta=delta/1000
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()
            return
        
        self.down=self.imuToScreen( self.normalize(imu.acc_read()) )
        self.angular_speed = 0.95*self.angular_speed + 10*delta*self.calc_angle(self.down,self.current)
        self.current = self.normalize( self.rotate(self.current,self.angular_speed*delta) )
        #print("{0} {1}".format(self.angular_speed,delta))
        for i in range(0,12):
            angle = 2*math.pi*(i+3.5)/12
            a = (math.cos(angle),math.sin(angle),0)
            product = self.dot(a,self.current)
            g = self.inverse_lerp(0.33,0.66,product)
                        
            tildagonos.leds[i+1] = self.vectorFloatsToInt( self.lerp3((0,0,0),(0,0,255),g) )

        tildagonos.leds.write()

    def inverse_lerp(self,min,max,x):
        if x<min and x<max:
            return 0
        if x>max and x>min:
            return 1
        return (x-min)/(max-min)

    def lerp(self,a,b,t):
        return a * (1-t) + b * t

    def lerp3(self,a,b,t):
        return (a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t,a[2]*(1-t)+b[2]*t)

    def vectorFloatsToInt(self,a):
        return (int(a[0]),int(a[1]),int(a[2]))

    def draw(self,ctx):        
        clear_background(ctx)
        ctx.save()
        ctx.rgb(255,255,255).begin_path()        
        ctx.move_to(0,0)
        ctx.line_to(self.down[0]*100,self.down[1]*100)
        ctx.stroke()

        ctx.rgb(10,0,0).begin_path()        
        ctx.move_to(0,0)
        ctx.line_to(self.current[0]*150,self.current[1]*150)
        ctx.stroke()


        ctx.restore()

    def imuToScreen(self,a):
        return self.rotate90((-a[0],a[1],a[2]))

    def dot(self,a,b):
        if(len(a)==2 or len(b)==2):
            return a[0]*b[0]+a[1]*b[1]
        return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
    
    def normalize(self,a):
        if(len(a)==2):
            l = math.sqrt(a[0]*a[0]+a[1]*a[1])
            return (a[0]/l,a[1]/l)

        l = math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])
        return (a[0]/l,a[1]/l,a[2]/l)

    def calc_angle(self,a,b):
        return math.atan2( self.dot(a,self.rotate90(b)),self.dot(a,b) )

    def rotate90(self,v):
        return (-v[1],v[0],0)

    def rotate(self,v,a):
        return (
                    v[0]*math.cos(a)-v[1]*math.sin(a),
                    v[0]*math.sin(a)+v[1]*math.cos(a)
                )

__app_export__  = Liquid