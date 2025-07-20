# # edgar_spider.py

# import scrapy
# from urllib.parse import urlencode

# class EdgarSpider(scrapy.Spider):
#     name = "edgar"
#     allowed_domains = ["efts.sec.gov", "sec.gov"]
#     download_delay = 0.2  # be polite

#     # 1) your rotating lists
#     KEYWORDS = [
#         "licensing agreement",
#         "positive clinical",
#         "regain compliance",
#     ]
#     TICKERS = ["VSTE", "KNW", "MRM", "NWTG", "XPON", "OP", "KIRK"]

#     # 2) API endpoint + headers
#     API_BASE = "https://efts.sec.gov/LATEST/search-index"
#     HEADERS = {
#         'accept': 'application/json, text/javascript, */*; q=0.01',
#         'origin': 'https://www.sec.gov',
#         'referer': 'https://www.sec.gov/',
#         'user-agent': 'Mozilla/5.0',
#     }

#     def start_requests(self):
#         for q in self.KEYWORDS:
#             for ticker in self.TICKERS:
#                 params = {
#                     "q": q,
#                     "category": "custom",
#                     "entityName": ticker,
#                     "forms": "6-K,8-K",
#                     "startdt": "2020-07-14",
#                     "enddt": "2025-07-14",
#                 }
#                 url = f"{self.API_BASE}?{urlencode(params)}"
#                 yield scrapy.Request(
#                     url,
#                     headers=self.HEADERS,
#                     callback=self.parse,
#                     cb_kwargs={'ticker': ticker}
#                 )

#     def parse(self, response, ticker):
#         data = response.json()
#         for hit in data.get("hits", {}).get("hits", []):
#             src = hit.get("_source", {})
#             raw_cik = src.get("ciks", [""])[0]
#             adsh_filename = hit.get("_id", "")  # e.g. "0001964630-24-000015:vste-…pdf"

#             # Build the PDF URL:
#             #  - split _id into ADSH and filename
#             #  - strip leading zeros from raw_cik for the folder
#             try:
#                 adsh_part, filename = adsh_filename.split(":", 1)
#                 cik_folder = str(int(raw_cik))
#                 pdf_url = (
#                     "https://www.sec.gov/Archives/edgar/data/"
#                     f"{cik_folder}/{adsh_part}/{filename}"
#                 )
#             except ValueError:
#                 pdf_url = None

#             yield {
#                 "filing_date":   src.get("file_date"),
#                 "form_type":     src.get("form"),
#                 "ticker":        ticker,
#                 "company_name":  src.get("display_names", [""])[0],
#                 "url":           pdf_url,
#             }


import scrapy
import re
from urllib.parse import urlencode
from datetime import datetime


