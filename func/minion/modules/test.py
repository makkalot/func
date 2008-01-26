import func_module
import time
import exceptions

class Test(func_module.FuncModule):
    version = "11.11.11"
    api_version = "0.0.1"
    description = "Just a very simple example module"

    def add(self, numb1, numb2):
        return numb1 + numb2

    def ping(self):
        return 1

    def sleep(self,t):
        """
        Sleeps for t seconds, and returns time of day.
        Simply a test function for trying out async and threaded voodoo.
        """
        t = int(t)
        time.sleep(t)
        return time.time()

    def explode(self):
        """
        Testing remote exception handling is useful
        """
        raise exceptions.Exception("khhhhhhaaaaaan!!!!!!")
