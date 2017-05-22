from PIL import Image

import cmd
import readline
import sys

ocrParam = dict(  							#used to store tesseract parameters
	cmd = 1,                                     #parameter name
	help = 2,                                    #help text
	value = 3)                                   #value as string


pierCfg = dict(       #config of Pier class object
	ocr_param_gen = 1,    				#if true, Pier scrapes tesseract parameters from "tesseract --print-parameters' on init
	cur = 2,										#handle to current PIL Image object
	fileIn = 3, 									#source file name including path and extension
	fileTemp = 4,								#file name of temporary data files ( s_FileTemp.rec, s_FileTemp.img )
	intro = 5,										#text shown on module startup
	viewer = 6 )								#name of extern image viewer. needs to be executable on command line

record = dict( 		#one record equals one image manipulation / Pier object configuration step by pier
	arg = 1,										#string containing a pier edit session command
	cmd = 2 )										#arguments as string, divided by single space

class Pier( cmd.Cmd ):												#main class handling pier edit sessions and replays from command line
	op_tess: [] 																#tesseract parameters that can be passed to pytesseract
	op_user: []																#custom tesseract parameters that will be passed to pytesseract
	pc = { 'ocr_param_gen': True,
			'cur': None,
			'fileIn': '',
			'fileTemp': 'temp',
			'intro': 'pier v.0.0.14-ref',
			'viewer': 'feh' }            
	record: []																	#record of the steps from the source image to the current state of the temporary image		

	def do_load_defaults( self, arg ):							#load default values for Pier.pc. <arg> currntly unused
		self.init( self )
	def do_load_img( self, arg ):									#load image file <arg> as current Pier object image
		if( arg == "" ):
			if( self.pc[ 'fileIn' ] == "" ): return
		else: self.pc[ "fileIn" ] = arg
		
		print ( self.pc )
	def do_quit( self, arg ):				#stop execution
		sys.exit()        
	def init( self ):
		self.intro = self.pc[ 'intro' ]
		self.op_user = self.op_tess = [[ "psm", "13", "page segmentation mode" ], [ "oem", "1", "ocr engine mode"], [ "tessdata-dir", "/usr/share/tessdata/",  "tessdata path" ]]					
		self.prompt = "pier> "
	def preloop( self ):
		self.init()
if __name__ == "__main__":
	#pier = Pier()
	Pier().cmdloop()
