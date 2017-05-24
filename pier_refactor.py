from PIL import Image

import cmd
import pickle
import pytesseract
import readline
import subprocess
import sys

ocrParam = dict(  							#used to store tesseract parameters
	name = 0,                                     #parameter name
	help = 2,                                    #help text
	value = 1)                                   #value as string


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
	op_tess = [{}] 																#tesseract parameters that can be passed to pytesseract
	op_user = [{}]																#custom tesseract parameters that will be passed to pytesseract
	pc = { 'ocr_param_gen': True,
			'cur': None,
			'fileIn': '',
			'fileTemp': 'temp',
			'intro': 'pier v.0.0.14-ref',
			'viewer': 'feh' }            
	record = []																	#record of the steps from the source image to the current state of the temporary image		
	viewer = None															#handle to currently active image viewer process

	def do_load_defaults( self, arg ):							#load default values for Pier.pc. <arg> currently unused
		self.init()
		
	def do_load_img( self, arg ):									#load image file <arg> as current <Pier> object image. if <arg> is '', config param <fileIn> is used
		if( arg == "" ): imgFile = self.pc[ 'fileIn' ]			
		else: imgFile = arg
		
		try: img = Image.open( imgFile )						#open image file
		except IOError as err:
			 print( err )
			 return
		
		if( self.pc[ 'cur' ]): self.pc[ 'cur' ].close()			#if image was open previously close it

		self.pc[ 'fileIn' ] = imgFile									#update pier config to new image
		self.pc[ 'cur' ] = img
		self.record = [] 													#reset record
		
	def do_quit( self, arg ):											#stop execution
		sys.exit()        
		
	def do_save( self, arg ):											#save record and config in file <arg>+'.rec'. if <arg> is '', config param <fileTemp> is used. image is stored in <arg>+'.png'
		if( self.pc[ 'cur' ] == None ):	
			print( 'no image loaded' )
			return
			
		if( arg != '' ): sfile = arg
		else: sfile = self.pc[ 'fileTemp' ]
		
		try: 
			self.pc[ 'cur' ].save( sfile + '.png', dpi = ( 300, 300 ), quality = 100 )		#save image with 100% quality and preferably 300 dpi in each direction
			temp = open( sfile + '.rec', 'wb' )
			pickle.dump([ self.op_user, self.record], temp, protocol = 0 )					#store record and config
			temp.close()			
		except ( KeyError, IOError ) as err: print( err )
		
	def do_show( self, arg ):										#show image <arg> with viewer set in config param <viewer>. if <arg> is '', config param <fileIn> is used
		if( arg != ''): imgFile = arg
		else: imgFile = self.pc[ 'fileIn' ]
		
		if( self.viewer != None ):																		#close last instance
			self.viewer.terminate()
			self.viewer.kill()
			self.viewer = None
		
		try: self.viewer = subprocess.Popen([ self.pc[ 'viewer' ] , imgFile ])	#run viewer in subprocess and store handle
		except subprocess.SubprocessError as err:
			print( err )
			return
			
	def do_tesseract( self, arg = 'cur' ):		#runs tesseract on image depending on <arg>:  'cur' uses config param <cur>
		if( arg != '' ): imgFile = arg																							#'FILE' uses FILE+.png
		else: imgFile = self.pc[ 'fileTemp' ]																				#'' uses config param <fileTemp>
		
		param = ''
		
		for op in self.op_user:	#put together parameter. common params are formed '--param value', extended ones '-c param=value'
			if(( op[ ocrParam[ 'name' ]] == 'oem' ) or ( op[ ocrParam[ 'name' ] ] == 'psm' ) or ( op[ ocrParam[ 'name' ] ]  == 'tessdata-dir' )): 
				param += ( '--' + op[ ocrParam[ 'name' ] ] + ' ' + op[ ocrParam[ 'value' ] ] + ' ' )
			else:
				param += ( '-c ' + op[ ocrParam[ 'name' ] ] + '=' + op[ ocrParam[ 'value' ] ] + ' ' )
		
		try:		#try ton run tesseract on image, 'param' is reused for result
			if( arg == 'cur' ): param = pytesseract.image_to_string( self.pc[ 'cur' ], config = param )
			else: param = pytesseract.image_to_string( Image.open( imgFile + '.png' ), config = param )
		except IOError as err:
			print( err )
			return None		
			
		print( 'tesseract return: "{}"'.format( param ))
		return param
		
	def init( self ):
		self.intro = self.pc[ 'intro' ]
		self.op_user = self.op_tess = [[ 'psm', '13', 'page segmentation mode' ],
															['oem', '1', 'ocr engine mode'],
															  [ 'tessdata-dir', '/usr/share/tessdata/', 'tessdata path' ]]
		self.prompt = 'pier> '
	def preloop( self ):
		self.init()
		
if __name__ == '__main__':
	Pier().cmdloop()
