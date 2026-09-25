![banner](https://user-images.githubusercontent.com/17224428/111884012-10e2f400-89bf-11eb-9d65-3b0d1e0a78e0.png)

Deze repository bevat de Nederlandse vertaling voor Stardew Valley (1.6.15).

Versie 2.0 is een complete herbouw. Alle teksten zijn nagelopen en alle voorwerpnamen en -beschrijvingen
opnieuw vertaald. Ontbrekende en Engelse teksten zijn aangevuld, en het titelscherm en de bordjes in het
dorp zijn opnieuw getekend in de originele letters van het spel. Wat er precies veranderd is, staat in
[CHANGELOG.md](CHANGELOG.md).

:warning: De mod is uitvoerig getest, maar er kunnen natuurlijk nog foutjes in zitten. Maak daarom een backup van je savegames voordat je deze mod gaat gebruiken. Mocht je een fout tegenkomen, dan stellen wij het zeer op prijs als je hier een [Issue](https://github.com/janfokke/StardewValleyDutch/issues) voor aanmaakt.

![Installation](https://user-images.githubusercontent.com/17224428/111886773-a2a72d00-89d0-11eb-82f1-745288638640.png)
1. [Installeer de laatste versie van SMAPI.](https://smapi.io/)
2. [Download Content Patcher](https://www.nexusmods.com/stardewvalley/mods/1915) (2.9 of nieuwer) en pak deze uit in Stardew Valley/Mods.
3. [Download deze mod](https://github.com/janfokke/StardewValleyDutch/releases) en pak deze uit in Stardew Valley/Mods.
   Heb je een oudere versie (1.x)? Verwijder die map dan eerst.
4. Start het spel met SMAPI.
5. Verander de taal naar Nederlands op pagina 2 van de taalkeuze!

![Select](https://staticdelivery.nexusmods.com/mods/1303/images/24290/24290-1717275487-1683960106.png)

## Werkt samen met andere mods
De mod past alleen de teksten en de tekstvlakken in afbeeldingen aan, bovenop de gewone spelbestanden.
Spelgegevens (cadeauvoorkeuren, hoeden, quests) blijven die van de huidige spelversie, en mods die
dezelfde afbeeldingen aanpassen (zoals Seasonal Cute Characters) blijven gewoon werken.

## Voor vertalers
De mod wordt gebouwd uit bronbestanden met een paar Python-scripts (alleen de standaardbibliotheek):

| Map / script | Inhoud |
|---|---|
| `source/nl/` | de Nederlandse teksten, per spelbestand |
| `source/polish/` | de herschreven voorwerpnamen en -beschrijvingen (gaan boven `source/nl/`) |
| `source/glossary.json`, `docs/stijlgids.md` | woordenlijst en stijlgids |
| `art/` | de opnieuw getekende tekstvlakken |
| `tools/extract.py` | haalt de Engelse en officieel vertaalde spelbestanden uit de installatie (`vanilla/`) |
| `tools/build.py polished [--install]` | bouwt de mod naar `build/` (en installeert hem in Mods) |
| `tools/audit.py polished` | controleert alle teksten; voor een release moeten er 0 fouten zijn |
| `tools/flavored.py` | maakt de namen van wijn, jam, sap, honing, kuit enz. per ingrediënt |

Na een spelupdate: `extract.py`, dan `audit.py`. Die laat zien welke teksten nieuw of veranderd zijn.

# Credits
Originele vertaling door **Spawk** met technische ondersteuning van **JanFokke**
Mobiele V1.5 vertaling door **rhansenne**
Geupdated voor 1.6 door **Azelion**
