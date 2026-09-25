"""Generate Dutch names for flavored artisan goods (wine, jam, juice, pickles, honey, dried fruit, roe, bait,
smoked fish) per ingredient, as Strings/Objects:<Type>_Flavored_(O)<id>_Name entries for the polish layer.

The game looks these keys up before falling back to <Type>_Flavored_Name (which gets {0} = display name and
{1} = lowercase display name). A generated compound follows Dutch spelling (aardbeienjam, zalmkuit,
tilapia-aas); multi-word ingredients get a phrase instead (Wijn van wilde pruimen).

usage: flavored.py            (writes the batch and applies it to the polish layer)
"""
import os

from apply import apply as apply_batch
from objdata import objects
from paths import SOURCE, save_json

# fruit: compound stem, dried name
FRUIT = {
    "88": ("kokos", "Gedroogde kokos"), "90": ("cactusvrucht", "Gedroogde cactusvruchten"),
    "252": ("rabarber", "Gedroogde rabarber"), "254": ("meloen", "Gedroogde meloen"),
    "258": ("bosbessen", "Gedroogde bosbessen"), "260": ("chilipeper", "Gedroogde chilipepers"),
    "268": ("stervrucht", "Gedroogde stervruchten"), "282": ("veenbessen", "Gedroogde veenbessen"),
    "296": ("zalmbessen", "Gedroogde zalmbessen"), "396": ("kruidenbessen", "Gedroogde kruidenbessen"),
    "398": ("druiven", "Gedroogde druiven"), "400": ("aardbeien", "Gedroogde aardbeien"),
    "406": (None, "Gedroogde wilde pruimen"), "410": ("bramen", "Gedroogde bramen"),
    "414": ("kristalvrucht", "Gedroogde kristalvruchten"), "454": (None, "Gedroogd oeroud fruit"),
    "613": ("appel", "Gedroogde appel"), "634": ("abrikozen", "Gedroogde abrikozen"),
    "635": ("sinaasappel", "Gedroogde sinaasappel"), "636": ("perzik", "Gedroogde perziken"),
    "637": ("granaatappel", "Gedroogde granaatappel"), "638": ("kersen", "Gedroogde kersen"),
    "91": ("bananen", "Gedroogde banaan"), "832": ("ananas", "Gedroogde ananas"),
    "834": ("mango", "Gedroogde mango"), "889": ("Qi-vrucht", "Gedroogde Qi-vrucht"),
    "Powdermelon": ("poedermeloen", "Gedroogde poedermeloen"),
}
FRUIT_PHRASE = {"406": "wilde pruimen", "454": "oeroud fruit"}

# vegetables and forage greens: juice stem (None = phrase), pickled name
VEG = {
    "24": ("pastinaak", "Ingemaakte pastinaak"), "188": ("bonen", "Ingemaakte boontjes"),
    "190": ("bloemkool", "Ingemaakte bloemkool"), "192": ("aardappel", "Ingemaakte aardappels"),
    "248": ("knoflook", "Ingemaakte knoflook"), "250": ("boerenkool", "Ingemaakte boerenkool"),
    "256": ("tomaten", "Ingemaakte tomaten"), "259": ("struisvaren", "Ingemaakte struisvaren"),
    "262": ("tarwe", "Ingemaakte tarwe"), "264": ("radijs", "Ingemaakte radijsjes"),
    "266": ("rodekool", "Ingemaakte rode kool"), "270": ("maïs", "Ingemaakte maïs"),
    "271": (None, "Ingemaakte ongepelde rijst"), "272": ("aubergine", "Ingemaakte aubergine"),
    "274": ("artisjokken", "Ingemaakte artisjokken"), "276": ("pompoen", "Ingemaakte pompoen"),
    "278": ("paksoi", "Ingemaakte paksoi"), "280": (None, "Ingemaakte zoete aardappel"),
    "284": ("bieten", "Ingemaakte bietjes"), "300": ("amarant", "Ingemaakte amarant"),
    "304": ("hop", "Ingemaakte hop"), "815": ("thee", "Ingemaakte theebladeren"),
    "830": ("taro", "Ingemaakte taro"), "Carrot": ("wortel", "Ingemaakte worteltjes"),
    "SummerSquash": ("zomerpompoen", "Ingemaakte zomerpompoen"), "Broccoli": ("broccoli", "Ingemaakte broccoli"),
    "16": (None, "Ingemaakte wilde mierikswortel"), "20": ("prei", "Ingemaakte prei"),
    "22": ("paardenbloemen", "Ingemaakte paardenbloem"), "78": ("grottenwortel", "Ingemaakte grottenwortels"),
    "399": ("lente-uien", "Ingemaakte lente-uitjes"), "412": ("winterwortel", "Ingemaakte winterwortels"),
    "416": ("sneeuwknol", "Ingemaakte sneeuwknol"), "829": ("gember", "Ingemaakte gember"),
}
VEG_PHRASE = {"271": "ongepelde rijst", "280": "zoete aardappel", "16": "wilde mierikswortel"}

