import yaml
from jinja2 import Environment, FileSystemLoader
import subprocess

pythonToCpp = {
    str: "std::string",
    int: "int",
    bool: "bool",
    float: "double",
    list: "//TODO: type(list)",
}


def generate(partialConfig: dict, name: str | None = None) -> str:
    structs = []
    fields = []
    for key, value in partialConfig.items():
        if isinstance(value, dict):
            structs.append(generate(value, key))
        else:
            fields.append({"type": pythonToCpp[type(value)], "name": key})
    renderedStructs = ""
    rendered = ""
    if fields:
        renderedStructs = structTemplate.render(
            data={"name": name, "fields": fields}
        )
        rendered = renderedStructs
    if structs:
        rendered = namespaceTemplate.render(
            data={"name": name, "fields": structs + [renderedStructs]}
        )
    return rendered


def saveHeader(header: str, name: str):
    with open(f"examples/{name}.hpp", "w") as file:
        file.write(header)


def iterate(partialConfig: dict, spacer: int = 0, prevKey: str | None = None):
    for key, value in partialConfig.items():
        if isinstance(value, dict):
            if key == "ros__parameters":
                header = generate(value, prevKey)
                if prevKey is not None:
                    saveHeader(header, prevKey)
                else:
                    raise Exception("Previous key was None")
            else:
                print(" " * spacer + f"{key}:")
                iterate(value, spacer + 2, key)
        else:
            print(" " * spacer + f"{key}: {value}")


with open("examples/config.yaml", "r") as file:
    data = yaml.safe_load(file)
env = Environment(
    loader=FileSystemLoader("templates"), trim_blocks=True, lstrip_blocks=True
)
structTemplate = env.get_template("struct.h.j2")
namespaceTemplate = env.get_template("namespace.h.j2")
config = dict(data)
iterate(config)
subprocess.run("clang-format -i $(ls examples/*.hpp)",shell=True,executable="bash")
