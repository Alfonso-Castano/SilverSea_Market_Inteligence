# config/sources.py — Country configs, source URLs, and keywords
# Add new countries by appending to COUNTRIES with active=False

COUNTRIES = [
    {
        "name": "Singapore",
        "code": "SG",
        "active": True,
        "sources": [
            # Government & Regulatory
            {"name": "BCA", "url": "https://www1.bca.gov.sg/resources/newsroom/", "sector": "gov_agencies", "type": "website", "active": True},
            {"name": "MND", "url": "https://www.mnd.gov.sg/newsroom/press-releases", "sector": "gov_agencies", "type": "website", "active": True},
            {"name": "URA", "url": "https://www.ura.gov.sg/Corporate/Media-Room/Media-Releases", "sector": "gov_agencies", "type": "website", "active": True},
            {"name": "HDB", "url": "https://www.hdb.gov.sg", "sector": "gov_agencies", "type": "website", "active": True},
            {"name": "GeBIZ", "url": "https://www.gebiz.gov.sg/ptn/ppplisting/search.xhtml", "sector": "gov_agencies", "type": "website", "active": True},
            {"name": "Smart Nation / GovTech", "url": "https://www.smartnation.gov.sg/initiatives", "sector": "gov_agencies", "type": "website", "active": True},
            {"name": "JTC Corporation", "url": "https://www.jtc.gov.sg/about-jtc/news-and-stories", "sector": "gov_agencies", "type": "website", "active": True},
            {"name": "IMDA", "url": "https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches", "sector": "gov_agencies", "type": "website", "active": True, "fetcher": "dynamic"},  # JS-rendered page, needs browser rendering
            {"name": "Enterprise Singapore", "url": "https://www.enterprisesg.gov.sg/", "sector": "gov_agencies", "type": "website", "active": True},
            {"name": "SLA", "url": "https://www.sla.gov.sg/news/", "sector": "gov_agencies", "type": "website", "active": True},
            {"name": "GovTech", "url": "https://www.tech.gov.sg/media/", "sector": "gov_agencies", "type": "website", "active": True},
            # Associations
            {"name": "SGBC", "url": "https://www.sgbc.sg/news-insights/", "sector": "associations", "type": "website", "active": True},
            {"name": "SGTech", "url": "https://www.sgtech.org.sg/", "sector": "associations", "type": "website", "active": False},  # ASP.NET site, news pages return 404
            {"name": "REDAS", "url": "https://redas.com/news/", "sector": "associations", "type": "website", "active": True},
            {"name": "BCI Asia", "url": "https://www.bciasia.com/blog/", "sector": "associations", "type": "website", "active": True},
            {"name": "Construction Plus Asia", "url": "https://www.constructionplusasia.com/sg/category/news-and-events/", "sector": "associations", "type": "website", "active": False},  # SSL certificate verification error, site unreachable
            {"name": "BCA Academy", "url": "https://www.bcai.com.sg/", "sector": "associations", "type": "website", "active": True},
            {"name": "SIFMA Singapore", "url": "https://sifma.org.sg/", "sector": "associations", "type": "website", "active": True},
            {"name": "NTUC", "url": "https://www.ntuc.org.sg/", "sector": "associations", "type": "website", "active": True},
            # Customers
            {"name": "CapitaLand", "url": "https://www.capitaland.com/en/about-capitaland/newsroom.html", "sector": "customers", "type": "website", "active": True},
            {"name": "Mapletree", "url": "https://www.mapletree.com.sg/media-overview/newsroom/", "sector": "customers", "type": "website", "active": True},
            {"name": "Lendlease", "url": "https://www.lendlease.com/sg/media-centre/media-releases/", "sector": "customers", "type": "website", "active": True},
            {"name": "SGH", "url": "https://www.sgh.com.sg/about-us/news-room/news-releases", "sector": "customers", "type": "website", "active": True},
            {"name": "NUS", "url": "https://news.nus.edu.sg/press-room/", "sector": "customers", "type": "website", "active": True},
            {"name": "NTU", "url": "https://www.ntu.edu.sg/news", "sector": "customers", "type": "website", "active": True},
            {"name": "Keppel", "url": "https://www.keppel.com/en/news-and-media", "sector": "customers", "type": "website", "active": True},
            # Partners
            {"name": "AECOM", "url": "https://aecom.com/press-releases/", "sector": "partners", "type": "website", "active": True},
            {"name": "CPG Consultant", "url": "https://cpgcorp.com.sg/insights/", "sector": "partners", "type": "website", "active": True},  # /insights works; /news and /media return 404
            {"name": "Honeywell", "url": "https://www.honeywell.com/us/en/press", "sector": "partners", "type": "website", "active": True},
            {"name": "Cushman & Wakefield", "url": "https://www.cushmanwakefield.com/en/singapore/news", "sector": "partners", "type": "website", "active": True},
            {"name": "MCC", "url": "https://www.mcc.sg/", "sector": "partners", "type": "website", "active": True, "fetcher": "dynamic"},  # JS-only SPA — needs browser rendering
            {"name": "CSCEC", "url": "https://cscecsingapore.cscec.com/", "sector": "partners", "type": "website", "active": True},
            {"name": "CCCC", "url": "https://en.ccccltd.cn/", "sector": "partners", "type": "website", "active": False},  # Consistently times out — Chinese state contractor site unreachable from SG
            {"name": "CHEC", "url": "https://www.chec.bj.cn/", "sector": "partners", "type": "website", "active": False},  # SSL/connection errors on all URL variants, site unreachable
            {"name": "Sembcorp", "url": "https://www.sembcorp.com/en/media/", "sector": "partners", "type": "website", "active": True},
            {"name": "SJ Group", "url": "https://www.sjgroup.com/", "sector": "partners", "type": "website", "active": True, "fetcher": "stealth"},  # 403 bot protection — needs stealth
            {"name": "Meinhardt Group", "url": "https://meinhardtgroup.com/", "sector": "partners", "type": "website", "active": True},
            {"name": "BECA", "url": "https://www.beca.com/", "sector": "partners", "type": "website", "active": True},
            {"name": "Ramboll", "url": "https://www.ramboll.com/news", "sector": "partners", "type": "website", "active": True},
            {"name": "Azbil", "url": "https://www.azbil.com/", "sector": "partners", "type": "website", "active": True},
            {"name": "Johnson Controls", "url": "https://www.johnsoncontrols.com/media-center/news", "sector": "partners", "type": "website", "active": True},
            {"name": "Schneider Electric", "url": "https://www.se.com/ww/en/", "sector": "partners", "type": "website", "active": True, "fetcher": "stealth"},  # 403 bot protection — needs stealth
            {"name": "Quantum Automation", "url": "https://qa.com.sg/", "sector": "partners", "type": "website", "active": True},
            {"name": "ST Synthesis", "url": "https://www.stengg.com/en/newsroom/", "sector": "partners", "type": "website", "active": True},
            {"name": "Savills", "url": "https://www.savills.com.sg/insight-and-opinion/", "sector": "partners", "type": "website", "active": True},
            # Competitors
            {"name": "Hiverlab", "url": "https://hiverlab.com/news", "sector": "competitors", "type": "website", "active": True},
            {"name": "G Element", "url": "https://www.gelement.com/updates-resources/blog/", "sector": "competitors", "type": "website", "active": True},
            {"name": "TwinLogic", "url": "https://twinlogic.tech/", "sector": "competitors", "type": "website", "active": True},
            {"name": "Axomem", "url": "https://axomem.io/", "sector": "competitors", "type": "website", "active": True},
            {"name": "DataMesh", "url": "https://datamesh.com/about/news", "sector": "competitors", "type": "website", "active": True},
            {"name": "FacilityBot", "url": "https://facilitybot.co/", "sector": "competitors", "type": "website", "active": False},  # no blog/news page found, homepage only
            {"name": "Cryotos", "url": "https://www.cryotos.com/blog", "sector": "competitors", "type": "website", "active": True},
            {"name": "TwinMatrix", "url": "https://www.twinmatrix.net/", "sector": "competitors", "type": "website", "active": True},
            {"name": "Minuscule Technologies", "url": "https://www.minusculetechnologies.com/", "sector": "competitors", "type": "website", "active": True},
            {"name": "Alstern Technologies", "url": "https://alstern-technologies.com/", "sector": "competitors", "type": "website", "active": True, "fetcher": "stealth"},  # 403 bot protection — needs stealth
            {"name": "Aperio", "url": "https://aperio.ai/", "sector": "competitors", "type": "website", "active": True, "fetcher": "stealth"},  # 403 Forbidden with default fetcher — try stealth
            {"name": "Nuvola Media", "url": "https://www.nuvolamedia.com/", "sector": "competitors", "type": "website", "active": True},
            {"name": "SSI Corporate", "url": "https://www.ssi-corporate.com/", "sector": "competitors", "type": "website", "active": True},
            {"name": "NeuronCloud", "url": "https://www.neuroncloud.ai/", "sector": "competitors", "type": "website", "active": True},
            # General news — gap-filling, not tied to a specific sector
            {"name": "EdgeProp Singapore", "url": "https://www.edgeprop.sg/property-news", "sector": "general_news", "type": "website", "active": True},
            {"name": "The Business Times", "url": "https://www.businesstimes.com.sg/property", "sector": "general_news", "type": "website", "active": True},
            {"name": "Straits Times Property", "url": "https://www.straitstimes.com/property", "sector": "general_news", "type": "website", "active": True},
        ],
        "priority_keywords": [
            # Tender/RFP language — highest BD priority
            "tender", "RFP", "ITQ", "ITT", "GeBIZ",
            # Core product-category terms — direct Silversea relevance
            "digital twin", "BIM", "smart FM", "smart building", "proptech",
            "building automation", "3D scanning", "point cloud",
            "facility management", "smart facility",
        ],
        "keywords": [
            # Digital twin & immersive tech
            "virtual tour", "3D scan", "3D visualization",
            "immersive", "XR", "extended reality", "virtual reality", "augmented reality",
            "metaverse", "spatial computing",
            # Smart FM & buildings
            "building management", "smart estate", "intelligent building",
            "IoT", "CMMS", "predictive maintenance",
            # Construction & development
            "construction technology", "contech", "greenfield", "smart construction",
            "BCA Green Mark", "IDD", "integrated digital delivery",
            "TOP inspection", "defect inspection", "virtual inspection",
            "sustainability", "green building", "net zero",
            # Government & tenders
            "public sector", "smart nation", "government digital", "built environment",
            # Partners vocabulary
            "M&E integration", "BMS", "building automation system", "asset management system",
            # Tracked entity names — 1x weight, not auto-pass
            # Competitors
            "Hiverlab", "Gelement", "TwinLogic", "TwinMatrix", "Axomem", "DataMesh",
            "FacilityBot", "Cryotos", "Minuscule Technologies", "Alstern Technologies",
            "Aperio", "Nuvola Media", "SSI Corporate", "NeuronCloud",
            # Customers
            "CapitaLand", "Mapletree", "Lendlease", "JTC", "HDB estate",
            # Ecosystem players
            "MCC", "CSCEC", "CCCC", "CHEC", "Sembcorp", "SJ Group",
            "Meinhardt", "BECA", "Ramboll", "Azbil",
            "Johnson Controls", "Schneider", "Quantum Automation",
            "ST Synthesis", "Savills",
        ],
    },
    # Future countries — flip active to True when ready:
    # {"name": "Malaysia", "code": "MY", "active": False, "sources": [], "keywords": []},
    # {"name": "Indonesia", "code": "ID", "active": False, "sources": [], "keywords": []},
    # {"name": "Vietnam", "code": "VN", "active": False, "sources": [], "keywords": []},
]
