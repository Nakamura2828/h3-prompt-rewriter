# Image inventory — `images/`

Built session 6 (2026-08-11) by reading every file directly, not by running a describer over
them. This is ground truth for casting test cases and for judging describer *content*, which
`validate.py` cannot see.

**98 active files** as of session 7, built in three passes, each with its own table and probe-pair
list further down:

| pass | files | section |
|---|---|---|
| session 6 | 37 | this one, immediately below |
| session 7, first batch | 37 supplied + 5 crops | "Session 7 additions" |
| session 7, second batch | 14 supplied + 5 crops | "Session 7, second batch" — **every remaining gap closed** |

`p1_first.old.png` / `p1_last.old.png` are superseded duplicates and are excluded throughout.

**Later sections correct earlier ones.** Two claims in the first-batch section were reversed by
what arrived in the second, and one row in the session-6 table was reversed by the first batch.
Where they conflict, the later section wins; each says so at the point of conflict.

The session-6 medium tally below said "16" live-action photographic against a list of 17 names;
17 is correct and is what makes the total 37. Corrected in place.

Corrections and additions from the user after the first pass, all folded in below:

- **`cloud`, `forest_autumn`, `fuji`, `mountain_rain`, `vector_city` added** — five exteriors,
  four of them nature-dominant, closing the "no pure-nature exterior" gap the first pass raised
  and adding fog and rain to a corpus that previously had only snow. Three also bring new
  rendering media (digital painting ×2, flat vector ×1).

- **`p6_first`/`p6_last` show a window, not a doorway** — and it is the *same window* as
  `window.png`, which had been double-counted as an unrelated location. That makes
  `window` + `p6_first` + `p6_last` a **three-image same-place set**, the largest we have.
- **`city_day` / `city_night` added** — the same-place/different-time-of-day pair the first
  pass listed as the one blocking gap for the atmosphere quarantine.

The **medium** column uses the closed vocabulary proposed for `describer_style`'s `[[MEDIUM]]`
field — the same axis as the frame describer's `[[STYLE]]`.

## Table

| image | medium | int/ext | setting | prominent objects | notable garments | people |
|---|---|---|---|---|---|---|
| `bookshop` | live-action photographic | **ext (int visible)** | Paris-style bookshop frontage from the pavement; shop interior through the open door | tiered book displays, ceiling strip lights (on), downpipe, vent grille, doormat | black sweater, dark jeans | 1 adult man |
| `captain` | live-action photographic | ext | deck of a sailing yacht at sea, clear sky | **ship's wheel** (large, varnished), boom, furled sail, rigging, blocks, guardrail | **captain's uniform**: white peaked cap w/ gold emblem, navy double-breasted jacket, 4 cuff stripes, ribbon bar | 1 adult man |
| `castle` | live-action photographic | ext | castle grounds; round crenellated tower, curtain wall, cloudy sky | pennant flag, arrow-slit, partial wooden shield edge | **plate armour**: pauldrons, engraved cuirass, gorget, mail sleeves, gauntlets, brown belt | 1 young-adult woman |
| `classroom1` | live-action photographic | int | bright modern classroom; cream walls, curtained window | light-wood desks, storage cabinet, world-map bulletin board, open books, orange pencils | blue/white striped shirts, red neckties, navy pleated skirts | 5 children |
| `classroom2` | live-action photographic | int | older classroom; orange-yellow walls, tall windows | wooden desks, potted plant on sill, blue hardback, blue pencils, framed poster | navy waistcoats, white shirts, striped ties; houndstooth shirt-dress | 6+ children |
| `cloud` | **digital painting** (painterly, deckle border) | ext | grassy plain under towering cumulus; dirt track, distant blue hills, contrail | wooden fence, small white utility building | — | none |
| `forest_autumn` | live-action photographic | ext | **beech forest in fog**, autumn; grey trunks, rust foliage, deep leaf litter, exposed roots, dirt path | (none) | — | **1 tiny distant figure** on the path |
| `fuji` | live-action photographic | ext | **thatched village by a pond, snow-capped volcano behind**; topiary, azaleas, clipped hedge, conifers, deep blue sky | thatched roofs, **water wheel**, stone lantern | — | none |
| `mountain_rain` | **digital painting** (matte-painting style) | ext | **alpine panorama in driving rain**; snow-capped range, mossy rock ledge, conifers, alpine flowers, snow patches, dead trunk | (none) | — | none |
| `vector_city` | **flat vector illustration** | ext | stylised skyline of angular towers in coral and grey, reflected in water; teal sky, stylised clouds, sun flare | foreground rocks | — | none |
| `city_day` | live-action photographic | ext | **downtown skyline from above**, daylight, blue sky w/ cirrus; glass and masonry towers, a gold curtain-wall tower, a stepped-crown tower, low-rise grid, distant treeline | rooftop antennas, **rooftop brand signage**, construction scaffolding | — | **none** |
| `city_night` | live-action photographic | ext | **same skyline, same camera position**, blue hour; orange horizon glow, lit windows throughout | same towers; **illuminated signs and a lit crown** now readable, low-rise detail lost | — | **none** |
| `jacket` | live-action photographic | ext | **snowy park** — bare trees, falling snow, snow-covered ground | (none) | **grey quilted puffer jacket** w/ hood | 1 young-adult woman |
| `jacket2` | live-action photographic | ext | **same snowy park**, seated on a bench; near-featureless snow field behind | **wrought-iron bench** (scrollwork), brown leather handbag | same grey puffer jacket, **fur-trimmed mittens** | 1 young-adult woman (same person) |
| `kasia` | 2D illustration (flat cel) | **none** — plain pale-grey backdrop | no environment at all | **orange shoulder bag** w/ blue strap + 3 pin badges | black tank, denim cuffed shorts, fingerless gloves, striped knee socks, blue sneakers, orange headband | 1 girl |
| `kiki` | 2D anime | **none** — plain white ground | no environment; floating props | **6–7 breads/pastries** (loaf, baguette, rolls, filled bun) | navy long-sleeve top, red bow headband | 1 girl + 1 black cat |
| `miya` | 2D anime | ext | winter hillside road/lookout above a valley town; guardrail, bare trees, snow | guardrail, small trash bin, power pylons | cream double-breasted coat, black fur collar, grey pleated skirt, brown backpack, **cream headphones** | 1 teenage girl |
| `miyu` | **pixel art** | none — black void | no environment; ground litter only | **wheelie bin** (recycling pictograms, lid open), scattered leaves | not readable (occluded) | 1 girl (heavily occluded) + 1 shadow figure |
| `newspaper` | live-action photographic | int | bright minimal living room; cream walls, built-in white shelving | **folded broadsheet newspaper**, books, oatmeal armchair | navy shirt, dark trousers, black belt | 1 adult man |
| `p1_first` | live-action film (modern) | int | shabby apartment room, ochre distempered walls, very dim | **transistor radio**, handgun, corduroy couch, leather armchair, pole-mounted shelf + lamp, folding side table, tin ashtray | black top, shoulder-holster straps, round sunglasses | 1 adult man |
| `p1_last` | live-action film (modern) | int | **same room, far brighter and closer** | same radio, shelf, framed item | same | 1 adult man |
| `p2_first` | live-action film (modern) | int | shabby kitchen; yellow cabinets, maroon splashback, lace-curtained window | disassembled handguns, cloth, 2 solvent bottles, green dish rack, sink+tap, paper-towel roll, **box w/ brand text** | sage sleeveless waistcoat over white vest | 1 girl |
| `p2_last` | live-action film (modern) | int | **same kitchen, near-identical light** | same | same | 1 girl |
| `p3_first` | live-action film (modern) | int | dining room; ivory raised-panel wainscot, dark polished table | **cereal box w/ large brand text**, milk carton, pink milkshake glass, cut-glass fruit bowl, floral bowl + spoon, woven placemat | grey/white striped pyjama shirt | 1 girl |
| `p3_last` | live-action film (modern) | int | **same room, near-identical** | same | same | 1 girl |
| `p4_first` | live-action film (modern) | ext | city street, **background almost entirely defocused**, blown white sky | **leather case w/ brass latches**, second black case, potted houseplant, paper bag, blurred bus | olive bomber jacket, green/striped dress, choker; long dark overcoat | 1 girl + 1 adult man |
| `p4_last` | live-action film (modern) | ext | same street, same bokeh | same | same | 1 girl + 1 adult man |
| `p5_first` | **live-action film (vintage Technicolor)** | ext | studio-backlot city street **at night**; granite building corner, masonry apartments, lit windows | **1950s cars** (black sedan, red/white taxi), terracotta potted shrub, wooden double doors, stone kerb | black suit, white shirt, black tie, pocket square, **fedora**, **roller skates** | 1 adult man |
| `p5_last` | live-action film (vintage Technicolor) | ext | same corner, tighter, **heavy dissolve/superimposition** of a second figure | same | same | 1 adult man (+1 ghosted) |
| `p6_first` | live-action film (modern) | int | room with a **window** (not a doorway); peeling green-cream window frames, **exposed red brick** and a blue panel seen outside through it | 2 framed pictures, curtain, wooden floor | striped knit top, black choker w/ sun pendant, knee socks | 1 girl |
| `p6_last` | live-action film (modern) | int | **same window, tighter** | same brick, frames | same | 1 girl |
| `pancakes` | live-action photographic | int | modern kitchen; white tiled splashback, gas hob, extractor | **frying pan + pancakes**, spatula, grey plate of pancakes, whisk, wall control panel | white t-shirt, blue trousers; white floral pyjamas | 1 adult man + 1 child girl |
| `phone` | live-action photographic | **none** — cut out on pure white | studio white, no environment | **smartphone w/ teal bumper** | sleeveless blue knit top | 1 adult woman |
| `sleeping` | live-action photographic | int | bedroom; grey tweed upholstered bed frame, white linen, light-wood bedside table | **black-framed eyeglasses**, pillows, duvet | navy top | 1 young-adult woman |
| `stage` | live-action photographic | int | **grand theatre auditorium** — two gilded balcony tiers, plaster cartouches, globe lights, red velvet seating, red aisle, stage floor | stage lighting units, recessed downlights, tiered seating | blue sleeveless dress, blue heels | 1 woman + ~100 audience |
| `tv` | live-action photographic | int | domestic living room; damask wallpaper, dark wood TV stand | **CRT television** (off), DVD/VCR player, cables | navy botanical-print blouse, dark trousers | 1 older-adult woman |
| `window` | live-action film (modern) | int | **the same window as `p6`**, shot tighter and blown out — environment essentially unreadable | (none legible) | striped knit top, choker w/ pendant, knee socks, stuffed toy | 1 teenage girl |

