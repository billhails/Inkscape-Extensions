# Calligraphic Pen

Intended for use with the Inkscape Typography extension.
Non-destructive.

## Intended Operation

### Typography Glyph Layers

1. Find all top-level layers with a `GlyphLayer-` prefix.
2.  Rename them to `Original-GlyphLayer-*`.
3.  Create a new `GlyphLayer-*` layer.
4. Copy the contents from the `Original-` layer.
5. Within the new `GlyphLayer-` layer
	1. Inline all clones.
	2. unpack all groups.
	3. convert objects to paths.
	4. combine all paths to single path.
	5. Perform the calligraphic transform(s).

Exact behaviour depends on the possible pre-existence of an `Original-GlyphLayer-` layer:

|                                                  | `GlyphLayer-` exists                    | `GlyphLayer-` doesn't exist        |
|--------------------------------------------------|-----------------------------------------|------------------------------------|
| `Original-GlyphLayer-` exists                    | delete the `GlyphLayer-`, go to step 3. | go to step 3.                      |
| `Original-GlyphLayer-` doesn't exist             | go to step 1.                           | N/A                                |

Might be possible to tag the layers somehow, rather than relying on a naming convention (we still use the naming convention though).

### The Calligraphic Transform itself

We can keep the transform itself separate from the GlyphLayer manipulations,
there may be others we can apply later, but for now...

#### Parameters
* nib width (px, pt etc., optional with a checkbox)
* contrast (0-100% of stroke width)
* nib angle (0-360°)

#### Steps
* Select the path.
* Set the stroke width of the path to the specified amount.
	* optional, we should be allowed to keep pre-existing sizes, in case they vary within a character.
* Note the absolute position of the first point in the path.
* Rotate the points of the path by the negation of the specified angle.
* Scale the points of the path horizontally by the inverse of the specified scale.
* Scale the path itself horizontally by the specified scale.
* Rotate the path itself by the positive specified angle.
* Move the path to restore the absolute position of the first point.

Inkscape does some weird stuff when scaling paths and groups on one axis,
the stroke width of the other axis seems to be also affected. If we can work out
what it is doing we should be able to counter it. by adjusting stroke widths and
scaling appropriately.
