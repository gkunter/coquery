# -*- coding: utf-8 -*-

"""
coq_install_coca.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
import codecs
import csv

from corpusbuilder import *
import dbconnection

class COCABuilder(BaseCorpusBuilder):
    file_filter = "db_*_*.txt"

    word_table = "Words"
    word_id = "WordId"
    word_label = "Text"
    word_lemma_id = "LemmaId"
    word_pos = "POS"
    word_transcript = "Transcript"
    word_lemmatranscript = "Lemma_Transcript"
    
    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"

    corpus_table = "Corpus"
    corpus_id = "TokenId"
    corpus_word_id = "WordId"
    corpus_pos_id = "PosId"
    corpus_source_id = "SourceId"
    corpus_time = "Time"

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_lemma = "Lemma"
    word_pos = "POS"

    pos_table = "POS"
    pos_id = "PosId"
    pos_label = "POS"
    pos_labelclean = "POS_clean"
    
    source_table = "Sources"
    source_id = "SourceId"
    source_label = "Source"
    source_title = "Title"
    source_genre = "Genre"
    source_year = "Year"
    source_subgenre_id = "SubgenreId"
    
    subgenre_table = "Subgenres"
    subgenre_id = "SubgenreId"
    subgenre_label = "Subgenre"

    expected_files = [
        "coca-sources.txt", "lexicon.txt", "Sub-genre codes.txt",
        "db_acad_1990.txt", "db_acad_1991.txt", "db_acad_1992.txt", 
        "db_acad_1993.txt", "db_acad_1994.txt", "db_acad_1995.txt", 
        "db_acad_1996.txt", "db_acad_1997.txt", "db_acad_1998.txt", 
        "db_acad_1999.txt", "db_acad_2000.txt", "db_acad_2001.txt", 
        "db_acad_2002.txt", "db_acad_2003.txt", "db_acad_2004.txt", 
        "db_acad_2005.txt", "db_acad_2006.txt", "db_acad_2007.txt", 
        "db_acad_2008.txt", "db_acad_2009.txt", "db_acad_2010.txt", 
        "db_acad_2011.txt", "db_acad_2012.txt", "db_fic_1990.txt", 
        "db_fic_1991.txt", "db_fic_1992.txt", "db_fic_1993.txt", 
        "db_fic_1994.txt", "db_fic_1995.txt", "db_fic_1996.txt", 
        "db_fic_1997.txt", "db_fic_1998.txt", "db_fic_1999.txt", 
        "db_fic_2000.txt", "db_fic_2001.txt", "db_fic_2002.txt", 
        "db_fic_2003.txt", "db_fic_2004.txt", "db_fic_2005.txt", 
        "db_fic_2006.txt", "db_fic_2007.txt", "db_fic_2008.txt", 
        "db_fic_2009.txt", "db_fic_2010.txt", "db_fic_2011.txt", 
        "db_fic_2012.txt", "db_mag_1990.txt", "db_mag_1991.txt", 
        "db_mag_1992.txt", "db_mag_1993.txt", "db_mag_1994.txt", 
        "db_mag_1995.txt", "db_mag_1996.txt", "db_mag_1997.txt", 
        "db_mag_1998.txt", "db_mag_1999.txt", "db_mag_2000.txt", 
        "db_mag_2001.txt", "db_mag_2002.txt", "db_mag_2003.txt", 
        "db_mag_2004.txt", "db_mag_2005.txt", "db_mag_2006.txt", 
        "db_mag_2007.txt", "db_mag_2008.txt", "db_mag_2009.txt", 
        "db_mag_2010.txt", "db_mag_2011.txt", "db_mag_2012.txt", 
        "db_news_1990.txt", "db_news_1991.txt", "db_news_1992.txt", 
        "db_news_1993.txt", "db_news_1994.txt", "db_news_1995.txt", 
        "db_news_1996.txt", "db_news_1997.txt", "db_news_1998.txt", 
        "db_news_1999.txt", "db_news_2000.txt", "db_news_2001.txt", 
        "db_news_2002.txt", "db_news_2003.txt", "db_news_2004.txt", 
        "db_news_2005.txt", "db_news_2006.txt", "db_news_2007.txt", 
        "db_news_2008.txt", "db_news_2009.txt", "db_news_2010.txt", 
        "db_news_2011.txt", "db_news_2012.txt", "db_spok_1990.txt", 
        "db_spok_1991.txt", "db_spok_1992.txt", "db_spok_1993.txt", 
        "db_spok_1994.txt", "db_spok_1995.txt", "db_spok_1996.txt", 
        "db_spok_1997.txt", "db_spok_1998.txt", "db_spok_1999.txt", 
        "db_spok_2000.txt", "db_spok_2001.txt", "db_spok_2002.txt", 
        "db_spok_2003.txt", "db_spok_2004.txt", "db_spok_2005.txt", 
        "db_spok_2006.txt", "db_spok_2007.txt", "db_spok_2008.txt", 
        "db_spok_2009.txt", "db_spok_2010.txt", "db_spok_2011.txt", 
        "db_spok_2012.txt"]

    def __init__(self, gui=False, *args):
       # all corpus builders have to call the inherited __init__ function:
        super(COCABuilder, self).__init__(gui, *args)

        self.create_table_description(self.word_table,
            [Primary(self.word_id, "MEDIUMINT(8) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(43) NOT NULL"),
             Column(self.word_lemma, "TINYTEXT NOT NULL"),
             Column(self.word_pos, "VARCHAR(24) NOT NULL")])

        self.create_table_description(self.pos_table,
            [Primary(self.pos_id, "SMALLINT(4) UNSIGNED NOT NULL"),
             Column(self.pos_label, "VARCHAR(24)"),
             Column(self.pos_labelclean, "VARCHAR(24)")])
        
        self.create_table_description(self.file_table,
            [Primary(self.file_id, "SMALLINT(3) UNSIGNED NOT NULL"),
             Column(self.file_name, "ENUM('w_acad_1990.txt', 'w_acad_1991.txt', 'w_acad_1992.txt', 'w_acad_1993.txt', 'w_acad_1994.txt', 'w_acad_1995.txt', 'w_acad_1996.txt', 'w_acad_1997.txt', 'w_acad_1998.txt', 'w_acad_1999.txt', 'w_acad_2000.txt', 'w_acad_2001.txt', 'w_acad_2002.txt', 'w_acad_2003.txt', 'w_acad_2004.txt', 'w_acad_2005.txt', 'w_acad_2006.txt', 'w_acad_2007.txt', 'w_acad_2008.txt', 'w_acad_2009.txt', 'w_acad_2010.txt', 'w_acad_2011.txt', 'w_acad_2012.txt', 'w_fic_1990.txt', 'w_fic_1991.txt', 'w_fic_1992.txt', 'w_fic_1993.txt', 'w_fic_1994.txt', 'w_fic_1995.txt', 'w_fic_1996.txt', 'w_fic_1997.txt', 'w_fic_1998.txt', 'w_fic_1999.txt', 'w_fic_2000.txt', 'w_fic_2001.txt', 'w_fic_2002.txt', 'w_fic_2003.txt', 'w_fic_2004.txt', 'w_fic_2005.txt', 'w_fic_2006.txt', 'w_fic_2007.txt', 'w_fic_2008.txt', 'w_fic_2009.txt', 'w_fic_2010.txt', 'w_fic_2011.txt', 'w_fic_2012.txt', 'w_mag_1990.txt', 'w_mag_1991.txt', 'w_mag_1992.txt', 'w_mag_1993.txt', 'w_mag_1994.txt', 'w_mag_1995.txt', 'w_mag_1996.txt', 'w_mag_1997.txt', 'w_mag_1998.txt', 'w_mag_1999.txt', 'w_mag_2000.txt', 'w_mag_2001.txt', 'w_mag_2002.txt', 'w_mag_2003.txt', 'w_mag_2004.txt', 'w_mag_2005.txt', 'w_mag_2006.txt', 'w_mag_2007.txt', 'w_mag_2008.txt', 'w_mag_2009.txt', 'w_mag_2010.txt', 'w_mag_2011.txt', 'w_mag_2012.txt', 'w_news_1990.txt', 'w_news_1991.txt', 'w_news_1992.txt', 'w_news_1993.txt', 'w_news_1994.txt', 'w_news_1995.txt', 'w_news_1996.txt', 'w_news_1997.txt', 'w_news_1998.txt', 'w_news_1999.txt', 'w_news_2000.txt', 'w_news_2001.txt', 'w_news_2002.txt', 'w_news_2003.txt', 'w_news_2004.txt', 'w_news_2005.txt', 'w_news_2006.txt', 'w_news_2007.txt', 'w_news_2008.txt', 'w_news_2009.txt', 'w_news_2010.txt', 'w_news_2011.txt', 'w_news_2012.txt', 'w_spok_1990.txt', 'w_spok_1991.txt', 'w_spok_1992.txt', 'w_spok_1993.txt', 'w_spok_1994.txt', 'w_spok_1995.txt', 'w_spok_1996.txt', 'w_spok_1997.txt', 'w_spok_1998.txt', 'w_spok_1999.txt', 'w_spok_2000.txt', 'w_spok_2001.txt', 'w_spok_2002.txt', 'w_spok_2003.txt', 'w_spok_2004.txt', 'w_spok_2005.txt', 'w_spok_2006.txt', 'w_spok_2007.txt', 'w_spok_2008.txt', 'w_spok_2009.txt', 'w_spok_2010.txt', 'w_spok_2011.txt', 'w_spok_2012.txt') NOT NULL"),
             Column(self.file_path, "TINYTEXT NOT NULL")])

        self.create_table_description(self.subgenre_table,
            [Primary(self.subgenre_id, "ENUM('0','101','102','103','104','105','106','107','108','109','114','115','116','117','118','123','124','125','126','127','128','129','130','131','132','133','135','136','137','138','139','140','141','142','144','145','146','147','148','149','150','151','152') NOT NULL"),
             Column(self.subgenre_label, "ENUM('ACAD:Education','ACAD:Geog/SocSci','ACAD:History','ACAD:Humanities','ACAD:Law/PolSci','ACAD:Medicine','ACAD:Misc','ACAD:Phil/Rel','ACAD:Sci/Tech','FIC:Gen (Book)','FIC:Gen (Jrnl)','FIC:Juvenile','FIC:Movies','FIC:SciFi/Fant','MAG:Afric-Amer','MAG:Children','MAG:Entertain','MAG:Financial','MAG:Home/Health','MAG:News/Opin','MAG:Religion','MAG:Sci/Tech','MAG:Soc/Arts','MAG:Sports','MAG:Women/Men','NEWS:Editorial','NEWS:Life','NEWS:Misc','NEWS:Money','NEWS:News_Intl','NEWS:News_Local','NEWS:News_Natl','NEWS:Sports','SPOK:ABC','SPOK:CBS','SPOK:CNN','SPOK:FOX','SPOK:Indep','SPOK:MSNBC','SPOK:NBC','SPOK:NPR','SPOK:PBS') NOT NULL")])

        self.create_table_description(self.source_table,
            [Primary(self.source_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.source_year, "ENUM('1990','1991','1992','1993','1994','1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012') NOT NULL"),
             Column(self.source_genre, "ENUM('ACAD','FIC','MAG','NEWS','SPOK') NOT NULL"),
             Link(self.source_subgenre_id, self.subgenre_table),
             Column(self.source_label, "TINYTEXT NOT NULL"),
             Column(self.source_title, "TINYTEXT NOT NULL")])
            
        self.create_table_description(self.corpus_table,
            [Primary(self.corpus_id, "INT(9) UNSIGNED NOT NULL"),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_pos_id, self.pos_table),
             Link(self.corpus_source_id, self.source_table)])

        self.add_time_feature(self.source_year)
    
    @staticmethod
    def get_file_list(path, file_filter):
        L = []
        for source_path, folders, files in os.walk(path):
            for current_file in files:
                full_name = os.path.join(source_path, current_file)
                if not file_filter or fnmatch.fnmatch(current_file, file_filter) or current_file in (["coca-sources.txt", "lexicon.txt", "Sub-genre codes.txt"]):
                    L.append(full_name)
        return L
        
    @staticmethod
    def get_name():
        return "COCA"

    @staticmethod
    def get_db_name():
        return "coca"
    
    @staticmethod
    def get_title():
        return "Corpus of Contemporary American English"
        
    @staticmethod
    def get_description():
        return [
            "The Corpus of Contemporary American English (COCA) is the largest freely-available corpus of English, and the only large and balanced corpus of American English. The corpus was created by Mark Davies of Brigham Young University, and it is used by tens of thousands of users every month (linguists, teachers, translators, and other researchers). COCA is also related to other large corpora that we have created.",
            "The corpus contains more than 450 million words of text and is equally divided among spoken, fiction, popular magazines, newspapers, and academic texts. It includes 20 million words each year from 1990-2012 and the corpus is also updated regularly (the most recent texts are from Summer 2012). Because of its design, it is perhaps the only corpus of English that is suitable for looking at current, ongoing changes in the language (see the 2011 article in Literary and Linguistic Computing)."]

    @staticmethod
    def get_references():
        return ["Davies, Mark. (2008-) <i>The Corpus of Contemporary American English: 450 million words, 1990-present</i>. Available online at http://corpus.byu.edu/coca/"]

    @staticmethod
    def get_url():
        return "http://corpus.byu.edu/coca/"

    @staticmethod
    def get_license():
        return "Commercial license"

    @staticmethod
    def validate_files(l):
        found_list = [x for x in [os.path.basename(y) for y in l] if x.lower() in [y.lower() for y in BuilderClass.expected_files]]
        if len(found_list) < len(BuilderClass.expected_files):
            missing_list = [x for x in BuilderClass.expected_files if x.lower() not in [y.lower() for y in found_list]]
            sample = "<br/>".join(missing_list[:5])
            if len(missing_list) > 6:
                sample = "{}</code>, and {} other files".format(sample, len(missing_list) - 3)
            elif len(missing_list) == 6:
                sample = "<br/>".join(missing_list[:6])
            raise RuntimeError("<p>Not all expected corpora files were found in the specified corpus data directory. Missing files are:</p><p><code>{}</code></p>".format(sample))

    def build_load_files(self):
        files = self.get_file_list(self.arguments.path, self.file_filter)
        for file_name in (["coca-sources.txt", "lexicon.txt", "Sub-genre codes.txt"]):
            print("Load file {}".format(file_name))
            for x in files:
                if os.path.basename(x) == file_name:
                    file_path = x
                    break
            else:
                raise RuntimeError("File '{}' not found.".format(file_name))
            try:
                self.Con.load_infile(file_path, self.word_table, "LINES TERMINATED BY '\\r\\n' IGNORE 2 LINES")
            except dbconnection.mysql.OperationalError as e:
                raise RuntimeError("""
                    <p><b>The file '{}' could not be loaded into the database.</b></p>
                    <p>While attempting to load the file into the database, the 
                    following error occurred:</p>
                    <p><code>{}</code></p>
                    <p>One possible cause of this error is that your MySQL 
                    database server is not configured to allow LOCAL INFILE 
                    loading of data files. Please ask the administrator of 
                    your MySQL server to ensure that the option 
                    <code>local-infile=1</code> is set in the <code>[mysql]</code>
                    section of the server configuration file.</p>
                    """.format(file_name, e))
            
        print("Process corpus files")
        super(COCABuilder, self).build_load_files()

    def process_file(self, filename):
        print(filename)
        #file_body = False
        ## read file using the specified encoding (default is 'utf-8), and 
        ## retry using 'ISO-8859-1'/'latin-1' in case of an error:
        #try:
            #with codecs.open(filename, "r", encoding=self.arguments.encoding) as input_file:
                #input_data = input_file.read()
        #except UnicodeDecodeError:
            #with codecs.open(filename, "r", encoding="ISO-8859-1") as input_file:
                #input_data = input_file.read()
                
        #input_data = [x.strip() for x in input_data.splitlines() if x.strip()]
        #for row in input_data:
            #while "  " in row:
                #row = row.replace("  ", " ")
            ## only process the lines after the hash mark:
            #if row == "#":
                #file_body = True
            #elif file_body:
                #try:
                    #self._value_corpus_time, _, remain = row.partition(" ")
                    #_, _, value = remain.partition(" ")
                #except ValueError:
                    #continue

                #try:
                    #(self._value_word_label, 
                    #self._value_word_lemmatranscript, 
                    #self._value_word_transcript, 
                    #self._value_word_pos) = value.split("; ")
                #except ValueError:
                    #continue

                #if float(self._value_corpus_time) >= 0:
                    #self._word_id = self.table(self.word_table).get_or_insert(
                        #{self.word_label: self._value_word_label, 
                            #self.word_pos: self._value_word_pos,
                            #self.word_transcript: self._value_word_transcript,
                            #self.word_lemmatranscript: self._value_word_lemmatranscript})
                    
                    #self.add_token_to_corpus(
                        #{self.corpus_word_id: self._word_id, 
                        #self.corpus_file_id: self._file_id,
                        #self.corpus_time: self._value_corpus_time})
BuilderClass = COCABuilder

if __name__ == "__main__":
    COCABuilder().build()
