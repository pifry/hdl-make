"""Module providing the synthesis functionality for writing Makefiles"""

import string

from .makefile import ToolMakefile
from hdlmake.util import path as path_mod


class ToolSyn(ToolMakefile):

    """Class that provides the synthesis Makefile writing methods and status"""

    def __init__(self):
        super(ToolSyn, self).__init__()

    def makefile_syn_top(self, tool_path):
        """Create the top part of the synthesis Makefile"""
        if path_mod.check_windows():
            tcl_interpreter = self._tool_info["windows_bin"]
        else:
            tcl_interpreter = self._tool_info["linux_bin"]
        top_parameter = string.Template("""\
TOP_MODULE := ${top_module}
PWD := $$(shell pwd)
PROJECT := ${project_name}
PROJECT_FILE := $$(PROJECT).${project_ext}
TOOL_PATH := ${tool_path}
TCL_INTERPRETER := ${tcl_interpreter}
ifneq ($$(strip $$(TOOL_PATH)),)
TCL_INTERPRETER := $$(TOOL_PATH)/$$(TCL_INTERPRETER)
endif

""")
        self.writeln(top_parameter.substitute(
            tcl_interpreter=tcl_interpreter,
            project_name=self.top_module.manifest_dict["syn_project"],
            project_ext=self._tool_info["project_ext"],
            tool_path=tool_path,
            top_module=self.top_module.manifest_dict["syn_top"]))

    def makefile_syn_tcl(self):
        """Create the Makefile TCL dictionary for the selected tool"""
        tcl_string = string.Template("""\

define TCL_CREATE
${tcl_create}
endef
export TCL_CREATE

define TCL_OPEN
${tcl_open}
endef
export TCL_OPEN

define TCL_SAVE
${tcl_save}
endef
export TCL_SAVE

define TCL_CLOSE
${tcl_close}
endef
export TCL_CLOSE

define TCL_SYNTHESIZE
${tcl_synthesize}
endef
export TCL_SYNTHESIZE

define TCL_TRANSLATE
${tcl_translate}
endef
export TCL_TRANSLATE

define TCL_MAP
${tcl_map}
endef
export TCL_MAP

define TCL_PAR
${tcl_par}
endef
export TCL_PAR

define TCL_BITSTREAM
${tcl_bitstream}
endef
export TCL_BITSTREAM

""")
        self.writeln(tcl_string.substitute(
            tcl_create=self._tcl_controls["create"],
            tcl_open=self._tcl_controls["open"],
            tcl_save=self._tcl_controls["save"],
            tcl_close=self._tcl_controls["close"],
            tcl_synthesize=self._tcl_controls["synthesize"],
            tcl_translate=self._tcl_controls["translate"],
            tcl_map=self._tcl_controls["map"],
            tcl_par=self._tcl_controls["par"],
            tcl_bitstream=self._tcl_controls["bitstream"]))

    def makefile_syn_local(self):
        """Generic method to write the synthesis Makefile local target"""
        self.writeln("#target for performing local synthesis\n"
                     "local: syn_pre_cmd synthesis syn_post_cmd\n")

    def makefile_syn_build(self):
        """Generate the synthesis Makefile targets for handling design build"""
        self.writeln("""\
#target for performing local synthesis
synthesis: bitstream

tcl_clean:
\t\techo "" > run.tcl

ifeq ($(wildcard $(PROJECT_FILE)),)
tcl_open:
\t\t# The project doesn't exist, create
\t\techo "$$TCL_CREATE" >> run.tcl
\t\techo "$$TCL_FILES" >> run.tcl
else
tcl_open:
\t\t# The project exists, update
\t\techo "$$TCL_OPEN" >> run.tcl
endif
tcl_save:
\t\techo "$$TCL_SAVE" >> run.tcl
tcl_close: tcl_save
\t\techo "$$TCL_CLOSE" >> run.tcl
tcl_synthesize:
\t\techo "$$TCL_SYNTHESIZE" >> run.tcl
tcl_translate: tcl_synthesize
\t\techo "$$TCL_TRANSLATE" >> run.tcl
tcl_map: tcl_translate
\t\techo "$$TCL_MAP" >> run.tcl
tcl_par: tcl_map
\t\techo "$$TCL_PAR" >> run.tcl
tcl_bitstream: tcl_par
\t\techo "$$TCL_BITSTREAM" >> run.tcl

run_tcl:
\t\t$(TCL_INTERPRETER)run.tcl

synthesize: tcl_clean tcl_open tcl_synthesize tcl_close syn_pre_synthesize_cmd run_tcl syn_post_synthesize_cmd
\t\ttouch $@ tcl_synthesize
translate: tcl_clean tcl_open tcl_translate tcl_close syn_pre_translate_cmd run_tcl syn_post_translate_cmd
\t\ttouch $@ tcl_translate tcl_synthesize
map: tcl_clean tcl_open tcl_map tcl_close syn_pre_map_cmd run_tcl syn_post_map_cmd
\t\ttouch $@ tcl_map tcl_translate tcl_synthesize
par: tcl_open tcl_par tcl_close syn_pre_par_cmd run_tcl syn_post_par_cmd
\t\ttouch $@ tcl_par tcl_map tcl_translate tcl_synthesize
bitstream: tcl_clean tcl_open tcl_bitstream tcl_close syn_pre_bitstream_cmd run_tcl syn_post_bitstream_cmd
\t\ttouch $@ tcl_bitstream tcl_par tcl_map tcl_translate tcl_synthesize

""")

    def makefile_syn_command(self):
        """Create the Makefile targets for user defined commands"""
        syn_command = string.Template("""\
# User defined commands
syn_pre_cmd:
\t\t${syn_pre_cmd}
syn_post_cmd:
\t\t${syn_post_cmd}

syn_pre_synthesize_cmd:
\t\t${syn_pre_synthesize_cmd}
syn_post_synthesize_cmd:
\t\t${syn_post_synthesize_cmd}

syn_pre_translate_cmd:
\t\t${syn_pre_translate_cmd}
syn_post_translate_cmd:
\t\t${syn_post_translate_cmd}

syn_pre_map_cmd:
\t\t${syn_pre_map_cmd}
syn_post_map_cmd:
\t\t${syn_post_map_cmd}

syn_pre_par_cmd:
\t\t${syn_pre_par_cmd}
syn_post_par_cmd:
\t\t${syn_post_par_cmd}

syn_pre_bitstream_cmd:
\t\t${syn_pre_bitstream_cmd}
syn_post_bitstream_cmd:
\t\t${syn_post_bitstream_cmd}

""")
        self.writeln(syn_command.substitute(
            syn_pre_cmd=self.top_module.manifest_dict[
            "syn_pre_cmd"],
            syn_post_cmd=self.top_module.manifest_dict[
                "syn_post_cmd"],
            syn_pre_synthesize_cmd=self.top_module.manifest_dict[
                "syn_pre_synthesize_cmd"],
            syn_post_synthesize_cmd=self.top_module.manifest_dict[
                "syn_post_synthesize_cmd"],
            syn_pre_translate_cmd=self.top_module.manifest_dict[
                "syn_pre_translate_cmd"],
            syn_post_translate_cmd=self.top_module.manifest_dict[
                "syn_post_translate_cmd"],
            syn_pre_map_cmd=self.top_module.manifest_dict[
                "syn_pre_map_cmd"],
            syn_post_map_cmd=self.top_module.manifest_dict[
                "syn_post_map_cmd"],
            syn_pre_par_cmd=self.top_module.manifest_dict[
                "syn_pre_par_cmd"],
            syn_post_par_cmd=self.top_module.manifest_dict[
                "syn_post_par_cmd"],
            syn_pre_bitstream_cmd=self.top_module.manifest_dict[
                "syn_pre_bitstream_cmd"],
            syn_post_bitstream_cmd=self.top_module.manifest_dict[
                "syn_post_bitstream_cmd"]))

    def makefile_syn_clean(self):
        """Print the Makefile clean target for synthesis"""
        self.makefile_clean()
        self.writeln("\t\t" + path_mod.del_command() +
                     " synthesize translate map par bitstream")
        self.writeln("\t\t" + path_mod.del_command() + " tcl_synthesize " +
                     "tcl_translate tcl_map tcl_par tcl_bitstream")
        self.makefile_mrproper()

    def makefile_syn_phony(self):
        """Print synthesis PHONY target list to the Makefile"""
        self.writeln(
            ".PHONY: mrproper clean syn_pre_cmd syn_post_cmd synthesis")
