
import sys, os, pickle, re, copy, inspect
from types import * 

# Desired Features:
# > JSON Format
# > Shared Characteristics (only define same hyper-parameter once)
# > Define hyper-parameters dynamically
# > Parameterise the setup process (smaller function signatures)
# > Allow for conversion to nested Kwargs

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


class BluePrint(object):
    def __init__(self, id, filePath=None, **kwargs):
        self.id = id
        if filePath is not None:
            with open(filePath, 'rb') as handle:
                d = pickle.load(handle)
                for key, value in d.items():
                    if key == "id":
                        continue
                    exec("self.{}={}".format(key,value if type(value) is list else value.__name__))
        print(type(kwargs), len(kwargs))
        self.add_items(kwargs)

    def get(self, name):
        if hasattr(self, name):
            return eval("self.{}".format(name))
        else:
            return None

    def get_module_classes(self, moduleName):

        try:
            exec("import {}".format(moduleName))
        except:
            raise ImportError("Module {}".format(moduleName))

        black_list = ["List", ]
        func_list = []
        # ToDo: Select functions to REMOVE not to INCLUDE
        count = 0
        func_dict = {}
        for func in dir(eval(moduleName)):
            if re.search("__", func) or re.search("^_|_$", func) or func in black_list:
                continue

            desc = eval("{}.{}.__doc__".format(moduleName,func))
            if desc is None:
                desc = "No Description Found"
            else:
                desc = desc.split("\n")[0]
            print("{}: {}{}{} ({})".format(count,color.BOLD,func,color.END,desc))

            func_dict[count] = func
            count += 1

        resp = input("Provide digit (e.g. 3), or list of digits (e.g. 2,4,6 ), of elements to IGNORE")

        while resp != "x":
            print("'{}'".format(resp))
            numbers = resp.split(",")
            for number in numbers:
                if number.isdigit():
                    try:
                        del func_dict[int(number)]
                    except:
                        print("Could not remove '{}' from elements")
                else:
                    print("{} is not a digit".format(number))

            print("--------------")
            # clear_output(wait=True)

            for count, func in func_dict.items():
                desc = eval("{}.{}.__doc__".format(moduleName,func))
                if desc is None:
                    desc = "No Description Found"
                else:
                    desc = desc.split("\n")[0]
                print("{}: {}{}{} ({})".format(count,color.BOLD,func,color.END,desc))
            resp = input("Provide digit or list of digits to ignore, 'x' to exit")

        return ["{}.{}".format(moduleName,value) for value in func_dict.values()]

    def add_items(self, item_dict):
        if type(item_dict) is not dict:
            raise TypeError(
                "Items must be a dictionary \{name:type OR list\}")
        for key, value in item_dict.items():
            print("{}:{}".format(key,value))
            if type(key) is str and type(value) is type:
                exec("self.{}={}".format(key,value.__name__))  # int
            elif type(key) is str and type(value) is str:
                exec("self.{}={}".format(key,self.get_module_classes(value)))
            elif type(key) is str and type(value) is list:
                exec("self.{}={}".format(key,value))
            else:
                raise TypeError("Key must be str, value must be type or list")

    def remove_items(self, *names):
        for name in names:
            if hasattr(self, name):
                delattr(self, name)
                print("Removed attribute {} from BluePrint".format(name))
            else:
                print(f"Attribute {name} does not exist in BluePrint")

    def save(self, dirPath):
        d = self.__dict__
        file_path = os.path.join(dirPath, 'BluePrint_{}.pickle'.format(self.id))
        if os.path.exists(file_path):
            raise ValueError("{} already exists".format(file_path))
        with open(file_path, 'wb') as handle:
            pickle.dump(d, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print("Saved BluePrint to file:\n{}".format(file_path))

    def __str__(self):
        info_str = ">>> {0}BluePrint {2}{1} <<<\n".format(color.BOLD,color.END,self.id)
        for key,value in vars(self).items():
            info_str += "\n{0}{2}{1}={3}\n".format(color.BOLD,color.END,key,value)
        return info_str


class HyperParameters(object):
    blueprint = None

    def __init__(self, file_path=None, blueprint=None, verbose = False, **kwargs):
        if file_path is not None:
            if verbose: print("Loading HyperParameters from {}".format(file_path.split(os.path.sep)[-1]))
            with open(file_path, 'rb') as handle:
                d = pickle.load(handle)
                for key, value in d.items():
                    value, kwargs = value
                    if verbose: print(key, str(value), type(value))
                    if type(value) is str:
                        exec("self.{} = ('{}',{})".format(key,value,kwargs))
                    else:
                        exec("self.{}=({},{})".format(key,value,kwargs))
            self.configured = (True, None)
            return

        if HyperParameters.blueprint is None:
            if isinstance(blueprint, BluePrint):
                print("Setting BluePrint for all Hyper-Parameter Instances")
                HyperParameters.blueprint = blueprint
            else:
                raise TypeError(
                    "BluePrint must be provided on 1st instance of Hyper-Parameter Class")

        if len(kwargs) > 1:
            for key, value in kwargs.items():
                if HyperParameters.blueprint.get(key) is not None:
                    try:
                        value, kwargs = value
                        if type(value) is str:
                            exec("self.{}=('{}',{})".format(key,value,kwargs))
                        else:
                            exec("self.{}=({},{})".format(key,value,kwargs))
                    except:
                        exec("self.{}=({},None)".format(key,value))
                else:
                    raise NameError("{} not found in available hyperparameters.".format(key))
            self.configured = (True, None)
        else:
            self.configured = (False, None)

    def wizard(self):
        if self.configured[0]:
            print("Already Configured {}".format(id(self)))
            return False  # Unsuccessful

        for param, abstract_val in HyperParameters.blueprint.__dict__.items():

            is_typed = False
            if param == "id":
                continue
            print(">>> Choose {} <<<".format(param))
            if type(abstract_val) is list:
                print('\n'.join("{}: {}".format(i,abstract_val[i]) for i in range(len(abstract_val))))
            else:
                is_typed = True
                print(abstract_val)
                print("Enter value of Type {}".format(abstract_val.__name__))
            resp = input()
            while True:
                if is_typed == True:
                    try:
                        specific_val = abstract_val(resp)
                    except:
                        resp = input("Please enter value of type {}".format(abstract_val.__name__))
                        continue
                    exec("self.{} = ({},None)".format(param, specific_val)) in locals()
                    break
                else:  # Not Typed
                    if resp.isdigit():
                        try:
                            specific_val = abstract_val[int(resp)]
                        except:
                            resp = input("Please pick an integer index in range {}".format(len(abstract_val)))
                            continue

                        #*package, method = specific_val.split('.')
                        exec("import {}".format('.'.join(specific_val.split('.')[:-1]))) in locals()
                        print(specific_val)
                        
                        method = eval(specific_val)
                        # >>> Display Optional Parameters <<<
                        counter = 0
                        valid_counts = []; kwargs = {}
                        sig = inspect.signature(method)
                        defaults = [param.default for param in sig.parameters.values() if param.default is not inspect.Parameter.empty]
                        args = [param_name for param_name in sig.parameters.keys()]
                        # args,_, _,defaults = inspect.argspec(method.__init__ if inspect.isclass(method) else method)
                        if defaults is not None:
                            offset = len(args)-len(defaults)
                            for i in range(offset,len(args)):
                                key, default_value = args[i], defaults[i-offset]

                                if default_value not in [None]:
                                    print("{}: {} [Default:{}]".format(counter,key,default_value))
                                    valid_counts.append(counter)
                                counter += 1

                            if len(valid_counts) > 0:
                                resp = input("Select parameter by number (e.g. 0), or ENTER to continue")
                                while resp:
                                    if resp.isdigit():
                                        if int(resp) in valid_counts:
                                            key, default_value = args[int(resp)+offset], defaults[int(resp)]
                                            new_value = input("Enter new value of type {} [Default: {}]".format(type(default_value).__name__,
                                                                                                                default_value))
                                            while new_value:
                                                try:
                                                    new_default_val = type(default_value)(new_value)
                                                    break
                                                except:
                                                    new_value = input("Enter new value of type {} [Default: {}]".format(type(default_value).__name__,
                                                                                                        default_value))
                                            kwargs[key] = new_default_val
                                    resp = input("Select parameter by number (e.g. 0), or ENTER to continue")
                        exec("self.{} = ('{}',{})".format(param, specific_val, kwargs)) in locals()
                        break
                    resp = input("Please pick an integer index in range {}".format(len(abstract_val)))
        self.configured = (True, None)
        return True

    def save(self, dirPath):
        name = input("Please select a name for the HyperParameters >>>")
        file_path = os.path.join(dirPath, 'HyperParameters{}.pickle'.format(name))
        if os.path.exists(file_path):
            raise ValueError("{} already exists".format(file_path))
        with open(file_path, 'wb') as handle:
            pickle.dump(self.__dict__, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
        print("Saved HyperParameters to:\n{}".format(file_path))
        return file_path

    def get(self, attribute, default=None, kwargs=False):
        try:
            specific_val, kwargs = eval("self.{}".format(attribute))
        except:
            return default

        try:
            constraint = eval("HyperParameters.blueprint.{}".format(attribute))
        except:
            constraint = None
        if type(constraint) is type:
            return constraint(specific_val)
        else:
            exec("import {}".format('.'.join(specific_val.split('.')[:-1])))
            return eval(specific_val), kwargs

    def as_dict(self):
        return vars(self)
    
    def __str__(self):
        info_str = ">>> {} Hyper-Parameters {} <<<".format(color.BOLD,color.END)
        for key,value in vars(self).items():
            if type(value) == tuple:
                info_str += "\n{0}{2}{1} = {3}".format(color.BOLD,color.END,key,value[0])
                if len(value) == 2:
                    if value[1] is not None: info_str += "\n\t**kwargs = {}".format(value[1])
            else:
                info_str += "\n{} = {}".format(key,value)
        return info_str