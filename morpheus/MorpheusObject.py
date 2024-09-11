
properties_to_remove =[
    "ws"#, "session", "asi_session", #change based on cadence session
    #"global_dict","cv","global_dict","local_dict",
    #"equationDict", #TODO REMOVE not needed anymore
    #"config", #TDOD remove not needed anymore
    #"tests" #TODO TEMP
]
from skillbridge import RemoteObject
class morpheusObject:

    def __getstate__(self):
        state = self.__dict__.copy()
        local_properties_to_remove = list()
        for prop in state:
            if(type(state[prop]) == RemoteObject):
                local_properties_to_remove.append(prop)

        for prop in local_properties_to_remove:
            if(prop in state):
                del state[prop]

        for prop in properties_to_remove:
            if(prop in state):
                del state[prop]
        state =  morpheusObject.recursiveGetState( state)

        #morpheusObject.recursiveGetState(state)
        # for prop in state:
        #     if hasattr(prop,"__getstate_"):
        #         prop.__getstate__()

        return state
    def recursiveGetState(object_to_get_state):
        state =object_to_get_state
        local_properties_to_remove = list()
        #if(hasattr(object_to_get_state,'lib')):
       #         print("hello")
        if hasattr(object_to_get_state, '__iter__'):
            if(type(object_to_get_state) == dict):
                for subObject in object_to_get_state:
                    if(type(state[subObject]) == RemoteObject):
                        local_properties_to_remove.append(subObject)
                    state[subObject] = morpheusObject.recursiveGetState( object_to_get_state[subObject])
                for prop in local_properties_to_remove:
                    if(prop in state):
                        del state[prop]
                
            elif(type(object_to_get_state) == list):
                state = list()
                for subObject in object_to_get_state:
                    if(type(subObject) == RemoteObject):
                        local_properties_to_remove.append(subObject)
                    elif(subObject !=object_to_get_state ):
                        state.append(morpheusObject.recursiveGetState(subObject))
                #for prop in local_properties_to_remove:
                #    state.remove()
        elif hasattr(object_to_get_state,"__getstate__"):
            if(type(object_to_get_state) is bool):
                pass
            else:
                state = object_to_get_state.__getstate__()
                if(state == None):
                    state =object_to_get_state
        return state
    def save(self):
        with open('savetesting_test0.yml', 'w') as yaml_file:
            yaml.dump(self, yaml_file, default_flow_style=False)
        pass


