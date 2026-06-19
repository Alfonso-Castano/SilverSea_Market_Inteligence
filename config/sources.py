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
            # Associations
            {"name": "SGBC", "url": "https://www.sgbc.sg/news-insights/", "sector": "associations", "type": "website", "active": True},
            {"name": "BCI Asia", "url": "https://www.bciasia.com/blog/", "sector": "associations", "type": "website", "active": True},
            {"name": "Construction Plus Asia", "url": "https://www.constructionplusasia.com/sg/category/news-and-events/", "sector": "associations", "type": "website", "active": True},
            # Customers
            {"name": "CapitaLand", "url": "https://www.capitaland.com/en/about-capitaland/newsroom.html", "sector": "customers", "type": "website", "active": True},
            {"name": "Mapletree", "url": "https://www.mapletree.com.sg/media-overview/newsroom/", "sector": "customers", "type": "website", "active": True},
            {"name": "Lendlease", "url": "https://www.lendlease.com/sg/media-centre/media-releases/", "sector": "customers", "type": "website", "active": True},
            {"name": "SGH", "url": "https://www.sgh.com.sg/about-us/news-room/news-releases", "sector": "customers", "type": "website", "active": True},
            {"name": "NUS", "url": "https://news.nus.edu.sg/press-room/", "sector": "customers", "type": "website", "active": True},
            {"name": "NTU", "url": "https://www.ntu.edu.sg/news", "sector": "customers", "type": "website", "active": True},
            # Partners (placeholder — real list pending supervisor input)
            {"name": "Partners TBD", "url": "https://example.com", "sector": "partners", "type": "website", "active": False},
            # Competitors
            {"name": "Hiverlab", "url": "https://hiverlab.com/news", "sector": "competitors", "type": "website", "active": True},
            {"name": "G Element", "url": "https://www.gelement.com/updates-resources/blog/", "sector": "competitors", "type": "website", "active": True},
            {"name": "TwinLogic", "url": "https://twinlogic.tech/", "sector": "competitors", "type": "website", "active": True},
            {"name": "TwinMatrix", "url": "https://www.twinmatrix.net/", "sector": "competitors", "type": "website", "active": True},
            {"name": "Axomem", "url": "https://axomem.io/", "sector": "competitors", "type": "website", "active": True},
            {"name": "DataMesh", "url": "https://datamesh.com/about/news", "sector": "competitors", "type": "website", "active": True},
            # General news — gap-filling, not tied to a specific sector
            {"name": "EdgeProp Singapore", "url": "https://www.edgeprop.sg/property-news", "sector": "general_news", "type": "website", "active": True},
            {"name": "The Business Times", "url": "https://www.businesstimes.com.sg/property", "sector": "general_news", "type": "website", "active": True},
        ],
        "keywords": [
            # Digital twin & immersive tech
            "digital twin", "virtual tour", "3D scan", "BIM", "point cloud",
            "immersive", "XR", "extended reality", "virtual reality", "augmented reality",
            "metaverse", "spatial computing",
            # Smart FM & buildings
            "smart building", "smart FM", "facilities management", "building management",
            "proptech", "smart estate", "intelligent building", "building automation",
            # Construction & development
            "construction technology", "contech", "greenfield", "smart construction",
            "BCA Green Mark", "IDD", "integrated digital delivery",
            # Government & tenders
            "GeBIZ", "ITQ", "ITT", "RFP", "tender", "public sector",
            "smart nation", "government digital", "built environment",
            # Competitor names
            "Hiverlab", "Gelement", "TwinLogic", "TwinMatrix", "Axomem", "DataMesh",
            # Customer names
            "JTC", "CapitaLand", "Mapletree", "Lendlease", "HDB estate",
        ],
        "entities": {
            "government": ["BCA", "MND", "URA", "HDB", "SGBC", "JTC", "Smart Nation"],
            "prospects": ["JTC Corporation", "CapitaLand", "Mapletree", "Lendlease",
                          "SGH", "NUH", "TTSH", "Alexandra Hospital",
                          "NUS", "NTU", "SMU"],
            "competitors": ["Hiverlab", "Gelement", "TwinLogic", "TwinMatrix", "Axomem", "DataMesh"],
        },
    },
    # Future countries — flip active to True when ready:
    # {"name": "Malaysia", "code": "MY", "active": False, "sources": [], "keywords": [], "entities": {}},
    # {"name": "Indonesia", "code": "ID", "active": False, "sources": [], "keywords": [], "entities": {}},
    # {"name": "Vietnam", "code": "VN", "active": False, "sources": [], "keywords": [], "entities": {}},
]
