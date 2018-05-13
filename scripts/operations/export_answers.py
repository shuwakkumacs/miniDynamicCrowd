
def run(context):
        context.export_answers(lambda ans,task: print("{} - {}".format(ans,task)))