class EdgarSpider(scrapy.Spider):
    name = "edgar"
    allowed_domains = ["efts.sec.gov", "sec.gov"]
    

    download_delay = 0.2  # be polite

    # 1) your rotating lists for keyword-based search
    KEYWORDS = [
        "licensing agreement", "License agreement", "exclusive agreement", "exclusive", "exclusively",
        "Purchase Agreement", "year Purchase Agreement", "year Purchase", "year supply", "year Agreement",
        "positive clinical", "licensing deal", "License deal", "Preclinical Success", "announces successful",
        "announces positive", "announces strong", "that the U.S. Food and Drug Administration", "has regained compliance",
        "has granted the Company", "the Company has been granted an", "granted the Company an", "Press Release, dated",
        "allowance", "AI-Powered", "Positive Results", "Private Placement", "has acquired"
    ]

    TICKERS = [
        "VSTE", "KNW", "MRM", "NWTG", "XPON", "OP", "KIRK", "CURR", "EDUC", "ZEO", "ITRM", "CURI", "ELAB", "MSPR", "AGRI", "PBM", "XTIA", "APLM", 
        "XXII", "AKTS", "CDT", "EYEN", "CETX", "DBGI", "CNSP", "CTXR", "PSNYW", "TANH", "TOI", "APDN", "EDBL", "VIRX", "BHAT", "ICCT",
        "IDAI", "ACON", "WBUY", "LYRA", "APTO", "TNXP", "COEP", "MLGO", "MBIO", "CLEU", "MYNZ", "PET", "LITM", "NITO", "PIII", "IVP", "CERO", "OST",
        "BNGO", "CMCT", "LGCB", "SMX", "MTC", "GMM", "HAO", "SPRC", "TIVC", "JL", "VINC", "RIME", "AEHL", "GCTK", "FCUV", "CDIO", "PTPI", "NXU", "AIEV",
        "BLRX", "FAMI", "MNDR", "BGLC", "SYRS", "UBXG", "CARA", "SLXN", "APVO", "TWG", "GWAV", "BMRA", "CUTR", "GLYC", "INAB", "HTOO", "PEV", "VERO",
        "MRNS", "TGL", "CNEY", "WAI", "ENVB", "LDTC", "MTEM", "XFOR", "ADTX", "TAOP", "CGBS", "TFFP", "LTRY", "WTO", "NKGN", "BLUE", "KLTO", "BSLK",
        "CYCC", "SYRA", "IPA", "SXTC", "RNAZ", "OMEX", "FGEN", "ONVO", "FTFT", "FTCI", "AEMD", "BOXL", "VEEE", "CYTO", "CGTX", "ENSC", "TRUG", "FLYE",
        "GOEV", "LAES", "HSDT", "ENTO", "WATT", "RVSN", "AIMD", "DBVT", "APCX", "HOVR", "OPTN", "TSBX", "SPRB", "CLRO", "GGR", "FEAM", "WINT", "PASG",
        "NIVF", "BTAI", "TTOO", "RENB", "ERNA", "SCLX", "SNSE", "SGBX", "ARBB", "ANTE", "FAAS", "UNCY", "MKTW", "ZKIN", "INVZ", "SLGL", "ULY", "XAIR",
        "HUBC", "NCI", "AMRN", "ABVC", "ALVR", "ATXG", "BLMZ", "MNTS", "PSIG", "VRPX", "SQFT", "BOLT", "BREA", "PRZO", "QNRX", "NEGG", "IMG", "VXRT",
        "ELEV", "SLE", "YI", "NVFY", "VRME", "RR", "GURE", "INTZ", "TCBP", "JDZG", "ABTS", "CHNR", "ASST", "WKSP", "ATHA", "ABVE", "PTIX", "FRSX", "CRKN",
        "ADAP", "HEPA", "VERU", "YHGJ", "SRM", "VRAR", "SBET", "HWH", "INKT", "CREG", "NMTC", "ROMA", "EM", "GRYP", "GRI", "EKSO", "TLPH", "GOSS",
        "IPW", "IVVD", "CETY", "NAOV", "IOBT", "PC", "AMLI", "EQ", "ICCM", "MHUA", "CMAX", "POAI", "GVH", "OCEA", "TOMZ", "HYFM", "CMLS", "BCTX", "CYTH",
        "MOBX", "BNRG", "APM", "AYRO", "EJH", "COSM", "AWH", "QMMM", "NDLS", "REVB", "MFI", "SMSI", "ASPS", "MCRB", "PRPH", "ANGH", "HCWB", "PXLW",
        "OMGA", "KAVL", "VOR", "IPDN", "CNTM", "FGI", "TCTM", "IMNN", "BPTH", "OESX", "DGLY", "CHEK", "CARM", "AVGR", "NVNI", "SY", "SHOT", "GP",
        "WNW", "WIMI", "OM", "HOTH", "LPSN", "DRIO", "KPTI", "KWE", "CISS", "PRSO", "EPOW", "BNAI", "CTOR", "TC", "SILO", "PCSA", "NAYA", "INTJ",
        "BFRI", "GAME", "MESA", "SHPH", "OPTX", "ALLK", "LVO", "BKYI", "AHG", "PRPL", "ONMD", "STIM", "ONDS", "ABAT", "CTMX", "XLO", "BRNS", "SXTP",
        "NRSN", "ABLV", "ACET", "CMRX", "PGEN", "KRON", "TPST", "OCGN", "ESLA", "TMC", "VVPR", "SJ", "CTSO", "PROC", "SNAL", "HOFV", "ENLV", "DTCK",
        "TYGO", "MKDW", "AQB", "IMAB", "NXPL", "ASRT", "PRLD", "COOT", "RETO", "SOPA", "LYEL", "TLSA", "ONCY", "SNAX", "LIDR", "REKR", "PAVS", "EDTK",
        "UONEK", "ECDA", "SYTA", "MBOT", "EZGO", "BANL", "VRCA", "MOND", "PT", "LUCD", "INDP", "PAVM", "NCRA", "CNTB", "SKYX", "STTK", "ADIL", "SOHO",
        "DRRX", "IRD", "CODX", "AGAE", "SCWO", "KOPN", "THCH", "EEIQ", "ILAG", "AACG", "RLYB", "CUE", "HYPR", "LGCL", "TOUR", "MVIS", "PMN", "JAGX",
        "JYD", "WW", "JZ", "FEMY", "OKYO", "AERT", "OVID", "NKTR", "ZCMD", "KITT", "CPIX", "ACHL", "ZJYL", "LNZA", "GRNQ", "ATHE", "DLPN", "FTEK",
        "DHAI", "HRTX", "BACK", "KDLY", "RAPT", "CLSD", "YGMZ", "ONCO", "CHRS", "GNPX", "WKHS", "SMXT", "IMUX", "ARTL", "VSME", "MSGM", "IBG", "SAIH",
        "CLPS", "SFWL", "BLIN", "SWAG", "PRTS", "SVRE", "ZVSA", "DRMA", "JCSE", "ONCT", "CPOP", "UBX", "RVPH", "MNY", "RPID", "ZTEK", "PETZ", "SPRO",
        "SKYQ", "FOSL", "SLS", "PSTV", "CMBM", "CLIR", "GXAI", "CISO", "MDAI", "NXTC", "JXJT", "RAYA", "SPPL", "SCYX", "THTX", "AREC", "MAPS", "IMTE",
        "NUWE", "ASNS", "RVYL", "STBX", "IPSC", "XRTX", "TRIB", "BIAF", "PLBY", "ATOS", "GPRO", "UK", "NCNA", "KNDI", "AMPG", "LVLU", "ORGN", "CENN",
        "BBLG", "ONFO", "EFOI", "BCLI", "HLP", "HTCO", "UCL", "NRXP", "ALLR", "SIDU", "OCG", "POWW", "BDSX", "DRCT", "RNXT", "GFAI", "AKTX", "GIFT",
        "CTHR", "ALZN", "BROG", "DMN", "MIRA", "CMND", "LEDS", "TNFA", "JZXN", "ANTX", "VANI", "MYSZ", "QH", "ACXP", "INCR", "MOB", "AKAN", "ALCE",
        "ENG", "HKIT", "IINN", "SLRX", "MYNA", "TXMD", "GBIO", "SYPR", "NB", "CNTX", "EVTV", "ZENV", "SATL", "SELX", "CXAI", "LOOP", "ALXO", "CGEN",
        "HTCR", "NWGL", "REBN", "ALTO", "SKIN", "CYCN", "CLWT", "SYBX", "FLGC", "GLXG", "OP", "RDI", "APYX", "DWSN", "ATPC", "GIGM", "ANEB", "FRGT", 
        "SCKT", "CPSH", "WRAP", "YTRA", "RGLS", "BRTX", "FMST", "VSEE", "UONE", "VIOT", "EVAX", "RAY", "HOUR", "LPTH", "CMPX", "XWEL", "GLBS", "AWRE", 
        "AILE", "TVGN", "NEPH", "CLIK", "GV", "BLNK", "UGRO", "ICAD", "BNZI", "INBS", "MGIH", "TDUP", "BTBD", "BON", "BCAB", "GDHG", "CLRB", "ENTX", 
        "SPGC", "WAFU", "LVTX", "SGLY", "DOMH", "FBIO", "PMVP", "EVGN", "HGBL", "CRDL", "QSI", "LYT", "LIXT", "AYTU", "IPHA", "AXDX", "MSAI", "VS", 
        "SUGP", "CMMB", "MCHX", "CNET", "BIOR", "LIQT", "FPAY", "VIVK", "MODD", "TRVG", "SOGP", "HYZN", "PMCB", "YJ", "TROO", "MTEK", "BGFV", "IKNA", 
        "BWEN", "GANX", "BRLT", "AGMH", "LKCO", "BYSI", "NUKK", "SURG", "ESGL", "NTRP", "WETH", "BOF", "CCTG", "ZENA", "IMMX", "PSHG", "IRIX", "DVLT", 
        "QVCGA", "FFAI", "RDGT", "MMVVF", "RGFC", "IPM", "XAGE", "SVUHF", "SPIEF", "RNTX", "QTIH", "BLNE", "YHC", "NEUP", "FREHY", "NXXT", "PIKM", "FMTO", 
        "ZBAI", "GITS","PHLT", "OTRK", "GEG", "GELS", "IFBD", "SKK", "GAN", "MIST", "AZI", "BAOS", "VTYX", "NIU", "CTNT", "GIPR", "PODC", "USEG", "LUNA", 
        "HLVX", "GRWG", "CABA", "XNET", "CLLS", "IMRN", "WLDS", "ZAPP", "XTLB", "MDXH", "MYPS","LGVN", "MGX", "YQ", "HOWL", "FNGR", "PYXS", "ARBE", "LFWD", 
        "LIFW", "IMMP", "UPC", "APWC", "DYAI", "ARAY", "CSLR", "OLB", "HIHO", "FEBO", "HUDI", "CJET", "MNDO", "QNCX", "BFRG", "MGRM", "AXTI", "VCIG", 
        "YYGH","WCT", "IXHL", "SPWH", "RMNI", "ATXI", "VRAX", "TPIC", "NKLA", "CRBU", "LGO", "DATS", "MRSN", "LGMK", "ICU", "USEA", "LOBO", "RANI", "IFRX",
        "WKEY", "LEXX", "PDSB", "WORX", "FARM", "IMRX", "SHIM", "SSP", "MRIN", "AKYA", "KXIN", "MNOV", "HOLO", "LXEH", "IVDA", "HOOK", "AQMS", "LICN",
        "FORA", "EDSA", "SNTI", "COCH", "PPBT", "ALTS", "ADAG", "COCP", "LRE", "FGL", "GTEC", "SGRP", "RCON", "TDTH", "AREB", "NERV", "ATNF", "RMTI",
        "GDTC", "BCDA", "STKH", "HBIO", "SNES", "BDMD", "DSY", "FATE", "IZM", "NMHI", "IKT", "DXLG", "DRTS", "OSS", "PMD", "ORMP", "MGOL", "TRSG",
        "BOLD", "SBFM", "NRBO", "CRGO", "ABOS", "BZUN", "TNYA", "TCRT", "TARA", "OCC", "NXTT", "QIPT", "AMST", "CVGI", "SND", "SEER", "PALI", "HYMC",
        "AISP", "EDIT", "SEED", "CHR", "CRDF", "NKTX", "PHIO", "ADGM", "EDAP", "STAF", "SHMD", "ALBT", "ASTI", "DPRO", "GDC", "STRO", "PFIE", "VSTA",
        "TNON", "BDTX", "DWTX", "GNLX", "LPTX", "THAR", "MASS", "ABSI", "TAIT", "ATER", "INTS", "VTGN", "SNPX", "DAIO", "FBLG", "IMCC", "IVA", "AFMD",
        "LSB", "DSWL", "LIPO", "ANL", "ELWS", "GTIM", "MGRX", "DTSS", "RMCF", "NSPR", "HITI", "BLBX", "AVTE", "HSCS", "NTWK", "IVAC", "VMAR", "SGMA",
        "NIXX", "TORO", "BAER", "MRM", "OCX", "IDN", "MBRX", "VERI", "ZURA", "PSTX", "RKDA", "SAG", "GLMD", "CELU", "ZOOZ", "SISI", "ICON", "MEIP",
        "VOXR", "GALT", "BEAT", "CREV", "RLMD", "QSG", "TOYO", "FLNT", "RPTX", "INZY", "CCLD", "GSUN", "IZEA", "SUUN", "SNOA", "BRFH", "SHLT", "LTRX",
        "JFBR", "APRE", "LSTA", "UTSI", "RAVE", "TRVI", "MULN", "CSCI", "STRR", "GOVX", "EMKR", "PRFX", "SONN", "SNT", "AIFF", "PBYI", "TELA", "BMR",
        "VYNE", "ATYR", "SSKN", "CLYM", "GTBP", "TPCS", "LTRN", "RMSG", "CVV", "ORKT", "KTTA", "KRKR", "MRKR", "PMAX", "ABP", "ME", "TRNR", "SUNE",
        "CPTN", "SABS", "STRM", "NAAS", "XYLO", "GSIT", "VIGL", "BCOV", "SMTK", "VVOS", "CDTG", "ANIX", "SOPH", "ZNTL", "MGNX", "RSSS", "FULC", "TLS",
        "GRCE", "CMTL", "BLDE", "SNGX", "WVVI", "BRAG", "WHLRP", "NXGL", "UPLD", "TKLF", "DARE", "AGEN", "BOSC", "MURA", "SCPH", "SONM", "SDOT", "JRSH",
        "KPRX", "IMPP", "SIFY", "CDZI", "AVIR", "JWEL", "OBLG", "NVNO", "NLSP", "SLNH", "STKS", "MOVE", "CREX", "CALC", "PAYS", "STSS", "PSNL", "JVA",
        "EPRX", "TUSK", "BJDX", "YYAI", "KRMD", "III", "SCNI", "DTI", "HFFG", "PYPD", "RECT", "CTRM", "NVVE", "NOTV", "YIBO", "TSVT", "YOSH", "VCNX",
        "PRQR", "SPCB", "ICCC", "ILPT", "ACCD", "TTNP", "SOND", "WVVIP", "EHGO", "DLTH", "CKPT", "HURA", "BZFD", "GNSS", "NBTX", "ACRS", "MIND", "DIBS",
        "FORD", "WHLM", "OSUR", "BHIL", "CNVS", "SOWG", "CDLX", "GLE", "DTST", "INVE", "NNBR", "MMLP", "HTLM", "VSTM", "HUHU", "SGHT", "ELDN", "POET",
        "CRIS", "AMTX", "KGEI", "MARPS", "RFIL", "INO", "PXS", "XGN", "XBIO", "SKYE", "ELUT", "LDWY", "CLGN", "CBUS", "CSTE", "TACT", "BEEM", "CLNN",
        "VGAS", "GNFT", "NAII", "TLF", "WLGS", "ELSE", "ALLT", "TELO", "NURO", "FKWL", "TCRX", "ICG", "ACHV", "ICLK", "LUMO", "SOBR", "EVOK", "ACB",
        "JCTC", "CAAS", "CNTY", "KYTX", "VISL", "TZUP", "PEPG", "WPRT", "ISPC", "LINK", "TRAW", "CLAR", "CRWS", "TLSI", "EUDA", "XOS", "CSBR", "BDRX",
        "SPAI", "DUOT", "FATBB", "PDYN", "PRTG", "SOTK", "INM", "PTHL", "GNTA", "DMAC", "CING", "STFS", "SPHL", "SGMT", "GRRR", "PETS", "NTRB", "QLGN",
        "PTLE", "ALDX", "FLL", "OPRX", "INMB", "PHUN", "PLUR", "RZLT", "VLCN", "TENX", "ELTX", "SINT", "INHD", "AENT", "TTEC", "SLNG", "OTLK", "SDIG",
        "CADL", "OB", "NDRA", "VNDA", "CASI", "NVCT", "POCI", "FOXX", "FBIOP", "LPCN", "SELF", "RRGB", "VRA", "CXDO", "GILT", "KVHI", "MOLN", "ADD",
        "FAT", "FENC", "LOAN", "EGAN", "DERM", "SLDB", "QNTM", "RSLS", "BNR", "KTCC", "GLTO", "NHTC", "UPXI", "BRLS", "MNTX", "ASYS", "KZIA", "DALN",
        "LCUT", "OBIO", "WOK", "QURE", "SNYR", "ATOM", "HPAI", "LFMD", "RGC", "KMDA", "PANL", "HHS", "PRPO", "JTAI", "BTOC", "AIXI", "MTEN", "ABEO",
        "CEAD", "HDSN", "ZCAR", "ADVM", "EPSN", "GASS", "CYN", "UHG", "PULM", "ORIS", "UCAR", "SWVL", "PPSI", "SANG", "BLZE", "AMIX", "LTBR", "KLXE",
        "RMBL", "MRAM", "RDIB", "BMEA", "GAIA", "LXEO", "COYA", "SERA", "ACRV", "LUCY", "AUID", "SANW", "KPLT", "TTSH"
    ]  

    FORMS_K = ["6-K", "8-K"]

    # 2) your rotating tickers for form-based search (no keywords)
    FORMS_Q = ["10-Q", "13F-E", "13F-HR", "13F-NT", "13FCONP", "424B4"]

    # API endpoint + headers
    API_BASE = "https://efts.sec.gov/LATEST/search-index"
    HEADERS = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'origin': 'https://www.sec.gov',
        'referer': 'https://www.sec.gov/',
        'user-agent': 'Mozilla/5.0',
    }
    
    
    
    def start_requests(self):
        # First: keyword + ticker loop for forms 6-K, 8-K
        for q in self.KEYWORDS:
            for ticker in self.TICKERS:
                params = {
                    "q": q,
                    "category": "custom",
                    "entityName": ticker,
                    "forms": ",".join(self.FORMS_K),
                    "startdt": "2024-07-14",
                    "enddt": "2025-07-14",
                }
                url = f"{self.API_BASE}?{urlencode(params)}"
                yield scrapy.Request(
                    url,
                    headers=self.HEADERS,
                    callback=self.parse,
                    cb_kwargs={'ticker': ticker}
                )

        # Second: ticker-only loop for forms 10-Q, 13F-types, 424B4
        for ticker in self.TICKERS:
            params = {
                'dateRange': 'all',
                'category': 'custom',
                'entityName': ticker,
                'forms': ",".join(self.FORMS_Q),
                'startdt': '2004-01-01',
                'enddt': '2025-07-16',
            }
            url = f"{self.API_BASE}?{urlencode(params)}"
            yield scrapy.Request(
                url,
                headers=self.HEADERS,
                callback=self.parse,
                cb_kwargs={'ticker': ticker}
            )
    
    cookies = {
        'nmstat': '8ccd26cd-4ef3-d0db-7716-01dfcacad0d6',
        '_gid': 'GA1.2.2142639437.1752780207',
        '_ga': 'GA1.1.120253980.1752174201',
        '_4c_': '%7B%22_4c_s_%22%3A%22fZFBj5swEIX%2FysoHTiHYGIITCe0h523VqmqPkbEHsJbYyJi4aZT%2FXpugtmrUcmH0%2Bb3x88wN%2BR40OpCqzFlOq5IRRjfoHa4TOtyQVTL%2BLuiAGlruKGdlSvckT4u8oGnDCx6qtsEtB%2BBcoA36HnvtcF4RTApM8%2FsGiXHtcUPCSAi9yH5L2Ban7RQc7kcgFONQjtbIWbiTu45R5qF5meR7OJBwUQJOXknXR3%2FO8G%2Fag%2Bp6FzBbmsjRRkmovNLS%2BL9dK%2F3l2lU00MYaP0F0HntrzvBCKAvYhDGgb4sjZrXQgrWLrHdunA5Z5r3fTiC2nblkIDtuswm4FX0W5JNy8R3r8QrCbB8sfbCvKlJ5%2BnL8HPiHP8in48e3FY1xBTHnYAQfYtOwtQ2a7fCPKKJTaaN09nhXuiR75cIpo%2BsOnDDnketr0qoB9HyuMSYpZQWtkjj7OpHcQVMnxmuwtdJimCUkk%2BPW1QVOhJl1LNB9XXiZ7zEhhBa4Cgt1IRTbFTh%2B90f2Zf%2F0SZ0%2Fq9fAcT6g%2F2N9uuh%2B%2Fwk%3D%22%7D',
        'ak_bmsc': '9B6A3EEE9E922DF08F762BDC82B6A5DA~...snip...',
        'bm_sv': '4359DDC3456AB4B966E785024100055B~...snip...',
        '_ga_CSLL4ZEK4L': 'GS2.1.s1752857085$o10$g1$t1752857494$j51$l0$h0',
        '_ga_300V1CHKH1': 'GS2.1.s1752857086$o12$g1$t1752857524$j21$l0$h0',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,pl;q=0.8',
        'cache-control': 'max-age=0',
        # 'if-modified-since': 'Mon, 28 Oct 2024 10:31:25 GMT',
        'priority': 'u=0, i',
        'referer': 'https://www.sec.gov/edgar/search/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }

    def parse(self, response, ticker="UNKNOWN"):
        data = response.json()

        for hit in data.get("hits", {}).get("hits", []):
            src = hit.get("_source", {})
            raw_cik = src.get("ciks", [""])[0]
            adsh = src.get("adsh", "")
            if not adsh:
                continue

            cleaned_cik = str(int(raw_cik))  # remove leading zeros
            flattened_adsh = adsh.replace("-", "")
            index_url = (
                f"https://www.sec.gov/Archives/edgar/data/{cleaned_cik}/"
                f"{flattened_adsh}/{adsh}-index.html"
            )

            meta = {
                "form": src.get("form"),
                "ticker": ticker,
                "adsh": adsh,
                "cik": cleaned_cik,
                "display_name": src.get("display_names", [""])[0],
                "pdf_url": self.build_pdf_url(src.get("ciks", [""])[0], hit.get("_id", "")),
            }

            yield scrapy.Request(
                url=index_url,
                callback=self.parse_index_page,
                meta=meta,
                headers=self.headers,
                cookies=self.cookies,
                dont_filter=True,
            )

    def build_pdf_url(self, raw_cik, raw_id):
        if ':' in raw_id:
            first_part, second_part = raw_id.split(':', 1)
        elif '/' in raw_id:
            first_part, second_part = raw_id.split('/', 1)
        else:
            first_part, second_part = raw_id, ""
        cleaned_adsh = first_part.replace('-', '')
        try:
            adsh_part, filename = f"{cleaned_adsh}/{second_part}".split('/', 1)
            cik_folder = str(int(raw_cik))  # remove leading zeros
            return f"https://www.sec.gov/Archives/edgar/data/{cik_folder}/{adsh_part}/{filename}"
        except ValueError:
            return None

    def parse_index_page(self, response):
        filed_date_raw = response.css(".info:nth-child(4)::text").get()
        formatted = filed_date_raw.strip()  # Default fallback

        try:
            # Handle format like: 2024-10-28 06:31:25
            dt = datetime.strptime(filed_date_raw.strip(), "%Y-%m-%d %H:%M:%S")
            # Desired format: Oct 28,2024, 06:31:25 UTC
            formatted = dt.strftime("%b %d,%Y, %H:%M:%S UTC")
        except ValueError:
            try:
                # Fallback for just date like 2024-10-28
                dt = datetime.strptime(filed_date_raw.strip(), "%Y-%m-%d")
                formatted = dt.strftime("%b %d,%Y, 00:00:00 UTC")
            except Exception:
                pass  # Use raw if parsing fails


        display_name = response.meta.get("display_name", "")
        company_name = re.split(r"\s+\(.*?\)", display_name)[0].strip()

        yield {
            "Filing_date": formatted,
            "Form_type": response.meta.get("form"),
            "Ticker": response.meta.get("ticker"),
            "Company_Name": company_name,
            "View Fillings": response.meta.get("pdf_url"),
        }
    
    # def parse(self, response, ticker):
    #     data = response.json()
        
    #     for hit in data.get("hits", {}).get("hits", []):
    #         src = hit.get("_source", {})
    #         raw_cik = src.get("ciks", [""])[0]
    #         raw_id = hit.get("_id", "")  # e.g. "0001964630-24-000015:vste-…pdf" or "0001564590-18-029294/opbk-10q_20180930.htm"

    #         # Normalize the _id by removing dashes in the first part
    #         if ':' in raw_id:
    #             first_part, second_part = raw_id.split(':', 1)
    #         elif '/' in raw_id:
    #             first_part, second_part = raw_id.split('/', 1)
    #         else:
    #             first_part, second_part = raw_id, ""

    #         cleaned_adsh = first_part.replace('-', '')
    #         adsh_filename = f"{cleaned_adsh}/{second_part}" if second_part else cleaned_adsh

    #         # Build the PDF or document URL
    #         try:
    #             adsh_part, filename = adsh_filename.split('/', 1)
    #             cik_folder = str(int(raw_cik))  # remove any leading zeros
    #             pdf_url = (
    #                 "https://www.sec.gov/Archives/edgar/data/"
    #                 f"{cik_folder}/{adsh_part}/{filename}"
    #             )
    #         except ValueError:
    #             pdf_url = None
    #         display_name = src.get("display_names", [""])[0]
    #         company_name = re.split(r"\s+\(.*?\)", display_name)[0].strip()
    #         raw_date = src.get("file_date")            # e.g. "2024-10-28"
    #         dt      = datetime.strptime(raw_date, "%Y-%m-%d")
    #         pretty  = dt.strftime("%b %d , %Y").lower()  # "Oct 28 , 2024" → "oct 28 , 2024"
            
    #         yield {
    #             # "Filing_date":   src.get("file_date"),
    #             "Filing_date":  pretty,
    #             "Form_type":     src.get("form"),
    #             "Ticker":        ticker,
    #             "Company_Name":  company_name,
    #             "View Fillings":           pdf_url,
    #         }
