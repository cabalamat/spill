# decspill.py = decorators for spill

import spilltypes

GL_PRINTARGS_DEPTH = 0
GL_PRINTARGS_INDENT = ": "

def printargs(fn):
    def wrapper(*args, **kwargs):
        global GL_PRINTARGS_DEPTH
        argStr = ", ".join([repr(a) for a in args])
        kwargStr = ", ".join(["%s=%r"%(k,v) for v,k in enumerate(kwargs)])
        comma = ""
        if argStr and kwargStr: comma = ", "
        akStr = argStr + comma + kwargStr
        print '%s%s(%s)' % (GL_PRINTARGS_INDENT * GL_PRINTARGS_DEPTH,
           fn.__name__, akStr)
        GL_PRINTARGS_DEPTH += 1
        retVal = fn(*args, **kwargs)
        GL_PRINTARGS_DEPTH -= 1
        if retVal != None:
            print "%s%s(%s) => %r" % (GL_PRINTARGS_INDENT * GL_PRINTARGS_DEPTH,
               fn.__name__, akStr,
               retVal)
        return retVal
    return wrapper

#special version for the eval function

GL_EVALARGS_DEPTH = 0
GL_EVALARGS_INDENT =   "> "
GL_EVALARGS_INDENT_R = "  "

def evalargs(fn):
    def wrapper(*args):
        global GL_EVALARGS_DEPTH

        akStr = spilltypes.show(args[0])
        print '%s%s %s' % (GL_EVALARGS_INDENT * GL_EVALARGS_DEPTH,
           fn.__name__, akStr)
        GL_EVALARGS_DEPTH += 1
        retVal = fn(*args)
        GL_EVALARGS_DEPTH -= 1
        if retVal != None:
            print "%s%s %s => %r" % (GL_EVALARGS_INDENT_R * GL_EVALARGS_DEPTH,
               fn.__name__, akStr,
               retVal)
        return retVal
    return wrapper

#end
