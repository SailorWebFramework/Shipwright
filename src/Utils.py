
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

        out_dir = os.path.dirname(out_url)

        Utils.checkAndCreate(out_dir)

        of = open(out_url,"w")
        of.write(output)
        of.close()
    
    def createLastElementDictArray(data):
        for d in data:
            d["last"] = False
        
        if len(data) > 0:
            data[-1]["last"] = True
        return data

    def checkAndCreate(dir):
        # Check if the outdir directory exists
        if not os.path.exists(dir):
            # Create the directory
            os.makedirs(dir)

    # def switch_to_camel_dep(switch_str, char):
    #     components = switch_str.split(char)
    #     return components[0] + ''.join(x.title() for x in components[1:])

    def capitalize_keep_upper(s):
        return s[0].upper() + s[1:] if s else s
    
    def switch_to_camel(switch_str):
        chars = ["_", "-", "\\", "/"]
        output = switch_str
        for char in chars:
            components = output.split(char)
            start = components[0]
            if len(start) > 0:
                start = start[0].lower() + start[1:]
            output = start + ''.join(Utils.capitalize_keep_upper(x) for x in components[1:])
        return output
    


