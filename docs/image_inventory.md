# Image inventory — `images/`

Ground truth for the test corpus, built by **reading every file directly**, not by running a
describer over them. `validate.py` checks format and cannot see content; this document is what
lets us judge whether a describer said something *true*.

**100 active files.** The two files formerly excluded as `p1_first.old.png` / `p1_last.old.png`
were renamed to `door_first` / `door_last` in session 8 and read properly for the first time —
they are not duplicates of `p1`, they are a different shot, and one of them is the most useful
failure case in the corpus (see "Known describer limitations").

## How to maintain this document

Reorganised in session 8. It had previously grown one section per pass — three image tables, two
pair tables, two medium tallies, three gap lists — so answering "what do we have with vehicles in
it" meant reading the whole file. The rules below exist to stop that recurring.

- **New images append rows to the master table and the contents table.** Never open a new
  per-session table; the `added` column carries that information.
- **A correction edits the master/contents row in place *and* adds a row to
  "Corrections & superseded findings".** The tables are always current-truth; the corrections
  table is the audit trail. Do not leave struck-through prose behind.
- **`docs/` is git-tracked**, so superseded content can be *deleted* rather than carried — git
  has it. Keep only what still changes a decision.
- **The medium tally is generated**, not hand-edited. Run `scripts/inventory.py` (see TODO —
  not built yet) to regenerate it and to cross-check `images/` against the master table.
- The `medium` and `sub` columns use the **closed two-level vocabulary** defined below — the
  draft for `describer_style`'s `[[MEDIUM]]` field. Free-text nuance goes in `detail`, never in
  `medium` or `sub`, or the tally stops grouping.

**Flags:** `text` printed/legible text in frame · `real` real identifiable person or place ·
`franchise` recognisable licensed fictional character · `derived` derived from another corpus
file · `corr` has a row in the corrections table · `amb` **medium is not visually determinable** —
the classification rests on provenance the describer cannot see, so **do not score `[[MEDIUM]]`
on this image either way**.

**`added`:** `s6` session 6 · `s7a` session 7 first batch · `s7b` session 7 second batch ·
`-crop` suffix for files derived in that session.

---

## Medium vocabulary — closed, two-level

Adopted session 8. This is the **draft `[[MEDIUM]]` vocabulary for `describer_style`**, not just
an inventory convention — reclassifying the corpus and designing that field are the same job.

The previous list had grown to 20 ad-hoc terms one image at a time, and it mixed three unrelated
axes: **how it was made** (oil, vector, pixel), **colour/era treatment** ("archival B&W", "vintage
Technicolor"), and **what was rendered** ("product render" vs "feature animation" — both are 3D
CG). That is the age-drift failure mode in a worse form: with age, two describers could disagree
on where a boundary sits; here they could disagree on *which axis they were answering*.
`destroyer_photo` is truthfully archival, monochrome **and** photographic, and every one of those
was a top-level term.

A flat list would have fixed the drift and **broken the corpus on purpose** — `azumanga_anime`/
`azumanga_toon`, `ayanami_oil`/`woman_oil` and `ivy_toon`/`peter_griffin_toon` exist specifically
as fine-discrimination probes, and a vocabulary that cannot express their difference does not make
them pass, it makes them meaningless. So: **coarse term always emitted, sub-term where the coarse
term has one.** The coarse level is drift-proof; the sub level carries what the probe pairs test.

| coarse (11) | sub-terms |
|---|---|
| `photograph` | `colour` · `archival` |
| `live-action film` | `modern` · `vintage Technicolor` |
| `3D CG` | `product render` · `character render` · `feature animation` |
| `stop-motion` | — |
| `2D cel` | `anime` · `western toon` · `flat illustration` |
| `comic` | — |
| `painting` | `oil` · `watercolour` · `gouache` · `digital` |
| `drawing` | `marker` · `sketch` · `ink` |
| `vector` | — |
| `pixel art` | — |
| `print` | `engraving` · `technical plate` |

### Tie-break rules

These exist so that two records of one image cannot legitimately disagree — the same job the
"no environment → interior" tie-break does for `[[SETTING_KIND]]`.

1. **`stop-motion` beats `photograph`.** A stop-motion frame is literally a photograph of physical
   objects, so without this rule `coraline1`/`coraline2` are defensibly photographic and will
   drift. What is photographed is a constructed miniature; that wins.
2. **Nested images report the OUTER medium.** `annie2` is a photograph *of* a watercolour, so it
   is `photograph / colour`, with `annie2_cropped` serving as the clean watercolour sample. Same
   rule `tv` needs for its CRT and any poster, phone screen or television in frame.
3. **Digital imitation reports the idiom, not the substrate.** `ayanami_oil` is a digital file in
   an oil/gouache idiom → `painting / digital`; `woman_oil` is paint on a surface →
   `painting / oil`. The pair therefore **agrees at coarse level and differs at sub level**,
   which is a scorable result rather than a collapse. This is the design working as intended.
4. **`photograph` and `live-action film` stay separate** even though a film still is a photograph.
   The distinction is look — grain, grade, aspect, lighting — and "cinematic" is a real signal for
   a *video* prompt. Judged on presentation, not on provenance.

### The sub level needs a third axis — the session-9 finding, to be executed next session

`L-ONE-AXIS-PER-VOCABULARY` was applied to the **coarse** list in session 8 and never to the
sub-lists. The full-corpus sweep made the cost measurable, and the user's diagnosis reframed it
from a labelling annoyance into the **cause of the biggest failure in the round**.

#### The sub level is a grab-bag of at least five axes

| sub-list | what it actually mixes |
|---|---|
| `2D cel` — anime · western toon · flat illustration | **idiom / tradition** |
| `drawing` — marker · sketch · ink | **instrument** (marker, ink) vs **degree of finish** (sketch) |
| `painting` — oil · watercolour · gouache · digital | **medium** (first three) vs **substrate** (digital) |
| `photograph` — colour · archival | **property** vs **era/treatment** |
| `live-action film` — modern · vintage Technicolor | **era** vs **a specific process** |
| `3D CG` — product render · character render · feature animation | **purpose / what is depicted** |
| `print` — engraving · technical plate | **process** vs **purpose** |

#### The coupling causes the coarse misclassification — this is the important part

**`drawing` was emitted once in 100 images**, against five true `drawing` files. Every one of the
four misses is explained by the *sub*-term, not the coarse term:

| image | idiom the model saw | the only coarse term that owns it | what it emitted |
|---|---|---|---|
| `car_interior_sketch` | anime | `2D cel` | `2D cel / anime` |
| `marker`, `supergirl1` | digital | `painting` | `painting / digital` |
| `annie1` | watercolour | `painting` | `painting / watercolour` |

The model is not failing to see a drawing. **It sees the idiom correctly, and the vocabulary gives
it nowhere to put that idiom except under a different coarse term.** The sub-term drags the coarse
term with it. That also explains `painting / digital` being a sink (10 emitted, 7 true): `digital`
is the only place a digitally-made image can go, so everything digital lands in `painting`.

#### The agreed fix: a third field

Proposed by the user, session 9. `anime` and `western toon` are **traditions**, orthogonal to how
an image was made — you can have anime in cel, in pixel art, in a drawing, in a painting, in 3D CG.
So separate the axes properly rather than widening sub-terms case by case:

```
[[MEDIUM]]     how it was made      photograph · live-action film · 3D CG · stop-motion ·
                                    2D cel · comic · painting · drawing · vector · pixel art · print
[[IDIOM]]      what tradition       anime · western toon · realist · ... · none
[[TREATMENT]]  colour / era         archival · vintage Technicolor · monochrome · ... · none
```

The user's own examples become natural and currently cannot be expressed at all:
`car_interior_sketch` → **drawing / anime**, `miyu` → **pixel art / anime**,
`peter_griffin_painting` → **painting / western toon**.

**This is not a restart.** The coarse column is unchanged and it is the column that scored 86/95.
What changes is re-deriving the sub column, and `scripts/inventory.py` already parses and validates
the master table, so most of it is mechanical rather than a re-reading of 100 images.

Open questions to settle when executing:

- Do `product render` / `character render` / `feature animation` belong on a fourth axis (purpose),
  or do they collapse into `[[IDIOM]] realist` plus nothing?
- Does `sketch` become a `[[TREATMENT]]` (degree of finish), leaving `[[MEDIUM]] drawing` with
  `[[IDIOM]]` carrying the tradition?
- Whether three emitted fields is worth it versus widening sub-terms across coarse terms — the
  lighter option, which fixes the named cases but leaves `drawing` and `painting` still mixing.
- Whether `chair` / `car_1` / `car_2` leave `amb` under a consistent presentation rule (see
  "The `amb` images").

**Until it is executed**: score the coarse term with confidence, and treat a lone sub-term miss in
`drawing`, `painting`, `2D cel` or `live-action film` as **contested rather than wrong**.

### What the reclassification changed

- **`annie2` moved from watercolour to `photograph`** under rule 2. That is a deliberate
  consequence of the nesting rule, not a re-reading of the image. It nudges the live-action share
  up by one with a file whose *content* is a drawing — worth remembering before quoting that
  percentage.
