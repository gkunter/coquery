# -*- coding: utf-8 -*-

"""
coq_install_obc2.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from coquery.corpusbuilder import TEICorpusBuilder, ET
from coquery.tables import Column, Identifier, Link


class BuilderClass(TEICorpusBuilder):
    file_filter = "*.*"

    word_table = "Lexicon"
    word_id = "WordId"
    word_label = "Word"
    word_pos = "POS"
    word_columns = [
        Identifier(word_id, "MEDIUMINT(5) UNSIGNED NOT NULL"),
        Column(word_label, "VARCHAR(33) NOT NULL"),
        Column(word_pos, "VARCHAR(7) NOT NULL")]

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"
    file_columns = [
        Identifier(file_id, "SMALLINT(5) UNSIGNED NOT NULL"),
        Column(file_name, "VARCHAR(21) NOT NULL"),
        Column(file_path, "VARCHAR(2048) NOT NULL")]

    speaker_table = "Speakers"
    speaker_id = "SpeakerId"
    speaker_label = "Speaker"
    speaker_sex = "Sex"
    speaker_age = "Age"
    speaker_role = "Role"
    speaker_hiscolabel = "HISCO_Occupation"
    speaker_hisclass = "HISCLASS"
    speaker_class = "Class"

    speaker_columns = [
        Identifier(speaker_id, "MEDIUMINT(4) UNSIGNED NOT NULL"),
        Column(speaker_label, "VARCHAR(15) NOT NULL"),
        Column(speaker_sex, "ENUM('m','f','?') NOT NULL"),
        Column(speaker_age, "VARCHAR(6) NOT NULL"),
        Column(speaker_role, "VARCHAR(20) NOT NULL"),
        Column(speaker_hiscolabel, "VARCHAR(135) NOT NULL"),
        Column(speaker_hisclass, "TINYINT UNSIGNED"),
        Column(speaker_class,
               "ENUM('?','upper (1-5)','lower (6-13)') NOT NULL")]

    event_table = "Event"
    event_id = "EventId"
    event_label = "Event"
    event_scribe = "Scribe"
    event_publisher = "Publisher"
    event_printer = "Printer"
    event_length = "Length"
    event_columns = [
        Identifier(event_id, "MEDIUMINT(13) UNSIGNED NOT NULL"),
        Column(event_label, "VARCHAR(15) NOT NULL"),
        Column(event_scribe, "VARCHAR(128) NOT NULL"),
        Column(event_publisher, "VARCHAR(128) NOT NULL"),
        Column(event_printer, "VARCHAR(128) NOT NULL"),
        Column(event_length, "SMALLINT UNSIGNED NOT NULL")]


    source_table = "Trials"
    source_id = "TrialId"
    source_label = "Source"
    source_type = "Type"
    source_year = "Year"
    source_decade = "Decade"
    source_offence = "Offence"
    source_verdict = "Verdict"
    source_punishment = "Punishment"
    source_offencesubtype = "OffenceSub"
    source_verdictsubtype = "VerdictSub"
    source_punishmentsubtype = "PunishmentSub"

    source_columns = [
        Identifier(source_id, "SMALLINT(5) UNSIGNED NOT NULL"),
        Column(source_label, "VARCHAR(15) NOT NULL"),
        Column(source_type,
               "ENUM('trialAccount','supplementaryMaterial') NOT NULL"),
        Column(source_year, "SMALLINT(5) UNSIGNED NOT NULL"),
        Column(source_decade, "VARCHAR(10) NOT NULL"),
        Column(source_offence, "VARCHAR(128) NOT NULL"),
        Column(source_verdict, "VARCHAR(128) NOT NULL"),
        Column(source_punishment, "VARCHAR(128) NOT NULL"),
        Column(source_offencesubtype, "VARCHAR(128) NOT NULL"),
        Column(source_verdictsubtype, "VARCHAR(128) NOT NULL"),
        Column(source_punishmentsubtype, "VARCHAR(128) NOT NULL"),
        ]

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_file_id = "FileId"
    corpus_event_id = "UtteranceId"
    corpus_speaker_id = "SpeakerId"
    corpus_source_id = "SourceId"

    corpus_columns = [
        Identifier(corpus_id, "INT(7) UNSIGNED NOT NULL"),
        Link(corpus_file_id, file_table),
        Link(corpus_word_id, word_table),
        Link(corpus_speaker_id, speaker_table),
        Link(corpus_source_id, source_table),
        Link(corpus_event_id, event_table)]

    auto_create = ["word", "file", "speaker", "event", "offence", "source", "corpus"]

    #_source_map = {
        #"offenceDescription": source_offence,
        #"verdictDescription": source_verdict,
        #"punishmentDescription": source_punishment,
        #"defendantName": source_defendant,
        #"placeName": source_place,
        #"victimName": source_victim}

    expected_files = [
     "OBC2POS-17200427.xml", "OBC2POS-17550116.xml", "OBC2POS-18210912.xml",
     "OBC2POS-17200602.xml", "OBC2POS-17550226.xml", "OBC2POS-18211205.xml",
     "OBC2POS-17200907.xml", "OBC2POS-17550301.xml", "OBC2POS-18220109.xml",
     "OBC2POS-17201012.xml", "OBC2POS-17550409.xml", "OBC2POS-18220522.xml",
     "OBC2POS-17210113.xml", "OBC2POS-17550515.xml", "OBC2POS-18220703.xml",
     "OBC2POS-17210301.xml", "OBC2POS-17550702.xml", "OBC2POS-18230219.xml",
     "OBC2POS-17210525.xml", "OBC2POS-17550910.xml", "OBC2POS-18231022.xml",
     "OBC2POS-17210712.xml", "OBC2POS-17551022.xml", "OBC2POS-18250113.xml",
     "OBC2POS-17211011.xml", "OBC2POS-17551204.xml", "OBC2POS-18261026.xml",
     "OBC2POS-17211206.xml", "OBC2POS-17561020.xml", "OBC2POS-18270712.xml",
     "OBC2POS-17220228.xml", "OBC2POS-17561208.xml", "OBC2POS-18271206.xml",
     "OBC2POS-17220404.xml", "OBC2POS-17570223.xml", "OBC2POS-18290716.xml",
     "OBC2POS-17220704.xml", "OBC2POS-17570420.xml", "OBC2POS-18300218.xml",
     "OBC2POS-17220907.xml", "OBC2POS-17570526.xml", "OBC2POS-18320705.xml",
     "OBC2POS-17221205.xml", "OBC2POS-17570713.xml", "OBC2POS-18341205.xml",
     "OBC2POS-17230116.xml", "OBC2POS-17570914.xml", "OBC2POS-18350202.xml",
     "OBC2POS-17230424.xml", "OBC2POS-17580113.xml", "OBC2POS-18350302.xml",
     "OBC2POS-17230530.xml", "OBC2POS-17580222.xml", "OBC2POS-18350406.xml",
     "OBC2POS-17230828.xml", "OBC2POS-17580405.xml", "OBC2POS-18350511.xml",
     "OBC2POS-17231016.xml", "OBC2POS-17581206.xml", "OBC2POS-18350615.xml",
     "OBC2POS-17240117.xml", "OBC2POS-17590711.xml", "OBC2POS-18350706.xml",
     "OBC2POS-17240226.xml", "OBC2POS-17591024.xml", "OBC2POS-18351214.xml",
     "OBC2POS-17240521.xml", "OBC2POS-17600116.xml", "OBC2POS-18360404.xml",
     "OBC2POS-17240708.xml", "OBC2POS-17600227.xml", "OBC2POS-18360509.xml",
     "OBC2POS-17241014.xml", "OBC2POS-17600416.xml", "OBC2POS-18360704.xml",
     "OBC2POS-17241204.xml", "OBC2POS-17600521.xml", "OBC2POS-18360713.xml",
     "OBC2POS-17250224.xml", "OBC2POS-17600709.xml", "OBC2POS-18360815.xml",
     "OBC2POS-17250407.xml", "OBC2POS-17600910.xml", "OBC2POS-18370102.xml",
     "OBC2POS-17250630.xml", "OBC2POS-17601204.xml", "OBC2POS-18370227.xml",
     "OBC2POS-17250827.xml", "OBC2POS-17610116.xml", "OBC2POS-18380129.xml",
     "OBC2POS-17251208.xml", "OBC2POS-17610401.xml", "OBC2POS-18380226.xml",
     "OBC2POS-17260114.xml", "OBC2POS-17610506.xml", "OBC2POS-18390408.xml",
     "OBC2POS-17260420.xml", "OBC2POS-17610625.xml", "OBC2POS-18390513.xml",
     "OBC2POS-17260425.xml", "OBC2POS-17611021.xml", "OBC2POS-18410405.xml",
     "OBC2POS-17260831.xml", "OBC2POS-17620114.xml", "OBC2POS-18410705.xml",
     "OBC2POS-17261012.xml", "OBC2POS-17620224.xml", "OBC2POS-18410823.xml",
     "OBC2POS-17270113.xml", "OBC2POS-17620421.xml", "OBC2POS-18410920.xml",
     "OBC2POS-17270222.xml", "OBC2POS-17620526.xml", "OBC2POS-18411213.xml",
     "OBC2POS-17270517.xml", "OBC2POS-17620714.xml", "OBC2POS-18421128.xml",
     "OBC2POS-17270705.xml", "OBC2POS-17620917.xml", "OBC2POS-18430130.xml",
     "OBC2POS-17271017.xml", "OBC2POS-17621020.xml", "OBC2POS-18430227.xml",
     "OBC2POS-17271206.xml", "OBC2POS-17630114.xml", "OBC2POS-18430403.xml",
     "OBC2POS-17280228.xml", "OBC2POS-17630223.xml", "OBC2POS-18430703.xml",
     "OBC2POS-17280501.xml", "OBC2POS-17630413.xml", "OBC2POS-18430821.xml",
     "OBC2POS-17280717.xml", "OBC2POS-17630518.xml", "OBC2POS-18451027.xml",
     "OBC2POS-17280828.xml", "OBC2POS-17631019.xml", "OBC2POS-18451215.xml",
     "OBC2POS-17281204.xml", "OBC2POS-17640222.xml", "OBC2POS-18460706.xml",
     "OBC2POS-17290416.xml", "OBC2POS-17640502.xml", "OBC2POS-18481218.xml",
     "OBC2POS-17290521.xml", "OBC2POS-17640607.xml", "OBC2POS-18490101.xml",
     "OBC2POS-17290827.xml", "OBC2POS-17640728.xml", "OBC2POS-18490226.xml",
     "OBC2POS-17291015.xml", "OBC2POS-17650116.xml", "OBC2POS-18500408.xml",
     "OBC2POS-17300116.xml", "OBC2POS-17650227.xml", "OBC2POS-18500506.xml",
     "OBC2POS-17300513.xml", "OBC2POS-17650417.xml", "OBC2POS-18501216.xml",
     "OBC2POS-17301014.xml", "OBC2POS-17650522.xml", "OBC2POS-18510616.xml",
     "OBC2POS-17301204.xml", "OBC2POS-17650710.xml", "OBC2POS-18511215.xml",
     "OBC2POS-17310115.xml", "OBC2POS-17650918.xml", "OBC2POS-18520202.xml",
     "OBC2POS-17310428.xml", "OBC2POS-17651016.xml", "OBC2POS-18520223.xml",
     "OBC2POS-17310602.xml", "OBC2POS-17660702.xml", "OBC2POS-18520510.xml",
     "OBC2POS-17310908.xml", "OBC2POS-17661022.xml", "OBC2POS-18520614.xml",
     "OBC2POS-17311013.xml", "OBC2POS-17670115.xml", "OBC2POS-18520705.xml",
     "OBC2POS-17311208.xml", "OBC2POS-17670218.xml", "OBC2POS-18521025.xml",
     "OBC2POS-17320114.xml", "OBC2POS-17670603.xml", "OBC2POS-18530103.xml",
     "OBC2POS-17320223.xml", "OBC2POS-17670715.xml", "OBC2POS-18530228.xml",
     "OBC2POS-17320419.xml", "OBC2POS-17670909.xml", "OBC2POS-18530613.xml",
     "OBC2POS-17320525.xml", "OBC2POS-17690222.xml", "OBC2POS-18540102.xml",
     "OBC2POS-17320705.xml", "OBC2POS-17690405.xml", "OBC2POS-18540227.xml",
     "OBC2POS-17320906.xml", "OBC2POS-17700221.xml", "OBC2POS-18540403.xml",
     "OBC2POS-17321011.xml", "OBC2POS-17700425.xml", "OBC2POS-18540703.xml",
     "OBC2POS-17321206.xml", "OBC2POS-17700630.xml", "OBC2POS-18550507.xml",
     "OBC2POS-17330112.xml", "OBC2POS-17700711.xml", "OBC2POS-18570615.xml",
     "OBC2POS-17330221.xml", "OBC2POS-17700912.xml", "OBC2POS-18570706.xml",
     "OBC2POS-17330404.xml", "OBC2POS-17701024.xml", "OBC2POS-18590131.xml",
     "OBC2POS-17330510.xml", "OBC2POS-17710116.xml", "OBC2POS-18601126.xml",
     "OBC2POS-17330628.xml", "OBC2POS-17710703.xml", "OBC2POS-18601217.xml",
     "OBC2POS-17330912.xml", "OBC2POS-17710911.xml", "OBC2POS-18610128.xml",
     "OBC2POS-17331010.xml", "OBC2POS-17720109.xml", "OBC2POS-18610225.xml",
     "OBC2POS-17331205.xml", "OBC2POS-17720219.xml", "OBC2POS-18610408.xml",
     "OBC2POS-17340116.xml", "OBC2POS-17720429.xml", "OBC2POS-18610505.xml",
     "OBC2POS-17340227.xml", "OBC2POS-17720603.xml", "OBC2POS-18620106.xml",
     "OBC2POS-17340424.xml", "OBC2POS-17720715.xml", "OBC2POS-18620303.xml",
     "OBC2POS-17340630.xml", "OBC2POS-17720909.xml", "OBC2POS-18620407.xml",
     "OBC2POS-17340710.xml", "OBC2POS-17721021.xml", "OBC2POS-18620512.xml",
     "OBC2POS-17340911.xml", "OBC2POS-17730113.xml", "OBC2POS-18620616.xml",
     "OBC2POS-17341016.xml", "OBC2POS-17730217.xml", "OBC2POS-18620707.xml",
     "OBC2POS-17341204.xml", "OBC2POS-17730707.xml", "OBC2POS-18640229.xml",
     "OBC2POS-17350116.xml", "OBC2POS-17731020.xml", "OBC2POS-18640411.xml",
     "OBC2POS-17350226.xml", "OBC2POS-17740413.xml", "OBC2POS-18650227.xml",
     "OBC2POS-17350416.xml", "OBC2POS-17740518.xml", "OBC2POS-18651218.xml",
     "OBC2POS-17350522.xml", "OBC2POS-17741019.xml", "OBC2POS-18660507.xml",
     "OBC2POS-17350702.xml", "OBC2POS-17750111.xml", "OBC2POS-18660709.xml",
     "OBC2POS-17350911.xml", "OBC2POS-17750218.xml", "OBC2POS-18670408.xml",
     "OBC2POS-17351015.xml", "OBC2POS-17750426.xml", "OBC2POS-18670506.xml",
     "OBC2POS-17360115.xml", "OBC2POS-17750531.xml", "OBC2POS-18670610.xml",
     "OBC2POS-17360225.xml", "OBC2POS-17750712.xml", "OBC2POS-18680106.xml",
     "OBC2POS-17360505.xml", "OBC2POS-17750913.xml", "OBC2POS-18680406.xml",
     "OBC2POS-17360610.xml", "OBC2POS-17751206.xml", "OBC2POS-18680504.xml",
     "OBC2POS-17360721.xml", "OBC2POS-17760417.xml", "OBC2POS-18690607.xml",
     "OBC2POS-17361013.xml", "OBC2POS-17770115.xml", "OBC2POS-18690816.xml",
     "OBC2POS-17361208.xml", "OBC2POS-17770219.xml", "OBC2POS-18700404.xml",
     "OBC2POS-17370114.xml", "OBC2POS-17770514.xml", "OBC2POS-18700919.xml",
     "OBC2POS-17370216.xml", "OBC2POS-17770702.xml", "OBC2POS-18701024.xml",
     "OBC2POS-17370224.xml", "OBC2POS-17770910.xml", "OBC2POS-18701121.xml",
     "OBC2POS-17370420.xml", "OBC2POS-17771015.xml", "OBC2POS-18701212.xml",
     "OBC2POS-17370526.xml", "OBC2POS-17780603.xml", "OBC2POS-18710109.xml",
     "OBC2POS-17370706.xml", "OBC2POS-17790217.xml", "OBC2POS-18710130.xml",
     "OBC2POS-17370907.xml", "OBC2POS-17790519.xml", "OBC2POS-18710227.xml",
     "OBC2POS-17371012.xml", "OBC2POS-17790915.xml", "OBC2POS-18710403.xml",
     "OBC2POS-17371207.xml", "OBC2POS-17800112.xml", "OBC2POS-18710501.xml",
     "OBC2POS-17380113.xml", "OBC2POS-17800223.xml", "OBC2POS-18710605.xml",
     "OBC2POS-17380222.xml", "OBC2POS-17800405.xml", "OBC2POS-18710710.xml",
     "OBC2POS-17380412.xml", "OBC2POS-17800913.xml", "OBC2POS-18720108.xml",
     "OBC2POS-17380518.xml", "OBC2POS-17801018.xml", "OBC2POS-18720226.xml",
     "OBC2POS-17380628.xml", "OBC2POS-17801206.xml", "OBC2POS-18720610.xml",
     "OBC2POS-17380906.xml", "OBC2POS-17810110.xml", "OBC2POS-18720708.xml",
     "OBC2POS-17381011.xml", "OBC2POS-17810222.xml", "OBC2POS-18720923.xml",
     "OBC2POS-17381206.xml", "OBC2POS-17810425.xml", "OBC2POS-18721216.xml",
     "OBC2POS-17390117.xml", "OBC2POS-17810711.xml", "OBC2POS-18730303.xml",
     "OBC2POS-17390221.xml", "OBC2POS-17811017.xml", "OBC2POS-18730407.xml",
     "OBC2POS-17390502.xml", "OBC2POS-17820109.xml", "OBC2POS-18741123.xml",
     "OBC2POS-17390607.xml", "OBC2POS-17820220.xml", "OBC2POS-18750201.xml",
     "OBC2POS-17390718.xml", "OBC2POS-17820515.xml", "OBC2POS-18750301.xml",
     "OBC2POS-17390906.xml", "OBC2POS-17820605.xml", "OBC2POS-18760403.xml",
     "OBC2POS-17391017.xml", "OBC2POS-17820703.xml", "OBC2POS-18780311.xml",
     "OBC2POS-17391205.xml", "OBC2POS-17821016.xml", "OBC2POS-18800112.xml",
     "OBC2POS-17400116.xml", "OBC2POS-17830430.xml", "OBC2POS-18800209.xml",
     "OBC2POS-17400227.xml", "OBC2POS-17830726.xml", "OBC2POS-18800301.xml",
     "OBC2POS-17400416.xml", "OBC2POS-17841210.xml", "OBC2POS-18800524.xml",
     "OBC2POS-17400522.xml", "OBC2POS-17850406.xml", "OBC2POS-18800803.xml",
     "OBC2POS-17400709.xml", "OBC2POS-17860719.xml", "OBC2POS-18801018.xml",
     "OBC2POS-17400903.xml", "OBC2POS-17861215.xml", "OBC2POS-18801123.xml",
     "OBC2POS-17401015.xml", "OBC2POS-17870110.xml", "OBC2POS-18801213.xml",
     "OBC2POS-17401204.xml", "OBC2POS-17870112.xml", "OBC2POS-18810110.xml",
     "OBC2POS-17410116.xml", "OBC2POS-17870115.xml", "OBC2POS-18810131.xml",
     "OBC2POS-17410405.xml", "OBC2POS-17870418.xml", "OBC2POS-18810912.xml",
     "OBC2POS-17410701.xml", "OBC2POS-17870523.xml", "OBC2POS-18811121.xml",
     "OBC2POS-17410828.xml", "OBC2POS-17900224.xml", "OBC2POS-18811212.xml",
     "OBC2POS-17411204.xml", "OBC2POS-17900416.xml", "OBC2POS-18820109.xml",
     "OBC2POS-17420115.xml", "OBC2POS-17900417.xml", "OBC2POS-18820130.xml",
     "OBC2POS-17420224.xml", "OBC2POS-17900708.xml", "OBC2POS-18820327.xml",
     "OBC2POS-17420428.xml", "OBC2POS-17900710.xml", "OBC2POS-18820626.xml",
     "OBC2POS-17420603.xml", "OBC2POS-17910216.xml", "OBC2POS-18830319.xml",
     "OBC2POS-17420714.xml", "OBC2POS-17910720.xml", "OBC2POS-18840421.xml",
     "OBC2POS-17420715.xml", "OBC2POS-17910914.xml", "OBC2POS-18860308.xml",
     "OBC2POS-17420909.xml", "OBC2POS-17911026.xml", "OBC2POS-18871212.xml",
     "OBC2POS-17430114.xml", "OBC2POS-17911207.xml", "OBC2POS-18880319.xml",
     "OBC2POS-17430223.xml", "OBC2POS-17920113.xml", "OBC2POS-18890506.xml",
     "OBC2POS-17430413.xml", "OBC2POS-17920215.xml", "OBC2POS-18900908.xml",
     "OBC2POS-17430629.xml", "OBC2POS-17920329.xml", "OBC2POS-18901215.xml",
     "OBC2POS-17431012.xml", "OBC2POS-17920704.xml", "OBC2POS-18910112.xml",
     "OBC2POS-17431207.xml", "OBC2POS-17920912.xml", "OBC2POS-18910209.xml",
     "OBC2POS-17440223.xml", "OBC2POS-17921031.xml", "OBC2POS-18910406.xml",
     "OBC2POS-17440404.xml", "OBC2POS-17930626.xml", "OBC2POS-18910504.xml",
     "OBC2POS-17440912.xml", "OBC2POS-17931204.xml", "OBC2POS-18910525.xml",
     "OBC2POS-17441017.xml", "OBC2POS-17940219.xml", "OBC2POS-18920208.xml",
     "OBC2POS-17441205.xml", "OBC2POS-17950114.xml", "OBC2POS-18920307.xml",
     "OBC2POS-17450116.xml", "OBC2POS-17950218.xml", "OBC2POS-18920404.xml",
     "OBC2POS-17450227.xml", "OBC2POS-17950701.xml", "OBC2POS-18920725.xml",
     "OBC2POS-17450424.xml", "OBC2POS-17960406.xml", "OBC2POS-18930501.xml",
     "OBC2POS-17450530.xml", "OBC2POS-17961026.xml", "OBC2POS-18940305.xml",
     "OBC2POS-17450710.xml", "OBC2POS-17970712.xml", "OBC2POS-18950225.xml",
     "OBC2POS-17450911.xml", "OBC2POS-17970920.xml", "OBC2POS-18950722.xml",
     "OBC2POS-17451016.xml", "OBC2POS-17971025.xml", "OBC2POS-18951209.xml",
     "OBC2POS-17451204.xml", "OBC2POS-17980704.xml", "OBC2POS-18960323.xml",
     "OBC2POS-17460117.xml", "OBC2POS-17981205.xml", "OBC2POS-18961214.xml",
     "OBC2POS-17460226.xml", "OBC2POS-18000115.xml", "OBC2POS-18970914.xml",
     "OBC2POS-17460409.xml", "OBC2POS-18000219.xml", "OBC2POS-18980913.xml",
     "OBC2POS-17460702.xml", "OBC2POS-18000528.xml", "OBC2POS-18981212.xml",
     "OBC2POS-17460903.xml", "OBC2POS-18000917.xml", "OBC2POS-18990109.xml",
     "OBC2POS-17461205.xml", "OBC2POS-18001203.xml", "OBC2POS-18990912.xml",
     "OBC2POS-17470225.xml", "OBC2POS-18020217.xml", "OBC2POS-18991023.xml",
     "OBC2POS-17470604.xml", "OBC2POS-18020602.xml", "OBC2POS-18991120.xml",
     "OBC2POS-17470715.xml", "OBC2POS-18020714.xml", "OBC2POS-18991211.xml",
     "OBC2POS-17470909.xml", "OBC2POS-18021027.xml", "OBC2POS-19000115.xml",
     "OBC2POS-17471014.xml", "OBC2POS-18030112.xml", "OBC2POS-19000212.xml",
     "OBC2POS-17480115.xml", "OBC2POS-18030914.xml", "OBC2POS-19000312.xml",
     "OBC2POS-17480526.xml", "OBC2POS-18031026.xml", "OBC2POS-19010225.xml",
     "OBC2POS-17480907.xml", "OBC2POS-18031130.xml", "OBC2POS-19020113.xml",
     "OBC2POS-17481012.xml", "OBC2POS-18040111.xml", "OBC2POS-19020210.xml",
     "OBC2POS-17481207.xml", "OBC2POS-18050109.xml", "OBC2POS-19020310.xml",
     "OBC2POS-17490113.xml", "OBC2POS-18050220.xml", "OBC2POS-19020407.xml",
     "OBC2POS-17490222.xml", "OBC2POS-18060521.xml", "OBC2POS-19020505.xml",
     "OBC2POS-17490405.xml", "OBC2POS-18060702.xml", "OBC2POS-19020721.xml",
     "OBC2POS-17490411.xml", "OBC2POS-18070114.xml", "OBC2POS-19020909.xml",
     "OBC2POS-17490705.xml", "OBC2POS-18070701.xml", "OBC2POS-19030330.xml",
     "OBC2POS-17490906.xml", "OBC2POS-18070916.xml", "OBC2POS-19040111.xml",
     "OBC2POS-17491011.xml", "OBC2POS-18081130.xml", "OBC2POS-19040229.xml",
     "OBC2POS-17491209.xml", "OBC2POS-18090517.xml", "OBC2POS-19040321.xml",
     "OBC2POS-17500117.xml", "OBC2POS-18100110.xml", "OBC2POS-19040725.xml",
     "OBC2POS-17500228.xml", "OBC2POS-18100411.xml", "OBC2POS-19050502.xml",
     "OBC2POS-17500425.xml", "OBC2POS-18100718.xml", "OBC2POS-19050626.xml",
     "OBC2POS-17500530.xml", "OBC2POS-18110403.xml", "OBC2POS-19060108.xml",
     "OBC2POS-17500711.xml", "OBC2POS-18120115.xml", "OBC2POS-19060205.xml",
     "OBC2POS-17500912.xml", "OBC2POS-18120701.xml", "OBC2POS-19060402.xml",
     "OBC2POS-17501017.xml", "OBC2POS-18120916.xml", "OBC2POS-19060430.xml",
     "OBC2POS-17501205.xml", "OBC2POS-18130113.xml", "OBC2POS-19070108.xml",
     "OBC2POS-17510116.xml", "OBC2POS-18130217.xml", "OBC2POS-19070225.xml",
     "OBC2POS-17510227.xml", "OBC2POS-18131027.xml", "OBC2POS-19070910.xml",
     "OBC2POS-17510417.xml", "OBC2POS-18140112.xml", "OBC2POS-19090518.xml",
     "OBC2POS-17510523.xml", "OBC2POS-18150111.xml", "OBC2POS-19100208.xml",
     "OBC2POS-17510703.xml", "OBC2POS-18150405.xml", "OBC2POS-19100426.xml",
     "OBC2POS-17520116.xml", "OBC2POS-18150621.xml", "OBC2POS-19100628.xml",
     "OBC2POS-17520218.xml", "OBC2POS-18150913.xml", "OBC2POS-19101206.xml",
     "OBC2POS-17520219.xml", "OBC2POS-18161204.xml", "OBC2POS-19110228.xml",
     "OBC2POS-17520408.xml", "OBC2POS-18170115.xml", "OBC2POS-19110328.xml",
     "OBC2POS-17520514.xml", "OBC2POS-18170521.xml", "OBC2POS-19110717.xml",
     "OBC2POS-17520625.xml", "OBC2POS-18170702.xml", "OBC2POS-19111205.xml",
     "OBC2POS-17520914.xml", "OBC2POS-18170917.xml", "OBC2POS-19120109.xml",
     "OBC2POS-17530906.xml", "OBC2POS-18180909.xml", "OBC2POS-19120227.xml",
     "OBC2POS-17531024.xml", "OBC2POS-18200112.xml", "OBC2POS-19120722.xml",
     "OBC2POS-17540116.xml", "OBC2POS-18200217.xml", "OBC2POS-19130107.xml",
     "OBC2POS-17540424.xml", "OBC2POS-18201206.xml", "OBC2POS-19130304.xml",
     "OBC2POS-17540530.xml", "OBC2POS-18210411.xml", "OBC2POS-17540717.xml",
     "OBC2POS-18210718.xml"]

    def __init__(self, gui=False, *args):
        super(BuilderClass, self).__init__(gui=gui, *args)
        self.add_time_feature(self.source_year)
        # self.add_time_feature(self.speaker_age)
        self._speaker_id = 0
        self._offence_id = 0
        self._source_id = 0

    @staticmethod
    def get_name():
        return "Old_Bailey_Corpus"

    @staticmethod
    def get_db_name():
        return "coq_obc2"

    @staticmethod
    def get_title():
        return "The Old Bailey Corpus 2.0, 1720–1913"

    @staticmethod
    def get_language():
        return "English"

    @staticmethod
    def get_language_code():
        return "en-UK"

    @staticmethod
    def get_description():
        return [("The Old Bailey Corpus (OBC) is a sociolinguistically, "
                 "pragmatically and textually annotated corpus based on a "
                 "selection of the <i>Proceedings of the Old Bailey</i> "
                 "(Hitchcock et al. 2015), the published version of the "
                 "trials at London's Central Criminal Court."),
                ("Version 2.0 of the <i>OBC</i> consists of 637 selected "
                 "<i>Proceedings</i>, from 1720 to 1913. OBC 2.0 contains a "
                 "total of 24.4 million words, with 1.2 million "
                 "speech-related words per decade on average.")]

    @staticmethod
    def get_references():
        return [
            "Magnus Huber, Magnus Nissel, Karin Puga (2016). <i>Old Bailey "
            "Corpus 2.0.</i> <a "
            "href='http://hdl.handle.net/11858/00-246C-0000-0023-8CFB-2'>"
            "hdl:11858/00-246C-0000-0023-8CFB-2</a>."]

    @staticmethod
    def get_url():
        s = "http://fedora.clarin-d.uni-saarland.de/oldbailey/downloads.html"
        return s

    @staticmethod
    def get_license():
        return ("The <i>Old Bailey Corpus</i> is licensed under a Creative "
                "Commons Attribution-NonCommercial-ShareAlike license (<a "
                "href='http://creativecommons.org/licenses/by-nc-sa/4.0/'>CC "
                "BY-NC-SA 4.0</a>).")

    @classmethod
    def get_file_list(cls, *args, **kwargs):
        l = super(BuilderClass, cls).get_file_list(*args, **kwargs)
        return l

    @classmethod
    def _get_text(cls, node):
        def traverse(node, no_tail=False):
            if node.text:
                s_list = [node.text]
            else:
                s_list = []

            for child in node.getchildren():
                s_list += traverse(child)

            if node.tail and not no_tail:
                s_list += [node.tail]
            return s_list

        return " ".join([x.strip() for x in traverse(node, no_tail=True)])

    def _split_words(self, s):
        """
        Split the words contained in the string s by the underscore character
        '_' and return two lists 'words' and 'tags'. If a word doesn't have
        a POS tag, return 'UNKNOWN' for that word.
        """

        # File OBC2POS-17370420.xml contains an error: in line 1705 there's
        # a space missing in ;_;T'_PPH1.
        # Fix this issue manually:
        if self._event == "17370420-368":
            s = s.replace(";_;T'_PPH1", ";_; T'_PPH1")

        tokens = s.split()
        elements = [x for x in tokens if x]
        if elements:
            words, _, tags = zip(*(w.partition("_") for w in elements))
            tags = [pos or "UNKNOWN" for pos in tags]
            return words, tags
        else:
            return [], []

    def make_tree(self, data):
        data = "\n".join(data)
        try:
            tree = ET.XML(bytes(data, encoding="utf8"))
        except:
            tree = ET.XML(data)
        return tree

    def _process_utterances(self, utterances):
        self._new_people = {}
        for u in utterances:
            text = self._get_text(u)
            age = u.attrib.get("age", None)
            speaker = u.attrib.get("speaker", None)
            sex = u.attrib.get("sex", None) or "?"

            label = u.attrib.get("hiscoLabel", None) or ""
            role = u.attrib.get("role", None) or "?"

            hisclass = u.attrib.get("hisclass", None)
            try:
                hisclass = int(hisclass)
            except ValueError:
                hisclass = None
            class_cat = ("?" if hisclass is None else
                         "lower (6-13)" if hisclass > 6 else
                         "upper (1-5)")

            d_speaker = {self.speaker_age: age,
                         self.speaker_sex: sex,
                         self.speaker_role: role,
                         self.speaker_hiscolabel: label,
                         self.speaker_hisclass: hisclass,
                         self.speaker_class: class_cat,
                         self.speaker_label: speaker}

            if speaker in self._new_people:
                existing_speaker = self._new_people[speaker]
                # update existing speaker with new values
                for x in d_speaker:
                    existing_val = existing_speaker[x]
                    new_val = d_speaker[x]
                    if existing_val in ["", "?", None]:
                        existing_speaker[x] = new_val
                    elif new_val in ["", "?", None]:
                        d_speaker[x] = existing_val
                self._new_people[speaker] = existing_speaker
            else:
                self._speaker_id += 1
                d_speaker[self.speaker_id] = self._speaker_id
                self._new_people[speaker] = d_speaker


            printer = u.attrib.get("printer", None) or "?"
            publisher = u.attrib.get("publisher", None) or "?"
            scribe = u.attrib.get("scribe", None) or "?"
            self._event = u.attrib.get("event")
            try:
                length = int(u.attrib.get("wc", None))
            except (TypeError, ValueError):
                length = 0

            d_event = {self.event_label: self._event,
                       self.event_printer: printer,
                       self.event_publisher: publisher,
                       self.event_scribe: scribe,
                       self.event_length: length}

            self._event_id = self.table(self.event_table).get_or_insert(
                d_event)

            for word, pos in zip(*self._split_words(text)):
                d_word = {self.word_label: word,
                          self.word_pos: pos}
                self._word_id = self.table(self.word_table).get_or_insert(
                    d_word)

                self.add_token_to_corpus(
                    {self.corpus_word_id: self._word_id,
                     self.corpus_file_id: self._file_id,
                     self.corpus_speaker_id: self._speaker_id,
                     self.corpus_event_id: self._event_id,
                     self.corpus_source_id: self._source_id})

        for speaker in self._new_people:
            self.table(self.speaker_table).add_with_id(
                self._new_people[speaker])

    def _process_charge(self, charge, trial, d):
        targets = charge.attrib["targets"]
        for target in targets.split():
            rs = trial.find(".//rs[@id='{}']".format(target))
            if rs is not None:
                if rs.attrib["type"] == "offenceDescription":
                    for interp in rs.findall(".//interp"):
                        i_type = interp.attrib["type"]
                        val = interp.attrib["value"]
                        if i_type == "offenceCategory":
                            d[self.source_offence] = val
                        elif i_type == "offenceSubcategory":
                            d[self.source_offencesubtype] = val
                elif rs.attrib["type"] == "verdictDescription":
                    for interp in rs.findall(".//interp"):
                        i_type = interp.attrib["type"]
                        val = interp.attrib["value"]
                        if i_type == "verdictCategory":
                            d[self.source_verdict] = val
                        elif i_type == "verdictSubcategory":
                            d[self.source_verdictsubtype] = val
        rs = trial.find(".//rs[@type='punishmentDescription']")
        if rs is not None:
            for interp in rs.findall(".//interp"):
                i_type = interp.attrib["type"]
                val = interp.attrib["value"]
                if i_type == "punishmentCategory":
                    d[self.source_punishment] = val
                elif i_type == "punishmentSubcategory":
                    d[self.source_punishmentsubtype] = val
        return d

    def process_tree(self, tree):
        for trial in tree.iter(tag="div1"):
            date_node = tree.xpath(".//interp[@type='year' or @type='date']")
            if date_node:
                year = date_node[0].attrib["value"][:4]
                decade = "{0}0-{0}9".format(year[:-1])
            else:
                year = "?"
                decade = "?"

            utterances = trial.findall(".//u")
            if not utterances:
                continue

            self._source_id = self._source_id + 1
            d_trial = {}
            d_trial[self.source_offence] = ""
            d_trial[self.source_verdict] = ""
            d_trial[self.source_punishment] = ""
            d_trial[self.source_offencesubtype] = ""
            d_trial[self.source_verdictsubtype] = ""
            d_trial[self.source_punishmentsubtype] = ""
            d_trial[self.source_label] = trial.attrib["id"]

            d_trial[self.source_type] = trial.attrib["type"]
            d_trial[self.source_year] = year
            d_trial[self.source_decade] = decade

            for join in trial.findall("./join"):
                if join.attrib["result"] == "criminalCharge":
                    d_trial = self._process_charge(join, trial, d_trial)

            self._source_id = self.table(self.source_table).add(d_trial)
            self._process_utterances(utterances)
