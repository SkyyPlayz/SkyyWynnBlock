"""Derive SkyySacks/build_skyysacks_0.6.7.py from 0.6.6.
0.6.7 (Skyy): life essence belongs to Farming; new COMBAT bag for mob drops.
 - Farming now also takes every Ingredient_Life_Essence* item (plain, concentrated, crop-specific) and Ingredient_Poop (fertilizer).
 - Combat (new category): bones, hides, chitin, venom sacs, feathers, fabric scraps, voidhearts, boom powder, and every elemental
   essence (Fire/Ice/Void/Lightning _Essence, not Life). Item list taken from the game's NPC drop tables (Server/Drops/NPCs).
   Raw meat stays Farming (Hypixel counts meat as farming); arrows are never pooled (bows need them in the inventory).
 - Combat bags Small/Medium/Large (recipe: 3 wool bolts + 4 bone fragments, then linen, then silk like the other bags), right-click page
   SkyySacksCombat, tab on the bag page (tabs narrowed to fit four).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.6.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.7.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
BS = chr(92)
Q = BS + BS + '"'


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    s = s.replace(old, new, count)


rep('VERSION = "0.6.6"', 'VERSION = "0.6.7"')
s = s.replace('"""SkyySacks 0.6.6', '"""SkyySacks 0.6.7' + LF + '0.6.7: life essence -> Farming; new Combat bag for mob drops.' + LF, 1)

rep('public static final String[] CATS = new String[] { "Mining", "Foraging", "Farming" };',
    'public static final String[] CATS = new String[] { "Mining", "Foraging", "Farming", "Combat" };')
rep('  if (itemId.startsWith("Plant_") || itemId.startsWith("Food_") || itemId.startsWith("Fish_")) return "Farming";',
    LF.join([
        '  if (itemId.startsWith("Plant_") || itemId.startsWith("Food_") || itemId.startsWith("Fish_")) return "Farming";',
        '  if (itemId.startsWith("Ingredient_Life_Essence") || itemId.equals("Ingredient_Poop")) return "Farming";',
        '  if (itemId.startsWith("Ingredient_Bone") || itemId.startsWith("Ingredient_Hide_") || itemId.startsWith("Ingredient_Chitin")',
        '      || itemId.startsWith("Ingredient_Sac_") || itemId.startsWith("Ingredient_Feathers") || itemId.startsWith("Ingredient_Fabric_Scrap_")',
        '      || itemId.equals("Ingredient_Voidheart") || itemId.equals("Ingredient_Powder_Boom")',
        '      || (itemId.startsWith("Ingredient_") && itemId.endsWith("_Essence"))) return "Combat";',
    ]))
rep('  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksFarming", new {PKG}.SacksPageFactory("Farming"));',
    '  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksFarming", new {PKG}.SacksPageFactory("Farming"));' + LF +
    '  {OCU}.registerSimple(this, {PKG}.SkyySacksPlugin.class, "SkyySacksCombat", new {PKG}.SacksPageFactory("Combat"));')
# bag page: four tabs must fit (900 wide page)
rep('" {{ Anchor: (Width: 175, Height: 36); Text: ' + Q + '" + cats[c]', '" {{ Anchor: (Width: 150, Height: 36); Text: ' + Q + '" + cats[c]')
rep('Craft a Mining or Foraging or Farming bag at a workbench.', 'Craft a Mining, Foraging, Farming or Combat bag at a workbench.')
# items + lang
rep('mats = {"Mining": "Ingredient_Bar_Copper", "Foraging": "Wood_Oak_Trunk", "Farming": "Food_Bread"}',
    'mats = {"Mining": "Ingredient_Bar_Copper", "Foraging": "Wood_Oak_Trunk", "Farming": "Food_Bread", "Combat": "Ingredient_Bone_Fragment"}')
rep('for cat in ("Mining", "Foraging", "Farming"):', 'for cat in ("Mining", "Foraging", "Farming", "Combat"):')
rep('"Farming": "plants, food and fish"}[cat]',
    '"Farming": "plants, food, fish and life essence", "Combat": "bones, hides, feathers, essences, venom sacs, chitin and fabric scraps"}[cat]')

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
