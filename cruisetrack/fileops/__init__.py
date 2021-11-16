
def fprintf_copy(stream, format_spec, *args):
    stream.write(format_spec % args)
