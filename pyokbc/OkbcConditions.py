
import exceptions

class AbstractError(exceptions.Exception):
    def __init__(self,error_message='abstract error message',continuable=0):
        self.error_message = error_message
        self.continuable = continuable
        self.args = error_message

class CannotHandle(AbstractError):
    _name = "cannot-handle"
    mess = "tell cannot handle sentence: %s"
    def __init__(self,sentence):
        self.sentence = sentence
        AbstractError.__init__(self,self.mess % (sentence))

class CardinalityViolation(AbstractError):
    _name = "cardinality-violation"
    mess = "Cardinality violation '%s'"
    def __init__(self,constraint_violation):
        self.constraint_violation = constraint_violation
        AbstractError.__init__(self,self.mess % (constraint_violation))
        

class ClassNotFound(AbstractError):
    _name = "class-not-found"
    mess = "Class '%s' not found in kb '%s'"
    def __init__(self,missing_class,kb):
        self.missing_class = missing_class
        self.kb = kb
        AbstractError.__init__(self,self.mess % (missing_class,kb))

class ConstraintViolation(AbstractError):
    _name = "constraint-violation"
    mess = "Constraint '%s' violated on frame '%s' on '%s' slot '%s' " +\
           "facet '%s' in kb '%s'"
    def __init__(self,constraint,frame,slot,slot_type,facet,kb):
        self.constraint = constraint
        self.frame = frame
        self.slot = slot
        self.slot_type = slot_type
        self.facet = facet
        self.kb = kb
        AbstractError.__init__(self,self.mess % (constraint,frame,slot_type,slot,
                                       facet,kb))

class DomainRequired(AbstractError):
    _name = "domain-required"
    mess = "Domain required for frame '%s' slot '%s' facet '%s' in kb '%s'"
    def __init__(self,frame,slot,facet,kb):
        self.frame = frame
        self.slot = slot
        self.facet = facet
        self.kb = kb
        AbstractError.__init__(self,self.mess % (frame,slot,facet,kb))

class EnumeratorExhausted(AbstractError):
    _name = "enumerator-exhausted"
    mess = "Enumerator '%s' exhausted"
    def __init__(self,enumerator):
        self.enumerator = enumerator
        AbstractError.__init__(self,self.mess % (enumerator))

class FacetAlreadyExists(AbstractError):
    _name = "facet-already-exists"
    mess = "Facet '%s' already exists in kb '%s'"
    def __init__(self,facet,kb):
        self.facet = facet
        self.kb = kb
        AbstractError.__init__(self,self.mess % (facet,kb))

class FacetNotFound(AbstractError):
    _name = "facet-not-found"
    mess = "Facet '%s' not found on '%s' slot '%s' on frame '%s'" + \
           " in kb '%s'"
    def __init__(self,frame,slot,slot_type,facet,kb):
        self.frame = frame
        self.slot = slot
        self.slot_type = slot_type
        self.facet = facet
        self.kb = kb
        AbstractError.__init__(self,self.mess % (facet,slot_type,slot,frame,kb))

class FrameAlreadyExists(AbstractError):
    _name = "frame-already-exists"
    mess = "Frame'%s' already exists in kb '%s'"
    def __init__(self,frame,kb):
        self.frame = frame
        self.kb = kb
        AbstractError.__init__(self,self.mess % (frame,kb))

class GenericError(AbstractError):
    _name = "generic-error"
    def __init__(self,error='Unspecified GenericError'):
        AbstractError.__init__(self,error)

class IllegalBehaviourValues(AbstractError):
    _name = "illegal-behaviour-values"
    mess = "For behaviour '%s' illegal proposed values '%s'"
    def __init__(self,behavior,proposed_values):
        self.behaviour = behaviour
        self.proposed_values = proposed_values
        AbstractError.__init__(self,self.mess % (behaviour,proposed_values))

class IndividualNotFound(AbstractError):
    _name = "individual-not-found"
    mess = "Individual '%s' not found in kb '%s'"
    def __init__(self,missing_individual,kb):
        self.missing_individual = missing_individual
        self.kb = kb
        AbstractError.__init__(self,self.mess % (missing_individual,kb))