MUSHROOMS = {"257": "Gedroogde morieljes", "281": "Gedroogde cantharellen", "404": "Gedroogde champignons",
             "420": "Gedroogde rode paddenstoelen", "422": "Gedroogde paarse paddenstoelen",
             "851": "Gedroogde magmahoeden"}

FLOWERS = {"402": "Reukerwtenhoning", "418": "Krokushoning", "421": "Zonnebloemhoning", "591": "Tulpenhoning",
           "593": "Zomerjuweelhoning", "595": "Feeënrozenhoning", "597": "Honing van blauwe jazz",
           "376": "Klaprozenhoning"}

# legendary fish keep their capital (they're names), multi-word fish get phrases
LEGENDS = {"159", "160", "163", "682", "775", "898", "899", "900", "901", "902"}


def compound(stem, suffix):
    """Dutch compound; a hyphen where two vowels would merge (tilapia-aas)."""
    sep = "-" if stem[-1] == "a" and suffix[0] == "a" else ""
    return stem + sep + suffix


def cap(s):
    return s[0].upper() + s[1:]


def generate():
    objs = objects()
    nl = __import__("worklist").current("Strings/Objects")
    out = {}

    def put(kind, item_id, value):
        qid = f"(O){item_id}"
        out[f"{kind}_Flavored_{qid}_Name"] = value

    for item_id, (stem, dried) in FRUIT.items():
        if stem:
            put("Wine", item_id, cap(compound(stem, "wijn")))
            put("Jelly", item_id, cap(compound(stem, "jam")))
            put("Juice", item_id, cap(compound(stem, "sap")))
        else:
            phrase = FRUIT_PHRASE[item_id]
            put("Wine", item_id, f"Wijn van {phrase}")
            put("Jelly", item_id, f"Jam van {phrase}")
            put("Juice", item_id, f"Sap van {phrase}")
        put("DriedFruit", item_id, dried)
    for item_id, (stem, pickled) in VEG.items():
        put("Juice", item_id, cap(compound(stem, "sap")) if stem else f"Sap van {VEG_PHRASE[item_id]}")
        put("Pickles", item_id, pickled)
    for item_id, dried in MUSHROOMS.items():
        put("DriedFruit", item_id, dried)
    for item_id, honey in FLOWERS.items():
        put("Honey", item_id, honey)

    for item_id, data in objs.items():
        if data["category"] != -4:
            continue
        name = nl.get(data["key"], "")
        legend = item_id in LEGENDS
        if " " in name or not name:
            label = name if legend else name.lower()
            put("Roe", item_id, f"Kuit van {label}")
            put("AgedRoe", item_id, f"Gerijpte kuit van {label}")
            put("SpecificBait", item_id, f"Aas voor {label}")
        else:
            stem = name if legend else name.lower()
            put("Roe", item_id, cap(compound(stem, "kuit")))
            put("AgedRoe", item_id, "Gerijpte " + compound(stem, "kuit").lower() if not legend
                else "Gerijpte " + compound(stem, "kuit"))
            put("SpecificBait", item_id, cap(compound(stem, "aas")))
        put("SmokedFish", item_id, "Gerookte " + (name if legend else name.lower()))

    # fallbacks for modded ingredients: {1} is the lowercase display name
    out.update({
        "Wine_Flavored_Name": "Wijn van {1}", "Jelly_Flavored_Name": "Jam van {1}",
        "Juice_Flavored_Name": "Sap van {1}", "Pickles_Flavored_Name": "{0} (ingemaakt)",
        "Honey_Flavored_Name": "Honing van {1}", "DriedFruit_Flavored_Name": "Gedroogde {1}",
        "Roe_Flavored_Name": "Kuit van {1}", "AgedRoe_Flavored_Name": "Gerijpte kuit van {1}",
        "SpecificBait_Flavored_Name": "Aas voor {1}", "SmokedFish_Flavored_Name": "Gerookte {1}",
        "Jelly_Name": "Jam", "Pickles_Name": "Ingemaakte groente",
        "Pickles_Description": "Een pot zelf ingemaakte groente.",
        "DriedFruit_Description": "Taaie stukjes gedroogd fruit.",
    })
    return out


if __name__ == "__main__":
    batch = {"Strings/Objects": generate()}
    path = os.path.join(SOURCE, "..", "review", "flavored.json")
    save_json(path, batch)
    apply_batch(batch, "polish")
    print(len(batch["Strings/Objects"]), "flavored names")