- **`chair` is a coarse-level ambiguity** (`photograph` vs `3D CG`), the worst kind. It is filed
  as `photograph` and stays deliberately ambiguous — that is what makes it a good hard case.
- The five old era/treatment terms (`archival B&W photograph`, `live-action film (vintage
  Technicolor)`, `western TV-cartoon`, `3D CG feature animation`, `2D illustration (flat cel)`)
  are all now sub-terms, which is where they belonged.

---

## Master table — classification

| image | medium | sub | detail | int/ext | people | sets | added | flags |
|---|---|---|---|---|---|---|---|---|
| `annie1` | drawing | marker | ink and marker, digital | none | **2 distinct characters**: a girl (full figure) + a masked male hero (head and shoulders) | annie | s7a | text, franchise, corr |
| `annie2` | photograph | colour | + ink, photographed in a hand | **nested** — int (photo) / none (drawing) | 1 girl (drawn) + 1 hand (real) | annie | s7a | franchise, nested |
| `annie2_cropped` | painting | watercolour | clean page, hand and hall removed | none | 1 girl (drawn) | annie | s7a-crop | franchise, derived |
| `annie3` | comic | — | 4 panels | ext | **4 distinct**: 1 girl, 2 costumed heroes (a boy, a woman), 1 man | annie | s7a | text, franchise, corr |
| `annie3_panel1` | comic | — | leftmost panel | ext | 1 girl + 2 costumed heroes | annie | s7a-crop | text, franchise, derived |
| `ayanami_oil` | painting | digital | **digital**, oil/gouache idiom | int | 1 girl, blue hair, red eyes | oil-idiom | s7b | franchise |
| `azumanga_anime` | 2D cel | anime | flat cel, thick outline, sticker border | none | 3 schoolgirls | azumanga | s7a | franchise |
| `azumanga_toon` | 2D cel | western toon | flat toon over textured paint | ext | same 3 schoolgirls | azumanga | s7a | franchise |
| `bird_vector` | vector | — | — | none | none (1 bird) | bird | s7a | — |
| `bird_watercolor` | painting | watercolour | on textured paper | none | none (1 bird) | bird | s7a | — |
| `bookshop` | photograph | colour | — | **ext (int visible)** | 1 adult man | setting-boundary | s6 | — |
| `cannon` | photograph | colour | — | ext | none | — | s7a | — |
| `captain` | photograph | colour | — | ext | 1 adult man | — | s6 | — |
| `car_1` | photograph | colour | user: automaker press shot. Photo vs render **not visually determinable** | none | none | car-angle | s7b | text, amb |
| `car_2` | photograph | colour | as `car_1` | none | none | car-angle | s7b | text, amb |
| `car_interior_mecha_driver` | 2D cel | anime | painted, desaturated green-grey | **int (vehicle)** | 1 teenage girl + 1 humanoid robot | car-interior | s7a | text, franchise |
| `car_interior_photo` | photograph | colour | press/product shot | **int (vehicle)** | none | car-interior | s7a | text |
| `car_interior_sketch` | drawing | sketch | digital, construction lines visible | **int (vehicle)** | 2 young women | car-interior | s7a | — |
| `castle` | photograph | colour | — | ext | 1 young-adult woman | — | s6 | — |
| `chair` | photograph | colour | user: Amazon listing. Photo vs render **not visually determinable** | none | none | — | s7a | amb |
| `chips_hotdog_dr_pepper_painting` | painting | oil | traditional, alla prima | int-ish | none | — | s7a | text |
| `city_day` | photograph | colour | — | ext | none | city-daynight | s6 | text |
| `city_night` | photograph | colour | blue hour | ext | none | city-daynight | s6 | text |
| `classroom1` | photograph | colour | — | int | 5 children | classroom | s6 | — |
| `classroom2` | photograph | colour | — | int | 6+ children | classroom | s6 | — |
| `cloud` | painting | digital | painterly, deckle border | ext | none | — | s6 | text |
| `comic` | comic | — | 5 panels | int | 6+ children, 1 adult teacher, 1 costumed figure | comic-page | s7a | text |
| `comic_panel2` | comic | — | top-right panel, 335x429 | int | 1 girl (close-up) | comic-page | s7a-crop | text, derived |
| `comic_panel3` | comic | — | middle panel, 1161x460 | int | 2 adults | comic-page | s7a-crop | text, derived |
| `comic_panel4` | comic | — | bottom panel, 1249x904 | int | 6+ children | comic-page, classroom | s7a-crop | derived |
| `coraline1` | stop-motion | — | puppet on a **transparent** ground — reaches the model as black, see gotchas | none | 1 girl (puppet) | coraline | s7a | franchise, corr |
| `coraline2` | stop-motion | — | film still | int | 2 puppets (girl + adult woman, button eyes) | coraline | s7a | text, franchise |
| `destroyer_drawing` | print | technical plate | halftone recognition plate, line and wash | none | none | destroyer | s7a | text |
| `destroyer_photo` | photograph | archival | — | ext | a few tiny indistinct crew | destroyer | s7a | text |
| `door_first` | live-action film | modern | **first frame** — door shut, corridor empty | int | **none** | door, first-last | s8 | text |
| `door_last` | live-action film | modern | **last frame** — same door open, room and man revealed | int | 1 adult man | door, first-last | s8 | text |
| `fish_pixel` | pixel art | — | flat sprite | none | none | — | s7a | — |
| `forest_autumn` | photograph | colour | — | ext | **1 tiny distant figure** | — | s6 | — |
| `forest_day` | vector | — | upper panel, 947x739 | ext | none | forest-daynight | s7b-crop | derived |
| `forest_day_night` | vector | — | **composite**, 2 stacked panels | ext | none | forest-daynight | s7b | — |
| `forest_night` | vector | — | lower panel, 947x738 | ext | none | forest-daynight | s7b-crop | derived |
| `fruitbowl` | 3D CG | product render | synthetic still life | int | none | — | s7a | text |
| `fuji` | photograph | colour | — | ext | none | — | s6 | real |
| `girl_painting` | painting | digital | oil-style, soft edges | none | 1 girl | girl-painting | s7a | text |
| `girl_painting_reference` | live-action film | modern | film still | int | 1 girl | girl-painting | s7a | real |
| `ivy_toon` | 2D cel | western toon | 90s cel animation still | int | 1 young woman, red bob | toon-era | s7b | franchise |
| `jacket` | photograph | colour | — | ext | 1 young-adult woman | jacket | s6 | — |
| `jacket2` | photograph | colour | — | ext | same woman | jacket | s6 | — |
| `kasia` | 2D cel | flat illustration | the original drawing; an anime-inspired toon idiom, leaning slightly western — **the sub-term is contested, the coarse term is not** | none | 1 girl | kasia | s6 | corr |
| `kasia_bag` | photograph | colour | AI-rendered, but **classified by presentation**, which is photographic | none | none | kasia, bag-angle | s7a | corr |
| `kasia_bag_2` | photograph | colour | as `kasia_bag`, second angle, re-render | none | none | kasia, bag-angle | s7b | corr |
| `kasia_outfit` | photograph | colour | **flat-lay**, derived from `kasia`; AI-rendered, classified by presentation | none | none | kasia | s7a | corr |
| `kasia_render` | 3D CG | character render | stylised anime character render | none | 1 girl | kasia | s7a | — |
| `kasia_swimsuit` | photograph | colour | **flat-lay**, derived from `kasia_swimsuit_worn`; AI-rendered, classified by presentation | none | none | kasia | s7a | corr |
| `kasia_swimsuit_render` | 3D CG | character render | AI render, anime idiom | ext | 1 girl (same character) | kasia | s7b | — |
| `kasia_swimsuit_worn` | 2D cel | flat illustration | the original commission | none | 1 girl (same character) | kasia | s7b | text |
| `kaypro_ii` | photograph | colour | — | none | none | — | s7a | text |
| `kiki` | 2D cel | anime | — | none | 1 girl + 1 black cat | — | s6 | franchise |
| `lincoln_photo` | photograph | archival | albumen portrait | none | 1 older adult man | lincoln | s7a | real |
| `lincoln_money` | print | engraving | banknote | none | a portrait *within an object* | lincoln | s7a | text, real |
| `marker` | drawing | marker | — | int | 1 young woman | — | s7b | text |
| `miya` | 2D cel | anime | — | ext | 1 teenage girl | — | s6 | text, franchise |
| `miyu` | pixel art | — | — | none | 1 girl (heavily occluded) + 1 shadow figure | — | s6 | franchise |
| `mountain_rain` | painting | digital | matte-painting style | ext | none | — | s6 | — |
| `newspaper` | photograph | colour | — | int | 1 adult man | — | s6 | — |
| `p1_first` | live-action film | modern | very dim | int | 1 adult man | p1 | s6 | — |
| `p1_last` | live-action film | modern | far brighter and closer | int | 1 adult man | p1 | s6 | — |
| `p2_first` | live-action film | modern | — | int | 1 girl | p2 | s6 | text |
| `p2_last` | live-action film | modern | near-identical light | int | 1 girl | p2 | s6 | text |
| `p3_first` | live-action film | modern | — | int | 1 girl | p3 | s6 | text |
| `p3_last` | live-action film | modern | near-identical | int | 1 girl | p3 | s6 | text |
| `p4_first` | live-action film | modern | heavy bokeh | ext | 1 girl + 1 adult man | p4 | s6 | — |
| `p4_last` | live-action film | modern | same bokeh | ext | 1 girl + 1 adult man | p4 | s6 | — |
| `p5_first` | live-action film | vintage Technicolor | night | ext | 1 adult man | p5 | s6 | — |
| `p5_last` | live-action film | vintage Technicolor | tighter, heavy dissolve | ext | 1 adult man (+1 ghosted) | p5 | s6 | — |
| `p6_first` | live-action film | modern | — | int | 1 girl | p6-window | s6 | corr |
| `p6_last` | live-action film | modern | same window, tighter | int | 1 girl | p6-window | s6 | corr |
| `pancakes` | photograph | colour | — | int | 1 adult man + 1 child girl | char-drift | s6 | — |
| `peter_griffin_painting` | painting | digital | flat-cartoon character rendered painterly | none | 1 adult man | peter-griffin | s7a | franchise |
| `peter_griffin_toon` | 2D cel | western toon | modern flat digital | int | 2 adult men | peter-griffin, toon-era | s7b | franchise |
| `phone` | photograph | colour | cut out on pure white | none | 1 adult woman | — | s6 | — |
| `ramen_pixel` | pixel art | — | hi-fi, shaded, anti-aliased | none | none | — | s7a | — |
| `san_fransisco_day_evening_night` | vector | — | **composite**, 3 stacked panels | ext | none | sanfran-daynight | s7b | — |
| `sanfran_day` | vector | — | 1039x487 | ext | none | sanfran-daynight | s7b-crop | derived |
| `sanfran_evening` | vector | — | 1039x487, golden sky | ext | none | sanfran-daynight | s7b-crop | derived |
| `sanfran_night` | vector | — | 1039x487 | ext | none | sanfran-daynight | s7b-crop | derived |
| `shrek_cg` | 3D CG | feature animation | — | ext | 1 green ogre, close-up | — | s7b | franchise |
| `sleeping` | photograph | colour | — | int | 1 young-adult woman | — | s6 | — |
| `stage` | photograph | colour | — | int | 1 woman + ~100 audience | — | s6 | — |
| `supergirl1` | drawing | marker | copic-style on board | ext-ish (drawn panel) | 1 young woman | supergirl | s7a | text, franchise |
| `supergirl2` | drawing | sketch | **marker colour over an un-inked pencil sketch** — the colour medium is the same as `supergirl1`; only the linework differs. **Sub-term contested**, see the axis note under "Medium vocabulary" | none | same character | supergirl | s7a | text, franchise, corr |
| `teddy_taft` | photograph | archival | — | ext | 2 adult men | — | s7a | real |
| `temple_day` | painting | digital | high-key, painterly | ext | 1 young woman | temple | s7a | text |
| `temple_night` | painting | digital | low-key, same hand | ext | 1 young man | temple | s7a | text |
| `tv` | photograph | colour | — | int | 1 older-adult woman | — | s6 | — |
| `van_pixel` | pixel art | — | PC-98 style, dithered, 16-colour | ext | 1 girl | — | s7a | text |
| `vector_city` | vector | — | — | ext | none | — | s6 | — |
| `window` | live-action film | modern | tighter and blown out | int | 1 teenage girl | p6-window | s6 | corr |
| `woman_oil` | painting | oil | **traditional**, photorealist | int | 1 young woman, asleep | oil-idiom | s7b | — |
| `woody_cg` | 3D CG | feature animation | early CG | int | 1 male doll/figure | — | s7b | franchise |

