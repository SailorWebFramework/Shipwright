import click
import chevron
import os

from .Utils import Utils

class Sailor:
    
    def build(outdir, treasuredir):
        # click.echo(f"{outdir} : {treasuredir}.")

        Utils.checkAndCreate(outdir)

        if not os.path.exists(treasuredir):
            click.echo(f"cannot generate build treasure does not exist at {treasuredir}.")
            return 

        click.echo(f"building sailor...")
        
        # build 
        Sailor.buildHTMLElements()

        Sailor.buildAttributes()

        Sailor.buildCSSProperties()

        return 
    
    def buildHTMLElements():
        pass

    def buildAttributes():
        pass

    def buildCSSProperties():
        pass