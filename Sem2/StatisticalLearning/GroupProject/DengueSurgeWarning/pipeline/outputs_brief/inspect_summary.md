# Inspect summary

## mss/S24

139 monthly daily-record files (201106 -> 202212)

head of first file:
```
  Station  Year  Month  Day  Daily Rainfall Total (mm) Highest 30 Min Rainfall (mm) Highest 60 Min Rainfall (mm) Highest 120 Min Rainfall (mm)  Mean Temperature (°C)  Maximum Temperature (°C)  Minimum Temperature (°C)  Mean Wind Speed (km/h)  Max Wind Speed (km/h)
0  Changi  2011      6    1                        0.2                                                                                                        27.5                      31.9                      25.5                     5.8                   32.4
1  Changi  2011      6    2                        0.0                                                                                                        28.8                      33.0                      24.8                     8.6                   36.4
2  Changi  2011      6    3                        0.0                                                                                                        29.3                      32.0                      26.6                     7.1                   32.8
```

## MANIFEST.json

(unhandled type, 4668 bytes)

## moh_dengue_dhf_2014_2018.csv

shape: (530, 4)
columns / dtype / n_missing:
```
'year'                                   int64      0
'eweek'                                  int64      0
'type_dengue'                            object     0
'number'                                 float64    8
```
head:
```
   year  eweek type_dengue  number
0  2014      1      Dengue   436.0
1  2014      1         DHF     1.0
2  2014      2      Dengue   479.0
3  2014      2         DHF     0.0
4  2014      3      Dengue   401.0
```
tail:
```
     year  eweek type_dengue  number
527  2018     52         DHF     0.0
528  2018     53      Dengue     NaN
529  2018     53         DHF     NaN
```
distinct `type_dengue` (2):
```
DHF
Dengue
```

## moh_weekly_bulletin.csv

shape: (20070, 3)
columns / dtype / n_missing:
```
'epi_week'                               object     0
'disease'                                object     0
'no._of_cases'                           int64      0
```
head:
```
   epi_week                  disease  no._of_cases
0  2012-W01  Acute Viral hepatitis B             0
1  2012-W01  Acute Viral hepatitis C             0
2  2012-W01          Avian Influenza             0
3  2012-W01   Campylobacterenterosis             6
4  2012-W01        Chikungunya Fever             0
```
tail:
```
       epi_week        disease  no._of_cases
20067  2022-W52       Botulism             0
20068  2022-W52  Murine Typhus             0
20069  2022-W52      Monkeypox             0
```
distinct `disease` (46):
```
Acute Viral Hepatitis A
Acute Viral Hepatitis E
Acute Viral hepatitis B
Acute Viral hepatitis C
Avian Influenza
Botulism
Campylobacter enteritis
Campylobacterenterosis
Chikungunya
Chikungunya Fever
Cholera
Dengue Fever
Dengue Haemorrhagic Fever
Diphtheria
Ebola Virus Disease
Encephalitis
HFMD
Haemophilus influenzae type b
Hand, Foot Mouth Disease
Japanese Encephalitis
Legionellosis
Leptospirosis
Malaria
Measles
Melioidosis
Meningococcal Infection
Monkeypox
Mumps
Murine Typhus
Nipah
Nipah virus infection
Paratyphoid
Pertussis
Plague
Pneumococcal Disease (invasive)
Poliomyelitis
Rubella
SARS
Salmonellosis(non-enteric fevers)
Tetanus
Typhoid
Viral Hepatitis A
Viral Hepatitis E
Yellow Fever
Zika
Zika Virus Infection
```

## nea_dengue_clusters/20261106.geojson

features: 9
property keys: ['OBJECTID', 'LOCALITY', 'CASE_SIZE', 'NAME', 'HYPERLINK', 'HOMES', 'PUBLIC_PLACES', 'CONSTRUCTION_SITES', 'INC_CRC', 'FMEL_UPD_D', 'SHAPE.AREA', 'SHAPE.LEN']
total CASE_SIZE: 165, max: 101

## nea_rh_monthly.csv

shape: (537, 2)
columns / dtype / n_missing:
```
'month'                                  object     0
'mean_rh'                                float64    0
```
head:
```
     month  mean_rh
0  1982-01     81.2
1  1982-02     79.5
2  1982-03     82.3
3  1982-04     85.9
4  1982-05     83.2
```
tail:
```
       month  mean_rh
534  2026-07     80.2
535  2026-08     75.3
536  2026-09     77.3
```

## weather_open_meteo_daily.csv

shape: (4232, 6)
columns / dtype / n_missing:
```
'date'                                   object     0
'precipitation_sum'                      float64    0
'temperature_2m_mean'                    float64    0
'temperature_2m_max'                     float64    0
'temperature_2m_min'                     float64    0
'relative_humidity_2m_mean'              int64      0
```
head:
```
         date  precipitation_sum  temperature_2m_mean  temperature_2m_max  temperature_2m_min  relative_humidity_2m_mean
0  2011-06-01               10.0                 26.9                28.5                25.3                         87
1  2011-06-02               10.2                 26.9                29.1                24.8                         88
2  2011-06-03                3.1                 27.2                29.5                25.1                         86
3  2011-06-04               19.6                 26.6                28.6                24.9                         88
4  2011-06-05               15.3                 25.9                27.9                24.9                         91
```
tail:
```
            date  precipitation_sum  temperature_2m_mean  temperature_2m_max  temperature_2m_min  relative_humidity_2m_mean
4229  2022-12-29                3.6                 25.3                28.3                23.1                         85
4230  2022-12-30                1.5                 25.8                29.9                23.0                         81
4231  2022-12-31                0.7                 26.0                30.0                23.6                         79
```