---

## Contents table — what is in the frame

| image | setting | prominent objects | notable garments |
|---|---|---|---|
| `annie1` | no environment, cream paper ground | (none) | **girl**: coral open jacket, yellow tank, black skirt, black knee boots, choker · **hero**: black/red tunic w/ yellow bar fasteners, black cape, black glove, domino mask |
| `annie2` | **nested** — inside the drawing, a giant reptilian creature looming over a small girl; outside it, a defocused convention hall w/ black grid shelving | the sketchbook itself | coral jacket, pale yellow top, black shorts, choker, white socks |
| `annie2_cropped` | the painted page only — the creature and the girl, ink line over watercolour wash on textured paper | (none) | as `annie2` |
| `annie3` | alley between buildings; rooftop/street | (none) | **girl**: coral coat, tan top, black skirt, choker · **boy hero**: red/black tunic w/ yellow bars, black cape · **woman hero**: black/purple suit, yellow gloves and boots · **man**: tan shirt, striped trousers |
| `annie3_panel1` | alley, girl near-full-figure | (none) | as `annie3` |
| `ayanami_oil` | tiled washroom or pool edge; pale green tiles, dark floor tiles, green ledge | (none) | pale school swimsuit |
| `azumanga_anime` | no environment, white ground | (none) | coral sailor-style school jumpers, white collars, dark red pleated skirts, orange socks / white socks + brown loafers |
| `azumanga_toon` | school grounds; chain-link fence, clipped hedges, trees, grass, concrete path, brick edging, outline clouds | (none) | same coral uniforms; one w/ black over-knee socks |
| `bird_vector` | no environment, white | (none) | — |
| `bird_watercolor` | no environment, paper ground | branch | — |
| `bookshop` | Paris-style bookshop frontage from the pavement; shop interior through the open door | tiered book displays, ceiling strip lights (on), downpipe, vent grille, doormat | black sweater, dark jeans |
| `cannon` | stone-walled terrace/battery over woodland; limestone rubble walls, pale flagstones | **muzzle-loading cannon on a four-wheeled wooden carriage** | — |
| `captain` | deck of a sailing yacht at sea, clear sky | **ship's wheel** (large, varnished), boom, furled sail, rigging, blocks, guardrail | **captain's uniform**: white peaked cap w/ gold emblem, navy double-breasted jacket, 4 cuff stripes, ribbon bar |
| `car_1` | no environment, white | **white crossover SUV, front three-quarter**; roof rails, black wheel arches, maker emblem | — |
| `car_2` | no environment, white | **the same SUV, pure side view** — identical vehicle, lighting, ground and background | — |
| `car_interior_mecha_driver` | van/MPV cabin; city skyline through the windows | steering wheel, headrests, roof vent, **magazine w/ Japanese cover text** | school sailor uniform w/ blue neckerchief |
| `car_interior_photo` | front cabin of a modern electric car | steering wheel w/ **maker emblem**, large landscape touchscreen showing a map, wood dash trim, centre console | — |
| `car_interior_sketch` | car cabin, windows blown out white | steering wheel, headrest, seatbelt | olive short-sleeve shirt; pink tee |
| `castle` | castle grounds; round crenellated tower, curtain wall, cloudy sky | pennant flag, arrow-slit, partial wooden shield edge | **plate armour**: pauldrons, engraved cuirass, gorget, mail sleeves, gauntlets, brown belt |
| `chair` | no environment, pure white | **executive office chair**: black ribbed leather, gold-tone arms and five-star base, castors | — |
| `chips_hotdog_dr_pepper_painting` | painted backdrop and tabletop | **chip bag, glass soda bottle, hot dog in a bun, loose chips** — all w/ **painted brand text** | — |
| `city_day` | **downtown skyline from above**, daylight, blue sky w/ cirrus; glass and masonry towers, a gold curtain-wall tower, a stepped-crown tower, low-rise grid, distant treeline | rooftop antennas, **rooftop brand signage**, construction scaffolding | — |
| `city_night` | **same skyline, same camera position**, blue hour; orange horizon glow, lit windows throughout | same towers; **illuminated signs and a lit crown** now readable, low-rise detail lost | — |
| `classroom1` | bright modern classroom; cream walls, curtained window | light-wood desks, storage cabinet, world-map bulletin board, open books, orange pencils | blue/white striped shirts, red neckties, navy pleated skirts |
| `classroom2` | older classroom; orange-yellow walls, tall windows | wooden desks, potted plant on sill, blue hardback, blue pencils, framed poster | navy waistcoats, white shirts, striped ties; houndstooth shirt-dress |
| `cloud` | grassy plain under towering cumulus; dirt track, distant blue hills, contrail | wooden fence, small white utility building | — |
| `comic` | classroom; desks, whiteboard w/ geometry diagram, windows, planter boxes | pencil, spider, papers, backpack | black/red/white school uniforms w/ ties; grey blazer; red/black armoured super-suit |
| `comic_panel2` | close-up, classroom behind | (none) | school uniform |
| `comic_panel3` | **same room as `comic_panel4`**; whiteboard | dialogue balloon | grey blazer |
| `comic_panel4` | classroom interior; desks, windows, planter boxes | desks, papers | school uniforms w/ ties |
| `coraline1` | no environment — **transparent ground**, which the model receives as black, not white | forked twig | yellow raincoat, blue jeans, yellow wellingtons, dragonfly hair clip |
| `coraline2` | dim kitchen; sash window, panelled cabinets, deep sink, tiled splashback, round table | open laptop, **mug reading "I love Mulch"**, notebook, pen, a doll | yellow raincoat; grey knitted cardigan |
| `destroyer_drawing` | no environment | side elevation + plan view of a warship, range scale, rising-sun emblem | — |
| `destroyer_photo` | warship at anchor, calm water, blank pale sky, distant masts | twin funnels making smoke, turrets, torpedo tubes, bridge tower, ensign; **kana + "19" on the hull** | — |
| `door_first` | dim tenement corridor; vertically striped patterned wallpaper, painted timber frames; a green panelled door **numbered 410**, shut but standing a hand's width proud of its frame with a lit gap at the hinge side | brass doorknob, a small placard on the left wall, a glazed inner door at right with dirty glass and a diagonal strap across it, partial lettering low right | — |
| `door_last` | **the same corridor, the 410 door now standing open** onto the room beyond: arched window with pale curtains, wooden chair, papers on a low table | dark travelling case being lifted, same brass knob, same glazed door and lettering at right | black overcoat, dark knit cap, white t-shirt |
| `fish_pixel` | no environment, dark banded ground | side-on fish, teal-green back, white belly | — |
| `forest_autumn` | **beech forest in fog**, autumn; grey trunks, rust foliage, deep leaf litter, exposed roots, dirt path | (none) | — |
| `forest_day` / `forest_night` | one forest clearing backed by broadleaf trees and low scrub; grass foreground, distant hills | (none) | — |
| `forest_day_night` | the two panels above, stacked | (none) | — |
| `fruitbowl` | plain warm backdrop, wood tabletop | dark ceramic bowl of fruit (green apple, 2 red apples, grapes, 2 bananas), **2 wine bottles w/ illegible script labels**, 1 loose apple | — |
| `fuji` | **thatched village by a pond, snow-capped volcano behind**; topiary, azaleas, clipped hedge, conifers, deep blue sky | thatched roofs, **water wheel**, stone lantern | — |
| `girl_painting` | no environment, grey painterly ground | (none) | black choker, pale knit |
| `girl_painting_reference` | plain grey-green wall | (none) | black velvet choker, lilac knit |
| `ivy_toon` | blue technological interior; circuit-trace wall panels, yellow door frame | **a white and grey handheld device on a chain** | brown leather jacket, white top, khaki trousers |
| `jacket` | **snowy park** — bare trees, falling snow, snow-covered ground | (none) | **grey quilted puffer jacket** w/ hood |
| `jacket2` | **same snowy park**, seated on a bench; near-featureless snow field behind | **wrought-iron bench** (scrollwork), brown leather handbag | same grey puffer jacket, **fur-trimmed mittens** |
| `kasia` | no environment, plain pale-grey backdrop | **orange shoulder bag** w/ blue strap + **3 pin badges** | black tank, denim cuffed shorts, fingerless gloves, striped knee socks, blue sneakers, **orange** headband |
| `kasia_bag` | no environment, white | **yellow shoulder bag, blue flap w/ pale-blue circular emblem, navy webbing strap, gold slider** — no pin badges | — |
| `kasia_bag_2` | no environment, white | **the same bag upright, three-quarter front**; strap looped over the top | — |
| `kasia_outfit` | no environment, white | — | **black vest top, cuffed blue denim shorts, black/blue fingerless gloves, black-and-grey striped knee socks, blue lace-up sneakers** |
| `kasia_render` | no environment, white studio ground | (none) | black vest top, cuffed denim shorts, black fingerless gloves, grey striped knee socks, navy/white sneakers, **gold-yellow headband** |
| `kasia_swimsuit` | no environment, white | — | **black high-neck one-piece swimsuit, yellow collar and yellow chevron** |
| `kasia_swimsuit_render` | poolside; clipped hedge, handrails, pale coping, blue water | handrails | **the same swimsuit**, worn |
| `kasia_swimsuit_worn` | no environment, stylised water-pattern band on white | (none) | **the same swimsuit**, worn (character: black bob, **yellow** headband, green eyes, freckles) |
| `kaypro_ii` | no environment, white | **vintage portable computer**: blue/grey metal case, green CRT showing text, 2 floppy drives, detached keyboard w/ blue keypad · **brand name on case AND on screen** | — |
| `kiki` | no environment; floating props | **6–7 breads/pastries** (loaf, baguette, rolls, filled bun) | navy long-sleeve top, red bow headband |
| `lincoln_photo` | no environment, plain studio backdrop | (none) | dark frock coat, white shirt, black bow tie |
| `lincoln_money` | no environment | five-dollar certificate: portrait vignette, guilloche borders, blue treasury seal, serials, signatures — **almost entirely printed text** | — |
| `marker` | window with blue sky and clouds behind her; drawn board border | window | off-shoulder cable-knit top, dark high-waisted pleated skirt, black ribbon choker, hoop earrings, hair ribbons |
| `miya` | winter hillside road/lookout above a valley town; guardrail, bare trees, snow | guardrail, small trash bin, power pylons | cream double-breasted coat, black fur collar, grey pleated skirt, brown backpack, **cream headphones** |
| `miyu` | no environment, black void; ground litter only | **wheelie bin** (recycling pictograms, lid open), scattered leaves | not readable (occluded) |
| `mountain_rain` | **alpine panorama in driving rain**; snow-capped range, mossy rock ledge, conifers, alpine flowers, snow patches, dead trunk | (none) | — |
| `newspaper` | bright minimal living room; cream walls, built-in white shelving | **folded broadsheet newspaper**, books, oatmeal armchair | navy shirt, dark trousers, black belt |
| `p1_first` | shabby apartment room, ochre distempered walls, very dim | **transistor radio**, handgun, corduroy couch, leather armchair, pole-mounted shelf + lamp, folding side table, tin ashtray | black top, shoulder-holster straps, round sunglasses |
| `p1_last` | same room, far brighter and closer | same radio, shelf, framed item | same |
| `p2_first` | shabby kitchen; yellow cabinets, maroon splashback, lace-curtained window | disassembled handguns, cloth, 2 solvent bottles, green dish rack, sink+tap, paper-towel roll, **box w/ brand text** | sage sleeveless waistcoat over white vest |
| `p2_last` | same kitchen, near-identical light | same | same |
| `p3_first` | dining room; ivory raised-panel wainscot, dark polished table | **cereal box w/ large brand text** (green lettering), milk carton, pink milkshake glass, cut-glass fruit bowl, floral bowl + spoon, woven placemat | grey/white striped pyjama shirt |
| `p3_last` | same room, near-identical | same | same |
| `p4_first` | city street, **background almost entirely defocused**, blown white sky | **leather case w/ brass latches**, second black case, potted houseplant, paper bag, blurred bus | olive bomber jacket, green/striped dress, choker; long dark overcoat |
| `p4_last` | same street, same bokeh | same | same |
| `p5_first` | studio-backlot city street **at night**; granite building corner, masonry apartments, lit windows | **1950s cars** (black sedan, red/white taxi), terracotta potted shrub, wooden double doors, stone kerb | black suit, white shirt, black tie, pocket square, **fedora**, **roller skates** |
| `p5_last` | same corner, tighter, heavy dissolve/superimposition of a second figure | same | same |
| `p6_first` | room with a **window** (not a doorway); peeling green-cream window frames, **exposed red brick** and a blue panel seen outside through it | 2 framed pictures, curtain, wooden floor | striped knit top, black choker w/ sun pendant, knee socks |
| `p6_last` | same window, tighter | same brick, frames | same |
| `pancakes` | modern kitchen; white tiled splashback, gas hob, extractor | **frying pan + pancakes**, spatula, grey plate of pancakes, whisk, wall control panel | white t-shirt, blue trousers; white floral pyjamas |
| `peter_griffin_painting` | no environment, dark olive gradient | (none) | white collared shirt |
| `peter_griffin_toon` | office; desk, wall poster, framed wall chart, dark carpet | desktop monitor, keyboard, mouse, phone | white shirt w/ black belt, green trousers, brown shoes; blue polo |
| `phone` | studio white, no environment | **smartphone w/ teal bumper** | sleeveless blue knit top |
| `ramen_pixel` | no environment, dark ground w/ drop shadow | **bowl of ramen**: noodles, sliced pork, halved soft egg, spring onion, bamboo shoot, steam | — |
| `sanfran_day` / `sanfran_evening` / `sanfran_night` | grass bank and conifers, a red suspension bridge at left, a white high-rise cluster at right, water across the foreground | (none) | — |
| `san_fransisco_day_evening_night` | the three panels above, stacked | (none) | — |
| `shrek_cg` | open sky, wispy cloud, dry grass at right | (none) | brown leather-look tunic, cream undershirt w/ lacing |
| `sleeping` | bedroom; grey tweed upholstered bed frame, white linen, light-wood bedside table | **black-framed eyeglasses**, pillows, duvet | navy top |
| `stage` | **grand theatre auditorium** — two gilded balcony tiers, plaster cartouches, globe lights, red velvet seating, red aisle, stage floor | stage lighting units, recessed downlights, tiered seating | blue sleeveless dress, blue heels |
| `supergirl1` | sky and stylised clouds inside a drawn panel on white board | (none) | white crop tee w/ red-and-yellow chest emblem, blue skirt, red cape, white gloves, red boots, blue headband |
| `supergirl2` | no environment, white | (none) | same costume |
| `teddy_taft` | portico/doorway; wet stone step, glazed door, fluted column | (none) | dark overcoats, waistcoat, watch chain, boutonniere, pince-nez |
| `temple_day` | gothic ecclesiastical exterior in bright sun; twin-lancet traceried window, columns, balustraded stair rising, spire beyond, potted agaves, trailing greenery, doves | (none) | strapless cream gown, pale green sash, hair ribbon |
| `temple_night` | **the same architecture, ruined and dark**: same window and tracery, same stair now broken, rubble, fallen beams, torn red banner, dim violet sky | (none) | cream tunic, brown trousers, tall boots, red cape w/ fur collar, belt; **holding a sword** |
| `tv` | domestic living room; damask wallpaper, dark wood TV stand | **CRT television** (off), DVD/VCR player, cables | navy botanical-print blouse, dark trousers |
| `van_pixel` | roadside; trees, orange-red sky | **blue MPV/van**, front three-quarter, roof rack + luggage, **licence plate** | blue and white outfit, cap |
| `vector_city` | stylised skyline of angular towers in coral and grey, reflected in water; teal sky, stylised clouds, sun flare | foreground rocks | — |
| `window` | **the same window as `p6`**, shot tighter and blown out — environment essentially unreadable | (none legible) | striped knit top, choker w/ pendant, knee socks, stuffed toy |
| `woman_oil` | dark room; black wall, dark bench or piano stool, white drape at right | dark bench/stool w/ visible hinge, crumpled white cloth | cream puff-sleeved blouse, dark skirt |
| `woody_cg` | dim room, brown/ochre ground, indistinct | **holster on the belt**, sheriff badge | yellow check shirt, cow-print waistcoat, blue jeans, brown boots w/ spurs, brown hat |

