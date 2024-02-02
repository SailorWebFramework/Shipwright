import click
import chevron
import os
import json

from .Utils import Utils

class Sailor:

    excluded_tags = ["style", "head", "body", "script", "main", "html"]
    attribute_alias = {
        "class": "className",
    }

    def build(outdir, treasuredir):
        # click.echo(f"{outdir} : {treasuredir}.")

        if not os.path.exists(treasuredir):
            click.echo(f"cannot generate build treasure does not exist at {treasuredir}.")
            return 

        click.echo(f"building sailor...")
        
        # build 
        htmlout = os.path.join(outdir, "Tags")
        Utils.checkAndCreate(htmlout)

        Sailor.buildTags(htmlout, treasuredir)

        unitsout = os.path.join(outdir, "Units")
        Utils.checkAndCreate(unitsout)

        Sailor.buildUnits(unitsout, treasuredir)

        Sailor.buildGlobalAttributeGroup(outdir, treasuredir)

        Sailor.buildCSSProperties()

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
                attributes = Sailor.formatAttributes(body["attributes"])

            if tag in Sailor.excluded_tags:
                continue

            args = {
                "ctag": tag.capitalize(),
                "tag": tag.lower(),
                "description": description,
                "attributes": attributes,
            }

            out_url = os.path.join(outdir, f"{args['ctag']}.swift")

            Utils.build(templateURL, out_url, args)

        f.close()

    def buildGlobalAttributeGroup(outdir, treasuredir):
        # TODO: Utils.templates, Utils.tags
        tag_treasure = os.path.join(treasuredir, "global-attributes.json")
        templateURL = os.path.join("Templates", "Sailor", "HTML", "GlobalAttributeGroup.mustache")
        
        f = open(tag_treasure)
        data = json.load(f)

        attributes = Sailor.formatAttributes(data)
        
        args = {
            "description": "Group of all global attributes, which are attributes that can be used with any HTML element.",
            "attributes": attributes,
        }

        out_url = os.path.join(outdir, "GlobalAttributeGroup.swift")
        Utils.build(templateURL, out_url, args)

    def buildUnits(outdir, treasuredir):
        pass

    def buildCSSProperties():
        pass
    
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
                Utils.switch_to_camel(
                    Utils.switch_to_camel(
                        name.replace("*", ""), 
                        "_"), 
                    "-"
                )
            )
        def parse_alias(name) -> str:
            name = parse_name(name)
            if name in Sailor.attribute_alias:
                return Sailor.attribute_alias[name]

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