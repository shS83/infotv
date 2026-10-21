# PowerPoint-tuonti

Design Page / Suunnittelusivu → **Import a PPT/PPTX file** → **Upload**.
Cancel tyhjentää tiedostovalinnan ennen lähettämistä.

Jokaisesta diasta syntyy oma HTML-sivu hakemistoon `FlaskTV/templates/info_pages`.
Sivu sisältää dian PNG-kuvan, joten erillisiä kuvatiedostoja ei tarvitse ylläpitää.
Diat näkyvät profiilissa sekä järjestelysivulla. Ne ovat aluksi pois käytöstä ja
niiden oletusnäyttöaika on 10 sekuntia. Järjestä ja ota diat käyttöön järjestelysivulla
ja muuta näyttöajat ajastussivulla. Uusi tuonti luo uudet sivut eikä korvaa aiempia.

Enimmäiskoko on 50 Mt ja enintään 100 diaa. Muunnos tapahtuu palvelimella ja voi
kestää muutaman minuutin; palvelimen ja mahdollisen välityspalvelimen pyyntöjen
aikarajojen pitää sallia tämä. Kummankin muunnosvaiheen aikaraja on 120 sekuntia.
Epäonnistunut tuonti perutaan ja sen luomat HTML-sivut poistetaan.

Diat ovat staattisia kuvia: animaatiot, videot ja PowerPointin siirtymät eivät
toistu. Muokkaa sisältöä alkuperäisessä esityksessä ja tuo se uudelleen.
Palvelimelle asennetut fontit vaikuttavat ulkoasuun, joten asenna esityksissä
käytettävät fontit palvelimelle. Kuvat sovitetaan ruutuun mittasuhteet säilyttäen;
InfoTV-logo näkyy oikeassa yläkulmassa. Dian pisin sivu on 1920 pikseliä.

## Palvelimen riippuvuudet

Tarvitaan LibreOffice Impress (`libreoffice` tai `soffice`) sekä Popplerin
`pdftoppm`, molemmat Flask-palvelun PATH-ympäristömuuttujassa.

Ubuntu/Debian:

```sh
sudo apt install libreoffice-impress poppler-utils
```

Arch Linux:

```sh
sudo pacman -S libreoffice-fresh poppler
```

Muunnos käyttää [LibreOfficen komentorivimuunnosta](https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html)
ja erillistä väliaikaista käyttäjäprofiilia joka pyynnölle. Tiedostoja ei lähetetä
ulkoiseen muunnospalveluun. Makrojen suojaustaso on Very High.

## Testit

Projektin Python-riippuvuuksilla:

```sh
python -m unittest discover -s tests -v
```

Testit käyttävät väliaikaishakemistoja ja muistissa olevaa tietokantaa.
Muunnostyökalujen kutsut korvataan yksikkötesteissä testeihin sopivilla vastauksilla.
Varsinainen LibreOffice-muunnos kannattaa lisäksi kokeilla palvelimella omalla
PPT- ja PPTX-esityksellä, erityisesti esitysten käyttämien fonttien tarkistamiseksi.