---

## Probe pairs & sets

Merged from the three per-session pair lists. **Tier** says how much of a control it is:
`exact` = nothing varies but the one thing under test · `tight` · `loose` = same idea, much
else redrawn. Use the top for regression, the bottom for coverage.

**`p1`–`p6` and `door` are first-and-last frames of a single shot** — `*_first` is the opening
frame and `*_last` the closing frame of the same continuous take. That is why they exist: they
were sourced as **FL2VA fixtures**, not as same-place pairs. It was never written down before
session 8, and it changes how they should be read:

- **`setting` and `character` use them as same-place / same-person pairs**, which ignores the
  ordering. A disagreement is drift.
- **The frame describer and the FL2VA delta use them as before/after**, which depends on it
  entirely. A disagreement may be the *content* of the shot rather than a defect — that is the
  whole point of a delta.

So the same pair is a stability probe for one role and a change probe for another. Check which
you are running before scoring anything.

| set | files | holds constant | role | tier |
|---|---|---|---|---|
| girl-painting | `girl_painting_reference` → `girl_painting` | **everything** — the painting was made *from* that still: same subject, pose, crop, framing, expression | style | **exact.** The only true control; any content difference is a defect |
| car-angle | `car_1` / `car_2` | one object, two angles — same medium, lighting, ground, background. **Nothing varies but viewpoint** | object | **exact.** The object-viewpoint control |
| city-daynight | `city_day` / `city_night` | same skyline, same camera, **day vs blue hour** | setting | **the atmosphere-quarantine bar.** See the confound note below |
| p2 | `p2_first` / `p2_last` | same kitchen, near-identical light and framing | setting | tight — the clean control |
| p3 | `p3_first` / `p3_last` | same dining room, near-identical | setting | tight — second clean control |
| forest-daynight | `forest_day` / `forest_night` | one vector scene, relit, **signage-free** | setting | tight, but *easier* than `city-*` — see below |
| sanfran-daynight | `sanfran_day` / `_evening` / `_night` | one scene, **three** lighting states | setting | tight; the only series rather than pair |
| supergirl | `supergirl1` / `supergirl2` | same character, costume, near-identical flying pose; marker board vs rough pencil | style | very tight |
| lincoln | `lincoln_photo` / `lincoln_money` | same face, same era; albumen photograph vs line engraving | style, character | tight — an object *containing* a portrait, so `[[SUBJECT_KIND]]` is a live question |
| destroyer | `destroyer_photo` / `destroyer_drawing` | same warship class; archival photo vs technical plate | style, object | tight, and **the only media pair with no person in it** |
| p6-window | `window` + `p6_first` + `p6_last` | one window, **three** framings and exposures | setting | tight — the widest same-place spread. **Reframing costs more than relighting**; this pair agrees less well than `city-*` |
| p1 | `p1_first` / `p1_last` | same room, very different exposure | setting | secondary atmosphere probe (exposure, not time of day) |
| door | `door_first` / `door_last` | same corridor and door; **shut and empty → open, with a room and a man revealed** | frame describer, FL2VA delta | **the corpus's largest single-shot change**, and its most useful failure case — see below |
| kasia (swimsuit) | `kasia_swimsuit` → `_worn` / `_render` | one garment: flat, worn in 2D, worn in 3D | object, character | flat-to-worn; the flat-lay is *derived* from the 2D image, so not independent evidence |
| kasia (everyday) | `kasia_outfit` → `kasia_render` / `kasia` | flat-lay garments ↔ worn | object | same derivation caveat |
| bag-angle | `kasia_bag` / `kasia_bag_2` | one object, two angles, two renders | object | harder than `car-angle` — an AI re-render, strap arranged differently |
| peter-griffin | `peter_griffin_painting` / `peter_griffin_toon` | one character: canonical flat toon vs painterly | style | tests franchise recognition **without a label** |
| oil-idiom | `ayanami_oil` / `woman_oil` | oil idiom, **digital vs traditional** | style | fine `[[MEDIUM]]` discrimination |
| toon-era | `ivy_toon` / `peter_griffin_toon` | `2D cel / western toon`, **90s cel vs modern flat digital** | style | fine discrimination *below* the sub-term — nothing in the vocabulary separates these two |
| azumanga | `azumanga_anime` / `azumanga_toon` | same 3 characters, same uniforms; flat anime cel vs western TV-toon | style | loose, and a **fine** discrimination — both are flat 2D |
| coraline | `coraline1` / `coraline2` | same character; puppet on white vs film still | style, character | loose; doubles as isolated-subject vs in-scene |
| bird | `bird_vector` / `bird_watercolor` | a blue-and-orange bird | style | loose — not the same bird, the same *idea* of one |
| annie | `annie1` / `annie2_cropped` / `annie3_panel1` | one character across **three** media: marker sketch, watercolour, comic | style, character | loose, widest spread. **Requires a `SUBJECT:` line** — see below |
| car-interior | `car_interior_photo` / `_sketch` / `_mecha_driver` | one setting *type* across three media | setting | loosest — different vehicles |
| p4 | `p4_first` / `p4_last` | same street, both heavy bokeh | setting | low-information stress case |
| jacket | `jacket` / `jacket2` | same snowy park, same woman, same puffer jacket | character, object, setting | **weak for setting** — the snow is near-featureless, so durable content is thin by nature. Solid as the garment/identity pair |
| temple | `temple_day` / `temple_night` | same architecture, signage-free, **but ruined in one** | setting | **negative control** — the place really did change; see below |
| classroom | `classroom1` vs `classroom2` (+ `comic_panel4`) | *different* rooms of the same type | setting | **negative control** — must NOT collapse into one record. `comic_panel4` is a third, in a non-photographic medium |
| comic-page | `comic_panel3` / `comic_panel4` | same room, two panels, one comic medium | setting | the only same-place pair inside a drawn medium |
| comic-page | `comic_panel2` / `comic_panel4` | same girl, two framings, one medium | character | the comic analogue of the `p6` wide/close pair. **Her name is printed in the balloon** — the harshest no-name probe we have |
| char-drift | `pancakes` × several `SUBJECT:` wordings | **the image itself** — isolates prompt-side instability with image variation removed | character | produced byte-identical `[[APPEARANCE]]` lines; read this before any cross-image probe |
| setting-boundary | `bookshop` | camera outside, interior visible through the glass | setting | `[[SETTING_KIND]]` boundary case — correct in every round so far |