## What this gives us per role

### `setting` — usable now

**10 distinct interiors**: 2 classrooms, 2 kitchens, 3 living/dining rooms, bedroom, theatre
auditorium, window room, bookshop interior. (`window` and `p6` are one location, not two.)
**13 exteriors**: shop street, ship deck, castle grounds, snowy park, snowy hillside road, modern
city street, 1950s backlot street at night, downtown skyline from above, **beech forest in fog**,
**alpine range in rain**, **volcano and thatched village**, **grass plain under cumulus**,
**stylised vector skyline**.

Weather now covered: snow (×3), **fog**, **rain**, overcast, clear. Terrain now covered:
forest, alpine rock, grass plain, water, and four flavours of built-up.
**4 no-/low-setting cases** for the "not visible" behaviour: `kasia`, `kiki`, `phone` (all plain
studio grounds), `miyu` (black void). `window` is low-information but is now known to be `p6`.

Probe pairs available:

| pair | what it holds constant | use |
|---|---|---|
| `city_day`/`city_night` | same skyline, same camera, **day vs blue hour** | **the direct atmosphere-quarantine test** |
| `p2_first`/`p2_last` | same kitchen, near-identical light and framing | **the clean control** |
| `p3_first`/`p3_last` | same dining room, near-identical | second clean control |
| `window` + `p6_first` + `p6_last` | one window, **three** framings and exposures | the widest same-place spread we have |
| `p1_first`/`p1_last` | same room, very different exposure | secondary atmosphere probe (exposure, not time of day) |
| `p4_first`/`p4_last` | same street, both heavy bokeh | low-information stress case |
| `jacket`/`jacket2` | same snowy park, different spots in it | **weak** — the snow is near-featureless, so the durable content is thin by nature. Already the character-role garment pair; treat any setting agreement here as a bonus, not a bar |
| `classroom1` vs `classroom2` | *different* rooms of the same type | **negative control** — must NOT collapse into one record |
| `bookshop` | camera outside, interior visible through the glass | `[[SETTING_KIND]]` boundary case |

**Confound on `city_day`/`city_night`**: the skyline carries rooftop bank logos and a large neon
hotel sign. Night lights those up and hides low-rise detail, so a `[[DEFINITION]]` disagreement
across this pair has two possible causes — atmosphere leaking into the durable fields, or the
model naming an illuminated sign it could not read by day. Check which before scoring it. This
is also the strictest printed-text/brand probe in the set.

### `object` — usable now, thin on isolated shots

Good in-scene targets: the CRT television (`tv`), ship's wheel (`captain`), transistor radio
(`p1`), cereal box (`p3`), frying pan (`pancakes`), leather case (`p4`), wheelie bin (`miyu`),
wrought-iron bench (`jacket2`), shoulder bag (`kasia`), breads (`kiki`), newspaper (`newspaper`),
eyeglasses (`sleeping`), 1950s cars (`p5`).

Garments: plate armour (`castle`), captain's uniform (`captain`), puffer jacket
(`jacket`/`jacket2` — **an existing same-garment pair**, the natural drift probe), fedora and
roller skates (`p5`), school uniforms (`classroom1`/`classroom2`).

Only genuinely isolated object: the smartphone in `phone`, and even that is held.

### `style` — blocked, as expected

| medium | count | images |
|---|---|---|
| live-action photographic | 17 | bookshop, captain, castle, city_day, city_night, classroom1/2, forest_autumn, fuji, jacket, jacket2, newspaper, pancakes, phone, sleeping, stage, tv |
| live-action film (modern cinematic) | 11 | p1×2, p2×2, p3×2, p4×2, p6×2, window |
| live-action film (vintage Technicolor) | 2 | p5×2 |
| **digital painting** | 2 | cloud, mountain_rain |
| 2D anime | 2 | kiki, miya |
| 2D illustration (flat cel) | 1 | kasia |
| **flat vector** | 1 | vector_city |
| pixel art | 1 | miyu |

29 of 37 are live-action. Five non-live-action media now, but three of them still have a
single image each — the `style` shopping list below is unchanged apart from digital painting,
which is now covered.

