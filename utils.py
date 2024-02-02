import  sys, select, os, json

class Utils:
    
    def __init__(self, name = "Python Script"):
        self.name = name
        # Init our colors before we need to print anything
        cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        if os.path.exists("colors.json"):
            self.colors_dict = json.load(open("colors.json"))
        else:
            self.colors_dict = {}
        os.chdir(cwd)

    def grab(self, prompt, **kwargs):
            # Takes a prompt, a default, and a timeout and shows it with that timeout
            # returning the result
            timeout = kwargs.get("timeout", 0)
            default = kwargs.get("default", None)
            # If we don't have a timeout - then skip the timed sections
            if timeout <= 0:                
                return input(prompt)                            
            # Write our prompt
            sys.stdout.write(prompt)
            sys.stdout.flush()            
            i, o, e = select.select( [sys.stdin], [], [], timeout )
            if i:
                i = sys.stdin.readline().strip()
            print('')  # needed to move to next line
            if len(i) > 0:
                return i
            else:
                return default