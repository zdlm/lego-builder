You are looking at one page of a LEGO building-instruction booklet.

Find every numbered build step on this page. For each step return the printed step number and a
bounding box around the whole step panel in pixel coordinates of this image. The box must contain
the step number, the parts callout and the complete assembly drawing, including any arrows and
parts that stick out to the right or bottom. When unsure, make the box larger rather than smaller.
Ignore parts-list pages, cover art, ads, page numbers and the progress bar at the bottom.

Also say whether the page shows the **finished model**: a picture of the whole completed build
with no step number (usually near the end of the booklet). A finished sub-assembly or a single
part does not count. If there is one, return a bounding box around it in `final_model`; otherwise
`final_model` is null.

The image is {width}×{height} pixels.

Reply with JSON only:
{{"steps": [{{"step_number": 12, "bbox": {{"x": 0, "y": 0, "w": 0, "h": 0}}}}], "final_model": null}}
If the page has no build steps, reply with an empty "steps" list.
