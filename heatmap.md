# Heatmap Plotting

## Introduction

This tool takes in a 2D numpy array containing data from the radar and plots a Range Time Intensity graph, which depicts the existence of an object through the color of pixels, as well as its location, relative to the radar's position, over the period of time when the radar is scanning.

#### On the plot: 
- range (in meters) is the x-axis
- time (in seconds) is the y-axis
- intensity is represented by pixel color, where yellow is more intense and represents an object, and blue or purple is less intense and represents empty space

## Example
![Alt text](media/image.png)
The lime-colored line shows that there is an object and that the object's position is changing over time and in respect to the radar's position. The start time is at the bottom of the y-axis, and the end time at the top. The object is closer to the radar when the line is closer to the left side of the x-axis, and further from the radar when the line is farther from the left.

## Implementation

The function uses Matplotlib to plot the heatmap and display it to the user.


