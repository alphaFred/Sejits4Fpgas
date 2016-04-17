#
# Vivado (TM) v2015.2 (64-bit)
#
# template_project.tcl: Tcl script for re-creating project 'template_project'
#
# Generated by Vivado on Tue Jan 26 14:29:19 CET 2016
# IP Build 1264090 on Wed Jun 24 14:22:01 MDT 2015
#
# This file contains the Vivado Tcl commands for re-creating the project to the state*
# when this script was generated. In order to re-create the project, please source this
# file in the Vivado Tcl Shell.
#
# * Note that the runs in the created project will be configured the same way as the
#   original project, however they will not be launched automatically. To regenerate the
#   run results please launch the synthesis/implementation runs as needed.
#
#*****************************************************************************************
# NOTE: In order to use this script for source control purposes, please make sure that the
#       following files are added to the source control system:-
#
# 1. This project restoration tcl script (template_project.tcl) that was generated.
#
# 2. The following source(s) files that were local or imported into the original project.
#    (Please see the '$orig_proj_dir' and '$origin_dir' variable setting below at the start of the script)
#
#    <none>
#
# 3. The following remote source files that were added to the original project:-
#
#    "/home/philipp/University/M4/Masterthesis/src/vivado/template_project/template_project.srcs/sources_1/bd/template_design/template_design.bd"
#    "/home/philipp/University/M4/Masterthesis/src/vivado/template_project/template_project.srcs/sources_1/bd/template_design/hdl/template_design_wrapper.vhd"
#    "/home/philipp/University/M4/Masterthesis/src/vivado/template_project/template_project.srcs/sources_1/new/top.vhd"
#
#*****************************************************************************************

# Set the reference directory for source file relative paths (by default the value is script directory path)
set origin_dir "/home/philipp/University/M4/Masterthesis/src/vhdl-sejits/src/vivado/template_project"
# Set the directory path for the original project from where this script was exported
set orig_proj_dir "[file normalize "$origin_dir/"]"

# Create project
create_project -force template_project ./template_project

# Set the directory path for the new project
set proj_dir [get_property directory [current_project]]

# Set project properties
set obj [get_projects template_project]
set_property "board_part" "em.avnet.com:zed:part0:1.3" $obj
set_property "default_lib" "xil_defaultlib" $obj
set_property "simulator_language" "VHDL" $obj
set_property "target_language" "VHDL" $obj

# Create 'sources_1' fileset (if not found)
if {[string equal [get_filesets -quiet sources_1] ""]} {
  create_fileset -srcset sources_1
}

# Set 'sources_1' fileset object
set obj [get_filesets sources_1]
set files [list \
 "[file normalize "$origin_dir/template_project.srcs/sources_1/bd/template_design/template_design.bd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/bd/template_design/hdl/template_design_wrapper.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/top.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/accel_wrapper.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/generated.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/vector_dff.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/DReg.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/bram_fifo.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/Convolve.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/logic_dff.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/STD_FIFO.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/the_filter_package.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/filter.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/Split.vhd"]"\
 "[file normalize "$origin_dir/template_project.srcs/sources_1/new/BasicArith.vhd"]"\
]
add_files -norecurse -fileset $obj $files

# Set 'sources_1' fileset file properties for remote files
set file "$origin_dir/template_project.srcs/sources_1/bd/template_design/template_design.bd"
set file [file normalize $file]
set file_obj [get_files -of_objects [get_filesets sources_1] [list "*$file"]]
if { ![get_property "is_locked" $file_obj] } {
  set_property "generate_synth_checkpoint" "0" $file_obj
}

set file "$origin_dir/template_project.srcs/sources_1/bd/template_design/hdl/template_design_wrapper.vhd"
set file [file normalize $file]
set file_obj [get_files -of_objects [get_filesets sources_1] [list "*$file"]]
set_property "file_type" "VHDL" $file_obj

set file "$origin_dir/template_project.srcs/sources_1/new/top.vhd"
set file [file normalize $file]
set file_obj [get_files -of_objects [get_filesets sources_1] [list "*$file"]]
set_property "file_type" "VHDL" $file_obj


# Set 'sources_1' fileset file properties for local files
# None

# Set 'sources_1' fileset properties
set obj [get_filesets sources_1]
set_property "top" "top" $obj

# Create 'constrs_1' fileset (if not found)
if {[string equal [get_filesets -quiet constrs_1] ""]} {
  create_fileset -constrset constrs_1
}

# Set 'constrs_1' fileset object
set obj [get_filesets constrs_1]

# Empty (no sources present)

# Set 'constrs_1' fileset properties
set obj [get_filesets constrs_1]

# Create 'sim_1' fileset (if not found)
if {[string equal [get_filesets -quiet sim_1] ""]} {
  create_fileset -simset sim_1
}

# Set 'sim_1' fileset object
set obj [get_filesets sim_1]
# Empty (no sources present)

# Set 'sim_1' fileset properties
set obj [get_filesets sim_1]
set_property "top" "top" $obj
set_property "xelab.nosort" "1" $obj
set_property "xelab.unifast" "" $obj

# Create 'synth_1' run (if not found)
if {[string equal [get_runs -quiet synth_1] ""]} {
  create_run -name synth_1 -part xc7z020clg484-1 -flow {Vivado Synthesis 2015} -strategy "Vivado Synthesis Defaults" -constrset constrs_1
} else {
  set_property strategy "Vivado Synthesis Defaults" [get_runs synth_1]
  set_property flow "Vivado Synthesis 2015" [get_runs synth_1]
}
set obj [get_runs synth_1]

# set the current synth run
current_run -synthesis [get_runs synth_1]

# Create 'impl_1' run (if not found)
if {[string equal [get_runs -quiet impl_1] ""]} {
  create_run -name impl_1 -part xc7z020clg484-1 -flow {Vivado Implementation 2015} -strategy "Vivado Implementation Defaults" -constrset constrs_1 -parent_run synth_1
} else {
  set_property strategy "Vivado Implementation Defaults" [get_runs impl_1]
  set_property flow "Vivado Implementation 2015" [get_runs impl_1]
}
set obj [get_runs impl_1]
set_property "steps.write_bitstream.args.readback_file" "0" $obj
set_property "steps.write_bitstream.args.verbose" "0" $obj

# set the current impl run
current_run -implementation [get_runs impl_1]

puts "INFO: Project created:template_project"