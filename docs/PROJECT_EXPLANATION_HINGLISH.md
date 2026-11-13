# Warehouse Intelligence — Project Explanation (Hinglish)

## 1. Project ka idea

Warehouse Intelligence ek warehouse operations analytics application hai. Iska main kaam warehouse manager ko ek jagah par inventory, storage capacity, stock risk aur day-to-day operations samajhne mein help karna hai.

Normal inventory file mein aksar sirf SKU aur quantity hoti hai. Is project mein us data ko clean karke useful KPIs, charts, rack-level details aur operational alerts mein convert kiya jata hai. User built-in demo dataset se explore kar sakta hai ya apni inventory CSV upload kar sakta hai.

## 2. Technology stack

| Technology | Project mein use |
|---|---|
| Python | Main application logic aur calculations |
| Streamlit | Dashboard pages, filters, upload controls aur downloads |
| Pandas | CSV cleaning, mapping, grouping aur aggregation |
| NumPy | Numeric calculations aur demo data generation |
| Plotly | Interactive charts |
| HTML + CSS | Digital twin ka layout aur styling |
| JavaScript | 2D floor-plan interactions |
| Three.js | Browser mein 3D warehouse scene |
| Pytest | Data aur digital-twin tests |
| SQL | PostgreSQL ke liye reference schema |
| DAX / Power Query notes | Power BI integration ke starter assets |

## 3. Application ka data flow

1. App start hone par user Demo Dataset ya Upload CSV choose karta hai.
2. Demo mode mein Python fixed seed ke saath warehouses, zones, racks, products, inventory, movements, inbound aur outbound records banata hai.
3. CSV mode mein Pandas file read karta hai. Column mapper user ke column names ko standard inventory fields se match karta hai.
4. Mapped data ko normalized Pandas DataFrames mein convert kiya jata hai.
5. Global filters select warehouse, region, category, SKU, zone aur date scope ko control karte hain.
6. Filtered data se KPIs, charts, rack summaries aur exception records calculate hote hain.
7. Streamlit pages in results ko tables, metrics aur Plotly charts mein dikhate hain.
8. Digital Twin page ko Python rack aur inventory records JSON ke form mein deta hai. HTML/CSS/JavaScript layer 2D aur 3D views render karti hai.

## 4. Main pages — kya kaam karti hain?

### 1. Command Center

Ye landing page hai. Isme total inventory units, inventory value, active SKUs, capacity utilization, low-stock SKUs aur non-moving inventory value jaise KPIs milte hain. Saath mein warehouse-wise value, category mix, inbound/outbound trends aur ageing charts dikhte hain.

### 2. 3D Digital Twin

Is page par warehouse ka 3D model dikhta hai. User mouse se orbit, zoom aur pan kar sakta hai. Rack select karne par us rack ke capacity, occupied units, available units, utilization, inventory value aur SKU details update hote hain. Forklift movement ko scenario ke through play/pause kiya ja sakta hai.

### 3. 2D Floor Plan

Ye warehouse ka top-view layout hai. Racks ko occupancy/status ke hisaab se colour kiya jata hai. Rack par click karne se detail panel aur rack inventory update hoti hai. Search se SKU ya rack locate kiya ja sakta hai.

### 4. Inventory Intelligence

Isme stock health, stock ageing, ABC classification, category-wise inventory value aur reorder-level comparison aata hai. Inventory table ko filter aur export bhi kar sakte hain.

### 5. Rack & Bin Explorer

Warehouse → zone → rack level par drill-down milta hai. Selected rack ki capacity, occupied/available units, utilization, stock value aur SKU-level contents dekhe ja sakte hain. Current model rack-level tak focused hai; shelf/bin detail ke liye source data mein woh columns hone chahiye.

### 6. Warehouse Map

Warehouse aur rack occupancy ko 2D layout ke through compare karne ke liye hai. Isse high-utilization aur low-utilization locations identify kar sakte hain.

### 7. Inbound Operations

Demo dataset mein receiving records, supplier, expected/received units, receiving completion, delay aur inspection status analyse kiya jata hai. Inventory-only CSV upload mein inbound file na ho toh relevant analysis available nahi hota.

### 8. Outbound Operations

Orders, picked units, dispatched units, fulfilment rate aur picking duration analyse hota hai. OTIF tabhi calculate ho sakta hai jab promised aur actual delivery dates available hon; current inventory-only CSV mein ye fields nahi hoti.

### 9. Workforce & Equipment

Receiving-to-storage, replenishment aur picking-to-dispatch jaise scenarios choose karke forklift/AGV task state aur event timeline explore kar sakte hain. Ye in-app scenario playback hai; isse real vehicle ya employee system operate nahi hota.

### 10. Space Optimization

