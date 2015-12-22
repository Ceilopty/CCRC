LOG_ON = 0

_open = open

def track(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args,**kwargs):
        result = func(*args,**kwargs)
        _log("%s%s->\n%s"%(func.__qualname__,str((args,kwargs))[:200],str(result)[:100]))
        return result
    return wrapper

def last():
    from traceback import format_exc
    _log(format_exc())

def pt():
    from threading import current_thread
    from multiprocessing import current_process
    p,t = current_process(),current_thread()
    info = "%s:%s %s:%s"%(p.name,p.ident,t.name,t.ident)
    return info

def open():
    
    from time import asctime, gmtime
    with _open("debug.log", "a+", encoding="utf-8") as f:
        f.write("%s START\t%s\n"%(asctime(gmtime()),pt()))
def close():
    from time import asctime, gmtime
    with _open("debug.log", "a+", encoding="utf-8") as f:
        f.write("%s END\n"%asctime(gmtime()))

def _log(string):
    from time import asctime, gmtime
    with _open("debug.log", "a+", encoding="utf-8") as f:
        f.write("%s\t%s\n\t%s\n\n"%(asctime(gmtime()),pt(),"\n\t".join(string.splitlines())))

def log(*args, **kwargs):
    from types import FunctionType
    from time import asctime, gmtime
    from functools import wraps
    from traceback import format_exc
    if LOG_ON:
        print(asctime(gmtime()), *args, **kwargs)
        try:_log('\n'.join(map(str,args)))
        except:pass
    if len(args) is 1 and type(args[0]) is FunctionType:
        func = args[0]
        print("Function %s will be logged"%func.__qualname__)
        @wraps(func)
        def wrapper(*ar,**kw):
            try: result = func(*ar,**kw)
            except:
                info = "%s\n\t%s\n\n"%(asctime(gmtime()),"\n\t".join(format_exc().splitlines()))
                with _open("debug.log", "a+", encoding="utf-8") as f:
                    f.write(info[:500])
                print(info)
            else: return result
        return wrapper
        
        
    
