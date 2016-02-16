# NicheLife
A map visualization tool to find your ideal neighborhoods in Manhattan.

Developed at Cornell Data Science Hackathon (#DataHack16) by Priyanka Vijay, Jack Hayford, Mihir Prakash, Edward Flores, and Xinli Wang.

## Python package dependencies:
pandas, numpy, pyshp, bokeh

## To run locally:
bokeh serve --show main.py


Colors: 

The darker the red, the closer the area matches your preferences.
The darker the blue, the cheaper an area is (price per square foot).
Dark purple shows the most affordable areas that also match your preferences.


### Example 1. My ideal place has good access to subways, is reasonably safe, and is close to grocery stores and bars.
![Image of Example](https://github.com/priya-vijay/NicheLife/blob/master/examples/NicheLife_example.png)

### Example 2. I'm just curious about where people are the most satisfied, i.e., submitted the least complaints to http://www1.nyc.gov/311
![Image of Example](https://github.com/priya-vijay/NicheLife/blob/master/examples/Only_satisfaction.png)

### Example 3. What parts of Manhattan have the best access to grocery stores and restaurants?

(Data from yelp)

Can immediately visualize potential food deserts in a city.
![Image of Example](https://github.com/priya-vijay/NicheLife/blob/master/examples/Only_food.png)

### Example 4. What are the cheapest parts of the city that are also close to subways?

Can also zoom in and out and hover over blocks to learn more information.
![Image of Example](https://github.com/priya-vijay/NicheLife/blob/master/examples/Subway_and_Price_zoom.png)