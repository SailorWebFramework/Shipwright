
import csv
import chevron
import os

class Utils:
    def build(template_url, out_url, data_args):

        template_fd = open(template_url, "r")
        template = template_fd.read()

        args = {
            'template': template,
            'data': data_args
        }

        output = chevron.render(**args)

        of = open(out_url,"w")
        of.write(output)
        of.close()

    def checkAndCreate(dir):
        # Check if the outdir directory exists
        if not os.path.exists(dir):
            # Create the directory
            os.makedirs(dir)
