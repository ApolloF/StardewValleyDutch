# Stijlgids Nederlandse vertaling

Doel: het spel moet voelen alsof ConcernedApe het zelf in het Nederlands heeft geschreven.
Kort, warm, eenvoudig. Een knipoog alleen waar het Engels er ook een maakt.

## Toon
- Spreek de speler aan met **je**. Nooit u (behalve als een personage bewust formeel is, zoals Morris).
- Vertaal de *bedoeling*, niet de woorden. Lees de Engelse zin, bedenk hoe een Nederlander het
  zou zeggen, en houd dezelfde lengte en hetzelfde ritme aan.
- Grapjes, woordspelingen en droge opmerkingen blijven grapjes: zoek een Nederlands equivalent in
  plaats van de letterlijke vertaling. Geen grap toevoegen waar het origineel neutraal is.
- Geen Engelse woorden in Nederlandse zinnen als er een gewoon Nederlands woord voor is.

## Voorwerpnamen
- Zinshoofdletter: *Gouden masker*, niet *Gouden Masker*. Eigennamen houden hun hoofdletter.
- Samenstellingen aaneen, volgens de Woordenlijst: *Regentotem*, *Iridiumbijl*, *Wortelzaad*,
  *Veenbessenwijn*. Met koppelteken bij eigennamen of klinkerbotsing: *Calico-ei*, *Qi-munten*.
- Zaden heten *…zaad* (*Bloemkoolzaad*), stekjes *…stek*, jonge boompjes *…boompje*.
- Een naam past in het vakje: liever kort en gewoon dan lang en letterlijk.
- Bezittelijke vorm volgens de Taalunie: *Haley's*, *Abby's*, *Leah's*, *Maru's*, maar *Pierres*,
  *Elliotts*, *Sams*, *Gils*, *Abigails*; na een sis-klank *Alex'*.
- Houtsoorten: *Eikenhouten*, *Notenhouten*, *Berkenhouten*, *Mahoniehouten*.
- Kleding: *shirt* is het gewone woord; *overhemd* alleen voor een net hemd met kraag en knopen;
  *gilet* voor een vest zonder mouwen; varianten met *(V)* en *(M)*.
- Merken met koppelteken in samenstellingen: *Joja-kussen*, *Joja Cola-koelkast*; Junimo en Retro
  gewoon aaneen: *Junimokist*, *Retrolamp*.
- Artisanale producten per ingrediënt (gegenereerd door `tools/flavored.py`): *Aardbeienwijn*,
  *Aardbeienjam*, *Tomatensap*, *Ingemaakte bietjes*, *Tulpenhoning*, *Gedroogde abrikozen*,
  *Zalmkuit*, *Gerijpte zalmkuit*, *Zalmaas*, *Gerookte zalm*. Bij namen van meer woorden een
  omschrijving: *Wijn van wilde pruimen*, *Kuit van Mevrouw Zeeduivel*.

## Beschrijvingen
- Volledige, korte zinnen met een punt. Geen telegramstijl, tenzij het Engels die ook gebruikt.
- Vaste formuleringen:
  - "Consumed on use." → *Verdwijnt na gebruik.*
  - "Plant these in the spring. Takes N days to mature." → *Plant in de lente. Na N dagen rijp.*
  - "Place on the ground…" → *Leg op de grond…*
  - "A blacksmith can break this open for you." → *Een smid kan hem voor je openbreken.*
- Spelmechanische termen zoals in de interface: landbouw, vissen, mijnbouw, verzamelen, vechten,
  geluk, max. energie, magnetisme, snelheid, verdediging, aanval, energie, gezondheid.

## Namen en plaatsen (woordenlijst: source/glossary.json)
| Engels | Nederlands |
|---|---|
| Pelican Town, Stardew Valley, Ginger Island, Zuzu City | blijven Engels (eigennaam) |
| Calico Desert | Calico-woestijn |
| Calico Egg(s) | Calico-ei (Calico-eieren) |
| Calico Statue | Calico-beeld |
| Stardrop Saloon | blijft Engels (eigennaam) |
| Skull Cavern | Schedelgrot |
| Community Center | Buurthuis |
| Adventurer's Guild | Avonturiersgilde |
| JojaMart | JojaMarkt |
| Golden Walnut | Gouden walnoot |
| Qi Gem(s) | Qi-edelsteen (Qi-edelstenen) |
| Prismatic Shard | Prismatische scherf |
| Mr. Qi | Mr. Qi |
| Fern Islands | Vareneilanden |
| Gem Sea | Edelstenenzee |
| Crimsonfish | Karmozijnvis |
| Journey of the Prairie King | Reis van de Prairiekoning |
| Trout Derby | Forellenderby |
| Golden Tag | Gouden penning |
| Crab Pot | Krabkooi |
| Secret Note | Geheim briefje |
| Trinket | Ornament |
| Speed-Gro | Snel-Groei |
| Jelly (artisanaal) | Jam |
| Pickles | Ingemaakte groente |
| Void (Void Egg, …) | Schaduw… (*Schaduwei*) |
| Joja Cola | Joja Cola |

## Techniek (niet vertalen of veranderen)
- Tokens: `@`, `%adj`, `{0}`, `[LocalizedText …]`, `%item … %%`, `$h`, `$s`, `#$b#`, `#$e#`, `^`.
- Geslachtswissel: `${hij^zij}$` met dollartekens aan beide kanten.
- Portretcodes (`$h`, `$s`, …) staan aan het eind van dezelfde pagina als in het Engels.
- Keuzevragen (`$y 'vraag_antwoord_reactie_…'`) houden precies evenveel `_` als het Engels.
- Een voorwerp heet in dialogen, brieven, quests en tv-programma's precies zoals in zijn naam.
- Draai altijd `tools/audit.py`; nul fouten voor een release.
