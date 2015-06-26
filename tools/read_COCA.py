
from __future__ import unicode_literals 

import MySQLdb

import os, os.path
import glob
import logging
import sys
import progressbar
import getopt


from lxml import etree


EXPERIMENTAL = True

DataPath = "/usr/local/share/COCA/db/data/"
#Filter = "db_acad_1991.txt"
Filter = "new_db_*.txt"

InfoLevel = logging.INFO

Verbose = False
DryRun = True


# Format for index specifications:
# IndexName: ([Column1, Column2, ...], Length, "HASH"|"BTREE")
# Length is used for TEXT columns

IndicesStage = {
    "pos": {
        "PosId": (["PosId"], 0, "HASH"),
        "PoS" : (["PoS"], 0, "BTREE"),
        "PoSClean" : (["PosClean"], 0, "BTREE")
    },
    "lexicon": {
        "PosId": (["PosId"], 0, "HASH"),
        "Word": (["Word"], 0, "BTREE"),
        "Lemma": (["Lemma"], 13, "BTREE"),
    },
    "corpus": {
        #"TokenId": (["TokenId"], 0, "HASH"),
        "WordId": (["WordId"], 0, "HASH"),
        "TextId": (["TextId"], 0, "HASH"),
        "PosId": (["PosId"], 0, "HASH")
    },

    "corpusBig": {
        #"TokenId": (["TokenId"], 0, "HASH"),
        "TextId": (["TextId"], 0, "HASH"),
        "Genre": (["Genre"], 0, "BTREE"),
        "Year": (["Year"], 0, "BTREE"),
        "W1": (["W1"], 0, "HASH"),                         # COCA: *
        "P1": (["P1"], 0, "HASH"),                         # COCA: [n*]
        "W1_W2": (["W1", "W2"], 0, "HASH"),                   # COCA: * *
        "P1_W2": (["P1", "W2"], 0, "HASH"),                   # COCA: [n*] *
        "W1_P2": (["W1", "P2"], 0, "HASH"),                   # COCA: * [n*]
        "P1_P2": (["P1", "P2"], 0, "HASH"),                   # COCA: [n*] [n*]
        "W1_W2_W3": (["W1", "W2", "W3"], 0, "HASH"),             # COCA: * * * 
        "P1_W2_W3": (["P1", "W2", "W3"], 0, "HASH"),             # COCA: [n*] * *
        "W1_P2_W3": (["W1", "P2", "W3"], 0, "HASH"),             # COCA: * [n*] *
        "P1_P2_W3": (["P1", "P2", "W3"], 0, "HASH"),             # COCA: [n*] [n*] *
        "W1_W2_P3": (["W1", "W2", "P3"], 0, "HASH"),             # COCA: * * [n*]
        "P1_W2_P3": (["P1", "W2", "P3"], 0, "HASH"),             # COCA: [n*] * [n*]
        "W1_P2_P3": (["W1", "P2", "P3"], 0, "HASH"),             # COCA: * [n*] [n*]
        "P1_P2_P3": (["P1", "P2", "P3"], 0, "HASH")             # COCA: [n*] [n*] [n*]
    }
}

if EXPERIMENTAL:
    IndicesStage["corpusBig2"] = {
        "TextId": (["TextId"], 0, "HASH"),
        "Genre": (["Genre"], 0, "BTREE"),
        "Year": (["Year"], 0, "BTREE"),
        "W1": (["W1"], 0, "HASH"),                         # COCA: *
        "W1_W2": (["W1", "W2"], 0, "HASH"),                   # COCA: * *
        "W1_W2_W3": (["W1", "W2", "W3"], 0, "HASH"),             # COCA: * * * 
    }

