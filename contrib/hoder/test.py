import DataManage

#dasdf = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table="vue2");

class Aclass:
    def __init__(self):
        print "hi"

    def foo(self,Ad):
        print "method Foo of A"
        print Ad

class Bclass(Aclass):
    def __init__(self):
        Aclass.__init__(self)

#super(Bclass,self).__init__(self)
        self.foo("hi")
    
    def foo2(self):
        print "hi"

if __name__ == "__main__":
    fe = Bclass();
    fe.foo("hasdfadsfdfi")
