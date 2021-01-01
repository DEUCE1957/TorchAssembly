import torch, sys, datetime, time, numpy as np
from pathlib import Path
from torchvision import transforms

base_path = Path(__file__).parent.parent
script_path = Path(__file__).parent
if script_path.__str__() not in sys.path:
    sys.path.append(script_path.__str__())
print(base_path, script_path)
from torch_assembly import BluePrint, HyperParameters

bp = BluePrint(name := input("Chooce Blueprint Name: "),
    filePath=None,**{"architecture":"architectures",
                     "loss":"torch.nn.modules.loss",
                     "activation":"torch.nn.modules.activation",
                     "optimizer":"torch.optim",
                     "no_epochs":int,
                     "batch_size":int,
                     "shuffle":bool,
                     "dropout_probability":float,
                     "learning_rate":float}
)

bp.save(base_path / "blueprints")

# Open Saved File for validation
bp = BluePrint(name, filePath=base_path / "blueprints" / f"BluePrint_{name}.pickle")
print(bp)
# class BluePrint(object):
#     def __init__(self, id, filePath=None, **kwargs):