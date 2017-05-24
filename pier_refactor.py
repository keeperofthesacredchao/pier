from PIL import Image
from PIL import ImageOps
from os import system

import cmd
import pickle
import pytesseract
import readline
import subprocess
import sys

ocr_param = dict( #used to store tesseract parameters
	name = int( 0 ), #parameter name
	help = int( 2 ), #help text
	value = int( 1 )) #value as string

#pierCfg currently only as Pier.pc reference
#pierCfg = dict( #config dictionary of Pier class object
#	ocr_param_gen = 0, 
#	cur = 1, 
#	fileIn = 2, 
#	fileTemp = 3, 
#	intro = 4,	
#	viewer = 5 ) 

ocr_record = dict( #one record equals one image manipulation / Pier object configuration step by pier
	cmd = 0, #string containing a pier edit session command
	args = 1 ) #arguments as string, divided by single space

class Pier( cmd.Cmd ): #main class handling pier edit sessions and replays from command line
	op_tess = [] #tesseract parameters that can be passed to pytesseract
	op_user = [] #custom tesseract parameters that will be passed to pytesseract
	pc = { 'ocr_param_gen': True, #if true, Pier scrapes tesseract parameters from "tesseract --print-parameters' on init
			'cur': None, #handle to current PIL Image object
			'fileIn': '', #source file name including path and extension
			'fileTemp': 'temp', #file name of temporary data files ( s_FileTemp.rec, s_FileTemp.img )
			'intro': 'pier v.0.0.14-ref', #text shown on pier edit session startup
			'viewer': 'feh' } #name of extern image viewer. needs to be executable on command line
	record = [] #record of the steps from the source image to the current state of the temporary image		
	viewer = None #handle to currently active image viewer process

	def do_autocontrast( self, arg ): #calls PIL.ImageOps.autocontrast. syntax: autocontrast  [ cutoff [ ignore ]]
		if( self.pc[ 'cur' ] == None ):
			print( 'no image loaded' )
			return
			
		if( len( arg )):  #check for params
			param = arg.split( ' ' )		
			count = len( param )
		else: count = 0
		
		if( count >= 1 ):  #check for syntax
			cutoff = int( param[ 0 ])
			if( count == 2 ): ignore = int( param[ 1 ])
			else:
				print( 'syntax: autocontrast  [ cutoff [ ignore ]]' )
				return
		else: cutoff = 0

		try: #call image operation
			if( count == 2 ): self.pc[ 'cur' ] = ImageOps.autocontrast( self.pc[ 'cur' ], cutoff, ignore )
			else: self.pc[ 'cur' ] = ImageOps.autocontrast( self.pc[ 'cur' ], cutoff, None )
		except OSError as err: #not all image modes support autocontrast
			print( err )
			return
			
		self.record += [[ 'autocontrast', arg ]]
	def do_convert( self, arg ): #calls PIL.Image.convert. syntax: convert mode 
		#valid modes: 1, L, P, RGB, RGBA, CMYK, YCbCr,  LAB, HSV, I, F
		if( self.pc[ 'cur' ] == None ):
			print( 'no image loaded' )
			return
			
		if( len( arg )):  #check for params
			param = arg.split( ' ' )		
			count = len( param )
		else: count = 0		
		
		if( count == 0 or len ( param ) > 1 ): #check for syntax
			print( 'syntax: convert mode ' )
			return
		
		try: self.pc[ 'cur' ]  = self.pc[ 'cur' ].convert( param[ 0 ], dither = Image.NONE ) #floyd-steinberg dither gives no good results for captchas
		except ValueError as err: 
			print( err )
			return
		
		self.record += [[ 'convert', arg ]]
	def do_get( self, arg ): #get current value of ocr parameter <arg>
		
		for param in self.op_user: #search in user set parameter
			if( param[ ocr_param[ 'name' ]] == arg ):
				print( 'parameter: {}, value: {}, description: {}'.format( param[ ocr_param[ 'name' ]], param[ ocr_param[ 'value' ] ], param[ ocr_param[ 'help' ] ]))
				return
				
		for param in self.op_tess: #search in default parameter
			if( param[ ocr_param[ 'name' ]] == arg ):
				print( 'parameter: {}, value: {}, description: {}'.format( param[ ocr_param[ 'name' ] ], param[ ocr_param[ 'value' ] ], param[ ocr_param[ 'help' ] ]))
				return	
				
		print( 'parameter "{}" not found'.format( arg ))
		
	def do_invert( self, arg ): #inverts current image. syntax: invert
		try: self.pc[ 'cur' ] = ImageOps.invert( self.pc[ 'cur' ])
		except ( AttributeError, IOError ) as err: 
			print( err )
			return		
			
		self.record += [[ 'invert', arg ]]	
		
	def do_list_ocr_params( self, arg ): #list all loaded ocr parameter		
		for param in self.op_tess: print( '{} '.format( param[ ocr_param[ 'name' ]]), end = '' )		
		print( '\n{} parameter loaded'.format( len( self.op_tess )))
		
	def do_load( self, arg ): 
		#load image file <arg> as current <Pier> object image. if <arg> is '', config param <fileIn> is used.
		# tries to load the record file '<arg>.rec' if existing. returns True if image is loaded, otherwise False.
		
		if( arg == '' ): imgFile = self.pc[ 'fileIn' ]			
		else: imgFile = arg
		
		try: img = Image.open( imgFile ) #open image file
		except IOError as err:
			 print( err )
			 return False
		
		if( self.pc[ 'cur' ]): self.pc[ 'cur' ].close() #if image was open previously close it

		self.pc[ 'fileIn' ] = imgFile #update pier config to new image
		self.pc[ 'cur' ] = img
		self.record = [] #reset record
		
		print( 'image file "{}" loaded'.format( imgFile ))
		
		try:
			temp = open( self.pc[ 'fileIn' ] + '.rec', 'rb' )
			data = pickle.load( temp )
			temp.close()
			
			if( len( data ) != 2 ):
				print( 'no valid record file: "{}"'.format( imgFile + '.rec' ))
				return True
		except FileNotFoundError as err:
			print( 'no record file "{}.rec" found for image {}'.format( imgFile, imgFile ))
			return True
		
		self.op_user = data[ 'op_user' ]
		self.record = data[ 'record' ]
		
		print( 'record file "{}.rec" loaded'.format( imgFile ))
		
		self.do_replay( '' )
		
		return True
	def do_load_ocr_params( self, arg ): #runs the system tesseract command and scrapes the parameters available for use in pier
		print( 'loading ocr parameter..', end = '' )
		system( "tesseract --print-parameters --tessdata-dir /usr/share/tessdata > pyocr_param.txt" ) #run tesseract and store output in pyocr_params.txt
		
		with open( "pyocr_param.txt" ) as f: #read file and split into lines
			params = f.read().splitlines()
			
		try:	params.pop( 0 ) #remove first line ( prompt of tesseract command )
		except IndexError as err: #no first line means file not read for whatever reason, e.g. tesseract not installed 
			print( 'failed to read parameter' )
			return
			
		self.op_tess = [] #clear list of parameters
		
		for param in params:
			temp = param.split()
			if( temp[ 0 ] != "page_separator" ): #line includes special encoding but param isnt worth the effort to read it
				self.op_tess += [[ temp.pop( 0 ), temp.pop( 0 ), " ".join( temp )]] #reads parameter name, default value and help text
		
		print( len( self.op_tess ))
		
	def do_quit( self, arg ): #stop execution
		sys.exit()        
		
	def do_replay( self, arg ): #if arg is an empty string, replay of record is run on current image. if arg is set the image file 'arg' ( and its record if existing ) is loaded before running the replay.
		if( arg ): 
			if( self.do_load( arg ) == False ):	#try to load image specified by param <arg>
				print( 'could not load image - replay aborted' )
				return
	
		rec = self.record #self.record needs to fill itself so it's safe to assume the replay of the record works and to avoid 
		self. record = [] #filling self.record while executing the steps in it
		
		for entry in rec: #replay each record entry
			print( 'replay "{} {}"'.format( entry[ ocr_record[ 'cmd' ]], entry[ ocr_record[ 'args' ]]))
			self.onecmd( entry[ ocr_record[ 'cmd' ]] + ' ' + entry[ ocr_record[ 'args' ]])
			
	def do_resize( self, arg ): #scales the current image by factor <arg>
		scale = float( arg )
		try: self.pc[ 'cur' ] = self.pc[ 'cur' ].resize(( int( scale * self.pc[ 'cur' ].width ), int( scale * self.pc[ 'cur' ].height )), Image.ANTIALIAS )
		except AttributeError as err:
			print( err )
			return
			
		self.record += [[ 'resize', arg ]]			
	def do_save( self, arg ):	#saves record and config in config param '<fileTemp> + .png.rec' and current image in '<fileTemp> + .png' if arg is ''.
											#saves the current image as '<arg> + .png' if arg is a string of non zero length and stores config / record in '<arg> + .png.rec' otherwise
		if( arg != '' and self.pc[ 'cur' ] == None ):	
			print( 'no image loaded' )
			return
			
		if( arg != '' ): sfile = arg #save current image
		else: sfile = self.pc[ 'fileTemp' ] #use config param <fileTemp> + '.png.rec' to store 
		
		try:
			self.pc[ 'cur' ].save( sfile + '.png', dpi = ( 300, 300 ), quality = 100 ) #save image with 100% quality and preferably 300 dpi in each direction in <arg> + '.png'
			#https://github.com/python-pillow/Pillow/issues/2524  ( possibly PIL.Image.save does not store dpi correctly )
			temp = open( sfile + '.png.rec', 'wb' )
			pickle.dump({ 'op_user': self.op_user, 'record': self.record }, temp, protocol = 0 ) #store record and config
			temp.close()			
		except ( KeyError, IOError ) as err:
			 print( err )
			 return

		print( 'files "{}.png" and "{}.png.rec" saved'.format( sfile, sfile ))
	def do_set(  self, arg ): #set ocr parameter. syntax: set parameter value
		args = arg.split( ' ' )
		
		if( len( args ) < 1 or len( args ) > 2 ): #check for syntax
			print( 'syntax: set parameter value' )
			return
		
		for param in self.op_user: #search in user set parameter
			if( param[ ocr_param[ 'name' ]] == args[ 0 ]):
				param[ ocr_param[ 'value' ]] = args[ 1 ] #set current user parameter to new value
				return
				
		for param in self.op_tess: #search in ocr default parameter
			if( param[ ocr_param[ 'name' ]] == args[ 0 ]):
				self.op_user += [[ args[ 0 ], args[ 1 ], param[ ocr_param[ 'help']]]] #add new user parameter with new value
				return				
				
		print( 'parameter "{}" not found'.format( args[ 0 ]))
							
	def do_show( self, arg ): #show image <arg> with viewer set in config param <viewer>. if <arg> is '', config param <cur> is used
		if( self.viewer != None ): #close last instance
			self.viewer.terminate()
			self.viewer.kill()
			self.viewer = None
			
		if( len( arg )): imgFile = arg #check for file param
		else:
			self.do_save( '' )
			imgFile = self.pc[ 'fileTemp' ] + '.png' #save current image to show the file afterwards if no file param is given
		
		try: self.viewer = subprocess.Popen([ self.pc[ 'viewer' ] , imgFile ]) #run viewer in subprocess and store handle
		except subprocess.SubprocessError as err:
			print( err )
			return			
			
	def do_tesseract( self, arg = 'cur' ): #runs tesseract on image depending on <arg>:  'cur' uses config param <cur>
		if( arg != '' ): imgFile = arg #'FILE' uses FILE+.png
		else: imgFile = self.pc[ 'fileTemp' ] #'' uses config param <fileTemp>
		
		param = ''
		
		for op in self.op_user:	#put together parameter. common params are formed '--param value', extended ones '-c param=value'
			if(( op[ ocr_param[ 'name' ]] == 'oem' ) or ( op[ ocr_param[ 'name' ] ] == 'psm' ) or ( op[ ocr_param[ 'name' ] ]  == 'tessdata-dir' )): 
				param += ( '--' + op[ ocr_param[ 'name' ] ] + ' ' + op[ ocr_param[ 'value' ] ] + ' ' )
			else:
				param += ( '-c ' + op[ ocr_param[ 'name' ] ] + '=' + op[ ocr_param[ 'value' ] ] + ' ' )
		
		try: #try to run tesseract on image, 'param' is reused for result
			if( arg == 'cur' ): param = pytesseract.image_to_string( self.pc[ 'cur' ], config = param )
			else: param = pytesseract.image_to_string( Image.open( imgFile + '.png' ), config = param )
		except IOError as err:
			print( err )
			return None		
			
		print( 'tesseract return: "{}"'.format( param ))
		return param
		
	def init( self ):
		self.intro = self.pc[ 'intro' ]
		self.op_user = [[ 'psm', '13', 'page segmentation mode' ], ['oem', '1', 'ocr engine mode'], [ 'tessdata-dir', '/usr/share/tessdata/', 'tessdata path' ]]
		self.prompt = 'pier> '
		
		if( self.pc[ 'ocr_param_gen' ] == True ): self.do_load_ocr_params( '' )	
		if( self.pc[ 'cur' ]):
			self.pc[ 'cur' ].close()
			self.pc[ 'cur' ] = None
			
	def postcmd( self, stop, line ): #used to prompt pier status info	
		print( '\nparameter: {} | fileIn: "{}" | record: {}'.format( self.op_user, self.pc[ 'fileIn' ], self.record )) 
	def preloop( self ):
		self.init()
		self.postcmd( False, 0 )
		
if __name__ == '__main__': #syntax: pier [ fileIn fileOut ] 
	#fileIn must be full path with extension to an image file with corresponding .rec record file
	#fileOut must be full path with extension to a file where the tesseract ocr result is stored as string
	
	sys.argv.pop( 0 )	
	
	if( len( sys.argv ) == 0 ): #when no arguments are passed a pier edit session is started
		Pier().cmdloop()
		sys.exit()
		
	p = Pier()
	
	try:
		p.do_load( sys.argv.pop( 0 )) #run replay for fileIn

		fileOut = open( sys.argv.pop( 0 ), 'wt' )
		res = p.do_tesseract()
		fileOut.write( res ) #store ocr result in fileOut
		fileOut.close()
	except NameError as err:
		print( err )
		sys.exit( 1 )
	except IndexError as err:
		print( 'syntax: pier [ fileIn fileOut ]' )
		sys.exit( 2 )
	
	sys.exit( 0 )

