class BaseClass:
    def function(self):
        print(self.__class__.__name__)


class SonClass(BaseClass):
    def init():
        pass

if __name__=='__main__':
    BaseClass().function()
    SonClass().function()