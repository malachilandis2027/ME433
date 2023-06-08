# HW15

Here is a video demo:
https://www.youtube.com/watch?v=gWm47uxxWgo

My tactic for finding the line was to use an edge detection kernel to find areas of high change in the colors on select rows. I did this for each of the colors. Then I took the absolute values of all of these matrices and added them together. Then I did a weighted average, where 0 would be in the middle, 1 would be at the right, and -1 would be at the left. 