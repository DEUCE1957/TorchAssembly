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
    exec(f"from {'.'.join(parts[:-1])} import {parts[-1]}") # Try to import appropriate module
    return eval(parts[-1]) 