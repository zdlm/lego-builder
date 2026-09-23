You are looking at one page of a LEGO building-instruction booklet.

Find every numbered build step on this page. For each step return the printed step number and a
bounding box around the whole step panel (the assembly drawing plus its parts callout) in pixel
coordinates of this image. Ignore parts-list pages, cover art, ads and page numbers.

The image is {width}×{height} pixels.

Reply with JSON only:
{{"steps": [{{"step_number": 12, "bbox": {{"x": 0, "y": 0, "w": 0, "h": 0}}}}]}}
If the page has no build steps, reply {{"steps": []}}.
