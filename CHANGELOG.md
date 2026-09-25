# Wijzigingen

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
