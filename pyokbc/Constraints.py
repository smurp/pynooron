
from PyOkbc import *

class Constrainable:
    def enforce_slot_constraints(kb, frame, slot,
                                 current_values=[], future_values = [],
                                 inference_level=None,slot_type=None,
                                 value_selector=None,kb_local_only_p=None):
            
        # FIXME should do facets too
        future_values = kb.check_assertion_of_constraint_slot_values(frame,
                                                                     slot,
                                                                     current_values,
                                                                     future_values,
                                                                     inference_level,
                                                                     slot_type,
                                                                     value_selector,
                                                                     kb_local_only_p)
        
        return future_values

        
    def check_assertion_of_constraint_slot_values(kb, frame, slot,
                                                  current_values=[],
                                                  future_values = [],
                                                  inference_level=None,
                                                  slot_type=None,
                                                  value_selector=None,
                                                  kb_local_only_p=None):
        #for zlot in Node._standard_slots:
        #    print zlot
        return future_values
