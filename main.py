from PIL import Image
from PIL import ImageFilter
from PIL import ImageOps
from os import system

import cmd
import codecs
import pickle
import pytesseract
import readline
import subprocess
import sys

class pier( cmd.Cmd ):	
	b_generate_pyocr_params = True
	f_imgIn="captcha.png"
	f_imgOut="temp"	
	feh = None
	imgIn=None
	intro = "pier 0.0.12"
	prompt = "pier> "	
	pyocr_params = []
	pyocr_user_params = []
	record = []
	file=None
	def do_autocontrast( self, arg ):
		if( self.imgIn == None ): return None
		self.imgIn = ImageOps.autocontrast( self.imgIn )		
		self.record += [[ "autocontrast", arg ]]
	def do_blur( self = None , arg = "" ):
		if(( self == None ) or ( self.imgIn == None )): return None
		self.imgIn = self.imgIn.filter( ImageFilter.BLUR )
		self.record += [[ "bour", "" ]]
	def do_contour( self = None , arg = "" ):
		if(( self == None ) or ( self.imgIn == None )): return None
		self.imgIn = self.imgIn.filter( ImageFilter.CONTOUR )
		self.record += [[ "contour", "" ]]
	def do_convertL( self, arg ):
		if( self.imgIn == None ): return None
		self.imgIn = self.imgIn.convert("L", dither = Image.NONE)
		self.record += [[ "convertL", arg ]]
	def do_convertLA( self, arg ):
		if( self.imgIn == None ): return None
		self.imgIn = self.imgIn.convert("LA", dither = Image.NONE)		
		self.record += [[ "convertLA", arg ]]
	def do_convert1( self, arg ):
		if( self.imgIn == None ): return None
		self.imgIn = self.imgIn.convert("1", dither = Image.NONE )
		self.record += [[ "convert1", arg ]]
	def do_detail( self = None , arg = "" ):
		if(( self == None ) or ( self.imgIn == None )): return None
		self.imgIn = self.imgIn.filter( ImageFilter.DETAIL )
		self.record += [[ "detail", "" ]]
	def do_edge_enhance( self = None , arg = "" ):
		if(( self == None ) or ( self.imgIn == None )): return None
		self.imgIn = self.imgIn.filter( ImageFilter.EDGE_ENHANCE )
		self.record += [[ "edge_enhance", "" ]]		
	def do_edge_enhance_more( self = None , arg = "" ):
		if(( self == None ) or ( self.imgIn == None )): return None
		self.imgIn = self.imgIn.filter( ImageFilter.EDGE_ENHANCE_MORE )
		self.record += [[ "edge_enhance_more", "" ]]
	def do_emboss( self = None , arg = "" ):
		if(( self == None ) or ( self.imgIn == None )): return None
		self.imgIn = self.imgIn.filter( ImageFilter.EMBOSS )
		self.record += [[ "emboss", "" ]]
	def do_expand( self, arg ):
		if( self.imgIn == None ): return None
		if( arg == "" ): arg = "10"
		self.imgIn = ImageOps.expand( self.imgIn, int( arg ))
		self.record += [[ "expand", int( arg )]]
	def do_filter( self, arg ):
		if( self.imgIn == None ): return None 
		temp = arg.split( ' ' )
		for fl in temp: self.onecmd( fl )
	def do_find_edges( self = None , arg = "" ):
		if(( self == None ) or ( self.imgIn == None )): return None
		self.imgIn = self.imgIn.filter( ImageFilter.FIND_EDGES )
		self.record += [[ "find_edges", "" ]]
	def do_invert( self, arg ):
		if( self.imgIn == None ): return None
		self.imgIn = ImageOps.invert( self.imgIn )
		self.record += [[ "invert", arg ]]
	def do_load( self, arg ):
		if( arg == "" ): return None
		self.f_imgIn = arg
		self.preloop()
	def do_pyocr_gen_param_list( self, arg ):
		system( "tesseract --print-parameters  > pyocr_param.txt" )
		with codecs.open( "pyocr_param.txt" ) as f:
			params = f.read().splitlines()
		params.pop( 0 )
		for param in params:
			temp = param.split()
			if( temp[ 0 ] != "page_separator" ):  self.pyocr_params+= [[ temp.pop( 0 ), temp.pop( 0 ), " ".join( temp )]]
	def do_pyocr_param_get( self, arg ):
		for param in self.pyocr_params: 
			if( arg == param[0]):
				print( "param: {}, value: {}, help: {}".format( param[0], param[1], param[2] ))
				return None
		print( "parameter '{}' not found ".format( arg ))
	def do_pyocr_param_set( self, arg ):
		temp = arg.split( ' ' )
		for param in self.pyocr_params:
			if( temp[0] == param[0] ):
				temp.pop( 0 )
				temp = " ".join( temp )
				param[ 1 ] = temp
				for user_param in self.pyocr_user_params:
					if( user_param[0] == param[0] ): 
						user_param[ 1 ] = temp
						return None
				self.pyocr_user_params += [[ param[ 0 ], param[ 1 ]]]
				return None
		print( "parameter '{}' not found!".format( temp[ 0 ]))
	def do_pyocr_param_list( self, arg ):
		for param in self.pyocr_params: print( param[ 0 ], " ", end='' )
		print()
	def do_pytesseract( self, arg ):
		param = ""
		if( self.imgIn == None ): return None
		for temp in self.pyocr_user_params: param += ( '-' + temp[ 0 ] + ' ' + temp[ 1 ] + ' ' )
		print( "running with parameters: ", param )			
		print( pytesseract.image_to_string( self.imgIn, config = param ))		
	def do_quit( self, arg ):
		sys.exit()		
	def do_reload( self, arg ):
		if( self.f_imgIn == None ): return None
		if( self.imgIn ): self.imgIn.close()
		self.preloop()
		self.imgIn = Image.open( self.f_imgIn )
	def do_replay( self, arg ):
		if( arg == "" ): return None
		self.f_imgOut = arg
		temp = open( self.f_imgOut + ".rec", "rb" )
		replay = pickle.load( temp )
		temp.close()
		temp = replay[ 0 ]
		self.pyocr_user_params = replay[ 1 ]
		for x in temp: self.onecmd( x[ 0 ] + " " +  x[ 1 ])
		self.do_save( "" )
	def do_resize( self, arg ):
		if(( self.imgIn == None ) or ( arg == "" )): return None
		self.imgIn = self.imgIn.resize(( self.imgIn.width * int( arg ), self.imgIn.height * int( arg )), Image.ANTIALIAS )
		self.record += [[ "resize", arg ]]
	def do_save( self, arg ):
		if(( self.imgIn == None ) or  ( self.f_imgOut == None )): return None
		if( arg != "" ): self.f_imgOut = arg
		self.imgIn.save( self.f_imgOut + ".png", quality = 100 )
		temp = open( self.f_imgOut + ".rec", "wb" )
		pickle.dump([ self.record, self.pyocr_user_params ], temp, protocol = 0 )
		temp.close()
	def do_sharpen( self, arg ):
		if( self.imgIn == None ): return None
		self.imgIn = self.imgIn.filter( ImageFilter.SHARPEN )
		self.record += [[ "sharpen", arg ]]
	def do_show( self, arg ):
		if(( self.imgIn == None  ) or  ( self.f_imgIn == None )): return None		
		if( self.feh ):
			self.feh.terminate()
			self.feh.kill()	
		self.feh = subprocess.Popen([ 'feh', self.f_imgOut + ".png" ])
	def do_smooth( self = None , arg = "" ):
		if(( self == None ) or ( self.imgIn == None )): return None
		self.imgIn = self.imgIn.filter( ImageFilter.SMOOTH )
		self.record += [[ "smooth", "" ]]				
	def do_smooth_more( self = None , arg = "" ):
		if(( self == None ) or ( self.imgIn == None )): return None
		self.imgIn = self.imgIn.filter( ImageFilter.SMOOTH_MORE )
		self.record += [[ "smooth_more", "" ]]						
	def postcmd( self, stop = False , line = "" ):
		print( "f: {} | p: {} | r: {}".format( self.f_imgIn, self.pyocr_user_params, self.record ))
	def preloop( self ):
		self.record = []
		self.pyocr_params = [[ "psm", "7", "set page segmentation mode" ], [ "oem", "0", "set engine mode"]]
		self.pyocr_user_params = [[ "psm", "7" ],[ "oem", "0" ]]					
		if( self.b_generate_pyocr_params ):
			print( "collect tesseract parameters.." )
			self.do_pyocr_gen_param_list( "" )
		if( self.f_imgIn ):
			self.imgIn = Image.open( self.f_imgIn )	
			self.imgIn.save( self.f_imgOut + ".png", quality = 100 )
		
					
if __name__=="__main__":
		
	sys.argv.pop( 0 )	
	
	if( len( sys.argv ) == 0 ):
		pier().cmdloop()
		sys.exit()
	
	p = pier()
	p.do_load( sys.argv.pop( 0 ))
	p.do_replay( sys.argv.pop( 0 ))
	p.do_save( sys.argv.pop( 0 ))
