# Wijzigingen

## 2.0.1
Controleronde: voorwerpnamen overal gelijk, en fouten buiten de voorwerpbestanden gerepareerd.

### Gerepareerd
- Keuzevragen waarvan de antwoorden kapot waren: Demetrius (grotexperiment), Pam (IJsfestival),
  Penny (Winterster) en Caroline (nieuwe keuken).
- Marlons opdrachten op het Woestijnfestival toonden `{Monster:LocalisedName}` in plaats van de
  naam van het monster, en de beschrijving noemde 12 in plaats van 10 monsters.
- Foute informatie: de eiland-obelisk bracht je naar "Ingerwinsel", het Avonturiersgilde was
  open "tot 22:00" (moet 2:00 zijn), de superkomkommer zwom "in de zomer en winter" (moet herfst
  zijn), en bij de rivierboerderij ontbrak dat je met een visroker begint.
- Verkeerde namen: de waterput heette "Fontein", bij het verven van gebouwen stond twee keer
  "Dak", "Duits" heette "Nederlands" en de iridiumgolem heette "Wildness Golem".
- Engelse restjes en typfouten, zoals "Harvest an egg from your chickens", "Perfecte Ice Wand",
  "idiriumstaven", "verbanenn", "de de" en "om om". Vier puntjes ("....") zijn nu overal drie.
- Marnie en Willy wisselden in één gesprek tussen "u" en "je".

### Opgepoetst
- Een voorwerp heet in dialogen, brieven, quests en tv-programma's nu precies zoals het voorwerp
  zelf. Het Galaxyzwaard heette bij het vinden nog "melkwegzwaard". Andere voorbeelden:
  *Krabkooi*, *Gouden penning*, *Gouden dobber*, *Kruidenbes*, *Grottenwortel*, *Geheim briefje*,
  *Calico-beeld*, *Magische pijlkoker*, *Kevervlees*, en de recepten van De Sauskoningin.
- Overal *Stardrop Saloon* (niet meer "Stardew Saloon" of "Sterrendruppel Saloon") en
  *Forellenderby*.
- Lijsten die nog niet waren opgepoetst: gebouwen (*Woestijnobelisk*, *Aarde-obelisk*),
  bioscoopsnacks (*Boerenkoolsmoothie*, *Toverbal*), bundels (alle namen eindigen nu op "bundel"),
  prestaties, betoveringen en monsters.
- Woestijnfestival: de quizvragen lopen weer goed, en de chef, de wasbeer, de cactusman en de
  wedstrijdleider staan weer steeds met hun naam voor hun tekst. Hetzelfde geldt voor de vissers
  op de Forellenderby.
- Bezittelijke vorm volgens de stijlgids: *Emily's*, *Penny's*, *Willy's*, *Harvey's*.
- *IJspieperkuit* en *IJssandwich* met een hoofdletter-IJ.

### Techniek
- `tools/audit.py` meldt nu ook keuzevragen met een verkeerd aantal antwoorden en `{tokens}` die
  het spel niet kent.
- Woordenlijst en stijlgids aangevuld.

## 2.0.0
Complete herbouw voor Stardew Valley 1.6.15.

### Nieuw en aangevuld
- Alle gereedschapsteksten (`Strings/Tools`) vertaald; die stonden nog volledig in het Engels.
- De beschrijving van het Calico-ei ("Beschrijving.") en de afgekapte beschrijving van het
  luiaardskelet aangevuld.
- Engelse restjes vertaald, zoals "{0} Honey", "Monster Compendium", de watervalboerderij en een zin van
  Lewis op het IJsfeest.
- Eigen Nederlandse namen per ingrediënt voor wijn, jam, sap, ingemaakte groente, honing, gedroogd
  fruit, kuit, aas en gerookte vis: *Aardbeienwijn*, *Tulpenhoning*, *Gerijpte zalmkuit*, *Tilapia-aas*.
  Voorwerpen uit andere mods krijgen een nette omschrijving, zoals *Wijn van …*.
- Getallen met een punt als duizendtalscheiding (1.000.000g).

### Opgepoetst
- Alle voorwerpnamen en -beschrijvingen herschreven: voorwerpen, meubels, machines, wapens, kleding,
  hoeden en schoenen. Kort, warm en in de toon van het origineel, met dezelfde knipoogjes waar het
  Engels die ook heeft (*Thee-shirt*, *Ploertendoder*, *De Beuker*).
- Vaste terminologie in het hele spel: *Calico-ei*, *Calico-woestijn*, *Schedelgrot*, *Buurthuis*,
  *Ginger Island*, *Vareneilanden*, *Karmozijnvis*, *Joja Cola* (zie `docs/stijlgids.md`).
- Hernoemde voorwerpen ook aangepast in dialogen, brieven, quests en tv-programma's.
- Meesterschappen goed vertaald; "Mijnbouw beheersen" heette eerst "Minecraft beheersen".

### Gerepareerd
- Afgebroken zinnen hersteld, onder andere bij de trechter, de Junimokist en de zware boomtap.
- Kapotte placeholders en tokens die fouten konden geven (boerderijcomputer, Gil, Evelyn, `%seizoen`,
  `%naam`), losse accolades in geslachtswissels en ontbrekende antwoordopties in dialogen.
- 152 verloren portretemoties teruggezet, zodat personages weer lachen en kijken zoals bedoeld.
- Pierres `$d joja`-zin en Alex' lege regel op het Bloemenfeest aangevuld.
- Zero-width spaces verwijderd (die verschenen als vreemde tekens).

### Techniek
- De mod vervangt geen hele bestanden meer, maar past alleen de teksten aan (Content Patcher
  `EditData`). Daardoor blijven cadeauvoorkeuren, hoeden (zoals de regenboogkleur van de magische
  cowboyhoed) en quest-ID's gelijk aan de huidige spelversie, en blijven nieuwe teksten na een update
  Engels in plaats van kapot.
- Afbeeldingen worden alleen nog in de tekstvlakken aangepast, op de huidige 1.6-afbeeldingen. Het
  prikbord is weer groot genoeg, en mods zoals Seasonal Cute Characters werken gewoon mee.
- Titelscherm (*Nieuw*, *Laden*, *Co-op*, *Afsluiten*, *Terug*, *Ontwikkeld door*), het prikbord,
  het vistutorial, de rioolkaart, knoppen en bordjes opnieuw gezet in de originele handgetekende
  letters van het spel.