Rack/warehouse capacity utilization, available space, high-occupancy racks aur underused locations ko identify karne ke liye hai. Relocation ya capacity decisions ko actual business approval ke saath hi lena chahiye.

### 11. Risk & Exceptions

Low stock, out-of-stock, slow/non-moving stock, high rack utilization aur operational delays jaise conditions ke basis par alerts bante hain. User severity aur warehouse ke basis par exceptions dekh sakta hai.

### 12. Insights & Recommendations

Current filtered data se business observations generate hote hain—jaise highest inventory-value warehouse, stock replenishment candidates aur space pressure. Ye built-in metric/rule-based insights hain; external LLM API connected nahi hai.

### 13. Automation Center

User manually low-stock report, ageing report, overcapacity report ya daily summary generate kar sakta hai. Optional webhook field se user summary ko external workflow endpoint par bhej sakta hai.

### 14. Data Explorer

Source rows, columns, missing values, duplicate rows, data types, sample records aur quality warnings inspect kar sakte hain. Filtered inventory, SKU summary, warehouse summary aur alert register export bhi kar sakte hain.

### 15. Settings

Current data source, record count, warehouse count, available integration assets aur KPI formulas ka summary hai.

## 5. Important KPI formulas

- **Inventory Units** = `SUM(quantity_on_hand)`
- **Inventory Value** = `SUM(quantity_on_hand × unit_cost)`; ya uploaded data mein source-provided inventory value.
- **Capacity Utilization** = `occupied_units / capacity_units × 100`
- **Low Stock** = distinct SKUs jinki quantity reorder level ke equal ya neeche hai.
- **Out of Stock** = quantity zero ya negative.
- **Ageing** = aaj ki date minus last movement date.
- **Non-moving Inventory Value** = 90 din se zyada movement na hone wale stock ki value.
- **Receiving Completion** = `units_received / units_expected × 100`
- **Fulfilment Rate** = `units_dispatched / units_ordered × 100`

Kisi metric ke liye required column nahi milta toh app usko unavailable rakhta hai; missing value ko imaginary figure se replace nahi karta.

## 6. 2D aur 3D ka connection

`digital_twin.py` Python DataFrames se rack-wise records ready karta hai aur `static/` folder ke assets ko ek HTML view mein combine karta hai.

- `static/digital_twin.html` — view ka structure aur controls.
- `static/digital_twin.css` — styling, layout aur responsive behaviour.
- `static/floorplan.js` — SVG floor plan, rack search, rack click aur details.
- `static/three_scene.js` — Three.js model, camera controls, rack highlighting aur forklift path.

Dono views same embedded component ke rack selection ko use karte hain. 2D mein rack select karne par 3D highlight aur detail panel update hota hai; 3D mein rack click karne par 2D selection update hota hai.

## 7. Project folders aur files

```text
warehouse-intelligence/
├── app.py                  # Streamlit pages, data model, filters, KPIs aur alerts
├── digital_twin.py         # Python-to-HTML data bridge
├── requirements.txt        # Runtime Python packages
├── requirements-dev.txt    # Testing packages
├── run_windows.bat         # Windows setup aur launch script
├── data/
│   └── sample_inventory.csv
├── static/
│   ├── digital_twin.html
│   ├── digital_twin.css
│   ├── floorplan.js
│   └── three_scene.js
├── database/
│   └── schema.sql          # PostgreSQL reference schema
├── docs/                   # Guides, audit, formulas aur project notes
├── powerbi/                # DAX aur Power BI model/Power Query notes
└── tests/                  # Automated tests
```

## 8. Current build ka actual scope

- Local Streamlit app aur CSV inventory upload working foundation hain.
- Built-in demo dataset mein inbound, outbound aur movement records bhi hote hain.
- Single inventory CSV se inventory analysis hota hai; us file se missing receipt/order history create nahi ki jati.
- 2D floor plan browser SVG se banta hai. 3D scene Three.js modules ko CDN se load karta hai, isliye 3D view ke liye internet required hai.
- PostgreSQL schema reference hai; current app database connection open nahi karta.
- Power BI folder mein starter DAX/model/Power Query notes hain; PBIX file nahi hai.
- Insights local business rules se nikalte hain; Claude/OpenAI API connected nahi hai.
- Automation reports local generate hoti hain; external webhook sirf user ke manual action par call hota hai.

## 9. Project run aur test karna

Project folder mein PowerShell terminal open karo:

```powershell
py -m streamlit run app.py
```

Tests run karne ke liye:

```powershell
py -m pip install -r requirements-dev.txt
py -m pytest -q
```

Browser mein `http://localhost:8501` open karo. App ko stop karne ke liye terminal mein `Ctrl + C` press karo.
