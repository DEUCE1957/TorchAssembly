# Desired Features:
# > JSON Format
    # > Save/Load as JSON (can edit directly from file)
    # > Allow for conversion to nested Kwargs
# > Shared Characteristics (only define same hyper-parameter once)
# > Define hyper-parameters dynamically
    # > Add new hyper-parameter to hyper-parameters instance, optionally parent blueprint
# > Parameterise the setup process (smaller function signatures)
# > Add thorough documentation
# > Use same Saving Convention for both Blueprint and Hyperparameters
# > Add Logging
# > Add Argparse Control
# > Add UnitTesting
# > Add GitHub build status (continuous integration?)
import sys, pickle, re, copy, inspect, json
from types import * 
import torch
import logging
from pathlib import Path
from Color import Color as C

class BluePrint_Settings(object):

    def __init__(id, filePath=None, ):
        pass

class BluePrint(object):

    def __init__(self, id, filePath=None, **kwargs):
        self.id = id
        for k, v in kwargs.items():
            if isinstance(v, ModuleType):
                vars(self).update({k:self.get_module_classes(v)})
            else:
                vars(self).update({k:v})

    def save(self, dirPath):
        with open(dirPath / f"BluePrint_{self.id}.json", "w") as f:
             json.dump(self, f, cls=BluePrintEncoder)

    def load(self, dirPath):
        with open(dirPath / f"BluePrint_{self.id}.json", "r") as f:#
            kwargs = json.load(f, cls=BluePrintDecoder)
        vars(self).update(kwargs)

    def get_module_classes(self, module):
        cls_dict = {}
        for count, (name, cls) in enumerate(inspect.getmembers(module, inspect.isclass)):
            if re.search("__", name) or re.search("^_|_$", name):
                continue
            desc = cls.__doc__
            desc = "No Description Found" if desc is None else desc.split("\n")[0]
            print(f"{count}: {C.BOLD}{name}{C.END} ({desc})")
            cls_dict[count] = cls

        resp = input("Provide digit (e.g. 3), or list of digits (e.g. 2,4,6 ), of elements to IGNORE. 'x' to exit")
        while resp != "x":
            numbers = resp.split(",")
            for number in numbers:
                if number.isdigit():
                    try:
                        del cls_dict[int(number)]
                    except:
                        print(f"Could not remove '{number}' from elements")
                else:
                    print(f"{number} is not a digit")
            print("--------------")
            for count, cls in cls_dict.items():
                desc = cls.__doc__
                desc = "No Description Found" if desc is None else  desc.split("\n")[0]
                print(f"{count}: {C.BOLD}{cls.__name__}{C.END} ({desc})")
            resp = input("Provide digit or list of digits to ignore, 'x' to exit")
        return [class_from_string(f"{module.__name__}.{cls.__name__}") for cls in cls_dict.values()]


    def __eq__(self, other):
        x, y = vars(self), vars(other)
        for k in {**x, **y}.keys():
            if k == "id": continue
            if k not in x or k not in y: return False
            if x[k] != y[k]: return False
        return True

    def __str__(self):
        info_str = f">>> {C.BOLD}BluePrint {self.id}{C.END} <<<\n"
        for key, value in vars(self).items():
            info_str += f"\n{C.BOLD}{key}{C.END}={value.__name__ if isinstance(value, (ModuleType, type)) else value}" # ToDo: Pretty Print 
        return info_str

class BluePrintEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, BluePrint):
            template = {"id": "default", "__modules__":[],
                        "__types__":[], "__values__":[], "__lists__":[]}
            for k, v in vars(obj).items():
                if k == "id":
                    template["id"] = v
                elif isinstance(v, ModuleType):
                    template["__modules__"].append((k, v.__name__))
                elif isinstance(v, type):
                    template["__types__"].append((k,v.__name__))
                elif type(v) in [str, int, bool, float]:
                    template["__values__"].append((k,v))
                elif type(v) is list:
                    template["__lists__"].append((k, [f"{m.__module__}.{m.__name__}" for m in v]))
            return template
        return json.JSONEncoder.default(self, obj)

class BluePrintDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, dct):
        if "__modules__" in dct: # Is BluePrint
            kwargs = {}
            for k, v in dct["__modules__"] + dct["__types__"]:
                # ToDo: Add Import Statement + Error Handling
                kwargs[k] = eval(v)
            for k, v in dct["__values__"]:
                kwargs[k] = v
            for k, v in dct["__lists__"]:
                kwargs[k] = [class_from_string(m) for m in v]
            return kwargs
        return dct

def class_from_string(s):
    """
    Flexibly evaluates a string qualifier to allow for non-standard package hierarchies.
    Input: 
        Full object qualifier (str). Composed of module followed by class name 'MODULE_NAME.CLASS_NAME'
    Output:
        Class
    """
    try:
        cls = eval(s) # E.g. torch.nn.modules.loss.BSEloss
        return cls
    except:
        pass
    parts = s.split(".")
     # E.g. torch.optim.asgd.ASGD -> torch.optim.ASGD
    return eval(".".join(parts[:-2] + [parts[-1]])) # Note: Will throw error if len(parts) < 2


if __name__ == "__main__":
    print(fullname(torch.optim.ASGD), type(fullname(torch.optim.ASGD)))
    bp = BluePrint("test",
        optimizer=torch.optim, 
        loss=torch.nn.modules.loss,
        activation=torch.nn.modules.activation,
        no_epochs=int,
        batch_size=int,
        shuffle=bool,
        dropout_probability=float,
        learning_rate=float,
    )
    bp.save(Path.cwd() / "Blueprints")
    bp2 = BluePrint("test")
    bp2.load(Path.cwd() / "Blueprints")
    print(bp)
    print(bp2)
    print(bp == bp2)