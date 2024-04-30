# region: General Timing 
PIERCE_TIME = 5000
DEPIERCE_TIME = PIERCE_TIME
FLASK2FLASK = 5000
#endregion

# region : System Sterility Delays between substeps 
SSD1 = 1
SSD2 = SSD1 + 23000             #move to waste
SSD3 = SSD2 + PIERCE_TIME        #pierce
SSD4 = SSD3 + DEPIERCE_TIME     #depierce
SSD5 = SSD4 + FLASK2FLASK        #move to flask 2
SSD6 = SSD5 + PIERCE_TIME       #pierce
SSD7 = SSD6 + DEPIERCE_TIME      #depierce
SSD8 = SSD7 + FLASK2FLASK       #move to flask 3
SSD9 = SSD8 + PIERCE_TIME        #pierce
SSD10 = SSD9 + DEPIERCE_TIME    #depierce
SSD11 = SSD10 + FLASK2FLASK      #moveto flask 4
SSD12 = SSD11 + PIERCE_TIME     #pierce
SSD13 = SSD12 + DEPIERCE_TIME    #depierce
SSD14 = SSD13 + FLASK2FLASK     #moveto flask 5
SSD15 = SSD14 + PIERCE_TIME     #pierce
SSD16 = SSD15 + DEPIERCE_TIME    #depierce
SSD17 = SSD16 + FLASK2FLASK     #moveto flask 6
SSD18 = SSD17 + PIERCE_TIME     #pierce
SSD19 = SSD18 + DEPIERCE_TIME    #depierce
#endregion
