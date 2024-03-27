from .Utils import Utils

class SailorUtils:
    excluded_tags = ["style", "head", "body", "script", "main", "html", "base", "meta", "title", "link"]
    attribute_alias = {
        "class": "className",
    }

    excluded_attributes = ["class", "style", "id"]

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
            return f'(@escaping () -> {mystr})'
        
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