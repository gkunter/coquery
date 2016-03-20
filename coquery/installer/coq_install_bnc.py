# -*- coding: utf-8 -*-

"""
coq_install_bnc.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals 

from coquery.corpusbuilder import *
import re

class BuilderClass(BaseCorpusBuilder):
    file_filter = "???.xml"

    expected_files = [
    'A00.xml', 'A01.xml', 'A02.xml', 'A03.xml', 'A04.xml', 'A05.xml',
    'A06.xml', 'A07.xml', 'A08.xml', 'A0A.xml', 'A0B.xml', 'A0C.xml',
    'A0D.xml', 'A0E.xml', 'A0F.xml', 'A0G.xml', 'A0H.xml', 'A0J.xml',
    'A0K.xml', 'A0L.xml', 'A0M.xml', 'A0N.xml', 'A0P.xml', 'A0R.xml',
    'A0S.xml', 'A0T.xml', 'A0U.xml', 'A0V.xml', 'A0W.xml', 'A0X.xml',
    'A0Y.xml', 'A10.xml', 'A11.xml', 'A12.xml', 'A13.xml', 'A14.xml',
    'A15.xml', 'A16.xml', 'A17.xml', 'A18.xml', 'A19.xml', 'A1A.xml',
    'A1B.xml', 'A1D.xml', 'A1E.xml', 'A1F.xml', 'A1G.xml', 'A1H.xml',
    'A1J.xml', 'A1K.xml', 'A1L.xml', 'A1M.xml', 'A1N.xml', 'A1P.xml',
    'A1R.xml', 'A1S.xml', 'A1T.xml', 'A1U.xml', 'A1V.xml', 'A1W.xml',
    'A1X.xml', 'A1Y.xml', 'A20.xml', 'A21.xml', 'A22.xml', 'A23.xml',
    'A24.xml', 'A25.xml', 'A26.xml', 'A27.xml', 'A28.xml', 'A29.xml',
    'A2A.xml', 'A2B.xml', 'A2C.xml', 'A2D.xml', 'A2E.xml', 'A2F.xml',
    'A2G.xml', 'A2H.xml', 'A2J.xml', 'A2K.xml', 'A2L.xml', 'A2M.xml',
    'A2N.xml', 'A2P.xml', 'A2R.xml', 'A2S.xml', 'A2T.xml', 'A2U.xml',
    'A2V.xml', 'A2W.xml', 'A2X.xml', 'A2Y.xml', 'A30.xml', 'A31.xml',
    'A32.xml', 'A33.xml', 'A34.xml', 'A35.xml', 'A36.xml', 'A37.xml',
    'A38.xml', 'A39.xml', 'A3A.xml', 'A3B.xml', 'A3C.xml', 'A3D.xml',
    'A3E.xml', 'A3F.xml', 'A3G.xml', 'A3H.xml', 'A3J.xml', 'A3K.xml',
    'A3L.xml', 'A3M.xml', 'A3N.xml', 'A3P.xml', 'A3R.xml', 'A3S.xml',
    'A3T.xml', 'A3U.xml', 'A3V.xml', 'A3W.xml', 'A3X.xml', 'A3Y.xml',
    'A40.xml', 'A41.xml', 'A42.xml', 'A43.xml', 'A44.xml', 'A45.xml',
    'A46.xml', 'A47.xml', 'A48.xml', 'A49.xml', 'A4A.xml', 'A4B.xml',
    'A4C.xml', 'A4D.xml', 'A4E.xml', 'A4F.xml', 'A4G.xml', 'A4H.xml',
    'A4J.xml', 'A4K.xml', 'A4L.xml', 'A4M.xml', 'A4N.xml', 'A4P.xml',
    'A4R.xml', 'A4S.xml', 'A4U.xml', 'A4V.xml', 'A4W.xml', 'A4X.xml',
    'A4Y.xml', 'A50.xml', 'A51.xml', 'A52.xml', 'A53.xml', 'A54.xml',
    'A55.xml', 'A56.xml', 'A57.xml', 'A58.xml', 'A59.xml', 'A5A.xml',
    'A5B.xml', 'A5C.xml', 'A5D.xml', 'A5E.xml', 'A5F.xml', 'A5G.xml',
    'A5H.xml', 'A5J.xml', 'A5K.xml', 'A5L.xml', 'A5M.xml', 'A5N.xml',
    'A5P.xml', 'A5R.xml', 'A5S.xml', 'A5T.xml', 'A5U.xml', 'A5V.xml',
    'A5W.xml', 'A5X.xml', 'A5Y.xml', 'A60.xml', 'A61.xml', 'A62.xml',
    'A63.xml', 'A64.xml', 'A65.xml', 'A66.xml', 'A67.xml', 'A68.xml',
    'A69.xml', 'A6A.xml', 'A6B.xml', 'A6C.xml', 'A6D.xml', 'A6E.xml',
    'A6F.xml', 'A6G.xml', 'A6J.xml', 'A6L.xml', 'A6M.xml', 'A6N.xml',
    'A6R.xml', 'A6S.xml', 'A6T.xml', 'A6U.xml', 'A6V.xml', 'A6W.xml',
    'A6X.xml', 'A6Y.xml', 'A70.xml', 'A73.xml', 'A74.xml', 'A75.xml',
    'A77.xml', 'A79.xml', 'A7A.xml', 'A7C.xml', 'A7D.xml', 'A7F.xml',
    'A7G.xml', 'A7H.xml', 'A7J.xml', 'A7K.xml', 'A7L.xml', 'A7N.xml',
    'A7P.xml', 'A7S.xml', 'A7T.xml', 'A7U.xml', 'A7V.xml', 'A7W.xml',
    'A7X.xml', 'A7Y.xml', 'A80.xml', 'A81.xml', 'A82.xml', 'A83.xml',
    'A84.xml', 'A85.xml', 'A86.xml', 'A87.xml', 'A88.xml', 'A89.xml',
    'A8A.xml', 'A8B.xml', 'A8C.xml', 'A8D.xml', 'A8E.xml', 'A8F.xml',
    'A8G.xml', 'A8H.xml', 'A8J.xml', 'A8K.xml', 'A8L.xml', 'A8M.xml',
    'A8N.xml', 'A8P.xml', 'A8R.xml', 'A8S.xml', 'A8T.xml', 'A8U.xml',
    'A8V.xml', 'A8W.xml', 'A8X.xml', 'A8Y.xml', 'A90.xml', 'A91.xml',
    'A92.xml', 'A93.xml', 'A94.xml', 'A95.xml', 'A96.xml', 'A97.xml',
    'A98.xml', 'A99.xml', 'A9A.xml', 'A9B.xml', 'A9C.xml', 'A9D.xml',
    'A9E.xml', 'A9F.xml', 'A9G.xml', 'A9H.xml', 'A9J.xml', 'A9K.xml',
    'A9L.xml', 'A9M.xml', 'A9N.xml', 'A9P.xml', 'A9R.xml', 'A9S.xml',
    'A9T.xml', 'A9U.xml', 'A9V.xml', 'A9W.xml', 'A9X.xml', 'A9Y.xml',
    'AA0.xml', 'AA1.xml', 'AA2.xml', 'AA3.xml', 'AA4.xml', 'AA5.xml',
    'AA6.xml', 'AA7.xml', 'AA8.xml', 'AA9.xml', 'AAA.xml', 'AAB.xml',
    'AAC.xml', 'AAD.xml', 'AAE.xml', 'AAF.xml', 'AAG.xml', 'AAH.xml',
    'AAJ.xml', 'AAK.xml', 'AAL.xml', 'AAM.xml', 'AAN.xml', 'AAP.xml',
    'AAR.xml', 'AAS.xml', 'AAT.xml', 'AAU.xml', 'AAV.xml', 'AAW.xml',
    'AAX.xml', 'AAY.xml', 'AB3.xml', 'AB4.xml', 'AB5.xml', 'AB6.xml',
    'AB9.xml', 'ABA.xml', 'ABB.xml', 'ABC.xml', 'ABD.xml', 'ABE.xml',
    'ABF.xml', 'ABG.xml', 'ABH.xml', 'ABJ.xml', 'ABK.xml', 'ABL.xml',
    'ABM.xml', 'ABP.xml', 'ABR.xml', 'ABS.xml', 'ABU.xml', 'ABV.xml',
    'ABW.xml', 'ABX.xml', 'AC0.xml', 'AC2.xml', 'AC3.xml', 'AC4.xml',
    'AC5.xml', 'AC6.xml', 'AC7.xml', 'AC9.xml', 'ACA.xml', 'ACB.xml',
    'ACE.xml', 'ACG.xml', 'ACH.xml', 'ACJ.xml', 'ACK.xml', 'ACL.xml',
    'ACM.xml', 'ACN.xml', 'ACP.xml', 'ACR.xml', 'ACS.xml', 'ACV.xml',
    'ACW.xml', 'ACX.xml', 'ACY.xml', 'AD0.xml', 'AD1.xml', 'AD2.xml',
    'AD7.xml', 'AD9.xml', 'ADA.xml', 'ADB.xml', 'ADC.xml', 'ADD.xml',
    'ADE.xml', 'ADF.xml', 'ADG.xml', 'ADH.xml', 'ADK.xml', 'ADL.xml',
    'ADM.xml', 'ADP.xml', 'ADR.xml', 'ADS.xml', 'ADW.xml', 'ADX.xml',
    'ADY.xml', 'AE0.xml', 'AE4.xml', 'AE6.xml', 'AE7.xml', 'AE8.xml',
    'AE9.xml', 'AEA.xml', 'AEB.xml', 'AH9.xml', 'AHA.xml', 'AHB.xml',
    'AHC.xml', 'AHD.xml', 'AHE.xml', 'AHF.xml', 'AHG.xml', 'AHH.xml',
    'AHJ.xml', 'AHK.xml', 'AHL.xml', 'AHM.xml', 'AHN.xml', 'AHP.xml',
    'AHR.xml', 'AHS.xml', 'AHT.xml', 'AHU.xml', 'AHV.xml', 'AHW.xml',
    'AHX.xml', 'AHY.xml', 'AJ0.xml', 'AJ1.xml', 'AJ2.xml', 'AJ3.xml',
    'AJ4.xml', 'AJ5.xml', 'AJ6.xml', 'AJ7.xml', 'AJ8.xml', 'AJ9.xml',
    'AJA.xml', 'AJB.xml', 'AJC.xml', 'AJD.xml', 'AJE.xml', 'AJF.xml',
    'AJG.xml', 'AJH.xml', 'AJJ.xml', 'AJK.xml', 'AJL.xml', 'AJM.xml',
    'AJN.xml', 'AJP.xml', 'AJR.xml', 'AJS.xml', 'AJT.xml', 'AJU.xml',
    'AJV.xml', 'AJW.xml', 'AJX.xml', 'AJY.xml', 'AK0.xml', 'AK1.xml',
    'AK2.xml', 'AK3.xml', 'AK4.xml', 'AK6.xml', 'AK7.xml', 'AK8.xml',
    'AK9.xml', 'AKA.xml', 'AKB.xml', 'AKC.xml', 'AKD.xml', 'AKE.xml',
    'AKF.xml', 'AKG.xml', 'AKH.xml', 'AKJ.xml', 'AKK.xml', 'AKL.xml',
    'AKM.xml', 'AKN.xml', 'AKP.xml', 'AKR.xml', 'AKS.xml', 'AKT.xml',
    'AKU.xml', 'AKV.xml', 'AKW.xml', 'AKX.xml', 'AKY.xml', 'AL0.xml',
    'AL1.xml', 'AL2.xml', 'AL3.xml', 'AL4.xml', 'AL5.xml', 'AL6.xml',
    'AL7.xml', 'AL8.xml', 'AL9.xml', 'ALA.xml', 'ALB.xml', 'ALC.xml',
    'ALE.xml', 'ALF.xml', 'ALG.xml', 'ALH.xml', 'ALJ.xml', 'ALK.xml',
    'ALL.xml', 'ALM.xml', 'ALN.xml', 'ALP.xml', 'ALS.xml', 'ALT.xml',
    'ALU.xml', 'ALV.xml', 'ALW.xml', 'ALX.xml', 'ALY.xml', 'AM0.xml',
    'AM1.xml', 'AM2.xml', 'AM4.xml', 'AM5.xml', 'AM6.xml', 'AM7.xml',
    'AM8.xml', 'AM9.xml', 'AMA.xml', 'AMB.xml', 'AMC.xml', 'AMD.xml',
    'AMG.xml', 'AMH.xml', 'AMK.xml', 'AML.xml', 'AMM.xml', 'AMN.xml',
    'AMR.xml', 'AMS.xml', 'AMT.xml', 'AMU.xml', 'AMW.xml', 'AMX.xml',
    'AMY.xml', 'AN0.xml', 'AN1.xml', 'AN2.xml', 'AN3.xml', 'AN4.xml',
    'AN5.xml', 'AN7.xml', 'AN8.xml', 'AN9.xml', 'ANA.xml', 'ANB.xml',
    'ANC.xml', 'AND.xml', 'ANF.xml', 'ANH.xml', 'ANJ.xml', 'ANK.xml',
    'ANL.xml', 'ANM.xml', 'ANP.xml', 'ANR.xml', 'ANS.xml', 'ANT.xml',
    'ANU.xml', 'ANX.xml', 'ANY.xml', 'AP0.xml', 'AP1.xml', 'AP5.xml',
    'AP6.xml', 'AP7.xml', 'AP8.xml', 'APC.xml', 'APD.xml', 'APE.xml',
    'APH.xml', 'APJ.xml', 'APK.xml', 'APL.xml', 'APM.xml', 'APN.xml',
    'APP.xml', 'APR.xml', 'APS.xml', 'APT.xml', 'APU.xml', 'APV.xml',
    'APW.xml', 'APX.xml', 'AR0.xml', 'AR2.xml', 'AR3.xml', 'AR4.xml',
    'AR5.xml', 'AR7.xml', 'AR8.xml', 'AR9.xml', 'ARA.xml', 'ARB.xml',
    'ARC.xml', 'ARD.xml', 'ARE.xml', 'ARF.xml', 'ARG.xml', 'ARH.xml',
    'ARJ.xml', 'ARK.xml', 'ARM.xml', 'ARP.xml', 'ARR.xml', 'ARS.xml',
    'ART.xml', 'ARW.xml', 'ARX.xml', 'ARY.xml', 'AS0.xml', 'AS1.xml',
    'AS3.xml', 'AS4.xml', 'AS5.xml', 'AS6.xml', 'AS7.xml', 'ASA.xml',
    'ASB.xml', 'ASC.xml', 'ASD.xml', 'ASE.xml', 'ASF.xml', 'ASH.xml',
    'ASJ.xml', 'ASK.xml', 'ASL.xml', 'ASN.xml', 'ASR.xml', 'ASS.xml',
    'ASU.xml', 'ASV.xml', 'ASW.xml', 'ASY.xml', 'AT1.xml', 'AT3.xml',
    'AT4.xml', 'AT6.xml', 'AT7.xml', 'AT8.xml', 'AT9.xml', 'ATA.xml',
    'ATE.xml', 'ATG.xml', 'AYJ.xml', 'AYK.xml', 'AYM.xml', 'AYP.xml',
    'AYR.xml', 'AYX.xml', 'B01.xml', 'B02.xml', 'B03.xml', 'B04.xml',
    'B05.xml', 'B06.xml', 'B07.xml', 'B08.xml', 'B09.xml', 'B0A.xml',
    'B0B.xml', 'B0G.xml', 'B0H.xml', 'B0J.xml', 'B0K.xml', 'B0L.xml',
    'B0M.xml', 'B0N.xml', 'B0P.xml', 'B0R.xml', 'B0S.xml', 'B0U.xml',
    'B0W.xml', 'B0X.xml', 'B0Y.xml', 'B10.xml', 'B11.xml', 'B12.xml',
    'B13.xml', 'B14.xml', 'B15.xml', 'B16.xml', 'B17.xml', 'B19.xml',
    'B1A.xml', 'B1C.xml', 'B1D.xml', 'B1E.xml', 'B1F.xml', 'B1G.xml',
    'B1H.xml', 'B1J.xml', 'B1K.xml', 'B1L.xml', 'B1M.xml', 'B1N.xml',
    'B1P.xml', 'B1R.xml', 'B1S.xml', 'B1T.xml', 'B1U.xml', 'B1W.xml',
    'B1X.xml', 'B1Y.xml', 'B20.xml', 'B21.xml', 'B22.xml', 'B23.xml',
    'B24.xml', 'B25.xml', 'B26.xml', 'B27.xml', 'B28.xml', 'B29.xml',
    'B2A.xml', 'B2B.xml', 'B2C.xml', 'B2D.xml', 'B2E.xml', 'B2F.xml',
    'B2G.xml', 'B2H.xml', 'B2J.xml', 'B2K.xml', 'B2L.xml', 'B2M.xml',
    'B2N.xml', 'B2P.xml', 'B2S.xml', 'B2T.xml', 'B2U.xml', 'B2V.xml',
    'B2W.xml', 'B2X.xml', 'B2Y.xml', 'B30.xml', 'B31.xml', 'B32.xml',
    'B33.xml', 'B34.xml', 'B35.xml', 'B38.xml', 'B39.xml', 'B3A.xml',
    'B3B.xml', 'B3C.xml', 'B3D.xml', 'B3F.xml', 'B3G.xml', 'B3H.xml',
    'B3J.xml', 'B3K.xml', 'B71.xml', 'B72.xml', 'B73.xml', 'B74.xml',
    'B75.xml', 'B76.xml', 'B77.xml', 'B78.xml', 'B79.xml', 'B7A.xml',
    'B7B.xml', 'B7C.xml', 'B7D.xml', 'B7E.xml', 'B7F.xml', 'B7G.xml',
    'B7H.xml', 'B7J.xml', 'B7K.xml', 'B7L.xml', 'B7M.xml', 'B7N.xml',
    'BLW.xml', 'BLX.xml', 'BLY.xml', 'BM0.xml', 'BM1.xml', 'BM2.xml',
    'BM4.xml', 'BM5.xml', 'BM6.xml', 'BM9.xml', 'BMA.xml', 'BMB.xml',
    'BMC.xml', 'BMD.xml', 'BME.xml', 'BMF.xml', 'BMG.xml', 'BMH.xml',
    'BMJ.xml', 'BMK.xml', 'BML.xml', 'BMM.xml', 'BMN.xml', 'BMP.xml',
    'BMR.xml', 'BMS.xml', 'BMT.xml', 'BMU.xml', 'BMV.xml', 'BMW.xml',
    'BMX.xml', 'BMY.xml', 'BN1.xml', 'BN2.xml', 'BN3.xml', 'BN4.xml',
    'BN5.xml', 'BN6.xml', 'BN7.xml', 'BN8.xml', 'BN9.xml', 'BNA.xml',
    'BNB.xml', 'BNC.xml', 'BND.xml', 'BNE.xml', 'BNF.xml', 'BNG.xml',
    'BNH.xml', 'BNJ.xml', 'BNK.xml', 'BNL.xml', 'BNM.xml', 'BNN.xml',
    'BNP.xml', 'BNS.xml', 'BNT.xml', 'BNU.xml', 'BNV.xml', 'BNW.xml',
    'BNX.xml', 'BNY.xml', 'BP0.xml', 'BP1.xml', 'BP2.xml', 'BP3.xml',
    'BP4.xml', 'BP5.xml', 'BP6.xml', 'BP7.xml', 'BP8.xml', 'BP9.xml',
    'BPA.xml', 'BPB.xml', 'BPC.xml', 'BPD.xml', 'BPE.xml', 'BPF.xml',
    'BPG.xml', 'BPH.xml', 'BPJ.xml', 'BPK.xml', 'C85.xml', 'C86.xml',
    'C87.xml', 'C88.xml', 'C89.xml', 'C8A.xml', 'C8B.xml', 'C8D.xml',
    'C8E.xml', 'C8F.xml', 'C8G.xml', 'C8H.xml', 'C8J.xml', 'C8K.xml',
    'C8L.xml', 'C8M.xml', 'C8N.xml', 'C8P.xml', 'C8R.xml', 'C8S.xml',
    'C8T.xml', 'C8U.xml', 'C8V.xml', 'C8X.xml', 'C8Y.xml', 'C90.xml',
    'C91.xml', 'C92.xml', 'C93.xml', 'C94.xml', 'C95.xml', 'C96.xml',
    'C97.xml', 'C98.xml', 'C9A.xml', 'C9B.xml', 'C9C.xml', 'C9D.xml',
    'C9E.xml', 'C9F.xml', 'C9H.xml', 'C9J.xml', 'C9K.xml', 'C9L.xml',
    'C9M.xml', 'C9N.xml', 'C9P.xml', 'C9R.xml', 'C9S.xml', 'C9U.xml',
    'C9V.xml', 'C9W.xml', 'C9X.xml', 'C9Y.xml', 'CA0.xml', 'CA1.xml',
    'CA2.xml', 'CA3.xml', 'CA4.xml', 'CA5.xml', 'CA6.xml', 'CA7.xml',
    'CA8.xml', 'CA9.xml', 'CAA.xml', 'CAB.xml', 'CAC.xml', 'CAD.xml',
    'CAE.xml', 'CAF.xml', 'CAG.xml', 'CAH.xml', 'CAJ.xml', 'CAK.xml',
    'CAL.xml', 'CAM.xml', 'CAN.xml', 'CAP.xml', 'CAR.xml', 'CAS.xml',
    'CAT.xml', 'CAU.xml', 'CAV.xml', 'CAW.xml', 'CAX.xml', 'CAY.xml',
    'CB0.xml', 'CB1.xml', 'CB2.xml', 'CB3.xml', 'CB4.xml', 'CB5.xml',
    'CB6.xml', 'CB8.xml', 'CB9.xml', 'CBA.xml', 'CBB.xml', 'CBC.xml',
    'CBD.xml', 'CBE.xml', 'CBF.xml', 'CBG.xml', 'CBH.xml', 'CBJ.xml',
    'CBK.xml', 'CBL.xml', 'CBM.xml', 'CBN.xml', 'CBP.xml', 'CBR.xml',
    'CBT.xml', 'CBU.xml', 'CBV.xml', 'CBW.xml', 'CBX.xml', 'CBY.xml',
    'CC0.xml', 'CC1.xml', 'CC2.xml', 'CC3.xml', 'CC4.xml', 'CC5.xml',
    'CC6.xml', 'CC7.xml', 'CC8.xml', 'CC9.xml', 'CCA.xml', 'CCB.xml',
    'CCC.xml', 'CCD.xml', 'CCE.xml', 'CCF.xml', 'CCG.xml', 'CCH.xml',
    'CCJ.xml', 'CCK.xml', 'CCL.xml', 'CCM.xml', 'CCN.xml', 'CCP.xml',
    'CCR.xml', 'CCS.xml', 'CCT.xml', 'CCU.xml', 'CCV.xml', 'CCW.xml',
    'CCX.xml', 'CCY.xml', 'CD0.xml', 'CD2.xml', 'CD3.xml', 'CD4.xml',
    'CD5.xml', 'CD6.xml', 'CD8.xml', 'CD9.xml', 'CDA.xml', 'CDB.xml',
    'CDC.xml', 'CDD.xml', 'CDE.xml', 'CDF.xml', 'CDG.xml', 'CDH.xml',
    'CDJ.xml', 'CDK.xml', 'CDM.xml', 'CDN.xml', 'CDP.xml', 'CDR.xml',
    'CDS.xml', 'CDT.xml', 'CDU.xml', 'CDV.xml', 'CDW.xml', 'CDX.xml',
    'CDY.xml', 'CE0.xml', 'CE1.xml', 'CE2.xml', 'CE4.xml', 'CE5.xml',
    'CE6.xml', 'CE7.xml', 'CE8.xml', 'CE9.xml', 'CEB.xml', 'CEC.xml',
    'CED.xml', 'CEE.xml', 'CEF.xml', 'CEG.xml', 'CEH.xml', 'CEJ.xml',
    'CEK.xml', 'CEL.xml', 'CEM.xml', 'CEN.xml', 'CEP.xml', 'CER.xml',
    'CES.xml', 'CET.xml', 'CEU.xml', 'CEV.xml', 'CEW.xml', 'CEX.xml',
    'CEY.xml', 'CF4.xml', 'CF5.xml', 'CF6.xml', 'CF7.xml', 'CF8.xml',
    'CF9.xml', 'CFA.xml', 'CFB.xml', 'CFC.xml', 'CFD.xml', 'CFE.xml',
    'CFF.xml', 'CFG.xml', 'CFH.xml', 'CFJ.xml', 'CFK.xml', 'CFL.xml',
    'CFM.xml', 'CFN.xml', 'CFP.xml', 'CFR.xml', 'CFS.xml', 'CFT.xml',
    'CFU.xml', 'CFV.xml', 'CFW.xml', 'CFX.xml', 'CFY.xml', 'CG0.xml',
    'CG1.xml', 'CG2.xml', 'CG3.xml', 'CG5.xml', 'CG6.xml', 'CG7.xml',
    'CG8.xml', 'CG9.xml', 'CGA.xml', 'CGB.xml', 'CGC.xml', 'CGD.xml',
    'CGE.xml', 'CGF.xml', 'CGH.xml', 'CGJ.xml', 'CGL.xml', 'CGM.xml',
    'CGN.xml', 'CGP.xml', 'CGS.xml', 'CGT.xml', 'CGU.xml', 'CGV.xml',
    'CGW.xml', 'CGX.xml', 'CGY.xml', 'CH0.xml', 'CH1.xml', 'CH2.xml',
    'CH3.xml', 'CH4.xml', 'CH5.xml', 'CH6.xml', 'CH7.xml', 'CH8.xml',
    'CH9.xml', 'CHA.xml', 'CHB.xml', 'CHC.xml', 'CHE.xml', 'CHF.xml',
    'CHG.xml', 'CHH.xml', 'CHJ.xml', 'CHK.xml', 'CHL.xml', 'CHP.xml',
    'CHR.xml', 'CHS.xml', 'CHT.xml', 'CHU.xml', 'CHV.xml', 'CHW.xml',
    'CJ1.xml', 'CJ2.xml', 'CJ3.xml', 'CJ4.xml', 'CJ5.xml', 'CJ6.xml',
    'CJ7.xml', 'CJ8.xml', 'CJ9.xml', 'CJA.xml', 'CJB.xml', 'CJC.xml',
    'CJD.xml', 'CJE.xml', 'CJF.xml', 'CJG.xml', 'CJH.xml', 'CJJ.xml',
    'CJK.xml', 'CJM.xml', 'CJN.xml', 'CJP.xml', 'CJR.xml', 'CJS.xml',
    'CJT.xml', 'CJU.xml', 'CJX.xml', 'CK0.xml', 'CK1.xml', 'CK2.xml',
    'CK3.xml', 'CK4.xml', 'CK5.xml', 'CK6.xml', 'CK9.xml', 'CKA.xml',
    'CKB.xml', 'CKC.xml', 'CKD.xml', 'CKE.xml', 'CKF.xml', 'CKG.xml',
    'CKH.xml', 'CKJ.xml', 'CKK.xml', 'CKL.xml', 'CKM.xml', 'CKN.xml',
    'CKP.xml', 'CKR.xml', 'CKS.xml', 'CKT.xml', 'CKU.xml', 'CKV.xml',
    'CKW.xml', 'CKX.xml', 'CKY.xml', 'CL0.xml', 'CL1.xml', 'CL2.xml',
    'CL4.xml', 'CL5.xml', 'CL6.xml', 'CL7.xml', 'CL8.xml', 'CL9.xml',
    'CLA.xml', 'CLB.xml', 'CLC.xml', 'CLD.xml', 'CLE.xml', 'CLG.xml',
    'CLH.xml', 'CLK.xml', 'CLL.xml', 'CLM.xml', 'CLN.xml', 'CLP.xml',
    'CLR.xml', 'CLS.xml', 'CLT.xml', 'CLU.xml', 'CLV.xml', 'CLW.xml',
    'CLX.xml', 'CLY.xml', 'CM0.xml', 'CM1.xml', 'CM2.xml', 'CM4.xml',
    'CM5.xml', 'CM6.xml', 'CM8.xml', 'CM9.xml', 'CMA.xml', 'CMB.xml',
    'CMC.xml', 'CMD.xml', 'CME.xml', 'CMF.xml', 'CMG.xml', 'CMH.xml',
    'CMJ.xml', 'CMK.xml', 'CML.xml', 'CMM.xml', 'CMN.xml', 'CMP.xml',
    'CMR.xml', 'CMS.xml', 'CMT.xml', 'CMU.xml', 'CMW.xml', 'CMX.xml',
    'CMY.xml', 'CN0.xml', 'CN1.xml', 'CN2.xml', 'CN3.xml', 'CN4.xml',
    'CN5.xml', 'CN6.xml', 'CN9.xml', 'CNA.xml', 'CNC.xml', 'CND.xml',
    'CNE.xml', 'CNF.xml', 'CNG.xml', 'CNH.xml', 'CNJ.xml', 'CNK.xml',
    'CNL.xml', 'CNM.xml', 'CNN.xml', 'CNP.xml', 'CNR.xml', 'CNS.xml',
    'CNT.xml', 'CNU.xml', 'CNV.xml', 'CNW.xml', 'CNX.xml', 'CNY.xml',
    'CP0.xml', 'CP1.xml', 'CP2.xml', 'CP3.xml', 'CP4.xml', 'CP5.xml',
    'CP6.xml', 'CP7.xml', 'CP8.xml', 'CP9.xml', 'CPA.xml', 'CPB.xml',
    'CPC.xml', 'CPD.xml', 'CPE.xml', 'CPF.xml', 'CPG.xml', 'CPH.xml',
    'CPJ.xml', 'CPK.xml', 'CPL.xml', 'CPM.xml', 'CPN.xml', 'CPP.xml',
    'CPR.xml', 'CPS.xml', 'CPT.xml', 'CPU.xml', 'CPV.xml', 'CPW.xml',
    'CPX.xml', 'CPY.xml', 'CR0.xml', 'CR1.xml', 'CR2.xml', 'CR3.xml',
    'CR4.xml', 'CR5.xml', 'CR6.xml', 'CR7.xml', 'CR8.xml', 'CR9.xml',
    'CRA.xml', 'CRB.xml', 'CRC.xml', 'CRD.xml', 'CRE.xml', 'CRF.xml',
    'CRJ.xml', 'CRK.xml', 'CRM.xml', 'CRP.xml', 'CRR.xml', 'CRS.xml',
    'CRT.xml', 'CRU.xml', 'CRV.xml', 'CRW.xml', 'CRX.xml', 'CRY.xml',
    'CS0.xml', 'CS1.xml', 'CS2.xml', 'CS3.xml', 'CS4.xml', 'CS5.xml',
    'CS6.xml', 'CS7.xml', 'CS8.xml', 'CS9.xml', 'CSA.xml', 'CSB.xml',
    'CSC.xml', 'CSD.xml', 'CSE.xml', 'CSF.xml', 'CSG.xml', 'CSH.xml',
    'CSJ.xml', 'CSK.xml', 'CSL.xml', 'CSM.xml', 'CSN.xml', 'CSP.xml',
    'CSR.xml', 'CSS.xml', 'CST.xml', 'CSU.xml', 'CSV.xml', 'CSW.xml',
    'CSX.xml', 'CSY.xml', 'CT0.xml', 'CT1.xml', 'CT2.xml', 'CT3.xml',
    'CT4.xml', 'CT5.xml', 'CT6.xml', 'CT7.xml', 'CT8.xml', 'CT9.xml',
    'CTA.xml', 'CTB.xml', 'CTC.xml', 'CTD.xml', 'CTE.xml', 'CTF.xml',
    'CTG.xml', 'CTH.xml', 'CTJ.xml', 'CTK.xml', 'CTL.xml', 'CTM.xml',
    'CTN.xml', 'CTP.xml', 'CTR.xml', 'CTS.xml', 'CTT.xml', 'CTU.xml',
    'CTV.xml', 'CTW.xml', 'CTX.xml', 'CTY.xml', 'CU0.xml', 'CU1.xml',
    'D8Y.xml', 'D90.xml', 'D91.xml', 'D92.xml', 'D94.xml', 'D95.xml',
    'D96.xml', 'D97.xml', 'DCH.xml', 'DCJ.xml', 'DCK.xml', 'E9N.xml',
    'E9P.xml', 'E9R.xml', 'E9S.xml', 'E9T.xml', 'E9U.xml', 'E9V.xml',
    'E9W.xml', 'E9X.xml', 'E9Y.xml', 'EA0.xml', 'EA1.xml', 'EA2.xml',
    'EA3.xml', 'EA4.xml', 'EA5.xml', 'EA6.xml', 'EA7.xml', 'EA8.xml',
    'EA9.xml', 'EAA.xml', 'EAJ.xml', 'EAK.xml', 'EAM.xml', 'EAP.xml',
    'EAR.xml', 'EAS.xml', 'EAT.xml', 'EAU.xml', 'EAW.xml', 'EAX.xml',
    'EAY.xml', 'EB1.xml', 'EB2.xml', 'EB3.xml', 'EB6.xml', 'EB7.xml',
    'EB8.xml', 'EB9.xml', 'EBA.xml', 'EBB.xml', 'EBC.xml', 'EBD.xml',
    'EBE.xml', 'EBF.xml', 'EBG.xml', 'EBH.xml', 'EBJ.xml', 'EBK.xml',
    'EBL.xml', 'EBM.xml', 'EBN.xml', 'EBP.xml', 'EBR.xml', 'EBS.xml',
    'EBT.xml', 'EBU.xml', 'EBV.xml', 'EBW.xml', 'EBX.xml', 'EBY.xml',
    'EC0.xml', 'EC1.xml', 'EC2.xml', 'EC3.xml', 'EC4.xml', 'EC5.xml',
    'EC7.xml', 'EC8.xml', 'EC9.xml', 'ECB.xml', 'ECD.xml', 'ECE.xml',
    'ECF.xml', 'ECG.xml', 'ECH.xml', 'ECJ.xml', 'ECK.xml', 'ECL.xml',
    'ECM.xml', 'ECN.xml', 'ECR.xml', 'ECS.xml', 'ECT.xml', 'ECU.xml',
    'ECV.xml', 'ECX.xml', 'ECY.xml', 'ED0.xml', 'ED1.xml', 'ED2.xml',
    'ED3.xml', 'ED4.xml', 'ED5.xml', 'ED6.xml', 'ED7.xml', 'ED9.xml',
    'EDA.xml', 'EDB.xml', 'EDC.xml', 'EDD.xml', 'EDE.xml', 'EDF.xml',
    'EDG.xml', 'EDH.xml', 'EDJ.xml', 'EDK.xml', 'EDL.xml', 'EDN.xml',
    'EDP.xml', 'EDR.xml', 'EDT.xml', 'EDU.xml', 'EDY.xml', 'EE0.xml',
    'EE1.xml', 'EE2.xml', 'EE5.xml', 'EE6.xml', 'EE7.xml', 'EE8.xml',
    'EE9.xml', 'EEA.xml', 'EEB.xml', 'EEC.xml', 'EED.xml', 'EEE.xml',
    'EEF.xml', 'EEG.xml', 'EEH.xml', 'EEJ.xml', 'EEK.xml', 'EEL.xml',
    'EEM.xml', 'EEN.xml', 'EER.xml', 'EES.xml', 'EET.xml', 'EEV.xml',
    'EEW.xml', 'EEX.xml', 'EEY.xml', 'EF0.xml', 'EF1.xml', 'EF2.xml',
    'EF3.xml', 'EF4.xml', 'EF5.xml', 'EF6.xml', 'EF8.xml', 'EF9.xml',
    'EFA.xml', 'EFC.xml', 'EFD.xml', 'EFE.xml', 'EFF.xml', 'EFG.xml',
    'EFH.xml', 'EFJ.xml', 'EFN.xml', 'EFP.xml', 'EFR.xml', 'EFS.xml',
    'EFT.xml', 'EFU.xml', 'EFV.xml', 'EFW.xml', 'EFX.xml', 'EG0.xml',
    'EUR.xml', 'EUS.xml', 'EUU.xml', 'EUW.xml', 'EUX.xml', 'EUY.xml',
    'EV1.xml', 'EV3.xml', 'EV4.xml', 'EV5.xml', 'EV6.xml', 'EV8.xml',
    'EV9.xml', 'EVA.xml', 'EVB.xml', 'EVC.xml', 'EVF.xml', 'EVG.xml',
    'EVH.xml', 'EVJ.xml', 'EVK.xml', 'EVM.xml', 'EVN.xml', 'EVP.xml',
    'EVR.xml', 'EVS.xml', 'EVV.xml', 'EVW.xml', 'EVX.xml', 'EVY.xml',
    'EW1.xml', 'EW4.xml', 'EW5.xml', 'EW6.xml', 'EW7.xml', 'EW8.xml',
    'EW9.xml', 'EWA.xml', 'EWB.xml', 'EWC.xml', 'EWF.xml', 'EWG.xml',
    'EWH.xml', 'EWM.xml', 'EWR.xml', 'EWS.xml', 'EWW.xml', 'EWX.xml',
    'EX0.xml', 'EX1.xml', 'EX2.xml', 'EX4.xml', 'EX5.xml', 'EX6.xml',
    'EX7.xml', 'EX8.xml', 'F71.xml', 'F72.xml', 'F73.xml', 'F74.xml',
    'F75.xml', 'F76.xml', 'F77.xml', 'F78.xml', 'F7A.xml', 'F7C.xml',
    'F7E.xml', 'F7F.xml', 'F7G.xml', 'F7J.xml', 'F7K.xml', 'F7L.xml',
    'F7M.xml', 'F7N.xml', 'F7R.xml', 'F7S.xml', 'F7T.xml', 'F7U.xml',
    'F7V.xml', 'F7W.xml', 'F7X.xml', 'F7Y.xml', 'F81.xml', 'F82.xml',
    'F84.xml', 'F85.xml', 'F86.xml', 'F87.xml', 'F88.xml', 'F89.xml',
    'F8A.xml', 'F8B.xml', 'F8C.xml', 'F8D.xml', 'F8E.xml', 'F8F.xml',
    'F8G.xml', 'F8H.xml', 'F8J.xml', 'F8L.xml', 'F8M.xml', 'F8N.xml',
    'F8P.xml', 'F8R.xml', 'F8S.xml', 'F8U.xml', 'F98.xml', 'F99.xml',
    'F9A.xml', 'F9B.xml', 'F9C.xml', 'F9D.xml', 'F9F.xml', 'F9G.xml',
    'F9H.xml', 'F9J.xml', 'F9K.xml', 'F9L.xml', 'F9M.xml', 'F9P.xml',
    'F9R.xml', 'F9S.xml', 'F9T.xml', 'F9U.xml', 'F9V.xml', 'F9W.xml',
    'F9X.xml', 'F9Y.xml', 'FA0.xml', 'FA1.xml', 'FA2.xml', 'FA3.xml',
    'FA4.xml', 'FA6.xml', 'FA8.xml', 'FA9.xml', 'FAB.xml', 'FAC.xml',
    'FAD.xml', 'FAE.xml', 'FAF.xml', 'FAG.xml', 'FAH.xml', 'FAJ.xml',
    'FAK.xml', 'FAM.xml', 'FAN.xml', 'FAP.xml', 'FAS.xml', 'FAT.xml',
    'FAU.xml', 'FAV.xml', 'FAW.xml', 'FAY.xml', 'FB0.xml', 'FB1.xml',
    'FB2.xml', 'FB3.xml', 'FB4.xml', 'FB5.xml', 'FB6.xml', 'FB7.xml',
    'FB8.xml', 'FB9.xml', 'FBA.xml', 'FBB.xml', 'FBC.xml', 'FBD.xml',
    'FBE.xml', 'FBF.xml', 'FBG.xml', 'FBH.xml', 'FBJ.xml', 'FBK.xml',
    'FBL.xml', 'FBM.xml', 'FBN.xml', 'FBP.xml', 'FBR.xml', 'FBS.xml',
    'FBT.xml', 'FBU.xml', 'FBV.xml', 'FBW.xml', 'FBX.xml', 'FBY.xml',
    'FC0.xml', 'FC1.xml', 'FC2.xml', 'FC3.xml', 'FC4.xml', 'FC5.xml',
    'FC6.xml', 'FC7.xml', 'FC8.xml', 'FC9.xml', 'FCA.xml', 'FCB.xml',
    'FCC.xml', 'FCD.xml', 'FCE.xml', 'FCF.xml', 'FCG.xml', 'FCH.xml',
    'FCJ.xml', 'FCK.xml', 'FCL.xml', 'FCM.xml', 'FCN.xml', 'FCP.xml',
    'FCR.xml', 'FCS.xml', 'FCT.xml', 'FCU.xml', 'FCV.xml', 'FCW.xml',
    'FCX.xml', 'FCY.xml', 'FD0.xml', 'FD1.xml', 'FD2.xml', 'FD3.xml',
    'FD4.xml', 'FD5.xml', 'FD6.xml', 'FD7.xml', 'FD8.xml', 'FD9.xml',
    'FDA.xml', 'FDB.xml', 'FDC.xml', 'FDD.xml', 'FDE.xml', 'FDF.xml',
    'FDG.xml', 'FDH.xml', 'FDJ.xml', 'FDK.xml', 'FDL.xml', 'FDM.xml',
    'FDN.xml', 'FDP.xml', 'FDR.xml', 'FDS.xml', 'FDT.xml', 'FDU.xml',
    'FDV.xml', 'FDW.xml', 'FDX.xml', 'FDY.xml', 'FE0.xml', 'FE1.xml',
    'FE2.xml', 'FE3.xml', 'FE5.xml', 'FE6.xml', 'FEB.xml', 'FED.xml',
    'FEE.xml', 'FEF.xml', 'FEH.xml', 'FEJ.xml', 'FEM.xml', 'FEP.xml',
    'FES.xml', 'FET.xml', 'FEU.xml', 'FEV.xml', 'FEW.xml', 'FEX.xml',
    'FF0.xml', 'FL4.xml', 'FL5.xml', 'FL6.xml', 'FL7.xml', 'FL8.xml',
    'FL9.xml', 'FLA.xml', 'FLB.xml', 'FLC.xml', 'FLD.xml', 'FLE.xml',
    'FLF.xml', 'FLG.xml', 'FLH.xml', 'FLK.xml', 'FLL.xml', 'FLM.xml',
    'FLP.xml', 'FLR.xml', 'FLS.xml', 'FLU.xml', 'FLW.xml', 'FLX.xml',
    'FLY.xml', 'FM0.xml', 'FM1.xml', 'FM2.xml', 'FM3.xml', 'FM4.xml',
    'FM5.xml', 'FM7.xml', 'FM8.xml', 'FM9.xml', 'FMA.xml', 'FMB.xml',
    'FMC.xml', 'FMD.xml', 'FME.xml', 'FMF.xml', 'FMG.xml', 'FMH.xml',
    'FMJ.xml', 'FMK.xml', 'FML.xml', 'FMM.xml', 'FMN.xml', 'FMP.xml',
    'FMR.xml', 'FMS.xml', 'FNR.xml', 'FNS.xml', 'FNT.xml', 'FNU.xml',
    'FNW.xml', 'FNX.xml', 'FNY.xml', 'FP0.xml', 'FP1.xml', 'FP2.xml',
    'FP3.xml', 'FP4.xml', 'FP5.xml', 'FP6.xml', 'FP7.xml', 'FP8.xml',
    'FP9.xml', 'FPB.xml', 'FPC.xml', 'FPE.xml', 'FPF.xml', 'FPG.xml',
    'FPH.xml', 'FPJ.xml', 'FPK.xml', 'FPL.xml', 'FPM.xml', 'FPN.xml',
    'FPP.xml', 'FPR.xml', 'FPT.xml', 'FPU.xml', 'FPV.xml', 'FPW.xml',
    'FPX.xml', 'FPY.xml', 'FR0.xml', 'FR2.xml', 'FR3.xml', 'FR4.xml',
    'FR5.xml', 'FR6.xml', 'FR7.xml', 'FR9.xml', 'FRA.xml', 'FRB.xml',
    'FRC.xml', 'FRD.xml', 'FRE.xml', 'FRF.xml', 'FRG.xml', 'FRH.xml',
    'FRJ.xml', 'FRK.xml', 'FRL.xml', 'FRN.xml', 'FRS.xml', 'FRT.xml',
    'FRU.xml', 'FRX.xml', 'FRY.xml', 'FS0.xml', 'FS1.xml', 'FS2.xml',
    'FS3.xml', 'FS5.xml', 'FS6.xml', 'FS7.xml', 'FS8.xml', 'FSA.xml',
    'FSB.xml', 'FSC.xml', 'FSE.xml', 'FSF.xml', 'FSJ.xml', 'FSK.xml',
    'FSL.xml', 'FSN.xml', 'FSP.xml', 'FSR.xml', 'FSS.xml', 'FST.xml',
    'FSU.xml', 'FSV.xml', 'FSW.xml', 'FSY.xml', 'FT0.xml', 'FT1.xml',
    'FT2.xml', 'FT3.xml', 'FT4.xml', 'FT5.xml', 'FT6.xml', 'FT7.xml',
    'FT8.xml', 'FT9.xml', 'FTA.xml', 'FTB.xml', 'FTC.xml', 'FTD.xml',
    'FTE.xml', 'FTT.xml', 'FTU.xml', 'FTV.xml', 'FTW.xml', 'FTX.xml',
    'FTY.xml', 'FU0.xml', 'FU1.xml', 'FU2.xml', 'FU3.xml', 'FU4.xml',
    'FU5.xml', 'FU6.xml', 'FU7.xml', 'FU8.xml', 'FU9.xml', 'FUA.xml',
    'FUB.xml', 'FUE.xml', 'FUF.xml', 'FUG.xml', 'FUH.xml', 'FUJ.xml',
    'FUK.xml', 'FUL.xml', 'FUM.xml', 'FUN.xml', 'FUP.xml', 'FUR.xml',
    'FUS.xml', 'FUT.xml', 'FUU.xml', 'FX5.xml', 'FX6.xml', 'FX7.xml',
    'FX8.xml', 'FX9.xml', 'FXB.xml', 'FXC.xml', 'FXD.xml', 'FXE.xml',
    'FXF.xml', 'FXG.xml', 'FXH.xml', 'FXJ.xml', 'FXK.xml', 'FXL.xml',
    'FXM.xml', 'FXN.xml', 'FXP.xml', 'FXR.xml', 'FXT.xml', 'FXU.xml',
    'FXV.xml', 'FXW.xml', 'FXX.xml', 'FXY.xml', 'FY0.xml', 'FY1.xml',
    'FY2.xml', 'FY3.xml', 'FY4.xml', 'FY5.xml', 'FY6.xml', 'FY7.xml',
    'FY8.xml', 'FY9.xml', 'FYA.xml', 'FYB.xml', 'FYD.xml', 'FYE.xml',
    'FYF.xml', 'FYG.xml', 'FYH.xml', 'FYJ.xml', 'FYK.xml', 'FYL.xml',
    'FYM.xml', 'FYP.xml', 'FYS.xml', 'FYT.xml', 'FYV.xml', 'FYW.xml',
    'FYX.xml', 'FYY.xml', 'G00.xml', 'G01.xml', 'G02.xml', 'G03.xml',
    'G04.xml', 'G05.xml', 'G06.xml', 'G07.xml', 'G08.xml', 'G09.xml',
    'G0A.xml', 'G0C.xml', 'G0D.xml', 'G0E.xml', 'G0F.xml', 'G0G.xml',
    'G0H.xml', 'G0K.xml', 'G0L.xml', 'G0M.xml', 'G0N.xml', 'G0P.xml',
    'G0R.xml', 'G0S.xml', 'G0T.xml', 'G0U.xml', 'G0W.xml', 'G0X.xml',
    'G0Y.xml', 'G10.xml', 'G11.xml', 'G12.xml', 'G13.xml', 'G14.xml',
    'G15.xml', 'G16.xml', 'G17.xml', 'G19.xml', 'G1A.xml', 'G1C.xml',
    'G1D.xml', 'G1E.xml', 'G1F.xml', 'G1G.xml', 'G1H.xml', 'G1J.xml',
    'G1L.xml', 'G1M.xml', 'G1N.xml', 'G1R.xml', 'G1S.xml', 'G1V.xml',
    'G1W.xml', 'G1X.xml', 'G1Y.xml', 'G20.xml', 'G21.xml', 'G22.xml',
    'G23.xml', 'G24.xml', 'G25.xml', 'G26.xml', 'G27.xml', 'G28.xml',
    'G29.xml', 'G2A.xml', 'G2B.xml', 'G2C.xml', 'G2D.xml', 'G2E.xml',
    'G2F.xml', 'G2G.xml', 'G2J.xml', 'G2K.xml', 'G2L.xml', 'G2M.xml',
    'G2N.xml', 'G2P.xml', 'G2R.xml', 'G2S.xml', 'G2T.xml', 'G2V.xml',
    'G2W.xml', 'G2Y.xml', 'G30.xml', 'G31.xml', 'G32.xml', 'G33.xml',
    'G34.xml', 'G35.xml', 'G36.xml', 'G37.xml', 'G38.xml', 'G39.xml',
    'G3A.xml', 'G3B.xml', 'G3C.xml', 'G3D.xml', 'G3E.xml', 'G3F.xml',
    'G3G.xml', 'G3H.xml', 'G3J.xml', 'G3K.xml', 'G3L.xml', 'G3N.xml',
    'G3P.xml', 'G3R.xml', 'G3S.xml', 'G3T.xml', 'G3U.xml', 'G3V.xml',
    'G3W.xml', 'G3X.xml', 'G3Y.xml', 'G42.xml', 'G43.xml', 'G44.xml',
    'G45.xml', 'G46.xml', 'G47.xml', 'G48.xml', 'G49.xml', 'G4A.xml',
    'G4B.xml', 'G4C.xml', 'G4D.xml', 'G4E.xml', 'G4F.xml', 'G4G.xml',
    'G4H.xml', 'G4J.xml', 'G4K.xml', 'G4N.xml', 'G4P.xml', 'G4R.xml',
    'G4S.xml', 'G4T.xml', 'G4U.xml', 'G4V.xml', 'G4W.xml', 'G4X.xml',
    'G4Y.xml', 'G50.xml', 'G51.xml', 'G52.xml', 'G53.xml', 'G54.xml',
    'G55.xml', 'G56.xml', 'G57.xml', 'G58.xml', 'G59.xml', 'G5A.xml',
    'G5B.xml', 'G5C.xml', 'G5D.xml', 'G5E.xml', 'G5F.xml', 'G5G.xml',
    'G5H.xml', 'G5J.xml', 'G5K.xml', 'G5L.xml', 'G5M.xml', 'G5N.xml',
    'G5P.xml', 'G5R.xml', 'G5S.xml', 'G5T.xml', 'G5U.xml', 'G5V.xml',
    'G5W.xml', 'G5X.xml', 'G5Y.xml', 'G60.xml', 'G61.xml', 'G62.xml',
    'G63.xml', 'G64.xml', 'GSX.xml', 'GSY.xml', 'GT0.xml', 'GT1.xml',
    'GT2.xml', 'GT3.xml', 'GT4.xml', 'GT5.xml', 'GT6.xml', 'GT7.xml',
    'GT8.xml', 'GT9.xml', 'GTA.xml', 'GTB.xml', 'GTC.xml', 'GTD.xml',
    'GTE.xml', 'GTF.xml', 'GTG.xml', 'GTH.xml', 'GU5.xml', 'GU6.xml',
    'GU7.xml', 'GU8.xml', 'GU9.xml', 'GUA.xml', 'GUB.xml', 'GUC.xml',
    'GUD.xml', 'GUE.xml', 'GUF.xml', 'GUG.xml', 'GUH.xml', 'GUJ.xml',
    'GUK.xml', 'GUL.xml', 'GUM.xml', 'GUR.xml', 'GUS.xml', 'GUU.xml',
    'GUV.xml', 'GUW.xml', 'GUX.xml', 'GUY.xml', 'GV0.xml', 'GV1.xml',
    'GV2.xml', 'GV3.xml', 'GV5.xml', 'GV6.xml', 'GV7.xml', 'GV8.xml',
    'GV9.xml', 'GVA.xml', 'GVD.xml', 'GVF.xml', 'GVG.xml', 'GVH.xml',
    'GVJ.xml', 'GVK.xml', 'GVL.xml', 'GVM.xml', 'GVN.xml', 'GVP.xml',
    'GVR.xml', 'GVS.xml', 'GVT.xml', 'GVU.xml', 'GVW.xml', 'GVX.xml',
    'GVY.xml', 'GW0.xml', 'GW1.xml', 'GW2.xml', 'GW3.xml', 'GW4.xml',
    'GW5.xml', 'GW6.xml', 'GW8.xml', 'GW9.xml', 'GWA.xml', 'GWB.xml',
    'GWC.xml', 'GWF.xml', 'GWG.xml', 'GWH.xml', 'GWJ.xml', 'GWK.xml',
    'GWL.xml', 'GWM.xml', 'GWN.xml', 'GX0.xml', 'GX1.xml', 'GX2.xml',
    'GX3.xml', 'GX4.xml', 'GX5.xml', 'GX6.xml', 'GX7.xml', 'GX8.xml',
    'GX9.xml', 'GXA.xml', 'GXB.xml', 'GXE.xml', 'GXF.xml', 'GXG.xml',
    'GXH.xml', 'GXJ.xml', 'GXK.xml', 'GXL.xml', 'GXM.xml', 'GY4.xml',
    'GY5.xml', 'GY6.xml', 'GY7.xml', 'GY8.xml', 'GY9.xml', 'GYA.xml',
    'GYB.xml', 'GYC.xml', 'GYD.xml', 'GYE.xml', 'GYF.xml', 'GYG.xml',
    'GYH.xml', 'GYJ.xml', 'GYK.xml', 'GYL.xml', 'GYM.xml', 'GYN.xml',
    'GYP.xml', 'GYR.xml', 'GYS.xml', 'GYT.xml', 'GYU.xml', 'GYV.xml',
    'GYW.xml', 'GYX.xml', 'GYY.xml', 'H00.xml', 'H01.xml', 'H02.xml',
    'H03.xml', 'H04.xml', 'H05.xml', 'H06.xml', 'H07.xml', 'H09.xml',
    'H0A.xml', 'H0B.xml', 'H0C.xml', 'H0D.xml', 'H0E.xml', 'H0F.xml',
    'H0H.xml', 'H0J.xml', 'H0K.xml', 'H0M.xml', 'H0N.xml', 'H0P.xml',
    'H0R.xml', 'H0S.xml', 'H0U.xml', 'H0Y.xml', 'H10.xml', 'H13.xml',
    'H45.xml', 'H46.xml', 'H47.xml', 'H48.xml', 'H49.xml', 'H4A.xml',
    'H4B.xml', 'H4C.xml', 'H4D.xml', 'H4E.xml', 'H4F.xml', 'H4G.xml',
    'H4H.xml', 'H4J.xml', 'H4K.xml', 'H4L.xml', 'H4M.xml', 'H4N.xml',
    'H4P.xml', 'H4R.xml', 'H4S.xml', 'H4T.xml', 'H4U.xml', 'H4V.xml',
    'H4W.xml', 'H4X.xml', 'H4Y.xml', 'H50.xml', 'H51.xml', 'H52.xml',
    'H53.xml', 'H54.xml', 'H55.xml', 'H56.xml', 'H57.xml', 'H58.xml',
    'H59.xml', 'H5A.xml', 'H5B.xml', 'H5C.xml', 'H5D.xml', 'H5E.xml',
    'H5G.xml', 'H5H.xml', 'H5J.xml', 'H5K.xml', 'H5L.xml', 'H5M.xml',
    'H5N.xml', 'H5P.xml', 'H5R.xml', 'H5S.xml', 'H5T.xml', 'H5U.xml',
    'H5V.xml', 'H5W.xml', 'H5X.xml', 'H5Y.xml', 'H60.xml', 'H61.xml',
    'H78.xml', 'H79.xml', 'H7A.xml', 'H7B.xml', 'H7C.xml', 'H7E.xml',
    'H7F.xml', 'H7H.xml', 'H7K.xml', 'H7P.xml', 'H7R.xml', 'H7S.xml',
    'H7T.xml', 'H7U.xml', 'H7V.xml', 'H7W.xml', 'H7X.xml', 'H7Y.xml',
    'H81.xml', 'H82.xml', 'H83.xml', 'H84.xml', 'H85.xml', 'H86.xml',
    'H88.xml', 'H89.xml', 'H8A.xml', 'H8B.xml', 'H8C.xml', 'H8D.xml',
    'H8E.xml', 'H8F.xml', 'H8G.xml', 'H8H.xml', 'H8J.xml', 'H8K.xml',
    'H8L.xml', 'H8M.xml', 'H8P.xml', 'H8R.xml', 'H8S.xml', 'H8T.xml',
    'H8U.xml', 'H8V.xml', 'H8W.xml', 'H8X.xml', 'H8Y.xml', 'H90.xml',
    'H91.xml', 'H92.xml', 'H93.xml', 'H94.xml', 'H97.xml', 'H98.xml',
    'H99.xml', 'H9A.xml', 'H9C.xml', 'H9D.xml', 'H9E.xml', 'H9F.xml',
    'H9G.xml', 'H9H.xml', 'H9J.xml', 'H9L.xml', 'H9M.xml', 'H9N.xml',
    'H9R.xml', 'H9S.xml', 'H9T.xml', 'H9U.xml', 'H9V.xml', 'H9X.xml',
    'H9Y.xml', 'HA0.xml', 'HA1.xml', 'HA2.xml', 'HA3.xml', 'HA4.xml',
    'HA5.xml', 'HA6.xml', 'HA7.xml', 'HA9.xml', 'HAB.xml', 'HAC.xml',
    'HAD.xml', 'HAE.xml', 'HAF.xml', 'HAJ.xml', 'HAK.xml', 'HAL.xml',
    'HAM.xml', 'HAN.xml', 'HAP.xml', 'HAR.xml', 'HAS.xml', 'HAT.xml',
    'HAU.xml', 'HAV.xml', 'HAW.xml', 'HAX.xml', 'HAY.xml', 'HB0.xml',
    'HB1.xml', 'HB2.xml', 'HB3.xml', 'HB4.xml', 'HB5.xml', 'HB6.xml',
    'HB7.xml', 'HB8.xml', 'HB9.xml', 'HBA.xml', 'HBB.xml', 'HBC.xml',
    'HBD.xml', 'HBE.xml', 'HBG.xml', 'HBH.xml', 'HBJ.xml', 'HBK.xml',
    'HBM.xml', 'HBN.xml', 'HBP.xml', 'HBR.xml', 'HBS.xml', 'HBT.xml',
    'HBU.xml', 'HBV.xml', 'HBW.xml', 'HBX.xml', 'HBY.xml', 'HC0.xml',
    'HC1.xml', 'HC2.xml', 'HC3.xml', 'HC4.xml', 'HC5.xml', 'HC6.xml',
    'HC7.xml', 'HC8.xml', 'HC9.xml', 'HCA.xml', 'HCB.xml', 'HCC.xml',
    'HCD.xml', 'HCE.xml', 'HCG.xml', 'HCH.xml', 'HCJ.xml', 'HCK.xml',
    'HCL.xml', 'HCM.xml', 'HCN.xml', 'HCP.xml', 'HCR.xml', 'HCS.xml',
    'HCT.xml', 'HCU.xml', 'HCV.xml', 'HCW.xml', 'HCX.xml', 'HCY.xml',
    'HD0.xml', 'HD1.xml', 'HD2.xml', 'HD3.xml', 'HD4.xml', 'HD5.xml',
    'HD6.xml', 'HD7.xml', 'HD8.xml', 'HD9.xml', 'HDA.xml', 'HDB.xml',
    'HDC.xml', 'HDD.xml', 'HDH.xml', 'HDJ.xml', 'HDK.xml', 'HDL.xml',
    'HDM.xml', 'HDN.xml', 'HDP.xml', 'HDS.xml', 'HDT.xml', 'HDU.xml',
    'HDV.xml', 'HDW.xml', 'HDX.xml', 'HDY.xml', 'HE0.xml', 'HE1.xml',
    'HE2.xml', 'HE3.xml', 'HE4.xml', 'HE5.xml', 'HE6.xml', 'HE7.xml',
    'HE8.xml', 'HE9.xml', 'HEA.xml', 'HEC.xml', 'HED.xml', 'HEE.xml',
    'HEF.xml', 'HEG.xml', 'HEH.xml', 'HEJ.xml', 'HEK.xml', 'HEL.xml',
    'HEM.xml', 'HEN.xml', 'HEP.xml', 'HER.xml', 'HES.xml', 'HET.xml',
    'HEU.xml', 'HEV.xml', 'HEW.xml', 'HEX.xml', 'HEY.xml', 'HF0.xml',
    'HF1.xml', 'HF2.xml', 'HF3.xml', 'HGD.xml', 'HGE.xml', 'HGF.xml',
    'HGG.xml', 'HGH.xml', 'HGJ.xml', 'HGK.xml', 'HGL.xml', 'HGM.xml',
    'HGN.xml', 'HGP.xml', 'HGR.xml', 'HGS.xml', 'HGT.xml', 'HGU.xml',
    'HGV.xml', 'HGW.xml', 'HGX.xml', 'HGY.xml', 'HH0.xml', 'HH1.xml',
    'HH2.xml', 'HH3.xml', 'HH4.xml', 'HH5.xml', 'HH6.xml', 'HH7.xml',
    'HH8.xml', 'HH9.xml', 'HHA.xml', 'HHB.xml', 'HHC.xml', 'HHD.xml',
    'HHE.xml', 'HHF.xml', 'HHG.xml', 'HHH.xml', 'HHJ.xml', 'HHK.xml',
    'HHL.xml', 'HHM.xml', 'HHN.xml', 'HHP.xml', 'HHR.xml', 'HHS.xml',
    'HHT.xml', 'HHU.xml', 'HHV.xml', 'HHW.xml', 'HHX.xml', 'HHY.xml',
    'HJ0.xml', 'HJ1.xml', 'HJ2.xml', 'HJ3.xml', 'HJ4.xml', 'HJ5.xml',
    'HJ6.xml', 'HJ7.xml', 'HJ8.xml', 'HJ9.xml', 'HJA.xml', 'HJB.xml',
    'HJC.xml', 'HJD.xml', 'HJE.xml', 'HJG.xml', 'HJH.xml', 'HJJ.xml',
    'HJK.xml', 'HJL.xml', 'HJM.xml', 'HJN.xml', 'HJP.xml', 'HJR.xml',
    'HJS.xml', 'HJT.xml', 'HJU.xml', 'HJV.xml', 'HJW.xml', 'HJY.xml',
    'HK0.xml', 'HK1.xml', 'HK2.xml', 'HK3.xml', 'HK4.xml', 'HK5.xml',
    'HK7.xml', 'HK8.xml', 'HK9.xml', 'HKA.xml', 'HKC.xml', 'HKD.xml',
    'HKE.xml', 'HKF.xml', 'HKG.xml', 'HKH.xml', 'HKJ.xml', 'HKK.xml',
    'HKL.xml', 'HKM.xml', 'HKN.xml', 'HKP.xml', 'HKR.xml', 'HKS.xml',
    'HKT.xml', 'HKU.xml', 'HKV.xml', 'HKW.xml', 'HKX.xml', 'HKY.xml',
    'HL0.xml', 'HL1.xml', 'HL2.xml', 'HL3.xml', 'HL4.xml', 'HL5.xml',
    'HL6.xml', 'HL7.xml', 'HL8.xml', 'HL9.xml', 'HLA.xml', 'HLB.xml',
    'HLC.xml', 'HLD.xml', 'HLE.xml', 'HLF.xml', 'HLG.xml', 'HLH.xml',
    'HLJ.xml', 'HLK.xml', 'HLL.xml', 'HLM.xml', 'HLN.xml', 'HLP.xml',
    'HLR.xml', 'HLS.xml', 'HLT.xml', 'HLU.xml', 'HLW.xml', 'HLX.xml',
    'HLY.xml', 'HM2.xml', 'HM4.xml', 'HM5.xml', 'HM6.xml', 'HM7.xml',
    'HMA.xml', 'HMD.xml', 'HMG.xml', 'HMH.xml', 'HMJ.xml', 'HMK.xml',
    'HML.xml', 'HMM.xml', 'HMN.xml', 'HMP.xml', 'HNJ.xml', 'HNK.xml',
    'HNL.xml', 'HNM.xml', 'HNP.xml', 'HNR.xml', 'HNS.xml', 'HNT.xml',
    'HNU.xml', 'HNV.xml', 'HNW.xml', 'HNX.xml', 'HP0.xml', 'HP1.xml',
    'HP2.xml', 'HP3.xml', 'HP4.xml', 'HP5.xml', 'HP6.xml', 'HP7.xml',
    'HP8.xml', 'HP9.xml', 'HPA.xml', 'HPB.xml', 'HPC.xml', 'HPD.xml',
    'HPE.xml', 'HPF.xml', 'HPG.xml', 'HPH.xml', 'HPJ.xml', 'HPK.xml',
    'HPL.xml', 'HPM.xml', 'HPN.xml', 'HPP.xml', 'HPR.xml', 'HPS.xml',
    'HPT.xml', 'HPU.xml', 'HPV.xml', 'HPW.xml', 'HPX.xml', 'HPY.xml',
    'HR0.xml', 'HR1.xml', 'HR3.xml', 'HR4.xml', 'HR5.xml', 'HR7.xml',
    'HR8.xml', 'HR9.xml', 'HRA.xml', 'HRB.xml', 'HRC.xml', 'HRD.xml',
    'HRE.xml', 'HRF.xml', 'HRG.xml', 'HRH.xml', 'HRJ.xml', 'HRK.xml',
    'HRL.xml', 'HRM.xml', 'HRN.xml', 'HRP.xml', 'HRR.xml', 'HRS.xml',
    'HRT.xml', 'HRU.xml', 'HRV.xml', 'HRW.xml', 'HRX.xml', 'HRY.xml',
    'HS0.xml', 'HS1.xml', 'HS2.xml', 'HS3.xml', 'HS4.xml', 'HS7.xml',
    'HS8.xml', 'HS9.xml', 'HSA.xml', 'HSB.xml', 'HSC.xml', 'HSD.xml',
    'HSE.xml', 'HSF.xml', 'HSG.xml', 'HSH.xml', 'HSJ.xml', 'HSK.xml',
    'HSL.xml', 'HSM.xml', 'HSN.xml', 'HSP.xml', 'HSR.xml', 'HSS.xml',
    'HST.xml', 'HSU.xml', 'HSW.xml', 'HSX.xml', 'HSY.xml', 'HT0.xml',
    'HT1.xml', 'HT2.xml', 'HT3.xml', 'HT4.xml', 'HT5.xml', 'HT6.xml',
    'HT7.xml', 'HT8.xml', 'HT9.xml', 'HTA.xml', 'HTC.xml', 'HTD.xml',
    'HTE.xml', 'HTF.xml', 'HTG.xml', 'HTH.xml', 'HTJ.xml', 'HTK.xml',
    'HTL.xml', 'HTM.xml', 'HTN.xml', 'HTP.xml', 'HTR.xml', 'HTS.xml',
    'HTT.xml', 'HTU.xml', 'HTV.xml', 'HTW.xml', 'HTX.xml', 'HTY.xml',
    'HU0.xml', 'HU1.xml', 'HU2.xml', 'HU3.xml', 'HU4.xml', 'HU5.xml',
    'HU6.xml', 'HU7.xml', 'HU8.xml', 'HU9.xml', 'HUA.xml', 'HUB.xml',
    'HUC.xml', 'HUD.xml', 'HUE.xml', 'HUF.xml', 'HUG.xml', 'HUH.xml',
    'HUJ.xml', 'HUK.xml', 'HUL.xml', 'HUM.xml', 'HUN.xml', 'HUP.xml',
    'HUR.xml', 'HUS.xml', 'HUT.xml', 'HUU.xml', 'HUV.xml', 'HUW.xml',
    'HUX.xml', 'HUY.xml', 'HV0.xml', 'HV1.xml', 'HV2.xml', 'HV3.xml',
    'HV4.xml', 'HV5.xml', 'HV6.xml', 'HV7.xml', 'HV8.xml', 'HV9.xml',
    'HVA.xml', 'HVB.xml', 'HVC.xml', 'HVD.xml', 'HVE.xml', 'HVF.xml',
    'HVG.xml', 'HVH.xml', 'HVJ.xml', 'HVK.xml', 'HW8.xml', 'HW9.xml',
    'HWA.xml', 'HWB.xml', 'HWC.xml', 'HWD.xml', 'HWE.xml', 'HWF.xml',
    'HWG.xml', 'HWH.xml', 'HWK.xml', 'HWL.xml', 'HWM.xml', 'HWN.xml',
    'HWP.xml', 'HWS.xml', 'HWT.xml', 'HWU.xml', 'HWV.xml', 'HWW.xml',
    'HWX.xml', 'HWY.xml', 'HX0.xml', 'HX1.xml', 'HX2.xml', 'HX3.xml',
    'HX4.xml', 'HX5.xml', 'HX6.xml', 'HX7.xml', 'HX8.xml', 'HX9.xml',
    'HXA.xml', 'HXB.xml', 'HXC.xml', 'HXD.xml', 'HXE.xml', 'HXF.xml',
    'HXG.xml', 'HXH.xml', 'HXJ.xml', 'HXK.xml', 'HXL.xml', 'HXM.xml',
    'HXN.xml', 'HXP.xml', 'HXR.xml', 'HXS.xml', 'HXT.xml', 'HXU.xml',
    'HXV.xml', 'HXW.xml', 'HXX.xml', 'HXY.xml', 'HY0.xml', 'HY1.xml',
    'HY2.xml', 'HY3.xml', 'HY4.xml', 'HY5.xml', 'HY6.xml', 'HY7.xml',
    'HY8.xml', 'HY9.xml', 'HYA.xml', 'HYB.xml', 'HYC.xml', 'HYD.xml',
    'HYE.xml', 'HYF.xml', 'HYG.xml', 'HYH.xml', 'HYJ.xml', 'HYK.xml',
    'HYL.xml', 'HYM.xml', 'HYN.xml', 'HYP.xml', 'HYR.xml', 'HYS.xml',
    'HYT.xml', 'HYU.xml', 'HYV.xml', 'HYW.xml', 'HYX.xml', 'HYY.xml',
    'J0P.xml', 'J0R.xml', 'J0T.xml', 'J0U.xml', 'J0V.xml', 'J0W.xml',
    'J0X.xml', 'J0Y.xml', 'J10.xml', 'J11.xml', 'J12.xml', 'J13.xml',
    'J14.xml', 'J15.xml', 'J16.xml', 'J17.xml', 'J18.xml', 'J19.xml',
    'J1A.xml', 'J1B.xml', 'J1C.xml', 'J1D.xml', 'J1E.xml', 'J1F.xml',
    'J1G.xml', 'J1H.xml', 'J1J.xml', 'J1K.xml', 'J1L.xml', 'J1M.xml',
    'J1N.xml', 'J1P.xml', 'J1R.xml', 'J1S.xml', 'J1T.xml', 'J1U.xml',
    'J1V.xml', 'J1W.xml', 'J1X.xml', 'J1Y.xml', 'J20.xml', 'J21.xml',
    'J22.xml', 'J23.xml', 'J24.xml', 'J25.xml', 'J26.xml', 'J27.xml',
    'J28.xml', 'J29.xml', 'J2A.xml', 'J2B.xml', 'J2C.xml', 'J2D.xml',
    'J2E.xml', 'J2F.xml', 'J2G.xml', 'J2H.xml', 'J2J.xml', 'J2K.xml',
    'J2L.xml', 'J2N.xml', 'J2P.xml', 'J2R.xml', 'J2S.xml', 'J2T.xml',
    'J2U.xml', 'J2V.xml', 'J2W.xml', 'J2X.xml', 'J2Y.xml', 'J30.xml',
    'J31.xml', 'J32.xml', 'J33.xml', 'J34.xml', 'J35.xml', 'J36.xml',
    'J37.xml', 'J38.xml', 'J39.xml', 'J3A.xml', 'J3B.xml', 'J3C.xml',
    'J3D.xml', 'J3E.xml', 'J3F.xml', 'J3G.xml', 'J3H.xml', 'J3J.xml',
    'J3K.xml', 'J3L.xml', 'J3M.xml', 'J3N.xml', 'J3P.xml', 'J3R.xml',
    'J3S.xml', 'J3T.xml', 'J3U.xml', 'J3V.xml', 'J3W.xml', 'J3X.xml',
    'J3Y.xml', 'J40.xml', 'J41.xml', 'J42.xml', 'J43.xml', 'J44.xml',
    'J45.xml', 'J52.xml', 'J53.xml', 'J54.xml', 'J55.xml', 'J56.xml',
    'J57.xml', 'J59.xml', 'J5A.xml', 'J5B.xml', 'J5C.xml', 'J5D.xml',
    'J5E.xml', 'J5F.xml', 'J5G.xml', 'J5H.xml', 'J5J.xml', 'J5K.xml',
    'J5L.xml', 'J5M.xml', 'J5N.xml', 'J5P.xml', 'J6N.xml', 'J6P.xml',
    'J6R.xml', 'J6S.xml', 'J6T.xml', 'J6U.xml', 'J6V.xml', 'J6W.xml',
    'J6X.xml', 'J6Y.xml', 'J70.xml', 'J71.xml', 'J72.xml', 'J73.xml',
    'J74.xml', 'J75.xml', 'J76.xml', 'J77.xml', 'J78.xml', 'J79.xml',
    'J7A.xml', 'J7B.xml', 'J7C.xml', 'J7D.xml', 'J7E.xml', 'J7F.xml',
    'J7G.xml', 'J7H.xml', 'J7J.xml', 'J7K.xml', 'J7L.xml', 'J7M.xml',
    'J7P.xml', 'J7R.xml', 'J7S.xml', 'J7T.xml', 'J7U.xml', 'J7V.xml',
    'J7W.xml', 'J7X.xml', 'J7Y.xml', 'J80.xml', 'J81.xml', 'J82.xml',
    'J83.xml', 'J84.xml', 'J85.xml', 'J86.xml', 'J87.xml', 'J88.xml',
    'J89.xml', 'J8B.xml', 'J8D.xml', 'J8F.xml', 'J8G.xml', 'J8J.xml',
    'J8K.xml', 'J8M.xml', 'J8Y.xml', 'J90.xml', 'J91.xml', 'J92.xml',
    'J94.xml', 'J95.xml', 'J97.xml', 'J98.xml', 'J99.xml', 'J9A.xml',
    'J9B.xml', 'J9C.xml', 'J9D.xml', 'J9E.xml', 'J9F.xml', 'J9G.xml',
    'J9H.xml', 'J9J.xml', 'J9K.xml', 'J9L.xml', 'J9M.xml', 'J9N.xml',
    'J9P.xml', 'J9R.xml', 'J9S.xml', 'J9T.xml', 'J9U.xml', 'J9V.xml',
    'J9X.xml', 'J9Y.xml', 'JA0.xml', 'JA1.xml', 'JA2.xml', 'JA3.xml',
    'JA4.xml', 'JA5.xml', 'JA6.xml', 'JA8.xml', 'JA9.xml', 'JAA.xml',
    'JAB.xml', 'JAC.xml', 'JAD.xml', 'JAE.xml', 'JJ6.xml', 'JJ7.xml',
    'JJ8.xml', 'JJ9.xml', 'JJA.xml', 'JJC.xml', 'JJD.xml', 'JJE.xml',
    'JJF.xml', 'JJG.xml', 'JJH.xml', 'JJJ.xml', 'JJL.xml', 'JJN.xml',
    'JJP.xml', 'JJR.xml', 'JJS.xml', 'JJT.xml', 'JJU.xml', 'JJV.xml',
    'JJW.xml', 'JJX.xml', 'JJY.xml', 'JK0.xml', 'JK1.xml', 'JK2.xml',
    'JK5.xml', 'JK6.xml', 'JK7.xml', 'JK8.xml', 'JK9.xml', 'JN6.xml',
    'JN7.xml', 'JN8.xml', 'JNB.xml', 'JND.xml', 'JNE.xml', 'JNF.xml',
    'JNG.xml', 'JNH.xml', 'JNJ.xml', 'JNK.xml', 'JNL.xml', 'JNM.xml',
    'JNN.xml', 'JNP.xml', 'JNR.xml', 'JNS.xml', 'JNT.xml', 'JNU.xml',
    'JNV.xml', 'JNW.xml', 'JNX.xml', 'JNY.xml', 'JP0.xml', 'JP1.xml',
    'JP2.xml', 'JP3.xml', 'JP4.xml', 'JP5.xml', 'JP6.xml', 'JP7.xml',
    'JP8.xml', 'JS7.xml', 'JS8.xml', 'JS9.xml', 'JSA.xml', 'JSC.xml',
    'JSD.xml', 'JSE.xml', 'JSF.xml', 'JSG.xml', 'JSH.xml', 'JSJ.xml',
    'JSK.xml', 'JSL.xml', 'JSM.xml', 'JSN.xml', 'JST.xml', 'JSU.xml',
    'JSV.xml', 'JSY.xml', 'JT0.xml', 'JT1.xml', 'JT2.xml', 'JT3.xml',
    'JT4.xml', 'JT5.xml', 'JT7.xml', 'JT8.xml', 'JT9.xml', 'JTA.xml',
    'JTB.xml', 'JTC.xml', 'JTD.xml', 'JTE.xml', 'JTF.xml', 'JWA.xml',
    'JXG.xml', 'JXH.xml', 'JXJ.xml', 'JXK.xml', 'JXL.xml', 'JXM.xml',
    'JXN.xml', 'JXP.xml', 'JXS.xml', 'JXT.xml', 'JXU.xml', 'JXV.xml',
    'JXW.xml', 'JXX.xml', 'JXY.xml', 'JY0.xml', 'JY1.xml', 'JY2.xml',
    'JY3.xml', 'JY4.xml', 'JY5.xml', 'JY6.xml', 'JY7.xml', 'JY8.xml',
    'JY9.xml', 'JYA.xml', 'JYB.xml', 'JYC.xml', 'JYD.xml', 'JYE.xml',
    'JYF.xml', 'JYL.xml', 'JYM.xml', 'JYN.xml', 'K1B.xml', 'K1C.xml',
    'K1D.xml', 'K1E.xml', 'K1F.xml', 'K1G.xml', 'K1H.xml', 'K1J.xml',
    'K1K.xml', 'K1L.xml', 'K1M.xml', 'K1N.xml', 'K1P.xml', 'K1R.xml',
    'K1S.xml', 'K1T.xml', 'K1U.xml', 'K1V.xml', 'K1W.xml', 'K1X.xml',
    'K1Y.xml', 'K20.xml', 'K21.xml', 'K22.xml', 'K23.xml', 'K24.xml',
    'K25.xml', 'K26.xml', 'K27.xml', 'K28.xml', 'K29.xml', 'K2A.xml',
    'K2B.xml', 'K2C.xml', 'K2D.xml', 'K2E.xml', 'K2F.xml', 'K2G.xml',
    'K2H.xml', 'K2J.xml', 'K2K.xml', 'K2L.xml', 'K2M.xml', 'K2N.xml',
    'K2P.xml', 'K2R.xml', 'K2S.xml', 'K2T.xml', 'K2U.xml', 'K2V.xml',
    'K2W.xml', 'K2X.xml', 'K2Y.xml', 'K30.xml', 'K31.xml', 'K32.xml',
    'K33.xml', 'K34.xml', 'K35.xml', 'K36.xml', 'K37.xml', 'K38.xml',
    'K39.xml', 'K3A.xml', 'K3B.xml', 'K3C.xml', 'K3D.xml', 'K3E.xml',
    'K3F.xml', 'K3G.xml', 'K3H.xml', 'K3J.xml', 'K3K.xml', 'K3L.xml',
    'K3M.xml', 'K3N.xml', 'K3P.xml', 'K3R.xml', 'K3S.xml', 'K3T.xml',
    'K3U.xml', 'K3V.xml', 'K3W.xml', 'K3X.xml', 'K3Y.xml', 'K40.xml',
    'K41.xml', 'K42.xml', 'K43.xml', 'K44.xml', 'K45.xml', 'K46.xml',
    'K47.xml', 'K48.xml', 'K49.xml', 'K4A.xml', 'K4B.xml', 'K4C.xml',
    'K4D.xml', 'K4E.xml', 'K4F.xml', 'K4G.xml', 'K4H.xml', 'K4J.xml',
    'K4K.xml', 'K4L.xml', 'K4M.xml', 'K4N.xml', 'K4P.xml', 'K4R.xml',
    'K4S.xml', 'K4T.xml', 'K4U.xml', 'K4V.xml', 'K4W.xml', 'K4X.xml',
    'K4Y.xml', 'K50.xml', 'K51.xml', 'K52.xml', 'K53.xml', 'K54.xml',
    'K55.xml', 'K56.xml', 'K57.xml', 'K58.xml', 'K59.xml', 'K5A.xml',
    'K5B.xml', 'K5C.xml', 'K5D.xml', 'K5E.xml', 'K5F.xml', 'K5G.xml',
    'K5H.xml', 'K5J.xml', 'K5K.xml', 'K5L.xml', 'K5M.xml', 'K5N.xml',
    'K5P.xml', 'K5R.xml', 'K5S.xml', 'K5T.xml', 'K5U.xml', 'K5V.xml',
    'K5W.xml', 'K5X.xml', 'K5Y.xml', 'K60.xml', 'K61.xml', 'K62.xml',
    'K63.xml', 'K64.xml', 'K65.xml', 'K66.xml', 'K67.xml', 'K68.xml',
    'K69.xml', 'K6A.xml', 'K6B.xml', 'K6C.xml', 'K6D.xml', 'K6E.xml',
    'K6F.xml', 'K6G.xml', 'K6H.xml', 'K6J.xml', 'K6K.xml', 'K6L.xml',
    'K6M.xml', 'K6N.xml', 'K6P.xml', 'K6R.xml', 'K6S.xml', 'K6T.xml',
    'K6U.xml', 'K6V.xml', 'K6W.xml', 'K6X.xml', 'K6Y.xml', 'K70.xml',
    'K71.xml', 'K73.xml', 'K74.xml', 'K75.xml', 'K76.xml', 'K77.xml',
    'K78.xml', 'K79.xml', 'K7D.xml', 'K7E.xml', 'K7F.xml', 'K7G.xml',
    'K8R.xml', 'K8S.xml', 'K8T.xml', 'K8U.xml', 'K8V.xml', 'K8W.xml',
    'K8X.xml', 'K8Y.xml', 'K90.xml', 'K91.xml', 'K92.xml', 'K93.xml',
    'K94.xml', 'K95.xml', 'K96.xml', 'K97.xml', 'K98.xml', 'K99.xml',
    'K9A.xml', 'K9B.xml', 'K9C.xml', 'K9D.xml', 'K9E.xml', 'K9F.xml',
    'K9G.xml', 'K9H.xml', 'K9J.xml', 'K9K.xml', 'K9L.xml', 'K9M.xml',
    'K9N.xml', 'K9P.xml', 'K9R.xml', 'K9S.xml', 'K9T.xml', 'K9U.xml',
    'K9V.xml', 'K9W.xml', 'K9X.xml', 'K9Y.xml', 'KA0.xml', 'KA1.xml',
    'KA2.xml', 'KA3.xml', 'KA4.xml', 'KA5.xml', 'KA6.xml', 'KA7.xml',
    'KA8.xml', 'KA9.xml', 'KAA.xml', 'KAB.xml', 'KAC.xml', 'KAD.xml',
    'KAE.xml', 'KAF.xml', 'KAG.xml', 'KAH.xml', 'KAJ.xml', 'KAK.xml',
    'KAL.xml', 'KAM.xml', 'KAN.xml', 'KAP.xml', 'KAR.xml', 'KAS.xml',
    'KAT.xml', 'KAU.xml', 'KAV.xml', 'KAX.xml', 'KAY.xml', 'KB0.xml',
    'KB1.xml', 'KB2.xml', 'KB3.xml', 'KB4.xml', 'KB5.xml', 'KB6.xml',
    'KB7.xml', 'KB8.xml', 'KB9.xml', 'KBA.xml', 'KBB.xml', 'KBC.xml',
    'KBD.xml', 'KBE.xml', 'KBF.xml', 'KBG.xml', 'KBH.xml', 'KBJ.xml',
    'KBK.xml', 'KBL.xml', 'KBM.xml', 'KBN.xml', 'KBP.xml', 'KBR.xml',
    'KBS.xml', 'KBT.xml', 'KBU.xml', 'KBV.xml', 'KBW.xml', 'KBX.xml',
    'KBY.xml', 'KC0.xml', 'KC1.xml', 'KC2.xml', 'KC3.xml', 'KC4.xml',
    'KC5.xml', 'KC6.xml', 'KC7.xml', 'KC8.xml', 'KC9.xml', 'KCA.xml',
    'KCB.xml', 'KCC.xml', 'KCD.xml', 'KCE.xml', 'KCF.xml', 'KCG.xml',
    'KCH.xml', 'KCJ.xml', 'KCK.xml', 'KCL.xml', 'KCM.xml', 'KCN.xml',
    'KCP.xml', 'KCR.xml', 'KCS.xml', 'KCT.xml', 'KCU.xml', 'KCV.xml',
    'KCW.xml', 'KCX.xml', 'KCY.xml', 'KD0.xml', 'KD1.xml', 'KD2.xml',
    'KD3.xml', 'KD4.xml', 'KD5.xml', 'KD6.xml', 'KD7.xml', 'KD8.xml',
    'KD9.xml', 'KDA.xml', 'KDB.xml', 'KDC.xml', 'KDD.xml', 'KDE.xml',
    'KDF.xml', 'KDG.xml', 'KDH.xml', 'KDJ.xml', 'KDK.xml', 'KDL.xml',
    'KDM.xml', 'KDN.xml', 'KDP.xml', 'KDR.xml', 'KDS.xml', 'KDT.xml',
    'KDU.xml', 'KDV.xml', 'KDW.xml', 'KDX.xml', 'KDY.xml', 'KE0.xml',
    'KE1.xml', 'KE2.xml', 'KE3.xml', 'KE4.xml', 'KE5.xml', 'KE6.xml',
    'KEB.xml', 'KGH.xml', 'KGK.xml', 'KGL.xml', 'KGM.xml', 'KGN.xml',
    'KGP.xml', 'KGR.xml', 'KGS.xml', 'KGT.xml', 'KGU.xml', 'KGV.xml',
    'KGW.xml', 'KGX.xml', 'KJS.xml', 'KJT.xml', 'KJU.xml', 'KJV.xml',
    'KLE.xml', 'KLF.xml', 'KLG.xml', 'KLH.xml', 'KLS.xml', 'KLT.xml',
    'KLV.xml', 'KLW.xml', 'KLX.xml', 'KLY.xml', 'KM0.xml', 'KM1.xml',
    'KM2.xml', 'KM3.xml', 'KM4.xml', 'KM5.xml', 'KM6.xml', 'KM7.xml',
    'KM8.xml', 'KN1.xml', 'KN2.xml', 'KN3.xml', 'KN6.xml', 'KN7.xml',
    'KN8.xml', 'KN9.xml', 'KNA.xml', 'KNB.xml', 'KNC.xml', 'KND.xml',
    'KNF.xml', 'KNG.xml', 'KNH.xml', 'KNJ.xml', 'KNK.xml', 'KNR.xml',
    'KNS.xml', 'KNT.xml', 'KNU.xml', 'KNV.xml', 'KNW.xml', 'KNY.xml',
    'KP0.xml', 'KP1.xml', 'KP2.xml', 'KP3.xml', 'KP4.xml', 'KP5.xml',
    'KP6.xml', 'KP7.xml', 'KP8.xml', 'KP9.xml', 'KPA.xml', 'KPB.xml',
    'KPC.xml', 'KPD.xml', 'KPE.xml', 'KPF.xml', 'KPG.xml', 'KPH.xml',
    'KPJ.xml', 'KPK.xml', 'KPL.xml', 'KPM.xml', 'KPN.xml', 'KPP.xml',
    'KPR.xml', 'KPS.xml', 'KPT.xml', 'KPU.xml', 'KPV.xml', 'KPW.xml',
    'KPX.xml', 'KPY.xml', 'KR0.xml', 'KR1.xml', 'KR2.xml', 'KRE.xml',
    'KRF.xml', 'KRG.xml', 'KRH.xml', 'KRJ.xml', 'KRK.xml', 'KRL.xml',
    'KRM.xml', 'KRN.xml', 'KRP.xml', 'KRR.xml', 'KRS.xml', 'KRT.xml',
    'KRU.xml', 'KRV.xml', 'KRW.xml', 'KRX.xml', 'KRY.xml', 'KS0.xml',
    'KS1.xml', 'KS2.xml', 'KS3.xml', 'KS4.xml', 'KS5.xml', 'KS6.xml',
    'KS7.xml', 'KS8.xml', 'KS9.xml', 'KSN.xml', 'KSP.xml', 'KSR.xml',
    'KSS.xml', 'KST.xml', 'KSU.xml', 'KSV.xml', 'KSW.xml']

    def __init__(self, gui=False, *args):
        """
        Initialize the corpus builder.
        
        During initialization, the database table structure is defined.
        
        All corpus installers have to call the inherited initializer
        :func:`BaseCorpusBuilder.__init__`.
        
        Parameters
        ----------
        gui : bool
            True if the graphical installer is used, and False if the 
            installer runs on the console.
        """
        super(BuilderClass, self).__init__(gui, *args)

        # Add the main lexicon table. Each row in this table represents a
        # word-form that occurs in the corpus. It has the following columns:
        #
        # WordId
        # An int value containing the unique identifier of this word-form.
        #
        # Word
        # A text value containing the orthographic representation of this
        # word-form.
        #
        # Lemma
        # A text value containing the unique identifier of the lemma that
        # is associated with this word-form.
        # 
        # C5_POS
        # A text value containing the part-of-speech label of this 
        # word-form. The labels are from the CLAWS5 tag set.
        #
        # Lemma_POS
        # A text value containing the part-of-speech code of the lemma. This
        # code set is much more restricted than the CLAWS5 tag set.
        #
        # Type
        # An enum containing the type of the token.

        self.word_table = "Lexicon"
        self.word_id = "Word_id"
        self.word_label = "Word"
        self.word_lemma = "Lemma"
        self.word_pos = "C5_POS"
        self.word_lemma_pos = "Lemma_POS"
        self.word_type = "Type"

        self.create_table_description(self.word_table,
            [Identifier(self.word_id, "MEDIUMINT(7) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(131) NOT NULL"),
             Column(self.word_lemma, "VARCHAR(131) NOT NULL"),
             Column(self.word_pos, "ENUM('AJ0','AJ0-AV0','AJ0-NN1','AJ0-VVD','AJ0-VVG','AJ0-VVN','AJC','AJS','AT0','AV0','AV0-AJ0','AVP','AVP-PRP','AVQ','AVQ-CJS','CJC','CJS','CJS-AVQ','CJS-PRP','CJT','CJT-DT0','CRD','CRD-PNI','DPS','DT0','DT0-CJT','DTQ','EX0','ITJ','NN0','NN1','NN1-AJ0','NN1-NP0','NN1-VVB','NN1-VVG','NN2','NN2-VVZ','NP0','NP0-NN1','ORD','PNI','PNI-CRD','PNP','PNQ','PNX','POS','PRF','PRP','PRP-AVP','PRP-CJS','PUNCT','TO0','UNC','VBB','VBD','VBG','VBI','VBN','VBZ','VDB','VDD','VDG','VDI','VDN','VDZ','VHB','VHD','VHG','VHI','VHN','VHZ','VM0','VVB','VVB-NN1','VVD','VVD-AJ0','VVD-VVN','VVG','VVG-AJ0','VVG-NN1','VVI','VVN','VVN-AJ0','VVN-VVD','VVZ','VVZ-NN2','XX0','ZZ0') NOT NULL"), 
             Column(self.word_lemma_pos, "ENUM('ADJ','ADV','ART','CONJ','INTERJ','PREP','PRON','PUNCT','SUBST','UNC','VERB') NOT NULL"),
             Column(self.word_type, "ENUM('c', 'w') NOT NULL")])

        # Add the file table. Each row in this table represents an XML file
        # that has been incorporated into the corpus. Each token from the
        # corpus table is linked to exactly one file from this table, and
        # more than one token may be linked to each file in this table.
        # The table contains the following columns:
        #
        # id
        # An int value containing the unique identifier of this file.
        # 
        # Filename
        # A text value containing the name of this XML file.
        #
        # Path
        # A text value containing the full path that points to this XML file.
        
        self.file_table = "Files"
        self.file_id = "File_id"
        self.file_name = "Filename"
        self.file_path = "Path"

        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "SMALLINT(4) UNSIGNED NOT NULL"),
             Column(self.file_path, "TINYTEXT NOT NULL"),
             Column(self.file_name, "CHAR(7) NOT NULL")])

        # Add the speaker table. Each row in this table represents a speaker
        # who has contributed to the recordings in the BNC. Each sentence
        # from a spoken text is linked to exactly one speaker from this
        # table, and more than one sentence may be linked to each speaker.
        # The table contains the following columns:
        #
        # Speaker
        # A string value containing the label used in the BNC to refer to 
        # this speaker. It is used in the who attributes of the XML <u> 
        # elements as well as the xml:id attribute of the <person> element 
        # in the the profile description statement.
        #
        # Age
        # An string value containing the age of the speaker, taken from the 
        # <age> element within the <person> element if present, otherwise
        # from the age attribute of the <person> element if present, or 
        # empty otherwise.
        # 
        # Sex
        # A string value containing the sex of the speaker, taken from the 
        # sex attribute of the <person> element if present, or empty 
        # otherwise.
        
        self.speaker_table = "Speakers"
        self.speaker_id = "Speaker_id"
        self.speaker_label = "Speaker"
        self.speaker_age = "Age"
        self.speaker_sex = "Sex"
        
        self.create_table_description(self.speaker_table,
            [Identifier(self.speaker_id, "SMALLINT(4) UNSIGNED NOT NULL"),
             Column(self.speaker_label, "VARCHAR(8) NOT NULL"),
             Column(self.speaker_age, "ENUM('','-82+','0','1','10','10+','11','12','13','13+','14','14+','15','16','17','17+','18','19','2','20','20+','21','21+','22','23','24','25','25+','26','27','28','29','3','3+','30','30+','31','32','33','34','35','35+','36','37','38','39','4','40','40+','41','42','43','44','45','45+','46','46+','47','48','48+','49','5','50','50+','51','52','53','54','55','55+','56','57','58','59','6','60','60+','61','62','63','64','65','65+','66','67','68','69','7','70','70+','71','72','73','74','75','75+','76','77','78','79','8','80','80+','81','82','84','86','87','89','9','92','93','95') NOT NULL"),
             Column(self.speaker_sex, "ENUM('f','m','u') NOT NULL")])
       
        # Add the sentence table. Each row in this table represents a 
        # sentence from the XML file. Each token in the corpus table is 
        # linked to exactly one sentence from this table, and more than one
        # tokens may be linked to each sentence. The table contains the 
        # following columns:
        #
        # id
        # An int value containing the unique identifier of this file.

        self.sentence_table = "Sentences"
        self.sentence_id = "Sentence_id"
        self.sentence_label = "Sentence_id"

        self.create_table_description(self.sentence_table,
            [Identifier(self.sentence_id, "SMALLINT(4) UNSIGNED NOT NULL")])

        # Add the source table. Each row in this table represents a BNC 
        # source. Each sentence from the sentence table is linked to exactly
        # one source from this table, and more than one sentences may be
        # linked to each source. The table contains the following columns:
        #
        # id
        # An int value containing the unique identifier of this source.
        # 
        # XMLName
        # A string value that contains the three-letter identifier
        # of the XML file (e.g. F00). This value is taken from the <idno>
        # element with type "bnc" from the publication statement in the XML
        # file description component.
        # 
        # OldName
        # A string value that contains the label used in early BNC releases
        # to identify the source. This value is taken from the <idno>
        # element with type "old" from the publication statement in the XML
        # file description component.
        #
        # Type
        # An enum value that contains the text type, taken from the type 
        # attribute of the <wtext> and <stext> elements in the XML file.
        #
        # Class
        # A text value that contains the genre classification code, taken
        # from the <classCode scheme="DLEE"> element in the <textClass>
        # section of the XML profile description component.
        #
        # Date
        # A text value that contains the year in which the text was created,
        # taken from the date attribute of the <creation> element in the XML
        # profile description component, or from a <date> element within
        # this <creation> element.
        #
        # File_id
        # An int value containing the unique identifier of the file that 
        # this source is read from.
        
        self.source_table = "Texts"
        self.source_id = "Source_id"
        self.source_xmlname = "XMLName"
        self.source_oldname = "OldName"
        self.source_genre = "Type"
        self.source_class = "Class"
        self.source_year = "Date"
        self.source_file_id = "File_id"
        
        self.create_table_description(self.source_table,
            [Identifier(self.source_id, "SMALLINT(4) UNSIGNED NOT NULL"),
             Column(self.source_xmlname, "CHAR(3) NOT NULL"),
             Column(self.source_oldname, "CHAR(6) NOT NULL"),
             Column(self.source_genre, "ENUM('ACPROSE','CONVRSN','FICTION','NEWS','NONAC','OTHERPUB','OTHERSP','UNPUB') NOT NULL"),
             Column(self.source_class, "ENUM('S brdcast discussn','S brdcast documentary','S brdcast news','S classroom','S consult','S conv','S courtroom','S demonstratn','S interview','S interview oral history','S lect commerce','S lect humanities arts','S lect nat science','S lect polit law edu','S lect soc science','S meeting','S parliament','S pub debate','S sermon','S speech scripted','S speech unscripted','S sportslive','S tutorial','S unclassified','W ac:humanities arts','W ac:medicine','W ac:nat science','W ac:polit law edu','W ac:soc science','W ac:tech engin','W admin','W advert','W biography','W commerce','W email','W essay school','W essay univ','W fict drama','W fict poetry','W fict prose','W hansard','W institut doc','W instructional','W letters personal','W letters prof','W misc','W news script','W newsp brdsht nat: arts','W newsp brdsht nat: commerce','W newsp brdsht nat: editorial','W newsp brdsht nat: misc','W newsp brdsht nat: report','W newsp brdsht nat: science','W newsp brdsht nat: social','W newsp brdsht nat: sports','W newsp other: arts','W newsp other: commerce','W newsp other: report','W newsp other: science','W newsp other: social','W newsp other: sports','W newsp tabloid','W nonAc: humanities arts','W nonAc: medicine','W nonAc: nat science','W nonAc: polit law edu','W nonAc: soc science','W nonAc: tech engin','W pop lore','W religion') NOT NULL"),
             Column(self.source_year, "ENUM('0000','1947','1960','1961','1962','1963','1964','1965','1966','1967','1968','1969','1970','1971','1972','1973','1974','1975','1976','1977','1978','1979','1980','1981','1982','1983','1984','1985','1986','1987','1988','1989','1990','1991','1992','1993','1994') NOT NULL"),
             Link(self.source_file_id, self.file_table)])

        # Add the main corpus table. Each row in this table represents a 
        # token in the corpus. It has the following columns:
        # 
        # id
        # An int value containing the unique identifier of the token
        #
        # Entity_id
        # An int value containing the unique identifier of the lexicon
        # entry associated with this token.
        #
        # Source_id
        # An int value containing the unique identifier of the source that
        # contains this token.
        #
        # Speaker_id
        # An int value containing the unique identifier of the speaker who
        # produced this token. It is zero for written texts.
        #
        # Sentence_id
        # An int value containing the unique identifier of the sentence 
        # that contains this token.

        # These columns serve as linking columns that link the several other
        # tables to each token in the corpus.
        
        self.corpus_table = "Corpus"
        self.corpus_id = "Token_id"
        self.corpus_word_id = "Word_id"
        self.corpus_source_id = "Source_id"
        self.corpus_speaker_id = "Speaker_id"
        self.corpus_sentence_id = "Sentence_id"

        self.create_table_description(self.corpus_table, 
            [Identifier(self.corpus_id, "INT(9) UNSIGNED NOT NULL"),
             Link(self.corpus_sentence_id, self.sentence_table),
             Link(self.corpus_speaker_id, self.speaker_table),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_source_id, self.source_table)])

        # Add time features. A time feature is a column from a table that 
        # stores numerical data which is suitable for a time series plot.
        self.add_time_feature(self.source_year)
        self.add_time_feature(self.speaker_age)

        # This dictionary stores the speaker Id (used as the Identifier key in
        # the MySQL table) that is associated with a BNC speaker label (used
        # in the XML files).
        self._speaker_dict = {}

    def xml_preprocess_tag(self, element):
        self._tagged = False
        tag = element.tag
        # <u> is an utterance. This element has a who attribute that 
        # specifies the speaker of the utterance.
        if tag in set(("w", "c")):
            if element.text:
                word_text = element.text.strip()
            else:
                word_text = ""
            
            if tag == "w":
                lemma_text = element.attrib.get("hw", word_text).strip()
                lemma_pos = element.attrib.get("pos", "UNC").strip()
                word_pos = element.attrib.get("c5", "UNC").strip()
            else:
                lemma_text = word_text
                lemma_pos = "PUNCT"
                word_pos = "PUNCT"
                
            # get word_id that matches current token (a new one is created
            # if necessary:
            self._word_id = self.table(self.word_table).get_or_insert(
                {self.word_label: word_text, 
                 self.word_lemma: lemma_text, 
                 self.word_lemma_pos: lemma_pos,
                 self.word_pos: word_pos, 
                 self.word_type: tag}, case=True)
            
            # store the new token with all needed information:
            self.add_token_to_corpus(
                {self.corpus_word_id: self._word_id,
                 self.corpus_speaker_id: self._speaker_id,
                 self.corpus_sentence_id: self._sentence_id,
                 self.corpus_source_id: self._source_id})
        elif tag == "u":
            who = element.attrib["who"].strip()
            lookup = self._speaker_dict.get(who, None)
            if lookup:
                self._speaker_id = lookup
            else:
                self._speaker_id = self.table(self.speaker_table).find(
                    {self.speaker_label: who})
                if not self._speaker_id:
                    self._speaker_id = self.table(
                        self.speaker_table).get_or_insert(
                            {self.speaker_label: who,
                                self.speaker_age: "",
                                self.speaker_sex: "u"})
                    self._speaker_dict[who] = self._speaker_id
        # <s> is a sentence:
        elif tag == "s":
            self._sentence_id = self.table(self.sentence_table).get_or_insert({})
        
        #other supported elements:
        else:
            # Unknown tags:
            if element.text or list(element):
                self.tag_next_token(element.tag, element.attrib)
                self._tagged = True
            else:
                self.add_empty_tag(element.tag, element.attrib)
                
    def xml_postprocess_tag(self, element):
        if self._tagged:
            self.tag_last_token(element.tag, element.attrib)
    
    def get_speaker_data(self, person):
        """
        Obtain the speaker information from a 'person' element.
        
        'person' elements are stored in the particDesc part of the 
        'profile_desc' component of the BNC XML header. Each 'person' 
        specifies a different speaker. Supported attributes are 'sex' and 
        'age'. Persons also have an ID.
        
        Parameters
        ----------
        person : element
            An element with the tag 'person'.
            
        Returns
        -------
        l : list
            A list containing (in order) the ID, the age, and the sex of the 
            person. If the age or the sex are not given, the respective 
            strings are empty.
        """
        sex = person.attrib.get("sex", "")
        if person.find("age") != None:
            age = person.find("age").text.strip()
        else:
            age = person.attrib.get("age", "")
        # During parsing of the XML tree, the attribute "xml:id" is
        # interpreted as a qualified name (which it probably isn't).
        # Thus, the 'xml' part is replaced by the namespace, which for
        # XML files like those in the BNC is apparently
        # http://www.w3.org/XML/1998/namespace
        # Thus, in order to get the speaker identifier, we have to look
        # for {http://www.w3.org/XML/1998/namespace}id instead.
        xml_id = person.attrib.get("{http://www.w3.org/XML/1998/namespace}id", "")
        return [xml_id, age, sex]

    def xml_get_meta_info(self, root):
        """ Parse XML root so that any meta information that should be 
        retrieved from the XML tree is stored adequately in the corpus
        tables.
        
        FIXME:
        This method should evaluate the content of 
        
        <teiHeader>
            <fileDesc>
                <extent>6688 tokens; 6708 w-units; 423 s-units</extent>
            </fileDesc>
        </teiHeader> 
        
        to validate that the whole file is correctly processed.
        
        Alternatively, it should use the detailed usage information from 
        <teiHeader><
            encodingDesc>
                <tagsDecl>
                    <namespace name="">
                        <tagUsage gi="c" occurs="810" />
                        ...
        """

        def get_year(S):
            match = re.match("(\d\d\d\d)", S)
            if match:
                return match.group(1)
            else:
                return S
        header = root.find("teiHeader")
        file_desc = header.find("fileDesc")
        encoding_desc = header.find("encodingDesc")
        profile_desc = header.find("profileDesc")
        revision_desc = header.find("revisionDesc")
        # Get the date:
        creation = profile_desc.find("creation")
        date_element = creation.find("date")
        if date_element != None:
            source_date = get_year(date_element.text.strip())
        else:
            source_date = get_year(creation.attrib.get("date", "0000"))
                
        # Get XMLName and OldName:
        for idno in file_desc.find("publicationStmt").findall("idno"):
            if idno.attrib["type"] == "bnc":
                source_xmlname = idno.text.strip()
            else:
                source_oldname = idno.text.strip()
        
        body = self.xml_get_body(root)
        
        # Get the text classification string:
        source_type = body.attrib.get("type")
        for class_code in profile_desc.find("textClass").findall("classCode"):
            if class_code.attrib.get("scheme") == "DLEE":
                source_class = class_code.text.strip()

        # Find all speakers, and if there are some, make sure that they are
        # stored in the speaker table:
        participant_desc = profile_desc.find("particDesc")
        if participant_desc != None:
            for person in participant_desc.findall("person"):
                speaker_label, speaker_age, speaker_sex = self.get_speaker_data(person)
                self._speaker_dict[speaker_label] = self.table(self.speaker_table).get_or_insert(
                    {self.speaker_label: speaker_label,
                        self.speaker_age: speaker_age,
                        self.speaker_sex: speaker_sex})
        # Initially, there is no speaker. It is set for each <u> element. In
        # written texts, no <u> elements occur, so the variable remains 
        # empty.
        self._speaker_id = 0
        
        # Get a valid source id for this text. If it isn't in the source 
        # table yet, store it as a new entry:
        self._source_id = self.table(self.source_table).get_or_insert(
            {self.source_xmlname: source_xmlname, 
             self.source_oldname: source_oldname, 
             self.source_genre: source_type, 
             self.source_class: source_class, 
             self.source_year: source_date, 
             self.source_file_id: self._file_id})
        
    def xml_get_body(self, root):
        """ Obtain either the <wtext> element for written or the <stext> 
        element for spoken texts from the root."""
        
        body = root.find("wtext")
        if body == None:
            body = root.find("stext")
        if body == None:
            logger.warning("Neither <wtext> nor <stext> found in file, not processed.")
        return body

    def process_file(self, current_file):
        """ Process an XML file, and insert all relevant information into
        the corpus."""
        if self.interrupted:
            return
        e = self.xml_parse_file(current_file)
        self.xml_get_meta_info(e)
        self.xml_process_element(self.xml_get_body(e))

    @staticmethod
    def get_name():
        return "BNC"

    @staticmethod
    def get_db_name():
        return "bnc"

    @staticmethod
    def get_language():
        return "English"
    
    @staticmethod
    def get_language_code():
        return "en-GB"

    @staticmethod
    def get_title():
        return "British National Corpus – XML edition"

    @staticmethod
    def get_description():
        return ["The British National Corpus (BNC) is a 100 million word collection of samples of written and spoken language from a wide range of sources, designed to represent a wide cross-section of British English from the later part of the 20th century, both spoken and written.",
        "The written part of the BNC (90%) includes, for example, extracts from regional and national newspapers, specialist periodicals and journals for all ages and interests, academic books and popular fiction, published and unpublished letters and memoranda, school and university essays, among many other kinds of text.",
        "The spoken part (10%) consists of orthographic transcriptions of unscripted informal conversations (recorded by volunteers selected from different age, region and social classes in a demographically balanced way) and spoken language collected in different contexts, ranging from formal business or government meetings to radio shows and phone-ins."]
    
    @staticmethod
    def get_license():
        return "The BNC is available under the terms of the <a href='http://www.natcorp.ox.ac.uk/docs/licence.html'>BNC User Licence</a>."
        
    @staticmethod
    def get_references():
        return ["<i>The British National Corpus</i>, version 3 (BNC XML Edition). 2007. Distributed by Oxford University Computing Services on behalf of the BNC Consortium."]

    @staticmethod
    def get_url():
        return "http://www.natcorp.ox.ac.uk/"

if __name__ == "__main__":
    BuilderClass().build()
