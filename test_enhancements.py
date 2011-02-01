
def set_of_strings(a_list):
    """Turn an interable into a set of the contents converted to strings."""
    return set(map(str,list(a_list)))


class TestEnhancements:
    def perform_comparison(self,expect=None,got=None,contains=None,msg=""):
        """
        eg:
        self.perform_comparison(
            msg    = "get_kb_direct_parents() not working, first see test_0008",
            expect = set(['PeopleSchema', 'LiteratureOntology']),
            got    = set_of_strings(find_kb('PeopleData').get_kb_direct_parents()))
        

        BOILERPLATE:
        self.perform_comparison(
            msg    = "",
            expect = set(),
            got    = set())

        """
        #msg += "\n  expected: %(expect)s\n   but got: %(got)s"
        if type(contains) == set:
            missing = contains.difference(got)
            a = missing
            b = set([])
        if type(expect) == set and type(got) == set:
            missing = expect.difference(got) or None
            extra   = got.difference(expect) or None
            a = expect
            b = got
        else:
            a = expect
            b = got
        for variable in 'expect contains got missing extra'.split():
            if locals().get(variable) <> None:
                var_val = locals()[variable]
                msg += "\n %(variable)13s: %(var_val)s" % locals()
        self.assertEquals(a,b,msg % locals())
