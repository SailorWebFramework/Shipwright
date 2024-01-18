import click
import chevron
import os
import json

from .Utils import Utils

class Sailor:

    excluded_tags = ["style", "head", "body", "script"]
    
    def build(outdir, treasuredir):
        # click.echo(f"{outdir} : {treasuredir}.")

        Utils.checkAndCreate(outdir)

        if not os.path.exists(treasuredir):
            click.echo(f"cannot generate build treasure does not exist at {treasuredir}.")
            return 

        click.echo(f"building sailor...")
        
        # build 
        htmlout = os.path.join(outdir, "HTML")
        htmltresure = os.path.join(treasuredir, "htmlReference.json")
        Sailor.buildHTMLElements(htmlout, htmltresure)

        Sailor.buildAttributes()

        Sailor.buildCSSProperties()

        return 
    
    def buildHTMLElements(outdir, htmlTreasure):
        # TODO: Utils.templates
        templateURL = os.path.join("Templates", 'Sailor', "HTML", "Tag.mustache")
        
        f = open(htmlTreasure)
        data = json.load(f)

        for tag, body in data.items():
            # TODO: change when more fields are added
            description = body

            #TODO: format tag in treasure, not here
            chars_to_strip = ["<", ">", " ", "\n"]

            tag = tag.lower()
            for char in chars_to_strip:
                tag = tag.replace(char, "")

            for tag in tag.split(","):
                if tag in Sailor.excluded_tags:
                    continue

                args = {
                    "ctag": tag.capitalize(),
                    "tag": tag.lower(),
                    "description": description
                }

                out_url = os.path.join(outdir, f"{args['ctag']}.swift")

                Utils.build(templateURL, out_url, args)

        f.close()

    def buildAttributes():
        pass

    def buildCSSProperties():
        pass