### Notes attached to specific pairs

**`city_day`/`city_night` carries a signage confound.** The skyline has rooftop bank logos and a
large neon hotel sign. Night lights those up and hides low-rise detail, so a `[[DEFINITION]]`
disagreement has two possible causes — atmosphere leaking into the durable fields, or the model
naming an illuminated sign it could not read by day. Check which before scoring. It is also the
strictest printed-text/brand probe in the corpus.

**The vector day/night pairs close the gap but are an *easier* test.** `forest_*` and `sanfran_*`
deliver "same camera, same place, same structure, relit only" perfectly — one piece of vector
artwork recoloured, zero photographic variation, zero signage. But the failure mode session 6
diagnosed was that **by day the model describes forms and by night it describes lights**, and that
happens because a real night photograph genuinely destroys information: the low-rise detail in
`city_night` is simply gone. **In a vector illustration nothing is destroyed.** A describer can
pass these comfortably while still failing `city_*`. Use them as the *diagnostic* (a failure is
unambiguous); keep `city_*` as the *bar*.

**`temple_day`/`temple_night` is a split diptych, not two photographs.** The user found one
artwork with the ruined/night/male half on the left and the intact/day/female half on the right,
split it down the middle and **mirrored one half** so the architecture aligns. Three consequences:
it is genuinely signage-free, which is what the gap asked for; it is **not** a clean atmosphere
control, because the building is intact in one and ruined in the other and ruin is *structural*,
so `[[DEFINITION]]` divergence is partly legitimate; and because one half was mirrored, any
left/right language in `[[STRUCTURE]]` will conflict across the pair — `setting` has no POSITION
field so this is mostly harmless, but do not read "stair rising to the right" vs "to the left" as
drift. What it *is* good for, and this is not a consolation prize: a **"same place, different
condition"** probe where the durable record *should* partly disagree. The natural negative control
for the day-and-night test.

