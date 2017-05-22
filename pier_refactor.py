from PIL import Image
from typing import NamedTuple

import cmd
import sys

class OcrParam( NamedTuple ):	#used to store tesseract parameters
	cmd: str										#parameter name
	help: str										#help text
	value: str									#value as string


class PierCfg( NamedTuple ):		#config of Pier class object
	ocr_param_gen: bool 				#if true, Pier scrapes tesseract parameters from "tesseract --print-parameters' on init
	cur: any										#handle to current PIL Image object
	fileIn: str 									#source file name including path and extension
	fileTemp: str								#file name of temporary data files ( s_FileTemp.rec, s_FileTemp.img )
	intro: str										#text shown on module startup
	prompt: str									#prompt shown in pier edit session
	viewer: str 									#name of extern image viewer. needs to be executable on command line

class Record ( NamedTuple ):		#one record equals one image manipulation / Pier object configuration step by pier
	arg: str										#string containing a pier edit session command
	cmd: str										#arguments as string, divided by single space

class Pier( cmd.Cmd ):					#main class handling pier edit sessions and replays from command line
	op_tess: []									#tesseract parameters that can be passed to pytesseract
	op_user: []									#custom tesseract parameters that will be passed to pytesseract
	record: []										#record of the steps from the source image to the current state of the temporary image		
	def do_quit( self, arg ):				#stop execution
		sys.exit()

if __name__ == "__main__":
	pier = Pier()
	pier.cmdloop()