#show index_statistics;
#+--------------+------------+------------+-----------+
#| Table_schema | Table_name | Index_name | Rows_read |
#+--------------+------------+------------+-----------+
#| coca_maria   | corpus     | WordId     |      8033 |
#| coca_maria   | lexicon    | Word       |     60534 |
#| coca_maria   | corpusBig  | W1_W2_W3   |     33833 |
#| coca_maria   | pos        | PoS        |     33612 |
#| coca_maria   | corpusBig  | P1_W2_P3   |   1363363 |
#| coca_maria   | pos        | PRIMARY    |     17478 |
#| coca_maria   | lexicon    | PRIMARY    |     34088 |
#| coca_maria   | corpusBig  | W1_W2      |    703450 |
#| coca_maria   | corpusBig  | P1_W2_W3   |       188 |
#| coca_maria   | corpus     | PRIMARY    |    130532 |
#| coca_maria   | corpusBig  | PRIMARY    |        25 |
#| coca_maria   | corpusBig  | W1_W2_P3   |  12601223 |
#+--------------+------------+------------+-----------+

TableDescription = {
    "sources": {
        "Create": """
            `TextId` MEDIUMINT(7) UNSIGNED NOT NULL,
            `Year` ENUM('1990','1991','1992','1993','1994','1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012') NOT NULL,
            `Genre` ENUM('ACAD','FIC','MAG','NEWS','SPOK') NOT NULL,
            `SubGenreId` ENUM('0','101','102','103','104','105','106','107','108','109','114','115','116','117','118','123','124','125','126','127','128','129','130','131','132','133','135','136','137','138','139','140','141','142','144','145','146','147','148','149','150','151','152') NOT NULL,
            `Source` TINYTEXT NOT NULL,
            `Title` TINYTEXT NOT NULL,
            PRIMARY KEY (`TextID`)""", 
        "Source": {
            "File": "coca-sources.txt",
            "Args": "LINES TERMINATED BY '\\r\\n' IGNORE 2 LINES"}
        },
    "subgenres": {
        "Create": """
            `SubGenreId` ENUM('0','101','102','103','104','105','106','107','108','109','114','115','116','117','118','123','124','125','126','127','128','129','130','131','132','133','135','136','137','138','139','140','141','142','144','145','146','147','148','149','150','151','152') NOT NULL,
            `SubGenreName` ENUM('ACAD:Education','ACAD:Geog/SocSci','ACAD:History','ACAD:Humanities','ACAD:Law/PolSci','ACAD:Medicine','ACAD:Misc','ACAD:Phil/Rel','ACAD:Sci/Tech','FIC:Gen (Book)','FIC:Gen (Jrnl)','FIC:Juvenile','FIC:Movies','FIC:SciFi/Fant','MAG:Afric-Amer','MAG:Children','MAG:Entertain','MAG:Financial','MAG:Home/Health','MAG:News/Opin','MAG:Religion','MAG:Sci/Tech','MAG:Soc/Arts','MAG:Sports','MAG:Women/Men','NEWS:Editorial','NEWS:Life','NEWS:Misc','NEWS:Money','NEWS:News_Intl','NEWS:News_Local','NEWS:News_Natl','NEWS:Sports','SPOK:ABC','SPOK:CBS','SPOK:CNN','SPOK:FOX','SPOK:Indep','SPOK:MSNBC','SPOK:NBC','SPOK:NPR','SPOK:PBS') NOT NULL,
            PRIMARY KEY (`SubGenreId`)""",
        "Source": {
            "File": "Sub-genre codes.txt",
            "Args": "LINES TERMINATED BY '\\r\\n'" }
        },
    "lexicon": {
        "Create": """
            `WordId` MEDIUMINT(7) UNSIGNED NOT NULL,
            `Word` VARCHAR(43) NOT NULL,
            `Lemma` TINYTEXT NOT NULL,
            `PosId` SMALLINT(4) UNSIGNED NOT NULL,
            `Frequency` INT(8) UNSIGNED NOT NULL,
            PRIMARY KEY (`WordId`)""",
        "Source": {
            "File": "new_lexicon.txt",
            "Args": ""}
        },
    "pos": {
        "Create" : """
            `PosId` SMALLINT(4) UNSIGNED NOT NULL AUTO_INCREMENT, 
            `PoS` VARCHAR (24)
            PRIMARY KEY (`PosId`)""",
        "Source": {
            "File": "pos.txt",
            "Args": "LINES TERMINATED BY '\\r\\n'"},
        },
    "files": {
        "Create" : """
            `Filename` VARCHAR (20), 
            PRIMARY KEY (`Filename`)""" },
    "corpus": {
        "Create" : """
            `TextId` MEDIUMINT(7) UNSIGNED NOT NULL,
            `TokenId` INT(9) UNSIGNED NOT NULL,
            `WordId` MEDIUMINT(7) UNSIGNED NOT NULL,
            `PosId` SMALLINT(4) UNSIGNED NOT NULL,
            PRIMARY KEY (`TokenId`)""" },
    "corpusBig": {
        "Create": """
        `TokenId` INT(9) UNSIGNED NOT NULL,
        `TextId` MEDIUMINT(7) UNSIGNED NOT NULL,
        `Genre` ENUM('ACAD','FIC','MAG','NEWS','SPOK') NOT NULL,
        `Year` ENUM('1990','1991','1992','1993','1994','1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012') NOT NULL,
        `W1` MEDIUMINT(7) UNSIGNED NOT NULL,
        `P1` SMALLINT UNSIGNED NOT NULL,
        `W2` MEDIUMINT UNSIGNED NOT NULL,
        `P2` SMALLINT UNSIGNED NOT NULL,
        `W3` MEDIUMINT UNSIGNED NOT NULL,
        `P3` SMALLINT UNSIGNED NOT NULL,
        `W4` MEDIUMINT UNSIGNED NOT NULL,
        `P4` SMALLINT UNSIGNED NOT NULL,
        `W5` MEDIUMINT UNSIGNED NOT NULL,
        `P5` SMALLINT UNSIGNED NOT NULL,
        `W6` MEDIUMINT UNSIGNED NOT NULL,
        `P6` SMALLINT UNSIGNED NOT NULL,
        `W7` MEDIUMINT UNSIGNED NOT NULL,
        `P7` SMALLINT UNSIGNED NOT NULL,
        PRIMARY KEY (`TokenId`)""" }
    }


