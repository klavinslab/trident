import json
from os.path import dirname, abspath, join, isfile
from configparser import ConfigParser

VERSION_JSON_PATH = "version.json"
VERSION_TOML = "pyproject.toml"
VERSION_KEY = "tool.poetry"
VERSION_DIR = dirname(abspath(__file__))


def pull_version():
    rel_dir = join(VERSION_DIR, "..", "..")
    config_filename = join(rel_dir, VERSION_TOML)

    config = ConfigParser()
    config.read(config_filename)
    ver_data = dict(config[VERSION_KEY])

    clean = lambda s: s.replace('"', "").replace('"', "")

    for k, v in ver_data.items():
        ver_data[k] = clean(v)

    target_path = join(VERSION_DIR, VERSION_JSON_PATH)
    try:
        with open(target_path, "r") as f:
            print(">> Previous Version:")
            print(f.read())
    except:
        pass

    with open(target_path, "w") as f:
        print("<< New Version (path={}):".format(target_path))
        print(json.dumps(ver_data, indent=2))
        json.dump(ver_data, f, indent=2)


def get_version():
    with open(join(VERSION_DIR, VERSION_JSON_PATH), "r") as f:
        ver = json.load(f)
    return ver


if __name__ == "__main__":
    pull_version()


ver = get_version()

__version__ = ver["version"]
__title__ = ver["name"]
__author__ = ver["authors"]
__homepage__ = ver["homepage"]
__repo__ = ver["repository"]