**The annie ladder needs a `SUBJECT:` line.** `annie1` and `annie3_panel1` each contain the girl
*and* at least one costumed hero; only `annie2_cropped` has her alone. Cast across the three media
without disambiguation and the describer may legitimately record a different person in each, which
would read as catastrophic identity drift and would be nothing of the kind. Use the cropped and
panelled versions for content roles — raw `annie2` drags in a convention hall, raw `annie3` is four
scenes at once.

---

## Corrections & superseded findings

Every content error found so far, kept because each one would have changed a test verdict.
**`validate.py` cannot see any of this** — a record naming the wrong person is perfectly
well-formed and passes every structural check.

| claim | what we first recorded | what is actually true | how it surfaced | why it matters |
|---|---|---|---|---|
| `window` is its own location | catalogued as an unrelated room; `p6` described as showing a *doorway* | `p6` shows a **window**, and it is the **same window** as `window.png` | user correction, session 6 | turns two unrelated images into the corpus's largest same-place set (three framings) |
| `annie1` / `annie3` cast | "1 girl, drawn twice — as herself and as a masked hero" | the masked figure is a **separate recurring character**; `annie3` has **four** distinct people | user correction, session 7a | **would have inverted a test verdict** — a describer correctly keeping them as two people would have scored as a failure |
| `kasia_swimsuit` set membership | "not part of the kasia set — nothing visual ties it to the character, only the filename" | it **is** — `kasia_swimsuit_worn` is the original commission the flat-lay derives from | second batch arrived, session 7b | closes the second-flat-to-worn-garment gap; also the source of the general lesson below |
| kasia headband hue | `kasia.png` treated as the reference, the renders as drifting | `kasia.png` is the **outlier** — three files agree on yellow, only the original is orange (hue 28–34°) | measured, then re-framed in 7b | a describer saying "orange" for `kasia.png` is right about *that image* while wrong about *the character* |
| session-6 medium tally | "16 live-action photographic" | 17 — the list under it named 17 | arithmetic, session 7a | it is what makes the session-6 total 37 |
| medium tallies vs crops | the 74-file tally excluded comic-panel crops from "comic page" but **included** `annie2_cropped` in "watercolour" | crops are files and count everywhere | recount, session 8 | the reason the tally is now generated rather than hand-maintained |
| "no medium is a singleton any more" (7b) | asserted after oil / western toon / marker board each reached 2+ | **false** — `destroyer_drawing` and `lincoln_money` were singletons before that batch and still are | recount, session 8 | under the two-level vocabulary these are `print / technical plate` and `print / engraving`, one sample each. No *coarse* term is a singleton; those two *sub*-terms are. Do not treat a `style` result on either as replicated |
| `car_1` / `car_2` medium | classified `3D CG / product render` from appearance | `photograph` — automaker press shots, per the user's provenance. **But not visually determinable** | user correction, session 8 | shifted live-action 39%→42%, and established the **`amb` category**: ground truth taken from provenance rather than appearance is not a fair test of a describer |
| `supergirl2` medium | `drawing / sketch`, described as "coloured pencil / colour sketch" | the **colour is marker, the same as `supergirl1`**; what differs is the linework, which is an un-inked pencil under-drawing. The pair differs in *finish*, not in *instrument* | user, session 9, reading both images against the style v1 and v2 rounds | the `supergirl` pair was set up as a `marker` vs `sketch` discrimination and is not one. It also exposed that the `drawing` and `painting` sub-lists mix axes — see "Medium vocabulary" |
| the four kasia flat-lay / bag files | `3D CG / product render`; briefly flagged `amb` mid-session 9 on the grounds that AI origin made photo-vs-render undeterminable | **`photograph / colour`.** All four are AI-rendered, and the user classifies them by **presentation** anyway, which is photographic | user, session 9, ruling on the full-corpus sweep | **the `amb` flag was the wrong tool here.** `amb` exists for images whose *provenance* we know and whose pixels do not match it; tie-break 4 already says to judge on presentation rather than provenance, and once that rule is applied consistently the ambiguity dissolves. It also raises whether `chair`/`car_1`/`car_2` should move the other way — the model calls all three `3D CG / product render`, which *is* the presentation read. **Unresolved, deliberately** — see the vocabulary redesign note |
| `kasia` sub-term | `flat illustration`, stated flatly | the coarse term `2D cel` is solid; the **sub-term is contested** — an anime-inspired toon idiom leaning slightly western | user, session 9, after style v1 answered `anime` | a sub-term miss here is not clearly a miss. Score the coarse term only |
| `coraline1` ground | "puppet cut out on white" | the file is a **palette PNG with a transparency key, 83.5% fully transparent**. It has no white ground; it has no ground at all. What reaches the model composites to **black** | the session-9 style round reported "pure black background" twice and was scored as a hallucination; the user identified transparency as the cause, confirmed by an alpha scan of the whole corpus | **a wrong ground truth was about to be recorded as a model defect.** It is the only genuinely transparent file in the corpus — six other files carry an alpha channel that is fully opaque, so they are inert |

**The general lesson is `L-CLAIM-ROWS-ARE-UNRELIABLE`, and it is about the inventory rather than
about kasia: a "these are
unrelated" judgement is only ever true of the corpus *as it stands*.** Two of the three content
errors caught in session 7 were of this shape — an inferred *relationship*, not a described
object. **Description rows have been reliable; claim rows have not**, and claim rows are the ones
that change a verdict.

---

## Coverage by role

### `setting`

**11 distinct interiors**: 2 classrooms (+ a third in `comic_panel4`), 2 kitchens, 3 living/dining
rooms, bedroom, theatre auditorium, window room, bookshop interior, office, tiled washroom.
**Plus 3 vehicle interiors** — the setting type that was entirely missing at session 6.

**Exteriors** cover shop street, ship deck, castle grounds, snowy park, snowy hillside road, modern
city street, 1950s backlot street at night, downtown skyline from above, beech forest in fog,
alpine range in rain, volcano and thatched village, grass plain under cumulus, stylised vector
skyline, school grounds, alley, stone battery, poolside, portico, gothic temple.

Weather: snow (×3), fog, rain, overcast, clear. Terrain: forest, alpine rock, grass plain, water,
and several flavours of built-up.

**No-/low-setting cases** for "not visible" behaviour: `kasia`, `kiki`, `phone`, `chair`,
`kaypro_ii`, `car_1`/`car_2` and most product renders (plain studio grounds), `miyu` (black void).

### `object`

**In-scene targets**: CRT television (`tv`), ship's wheel (`captain`), transistor radio (`p1`),
cereal box (`p3`), frying pan (`pancakes`), leather case (`p4`), wheelie bin (`miyu`), wrought-iron
bench (`jacket2`), shoulder bag (`kasia`), breads (`kiki`), newspaper (`newspaper`), eyeglasses
(`sleeping`), 1950s cars (`p5`), cannon (`cannon`), handheld device (`ivy_toon`), holster and badge
(`woody_cg`).

**Isolated shots** — the thing session 6 was short of, now well covered: `phone`, `chair`,
`kaypro_ii`, `fruitbowl`, `ramen_pixel`, `fish_pixel`, `kasia_bag`, `kasia_bag_2`, `car_1`,
`car_2`.

**Garments**: plate armour (`castle`), captain's uniform (`captain`), puffer jacket
(`jacket`/`jacket2`), fedora and roller skates (`p5`), school uniforms (`classroom1`/`classroom2`,
`azumanga`), and **two flat-to-worn pairs** (`kasia_outfit`, `kasia_swimsuit`).

### `style`

**No longer blocked.** 11 coarse media, **21 of 23 defined (coarse, sub) combinations
populated**; live-action down to 43% from 78%. Nine same-subject-across-media pairs,
one of them exact. See the tally and the pairs table.

The two vocabulary decisions this section used to flag as open are **now settled** by the
tie-break rules under "Medium vocabulary":

- **The oil case** — resolved by rule 3 (report the idiom, not the substrate). `woman_oil` is
  `painting / oil`, `ayanami_oil` is `painting / digital`. They agree at coarse level and differ
  at sub level, which is exactly what that probe pair should produce.
