#!/usr/bin/env python
"""default color dictionaries for aermodpy

developed for python 3.x
"""


color_dicts = {
 "post" :    ((   0, "#FFFFFF", "    0")
             ,( 250, "#FFFF99", "")
             ,( 500,  "yellow", "")
             ,(1000, "#FFCC00", "1,000")
             ,(1500,  "orange", "")
             ,(2000,     "red", "2,000")
             ,(4000, "magenta", "4,000")
             ,(8000, "#993399", "8,000")
             )
,"grf"  :    ((  0, "#FFFFFF", "    0")
             ,( 25, "#FFFF99", "")
             ,( 50,  "yellow", "")
             ,(100, "#FFCC00", "100")
             ,(150,  "orange", "")
             ,(200,     "red", "200")
             ,(400, "magenta", "400")
             ,(800, "#993399", "800")
             )
,"24h-pm":   ((  0, "#FFFFFF", " 0")
             ,(  4, "#FFFF99", " 4")
             ,( 10,  "yellow", "10")
             ,( 20, "#FFCC00", "20")
             ,( 35,  "orange", "35")
             ,( 40,     "red", "40")
             ,( 50, "magenta", "50")
             ,( 60, "#993399", "60")
             )
,"24h-pm-fine":   (
              (  0, "#FFFFFF", " 0")
             ,(1.2, "#fbfdfe", " 1.2 (SIL)")
             ,(  4, "#f2f9fc", " 4 (SMC)")
             ,(  9, "#eaf5fb", " 9 (increment)")
             ,( 10, "#fefebe", "")
             ,( 15, "#FDFD96", "15")
             ,( 20, "#FFFF00", "20")
             ,( 25, "#FFF700", "25")
             ,( 30, "#FFEF00", "30")
             ,( 35, "#FFB347", "35 (NAAQS)")
             ,( 40, "#FFA812", "40")
             ,( 45, "#FF7F00", "45")
             ,( 50, "#FF6700", "50")
             ,( 55, "#ff3838", "55")
             ,( 60, "red", "60")
             )
,"1h-pm-fine":   (
              (  0, "#FFFFFF", "  0")
             ,(1.2, "#dbfadf", "")
             ,(  4, "#c5f7cb", "")
             ,(  9, "#8aef98", "")
             ,( 12, "#fefebe", " 12 (Annual NAAQS)")
             ,( 15, "#FDFD96", " ")
             ,( 20, "#FFFF00", " 20")
             ,( 25, "#FFF700", " ")
             ,( 30, "#FFEF00", "")
             ,( 35, "#FFB347", " 35 (24H NAAQS)")
             ,( 40, "#FFA812", "")
             ,( 45, "#FF7F00", "")
             ,( 50, "#FF6700", " ")
             ,( 55, "#ff3838", " 55")
             ,( 70, "#fa0000", " ")
             ,( 80, "#d60000", " ")
             ,( 90, "#c20000", " ")
             ,(100, "#b30000", "100")
             ,(110, "#940000", "110")
             )
,"1h-pm-fine-high":   (
              (  0, "#FFFFFF", "  0")
             ,(1.2, "#dbfadf", "")
             ,(  4, "#c5f7cb", "")
             ,(  9, "#8aef98", "")
             ,( 12, "#fefebe", " 12 (Annual NAAQS)")
             ,( 15, "#FDFD96", " ")
             ,( 20, "#FFFF00", "")
             ,( 25, "#FFF700", " ")
             ,( 30, "#FFEF00", "")
             ,( 35, "#FFB347", " 35 (24H NAAQS)")
             ,( 40, "#FFA812", "")
             ,( 45, "#FF7F00", "")
             ,( 50, "#FF6700", " ")
             ,( 55, "#ff3838", " 55")
             ,( 70, "#fa0000", " ")
             ,( 80, "#d60000", " ")
             ,( 90, "#c20000", " ")
             ,(100, "#b30000", "100")
             ,(110, "#db00c2", "")
             ,(460, "#db00c2", "500")
             )
,"annual-pm-fine":   (
              (  0, "#FFFFFF", " ")
             ,(0.3, "#dbfadf", " 0.3 (SIL)")
             ,(  2, "#c5f7cb", " 2")
             ,(  4, "#8aef98", " 4 (increment)")
             ,(  6, "#fefebe", " 6")
             ,(  8, "#FDFD96", " 8")
             ,( 10, "#FFF700", "10")
             ,( 12, "#FFA812", "12 (NAAQS)")
             ,( 14, "#FF8C00", "14")
             ,( 16, "#FF6700", "16")
             ,( 18, "#ff3838", "18")
             ,( 20, "#CE1620", "20")
             ,( 22, "#B31B1B", "22")
             )
,"1h-no2":   (
              (  0, "#FFFFFF", "  0")
             ,( 15, "#dbfadf", "")
             ,( 30, "#c5f7cb", " 30")
             ,( 45, "#8aef98", "")
             ,( 53, "#fefebe", " 53 AQI=Moderate")
             ,( 70, "#FDFD96", "")
             ,( 80, "#FFF700", " 80")
             ,( 90, "#FFEF00", "")
             ,(100, "#FFB347", "100 (NAAQS)")
             ,(115, "#FFA812", "115")
             ,(130, "#FF7F00", "130")
             ,(150, "#FF6700", "150")
             ,(200, "#CC5500", "200")
             ,(360, "red", "360 AQI=Unhealthy")
             )
,"8h-co-high":   (
              ( 0.0, "#FFFFFF", " 0.0")
             ,( 0.4, "#dbfadf", " 0.4 8-h SIL")
             ,( 2.0, "#c5f7cb", " 2.0 1-h SIL")
             ,( 3.0, "#8aef98", "")
             ,( 4.4, "#fefebe", " 4.4 AQI=Moderate 8-h")
             ,( 5.0, "#FDFD96", "")
             ,( 6.0, "#FFF700", "")
             ,( 7.0, "#FFEF00", "")
             ,( 9.5, "#FFB347", " 9.5 AQI=USG 8-h")
             ,(10.0, "#FFA812", "")
             ,(11.0, "#FF7F00", "")
             ,(12.0, "#CC5500", "")
             ,(12.5, "#FF0000", "12.5 AQI=Unhealthy")
             ,(15.5, "#db00c2", "15.5 AQI=Very Unhealthy")
             ,(30.5, "#AA0020", "30.5 AQI=Hazardous")
             ,(50.5, "#000000", "")
             )
,"1h-co-high":   (
              ( 0.0, "#FFFFFF", " 0.0")
             ,( 0.4, "#dbfadf", " 0.4")
             ,( 2.0, "#c5f7cb", " 2.0 SIL")
             ,( 3.0, "#8aef98", "")
             ,( 4.4, "#fefebe", " 4.4 AQI=Moderate")
             ,( 5.0, "#FDFD96", "")
             ,( 6.0, "#FFF700", "")
             ,( 7.0, "#FFEF00", "")
             ,( 9.5, "#FFB347", " 9.5 AQI=USG")
             ,(10.0, "#FFA812", "")
             ,(11.0, "#FF7F00", "")
             ,(12.0, "#CC5500", "")
             ,(12.5, "#FF0000", "12.5 AQI=Unhealthy")
             ,(15.5, "#db00c2", "15.5 AQI=Very Unhealthy")
             ,(30.5, "#AA0020", "30.5 AQI=Hazardous")
             ,(50.5, "#000000", "")
             )
,"8h-co":   (
              ( 0.0, "#FFFFFF", " 0.0")
             ,( 0.4, "#dbfadf", " 0.4 8-h SIL")
             ,( 2.0, "#c5f7cb", " 2.0 1-h SIL")
             ,( 3.0, "#8aef98", "")
             ,( 4.4, "#fefebe", " 4.4 AQI=Moderate")
             ,( 5.0, "#FDFD96", "")
             ,( 6.0, "#FFF700", "")
             ,( 7.0, "#FFEF00", "")
             ,( 9.5, "#FFB347", " 9.5 AQI=USG")
             )
,"1h-co":   (
              ( 0.0, "#FFFFFF", " 0.0")
             ,( 0.4, "#dbfadf", " 0.4")
             ,( 2.0, "#c5f7cb", " 2.0 SIL")
             ,( 3.0, "#8aef98", "")
             ,( 4.4, "#fefebe", " 4.4 AQI=Moderate")
             ,( 5.0, "#FDFD96", "")
             ,( 6.0, "#FFF700", "")
             ,( 7.0, "#FFEF00", "")
             ,( 9.5, "#FFB347", " 9.5 AQI=USG")
             )
              }
