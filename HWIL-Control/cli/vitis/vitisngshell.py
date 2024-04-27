#!/usr/bin/env python3
import os
import time
from IPython.terminal.prompts import Prompts, Token

class CustomPrompt(Prompts):

    def in_prompt_tokens(self, cli=None):

       return [
            (Token.Prompt, 'Vitis ['),
            (Token.PromptNum, str(self.shell.execution_count)),
            (Token.Prompt, ']: '),
            ]

    def out_prompt_tokens(self):
       return [
            (Token.OutPrompt, 'Out['),
            (Token.OutPromptNum, str(self.shell.execution_count)),
            (Token.OutPrompt, ']: '),
        ]

from traitlets.config import Config
try:
    get_ipython
except NameError:
    nested = 0
    cfg = Config()
    cfg.TerminalInteractiveShell.prompts_class=CustomPrompt
    cfg.HistoryManager.enabled = True
    #cfg.HistoryManager.hist_file = "/tmp/vitisng_history.txt"

# First import the embeddable shell class
from IPython.terminal.embed import InteractiveShellEmbed

# Now create an instance of the embeddable shell. The first argument is a
# string with options exactly as you would type them if you were starting

ipshell = InteractiveShellEmbed(config=cfg,
                         banner1 = "Welcome to Vitis Python Shell",
                         banner2 = "Journal file generates at "+os.path.abspath("vitis_journal.py")+
                         "\nDo not use the file until the session is closed.",
                         enabled = False)
import vitis

#VITIS NG Journal File Generation
vitis_version = "2023.1"
default_log_file = "vitis_journal.py"
session_start_time = time.ctime()
log_start_option = " -o -q " + default_log_file
ipshell.run_line_magic('logstart', log_start_option)

ipshell()

journal_file_path = os.path.abspath(ipshell.logfile)
JOURNAL_HEADER = f"#-----------------------------------------------------------------\n\
# Vitis v{vitis_version} (64-bit)\n\
# Start of session at: {session_start_time}\n\
# Current directory: {os.getcwd()}\n\
# Command line: vitis -i\n\
# Journal file: {ipshell.logfile}\n\
# Batch mode: $XILINX_VITIS/bin/vitis -new -s {journal_file_path}\n\
#-----------------------------------------------------------------\n\n\
#!/usr/bin/env python3\n\
import vitis"

log_head = "# IPython log file"
ipython_line = "get_ipython()."
dispose_line = "vitis.dispose()"

data = []
journal_data = []
if(os.path.isfile(journal_file_path)):
    with open(ipshell.logfile, 'r') as input_journal:
        data = input_journal.readlines()

    for line in data:
        if log_head in line:
            journal_data.append(JOURNAL_HEADER)
        elif ipython_line in line:
            ipython_line_read = True
            prev_line = journal_data.pop()
            if "# " not in prev_line:
                journal_data.append(prev_line)
        elif "#[Out]# " in line:
            if ipython_line_read != True:
                journal_data.append(line)
        else:
            ipython_line_read = False
            journal_data.append(line)

    journal_data.append(dispose_line)
    journal_data.append("\n")

    with open(ipshell.logfile, 'w') as output_journal:
        output_journal.writelines(journal_data)
    print(f"Vitis Journal File is '{journal_file_path}'")

print(f'Vitis Python Shell Execution finished. Bye!!')
