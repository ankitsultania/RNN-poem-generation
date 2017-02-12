'''
Update the path to the location of directory "download"
generated in scraping.

'''


import glob
import re

PATH = '../../download/*/*.txt'
VERSE_SEPARATOR = "^^^^^^^^^^#"
HALF_VERSE_SEPARATOR = "^^^^^^^%"
LINE_SEPARATOR = "^^^^^$"
FOOTER_TEXT = "This text is part of the TITUS"

def main():
    global PATH, VERSE_SEPARATOR, HALF_VERSE_SEPARATOR, LINE_SEPARATOR, FOOTER_TEXT
    
    with open("regularized_data.txt", 'w', encoding="utf8") as outputfile:
        
        for file in glob.glob(PATH):
            
            with open(file, 'r', encoding="utf8") as inputfile:
                
                """ Split each verses in the file"""
                
                chapter = inputfile.read()
                chapter_without_footer = chapter.split(FOOTER_TEXT)[0] #remove footer text
                verses = chapter_without_footer.split("Verse:")
                verses = verses[1:]
                
                for verse in verses:
                    
                    """ Split each sub-verse in the verse """
                    
                    verse = re.sub('/[\d]*/', '//', verse)
                    outputfile.write(VERSE_SEPARATOR)
                    halfverses = re.split('Halfverse: (?:[a-z])', verse)
                    halfverses = halfverses[1:]
                    
                    for halfverse in halfverses:
                        
                        """ Split each line in the half verse """
                        
                        halfverse.strip()
                        outputfile.write(HALF_VERSE_SEPARATOR)
                        lines = halfverse.split("\n");
                        
                        for line in lines:
                            
                            if not line == '':
                                outputfile.write(LINE_SEPARATOR)
                                line = re.sub('/[^\/]*', '/', line) #remove arbitrary data following end of sentence marker
                                outputfile.write(line.strip())
    
if __name__=="__main__":
    main()