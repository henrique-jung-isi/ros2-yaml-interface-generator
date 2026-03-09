import yaml
from jinja2 import Environment, FileSystemLoader
import subprocess
import re


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case string to camelCase (lower camel case)."""
    components = snake_str.split("_")
    return components[0] + "".join(x.capitalize() for x in components[1:])


def snake_to_pascal(snake_str: str) -> str:
    """Convert snake_case string to PascalCase (UpperCamelCase)."""
    components = snake_str.split("_")
    return "".join(x.capitalize() for x in components)


typeToCpp = {
    str: "std::string",
    int: "int",
    bool: "bool",
    float: "double",
    list: "//TODO: type(list)",
}

header = """//GENERATED FILE DO NOT EDIT BY HAND!

#pragma once
    
#include <rclcpp/rclcpp.hpp>
#include <string>
#include <sstream>

"""


def generate(
    partialConfig: dict,
    name: str,
    accumulatedName: str | None = None,
    structName: str | None = None,
) -> tuple[str, list]:
    structs = []
    fields = []
    initializations = []
    for key, value in partialConfig.items():
        acc = key if accumulatedName is None else accumulatedName + "." + key
        camel_name = snake_to_camel(key)
        pascal_name = snake_to_pascal(key)
        if isinstance(value, dict):
            [generated, inner] = generate(value, pascal_name, acc, camel_name)
            structs.append(generated)
            initializations += inner
        else:
            fields.append(
                {
                    "type": typeToCpp[type(value)],
                    "name": camel_name,
                }
            )
            initializations.append(
                {
                    "attributeName": acc,
                    "parameterName": key,
                    "fieldName": camel_name,
                    "structName": structName,
                }
            )

    template = namespaceTemplate if accumulatedName is None else innerStructTemplate
    rendered = template.render(
        data={
            "name": name,
            "variableName": structName,
            "fields": fields,
            "structs": structs,
            "initializations": initializations,
        }
    )

    return (rendered, initializations)


def save(source: str, name: str):
    with open(f"examples/{name}.hpp", "w") as file:
        file.write(header + source)


def iterate(partialConfig: dict, spacer: int = 0, prevKey: str | None = None):
    for key, value in partialConfig.items():
        if isinstance(value, dict):
            if key == "ros__parameters" and prevKey is not None:
                pascal_name = snake_to_pascal(prevKey)
                [source, _] = generate(value, pascal_name, None, None)
                save(source, pascal_name)
            else:
                print(" " * spacer + f"{key}:")
                iterate(value, spacer + 2, key)
        else:
            print(" " * spacer + f"{key}: {value}")


with open("examples/src/ros_example/config/config.yaml", "r") as file:
    data = yaml.safe_load(file)
env = Environment(
    loader=FileSystemLoader("templates"), trim_blocks=True, lstrip_blocks=True
)
innerStructTemplate = env.get_template("inner-struct.h.j2")
namespaceTemplate = env.get_template("namespace.h.j2")
config = dict(data)
iterate(config)
subprocess.run("clang-format -i $(ls examples/*.hpp)", shell=True, executable="bash")
