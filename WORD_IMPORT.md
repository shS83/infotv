# Word-tuonti

Design Page / Suunnittelusivu → **Import a DOC/DOCX File** → **Upload**.
Cancel tyhjentää valinnan ennen lähettämistä.

Jokainen asiakirjan sivu muunnetaan kuvaksi ja tallennetaan omaksi HTML-sivuksi
hakemistoon `FlaskTV/templates/info_pages`. Kuva sisältyy HTML-tiedostoon.
Sivut näkyvät profiilissa ja järjestelysivulla alkuperäisessä sivujärjestyksessä.
Ne ovat aluksi pois käytöstä. Ota ne käyttöön järjestelysivulla ja säädä
tarvittaessa oletusnäyttöaikaa (10 sekuntia) ajastussivulla.

Sivut sovitetaan ruutuun kokonaisina ja mittasuhteet säilyttäen. Pystysivun
sivuille jää tyhjää tilaa; television sisältöä varten voit käyttää Wordissa
vaakasivua ja riittävän suurta tekstiä. InfoTV-logo pysyy oikeassa yläkulmassa.
Sivun pisin reuna on 1920 pikseliä.

Sisältö tuodaan staattisina kuvina. Muokkaa tekstiä ja asettelua Wordissa ja tuo
asiakirja uudelleen. Uusi tuonti ei korvaa aiemmin tuotuja sivuja. Palvelimen
fontit voivat vaikuttaa tekstin asetteluun ja sivutukseen. Salasanalla suojattuja
asiakirjoja ei tueta.

Rajat: 50 Mt ja 100 sivua. Muunnoksen kumpikin vaihe saa kestää enintään 120
sekuntia. Palvelimen ja mahdollisen välityspalvelimen aikarajojen on sallittava
muunnos. Epäonnistunut tuonti perutaan ja sen luomat HTML-sivut poistetaan.

## Palvelimen riippuvuudet

LibreOffice Writer (`libreoffice` tai `soffice`) ja Popplerin `pdftoppm` täytyy
löytyä Flask-palvelun PATH-ympäristömuuttujasta.

Ubuntu/Debian:

```sh
sudo apt install libreoffice-writer poppler-utils
```

Arch Linux:

```sh
sudo pacman -S libreoffice-fresh poppler
```

Muunnos käyttää samaa paikallista muunnosketjua kuin PowerPoint-tuonti,
mutta PDF-vienti tehdään LibreOffice Writerilla. Asiakirjoja ei lähetetä
ulkoiseen palveluun. Jokainen muunnos käyttää erillistä väliaikaista profiilia,
jossa makrojen suojaustaso on Very High.

## Testaus

```sh
python -m unittest discover -s tests -v
```

Testit käyttävät väliaikaistiedostoja ja muistissa olevaa tietokantaa.
Kokeile lisäksi omia DOC- ja DOCX-asiakirjoja palvelimella fonttien ja sivutuksen
varmistamiseksi.