## create lexicon with pos as string:

#SET autocommit=0;
#SET unique_checks=0;
#SET foreign_key_checks=0;

#CREATE TABLE `lex` (
    #`WordId` MEDIUMINT(8) UNSIGNED NOT NULL,
    #`Word` VARCHAR(43) NOT NULL,
    #`Lemma` TINYTEXT NOT NULL,
    #`PoS` TINYTEXT NOT NULL,
    #PRIMARY KEY (`WordId`)
    #);

#LOAD DATA LOCAL INFILE '/usr/local/share/COCA/db/data/lexicon.txt' INTO TABLE lex CHARACTER SET 'latin1' LINES TERMINATED BY '\r\n' IGNORE 2 LINES;

#CREATE INDEX Word ON lex(Word(20));
#CREATE INDEX Lemma ON lex(Lemma(18));
#CREATE INDEX PoS ON lex(PoS(15));


if EXPERIMENTAL:
    TableDescription["corpusBig2"] = {
        "Create": """
        `TokenId` INT(9) UNSIGNED NOT NULL,
        `TextId` MEDIUMINT(7) UNSIGNED NOT NULL,
        `Genre` ENUM('ACAD','FIC','MAG','NEWS','SPOK') NOT NULL,
        `Year` ENUM('1990','1991','1992','1993','1994','1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012') NOT NULL,
        `W1` MEDIUMINT UNSIGNED NOT NULL,
        `W2` MEDIUMINT UNSIGNED NOT NULL,
        `W3` MEDIUMINT UNSIGNED NOT NULL,
        `W4` MEDIUMINT UNSIGNED NOT NULL,
        `W5` MEDIUMINT UNSIGNED NOT NULL,
        `W6` MEDIUMINT UNSIGNED NOT NULL,
        `W7` MEDIUMINT UNSIGNED NOT NULL,
        PRIMARY KEY (`TokenId`)""" }

