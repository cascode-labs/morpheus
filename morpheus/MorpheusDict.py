


from morpheus.Formatter import moprheus_Formatter

class morpheusDict(dict):
    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            try:
                return super().__getitem__("global_dict").__getitem__
            except KeyError:
                return "{" + str(item) + "}"
        # end try
    # end def
# end class
    def formatObjStrings(self, obj):
        results = [obj.copy()]
        total_fields = []
        for key,value in obj.__dict__.items():
            if type(value) is str:
                #obj.__dict__[key] = self.formatString(value)
                
                formatter = moprheus_Formatter()
                [formatted_text , fields] = formatter.format( value,**self)
                if fields in total_fields:
                    for result in results:
                        results.__dict__[key]

    def formatString(self,text):

        formatter = moprheus_Formatter()
        #expression = formatter.format(equation.equation,**tempDict) 

        strings = list()
        string_split = text.split(".")
        dictionary_definition = self.copy()
        [formatted_text , fields] = formatter.format( text,**self)
        # for string in string_split:
        #     if(type(dictionary_definition) is morpheusDict or type(dictionary_definition) is dict):
        #         dictionary_definition = dictionary_definition[string]
        #     else:
        #         dictionary_definition = morpheusDict(dictionary_definition.__dict__)[string]
        #formatted_text = "temp"#text.format(**tempDict) 
        #strings.append(formatted_text)
        return formatted_text