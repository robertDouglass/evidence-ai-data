# BGR Quick Access Guide

**Quick reference for legitimate BGR data access methods**

---

## 🔑 Key Endpoints

### CSW Catalog Service (Metadata Harvesting)
```bash
# Get service capabilities
curl "https://geoportal.bgr.de/smartfindersdi-csw/api?Request=GetCapabilities&Service=CSW&Version=2.0.2"

# Search for BGR records
curl "https://geoportal.bgr.de/smartfindersdi-csw/api?Request=GetRecords&Service=CSW&Version=2.0.2&elementSetName=full&resultType=results"
```

**Contact:** geodatenmanagement@bgr.de

---

## 🗺️ WMS Services (Quick Access)

### Surface Geology
```
https://services.bgr.de/wms/geologie/BGR_EN_Surface_Geology/?REQUEST=GetCapabilities&VERSION=1.3.0&SERVICE=WMS
```

### Groundwater Resources
```
https://services.bgr.de/wms/grundwasser/ergw1000/?service=WMS&version=1.3.0&request=getCapabilities
https://services.bgr.de/wms/grundwasser/gwn1000/?REQUEST=GetCapabilities&SERVICE=wms&VERSION=1.3.0
```

### Mineral Resources
```
https://services.bgr.de/wms/rohstoffe/bsk1000/?REQUEST=GetCapabilities&SERVICE=WMS
```

### INSPIRE Geology Services
```
# Geological map 1:250,000
https://services.bgr.de/wms/inspire_ge/guek250/?REQUEST=GetCapabilities&SERVICE=wms&VERSION=1.3.0

# Geological map 1:1,000,000
https://services.bgr.de/wms/inspire_ge/gk1000/?REQUEST=GetCapabilities&SERVICE=WMS

# Borehole locations
https://services.bgr.de/wms/inspire_ge/gbl/?REQUEST=GetCapabilities&SERVICE=WMS
```

### Soil
```
https://services.bgr.de/wms/boden/eusr5000/?REQUEST=GetCapabilities&VERSION=1.3.0&SERVICE=WMS
```

---

## 📚 Publication Repositories

### BGR Geoportal (Main Access)
```
https://geoportal.bgr.de/
```
- Search publications, datasets, maps
- Free downloads (PDF, GeoTIFF, Shapefiles)
- Interactive map viewer

### GEO-LEOe-docs (Open Access Repository)
```
https://e-docs.geo-leo.de/
```
- Search for "BGR" or "Bundesanstalt für Geowissenschaften"
- DSpace repository with OAI-PMH support
- Free worldwide access

### DERA (German Mineral Resources Agency)
```
https://www.deutsche-rohstoffagentur.de/
```
- Raw materials publications
- Commodity Top News
- Energy data reports

---

## 🌍 European Portals

### EGDI (European Geological Data Infrastructure)
```
https://www.europe-geology.eu/
```
- Pan-European geological data
- BGR contributions included
- 900+ datasets

### INSPIRE Geoportal
```
https://inspire-geoportal.ec.europa.eu/
```
- Search for "BGR" or "Germany"
- INSPIRE-compliant services

### GDI-DE (German Geospatial Infrastructure)
```
https://gdk.gdi-de.org/
```
- National catalog
- BGR metadata included

---

## 🚀 Quick Start Commands

### Python: Query CSW Catalog
```python
from owslib.csw import CatalogueServiceWeb

csw = CatalogueServiceWeb('https://geoportal.bgr.de/smartfindersdi-csw/api')
csw.getrecords2(maxrecords=10, esn='full')

for rec in csw.records:
    print(csw.records[rec].title)
    print(csw.records[rec].abstract)
```

### Python: Access WMS Layer
```python
from owslib.wms import WebMapService

wms = WebMapService('https://services.bgr.de/wms/geologie/BGR_EN_Surface_Geology/', version='1.3.0')
print(list(wms.contents))

# Get map image
img = wms.getmap(
    layers=['DEU_BGR_1M_Surface_Lithology'],
    srs='EPSG:4326',
    bbox=(5.85, 47.27, 15.05, 55.05),
    size=(800, 600),
    format='image/png'
)

with open('bgr_geology.png', 'wb') as f:
    f.write(img.read())
```

### cURL: Download WMS Layer as GeoTIFF
```bash
curl "https://services.bgr.de/wms/geologie/BGR_EN_Surface_Geology/?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=DEU_BGR_1M_Surface_Lithology&CRS=EPSG:4326&BBOX=5.85,47.27,15.05,55.05&WIDTH=800&HEIGHT=600&FORMAT=image/geotiff" -o bgr_geology.tif
```

### GDAL/OGR: Access WMS as Raster
```bash
# Create GDAL WMS service file
cat > bgr_wms.xml << EOF
<GDAL_WMS>
  <Service name="WMS">
    <ServerUrl>https://services.bgr.de/wms/geologie/BGR_EN_Surface_Geology/</ServerUrl>
    <Version>1.3.0</Version>
    <Layers>DEU_BGR_1M_Surface_Lithology</Layers>
    <SRS>EPSG:4326</SRS>
  </Service>
</GDAL_WMS>
EOF

# Access with GDAL
gdalinfo bgr_wms.xml
gdal_translate -of GTiff -projwin 5.85 55.05 15.05 47.27 bgr_wms.xml output.tif
```

---

## 📋 Supported Output Formats

### WMS
- **Images:** PNG, JPEG, TIFF, BMP, GIF, SVG+XML
- **Feature Info:** XML, GeoJSON, HTML, plain text

### WFS
- **Vector:** GML, GeoJSON, Shapefile

### CSW
- **Metadata:** ISO 19139 XML, Dublin Core

---

## 🔍 Search Queries

### Find Groundwater Publications
```
Topic: Groundwater
Keywords: "groundwater management", "water resources", "SDG 6"
Year: 2013-2024
```

### Find Mining Governance Reports
```
Topic: International Cooperation, Mining
Keywords: "sustainable mining", "mining governance", "SDG 12"
Year: 2013-2024
```

### Find Climate Risk Documents
```
Topic: Geoscience, Climate
Keywords: "climate risk", "climate adaptation", "geohazards", "SDG 13"
Year: 2013-2024
```

---

## 📞 Contact Information

| Topic | Contact |
|-------|---------|
| Geodata & Services | geodatenmanagement@bgr.de |
| Publications | Via GeoShop or main website contact form |
| Printed Maps | ilhinfo@ilh-stuttgart.de (ILH Stuttgart) |
| General Inquiries | +49 (0)511 643-0 |

**Address:**
Bundesanstalt für Geowissenschaften und Rohstoffe (BGR)
Stilleweg 2
30655 Hannover, Germany

---

## ⚠️ Important Notes

1. **Do NOT scrape bgr.bund.de** - Use official APIs instead
2. **Respect rate limits** - Add delays between requests
3. **Follow INSPIRE compliance** - Use standard protocols
4. **Cite sources** - Always attribute BGR in publications
5. **Free access** - Most services are free but check individual terms

---

## 📖 Full Documentation

See **BGR_DATA_ACCESS_INVESTIGATION.md** for comprehensive investigation report.

---

**Last Updated:** 2025-11-19
