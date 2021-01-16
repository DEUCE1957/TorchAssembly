import sys, os, pickle, re, copy, inspect, json, logging
from types import * 
from pathlib import Path
from Color import Color as C
from BluePrint import BluePrint, BluePrintEncoder, BluePrintDecoder
from Utils import class_from_string
# Desired Features:
# > Support Default Values TICK
# > JSON Format TICK
    # > Save/Load as JSON (can edit directly from file) TICK
    # > Allow for conversion to nested Kwargs TICK
# > Support Synonyms
# > Shared Characteristics (only define same hyper-parameter once) TICK
# > Define hyper-parameters dynamically TICK
    # > Add new hyper-parameter to hyper-parameters instance, optionally parent blueprint TICK
# > Parameterise the setup process (smaller function signatures)
# > Add thorough documentation
# > Use same Saving Convention for both Blueprint and Hyperparameters TICK
# > Add Logging (with comet ML)
# > Add Argparse Control
# > Add UnitTesting
# > Add GitHub build status (continuous integration?)


class HyperParameters(object):
    dirPath = None

    def __init__(self, id, blueprint, load_existing=False, custom_dir=None, **kwargs):
        self.id = id
        if HyperParameters.dirPath is None:
            HyperParameters.dirPath = Path.cwd() / "HyperParameters" if custom_dir is None else custom_dir
            HyperParameters.dirPath.mkdir(parents=True, exist_ok=True) # Create directory if it doesn't exist
        if load_existing:
            self.load(HyperParameters.dirPath if custom_dir is None else custom_dir)
        self.blueprint = blueprint

        for k,v in kwargs.items():
            if k not in self.blueprint:
                print(f"{k} not in BluePrint {blueprint.id}")
                continue
            if self.blueprint.check(k, v):
                vars(self).update({k:v})
            else:
                print(f"{k} did not pass BluePrint {blueprint.id} constraints")

    def save(self, custom_dir=None):
        file_path = Path(HyperParameters.dirPath if custom_dir is None else custom_dir) / f"HyperParameters_{self.id}.json"
        with open(file_path, "w") as f:
             json.dump(self, f, cls=HyperParametersEncoder)

    def load(self, custom_dir=None):
        file_path = Path(HyperParameters.dirPath if custom_dir is None else custom_dir) / f"HyperParameters_{self.id}.json"
        if not file_path.exists() and file_path.is_file(): 
            raise FileNotFoundError(f"{file_path} does not exist so it could not be loaded into Hyperparameters {self.id}.")
        with open(file_path, "r") as f:
            kwargs = json.load(f, cls=HyperParametersDecoder)
        vars(self).update(kwargs)
        return self
    
    def fetch_class_hyperparameters(self, cls):
        if not inspect.isclass(cls): raise TypeError(f"Attempted to fetch hyper-parameters for non-class")
        kwargs = {}
        sig = inspect.signature(cls)
        for param in sig.parameters.values():
            if param.default not in [inspect.Parameter.empty, inspect._empty]:
                # Use existing hyper-parameter as default argument, otherwise use existing default argument
                kwargs.update({param.name: vars(self).get(param.name, param.default)})
        return kwargs
            
    def get(self, key, default=None):
        item = vars(self).get(key, default) 
         # If hyper-parameter shows up as option for class, use it instead of default
        return (item, self.fetch_class_hyperparameters(item)) if inspect.isclass(item) else item

    def __getitem__(self, key):
        try:
            item = vars(self).get(key)
        except:
            raise KeyError(f"{key} not in Hyperparameters {self.id}")
         # If hyper-parameter shows up as option for class, use it instead of default
        return (item, self.fetch_class_hyperparameters(item)) if inspect.isclass(item) else item

    def __setitem__(self, key, value, update_blueprint=False):
        if update_blueprint:
            try:
                self.blueprint[key] = value
            except (ValueError, TypeError):
                print(f"Warning: Failed to update Blueprint {self.blueprint.id} with key {key} and value {value}")
        if key in self.blueprint:
            if self.blueprint.check(key, value):
                vars(self).update({key:value})
            else:
                raise ValueError(f"Value {value} for key {key} does not meet constraint: {self.blueprint[key]}")
        else: # Hyperparameter only exists in this instance
            vars(self).update({key:value})

    def __str__(self):
        info_str = f">>> {C.BOLD} Hyper-Parameters '{self.id}' {C.END} <<<"
        for key,value in vars(self).items():
            if key in inspect.signature(self.__init__).parameters.keys(): continue # Ignore __init__ signature params
            if type(value) == tuple:
                info_str += "\n{C.BOLD}{key}{C.END} = {value}"
                if len(value) == 2:
                    if value[1] is not None: info_str += f"\n\t**kwargs = {value[1]}"
            else:
                info_str += f"\n{key} = {value}"
        return info_str

class HyperParametersEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, HyperParameters):
            template = {"id": "default", "__classes__":[],
                        "__primitives__":[]}
            for k, v in vars(obj).items():
                if k == "id":
                    template["id"] = v
                elif callable(v):
                    template["__classes__"].append((k,f"{v.__module__}.{v.__name__}"))
                elif type(v) in [str, int, bool, float]:
                    template["__primitives__"].append((k,v))
            return template
        return json.JSONEncoder.default(self, obj)

class HyperParametersDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, dct):
        if "__classes__" in dct and "__primitives__" in dct: # Is Hyperparameters instance
            kwargs = {}
            for k, v in dct["__classes__"]:
                kwargs[k] = class_from_string(v)
            for k, v in dct["__primitives__"]:
                kwargs[k] = v
            return kwargs
        return dct


if __name__ == "__main__":
    from BluePrint import BluePrint
    import torch
    bp = BluePrint("test")
    bp.load(Path.cwd() / "Blueprints")

    hparams = HyperParameters("test", blueprint=bp, no_epochs=20, shuffle=True, optimizer=torch.optim.ASGD)
    hparams.save()
    hparams2 = HyperParameters("test", blueprint="test")
    hparams2.load()
    print(hparams2.get("optimizer", torch.optim.Adam))
    print(hparams2.get("no_epochs", 10))