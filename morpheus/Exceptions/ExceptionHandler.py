import skillbridge


class MorpheusExceptionHandler():
    def __init__(self) -> None:
        pass
    def getTraceBack(tb):
        if(tb.tb_next):
            return MorpheusExceptionHandler.getTraceBack(tb.tb_next)
        else:
            return tb
    def getTBClass(tb):
        return tb.tb_frame.f_locals.get("cls")
    def catch(self,e):
        #check if note starts with MORPHEUS
        tb = MorpheusExceptionHandler.getTraceBack(e.__traceback__)
        cls = MorpheusExceptionHandler.getTBClass(tb)
        if(cls == skillbridge.client.workspace.Workspace):
            print("IT SKILL ISSUES")
        #elif()
        return str(e)
        pass
    def bridge(self):

        pass