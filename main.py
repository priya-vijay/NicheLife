#! /usr/bin/env python
"""
adding legend
"""
import imp
import numpy as np
from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource, HBox, VBoxForm, ImageURL
from bokeh.models.widgets import Slider, TextInput, Select
from bokeh.io import curdoc
import pandas as pd
from bokeh.models import HoverTool, PanTool, BoxZoomTool, WheelZoomTool, ResetTool, PreviewSaveTool
import shapefile


# plot basemap
baseshapefile = "data/shapefile/FinalManhattan_CT_New_Crime_Dist_Complaints_NewProjection"  # should be 288


sf = shapefile.Reader(baseshapefile)
shapes = sf.shapes()
records = sf.records()
recdf = pd.DataFrame(records)
recdf.columns = [i[0] for i in sf.fields[1:]]
recdf.index = recdf["BoroCT2010"]

extrainfo = pd.DataFrame.from_csv("data/nyct2010_neighborhoods_mn.csv")
extrainfo.index = extrainfo["BoroCT2010"]

# pricevals = np.random.randint(100, 3000, len(qivals))
pricevals_dummy = [0]*len(shapes)
pricevals_real = pd.DataFrame.from_csv("data/Prices_fromzipcode_mappedCT.csv")["Price"]
imageurl_noprice = "data/legend_noprice.png"
imageurl_wprice = "data/legend_wprice.png"

pricevals = pricevals_real
imageurl = imageurl_wprice

# yelp data
yelp = pd.DataFrame.from_csv("data/yelpdata_reformat.csv")
yelp["BoroCT2010"] = yelp.index
yelp.index = map(str, yelp["BoroCT2010"])

# print "Number of shapes:", len(shapes)

ct_x = []
ct_y = []
for shape in shapes:
    lats = []
    lons = []
    for point in shape.points:
        lats.append(point[0])
        lons.append(point[1])
    ct_x.append(lats)
    ct_y.append(lons)

# colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]
# #bivariate color map 00 = bottom left, 20 = bottom right, 02 = top left, 22 = top right,
colorsdict = {"00": "#E8E8E8", "10": "#E4ACAC", "20": "#C85A5A",
              "01": "#B0D5DF", "11": "#AD9EA5", "21": "#985356",
              "02": "#64acbe", "12": "627F8C", "22": "#574249"}


def mapcolors(qivallist, pricevallist):
    """
    00 = low qivallist, high price (bottom left)
    20 = high qivallist, high price (bottom right)
    02 = low qivallist, low price (top left)
    22 = high qivallist, low price (top right) !!we have a winner!!
    """
    # split qivallist into 3 categories
    qi_split1 = np.percentile(qivallist, 33)
    qi_split2 = np.percentile(qivallist, 66)
    # print qi_split1, qi_split2
    # print type(qi_split1)
    qi_colorcodes = []
    if qi_split1 == qi_split2:
        qi_colorcodes = ["0"]*len(qivallist)
    else:
        for qi in qivallist:
            # qi = qiv.values[0]
            if qi < qi_split1:
                qi_colorcodes.append("0")
            elif qi < qi_split2:
                qi_colorcodes.append("1")
            else:
                qi_colorcodes.append("2")
    # split pricevallist into 3 categories
    price_split1 = np.percentile(pricevallist, 33)
    price_split2 = np.percentile(pricevallist, 66)
    price_colorcodes = []
    if price_split1 == price_split2:
        price_colorcodes = ["0"]*len(pricevallist)
    else:
        for price in pricevallist:
            if price < price_split1:
                price_colorcodes.append("2")
            elif price < price_split2:
                price_colorcodes.append("1")
            else:
                price_colorcodes.append("0")
    colorlist = [colorsdict[qi_colorcodes[x] + price_colorcodes[x]] for x in range(len(qi_colorcodes))]
    return colorlist


# def getscore(userinputs):  # user inputs: list of feature importance values
#     keepfeatures = recdf[["Distance", "Crime_Ct", "Complaints"]].applymap(float) + 1
#     logfeatures = keepfeatures.applymap(np.log)
#     zscores = logfeatures.apply(lambda x: (x - np.mean(x)) / np.std(x))
#     compscore = zscores.apply(lambda x: -userinputs[0] * x["Distance"] - userinputs[1] * x["Crime_Ct"] - userinputs[2] * x["Complaints"], axis=1)
#     return compscore

