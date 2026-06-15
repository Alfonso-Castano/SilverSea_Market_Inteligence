# config/sources.py — Country configs, source URLs, and keywords
# Add new countries by appending to COUNTRIES with active=False

COUNTRIES = [
    {
        "name": "Singapore",
        "code": "SG",
        "active": True,
        "sources": [
            # Government & Regulatory
            {"name": "BCA", "url": "https://www.bca.gov.sg/newsroom/", "type": "government"},
            {"name": "MND", "url": "https://www.mnd.gov.sg/newsroom/", "type": "government"},
            {"name": "URA", "url": "https://www.ura.gov.sg/Corporate/Media-Room/Media-Releases", "type": "government"},
            {"name": "HDB", "url": "https://www.hdb.gov.sg/about-us/news-and-publications/press-releases", "type": "government"},
            {"name": "Smart Nation", "url": "https://www.smartnation.gov.sg/media-hub/press-releases", "type": "government"},
            {"name": "JTC", "url": "https://www.jtc.gov.sg/who-we-are/newsroom", "type": "prospect"},
            # Industry News
            {"name": "Construction Plus Asia", "url": "https://www.construction-plus.com/singapore/", "type": "industry"},
            {"name": "EdgeProp Singapore", "url": "https://www.edgeprop.sg/property-news", "type": "industry"},
            {"name": "The Business Times", "url": "https://www.businesstimes.com.sg/property", "type": "industry"},
            # Competitor Monitoring
            {"name": "Hiverlab", "url": "https://www.hiverlab.com/news", "type": "competitor"},
            {"name": "Gelement", "url": "https://www.gelement.com/news", "type": "competitor"},
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
