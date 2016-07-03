#
# Set up the specializers default configuration here
#
#
[${specializer_name}]
#put specializer specific options here

[jit]
CC = clang
CFLAGS = -O2
PRESERVE_SRC_DIR = False

[log]
# maximum number of lines to show when programs are printed to the log
max_lines_per_source = 10

[opentuner]
args = --quiet --no-dups
timeout = 3
