To interact with the parser, first write a file containing expressions of the following form:
  variable x y z ...
  parameter (positive|negative) a b c ...
  Any objective (i.e. '-log(x) + max(square(y),a) + b*z')

See sample.txt for an example.

Run demo.py and follow the instructions. You will then be able to browse the parse trees for the objectives in the file.