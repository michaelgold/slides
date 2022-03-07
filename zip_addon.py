import shutil
import json
import sys

with open('bl_info.json') as f:
   bl_info = json.load(f)

sys.dont_write_bytecode = True

if __name__ == "__main__":
    # plugin_version="".join(str(bl_info["version"]))
    plugin_name = bl_info["name"]
    plugin_version = ".".join([str(version_int) for version_int in bl_info["version"]])
    output_filename = "{}-{}".format(plugin_name, plugin_version)

    # build
    shutil.rmtree("dist")
    shutil.copytree(plugin_name, "dist/{}".format(plugin_name), symlinks=True,
                        ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))

    shutil.make_archive(output_filename, 'zip', "dist")
    

    print(output_filename)