- **The nested-medium case** — resolved by rule 2 (report the outer medium). `annie2` is
  `photograph`, with `annie2_cropped` as the clean watercolour sample. The rule generalises to
  `tv`'s CRT and to any poster, phone screen or television in frame, which is ordinary in real use.

### The `amb` images — a category, not a defect

**Three members: `chair`, `car_1`, `car_2`** — and the category is **under review**, because
session 9 nearly doubled it and then reversed course, which is informative in itself.

The four kasia flat-lay/bag files were flagged `amb` mid-session on the grounds that their AI origin
made photo-vs-render undeterminable, then reclassified to `photograph / colour` when the user ruled
on them: **tie-break 4 already says to judge on presentation rather than provenance**, and applying
that consistently dissolves the ambiguity rather than cataloguing it.

That cuts at the remaining three too. The model called `chair`, `car_1` and `car_2`
`3D CG / product render` in every round — which *is* the presentation read. If presentation decides,
the model is right and the master table is wrong; the `amb` flag is preserving a provenance-based
answer that our own tie-break says not to use. **Unresolved deliberately** — it interacts with the
vocabulary redesign, so both get settled together rather than piecemeal. See `.claude/TODO.md`.

Note the one thing that survives regardless. `[[MEDIUM]]` may be unscorable on a file, **but two
views of one object disagreeing with each other is still a real failure** — they must land in the
same place whatever that place is. The flag suspends the answer key, not the consistency
requirement. `car_1`/`car_2` passed that; the kasia bags did not.

The original three, and the reasoning that built the category:

`chair`, `car_1` and `car_2` are studio product shots on white. The user knows their provenance —
`chair` came from an Amazon listing, `car_1`/`car_2` direct from an automaker — so they are filed
as `photograph`. **But the pixels do not settle it.** Contemporary automaker press imagery is
routinely CGI, and a clean e-commerce shot on a seamless white ground is exactly the case where a
photograph and a good product render converge. The user's own read is "probably photographs, but I
could be wrong", and that is the correct confidence level.

The consequence for testing is the point: **`[[MEDIUM]]` is unscorable on these three, in either
direction.** A describer saying `3D CG` is not wrong; a describer saying `photograph` is not right
for a reason it could have known. Scoring them either way manufactures a signal that isn't there.

That is worth having as a standing category rather than a footnote. Ground truth in this document
comes from two different places — **what is visible** and **what we happen to know** — and only the
first is a fair test. The `amb` flag marks where they diverge. `chair` and the two cars are the
current members; anything whose classification rests on provenance rather than appearance belongs
there too.

Still genuinely open, and a *prompt* question rather than a vocabulary one: whether
`describer_style` emits the sub-term unconditionally or only when confident. An optional element
that fires on judgement is the exact shape that cost `setting` three rounds — so the default
should be "always emit, with an explicit `not determinable` value available" rather than "omit
when unsure". The `amb` images are the natural test of that value.

---

## Multi-panel images — a trap to know, not to defend against

`comic` (5 panels), `annie3` (4 panels), and the two day/night composites are single files
containing several scenes; `annie2` is a photograph of a painting held in a hand. Every describer
built so far assumes one frame, one place, one moment, so `[[SETTING_KIND]]` has no correct answer
for any of them.

**Agreed approach**: crop panels for the content roles, keep the full pages for `style`, and run an
uncropped page through `setting` **once, as a diagnostic that is recorded and never patched.**

The reasoning is this project's own most expensive lesson, `L-OPTIONAL-JUDGEMENT-IS-A-LIABILITY`
(see `.claude/lessons_learned.md`). `[[SUBJECT NOT FOUND]]` cost three
rounds and caused *every* format failure in setting v1–v3 before it was deleted, and the conclusion
was that **an optional behaviour that fires on judgement is a liability unless the role genuinely
needs the judgement**. Multi-panel handling is that trap in a new costume: if a comic page produces
mush, the reflex is to add an "if the image contains multiple panels…" rule, and that rule will
cost us elsewhere the way the setting-v2 paragraph did.

Both composites are kept alongside their crops — they cost nothing, they are the provenance, and
they are a second kind of multi-panel diagnostic where the panels are the *same* scene rather than
a sequence.

---

## Printed text and real-identity pressure

