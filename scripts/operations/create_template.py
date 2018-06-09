import sys
def run(context):
    template_name = sys.argv[3]
    context.create_template(template_name)
