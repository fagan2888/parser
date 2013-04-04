# from utils import error_msg, id_wrapper, \
#     isunknown, ispositive, isnegative, \
#     isaff, iscvx, isccv, ismatrix, isscalar, isvector   
from sign import Sign
from vexity import Vexity

class Expression(object):
    """
    A convex optimization expression.
    Records sign, vexity, string representation, and component expressions.
    The component expressions can be used to reconstruct the parse tree.

    Priority is the order of operations priority of the binary operation that
    created the expression (if any). It is used to reconstruct parentheses.
    """
    
    def __init__(self, vexity, sign, name, subexpressions, priority = -1):
        self.vexity = vexity
        self.sign = sign
        self.name = name
        self.subexpressions = subexpressions
        self.priority = priority
    
    def __add__(self, other):
        return Expression(self.vexity + other.vexity,
                          self.sign + other.sign,
                          str(self) + ' + ' + str(other), 
                          [self,other])
    
    def __sub__(self, other):
        return Expression(self.vexity - other.vexity,
                          self.sign - other.sign,
                          str(self) + ' - ' + str(other), 
                          [self,other])

    def __mul__(self, other):
        sign = self.sign * other.sign
        vexity = self.vexity * other.vexity
        exp = Expression(vexity, sign, str(self) + ' * ' + str(other), [self,other])
        exp.sign_by_vexity()
        return exp

    def __div__(self, other):
        sign = self.sign / other.sign
        vexity = self.vexity / other.vexity
        exp = Expression(vexity, sign, str(self) + ' / ' + str(other), [self,other])
        exp.sign_by_vexity()
        return exp

    # Adjust vexity based on sign of subexpressions.
    # Used for multiplication and division.
    # Only constant expressions can change the vexity,
    # e.g. negative constant * convex == concave
    # For multiplication by non-constants, the vexity
    # is always nonconvex.
    def sign_by_vexity(self):
        for i in range(2):
            vexity = self.subexpressions[i].vexity
            sign = self.subexpressions[i].sign
            if vexity == Vexity(Vexity.CONSTANT_KEY):
                self.vexity = self.vexity.sign_mult(sign)
        
    def __neg__(self):
        return Expression(-self.vexity,
                          -self.sign,
                          '-' + str(self), 
                          [self])
    
    # def __le__(self,other):
    #     if iscvx(self) and isccv(other):
    #         return LeqConstraint(self,other)
    #     else:
    #         raise Exception("Cannot have '%s <= %s'" % (self.vexity_names[self.vexity], other.vexity_names[self.vexity]))
    
    # def __ge__(self,other):
    #     if isccv(self) and iscvx(other):
    #         return GeqConstraint(self,other)
    #     else:
    #         raise Exception("Cannot have '%s >= %s'" % (self.vexity_names[self.vexity], other.vexity_names[self.vexity]))
    
    # def __eq__(self,other):
    #     if isaff(self) and isaff(other):
    #         return EqConstraint(self,other)
    #     else:
    #         raise Exception("Cannot have '%s == %s'" % (self.vexity_names[self.vexity], other.vexity_names[self.vexity]))
            
    def __lt__(self, other): return NotImplemented
    def __gt__(self, other): return NotImplemented
    def __ne__(self, other): return NotImplemented
    
    def __repr__(self):
        """Representation in Python"""
        return "Expression(%s, %s, %s, %s)" % (self.vexity, self.sign, self.name, self.subexpressions)
    
    def __str__(self):
        """String representation"""
        return self.name


# class Variable(Expression):
#     def __init__(self, name, shape):
#         if not ismatrix(shape):
#             super(Variable, self).__init__(AFFINE, UNKNOWN, shape, name, LinearFunc.variable(name))
#         else:
#             raise TypeError("Cannot create a matrix variable.")
    
#     def __repr__(self):
#         return "Variable(%s, %s)" % (self.name, self.shape)
        
#     def scoop(self):
#         """Declaration of variable in SCOOP lang"""
#         return "variable %s %s" % ( str(self.name), str.lower(str(self.shape)) )
        
# class Parameter(Expression):
#     def __init__(self, name, shape, sign):
#         super(Parameter, self).__init__(AFFINE, sign, shape, name, LinearFunc.constant(name))
        
#     def __repr__(self):
#         return "Parameter(%s, %s, %s)" % (self.name, self.shape, self.sign)
            
#     def __str__(self):
#         return self.name
    
#     def scoop(self):
#         if isunknown(self):
#             return "parameter %s %s" % ( str(self.name), str.lower(str(self.shape)) )
#         else:
#             return "parameter %s %s %s" % ( str(self.name), str.lower(str(self.shape)), str.lower(str(self.sign)) )
    
        
# class Constant(Expression):
#     # value = 0.0
    
#     def __init__(self, value):
#         if value >= 0:
#             sign = POSITIVE
#         else:
#             sign = NEGATIVE
#         super(Constant, self).__init__(AFFINE, sign, Scalar(), str(value), LinearFunc.constant(value))
        
#     def __repr__(self):
#         return "Constant(%s)" % self.name
    
#     def scoop(self):
#         """Declaration of variable in SCOOP lang"""
#         return "variable %s %s" % ( str(self.name), str.lower(str(self.shape)) )