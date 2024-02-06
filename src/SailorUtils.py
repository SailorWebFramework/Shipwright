from .Utils import Utils

class SailorUtils:
    excluded_tags = ["style", "head", "body", "script", "main", "html"]
    attribute_alias = {
        "class": "className",
    }

    # helpers methods

    def formatAttributes(attributes):
        def parse_type(type) -> str:
            if "char" == type:
                return "Character"
            
            if "sequence[" in type:
                return Utils.capitalize_keep_upper(f'{type[9:-1]}...')

            if "," in type:
                return Utils.capitalize_keep_upper(type.split(",")[-1])
            
            # TODO: someohow convert this value to the first value in Sailor
            if "/" in type:
                return Utils.capitalize_keep_upper(type.split("/")[-1])
            
            return Utils.capitalize_keep_upper(type)

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
            map( 
                # name, value
                lambda item: {
                    "name": parse_name(item[0]),
                    "alias": parse_alias(item[0]),
                    "description": item[1]["description"],
                    "type": parse_type(item[1]["type"]),
                    "isWildCard": "*" in item[0],
                    "isSequence": "sequence[" in item[1]["type"],
                    "isMappedBool": "/bool" in item[1]["type"],
                    "isStyle": "style" in item[0],
                }, 
                attributes.items()
            )
        )