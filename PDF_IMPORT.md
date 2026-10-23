# PDF-tuonti

Suunnittelusivulla voit tuoda PDF-tiedoston samalla tavalla kuin Word- ja
PowerPoint-tiedoston. Jokaisesta PDF-sivusta luodaan oma kuvan sisältävä HTML-sivu.
Tuodut sivut ovat aluksi pois käytöstä, ja niiden näyttöaika on 10 sekuntia.
Ota sivut käyttöön ja järjestä ne Järjestely-sivulla.

Rajat: tiedosto voi olla enintään 50 Mt ja siinä voi olla enintään 100 sivua.
Salasanalla suojattuja PDF-tiedostoja ei tueta. Epäonnistunut tuonti ei jätä
puolikkaita sivuja.

Palvelimella täytyy olla Popplerin `pdftoppm` asennettuna ja Flask-palvelun
PATH-ympäristömuuttujassa. PDF:n sivut muunnetaan PNG-kuviksi, joiden pisin reuna
on 1920 pikseliä. Kuvat upotetaan HTML-tiedostoihin.
