
from string import Formatter

import _string

class morpheus_dict(dict):
    def append_2(key,item):

        if key not in self: #no key
            self.equationDict.setdefault(pin.type, []) #initialize array
        self[key].append(item)
    def format():
        pass

class moprheus_Formatter:
    def format(self, format_string, /, *args, **kwargs):
        return self.vformat(format_string, args, kwargs,returnlist=True)

    def vformat(self, format_string, args, kwargs,returnlist = False):
        used_args = set()
        result, _ = self._vformat(format_string, args, kwargs, used_args, 2,returnlist=returnlist)
        self.check_unused_args(used_args, args, kwargs)
        return result

    def _vformat(self, format_string, args, kwargs, used_args, recursion_depth,
                 auto_arg_index=0,returnlist=False):
        if recursion_depth < 0:
            raise ValueError('Max string recursion exceeded')
        result = []
        results= [[]]
        total_fields = []
        for literal_text, field_name, format_spec, conversion in \
                self.parse(format_string):

            # output the literal text
            if literal_text:
                result.append(literal_text)
                self.appendToAll(results,literal_text,None)

            # if there's a field, output it
            if field_name is not None:
                # this is some markup, find the object and do
                #  the formatting
                total_fields.append(field_name)
                # handle arg indexing when empty field_names are given.
                if field_name == '':
                    if auto_arg_index is False:
                        raise ValueError('cannot switch from manual field '
                                         'specification to automatic field '
                                         'numbering')
                    field_name = str(auto_arg_index)
                    auto_arg_index += 1
                elif field_name.isdigit():
                    if auto_arg_index:
                        raise ValueError('cannot switch from manual field '
                                         'specification to automatic field '
                                         'numbering')
                    # disable auto arg incrementing, if it gets
                    # used later on, then an exception will be raised
                    auto_arg_index = False

                # given the field_name, find the object it references
                #  and the argument it came from
                obj, arg_used = self.get_field(field_name, args, kwargs)
                used_args.add(arg_used)

                # do any conversion on the resulting object
                obj = self.convert_field(obj, conversion)

                # expand the format spec, if needed
                format_spec, auto_arg_index = self._vformat(
                    format_spec, args, kwargs,
                    used_args, recursion_depth-1,
                    auto_arg_index=auto_arg_index)

                # format the object and append to the result
                result.append(self.format_field(obj, format_spec))
                results = self.appendToAll(results,obj,format_spec)
        resultsbuffer = results
        results = []
        for result in resultsbuffer:
            results.append(''.join(result))
        if returnlist:
            return [results,total_fields],auto_arg_index#''.join(result), auto_arg_index
        else:
            return ''.join(result), auto_arg_index
    def appendToAll(self,results,thingtoappend,format_spec):
        if(type(thingtoappend) is list):
            results_before = results.copy()
            results = []
            for appendThing in thingtoappend:
                for result in results_before:
                    text = self.format_field(appendThing, format_spec)
                    cur_result = result.copy()
                    cur_result.append(text)
                    results.append(cur_result)
        else:

            for result in results:
                result.append(thingtoappend)
        return results


    def get_value(self, key, args, kwargs):
        if isinstance(key, int):
            return args[key]
        else:
            return kwargs[key]


    def check_unused_args(self, used_args, args, kwargs):
        pass


    def format_field(self, value, format_spec):
        return format(value, format_spec)


    def convert_field(self, value, conversion):
        # do any conversion on the resulting object
        if conversion is None:
            return value
        elif conversion == 's':
            return str(value)
        elif conversion == 'r':
            return repr(value)
        elif conversion == 'a':
            return ascii(value)
        raise ValueError("Unknown conversion specifier {0!s}".format(conversion))


    # returns an iterable that contains tuples of the form:
    # (literal_text, field_name, format_spec, conversion)
    # literal_text can be zero length
    # field_name can be None, in which case there's no
    #  object to format and output
    # if field_name is not None, it is looked up, formatted
    #  with format_spec and conversion and then used
    def parse(self, format_string):
        return _string.formatter_parser(format_string)


    # given a field_name, find the object it references.
    #  field_name:   the field being looked up, e.g. "0.name"
    #                 or "lookup[3]"
    #  used_args:    a set of which args have been used
    #  args, kwargs: as passed in to vformat
    def get_field(self, field_name, args, kwargs):
        first, rest = _string.formatter_field_name_split(field_name)

        obj = self.get_value(first, args, kwargs)

        # loop through the rest of the field_name, doing
        #  getattr or getitem as needed
        for is_attr, i in rest:
            if is_attr:
                try:
                    obj = getattr(obj, i)
                except AttributeError:
                    obj = obj.global_dict[i]
            else:
                obj = obj[i]
        return obj, first
