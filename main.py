import csv
import chevron
import os
import click

from src import Sailor

path = os.path

@click.group()
@click.version_option("0.1.0", prog_name="shipwright")
def shipwright():
    pass

@shipwright.command()
@click.argument("target")
@click.option('--outdir', default=path.join(os.getcwd(), "Generated"), help='Selects where to output the build.')
@click.option('--treasuredir', default=path.join(os.getcwd(), "Treasure"), help='Selects where the input files are.')
def build(target, outdir, treasuredir):

    # build(template_url, out_url, data_args)
    if target == "sailor":
        Sailor.build(outdir, treasuredir)
        return
    
    click.echo(f"target not found.")

if __name__ == "__main__":
    shipwright()

# data_path = os.path.join('.', 'Data')

# tags_url = os.path.join(data_path, 'tags.csv')
# attributes_url =  os.path.join(data_path, 'attributes.csv')
# events_url =  os.path.join(data_path, 'events.csv')
# css_props_url = os.path.join(data_path, 'css_properties.csv')

# templates_url = os.path.join('.', 'Templates')
# page_template_url = os.path.join(templates_url, 'Page.mustache')
# page_events_template_url = os.path.join(templates_url, 'Page+Events.mustache')
# tag_template_url = os.path.join(templates_url, 'HTMLTag.mustache')
# events_mustache_url =  os.path.join(templates_url, 'Events.mustache')
# css_props_template_url = os.path.join(templates_url, 'Properties.mustache')

# out_dir = os.path.join('..', 'Sailor', 'Sailboat', 'Sources', 'Generated')
# tag_out_dir = os.path.join(out_dir, 'Tags')
# page_out_dir = os.path.join(out_dir, 'Page')
# events_out_dir = os.path.join(out_dir, 'Events')
# css_props_out_dir = os.path.join(out_dir, 'Properties')

# # https://www.w3schools.com/tags/default.asp
# # Generate Tags
# with open(tags_url, newline='') as csvfile:
#     reader = csv.reader(csvfile)

#     # skip titles in csv
#     next(reader)

#     template_fd = open(tag_template_url, "r")
#     template = template_fd.read()

#     for row in reader:
#         tagname = row[0]
#         ctagname = tagname.capitalize()
#         type = row[1].strip() == "DEFAULT"

#         args = {
#             'template': template,
#             'data': {
#                 'tag': tagname, 
#                 'ctag': ctagname,
#                 'type': type
#             }
#         }

#         output = chevron.render(**args)

#         genfile_out = os.path.join(tag_out_dir, ctagname + ".swift")
#         of = open(genfile_out,"w")
#         of.write(output)
#         of.close()



# # https://www.w3schools.com/jsref/dom_obj_event.asp
# # Generate Events
# with open(events_url, newline='') as csvfile:
#     reader = csv.reader(csvfile)

#     # skip titles in csv
#     next(reader)

#     template_fd = open(events_mustache_url, "r")
#     template = template_fd.read()

#     events = []

#     for row in reader:
#         name = row[0].strip()
#         typedreturn = row[1].strip()
#         returnvalue = row[2].strip()

#         ctype = typedreturn

#         if ctype == 'object':
#             ctype = "JSObject"

#         events.append({
#             'name': name, 
#             'lname': name.lower(),
#             'ctype': ctype,
#             'ltype': typedreturn.lower(),
#             'evalue': returnvalue,
#             'istyped': returnvalue != 'none' and typedreturn != 'none'
#         })

#         args = {
#             'template': template,
#             'data': events[-1]
#         }

#         output = chevron.render(**args)

#         genfile_out = os.path.join(events_out_dir, "Page+" + "on"+ name + ".swift")
#         of = open(genfile_out,"w")
#         of.write(output)
#         of.close()
    
#     #TODO: add? write to Page.swift
#     # template_fd = open(page_template_url, "r")
#     # template = template_fd.read()

#     # args = {
#     #     'template': template,
#     #     'data': {
#     #         "events": events
#     #     }
#     # }

#     # output = chevron.render(**args)
    
#     # genfile_out = os.path.join(page_out_dir, "InternalGeneratedPage.swift")

#     # of = open(genfile_out,"w")
#     # of.write(output)
#     # of.close()

#     # template_fd = open(page_events_template_url, "r")
#     # template = template_fd.read()

#     # args = {
#     #     'template': template,
#     #     'data': {
#     #         "events": events
#     #     }
#     # }

#     # output = chevron.render(**args)
#     # genfile_out = os.path.join(page_out_dir, "Page+Events.swift")

#     # of = open(genfile_out,"w")
#     # of.write(output)
#     # of.close()


# # https://www.w3schools.com/jsref/dom_obj_event.asp
# # Generate Properties
# with open(css_props_url, newline='') as csvfile:
#     reader = csv.reader(csvfile)

#     # skip titles in csv
#     next(reader)

#     template_fd = open(css_props_template_url, "r")
#     template = template_fd.read()

#     events = []

#     for row in reader:
#         fname = row[0].strip()
#         name = row[1].strip()
#         unit = row[2].strip()

#         events.append({
#             'fname': fname, 
#             'cfname': fname.capitalize(),
#             'name': name,
#             'unit': unit
#         })
        
#         args = {
#             'template': template,
#             'data': events[-1]
#         }

#         output = chevron.render(**args)

#         genfile_out = os.path.join(css_props_out_dir, "Style.Property+" + fname + ".swift")
#         of = open(genfile_out,"w")
#         of.write(output)
#         of.close()
    
#     # #write to Page.swift
#     # template_fd = open(page_template_url, "r")
#     # template = template_fd.read()

#     # args = {
#     #     'template': template,
#     #     'data': {
#     #         "events": events
#     #     }
#     # }

#     # output = chevron.render(**args)
    
#     # genfile_out = os.path.join(page_out_dir, "Page.swift")

#     # of = open(genfile_out,"w")
#     # of.write(output)
#     # of.close()

# # TODO: make Lang attribute integrated not string
# # Generate Attributes
# # with open(attributes_url, newline='') as csvfile:
# #     reader = csv.reader(csvfile)

# #     # skip titles in csv
# #     next(reader)

#     # template_fd = open(tag_template_url, "r")
#     # template = template_fd.read()

#     # for row in reader:
#     #     tagname = row[0]
#     #     ctagname = tagname.capitalize()
#     #     type = row[1].strip() == "DEFAULT"

#     #     args = {
#     #         'template': template,
#     #         'data': {
#     #             'tag': tagname, 
#     #             'ctag': ctagname,
#     #             'type': type
#     #         }
#     #     }

#     #     output = chevron.render(**args)

#     #     genfile_out = os.path.join(tag_out_dir, ctagname + ".swift")
#     #     of = open(genfile_out,"w")
#     #     of.write(output)
#     #     of.close()
