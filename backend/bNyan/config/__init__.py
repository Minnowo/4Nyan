


import os.path 
import sys 
import json 

from .. import util 
from .. import constants_

_config = {
    
}


_default_configs = [
    
]

def load(files=None, sub=None, strict=False, *, conf = _config):
    """Load JSON configuration files"""

    if isinstance(files, str):
        files = [files]

    parsefunc = json.load

    for path in files or _default_configs:

        try:
            with open(path, encoding="utf-8") as file:
                confdict = parsefunc(file)

        except OSError as exc:
            if strict:
                print(exc)
                sys.exit(1)

        except Exception as exc:
            print("Could not parse '%s': %s", path, exc)
            if strict:
                sys.exit(2)
                
        else:
            if not conf:
                if sub:
                    if sub not in conf:
                        conf[sub] = confdict
                        continue

                    util.combine_dict(conf[sub], confdict)
                    continue
                
                conf.update(confdict)
                continue
            
            if sub:
                if sub not in conf:
                    conf[sub] = confdict
                    continue

                util.combine_dict(conf[sub], confdict)
                continue

            util.combine_dict(conf, confdict)

def save(path = constants_.MAIN_CONFIG, sub = None, *, conf = _config):

    util.create_directory_from_file_name(path)

    if sub:
        try:
            for i in sub:
                conf = conf[i]

        except:pass 

    with open(path, "w") as f:
        json.dump(util.replace_set_list(conf), f, indent = 3)


def clear():
    """Reset configuration to an empty state"""
    _config.clear()


def get(path : tuple, key : str, default = None, *, conf = _config):
    """Get the value of property 'key' or a default value"""
    
    if isinstance(path, str):
        path = (path,)

    try:
        for p in path:
            conf = conf[p]
        
        return conf[key]

    except Exception :
        return default


def set(path, key, value, *, conf=_config):
    """Set the value of property 'key' for this session"""
        
    if isinstance(path, str):
        path = (path,)

    for p in path:
        try:
            conf = conf[p]
        except KeyError:
            conf[p] = conf = {}
    conf[key] = value


def setdefault(path, key, value, *, conf=_config):
    """Set the value of property 'key' if it doesn't exist"""
    for p in path:
        try:
            conf = conf[p]
        except KeyError:
            conf[p] = conf = {}
    return conf.setdefault(key, value)


def unset(path, key, *, conf=_config):
    """Unset the value of property 'key'"""
    try:
        for p in path:
            conf = conf[p]
        del conf[key]
    except Exception:
        pass