def Execute (Cur, S, Internal = False):
    S = S.strip ()
    Command = S.partition (" ") [0].upper ()
    if Command in ["ALTER", "CREATE", "DELETE", "DROP", "INSERT", "LOAD", "UPDATE", "OPTIMIZE"]:
        Modify = True
    elif Command in ["SELECT", "SHOW", "SET"]:
        Modify = False
    else:
        ToLog ("Command '%s' not categorized, assuming modifying commannd" % Command, logging.warning)
        Modify = True
    try:
        if Verbose:
            if not Internal:
                ToLog (S, logging.info)
        if Modify:
            if not DryRun:
                Cur.execute (S)
        else:
            Cur.execute (S)
    except MySQLdb.OperationalError as e:
        ToLog (e [1], logging.error)

def Commit (Con):
    if not DryRun:
        Con.commit ()
        
def Rollback (Con):
    if not DryRun:
        Con.rollback ()

def ToLog (Text, Level=logging.info):
    global Stage
    if Verbose:
        print "[%s]: %s" % (Stage, Text)
    Level ("[%s]: %s" % (Stage, Text))

def Options (argv):
    def Help():
        print "read_mysql.py [-h] [-v] [-w]\n"
        print "-h   Print this information."
        print "-v   Produce verbose output."
        print "-w   Actually do something; default behaviour is simulation."
        print
    global Verbose
    global DryRun
    try:
        opts, args = getopt.getopt (argv, "hvw")
    except getopt.GetoptError:
        Help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            Help()
            sys.exit()
        elif opt == "-v":
            Verbose = True
        elif opt == "-w":
            Reply = raw_input("""
You have indicated that you want all modifications to be written to the
database. These changes will consume an enormous amount of time, and possibly
also of disk space.

Type Y if you really want to the modifications to be written. Type n for a 
dry-run during which no modifications are written. [Yn] """)
            if Reply == "Y":
                DryRun = False
                print "\nThe changes will be written to the database.\n"
            else:
                print "\nThe changes will not be written to the database.\n"

def HasTable (Table):
    Execute (Cur, "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'coca_maria' AND table_name = '%s'" % Table, Internal=True)
    Results = Cur.fetchall ()
    return Results [0] [0]

def HasColumn (Table, Column):
    Execute (Cur, "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = 'coca_maria' AND TABLE_NAME = '%s' and COLUMN_NAME = '%s'" % (Table, Column), Internal=True)
    Results = Cur.fetchall ()
    return Results [0] [0]

def GetMax (Table, Column):
    Execute (Cur, "SELECT MAX(%s) FROM %s" % (Column, Table), True);
    return list (Cur.fetchall ()) [0] [0]

def GetMin (Table, Column):
    Execute (Cur, "SELECT MIN(%s) FROM %s" % (Column, Table), True);
    return list (Cur.fetchall ()) [0] [0]

def CreateIndex (Indices):
    for CurrentTable in Indices:
        try:
            Execute (Cur, "SHOW INDEX FROM %s" % CurrentTable, True);
        except (MySQLdb.OperationalError, MySQLdb.ProgrammingError) as e:
            ToLog (e [1], logging.error)
            
        FoundIndices = list (Cur.fetchall ())
        
        RequestedIndices = Indices [CurrentTable]
        
        for CurrentIndex in FoundIndices:
            if CurrentIndex [2] in RequestedIndices:
                RequestedIndices.pop (CurrentIndex [2])

        for CurrentIndex in RequestedIndices:
            Columns, Length, Type = RequestedIndices [CurrentIndex]
            ToLog ("Creating index '%s' %s on '%s'" % (CurrentIndex, Columns, CurrentTable), logging.info)
            try:
                if Length:
                    ExecuteString = "CREATE INDEX %s ON %s(%s(%s))" % (CurrentIndex, CurrentTable, ", ".join(Columns), Length)
                else:
                    ExecuteString = "CREATE INDEX %s ON %s(%s) USING %s" % (CurrentIndex, CurrentTable, ", ".join(Columns), Type)
                Execute (Cur, ExecuteString)
            except MySQLdb.OperationalError as e:
                ToLog (e [1], logging.error)
            Commit (Con)
   
