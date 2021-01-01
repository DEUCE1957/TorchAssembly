import torch, sys, datetime, time, numpy as np
from pathlib import Path
from torchvision import transforms

base_path = Path(__file__).parent.parent
script_path = Path(__file__).parent
if script_path.__str__() not in sys.path:
    sys.path.append(script_path.__str__())
print(base_path, script_path)
from torch_assembly import BluePrint, HyperParameters

# Show Blueprint choices
choices = [f.name for f in (base_path / "blueprints").iterdir() if f.is_file()]
print("\n".join([f"{i}: {choice}" for i, choice in enumerate(choices)]))
# Check if chosen blueprint is one of the options, repeat until one is selected
while (choice := int(input("Choose a Blueprint: "))) not in range(0, len(choices)):
    print(f"Choice {choice} not in range {0} to {len(choices)}, please try again: ")
prefix, *name = choices[choice].split("_")
name = '_'.join(name)
print("You chose: {prefix}_{name}")

blueprint = BluePrint(prefix, filePath=base_path / "blueprints"/ f"{prefix}_{name}")
print(blueprint)

HyperParameters(blueprint=blueprint)  # Initialize with blueprint
hyperparams = HyperParameters()
hyperparams.wizard() # Choose Hyper-parameters
hyperparams.save(base_path / "hyperparameters")