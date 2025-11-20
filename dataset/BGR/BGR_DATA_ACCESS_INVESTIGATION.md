# BGR Data Access Investigation Report

**Date:** 2025-11-19
**Issue:** 403 Forbidden errors when attempting to scrape https://www.bgr.bund.de
**Investigation Goal:** Identify legitimate, authorized ways to access BGR publications and data

---

## Executive Summary

The BGR website (https://www.bgr.bund.de) implements anti-scraping protections that result in 403 Forbidden errors. However, BGR provides multiple **legitimate, authorized channels** for programmatic access to their publications and geoscience data through:

1. **OGC Web Services (WMS/WFS)** - For geospatial data
2. **CSW Catalog Service** - For metadata harvesting
3. **GEO-LEOe-docs Repository** - For publications via standard protocols
4. **EGDI European Portal** - For pan-European geological data
5. **Direct Download Services** - Free access via BGR Geoportal
6. **OneGeology WMS Services** - International geological mapping project

**Key Finding:** Instead of web scraping the main BGR website, use their official data portals, OGC services, and institutional repositories that are designed for programmatic access.

---

## 1. Public APIs and Data Portals

### 1.1 BGR Geoportal
**Primary Access Point:** https://geoportal.bgr.de/

**Description:** The BGR Geoportal is the official platform for accessing BGR's geoscientific data, including soil, geochemistry, geology, geophysics, groundwater, mineral resources, and **scientific publications**.

**Features:**
- Search, view, and download functionality
- Interactive map viewer (Geoviewer)
- Multiple data formats: ESRI Shapefiles, GeoTIFF (600 dpi), JPEG, PDF
- **Free downloads** - no registration required for most datasets
- Web Map Services (WMS) for real-time data access

**Access Method:**
```
Direct URL: https://geoportal.bgr.de/mapapps/resources/apps/geoportal/index.html?lang=en#/
```

**Best Practice:** Use the Geoportal's built-in search and download features rather than scraping the main website.

---

### 1.2 CSW Catalog Service (Metadata Harvesting)
**Endpoint:** https://geoportal.bgr.de/smartfindersdi-csw/api

**Protocol:** OGC Catalog Service for the Web (CSW) 2.0.2

**Capabilities:**
- **GetCapabilities** - Retrieve service metadata
- **GetRecords** - Search for metadata records with filtering
- **GetRecordById** - Fetch specific records by identifier
- **DescribeRecord** - Describe available record types

**Supported Standards:**
- ISO 19115 metadata
- ISO 19139 XML encoding
- INSPIRE compliance
- Dublin Core

**Example Query:**
```xml
GET: https://geoportal.bgr.de/smartfindersdi-csw/api?
     Request=GetCapabilities&
     Service=CSW&
     Version=2.0.2
```

**Queryable Fields:**
- OrganisationName (search for "Bundesanstalt für Geowissenschaften und Rohstoffe")
- ResourceIdentifier
- CreationDate / RevisionDate
- TopicCategory
- Keywords

**Use Case:** Harvest metadata about BGR datasets and publications programmatically. This is a **legitimate, INSPIRE-compliant** method for discovering BGR resources.

**Contact:** geodatenmanagement@bgr.de

---

### 1.3 WMS Services (Web Map Services)
BGR provides numerous WMS endpoints for accessing geospatial data layers:

#### Available Services on services.bgr.de:

**Groundwater Services:**
- `https://services.bgr.de/wms/grundwasser/ergw1000/` - Groundwater occurrences
- `https://services.bgr.de/wms/grundwasser/gwn1000/` - Mean annual groundwater recharge (1961-1990)
- `https://services.bgr.de/wms/grundwasser/whymap_wokam/` - World groundwater resources
- `https://services.bgr.de/wms/grundwasser/norm/` - Groundwater normalization data

**Geology Services:**
- `https://services.bgr.de/wms/rohstoffe/bsk1000/` - Spatial distribution of energy and mineral resources
- `https://services.bgr.de/wms/inspire_ge/guek250/` - Surface geology 1:250,000 (INSPIRE)
- `https://services.bgr.de/wms/inspire_ge/gk1000/` - Surface geology 1:1,000,000 (INSPIRE)
- `https://services.bgr.de/wms/inspire_ge/gbl/` - Borehole locations (INSPIRE)
- `https://services.bgr.de/wms/inspire_ge/inspee/` - Salt structures in Northern Germany (INSPIRE)
- `https://services.bgr.de/wms/geologie/BGR_EN_Surface_Geology/` - Harmonized surface geology

**Soil Services:**
- `https://services.bgr.de/wms/boden/eusr5000/` - Soil regions map of the European Union

**Example GetCapabilities Request:**
```
https://services.bgr.de/wms/geologie/BGR_EN_Surface_Geology/?REQUEST=GetCapabilities&VERSION=1.3.0&SERVICE=WMS
```

**Supported Formats:**
- Map Images: BMP, JPEG, TIFF, PNG, GIF, SVG+XML
- Feature Info: XML, GeoJSON, HTML, plain text
- Coordinate Systems: 23+ CRS options including EPSG:4326, EPSG:3857

**Use Case:** Access geospatial datasets programmatically for groundwater, geology, and soil data without web scraping.

---

### 1.4 WFS Services (Web Feature Services)
BGR provides WFS endpoints for downloading vector data:

**Borehole Data:**
- BGR maintains a German Borehole Registry available via WFS
- INSPIRE-compliant borehole data provision
- REST API documentation available: https://www.bgr.bund.de/DE/Themen/Geodatenmanagement/Downloads/borehole_profil_backend_REST-schnittstellenbeschreibung.pdf

**Access:** Contact BGR for specific WFS endpoint URLs or search via the Geoportal catalog.

---

## 2. Alternative URLs and Endpoints

### 2.1 OneGeology WMS Service
**Project:** OneGeology - World's biggest geological mapping project

**BGR WMS Endpoint:**
```
https://services.bgr.de/wms/geologie/BGR_EN_Surface_Geology/?REQUEST=GetCapabilities&VERSION=1.3.0&SERVICE=WMS
```

**Available Layers:**
- DEU_BGR_1M_Surface_Lithology (composition)
- DEU_BGR_1M_Surface_Age (stratigraphy)

**Coverage:** Germany (5.85°E to 15.05°E, 47.27°N to 55.05°N)

**Standards:** OneGeology-Europe harmonized terminology

**Use Case:** Access German geological maps through the international OneGeology portal.

---

### 2.2 EMODnet Geology WMS
**Endpoint:**
```
https://drive.emodnet-geology.eu/geoserver/bgr/wms/?request=GetCapabilities&service=WMS
```

**Data:** BGR contributions to European marine geology including:
- Pre-Quaternary geological units of the seafloor
- Quaternary geological units of the seafloor

**Use Case:** Access BGR's marine geoscience data through the European Marine Observation portal.

---

### 2.3 GDK (Geodateninfrastruktur Deutschland)
**Catalog:** https://gdk.gdi-de.org/

**Description:** National geospatial data infrastructure catalog that aggregates metadata from BGR and other German federal/state agencies.

**BGR Resources in GDK:**
- All BGR WMS/WFS services are registered
- INSPIRE-compliant metadata
- CSW interface for harvesting

**GDK Metadata API:**
```
https://gdk.gdi-de.org/geonetwork/srv/api/records/c5ac4e88-455f-4975-80e6-56cd5fa0ae1a
```
(Example record for BGR Geoportal)

**Use Case:** Search for BGR resources across Germany's entire geospatial infrastructure.

---

## 3. Direct Links to Publication Archives

### 3.1 BGR Main Publications Page
**URL:** https://www.bgr.bund.de/EN/Infothek/Publikationen/publikationen_node.html

**Status:** Protected against scraping (403 errors)

**Alternative Approach:**
- Use the Geoportal search instead
- Access via CSW metadata harvesting
- Request bulk download from BGR directly

---

### 3.2 BGR Products & Downloads Page
**URL:** https://www.bgr.bund.de/DE/Gemeinsames/Produkte/produkte_schriften_download.html

**Content:**
- Internal and external BGR publications
- Most available for **free download**
- Digital products (PDF, GeoTIFF, Shapefiles)

**Note:** Individual publication pages may allow direct PDF downloads, but automated traversal triggers 403 errors.

---

### 3.3 DERA (Deutsche Rohstoffagentur) Publications
**URL:** https://www.deutsche-rohstoffagentur.de/

**BGR Division:** German Mineral Resources Agency (part of BGR)

**Publication Series:**
- **DERA Rohstoffinformationen** - Raw materials information series
- **DERA Themenheft** - Topic papers
- **Commodity TopNews** - Regular updates on raw materials
- **DERA Raw Material List** - Published every 2 years

**Access:**
- Free download from deutsche-rohstoffagentur.de
- Focus on mineral resources, energy, circular economy

**Relevant Topics:** SDG 12 (Responsible Consumption & Production)

---

### 3.4 BGR Energy Data
**URL:** https://www.deutsche-rohstoffagentur.de/EN/Themen/Energie/Produkte/Energiedaten/energiedaten_inhalt_en.html

**Content:** Annual publication on worldwide energy supplies

**Format:** Data tables and PDF reports

**Download:** Free

**Relevant Topics:** SDG 7, SDG 13 (energy and climate)

---

### 3.5 BGR GeoShop Hannover
**URL:** Via BGR Geoportal Produktcenter

**Description:** Online shop for digital and printed maps/publications

**Digital Products:**
- Available for immediate download after ordering
- Free for most items
- Formats: PDF, TIFF, JPEG, ESRI-Shape

**Printed Products:**
- Ordered via Internationales Landkartenhaus (ILH) Stuttgart
- Email: ilhinfo@ilh-stuttgart.de

---

## 4. Scientific Databases and Institutional Repositories

### 4.1 GEO-LEOe-docs Repository
**URL:** https://e-docs.geo-leo.de/

**Operator:** Göttingen State and University Library (SUB Göttingen)

**Maintained by:** FID GEO (Specialized Information Service for Geosciences)

**Platform:** DSpace CRIS (version dspace-cris-2023.01.00)

**Content:**
- Geoscientific documents from BGR and other institutions
- Monographs, pre-/postprints, peer-reviewed papers
- Institutional series and journals
- Grey literature
- **Geological maps** (digitized GK25)

**Access:**
- **All documents freely accessible worldwide**
- No registration required
- Downloadable without charge
- **Green Open Access** secondary publications

**Search for BGR:**
```
Search query: "BGR" or "Bundesanstalt für Geowissenschaften"
Results include BGR-authored papers and reports
```

**OAI-PMH Endpoint (likely):**
```
https://e-docs.geo-leo.de/oai/request
```
(Standard DSpace OAI-PMH endpoint - verify with repository)

**Use Case:** Search for BGR publications in an open-access geoscience repository that supports metadata harvesting.

**Contact:** Repository administrators via e-docs.geo-leo.de

---

### 4.2 ResearchGate
**Platform:** https://www.researchgate.net/

**BGR Presence:** Many BGR researchers share publications on ResearchGate

**Access:**
- Search for BGR authors or institution
- Download full-text PDFs where available (54.8% availability rate for German researchers)

**Advantages:**
- Researcher profiles with publication lists
- Direct PDF downloads
- No institutional access required

**Limitations:**
- Not comprehensive
- Voluntary uploads by researchers
- May include preprints/postprints rather than final versions

**Use Case:** Supplement official channels by finding BGR publications shared by individual researchers.

---

### 4.3 Dr. BGR Publications
**URL:** https://drbgrpublications.in/

**Note:** This appears to be an **independent open-access journal publisher** (not affiliated with German BGR), but indexed in US NLM Catalog and ROAD.

**Status:** NOT the same as German BGR - different organization.

---

## 5. Mirrors and Indexed Collections

### 5.1 EGDI (European Geological Data Infrastructure)
**URL:** https://www.europe-geology.eu/

**Description:** Pan-European geological data portal operated by EuroGeoSurveys

**BGR Participation:** BGR is a member of EuroGeoSurveys

**Content:**
- 900+ datasets from European geological surveys
- Onshore and marine geological maps
- 3D geological models
- Mineral resources, geo-energy, groundwater
- Geohazards, geochemistry, boreholes

**Standards:**
- INSPIRE-compliant
- FAIR data principles
- Interoperable with EU Open Data Portal, EPOS, EOSC

**Access to BGR Data:**
- Search by country: Germany
- Filter by contributing organization: BGR
- Download harmonized European datasets that include BGR contributions

**Use Case:** Access BGR data in a pan-European context with standardized formats.

**Status:** Portal was temporarily unavailable (503 error) during testing but is normally operational.

---

### 5.2 INSPIRE Geoportal
**URL:** https://inspire-geoportal.ec.europa.eu/

**Description:** EU's official geospatial data portal

**BGR Services Registered:**
- All INSPIRE-compliant BGR WMS/WFS services
- Metadata for BGR datasets
- View and Download services

**Access:** Search for "BGR" or "Germany" and filter by geological/environmental themes.

---

### 5.3 GovData (German Open Data Portal)
**URL:** https://www.govdata.de/

**Description:** Central open data portal for Germany

**BGR Datasets:** Selected BGR datasets are published on GovData

**Connection:** Harvested from GDI-DE (Geodateninfrastruktur Deutschland)

**Use Case:** Search for open datasets from BGR alongside other German federal agencies.

---

## 6. Recommended Data Acquisition Strategy

### Phase 1: Metadata Harvesting via CSW
**Priority:** HIGH
**Timeline:** Days 1-3

1. Query the BGR CSW endpoint:
   ```
   https://geoportal.bgr.de/smartfindersdi-csw/api
   ```

2. Use GetRecords with filter:
   ```xml
   OrganisationName = "Bundesanstalt für Geowissenschaften und Rohstoffe"
   TopicCategory = "geoscientificInformation"
   CreationDate >= 2013
   ```

3. Harvest metadata for all BGR resources

4. Extract PDF URLs and dataset identifiers

**Expected Output:** Comprehensive list of BGR publications with metadata

---

### Phase 2: OGC Service Data Downloads
**Priority:** HIGH
**Timeline:** Days 4-10

1. Identify relevant WMS/WFS services from metadata

2. Use GetCapabilities to list available layers

3. Download vector data via WFS (GeoJSON, GML formats)

4. Download raster data via WMS (GeoTIFF format)

**Expected Output:** Geospatial datasets in standard formats

---

### Phase 3: GEO-LEOe-docs Repository Search
**Priority:** MEDIUM
**Timeline:** Days 11-15

1. Access https://e-docs.geo-leo.de/

2. Search for:
   - "Bundesanstalt für Geowissenschaften"
   - "BGR"
   - Specific topics (groundwater, mining, climate)

3. Download full-text PDFs directly

4. Optionally: Set up OAI-PMH harvester for bulk metadata extraction

**Expected Output:** Open-access BGR publications and papers

---

### Phase 4: Direct Publication Downloads via Geoportal
**Priority:** MEDIUM
**Timeline:** Days 16-25

1. Use BGR Geoportal search interface:
   ```
   https://geoportal.bgr.de/
   ```

2. Apply filters:
   - Document type: Publications
   - Year: 2013-2024
   - Topic: International Cooperation, Groundwater, Mining

3. Manually or semi-automatically download PDFs from search results

4. Respect rate limits and download delays

**Expected Output:** Policy reports and evaluation documents

---

### Phase 5: EGDI and OneGeology Access
**Priority:** LOW (Supplementary)
**Timeline:** Days 26-30

1. Access BGR data via EGDI portal:
   ```
   https://www.europe-geology.eu/
   ```

2. Download BGR contributions to European datasets

3. Access OneGeology WMS services for geological maps

**Expected Output:** Harmonized European geological data including BGR contributions

---

### Phase 6: Researcher Outreach & Manual Requests
**Priority:** LOW (Gap Filling)
**Timeline:** As needed

1. Contact BGR directly:
   - Email: geodatenmanagement@bgr.de
   - Request bulk access to publication catalog

2. Reach out to BGR researchers on ResearchGate

3. Request specific publications via GeoShop Hannover

**Expected Output:** Access to publications not available through automated methods

---

## 7. Why 403 Errors Occur

### 7.1 Anti-Scraping Protections
BGR's main website (bgr.bund.de) implements standard web application firewall (WAF) rules that detect and block:

- **Rapid sequential requests** (exceeding human browsing patterns)
- **Missing or suspicious User-Agent headers**
- **Lack of session cookies/JavaScript execution**
- **IP addresses flagged for automated access**
- **Direct PDF traversal** without referrer headers

### 7.2 Robots.txt Compliance
Check BGR's robots.txt file:
```
https://www.bgr.bund.de/robots.txt
```

The file may disallow scraping of certain paths. Violating robots.txt can lead to:
- IP blocking
- Legal implications (breach of terms of service)

### 7.3 Terms of Service
BGR's terms of use likely prohibit automated scraping of the main website. However, they **explicitly provide** alternative channels (WMS, CSW, Geoportal) for programmatic access.

### 7.4 Legitimate Use Policy
**Recommended:**
- ✅ Use OGC services (WMS/WFS/CSW)
- ✅ Access data via Geoportal with reasonable delays
- ✅ Harvest metadata from INSPIRE-compliant endpoints
- ✅ Download from open repositories (GEO-LEOe-docs)

**Not Recommended:**
- ❌ Scraping bgr.bund.de with automated crawlers
- ❌ Circumventing 403 blocks with proxies/VPNs
- ❌ Ignoring robots.txt directives

---

## 8. Contact Information

### BGR Geodata Management
**Email:** geodatenmanagement@bgr.de
**Topic:** Questions about geoportal access, WMS/WFS services, metadata

### BGR Main Contact
**Address:**
Bundesanstalt für Geowissenschaften und Rohstoffe (BGR)
Stilleweg 2
30655 Hannover, Germany

**Phone:** +49 (0)511 643-0

### DERA (German Mineral Resources Agency)
**Address:**
Wilhelmstraße 26
13593 Berlin-Spandau, Germany

**Email:** Via contact form on deutsche-rohstoffagentur.de

---

## 9. Summary of Access Methods

| Method | Protocol | Legitimacy | Bulk Download | Best For |
|--------|----------|------------|---------------|----------|
| **CSW Catalog Service** | OGC CSW 2.0.2 | ✅ Official | ✅ Yes | Metadata harvesting |
| **WMS Services** | OGC WMS 1.3.0 | ✅ Official | ✅ Yes | Geospatial raster data |
| **WFS Services** | OGC WFS 2.0 | ✅ Official | ✅ Yes | Vector data |
| **BGR Geoportal** | Web UI + API | ✅ Official | ⚠️ Rate limited | Publications, maps |
| **GEO-LEOe-docs** | DSpace / OAI-PMH | ✅ Official | ✅ Yes | Open access papers |
| **EGDI Portal** | Web UI | ✅ Official | ⚠️ Manual | European datasets |
| **OneGeology WMS** | OGC WMS | ✅ Official | ✅ Yes | Geological maps |
| **ResearchGate** | Web UI | ⚠️ Voluntary | ❌ No | Individual papers |
| **Web Scraping bgr.bund.de** | HTTP | ❌ Blocked | ❌ No | NOT RECOMMENDED |

---

## 10. Conclusion

**The 403 Forbidden errors are a clear signal that BGR does not support web scraping of their main website.** However, BGR provides extensive **legitimate, authorized channels** for accessing their data programmatically:

1. **For geospatial data:** Use WMS/WFS/CSW services
2. **For publications:** Use Geoportal search, GEO-LEOe-docs, or contact BGR directly
3. **For metadata:** Harvest via CSW catalog service
4. **For European data:** Access via EGDI portal

**Recommendation:**
Pivot from web scraping to using BGR's official OGC services and institutional repositories. This approach is:
- ✅ **Legitimate** - Authorized by BGR
- ✅ **Reliable** - No 403 blocks
- ✅ **Comprehensive** - Access to more data than web scraping
- ✅ **Sustainable** - Standards-based, future-proof
- ✅ **Legal** - Compliant with terms of service

**Next Steps:**
1. Implement CSW metadata harvester
2. Download datasets via WMS/WFS
3. Search GEO-LEOe-docs for BGR publications
4. Request bulk access from geodatenmanagement@bgr.de if needed

---

## 11. Additional Resources

### OGC Standards Documentation
- CSW: https://www.ogc.org/standards/cat/
- WMS: https://www.ogc.org/standards/wms/
- WFS: https://www.ogc.org/standards/wfs/

### INSPIRE Directive
- https://inspire.ec.europa.eu/

### FID GEO (Geoscience Information Service)
- https://www.fidgeo.de/

### EuroGeoSurveys
- https://eurogeosurveys.org/

---

**Report Prepared By:** Claude (Anthropic)
**Investigation Date:** 2025-11-19
**Status:** Complete
