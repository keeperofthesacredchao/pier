# pier 0.0.12c - Python Image Edit Recorder

pier aims to help scripted captcha solution. often the problem in hacking challenges is to solve a captcha under time constraints ( e.g. www.hackthis.co.uk ).
using python scripts to solve these challenges with googles tesseract ocr require working out the steps to prepare the captcha for good ocr results beforehand.
pier will hopefully be a tool for image preparation, setting tesseract parameters and checking the ocr output for the current version of the image.
the image editing steps are recorded to provide a way to replicate the image preparation in the hacking challenges in a fast way. this project is used as a first step in python.


## Versioning

### 0.0.12

* save / load / replay record done
* loading and replaying record from command line  with custom source / destination now possible
* some issues fixed

### 0.0.11

* scrapes all parameters via "tesseract --print-parameters" except page_separator
* user set tesseract parameters are passed to pytesseract via config parameter
* oem and psm are valid parameters as well

### 0.0.1 

* basic console
* exploration of converter and filter options in PIL