# get score with yelp
def getscore(userinputs):  # user inputs: list of feature importance values
    merged = pd.concat([yelp, recdf], axis=1)
    keepfeatures = merged[["Distance", "Crime_Ct", "Complaints", "restaurants", "food", "nightlife"]].applymap(float) + 1
    logfeatures = keepfeatures.applymap(np.log)
    zscores = logfeatures.apply(lambda x: (x - np.mean(x)) / np.std(x))
    # compscore = zscores.apply(lambda x: -userinputs[0] * x["Distance"] - userinputs[1] * x["Crime_Ct"] - userinputs[2] * x["Complaints"] + userinputs[2] * x["Complaints"], axis=1)
    multiplier = [-1, -1, -1, 1, 1, 1]
    newuservector = [userinputs[i]*multiplier[i] for i in range(len(userinputs))]
    compscore = zscores.dot(newuservector)
    compzscore = (compscore - np.mean(compscore))/np.std(compscore)
    return compscore


qivals = getscore([0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
# print qivals
# outfile = open("test_qivals.txt", "w")
# for item in qivals:
#     outfile.write(item+"\n")
# outfile.close()
# # print qivals
# print len(qivals)
# print type(qivals)


ct_colors = mapcolors(qivals, pricevals)

# output_file("nyc_basemap.html", title="NYC census tracts")
source = ColumnDataSource(data=dict(QI_colmap=ct_colors, ct_x=ct_x, ct_y=ct_y, NicheScore=qivals, Price=pricevals, Neighborhood=extrainfo["NTAName"])) #.loc[recdf.index]
# print source
hover = HoverTool(
        tooltips=[
            ("Niche Score", "@NicheScore"),
            ("Price", "@Price"),
        ]
    ) #("Area", "@Neighborhood"),

tools = [PanTool(), BoxZoomTool(), WheelZoomTool(), ResetTool(), hover, PreviewSaveTool()]

p = Figure(title="NicheLife Map", plot_width=800, plot_height=700, tools=tools)
           # tools="pan,wheel_zoom,reset,box_zoom,save")  # toolbar_location="top", #box_select,
p.grid.grid_line_alpha = 0

p.patches('ct_x', 'ct_y', source=source, fill_color='QI_colmap', fill_alpha=0.7, line_color="white", line_width=0.5)

# image1 = ImageURL(url=source.data["image"], x=-74.04, y=40.85)
# p.add_glyph(source, image1)
p.image_url(url=imageurl, x="-74.04", y="40.85")


# Set up widgets
text = TextInput(title="Map Name", value="NicheLife Map")
feature1 = Slider(title="Subway Accessibility", value=0.5, start=0, end=1, step=.1)
feature2 = Slider(title="Safety", value=0.5, start=0, end=1, step=.1)
feature3 = Slider(title="Public Satisfaction", value=0.5, start=0, end=1, step=.1)
feature4 = Slider(title="Restaurants", value=0.5, start=0, end=1, step=.1)
feature5 = Slider(title="Grocery Stores", value=0.5, start=0, end=1, step=.1)
feature6 = Slider(title="Nightlife", value=0.5, start=0, end=1, step=.1)
price = Select(title="Show Affordability", options=["Yes", "No"])


# Set up callbacks
def update_title(attrname, old, new):
    p.title = text.value


text.on_change('value', update_title)


def update_data(attrname, old, new):
    # Get the current slider values
    f1user = feature1.value
    f2user = feature2.value
    f3user = feature3.value
    f4user = feature4.value
    f5user = feature5.value
    f6user = feature6.value
    showprice = price.value

    # Calculate score based on user input
    qivals = getscore([f1user, f2user, f3user, f4user, f5user, f6user])

    # Calcualte color palette based on whether showing price or not
    if showprice == "Yes":
        pricevals = pricevals_real
        imageurl = imageurl_wprice
    else:
        pricevals = pricevals_dummy
        imageurl = imageurl_noprice
    ct_colors = mapcolors(qivals, pricevals)

    # p.title = "hi"

    source.data = dict(QI_colmap=ct_colors, ct_x=ct_x, ct_y=ct_y, NicheScore=qivals, Price=pricevals, Neighborhood=extrainfo["NTAName"])
    # source.data = pd.DataFrame([ct_colors, ct_x, ct_y], columns=["QI_colmap", "ct_x", "ct_y"])

for w in [feature1, feature2, feature3, feature4, feature5, feature6, price]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = VBoxForm(children=[text, feature1, feature2, feature3, feature4, feature5, feature6, price])
# inputs = VBoxForm(children=[feature1, feature2, feature3])
# inputs = VBoxForm(children=[text])
curdoc().add_root(HBox(children=[p, inputs]))  # , width=800


# show(p)
