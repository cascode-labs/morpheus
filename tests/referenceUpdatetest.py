#https://stackoverflow.com/questions/986006/how-do-i-pass-a-variable-by-reference

# class object_to_update:
#     def __init__(self):
#         self.value = "NOT UPDATED"
#         pass

# class gui_element:
#     def __init__(self,value):
#         value = "UPDATED"
#         pass
#     def betterUpdate(self,obj_updatable):
#         obj_updatable.value = "UPDATED"
#     def lists_are_cool(self,value_updateable_list):
#         value_updateable_list[0] = "UPDATED"
# test_obj = object_to_update()

# print(f"first we start with {test_obj.value}")
# gui = gui_element(test_obj.value)

# print(f"then we try updating to {test_obj.value}")

# gui.betterUpdate(test_obj)
# print(f"but if we try updating to {test_obj.value}")


# test_obj = object_to_update()

# print(f"first we start with {test_obj.value}")
# gui.lists_are_cool([test_obj.value])
# print(f"then we try updating to {test_obj.value}")

dict_gloabl = {
"TEST": "HELLO",
"TEST2": "GOODBYE!"
}

dict_temp = dict_gloabl
print(dict_gloabl["TEST"])
dict_temp["TEST"] = "WORLD!"
print(dict_gloabl["TEST"])