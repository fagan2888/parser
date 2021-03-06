from dcp_parser.parser import Parser
from dcp_parser.expression.curvature import Curvature
from dcp_parser.expression.sign import Sign
from dcp_parser.expression.expression import *
from nose.tools import assert_equals

class TestParser(object):
      """ Unit tests for the parser/parser class. """
      def setup(self):
          self.parser = Parser()

      def test_parser_errors(self):
          self.parser.parse('variable x y z')
          self.parser.parse('parameter positive a b')

          try:
               self.parser.parse("x < 2")
               assert False
          except Exception as e:
               assert_equals(str(e), "'<' constraints are not valid. Consider using '<='.")

          try:
               self.parser.parse("x > 2")
               assert False
          except Exception as e:
               assert_equals(str(e), "'>' constraints are not valid. Consider using '>='.")

          try:
               self.parser.parse('a * x = y + b')
               assert False
          except Exception as e:
                assert_equals(str(e), "'=' is not valid. Did you mean '=='?")

          try:
               self.parser.parse('x^2')
               assert False
          except Exception as e:
                assert_equals(str(e), "'^' is not valid. Consider using the 'pow' function.")

          try:
               self.parser.parse('.')
               assert False
          except Exception as e:
               assert_equals(str(e), "Illegal character '.'.")

          try:
               self.parser.parse('1 + sum(x,y) + max(1,,)')
               assert False
          except Exception as e:
               assert_equals(str(e), "Missing arguments in 'max(1, , )'.")

          try:
               self.parser.parse('none')
               assert False
          except Exception as e:
               assert_equals(str(e), "'none' is not a known variable or parameter.")
          try:
               self.parser.parse('max()')
               assert False
          except Exception as e:
               assert_equals(str(e), "Missing arguments in 'max()'.")

          try:
               self.parser.parse('max(1 1)')
               assert False
          except Exception as e:
               assert_equals(str(e), "Syntax error in call to 'max'.")

          try:
               self.parser.parse('none(x)')
               assert False
          except Exception as e:
               assert_equals(str(e), "'none' is not a known function.")

          # Arithmetic expression errors.
          try:
               self.parser.parse('1 + sum(x,y) + max(1,++)')
               assert False
          except Exception as e:
               assert_equals(str(e), "Syntax error in call to 'max'.")


          try:
               self.parser.parse('-')
               assert False
          except Exception as e:
               assert_equals(str(e), "'-' is not a valid expression.")

          try:
               self.parser.parse('1--')
               assert False
          except Exception as e:
               assert_equals(str(e), "'1--' is not a valid expression.")

          try:
               self.parser.parse('1<= ==')
               assert False
          except Exception as e:
               assert_equals(str(e), "Invalid syntax after '1'.")

          try:
               self.parser.parse('1 + >= max(1)')
               assert False
          except Exception as e:
               assert_equals(str(e), "Invalid syntax after '1'.")

          try:
               self.parser.parse('1 == 1 == 1')
               assert False
          except Exception as e:
               assert_equals(str(e), "An expression can only contain one constraint.")

          try:
               self.parser.parse('1 + 1 -2 <= 3*5 - x + max(x) <= 2')
               assert False
          except Exception as e:
               assert_equals(str(e), "An expression can only contain one constraint.")

          try:
               self.parser.parse('1 + (1 == 1)')
               assert False
          except Exception as e:
               assert_equals(str(e), "Invalid syntax after '1'.")

      def test_parse_variables(self):
          exp = 'variable x'
          self.parser.parse(exp)
          assert 'x' in self.parser.symbol_table
          assert_equals(self.parser.symbol_table['x'].curvature, Curvature.AFFINE)

          exp = ' variable  y    z '
          self.parser.parse(exp)
          assert 'z' in self.parser.symbol_table
          assert len(self.parser.symbol_table.keys()) == 3

      def test_parse_parameters(self):
          exp = 'parameter x'
          self.parser.parse(exp)
          assert 'x' in self.parser.symbol_table
          assert_equals(self.parser.symbol_table['x'].curvature, Curvature.CONSTANT)
          assert_equals(self.parser.symbol_table['x'].sign, Sign.UNKNOWN)

          exp = ' parameter negative  y    z '
          self.parser.parse(exp)
          assert 'z' in self.parser.symbol_table
          assert_equals(self.parser.symbol_table['z'].sign, Sign.NEGATIVE)
          assert_equals(len(self.parser.symbol_table.keys()), 3)

      # Test parser with only variables and parameters
      def test_basic_eval(self):
          # Empty string
          self.parser.parse('')
          assert_equals(len(self.parser.statements),0)

          self.parser.parse('variable x y z')
          self.parser.parse('parameter positive a b')
          self.parser.parse('parameter zero c d')
          expression = 'c * (a * x + d * (y / b - z) + x)'
          self.parser.parse(expression)

          result = self.parser.statements[0]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.CONSTANT)
          assert_equals(result.sign, Sign.ZERO)

          rh_exp = result.subexpressions[1]
          assert_equals('(a * x + d * (y / b - z) + x)', str(rh_exp))
          assert_equals(rh_exp.curvature, Curvature.AFFINE)

      # Test parser with numeric constants
      def test_constants_eval(self):
          self.parser.parse('variable x y z')
          self.parser.parse('parameter negative a b')
          expression = '-2 * b + 0 * (z * x - 5) + -a / 1.5'
          self.parser.parse(expression)

          result = self.parser.statements[0]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.CONSTANT)
          assert_equals(result.sign, Sign.POSITIVE)

      # Test parser with atoms
      def test_atoms_eval(self):
          self.parser.parse('variable u v')
          self.parser.parse('parameter positive c d')
          expression = 'c * square(square(u)) - log(v) - (-c * log_sum_exp(d, u, v) - max(u, c))'
          self.parser.parse(expression)

          result = self.parser.statements[0]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.CONVEX)
          assert_equals(result.sign, Sign.UNKNOWN)

          expression = '-square(square(u)) - max(square(v), c)'
          self.parser.parse(expression)
          result = self.parser.statements[len(self.parser.statements) - 1]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.CONCAVE)
          assert_equals(result.sign, Sign.NEGATIVE)

          expression = 'c * square(log(u)) + max(c, log_sum_exp(max(u, v), c))'
          self.parser.parse(expression)
          result = self.parser.statements[len(self.parser.statements) - 1]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.NONCONVEX)
          assert_equals(result.sign, Sign.POSITIVE)

          # Numeric arguments
          expression = 'kl_div(u, v)'
          self.parser.parse(expression)
          result = self.parser.statements[len(self.parser.statements) - 1]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.CONVEX)

          # Fixed arg expressions
          expression = 'huber(u, 2)'
          self.parser.parse(expression)
          result = self.parser.statements[len(self.parser.statements) - 1]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.CONVEX)

          expression = 'pow(u, -2)'
          self.parser.parse(expression)
          result = self.parser.statements[len(self.parser.statements) - 1]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.CONVEX)

          # Parameterized expressions
          expression = ("huber(u, 2) + pow(u, 2) + huber_circ(u, v, 2) "
                        "+ pow_pos(v, 3) + pow_abs(u, 5) + sum_largest(u, v, 1) "
                        "+ norm_largest(v, 2, 2) + norm(v) + norm(v, 2) + huber(u)")
          self.parser.parse(expression)
          result = self.parser.statements[len(self.parser.statements) - 1]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.CONVEX)

          expression = 'norm(u, Inf)'
          self.parser.parse(expression)
          result = self.parser.statements[len(self.parser.statements) - 1]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.CONVEX)

          expression = 'norm_inf(u)'
          self.parser.parse(expression)
          result = self.parser.statements[len(self.parser.statements) - 1]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.CONVEX)

          expression = 'norm1(u)'
          self.parser.parse(expression)
          result = self.parser.statements[len(self.parser.statements) - 1]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.CONVEX)

          expression = 'norm2(u)'
          self.parser.parse(expression)
          result = self.parser.statements[len(self.parser.statements) - 1]
          assert_equals(expression, str(result))
          assert_equals(result.curvature, Curvature.CONVEX)

      # Test parser with constraints
      def test_constraints_eval(self):
          self.parser.parse('variable x y')
          self.parser.parse('parameter positive a b')

          expression = 'a * x == y + b'
          self.parser.parse(expression)
          last = len(self.parser.statements) - 1
          result = self.parser.statements[last]
          assert_equals(expression, str(result))
          assert_equals(len(result.subexpressions), 2)
          assert_equals(len(result.errors), 0)

          expression = 'a * x + b == 2'
          self.parser.parse(expression)
          last = len(self.parser.statements) - 1
          result = self.parser.statements[last]
          assert_equals(expression, str(result))
          assert_equals(len(result.subexpressions), 2)
          assert_equals(len(result.errors), 0)

          expression = 'max(x, y) == (y + square(b))'
          self.parser.parse(expression)
          last = len(self.parser.statements) - 1
          result = self.parser.statements[last]
          assert_equals(expression, str(result))
          assert_equals(len(result.subexpressions), 2)
          assert_equals(len(result.errors), 1)

          expression = 'a * square(x) <= log(y) + b'
          self.parser.parse(expression)
          last = len(self.parser.statements) - 1
          result = self.parser.statements[last]
          assert_equals(expression, str(result))
          assert_equals(len(result.subexpressions), 2)
          assert_equals(len(result.errors), 0)

          expression = 'a * log(x) <= square(y) + b'
          self.parser.parse(expression)
          last = len(self.parser.statements) - 1
          result = self.parser.statements[last]
          assert_equals(expression, str(result))
          assert_equals(len(result.subexpressions), 2)
          assert_equals(len(result.errors), 1)

          expression = 'a * log(x) <= 2'
          self.parser.parse(expression)
          last = len(self.parser.statements) - 1
          result = self.parser.statements[last]
          assert_equals(expression, str(result))
          assert_equals(len(result.subexpressions), 2)
          assert_equals(len(result.errors), 1)

          expression = 'a * log(x) >= square(y) + b'
          self.parser.parse(expression)
          last = len(self.parser.statements) - 1
          result = self.parser.statements[last]
          assert_equals(expression, str(result))
          assert_equals(len(result.subexpressions), 2)
          assert_equals(len(result.errors), 0)      

          expression = 'a * square(x) >= log(y) + b'
          self.parser.parse(expression)
          last = len(self.parser.statements) - 1
          result = self.parser.statements[last]
          assert_equals(expression, str(result))
          assert_equals(len(result.subexpressions), 2)
          assert_equals(len(result.errors), 1) 
