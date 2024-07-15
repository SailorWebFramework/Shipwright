import click
import chevron
import os
import json

from .Utils import Utils
from .SailorUtils import SailorUtils

class Sailor:

    def build(outdir, treasuredir):
        # click.echo(f"{outdir} : {treasuredir}.")

        if not os.path.exists(treasuredir):
            click.echo(f"cannot generate build treasure does not exist at {treasuredir}.")
            return 

        click.echo(f"building sailor...")
        
        # build tags
        htmlout = os.path.join(outdir, "Tags")
        Utils.checkAndCreate(htmlout)

        Sailor.buildTags(htmlout, treasuredir)

        # build units
        unitsout = os.path.join(outdir, "Units")
        Utils.checkAndCreate(unitsout)

        Sailor.buildUnits(unitsout, treasuredir)

        Sailor.buildLanguageUnits(unitsout, treasuredir)

        # build events
        unitsout = os.path.join(outdir, "Events")
        Utils.checkAndCreate(unitsout)

        Sailor.buildEvents()

        # build events
        Sailor.buildEventResultMap()

        # build attributes
        Sailor.buildGlobalAttributeGroup(outdir, treasuredir)

        # build tailwind
        # Sailor.buildTailwind(outdir, treasuredir)

        # todo: css properties
        Sailor.buildCSSProperties(outdir, treasuredir)

        return 
    
    def buildTags(outdir, treasuredir):
        # TODO: Utils.templates, Utils.tags
        tag_treasure = os.path.join(treasuredir, "tags.json")
        templateURL = os.path.join("Templates", 'Sailor', "HTML", "Tag.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)
        
        for tag, body in data.items():
            tag = tag.lower()

            description = body["description"]

            if "attributes" not in body:
                attributes = []
            else:
                attributes = SailorUtils.formatAttributes(body["attributes"])

            if tag in SailorUtils.excluded_tags:
                continue

            # if "alias" in body:
            #     ctag = body["alias"]
            # else:
            #     ctag = tag.capitalize()
            ctag = tag.capitalize()

            # def check_init(name):
            #     for init in body["inits"]:
            #         if name == init["type"]:
            #             return True
            #     return False

            # TODO: add this back in, removed for 0.2
            
            args = {
                "ctag": ctag,
                "tag": tag.lower(),
                "head": body["type"] == "head" if "type" in body else False,
                "description": description,
                "attributes": attributes,
                "inits": list(map(lambda v: {
                    "initRequired": v["type"] == "required",
                    "initRequiredWithBody": v["type"] == "required-with-body",
                    "initRequiredWithText": v["type"] == "required-with-text",
                    "initEmpty": v["type"] == "empty",
                    "initText": v["type"] == "text", # and not check_init("body")
                    "initBody": v["type"] == "body",
                    "args": Utils.createLastElementDictArray(list(map(lambda arg: SailorUtils.createArgs(arg), v["args"].items())) if "args" in v else [])
                }, body["inits"]))
            }

            # # add default inits for all tags
            # args["inits"] = list(filter(lambda v: v["initRequired"] or v["initRequiredWithBody"], args["inits"]))

            # args["inits"].append({
            #     "initRequired": False,
            #     "initRequiredWithBody": False,
            #     "initEmpty": True,
            #     "initText": False,
            #     "initBody":True,
            #     "args": False
            # })
            
            # print(args)
            out_url = os.path.join(outdir, f"HTML+{args['ctag']}.swift")

            Utils.build(templateURL, out_url, args)

        f.close()

    def buildTailwind(outdir, treasuredir):
        tag_treasure = os.path.join(treasuredir, "tailwind.json")
        templateURL = os.path.join("Templates", "Sailor", "Styling", "Tailwind+Classes.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)

        def convert_name(name):
            if name[0] == "-":
                name = "neg" + name[1:]
            name = name.replace(" ", "")
            name = name.replace("/", "v")
            name = name.replace("\n", "")
            name = name.replace(".", "")
            name = name.replace("*", "")
            name = name.replace("#", "")
            name = name.replace(":", "")
            return name

        classes = list(
            map(
                lambda v: {
                    "name": v[0].replace(".", ""),
                    "alias": Utils.switch_to_camel(convert_name(v[0].replace(".", ""))),
                    "description": v[1].replace("\n", ""),
                    "isPack": ":" in v[0],
                }, data.items()
            )
        )
        packables = list(
            filter(
                lambda v: ":" not in v["name"],
                map(
                    lambda v: {
                        "name": v[0].replace(".", ""),
                        "alias": Utils.switch_to_camel(convert_name(v[0].replace(".", ""))),
                        "description": v[1].replace("\n", ""),
                    }, data.items()
                )
            )
        )

        args = {
            "description": "Tailwind CSS classes supported on sailor.",
            "cases": classes,
            "packables": packables
        }

        out_url = os.path.join(outdir, "Tailwind+Classes.swift")
        Utils.build(templateURL, out_url, args)

    def buildGlobalAttributeGroup(outdir, treasuredir):
        # TODO: Utils.templates, Utils.tags
        tag_treasure = os.path.join(treasuredir, "global-attributes.json")
        templateURL = os.path.join("Templates", "Sailor", "HTML", "GlobalAttributeGroup.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)

        attributes = SailorUtils.formatAttributes(data)
        
        args = {
            "description": "Group of all global attributes, which are attributes that can be used with any HTML element.",
            "attributes": attributes,
        }

        out_url = os.path.join(outdir, "GlobalAttributeGroup.swift")
        Utils.build(templateURL, out_url, args)

    def buildPropUnits(outdir, treasuredir):
        unit_treasure = os.path.join(treasuredir, "units.json")
        # punit_treasure = os.path.join(treasuredir, "property_units.json")

        templateURL = os.path.join("Templates", 'Sailor', "HTML", "PropUnit+Units.mustache")
        # TODO:
        
    def buildUnits(outdir, treasuredir):
        tag_treasure = os.path.join(treasuredir, "units.json")
        templateURL = os.path.join("Templates", 'Sailor', "HTML", "Unit+Enum.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)

        def format_cases(body):
            return list(
                map(lambda v: {
                "name": SailorUtils.remove_case_id(v[0]),
                "alias": SailorUtils.remove_case_id(v[0]),
                "description": v[1]["description"],
                "args": [
                    {
                        "name": SailorUtils.formatName(name), 
                        "value": SailorUtils.convert_type(value),
                        "isShown": isShown,
                    } for value, name, isShown in zip(
                        v[1]["values"] if "values" in v[1] else [], 
                        v[1]["names"] if "names" in v[1] else [],
                        ([True] * len(v[1]["names"] if "names" in v[1] else []) if "showNames" in v[1] else
                        v[1]["shown"] if "shown" in v[1] 
                        else [False] * len(v[1]["names"] if "names" in v[1] else [])),
                    )
                ],
                # "values": v[1]["values"] if "values" in v[1] else [],
                # "names": v[1]["names"] if "names" in v[1] else [],
                "hasAssociatedValue": "values" in v[1],
                "isFormatted": "format" in v[1],
                "format": SailorUtils.put_formatted(v[1]["format"], v[1]["names"], types=v[1]["values"]) if "format" in v[1] else "",
                "last": False
            }, body["cases"].items()))

        for name, body in data.items():
            description = body["description"]
            cname = Utils.capitalize_keep_upper(name)
            cases = format_cases(body)

            if "inherit" in body:
                for inherited_unit in body["inherit"]:
                    cases.extend(format_cases(data[inherited_unit]))

            for case in cases:
                case["alias"] = Utils.switch_to_camel(case["alias"])

                for arg in case["args"]: arg["last"] = False
                
                if len(case["args"]) > 0:
                    case["args"][-1]["last"] = True
                
                # case["values"] = list(map(lambda v: {"value": v, "last": False}, case["values"]))
                
                # if len(case["values"]) > 0:
                #     case["values"][-1]["last"] = True

            cases[-1]["last"] = True

            args = {
                "cname": cname,
                "cases": cases,
                "description": description
            }

            out_url = os.path.join(outdir, f"Unit+{cname}.swift")

            Utils.build(templateURL, out_url, args)

        f.close()

    def buildLanguageUnits(outdir, treasuredir):
        tag_treasure = os.path.join(treasuredir, "language-codes.json")
        templateURL = os.path.join("Templates", 'Sailor', "HTML", "Unit+Enum.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)

        # for name, code in data.items():
        description = "Language code for a specific language."
        cname = "Language"
        cases = list(
            map(lambda v: {
            "name": v[1],
            "alias": v[1],
            "description": f"language code for {v[0]}.",
            "values": [],
            "names": [],
            "hasAssociatedValue": False,
            "last": False
        }, data.items()))

        for case in cases:
            case["names"] = list(map(lambda v: {"value": v, "last": False}, case["names"]))
            if len(case["names"]) > 0:
                case["names"][-1]["last"] = True
            
            case["values"] = list(map(lambda v: {"value": v, "last": False}, case["values"]))
            
            if len(case["values"]) > 0:
                case["values"][-1]["last"] = True

        cases[-1]["last"] = True

        args = {
            "cname": cname,
            "cases": cases,
            "description": description
        }

        out_url = os.path.join(outdir, f"Unit+{cname}.swift")

        Utils.build(templateURL, out_url, args)

        f.close()

    def buildEvents():
        pass

    def buildEventResultMap():
        pass


    def buildCSSProperties(outdir, treasuredir):
        tag_treasure = os.path.join(treasuredir, "properties.json")
        # tag_global_props = os.path.join(treasuredir, "global-property-cases.json")

        templateURL = os.path.join("Templates", 'Sailor', "Styling", "Style+Property.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)

        completed = set()

        # fg = open(tag_global_props)
        # global_data = json.load(fg)

        args = {
            "properties": []
        }

        for name, body in data.items():
            name = name.split(":")[0]
            params = []

            if "*" in name:
                name = name[:-2]

                for label, body in body.items():
                    label = label.split(":")[0]
                    params.append((label, body))
            else:
                params = [("", body)]
            
            for param in params:
                # if param[0] != "":
                #     print(param[0])
                body = param[1]
                formatted_names = [SailorUtils.check_keyword_name(name) for name in body["names"]]
                is_param = param[0] != "" 
                is_shorthand = "shorthand" in body and body["shorthand"]
                shown_params = is_param or is_shorthand
                converted_types = [SailorUtils.convert_type(t) for t in body["types"]]
                if is_param:
                    full_name = name + "-" + param[0]
                    if "alias" in body:
                        full_name = body["alias"]
                else:
                    full_name = name

                # normal initializers
                if body["names"] != []:
                    args["properties"].append({
                        "name": full_name,
                        "shownParams": shown_params,
                        "isShorthand": is_shorthand,
                        "alias": SailorUtils.check_keyword_name(Utils.switch_to_camel(name)),
                        "typedNames": [ {"tname": tname, "type": tvalue, "last": False} for tname, tvalue in zip(formatted_names, converted_types) ],
                        "formatted": SailorUtils.put_formatted(body["format"], body["names"], formatted_names, body["types"]),
                        "description": body["description"]
                    })
                    
                    args["properties"][-1]["typedNames"][-1]["last"] = True

                # global params initializer
                if name not in completed:
                    #typeName = "globalValue" if param[0] == "" else param[0]
                    typeName = "globalValue"

                    completed.add(name)
                    args["properties"].append({
                        "name": name,
                        "shownParams": False, # shown_params
                        "isShorthand": False,
                        "alias": SailorUtils.check_keyword_name(Utils.switch_to_camel(name)),
                        "typedNames": [ {"tname": typeName, "type": "Unit.Global", "last": True } ],
                        "formatted": SailorUtils.put_formatted("{{" + typeName + "}}", [typeName]),
                        "description": body["description"]
                    })

        out_url = os.path.join(outdir, f"CSS+Properties.swift")

        Utils.build(templateURL, out_url, args)

        f.close()
        # fg.close()