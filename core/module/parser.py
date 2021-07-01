import hcl2
import sys, os
import re
import json
import ast

from typing import Any, Dict, List, Optional, TypeVar, Union

TYPE_PARSER = r"^\$\{([a-z]+)?\(?([a-z]+)?\)?\(?(\{.*\}|[a-z]+)?\)?\)?\}"

T = TypeVar("T")
Types = List[str]
Value = Optional[str]
Path = Union[str, os.PathLike]


def _remove_list_from_values(data: Dict):
    if isinstance(data, dict):
        new_data = {}
        for key, values in data.items():
            value = {}
            if isinstance(values, list) and values:
                if len(values) == 1:
                    value = values[0]
                else:
                    for val in values:
                        if isinstance(val, dict):
                            for k, v in val.items():
                                value[k] = v
            else:
                value = values
            value = _remove_list_from_values(value)
            new_data[key] = value
        data = new_data
    return data


class TfVariables:
    def __init__(self, module_name: str, filelist: List[str]):
        self.schema_obj = {
            "tittle": module_name,
            "type": "object",
            "properties": {},
            "required": [],
        }
        self.obj = self.load(filelist)

    def _resolve_type(self, type_str: str) -> str:
        _types = {
            "list": "array",
            "map": "object",
            "object": "object",
            "string": "string",
            "number": "number",
            "bool": "boolean",
        }
        return _types.get(type_str, type_str)

    def _guess_type(self, value: Any) -> List:
        if isinstance(value, str):
            return ["string"]
        elif isinstance(value, (int, float)):
            return ["number"]
        elif isinstance(value, bool):
            return ["boolean"]
        elif isinstance(value, list):
            _type = ["array"]
            if len(value) > 0:
                _type.extend(self._guess_type(value[0]))
            else:
                _type.append("string")
            return _type
        elif isinstance(value, dict):
            _type_map = {}
            for k, v in value.items():
                _type_map[k] = self._guess_type(v)

            return ["object", json.dumps(_type_map)]

    def load(self, filelist: List[str]):
        variables = {}
        for filename in filelist:
            with open(filename, "r") as fh:
                hcl_obj = hcl2.load(fh)
                obj = _remove_list_from_values(hcl_obj)
                variables.update(obj.get("variable", {}))

        return variables

    def _parse_type(self, type_str: str) -> List:
        _types = []
        if type_str is not None:
            match = re.match(TYPE_PARSER, type_str)
            _types.extend(
                [self._resolve_type(t) for t in match.groups() if t is not None]
            )
        return _types

    def _schema_str(self, value: Value, description: Value) -> Dict:
        res = {"type": "string"}
        if value is not None:
            res["default"] = value
        if description is not None:
            res["description"] = description
        return res

    def _schema_int(self, value: Value, description: Value) -> Dict:
        res = {"type": "number"}
        if value is not None:
            res["default"] = value
        if description is not None:
            res["description"] = description
        return res

    def _schema_bool(self, value: Value, description: Value) -> Dict:
        res = {"type": "boolean"}
        if value is not None:
            res["default"] = value
        if description is not None:
            res["description"] = description
        return res

    def _schema_list(self, value: Value, description: Value, types: Types = []) -> Dict:
        skema = {}
        skema["type"] = "array"
        if value is not None:
            skema["default"] = value
        if description is not None:
            skema["description"] = description

        if len(types) > 0 and types[0] != "any":
            skema["items"] = self._build(types, None, None)
        else:
            skema["items"] = {"type": "string"}
        return skema

    def _schema_dict(self, value: Value, description: Value, types: Types = []) -> Dict:
        skema = {}
        skema["type"] = "object"
        if value is not None:
            skema["default"] = value
        if description is not None:
            skema["description"] = description

        if len(types) > 0:
            _type = "string" if types[0] == "any" else types[0]
            if _type in ["string", "boolean", "number"]:
                skema["additionalProperties"] = {"type": _type}

            elif _type.startswith("{") and _type.endswith("}"):
                ast_dict = ast.literal_eval(_type)
                skema["properties"] = {}
                for key, value in ast_dict.items():
                    if self._is_go_cty_str(value):
                        type_list = self._parse_type(value)
                    else:
                        type_list = value

                    _property = {"title": key}
                    if len(type_list) > 0:
                        _property.update(self._build(type_list, None, None))
                    else:
                        _property["type"] = "string"

                    skema["properties"][key] = _property

        return skema

    def _is_go_cty_str(self, value: Value) -> bool:
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            return True
        return False

    def _build(self, types: Types, default: Value, description: Value) -> Dict:
        _type = "string"
        if len(types) > 0:
            _type = types[0]

        if _type == "string":
            return self._schema_str(default, description)
        elif _type == "number":
            return self._schema_int(default, description)
        elif _type == "boolean":
            return self._schema_bool(default, description)
        elif _type == "array":
            return self._schema_list(default, description, types[1:])
        elif _type == "object" or _type == "any":
            return self._schema_dict(default, description, types[1:])
        elif _type == "optional":
            return self._build(types[1:], None, None)
        else:
            pass

    def build(self) -> Dict:
        props = self.schema_obj["properties"]
        for variable in self.obj:
            section = self.obj[variable]

            defaultValue = section.get("default")
            description = section.get("description")
            varType = self._parse_type(section.get("type"))

            if len(varType) > 0 and "any" in varType and defaultValue:
                varType = self._guess_type(defaultValue)

            if len(varType) == 0 and defaultValue:
                varType = self._guess_type(defaultValue)

            props[variable] = {"tittle": variable, "description": description}
            props[variable].update(self._build(varType, defaultValue, description))

        return self.schema_obj

    def to_json(self, indent: int = 4) -> str:
        return json.dumps(self.schema_obj, indent=indent)

    def to_dict(self) -> dict:
        return self.schema_obj


class TfOutputs:
    def __init__(self, filelist: List[str]):
        self.outputs = {}
        self.obj = self.load(filelist)

    def load(self, filelist: List[str]):
        outputs = {}
        for filename in filelist:
            with open(filename, "r") as fh:
                hcl_obj = hcl2.load(fh)
                obj = _remove_list_from_values(hcl_obj)
                outputs.update(obj.get("output", {}))
        return outputs

    def build(self):
        for key in self.obj:
            section = self.obj[key]
            description = section.get("description", "")
            self.outputs[key] = description

    def to_json(self, indent: int = 4) -> str:
        return json.dumps(self.outputs, indent=indent)

    def to_dict(self):
        return self.outputs