if __name__ == "__main__":
    Options (sys.argv [1:])

    try:
        Con = MySQLdb.connect (host="localhost", port=3306, user="mysql", passwd="mysql", db="coca_maria", local_infile=1)
    except:
        print "Could not connect to data base %s@%s:%s.\nPerhaps the server is not running?" % ("coca_maria", "localhost", "3306")
        print "To check the server status under OpenSUSE, type:"
        print "\nsudo rcmysql status\n"
        print "Aborting."
        sys.exit (2)

    
    Cur = Con.cursor()
    
    logging.basicConfig(filename='coca_maria_db.log', format="%(asctime)s %(levelname)s %(message)s", level=InfoLevel)


    Stage = "initializing"
    if DryRun:
        ToLog ("--- Starting (dry run) ---", logging.info)
    else:
        ToLog ("--- Starting ---", logging.info)
        Execute (Cur, "SET autocommit=0")
        Execute (Cur, "SET unique_checks=0")
        Execute (Cur, "SET foreign_key_checks=0")
        
    Stage = "creating"
    
    for CurrentTable in TableDescription:
        if not HasTable (CurrentTable):
            ToLog ("New table '%s'" % CurrentTable, logging.info)
            Execute (Cur, "CREATE TABLE %s (%s)" % (CurrentTable, TableDescription [CurrentTable] ["Create"]))
            try:
                Source = TableDescription [CurrentTable] ["Source"]
                Execute (Cur, "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s %s" % 
                         (os.path.join (DataPath, Source ["File"]), CurrentTable, Source ["Args"]))
            except KeyError:
                pass
            except MySQLdb.OperationalError as e:
                ToLog (e [1], logging.error)
          
    Commit (Con)

    ## Create PosId instead of PoS in lexicon, if necessary:
    #if HasColumn ('lexicon', 'PoS'):
        ## Populate pos:
        #ToLog ("populating 'pos'", logging.info)
        #Execute (Cur, "INSERT INTO pos (PoS) SELECT DISTINCT(PoS) from lexicon")
        #ToLog ("Indexing 'pos'", logging.info)
        #Execute (Cur, "CREATE INDEX PoS ON pos (PoS)")
        #Execute (Cur, "CREATE INDEX PosId ON pos (PosId)")
        
        ## UPDATE lexicon.PosId with values from pos:
        #Execute (Cur, """
            #UPDATE lexicon l 
                #JOIN pos AS p ON l.PoS = p.PoS
                #SET l.PosId = p.PosId""")
        #Execute (Cur, "ALTER TABLE lexicon DROP PoS")
        #OptimizeLexicon = True

    # Create PoSClean in lexicon, if necessary:
    if not HasColumn ('pos', 'PoSClean'):
        ToLog ("creating 'PoSClean'", logging.info)
        Execute (Cur, "ALTER TABLE pos ADD PoSClean VARCHAR(24)") 
        Execute (Cur, "UPDATE pos SET PoSClean = REPLACE(PoS, '@', '')")
        Execute (Cur, "UPDATE pos SET PoSClean = REPLACE(PoSClean, '%', '')")

    Stage = "inserting"
    Execute (Cur, "SELECT * FROM files", True)
    Files = list (Cur.fetchall ())
    ExistingFiles = []
    for CurrentFile in Files:
        ExistingFiles.append (os.path.join (DataPath, CurrentFile [0]))

    Files = []
    FileNameList = glob.glob (os.path.join (DataPath, Filter))
    for CurrentFile in FileNameList:
        if not CurrentFile in ExistingFiles:
            Files.append (CurrentFile)
    FileNameList = Files

    # INSERT text files:
    if FileNameList:
        ToLog ("%s files to be loaded." % len (FileNameList), logging.info)

        if not Verbose:
            ProgressBar = progressbar.ProgressBar (len (FileNameList))
        
        for CurrentFile in FileNameList:
            Path, FileName = os.path.split (CurrentFile)
            ToLog ("Loading file %s" %FileName, logging.info)
            try:
                Execute (Cur, "LOAD DATA LOCAL INFILE '%s' INTO TABLE corpus (TextId, TokenId, WordId, PosId)" % CurrentFile)
                Execute (Cur, "INSERT INTO files VALUES('%s')" % FileName)
                Commit (Con)
            except StandardError as e:
                ToLog (e, logging.warning)
                Rollback (Con)
            if not Verbose:
                ProgressBar.Update ()



    #if GetMax("corpus", "PosId") <> GetMax("lexicon", "PosId"):
        #Stage = "corpus"
        #ToLog ("Creating WordId indices", logging.info)
        #Execute (Cur, "CREATE INDEX WordId ON corpus(WordId)")
        #Execute (Cur, "CREATE INDEX WordId ON lexicon(WordId)")
        #ToLog("Creating PosId", logging.info)
        #Execute (Cur, "UPDATE corpus c JOIN lexicon AS l ON c.WordId = l.WordId SET c.PosId = l.PosId")
        #Commit (Con)

    if HasTable ("corpusBig"):
        Stage = "corpusBig"

        MaxTokenCOCA = GetMax ("corpus", "TokenId")
        MaxTokenBig = GetMax ("corpusBig", "TokenId")
        if not MaxTokenBig:
            MaxTokenBig = 0

        ToLog ("Maximum TokenId: %s" % MaxTokenBig, logging.info)
        if MaxTokenBig < MaxTokenCOCA - 8:
            CurrentTokenId = MaxTokenBig
            Iterations = (MaxTokenCOCA - CurrentTokenId) // 1000 + 1
            if not Verbose:
                ProgressBar = progressbar.ProgressBar (Iterations)
            ToLog ("Inserting data, %s iterations" % Iterations, logging.info)
        
            while CurrentTokenId <= MaxTokenCOCA:
                MinToken = CurrentTokenId
                MaxToken = CurrentTokenId + 999
                #ToLog ("Inserting tokens %s to %s" % (MinToken, MaxToken), logging.info)
                ExecuteString = """
                    INSERT corpusBig (TokenId, TextId, Genre, Year, 
                        W1, W2, W3, W4, W5, W6, W7, 
                        P1, P2, P3, P4, P5, P6, P7)
                    SELECT a.TokenId, a.TextId, s.Genre, s.Year, 
                        a.WordId, b.WordId, c.WordId, d.WordId, e.WordId, f.WordId, g.WordId, a.PosId, b.PosId, c.PosId, d.PosId, e.PosId, f.PosId, g.PosId
                    FROM corpus AS a, 
                        corpus AS b, 
                        corpus AS c, 
                        corpus AS d, 
                        corpus AS e, 
                        corpus AS f, 
                        corpus AS g, 
                        sources as s
                    WHERE """ + "a.TokenId >= %s AND a.TokenId <= %s AND " % (MinToken, MaxToken) + """a.TokenId + 1 = b.TokenId AND
                    a.TokenId + 2 = c.TokenId AND
                    a.TokenId + 3 = d.TokenId AND
                    a.TokenId + 4 = e.TokenId AND
                    a.TokenId + 5 = f.TokenId AND
                    a.TokenId + 6 = g.TokenId AND
                    a.TextId = s.Textid
                    ORDER BY a.TokenId ASC"""

                Execute (Cur, ExecuteString)
                Commit (Con)
                if not Verbose:
                    ProgressBar.Update ()
                CurrentTokenId += 1000
    else:
        ToLog ("Table 'corpusBig' does not exist, skipping.", logging.info)

    if HasTable ("corpusBig2") and EXPERIMENTAL:
        Stage = "corpusBig2"

        MaxTokenCOCA = GetMax ("corpus", "TokenId")
        MaxTokenBig = GetMax ("corpusBig2", "TokenId")
        if not MaxTokenBig:
            MaxTokenBig = 0

        ToLog ("Maximum TokenId: %s" % MaxTokenBig, logging.info)
        if MaxTokenBig < MaxTokenCOCA - 8:
            CurrentTokenId = MaxTokenBig
            Iterations = (MaxTokenCOCA - CurrentTokenId) // 1000 + 1
            if not Verbose:
                ProgressBar = progressbar.ProgressBar (Iterations)
            ToLog ("Inserting data, %s iterations" % Iterations, logging.info)
        
            while CurrentTokenId <= MaxTokenCOCA:
                MinToken = CurrentTokenId
                MaxToken = CurrentTokenId + 999
                #ToLog ("Inserting tokens %s to %s" % (MinToken, MaxToken), logging.info)
                ExecuteString = """
                    INSERT corpusBig2 (TokenId, TextId, Genre, Year, 
                        W1, W2, W3, W4, W5, W6, W7)
                    SELECT a.TokenId, a.TextId, s.Genre, s.Year, 
                        a.WordId, b.WordId, c.WordId, d.WordId, e.WordId, f.WordId, g.WordId
                    FROM corpus AS a, 
                        corpus AS b, 
                        corpus AS c, 
                        corpus AS d, 
                        corpus AS e, 
                        corpus AS f, 
                        corpus AS g, 
                        sources as s
                    WHERE """ + "a.TokenId >= %s AND a.TokenId <= %s AND " % (MinToken, MaxToken) + """a.TokenId + 1 = b.TokenId AND
                    a.TokenId + 2 = c.TokenId AND
                    a.TokenId + 3 = d.TokenId AND
                    a.TokenId + 4 = e.TokenId AND
                    a.TokenId + 5 = f.TokenId AND
                    a.TokenId + 6 = g.TokenId AND
                    a.TextId = s.Textid
                    ORDER BY a.TokenId ASC"""

                Execute (Cur, ExecuteString)
                Commit (Con)
                if not Verbose:
                    ProgressBar.Update ()
                CurrentTokenId += 1000
    else:
        ToLog ("Table 'corpusBig2' does not exist, skipping.", logging.info)

    Stage = "indexing"
    CreateIndex (IndicesStage)

    #if not GetMax ("lexicon", "Frequency"):
        #ToLog ("Populating Frequency in 'lexicon'")
        #if not Verbose and not DryRun:
            #ProgressBar = progressbar.ProgressBar (GetMax ("lexicon", "WordId"))
        #for i in range (GetMax ("lexicon", "WordId")):
            #if not DryRun:
                #Execute (Cur, "SELECT COUNT(*) FROM corpus WHERE corpus.WordId = %s" % i)
                #Value = Cur.fetchall () [0] [0]
                #Execute (Cur, "UPDATE lexicon SET Frequency = %s WHERE lexicon.WordId = %s" % (Value, i))
                #if not Verbose:
                    #ProgressBar.Update()
        #OptimizeLexicon = True

    ##if OptimizeLexicon:
        ##ToLog ("optimizing 'lexicon'", logging.info)
        ##Execute (Cur, "OPTIMIZE TABLE lexicon")

    Stage = "finalizing"
    Commit (Con)

    ToLog ("--- Finished. ---", logging.info)


""" 

SELECT PosId FROM lexicon, pos WHERE PosId IN (12667, 24999, 57872, 106154, 252939, 302905, 539712, 835196) AND lexicon.PoS = pos.POS;


"""