from .Utils import Utils
import chevron
import re

class SailorUtils:
    excluded_tags = ["style", "head", "body", "script", "main", "html", "data", "noscript"]
    key_words = ["repeat", "class", "var", "default", "break"]
    attribute_alias = {
        "class": "className",
    }

    excluded_attributes = ["class", "style"]

    def createArgs(arg):
        alias = arg[0][0] + " " + arg[0][1:] if arg[0][0] == "_" else arg[0]
        name = arg[0].replace("_", "")

        type = arg[1] if isinstance(arg[1], str) else arg[1]["type"]
        utype = SailorUtils.parse_type(type)
        ltype = type.lower() if "binding[" not in type else type[8:-1].lower()
        event = "" if isinstance(arg[1], str) else arg[1]["event"]

        return { 
            "alias": alias, 
            "name": name, 
            "type": utype,
            "ltype": ltype,
            "event": event,
            "isBinding": "binding[" in type,
            }

    def parse_type(type) -> str:
        def wrap_in_func(mystr):
            return f'@autoclosure @escaping () -> {mystr}'
        
        if "char" == type:
            return wrap_in_func("Character")
        
        if "sequence[" in type:
            return  wrap_in_func(type[9:-1]) # wrap_in_func(Utils.capitalize_keep_upper(f'{type[9:-1]}...'))
        
        if "binding[" in type:
            return Utils.capitalize_keep_upper(f'Binding<{type[8:-1]}>')
        
        if "," in type:
            return wrap_in_func(Utils.capitalize_keep_upper(type.split(",")[-1]))
        
        # TODO: someohow convert this value to the first value in Sailor
        if "/" in type:
            return wrap_in_func(Utils.capitalize_keep_upper(type.split("/")[-1]))
        
        return wrap_in_func(Utils.capitalize_keep_upper(type))

    def check_keyword_name(name):
        if name in SailorUtils.key_words:
            return "`" + name + "`"
        return name
    
    # helpers methods

    def formatAttributes(attributes):
        def parse_name(name) -> str:
            return (
                Utils.switch_to_camel(name.replace("*", ""))
            )
        def parse_alias(name) -> str:
            name = parse_name(name)
            if name in SailorUtils.attribute_alias:
                return SailorUtils.attribute_alias[name]

            return name

        return list(
            filter(
                lambda item: item["name"] not in SailorUtils.excluded_attributes,
                map( 
                    # name, value
                    lambda item: {
                        "name": parse_name(item[0]),
                        "alias": parse_alias(item[0]),
                        "description": item[1]["description"],
                        "type": SailorUtils.parse_type(item[1]["type"]),
                        "isWildCard": "*" in item[0],
                        "isSequence": "sequence[" in item[1]["type"],
                        "isMappedBool": "/bool" in item[1]["type"],
                        "isStyle": "style" in item[0],
                    }, 
                    attributes.items()
                )
            )
        )
    
    def formatName(name):
        output = name
        if "@" == output[0]:
            output = output[1:]
        
        output = Utils.switch_to_camel(output)
        return output
    
    def put_formatted(data, names, real_names=None, types=None):

        def mapName(name, type=None):
            if type is None:
                return name
            if "@" == name[0]:
                return f'Utils.when({mapSearch(name)}, ret: "{name[1:]}")'
            if "optional[" in type:
                return f"Utils.unwrapUnit({name})"
            
            return name
        
        def mapSearch(name):
            return SailorUtils.formatName(name)

        if real_names is None:
            real_names = names

        if data[0:4] == "#SEQ":
            data = f'\\({real_names[-1]}.map {{ $0.description }}.joined(separator: "{data[4]}"))' + data[4:]
        
        pattern = re.compile(r"{{\?.*?\?}}")
        matches = []

        # Use finditer() to get match objects, which include the start and end positions
        for match in pattern.finditer(data):
            # Append a tuple with the match and its start and end indices
            matches.append((match.group(), match.start(), match.end()))
            # print("FOUND MATCH", match.group(), match.start(), match.end())
        
        for match in matches:
            found = []
            output = match[0]
            for name, real_name in zip(names, real_names):
                formatted_name = "{{!" + f'{name}' + "}}"
                if formatted_name in match[0]:
                    found.append(real_name)
                    output = output.replace(formatted_name, f'\\({real_name}!.description)')
            
            # print("mid", output)
            condition = ""
            
            for name in found:
                condition += f'{name} != nil && '
            
            if condition != "":
                condition = condition[:-4]
                output = f'\\({condition} ? "{output[3:-3]}" : "")'

            data = data.replace(match[0], output)

        # args = {
        #     'template': data,
        #     'data': {}
        # }
        # for name in names:
        #     args['data'][name] = f'\\({name}.description)'

        # output = chevron.render(**args)

        if types is None:
            for name, real_name in zip(names, real_names):
                data = data.replace("{{" + f'{mapSearch(name)}' + "}}", f'\\({mapName(real_name)})')
        else:
            for name, real_name, type in zip(names, real_names, types):
                data = data.replace("{{" + f'{mapSearch(name)}' + "}}", f'\\({ mapName(real_name, type) })')

        return data
    
    def remove_case_id(name):
        return name.split(":")[0]
    
    def convert_type(value):
        if "optional[" in value:
            return str(value[9:-1]) + "? = nil"
        
        if "sequence[" in value:
            return str(value[9:-1]) + "..."
        
        return value