**Printed text, hardest first**: `lincoln_money` (almost nothing but text) · `destroyer_drawing`
(class name, dimensions, tonnage, date) · `kaypro_ii` (brand on the case *and* rendered on the
screen) · `chips_hotdog_dr_pepper_painting` (**three** brands, hand-painted, so the text is part of
the brushwork) · `comic` / `annie3` / `comic_panel2` / `annie3_panel1` (dialogue balloons **plus a
character's name**) · `supergirl2` (hand-lettered title) · `car_interior_photo`, `car_1`, `car_2`
(maker emblem) · `car_interior_mecha_driver` (Japanese cover text) · `coraline2` (a mug slogan) ·
`van_pixel` (licence plate) · `annie1` (signature, seal, name in two scripts) · `girl_painting` (a
Weibo watermark) · `kasia_swimsuit_worn` (a commission credit) · `cloud` (artist signature and a
repeating watermark) · `miya` (printed title) · `p2`/`p3` (brand text on a box).

**Real identifiable people**: `lincoln_photo` + `lincoln_money` (the same man twice across two media
— the strongest identity probe we have), `teddy_taft` (two at once), `girl_painting_reference` (a
well-known actor, and the source of `girl_painting`). **Real place**: `fuji` — the first real test
of the no-real-place-names rule.

**Recognisable fictional characters**: coraline ×2, supergirl ×2, azumanga ×2, annie ×3 + 2 crops,
`comic`, peter_griffin ×2, `kasia`, `kiki`, `miya`, `miyu`, `ivy_toon`, `shrek_cg`, `woody_cg`,
`ayanami_oil`. Three cases are nastier than the rest:

- **`peter_griffin_painting`** — instantly recognisable but rendered in a medium the source never
  uses, so naming the franchise requires *recognition* rather than *reading a label*. With
  `peter_griffin_toon` now present, the canonical version is there for comparison.
- **`ivy_toon`, `shrek_cg`, `woody_cg`** — instantly recognisable licensed characters with **no
  text anywhere in frame**, across three more media. The no-franchise-name rule is now testable
  purely on recognition.
- **`annie1` and `annie3` mix an original character with licensed ones.** The girl is the artist's
  own; the masked hero beside her is not. A describer can therefore fail *partially* — correct and
  neutral about the girl, franchise-naming about the figure next to her — which is more realistic
  than an image where everything is licensed or nothing is.

---

## Known describer limitations this corpus exercises

- **An empty space that is about to be occupied invites invention — and `door_first` triggers it
  reliably.** That frame contains no person at all: a corridor, a shut door, a lit gap at the
  hinge. It has repeatedly produced a described person who is not there. It is the opening frame
  of a shot whose closing frame *does* contain a man, and the composition carries that prior.

  This is `L-CAPABILITY-CEILINGS`' "compound environmental reversal (empty → occupied space)"
  seen from the other side, and **`door_first` is the only reliable trigger for it in the
  corpus.** The pair was nearly deleted in session 8 as a superseded duplicate; it is kept
  precisely *because* it fails consistently. A reproducible failure is worth more than a clean
  pass — see `L-NAME-THE-CASE`, and note that `L-ONE-RUN-IS-A-SAMPLE` makes reproducible
  failures rare and valuable here.

  **Not yet run under the current describers.** The hallucination was observed during earlier
  FL2VA work, before the frame describer reached v8. Re-running it is on the TODO.
- **Dim and occluded scenes degrade object-state reading.** `miyu` (pixel art, heavily occluded)
  produced invention where "not visible" was wanted.
- **Reframing costs more than relighting.** The `p6` wide/close set agrees less well than the
  `city` day/night pair. A tighter shot simply contains less place — worth knowing before trusting
  any single frame as an environment reference.
- **Some disagreement is in the source, not the describer.** The `p4` girl is genuinely borderline
  (~12–13, on the child/pre-teen/teenager boundaries); the kasia bag differs in hue *and* pin
  badges between files. Do not chase these as prompt defects.
- **The city day/night gap may be irreducible.** The day record names gold cladding and a copper
  roof the night image genuinely does not show. That is a limit of the photograph.
- **Residual leaks accepted, not chased**: a cereal carton in `p3` survives the movable-clutter ban
  and is still described as having "green lettering" — the brand name is suppressed, the fact of
  text is not.

---

## Derived files & provenance

Gutters were detected **programmatically** (row/column runs of ≥97%-white pixels, then per-band
column analysis), not estimated by eye. All comic crops exclude the panel border rules with no
bleed from neighbours.

| crop | source | geometry | size |
|---|---|---|---|
| `comic_panel2` | `comic` top-right panel | — | 335x429 |
| `comic_panel3` | `comic` middle panel | — | 1161x460 |
| `comic_panel4` | `comic` bottom panel | — | 1249x904 |
| `annie3_panel1` | `annie3` leftmost panel | — | 428x1434 |
| `annie2_cropped` | `annie2`, hand + sketchbook edge + hall removed | — | 722x1273 |
| `forest_day` | `forest_day_night` | rows 0–739 | 947x739 |
| `forest_night` | `forest_day_night` | rows 742–1480 | 947x738 |
| `sanfran_day` | `san_fransisco_day_evening_night` | rows 0–487 | 1039x487 |
| `sanfran_evening` | same | rows 495–982 | 1039x487 |
| `sanfran_night` | same | rows 993–1480 | 1039x487 |

**The San Francisco composite has clean white gutters** (rows 487–495, 982–993). **The forest
composite has none** — the two panels butt directly and the seam was found from the row-to-row
brightness discontinuity, unambiguous at row 741 (mean brightness 102.8 → 24.7). One or two seam
rows are trimmed from each side; both crops were checked visually and carry no edge artefact.

**Panels deliberately not kept**: `comic` panel 1 (a hand and a spider — no usable setting or
subject) and `annie3` panels 2–4 (costumed figures on flat grounds; the corpus already has plenty
and they add no new probe). The crop boxes are in the session-7 handoff if any are wanted later.

**`annie2` is kept whole *and* cropped, deliberately** — the two files serve different jobs and
cannot confound each other. Uncropped is the corpus's only nested-medium case; cropped is a clean
traditional watercolour sample and the annie ladder's watercolour rung, free of the hand and hall
that would otherwise contaminate a character record.

### File-format gotchas found while reading

- **`coraline2.jpg` was not a JPEG** — an AVIF file with a `.jpg` extension. `run_tests.py`'s
  `image_payload()` maps extension to MIME with **no sniffing**, so it would have sent AVIF bytes
  labelled `image/jpeg`. Converted to `coraline2.png` (PIL, lossless re-encode of the decoded
  pixels) and the bad `.jpg` deleted. **If more images arrive from hosts that serve AVIF/WebP
  behind a `.jpg` URL, check the magic bytes before casting them.** A one-line guard in
  `image_payload()` is cheap insurance — on the TODO.
- **`cannon.JPG` was an MPO**, not a plain JPEG — a 2-frame stereo pair from a 3D camera,
  4320x3240, 6.3 MB (~8.4 MB base64, 5× the pixel count of anything else). Frame 0 extracted,
  Lanczos-resized to 2000x1500, saved as JPEG q90 → `cannon.jpg`, 0.99 MB. Visually identical. The
  original was marked read-only, which had to be cleared first.
- **`coraline1.png` is transparent, and transparency is not a neutral background.** It is a
  palette PNG carrying a `tRNS` transparency key, **83.5% fully transparent**. Viewed in most
  image tools it appears cut out on white; `run_tests.py` base64-encodes the **raw file bytes**
  and lets the server-side decoder flatten it, and that composites to **black**. A naive
  `Image.open(...).convert('RGB')` gives `(0, 0, 0)` at the corner, which is what the model
  reported.

  Two consequences worth carrying:

  1. **What we see in a viewer is not necessarily what the model receives.** Any ground-truth
     claim about a background on a transparent file is a claim about our viewer, not about the
     input. This is `L-SCORE-ONLY-WHAT-THE-INPUT-SHOWS` arriving from an unexpected direction —
     the mismatch was in the pipeline rather than in the provenance.
  2. **The corpus was scanned and `coraline1` is the only offender.** `azumanga_anime`,
     `car_interior_mecha_driver`, `car_interior_sketch`, `kiki`, `miyu` and `peter_griffin_toon`
     all carry an alpha channel whose minimum value is 255 — fully opaque, so they flatten
     identically whatever the decoder does. No earlier round is affected: no transparent file
     was in the `setting` or `character` test sets.

  Re-run the scan if images arrive from sources that ship cut-outs (product shots, sprite
  sheets, wiki renders):

  ```bash
  python -c "from PIL import Image; import pathlib; [print(p.name, Image.open(p).convert('RGBA').getchannel('A').getextrema()) for p in pathlib.Path('images').iterdir()]"
  ```

  **Left as-is rather than flattened**, pending a decision: flattening onto white would match how
  we read it, but the black ground is a legitimate input and `coraline1` is a `style` and
  `character` fixture where the ground barely matters. See `.claude/TODO.md`.
- **`teddy_taft.JPG` had an uppercase extension** — Harmless today
  (`image_payload()` should lowercase before mapping) but worth normalising.

---

## Medium tally

**Generated by `scripts/inventory.py` — do not hand-edit.** Counted over every active file,
crops included; the footnote markers below are driven by the master table's `flags` column, so
they stay attached to the right rows automatically. Run `python scripts/inventory.py` after any
change to the master table.

| medium | sub | count | images |
|---|---|---|---|
| `photograph` | | **31** | |
| | colour | 28 | annie2\*\*, bookshop, cannon, captain, car_1\*, car_2\*, car_interior_photo, castle, chair\*, city_day, city_night, classroom1, classroom2, forest_autumn, fuji, jacket, jacket2, kasia_bag, kasia_bag_2, kasia_outfit, kasia_swimsuit, kaypro_ii, newspaper, pancakes, phone, sleeping, stage, tv |
| | archival | 3 | destroyer_photo, lincoln_photo, teddy_taft |
| `live-action film` | | **16** | |
| | modern | 14 | door_first, door_last, girl_painting_reference, p1_first, p1_last, p2_first, p2_last, p3_first, p3_last, p4_first, p4_last, p6_first, p6_last, window |
| | vintage Technicolor | 2 | p5_first, p5_last |
| `3D CG` | | **5** | |
| | character render | 2 | kasia_render, kasia_swimsuit_render |
| | feature animation | 2 | shrek_cg, woody_cg |
| | product render | 1 | fruitbowl |
| `stop-motion` | — | **2** | coraline1, coraline2 |
| `2D cel` | | **9** | |
| | anime | 4 | azumanga_anime, car_interior_mecha_driver, kiki, miya |
| | western toon | 3 | azumanga_toon, ivy_toon, peter_griffin_toon |
| | flat illustration | 2 | kasia, kasia_swimsuit_worn |
| `comic` | — | **6** | annie3, annie3_panel1, comic, comic_panel2, comic_panel3, comic_panel4 |
| `painting` | | **11** | |
| | digital | 7 | ayanami_oil, cloud, girl_painting, mountain_rain, peter_griffin_painting, temple_day, temple_night |
| | oil | 2 | chips_hotdog_dr_pepper_painting, woman_oil |
| | watercolour | 2 | annie2_cropped, bird_watercolor |
| | *gouache* | *0* | *no sample* |
| `drawing` | | **5** | |
| | marker | 3 | annie1, marker, supergirl1 |
| | sketch | 2 | car_interior_sketch, supergirl2 |
| | *ink* | *0* | *no sample* |
| `vector` | — | **9** | bird_vector, forest_day, forest_day_night, forest_night, san_fransisco_day_evening_night, sanfran_day, sanfran_evening, sanfran_night, vector_city |
| `pixel art` | — | **4** | fish_pixel, miyu, ramen_pixel, van_pixel |
| `print` | | **2** | |
| | engraving | 1 | lincoln_money |
| | technical plate | 1 | destroyer_drawing |

**Total 100.** Live-action (`photograph` + `live-action film`) is **47 of 100, 47%** — down from 29/37, 78% at the start of session 7. 3 of those 47 are `amb`, so the honest range is 44–47.

\* The three `amb` files — `chair`, `car_1`, `car_2` — filed as `photograph` on provenance the
describer cannot see (an Amazon listing and an automaker press shot). The pixels do not settle it:
all three sit on a seamless white studio ground, the case where photograph, product render and AI
render converge. Do not score `[[MEDIUM]]` on them; two files of one object must still agree with
each other. **The category is under review** — the four kasia flat-lay/bag files were briefly
flagged `amb` and then reclassified `photograph` by presentation, and the same rule arguably moves
these three the other way. See "Coverage by role → style".
\*\* `annie2` is a photograph *of* a watercolour, filed by the outer medium per tie-break 2. Its
content is a drawing, so it inflates the live-action share by one.

**No coarse term is a singleton.** Three *sub*-terms are: `print / engraving`,
`print / technical plate`, and — new in session 9 — `3D CG / product render`, which dropped from
five samples to one (`fruitbowl`) when the four kasia flat-lay/bag files were reclassified as
`photograph`. The two `print` terms are single-sample because those media are genuinely rare in
practice; `product render` is single-sample because our examples of it turned out to be something
else. A `style` result on any of the three is unreplicated.

**Two defined sub-terms have no sample at all**: `painting / gouache` and `drawing / ink`. Same
situation as the character describer's untested age brackets — the vocabulary offers a term the
corpus cannot exercise, which is fine, but a describer emitting one of them cannot be checked
against anything.

---

## Standing gaps

**Nothing blocking.** Every gap raised in sessions 6 and 7 has been closed. What remains is
preference rather than obstruction:

1. **A day/night pair that is both photographic *and* signage-free.** `city_*` is photographic
   with signage; `forest_*`/`sanfran_*` are signage-free without photography. Between them the two
   isolate every variable — just not in one image. This is a refinement, not a blocker.
2. **More live-action breadth**, if `style` turns out to need it. 43% is healthy, but the
   photographic images skew heavily toward people and rooms.
3. **A second sample for the two singleton media**, if either ever matters to a `style` verdict.
