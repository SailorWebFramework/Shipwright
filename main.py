import csv
import chevron
import os

#TODO: removed style and main tags
#TODO: SUPPORT COLOR NAMES

data_path = os.path.join('.', 'Data')

tags_url = os.path.join(data_path, 'tags.csv')
attributes_url =  os.path.join(data_path, 'attributes.csv')
templates_url = os.path.join('.', 'Templates')
tag_template_url = os.path.join(templates_url, 'HTMLTag.mustache')

out_dir = os.path.join('..', 'Sailor', 'Sources', 'Generated')
tag_out_dir = os.path.join('..', 'Sailor', 'Sources', 'Generated', 'Tags')

# Generate Tags
with open(tags_url, newline='') as csvfile:
    reader = csv.reader(csvfile)

    # skip titles in csv
    next(reader)

    template_fd = open(tag_template_url, "r")
    template = template_fd.read()

    for row in reader:
        tagname = row[0]
        ctagname = tagname.capitalize()
        type = row[1].strip() == "DEFAULT"

        args = {
            'template': template,
            'data': {
                'tag': tagname, 
                'ctag': ctagname,
                'type': type
            }
        }

        output = chevron.render(**args)

        genfile_out = os.path.join(tag_out_dir, ctagname + ".swift")
        of = open(genfile_out,"w")
        of.write(output)
        of.close()

# TODO: make Lang attribute integrated not string
# Generate Attributes
# with open(attributes_url, newline='') as csvfile:
#     reader = csv.reader(csvfile)

#     # skip titles in csv
#     next(reader)

    # template_fd = open(tag_template_url, "r")
    # template = template_fd.read()

    # for row in reader:
    #     tagname = row[0]
    #     ctagname = tagname.capitalize()
    #     type = row[1].strip() == "DEFAULT"

    #     args = {
    #         'template': template,
    #         'data': {
    #             'tag': tagname, 
    #             'ctag': ctagname,
    #             'type': type
    #         }
    #     }

    #     output = chevron.render(**args)

    #     genfile_out = os.path.join(tag_out_dir, ctagname + ".swift")
    #     of = open(genfile_out,"w")
    #     of.write(output)
    #     of.close()