## Gap list

> **Superseded by session 7.** Every item below was filled by the session-7 additions, most of
> them more than once. Kept as written because the *reasoning* about what each gap was for still
> applies, and because the session-7 section refers back to it. The live gap list is
> "Remaining gaps after session 7" at the very bottom.

### Blocking `style` (session 7)

Missing entirely, in rough priority order:

1. **3D CG / CGI animation** — the most common non-live-action medium in real use
2. **watercolour or traditional painting** — `cloud` and `mountain_rain` are digital painting,
   which is close but is its own term; a real watercolour or oil would separate them
3. **comic / graphic-novel / inked line art**
4. **stop-motion or claymation**
5. **archival black-and-white film or photography** — also our only B&W of any kind
6. a second **flat vector** and **pixel art** so those aren't single-sample

A same-subject-across-two-media pair would be the strongest possible style probe (the same
scene as a photo and as a painting), but two unrelated images per medium is enough to start.

### Would help `setting`

Mostly filled. Remaining:

1. **a vehicle interior** (car, train, plane) — the only major setting type with no example
2. a second day/night pair **without signage**, to isolate atmosphere from the brand-text
   confound noted above

~~a natural landscape with no built structures~~ — **filled** by `forest_autumn`,
`mountain_rain`, `cloud`, `fuji`.
~~weather other than snow~~ — **filled**: fog (`forest_autumn`), rain (`mountain_rain`).
~~one place at two different times of day~~ — **filled** by `city_day`/`city_night`.

Probe value the new images add beyond terrain:

- `forest_autumn` holds a **tiny distant human figure** on the path — the person-exclusion rule
  at its hardest, since the figure is easy to miss and easy to mention
- `fuji` is a **famous real landmark** — the first real test of the no-real-place-names rule
- `cloud` carries an **artist signature and a repeating watermark** — printed-text probe
- `mountain_rain`, `cloud`, `vector_city` are stylised **landscapes**, so style leakage is
  tested on images whose content is nothing but environment

### Would help `object`

1. **two or three clean isolated product shots** — an object on a plain ground, nothing else
2. **a garment photographed flat or on a hanger**, and ideally the same garment worn by someone
3. a second view of one object from a different angle (the object equivalent of
   `jacket`/`jacket2`)

---

# Session 7 additions (2026-08-11)

37 files supplied by the user in `images/new/`, read one by one the same way, then moved into
`images/` and `new/` deleted. Five crops were then derived from three of them — four comic panels
and `annie2_cropped` (see "Panels cropped") — giving **79 active files** in `images/`:
74 supplied, 5 derived.