class KbNotFound(AbstractError):
    _name = "kb-not-found"
    mess = "Kb '%s' not found at '%s'"
    def __init__(self,kb,fname):
        self.kb = kb
        AbstractError.__init__(self,self.mess % (kb,fname))

class KbValueReadError(AbstractError):
    _name = "kb-value-read-error"
    mess = "Error reading kb '%s' from string '%s'"
    def __init__(self,read_string,kb):
        self.read_string = read_string
        self.kb = kb
        AbstractError.__init__(self,self.mess % (kb,read_string))

class MethodMissing(AbstractError):
    _name = "method-missing"
    mess = "Method '%s' missing on kb '%s'"
    def __init__(self,okbcop,kb):
        AbstractError.__init__(self,self.mess % (okbcop,kb))

class MissingFrames(AbstractError):
    _name = "missing-frames"
    mess = "While copying frame '%s' from kb '%s' missing frames '%s'"
    def __init__(self,missing_frames,frame,kb):
        self.missing_frames = missing_frames
        self.frame = frame
        self.kb = kb
        AbstractError.__init__(self,self.mess % (frame,kb,missing_frames))

class NetworkConnectionError(AbstractError):
    _name = "network-connection-error"
    mess = "Network connection error connecting to host '%s' and port '%s'"
    def __init__(self,host,port):
        self.host = host
        self.port = port
        AbstractError.__init__(self,self.mess % (host,port))

class NotAFrameType(AbstractError):
    _name = "not-a-frame-type"
    mess = "'%s' is not a frame-type in kb '%'"
    def __init__(self,frame_type,kb):
        self.frame_type = frame_type
        self.kb = kb
        AbstractError.__init__(self,self.mess % (frame_type,kb))

class NotCoercibleToFrame(AbstractError):
    _name = "not-coercible-to-frame"
    mess = "Cannot coerce '%s' to a frame in kb '%'"
    def __init__(self,frame,kb):
        self.frame = frame
        self.kb = kb
        AbstractError.__init__(self,self.mess % (frame,kb))

class NotUniqueError(AbstractError):
    _name = "not-unique-error"
    mess = "Match on pattern '%s' matches '%s' in context '%s' in kb '%s'"
    def __init__(self,pattern,matches,contenxt,kb):
        self.pattern = pattern
        self.matches = matches
        self.context = context
        self.kb = kb
        AbstractError.__init__(self,self.mess % (pattern,matches,context,kb))

class ObjectFreed(AbstractError):
    _name = "object-free"
    mess = "Object '%s' already freed"
    def __init__(self,object):
        self.object = object
        AbstractError.__init__(self,self.mess % (object))

class ReadOnlyViolation(AbstractError):
    _name = "read-only-violation"
    mess = "Write operation attempted on read-only kb '%s'"
    def __init__(self,kb):
        self.kb = kb
        AbstractError.__init__(self,self.mess % (kb))

class SlotAlreadyExists(AbstractError):
    _name = "slot-already-exists"
    mess = "Slot '%s' already exists in kb '%s'"
    def __init__(self,slot,kb):
        self.slot = slot
        self.kb = kb
        AbstractError.__init__(self,self.mess % (slot,kb))

class SlotNotFound(AbstractError):
    _name = "slot-not-found"
    mess = "'%s' slot '%s' not found on frame '%s' in kb '%s'"    
    def __init__(self,frame,slot,slot_type,kb):
        self.frame = frame
        self.slot = slot
        self.slot_type = slot_type
        self.kb = kb
        AbstractError.__init__(self,self.mess % (slot_type,slot,frame,kb))

class SyntaxError(AbstractError):
    _name = "syntax-error"
    mess = "Syntax error in '%s'"
    def __init__(self, erring_input):
        self.erring_input = erring_input
        AbstractError.__init__(self,self.mess % (erring_input))

class ValueTypeViolation(AbstractError):
    _name = "value-type-violation"
    mess = "Value type violation '%s'"
    def __init__(self, constraint_violation):
        self.constraint_violation = constraint_violation
        AbstractError.__init__(self,self.mess % (constraint_violation))