The user chose these deliberately against the session-6 gap list, and against the stretch goal
that list called out as probably out of reach — a same-subject-across-two-media pair. There are
now **nine** such pairs, one of them exact. That is the single most consequential thing about
this batch and it changes what `describer_style` can be tested for (see "What the media pairs
buy us").

## Housekeeping found while reading

- **`coraline2.jpg` was not a JPEG.** It was an AVIF file with a `.jpg` extension.
  `run_tests.py`'s `image_payload()` maps extension to MIME with no sniffing, so it would have
  sent AVIF bytes labelled `image/jpeg`. Converted to **`coraline2.png`** (PIL, lossless
  re-encode of the decoded pixels) and the bad `.jpg` deleted. **If more images arrive from image
  hosts that serve AVIF/WebP behind a `.jpg` URL, check the magic bytes before casting them.** A
  one-line guard in `image_payload()` would be cheap insurance.
- **`cannon.JPG` was an MPO**, not a plain JPEG — a 2-frame stereo pair from a 3D camera,
  4320x3240, 6.3 MB (~8.4 MB base64, 5x the pixel count of anything else here). **Fixed**: frame
  0 extracted, Lanczos-resized to 2000x1500, saved as plain JPEG q90 → **`cannon.jpg`, 0.99 MB**
  (~1.32 MB base64). Visually identical; the original was also marked read-only, which had to be
  cleared first. Note the extension is now lowercase.
- No filename collided with the existing corpus.

## Table

| image | medium | int/ext | setting | prominent objects | notable garments | people |
|---|---|---|---|---|---|---|
| `annie1` | ink-and-marker digital sketch | none — cream paper ground | no environment | (none) | **girl**: coral open jacket, yellow tank, black skirt, black knee boots, choker · **hero (a different person)**: black/red tunic w/ yellow bar fasteners, black cape, black glove, domino mask | **2 distinct characters** on one sheet — a girl (full figure, right) and a masked male hero (head-and-shoulders, left). **They are not the same person** — see the correction note below |
| `annie2` | **watercolour + ink in a sketchbook, photographed in someone's hand** | int (the photo's) / none (the drawing's) | **nested**: inside the drawing, a giant reptilian creature looming over a small girl; outside it, a defocused convention hall w/ black grid shelving | the sketchbook itself | same coral jacket, pale top, black shorts, choker, white socks | 1 girl (drawn) + **1 hand** (real, holding it) |
| `annie3` | **comic page, 4 panels** | ext | alley between buildings; rooftop/street | (none) | **girl**: coral coat, tan top, black skirt, choker · **masked boy hero**: red/black tunic w/ yellow bars, black cape · **masked woman hero**: black/purple suit, yellow gloves and boots · **man**: tan shirt, striped trousers | **4 distinct characters**: 1 girl + 2 costumed heroes (a boy and a woman, both recurring across panels) + 1 man. The heroes are **not** the girl in costume |
| `azumanga_anime` | 2D anime (flat cel, thick outline, sticker border) | none — white ground | no environment | (none) | coral sailor-style school jumpers, white collars, dark red pleated skirts, orange socks / white socks + brown loafers | 3 schoolgirls |
| `azumanga_toon` | **western TV-cartoon (flat toon over textured paint)** | ext | school grounds; chain-link fence, clipped hedges, trees, grass, concrete path, brick edging, outline clouds | (none) | same coral uniforms; one w/ black over-knee socks | same 3 schoolgirls |
| `bird_vector` | flat vector illustration | none — white | no environment | (none) | — | none (1 bird) |
| `bird_watercolor` | **watercolour on textured paper (traditional)** | none — paper ground | no environment | branch | — | none (1 bird) |
| `cannon` | live-action photographic | ext | stone-walled terrace/battery over woodland; limestone rubble walls, pale flagstones | **muzzle-loading cannon on a four-wheeled wooden carriage** | — | none |
| `car_interior_mecha_driver` | 2D anime (painted, desaturated green-grey) | **int — vehicle** | van/MPV cabin; city skyline through the windows | steering wheel, headrests, roof vent, **magazine w/ Japanese cover text** | school sailor uniform w/ blue neckerchief | 1 teenage girl + **1 humanoid robot driving** |
| `car_interior_photo` | live-action photographic (press/product shot) | **int — vehicle** | front cabin of a modern electric car | steering wheel w/ **maker emblem**, large landscape touchscreen showing a map, wood dash trim, centre console | — | none |
| `car_interior_sketch` | **rough digital sketch** (construction lines visible) | **int — vehicle** | car cabin, windows blown out white | steering wheel, headrest, seatbelt | olive short-sleeve shirt; pink tee | 2 young women (driver + passenger) |
| `chair` | **ambiguous — photographic or product render** | none — pure white | no environment | **executive office chair**: black ribbed leather, gold-tone arms and five-star base, castors | — | none |
| `chips_hotdog_dr_pepper_painting` | **oil painting (alla prima, visible brushwork)** | int-ish | painted backdrop and tabletop | **chip bag, glass soda bottle, hot dog in a bun, loose chips** — all w/ **painted brand text** | — | none |
| `comic` | **comic page, 5 panels** | int | classroom; desks, whiteboard w/ geometry diagram, windows, planter boxes | pencil, spider, papers, backpack | black/red/white school uniforms w/ ties; grey blazer; red/black armoured super-suit | 6+ children, 1 adult teacher, 1 costumed figure |
| `coraline1` | **stop-motion puppet, cut out on white** | none — white | no environment | forked twig | yellow raincoat, blue jeans, yellow wellingtons, dragonfly hair clip | 1 girl (puppet) |
| `coraline2` | **stop-motion film still** | int | dim kitchen; sash window, panelled cabinets, deep sink, tiled splashback, round table | open laptop, **mug reading "I love Mulch"**, notebook, pen, a doll | yellow raincoat; grey knitted cardigan | 2 puppets (girl + adult woman w/ **button eyes**) |
| `destroyer_drawing` | **B&W technical recognition plate (halftone, line and wash)** | none | no environment | side elevation + plan view of a warship, range scale, rising-sun emblem | — | none |
| `destroyer_photo` | **archival B&W photograph** | ext | warship at anchor, calm water, blank pale sky, distant masts | twin funnels making smoke, turrets, torpedo tubes, bridge tower, ensign; **kana + "19" on the hull** | — | a few tiny indistinct crew |
| `fish_pixel` | pixel art (flat sprite) | none — dark banded ground | no environment | side-on fish, teal-green back, white belly | — | none |
| `fruitbowl` | **3D render / synthetic still life** | int | plain warm backdrop, wood tabletop | dark ceramic bowl of fruit (green apple, 2 red apples, grapes, 2 bananas), **2 wine bottles w/ illegible script labels**, 1 loose apple | — | none |
| `girl_painting` | **digital painting (oil-style, soft edges)** | none — grey painterly ground | no environment | (none) | black choker, pale knit | 1 girl · **watermark: a Weibo handle** |
| `girl_painting_reference` | live-action film still | int | plain grey-green wall | (none) | black velvet choker, lilac knit | 1 girl — **the exact still `girl_painting` was painted from**; an identifiable real actor |
| `kasia_bag` | product render | none — white | no environment | **yellow shoulder bag, blue flap w/ pale-blue circular emblem, navy webbing strap, gold slider** | — | none |
| `kasia_outfit` | product render, **flat-lay** | none — white | no environment | — | **black vest top, cuffed blue denim shorts, black/blue fingerless gloves, black-and-grey striped knee socks, blue lace-up sneakers** | none |
| `kasia_render` | **3D CG character render (stylised anime)** | none — white studio ground | no environment | (none) | black vest top, cuffed denim shorts, black fingerless gloves, grey striped knee socks, navy/white sneakers, **gold-yellow headband** | 1 girl |
| `kasia_swimsuit` | product render, **flat-lay** | none — white | no environment | — | **black high-neck one-piece swimsuit, yellow collar and yellow chevron** | none · **part of the kasia set** — derived from `kasia_swimsuit_worn`, and worn by the character there and in `kasia_swimsuit_render` (second batch) |
| `kaypro_ii` | live-action photographic | none — white | no environment | **vintage portable computer**: blue/grey metal case, green CRT showing text, 2 floppy drives, detached keyboard w/ blue keypad · **brand name on case AND on screen** | — | none |
| `lincoln_photo` | **archival B&W albumen portrait** | none — plain studio backdrop | no environment | (none) | dark frock coat, white shirt, black bow tie | 1 older adult man · **real historical figure** |
| `lincon_money` | **engraved intaglio print (banknote)** | none | no environment | five-dollar certificate: portrait vignette, guilloche borders, blue treasury seal, serials, signatures — **almost entirely printed text** | — | a portrait *within an object*, not a depicted person |
| `peter_griffin_painting` | **digital painting of a flat-cartoon character** | none — dark olive gradient | no environment | (none) | white collared shirt | 1 adult man (cartoon character rendered painterly) |
| `ramen_pixel` | pixel art (hi-fi, shaded, anti-aliased) | none — dark ground w/ drop shadow | no environment | **bowl of ramen**: noodles, sliced pork, halved soft egg, spring onion, bamboo shoot, steam | — | none |
| `supergirl1` | **marker and ink on board (copic-style)** | ext-ish | sky and stylised clouds inside a drawn panel on white board | (none) | white crop tee w/ red-and-yellow chest emblem, blue skirt, red cape, white gloves, red boots, blue headband | 1 young woman · signed |
| `supergirl2` | **rough coloured-pencil / colour sketch** | none — white | no environment | (none) | same costume | same character, **near-identical flying pose** · hand-lettered title text |
| `teddy_taft` | **archival B&W photograph** | ext | portico/doorway; wet stone step, glazed door, fluted column | (none) | dark overcoats, waistcoat, watch chain, boutonniere, pince-nez | 2 adult men · **real historical figures** |
| `temple_day` | digital painting (high-key, painterly) | ext | gothic ecclesiastical exterior in bright sun; twin-lancet traceried window, columns, balustraded stair rising, spire beyond, potted agaves, trailing greenery, doves | (none) | strapless cream gown, pale green sash, hair ribbon | 1 young woman · date inscription |
| `temple_night` | digital painting (low-key, same hand) | ext | **the same architecture, ruined and dark**: same window and tracery, same stair now broken, rubble, fallen beams, torn red banner, dim violet sky | (none) | cream tunic, brown trousers, tall boots, red cape w/ fur collar, belt; **holding a sword** | 1 young man · signed |
| `van_pixel` | pixel art (PC-98 style, dithered, 16-colour) | ext | roadside; trees, orange-red sky | **blue MPV/van**, front three-quarter, roof rack + luggage, **licence plate** | blue and white outfit, cap | 1 girl at the driver's window |

## What the media pairs buy us

The session-6 list called a same-subject-across-two-media pair "the strongest possible style
probe" and treated it as aspirational. There are now nine, and they are not all equal — they
form a ladder from "identical content, medium is the only variable" down to "same character,
everything else redrawn". **Use the top of the ladder for regression, the bottom for coverage.**

| pair | what is held constant | tier |
|---|---|---|
| `girl_painting_reference` to `girl_painting` | **everything** — the painting was made *from* that still: same subject, pose, crop, framing, expression | **exact.** The only true control. Any content difference between the two records is a defect |
| `supergirl1` / `supergirl2` | same character, same costume, near-identical flying pose; marker board art vs rough pencil | very tight |
| `lincoln_photo` / `lincon_money` | same face, same era; albumen photograph vs line engraving | tight (an object *containing* a portrait, so `[[SUBJECT_KIND]]` is a live question) |
| `destroyer_photo` / `destroyer_drawing` | same warship class; archival photo vs technical plate | tight, and **the only pair with no person in it** |
| `bird_vector` / `bird_watercolor` | a blue-and-orange bird; flat vector vs traditional watercolour | loose — not the same bird, same *idea* of one |
| `coraline1` / `coraline2` | same character; puppet on white vs film still | loose, and doubles as an isolated-subject vs in-scene pair |
| `annie1` / `annie2_cropped` / `annie3_panel1` | one character across **three** media: marker sketch, watercolour, comic page. **Use the cropped/panelled versions for content roles** — the raw `annie2` drags in a convention hall and the raw `annie3` is four scenes at once. **Requires a `SUBJECT:` line**: only `annie2_cropped` has the girl alone; the other two also contain costumed heroes who are different people, so without disambiguation the describer may legitimately record the wrong subject | loose, widest spread |
| `azumanga_anime` / `azumanga_toon` | same three characters, same uniforms; flat anime cel vs western TV-toon | loose, and **a fine `[[MEDIUM]]` discrimination** — both are flat 2D, and telling them apart is exactly the hard case |
| `car_interior_photo` / `_sketch` / `_mecha_driver` | one setting *type* across three media | loosest — different vehicles, useful for `setting` more than `style` |

## Notes recorded against specific images

### The kasia set — authorial intent vs what is in the pixels

The set is **four files, not five**, and every one of them derives from the same drawing:

| file | how it links to `kasia.png` |
|---|---|
| `kasia.png` | the original 2D illustration — the character, her outfit and her bag, all in one image |
| `kasia_render` | a 3D render **based on** the drawing; same character, same outfit. **No bag** |
| `kasia_outfit` | a flat-lay of **the clothes she wears in the drawing**, produced by Qwen Image Edit extracting the garments *from* `kasia.png` — a derived asset, not independent evidence |
| `kasia_bag` | an isolated render of **the bag she carries in the drawing** |

> **SUPERSEDED by the second batch.** `kasia_swimsuit` **is** part of the set. When this was
> written nothing in the corpus linked them; `kasia_swimsuit_worn` (the original 2D commission the
> flat-lay derives from) and `kasia_swimsuit_render` now do. See "The swimsuit is now linked after
> all". The paragraph below is kept only to show what the evidence looked like at the time.

~~**`kasia_swimsuit` is not part of this set.** It is a different outfit, nobody is wearing it, and
**nothing visual ties it to the character** — only the filename does. Treat it purely as an
isolated flat-garment case (see below), and do not cast it in any kasia identity probe.~~

Two probe pairs fall out of the four linked files, and they are different in kind:

- **flat ↔ worn garment**: `kasia_outfit` → `kasia_render` / `kasia.png`. The corpus's only one.
- **isolated ↔ in-scene object**: `kasia_bag` → `kasia.png`, where the same bag is carried. This is
  the *object* analogue of the flat↔worn pair, and the corpus's only one of those too. It is
  imperfect evidence, though — the drawing's bag has **three pin badges** the isolated render
  lacks, on top of the colour difference below. Expect real disagreement and read it as source
  drift, not describer failure.

The headband/bag colour is worth recording precisely, because session 6 wrote "orange" into the
table above and the user reads it as yellow, as does the character's original owner. Sampling the
saturated warm pixels settles what is actually there:

| file | dominant hue | reads as |
|---|---|---|
| `kasia.png` (the original 2D illustration) | **28-34 deg** (`#f8b050`) | orange |
| `kasia_render.png` | **41 deg** (`#e8b850`) | amber, borderline |
| `kasia_bag.png` | **45-47 deg** (`#f8d040`) | yellow |

So this is **not** a shared Claude/Qwen misperception — `kasia.png` really is orange by any
standard hue boundary (yellow starts around 50-60 deg), and the newly generated assets drift
toward the intended yellow. The consequence for testing: **a describer that says "orange" for
`kasia.png` and "yellow" for `kasia_bag.png` is right both times.** A cross-image identity probe
on kasia will show a colour disagreement that originates in the source material, exactly like the
`p4` borderline-age caveat. Do not chase it as a prompt defect. Same applies to the sneakers
(navy/white in `kasia_render`, brighter blue in `kasia_outfit`) — generation drift between
derived assets.

### The temple pair — a split diptych, not two photographs

The user found a single artwork with the ruined/night/male half on the left and the
intact/day/female half on the right, **split it down the middle and mirrored one half** so the
architecture aligns. That has three consequences:

1. It is genuinely **signage-free**, which is what the session-6 gap asked for — the
   `city_day`/`city_night` brand-text confound is absent.
2. It is **not a clean atmosphere control.** The building is intact in one and ruined in the
   other. Ruin is *structural*, not transient, so `[[DEFINITION]]` divergence here is partly
   legitimate and cannot be scored the way `city_day`/`city_night` is. **The clean signage-free
   relight pair is still missing.**
3. Because one half was mirrored, any left/right language in `[[STRUCTURE]]` will conflict across
   the pair. `setting` has no POSITION field so this is mostly harmless, but do not read
   "stair rising to the right" vs "to the left" as drift.

What it *is* good for, and it is not a consolation prize: a **"same place, different condition"**
probe where the durable record *should* partly disagree. We have no other pair like it, and it is
the natural negative control for the day-and-night test — a place that really did change.

### The annie sheets contain two characters, not one in two guises — corrected

**Correction to the first session-7 pass.** `annie1` was originally catalogued as "1 girl, drawn
twice — as herself and as a masked hero". That is **wrong**, and the user caught it. The masked
figure is a **separate, recurring character** (a well-known costumed boy hero), not the girl in a
costume. `annie3` likewise has four distinct people — the girl, two costumed heroes (a boy and a
woman), and a man — not one girl plus her alter ego.

It matters in three ways, which is why it is recorded rather than quietly fixed:

1. **It would have inverted a test verdict.** Under the wrong reading, a describer that produced
   one record covering "a girl who is also a masked hero" would have looked correct, and a
   describer that correctly kept them as two people would have looked like a failure. We would
   have scored a right answer wrong.
2. **The identity ladder needs a `SUBJECT:` line.** `annie1` and `annie3_panel1` each contain the
   girl *and* at least one costumed hero; only `annie2_cropped` has her alone. Cast across the
   three media without disambiguation and the describer may legitimately record a different person
   in each, which would read as catastrophic identity drift and would be nothing of the kind.
3. **It is a genuine `character` disambiguation case**, in the same family as picking one child out
   of six in a classroom — and unlike the classroom, the candidates here differ by *costume*
   rather than by position, which is a different kind of hard.

The general point, and the reason this file exists: **`validate.py` cannot see any of this.** A
record naming the wrong person is perfectly well-formed and will pass every structural check.
Content errors need eyes, and eyes get things wrong too — this row was wrong for a full pass
before the user corrected it.

### Comic pages and the nested-medium case

`comic` and `annie3` are single files containing 4-5 separate scenes; `annie2` is a photograph of
a watercolour held in a hand in front of an exhibition hall. Every describer built so far assumes
one frame, one place, one moment, so `[[SETTING_KIND]]` has no correct answer for any of them.

**Agreed approach**: crop panels for the content roles, keep the full pages for `style`, and run
an uncropped page through `setting` **once, as a diagnostic that is recorded and never patched**.
The reasoning is this project's own most expensive lesson — `[[SUBJECT NOT FOUND]]` cost three
rounds and caused every format failure in setting v1–v3 before it was deleted, and the conclusion
written down was that *an optional behaviour that fires on judgement is a liability unless the
role genuinely needs the judgement*. Multi-panel handling is that trap in a new costume: if a
comic page produces mush, the reflex is to add an "if the image contains multiple panels…" rule,
and that rule will cost us elsewhere the way the setting-v2 paragraph did. Know the failure mode;
do not defend against it.

#### Panels cropped (session 7)

Gutters were detected programmatically (row/column runs of ≥97%-white pixels, then per-band
column analysis), not estimated by eye; all four crops exclude the panel border rules with no
bleed from neighbours. Kept deliberately few — these are the panels that earn a place, not all
nine.

| crop | source | why it was kept |
|---|---|---|
| `comic_panel4.jpg` (1249x904) | `comic` bottom panel | **classroom interior, 6+ people, desks, windows, planter boxes.** A *third* classroom for the `classroom1` vs `classroom2` negative control — and the first one in a non-photographic medium, so it tests that the negative control survives a medium change. Also a multi-person `character` disambiguation case |
| `comic_panel3.jpg` (1161x460) | `comic` middle panel | two adults at a whiteboard, **same room as `comic_panel4`** — so the two crops are a *same-place pair inside one comic medium*, which nothing else in the corpus provides. Carries a dialogue balloon |
| `comic_panel2.jpg` (335x429) | `comic` top-right panel | close-up of the **same girl as `comic_panel4`** → a same-character/two-framings drift probe in one medium (the comic analogue of the `p6` wide/close pair). **Her name is printed in the speech balloon**, making it the harshest no-name probe we have: the answer is literally written in the image |
| `annie3_panel1.jpg` (428x1434) | `annie3` leftmost panel | the girl near-full-figure in an alley — **completes the three-media identity ladder for the content roles**, not just for `style`: `annie1` (marker sketch) / `annie2_cropped` (watercolour) / `annie3_panel1` (comic). Also has her name in a balloon. **Two costumed heroes share the panel**, so cast it with a `SUBJECT:` line |

Not kept: `comic` panels 1 (a hand and a spider, no usable setting or subject) and `annie3`
panels 2–4 (costumed figures on flat grounds — the corpus already has plenty and they add no new
probe). The crop boxes are recorded in the session-7 handoff if any of them are wanted later.

**`annie2` is kept whole *and* cropped — both, deliberately.** The user added
**`annie2_cropped.jpg`** (722x1273), which removes the hand, the sketchbook edge and the
defocused convention hall, leaving only the painted page. This is better than cropping *or*
keeping alone, because the two files now serve two different jobs and cannot confound each other:

- **`annie2`** (uncropped) is the corpus's only **nested-medium** case — a photograph of a
  painting. "The reference image contains another image" is ordinary in real use (posters, phone
  screens, TVs — `tv.png` already has a CRT), and it argues for `describer_style` stating up front
  whether it reports the medium of the photograph or the medium of the thing photographed. That
  is a rule worth having *before* the prompt exists, unlike multi-panel handling, which would be
  a patch after the fact.
- **`annie2_cropped`** is a clean **traditional watercolour** sample with no photographic
  contamination — which matters because watercolour was one of the thinnest media in the corpus.
  It is also the Annie identity ladder's watercolour rung, and being free of the hand and the
  hall it can be compared against `annie1` and `annie3_panel1` without the character record
  picking up an exhibition hall that has nothing to do with her.

Content of the page itself: the girl in her coral jacket, pale yellow top, black shorts, choker
and white socks, standing small in the clawed hand of a huge tan reptilian creature whose head
looms above her. Ink line over watercolour wash on textured paper.

`annie2` is the exception worth a real rule: "the reference image contains another image" is
common in ordinary use (posters, phone screens, TVs — `tv.png` already has a CRT), and
`describer_style` will need to say up front whether it reports the medium of the photograph or
the medium of the thing photographed.

## Medium tally — full corpus (74)

| medium | count | images |
|---|---|---|
| live-action photographic | 21 | the session-6 17 + cannon, car_interior_photo, kaypro_ii, chair* |
| live-action film (modern cinematic) | 12 | p1x2, p2x2, p3x2, p4x2, p6x2, window, girl_painting_reference |
| live-action film (vintage Technicolor) | 2 | p5x2 |
| **archival B&W photograph** | 3 | destroyer_photo, lincoln_photo, teddy_taft |
| **3D CG / product render** | 5 | kasia_render, fruitbowl, kasia_bag, kasia_outfit, kasia_swimsuit |
| digital painting | 6 | cloud, mountain_rain, girl_painting, peter_griffin_painting, temple_day, temple_night |
| **oil painting** | 1 | chips_hotdog_dr_pepper_painting |
| **watercolour (traditional)** | 3 | bird_watercolor, annie2 (nested in a photograph), **annie2_cropped** (clean) |
| 2D anime | 4 | kiki, miya, azumanga_anime, car_interior_mecha_driver |
| 2D illustration (flat cel) | 1 | kasia |
| **western TV-cartoon** | 1 | azumanga_toon |
| **comic page (inked line art)** | 2 | comic, annie3 |
| **marker/copic board art** | 1 | supergirl1 |
| **rough sketch** | 3 | annie1, supergirl2, car_interior_sketch |
| **stop-motion** | 2 | coraline1, coraline2 |
| flat vector | 2 | vector_city, bird_vector |
| pixel art | 4 | miyu, fish_pixel, ramen_pixel, van_pixel |
| **B&W technical print** | 1 | destroyer_drawing |
| **engraved intaglio** | 1 | lincon_money |

\* `chair` is deliberately left ambiguous — it may be a photograph or a product render, and
neither reading is obviously wrong. That makes it a useful `describer_style` hard case rather
than a mislabelled row.

Live-action share has fallen from 29/37 (78%) to 38/74 (51%), and **every** medium now has at
least two images except five singletons (oil, western toon, marker board, technical print,
intaglio) — which are singletons because they are genuinely rare in practice, not because of
sampling.

## Printed text and real-identity pressure

Both no-name rules are now testable at far higher pressure than the two film stills of session 6.

**Printed text**, hardest first: `lincon_money` (almost nothing but text) · `destroyer_drawing`
(class name, dimensions, tonnage, date) · `kaypro_ii` (brand on the case *and* rendered on the
screen) · `chips_hotdog_dr_pepper_painting` (**three** brands, hand-painted, so the text is part
of the brushwork) · `comic` and `annie3` (dialogue balloons + a character name) · `supergirl2`
(hand-lettered title) · `car_interior_photo` (maker emblem) · `car_interior_mecha_driver`
(Japanese cover text) · `coraline2` (a mug slogan) · `van_pixel` (licence plate) · `annie1`
(signature, seal, name in two scripts) · `girl_painting` (a Weibo watermark).

**Real identifiable people**: `lincoln_photo` and `lincon_money` (the same man twice, across two
media — the strongest identity probe we have), `teddy_taft` (two at once),
`girl_painting_reference` (a well-known actor, and the source of `girl_painting`).

**Recognisable fictional characters**: coraline x2, supergirl x2, azumanga x2, annie x3 (+ the two
panel crops), comic, peter_griffin, kasia, kiki, miya. Two cases are nastier than the rest:

- `peter_griffin_painting` — instantly recognisable but rendered in a medium the source never
  uses, so naming the franchise requires *recognition* rather than *reading a label*.
- **`annie1` and `annie3` mix an original character with two famous licensed ones.** The girl is
  the artist's own; the masked hero beside her is not. A describer can therefore fail *partially*
  here — correct and neutral about the girl, franchise-naming about the figure next to her — which
  is a more realistic failure than an image where everything is licensed or nothing is.

## Remaining gaps after session 7

> **SUPERSEDED — all four items below were closed by the second batch.** Kept because the
> reasoning about *what each gap was for* still applies, and the second-batch section refers back
> to it. See "Remaining gaps after the second batch" at the very end for the live list.

This replaces the session-6 gap list above.

1. **A clean signage-free day/night pair** — same camera, same place, same structure, relit only.
   `temple_day`/`temple_night` is signage-free but changes the building (see above);
   `city_day`/`city_night` is a clean relight but carries brand signage. **No single pair is
   both**, and this is the one thing the atmosphere quarantine still cannot be tested against
   cleanly.
2. **A clean second view of one object** — the object equivalent of `jacket`/`jacket2`.
   **Partly covered now**: `kasia_bag` (isolated render) and `kasia.png` (the same bag carried on
   her shoulder) are two views of one object, which is more than we had. But it is confounded
   three ways at once — different angle *and* different medium *and* the drawing's bag has three
   pin badges the render lacks and reads a different hue. `destroyer_photo`/`destroyer_drawing`
   and `lincoln_photo`/`lincon_money` have the same problem: two *media*, not two *viewpoints*.
   `chair`, `kaypro_ii` and `cannon` are each a single angle. **What is still wanted is one
   object, two angles, same medium, nothing else changing** — the control that isolates viewpoint.
3. **A second flat-to-worn garment pair** — one garment photographed flat *and* worn by someone.
   `kasia_outfit` → `kasia_render` is the only one we have, and a single sample is thin.
   `kasia_swimsuit` does **not** help here despite the filename: nobody wears it anywhere in the
   corpus, and it isn't visually tied to the character (see "The kasia set"). Any garment would
   do — it does not have to involve kasia.
4. Nice-to-have, not blocking: a second oil painting, a second western TV-cartoon, and a second
   piece of marker/board art, so those three stop being singletons.

---

# Session 7, second batch — every remaining gap closed

14 more files supplied by the user in `images/new/`, plus **5 crops** derived from two of them.
Corpus is now **98 active files** (93 supplied, 5 derived here, plus the 5 derived earlier).
`images/new/` removed again.

These were chosen against the four-item gap list at the end of the first batch. **All four are now
closed**, and one of them reverses a correction made earlier the same session (see "The swimsuit
is now linked after all").

## Table

| image | medium | int/ext | setting | prominent objects | notable garments | people |
|---|---|---|---|---|---|---|
| `car_1` | product render (or studio photo — same ambiguity as `chair`) | none — white | no environment | **white crossover SUV, front three-quarter**; roof rails, black wheel arches, maker emblem | — | none |
| `car_2` | product render | none — white | no environment | **the same SUV, pure side view** — identical vehicle, lighting, ground and background | — | none |
| `kasia_bag_2` | product render | none — white | no environment | **the kasia bag upright, three-quarter front** — yellow body, navy flap, pale-blue circular emblem, navy strap looped over the top | — | none |
| `kasia_swimsuit_worn` | **2D illustration (flat cel / anime)** | none — stylised water-pattern band on white | no environment | (none) | **the black high-neck swimsuit w/ yellow collar and yellow chevron** — worn | 1 girl (**the kasia character**: black bob, yellow headband, green eyes, freckles) · **watermark: a commission credit** |
| `kasia_swimsuit_render` | AI 3D-ish render (anime idiom) | ext | poolside; clipped hedge, handrails, pale coping, blue water | handrails | **the same swimsuit**, worn | 1 girl (same character) |
| `ayanami_oil` | **digital painting in an oil/gouache idiom** | int | tiled washroom or pool edge; pale green tiles, dark floor tiles, green ledge | (none) | pale school swimsuit | 1 girl, blue hair, red eyes |
| `woman_oil` | **traditional oil painting (photorealist)** | int | dark room; black wall, dark bench or piano stool, white drape at right | dark bench/stool w/ visible hinge, crumpled white cloth | cream puff-sleeved blouse, dark skirt | 1 young woman, asleep on her arms |
| `marker` | **marker and ink on board** | int | window with blue sky and clouds behind her; drawn board border | window | off-shoulder cable-knit top, dark high-waisted pleated skirt, black ribbon choker, hoop earrings, hair ribbons | 1 young woman · signed |
| `ivy_toon` | **western TV-cartoon (90s cel animation still)** | int | blue technological interior; circuit-trace wall panels, yellow door frame | **a white and grey handheld device on a chain** | brown leather jacket, white top, khaki trousers | 1 young woman, red bob |
| `peter_griffin_toon` | **western TV-cartoon (modern flat digital)** | int | office; desk, wall poster, framed wall chart, dark carpet | desktop monitor, keyboard, mouse, phone | white shirt w/ black belt, green trousers, brown shoes; blue polo | 2 adult men |
| `shrek_cg` | **3D CG feature animation** | ext | open sky, wispy cloud, dry grass at right | (none) | brown leather-look tunic, cream undershirt w/ lacing | 1 green ogre, close-up, hand raised |
| `woody_cg` | **3D CG feature animation (early)** | int | dim room, brown/ochre ground, indistinct | **holster on the belt**, sheriff badge | yellow check shirt, cow-print waistcoat, blue jeans, brown boots w/ spurs, brown hat | 1 male doll/figure |
| `forest_day_night` | flat vector illustration | ext | **composite** — two stacked panels, day above and night below, of one forest clearing | — | — | none |
| `san_fransisco_day_evening_night` | flat vector illustration | ext | **composite** — three stacked panels, day / evening / night, of one park-and-skyline view | — | — | none |

### The five crops

| crop | source | size |
|---|---|---|
| `forest_day` | `forest_day_night` rows 0–739 | 947x739 |
| `forest_night` | `forest_day_night` rows 742–1480 | 947x738 |
| `sanfran_day` | `san_fransisco_day_evening_night` rows 0–487 | 1039x487 |
| `sanfran_evening` | rows 495–982 | 1039x487 |
| `sanfran_night` | rows 993–1480 | 1039x487 |

The San Francisco composite has clean white gutters (rows 487–495 and 982–993, found the same way
as the comic panels). **The forest composite has none** — the two panels butt directly, and the
seam had to be found from the row-to-row brightness discontinuity, which is unambiguous at row 741
(mean brightness 102.8 → 24.7). One or two seam rows are trimmed from each side; both crops were
checked visually and carry no edge artefact.

Both composites are **kept** alongside their crops. They cost nothing, they are the provenance,
and they are a second kind of multi-panel diagnostic — a non-comic one, where the panels are the
*same* scene rather than a sequence.

Crop content by common sense: `forest_*` is a clearing backed by broadleaf trees and low scrub,
grass foreground, distant hills. `sanfran_*` is a grass bank and conifers with a red suspension
bridge at left and a white high-rise cluster at right, water across the foreground.

## The swimsuit is now linked after all — reversing an earlier correction

Earlier this session `kasia_swimsuit` was removed from the kasia set on the grounds that "nothing
in our inventory links them except the filename". **That was true when it was written and is no
longer true.** `kasia_swimsuit_worn` is the **original 2D commission the flat-lay was derived
from**, and `kasia_swimsuit_render` is an AI render of the same character wearing it. The
character is unmistakably the same in both — black bob, **yellow** headband, green eyes, freckles.

So the kasia set is now **eight files, one character, two outfits**:

| outfit | worn | flat / isolated |
|---|---|---|
| everyday | `kasia.png` (2D drawing), `kasia_render` (3D) | `kasia_outfit` (flat-lay, derived from `kasia.png`), `kasia_bag` + `kasia_bag_2` (the bag she carries) |
| swimsuit | `kasia_swimsuit_worn` (2D commission), `kasia_swimsuit_render` (AI render) | `kasia_swimsuit` (flat-lay, derived from `kasia_swimsuit_worn`) |

Corrections to what the earlier section says:

- `kasia_swimsuit` **is** part of the set. Its table row and the "not part of this set" warning are
  superseded by this section.
- It is a **second** flat-to-worn garment pair, which was gap 3. That gap is closed.
- The colour finding still stands and is now better evidenced: the headband is **yellow** in
  `kasia_swimsuit_worn`, `kasia_swimsuit_render` and `kasia_render`, and **orange** only in
  `kasia.png`. That makes `kasia.png` the outlier rather than the reference, which is the opposite
  of how the first pass framed it. The measurement is unchanged — `kasia.png` really is hue 28–34°
  — but with three files now agreeing on yellow, a describer that says "orange" for `kasia.png`
  is still right about that image while being wrong about the character.

**The general lesson is about the inventory, not about kasia.** A "these are unrelated" judgement
is only ever true of the corpus *as it stands*. Two of the three content errors caught this session
were of this shape — an inferred relationship, not a described object. Description rows have been
reliable; **claim rows have not**, and they are the ones that change a test verdict.

## Every gap from the first batch is now closed

| gap | closed by | caveat |
|---|---|---|
| **1. A clean signage-free day/night pair** | `forest_day`/`forest_night` and `sanfran_day`/`_evening`/`_night` | **they are flat vector illustrations, not photographs** — see below |
| **2. A clean second view of one object, same medium** | **`car_1`/`car_2`** — the same SUV, front three-quarter and pure side, with identical lighting, ground and background. **Nothing changes but the viewpoint**, which is exactly the control that was missing | none. This is the clean one |
| | `kasia_bag`/`kasia_bag_2` as a second sample | an AI re-render, so not pixel-faithful; the strap is arranged differently. Use `car_*` as the control and this as the harder case |
| **3. A second flat-to-worn garment pair** | `kasia_swimsuit` → `kasia_swimsuit_worn` / `kasia_swimsuit_render` | the flat-lay is derived from the 2D image, so it is not independent evidence — same caveat as `kasia_outfit` |
| **4. Singleton media** | oil 1→3, western TV-cartoon 1→3, marker board art 1→2 | `ayanami_oil` is digital-emulating-oil rather than traditional oil; see the tally note |

### The day/night pairs close the gap, but they are an *easier* test than `city_day`/`city_night`

Worth being explicit, because it would be easy to over-read a pass here.

The gap asked for "same camera, same place, same structure, relit only", and these deliver that
perfectly — they are literally one piece of vector artwork recoloured, so there is **zero**
photographic variation and **zero** signage. As a control for the atmosphere quarantine that is
ideal.

But the failure mode session 6 diagnosed was that **by day the model describes forms and by night
it describes lights**, and that happens because a real night photograph genuinely destroys
information — the low-rise detail in `city_night` is simply gone. **In a vector illustration
nothing is destroyed.** The night forest still shows every tree, every shrub and the grass. So a
describer can pass these pairs comfortably while still failing `city_day`/`city_night`.

Use them as the *diagnostic* — they isolate atmosphere from signage and from information loss, so
a failure here is unambiguous. Keep `city_day`/`city_night` as the *bar*.

`sanfran_*` adds something no other pair has: **three time points**, so drift can be checked across
a series rather than a pair. Its evening panel is the interesting one — golden sky, everything else
identical.

## New probe pairs from this batch

| pair | holds constant | use |
|---|---|---|
| `car_1` / `car_2` | one object, two angles, **same medium, same lighting, same ground** | the object-viewpoint control. The cleanest pair in the whole corpus after `girl_painting_reference` |
| `peter_griffin_painting` / `peter_griffin_toon` | **one character, canonical flat toon vs painterly rendering** | directly tests the case flagged in the first batch — recognising a franchise character *without a label*, now with the canonical version present for comparison |
| `forest_day` / `forest_night` | one scene, relit | atmosphere quarantine, signage-free |
| `sanfran_day` / `_evening` / `_night` | one scene, **three** lighting states | atmosphere drift across a series |
| `kasia_swimsuit` / `_worn` / `_render` | one garment: flat, worn in 2D, worn in 3D | flat-to-worn, and a second kasia identity rung |
| `kasia_bag` / `kasia_bag_2` | one object, two angles, two renders | object viewpoint, harder than `car_*` |
| `ayanami_oil` / `woman_oil` | oil idiom, **digital vs traditional** | a fine `[[MEDIUM]]` discrimination, like `azumanga_anime`/`azumanga_toon` |
| `ivy_toon` / `peter_griffin_toon` | western TV-cartoon, **90s cel vs modern flat digital** | another fine discrimination inside one coarse category |

## Updated medium tally — 98 active files

Only the rows that changed are listed; everything else is as in the first-batch tally.

| medium | was | now | added |
|---|---|---|---|
| flat vector | 2 | **9** | forest_day_night + 2 crops, san_fransisco composite + 3 crops |
| 3D CG / product render | 5 | **9** | car_1, car_2, kasia_bag_2, kasia_swimsuit_render |
| **3D CG feature animation** | — | **2** | shrek_cg, woody_cg — *a new category, and distinct from product render: character animation, not object rendering* |
| oil / oil-idiom painting | 1 | **3** | woman_oil (**traditional**), ayanami_oil (**digital, emulating oil**) |
| western TV-cartoon | 1 | **3** | ivy_toon (90s cel), peter_griffin_toon (modern flat digital) |
| marker/copic board art | 1 | **2** | marker |
| 2D illustration (flat cel) | 1 | **2** | kasia_swimsuit_worn |

**No medium is a singleton any more.** Live-action is now roughly 38 of 98 (39%), down from 78% at
the start of session 7.

The oil row deserves care when the `[[MEDIUM]]` vocabulary is designed: `woman_oil` is paint on a
surface, `ayanami_oil` is a digital file imitating it, and `chips_hotdog_dr_pepper_painting` is
traditional oil of a photographic subject. If the vocabulary has one "oil painting" term, all three
collapse into it — which may be the right answer, but it should be a decision rather than an
accident.

## Printed text and identity — additions

- `kasia_swimsuit_worn` carries a **commission watermark** — a credit line, not a brand.
- `car_1`/`car_2` carry a **maker emblem** on the grille and wheels, like `car_interior_photo`.
- `ivy_toon`, `peter_griffin_toon`, `shrek_cg`, `woody_cg` are all **instantly recognisable
  licensed characters with no text anywhere in frame**. Combined with `peter_griffin_painting`
  they make the no-franchise-name rule testable purely on recognition, across four different media.

## Remaining gaps after the second batch

**None outstanding.** Every item on the previous list is closed. What is left is not a gap so much
as a standing preference:

1. **More live-action breadth**, if `style` turns out to need it — 39% is healthy, but the
   photographic images skew heavily toward people and rooms.
2. **A day/night pair that is both photographic *and* signage-free** would still be the ideal, and
   remains unfilled — `city_*` is photographic with signage, `forest_*`/`sanfran_*` are
   signage-free without photography. This is now a refinement rather than a blocker: between them
   the two pairs isolate every variable, just not in one image.
