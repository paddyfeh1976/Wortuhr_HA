# Wortuhr Integration für Home Assistant

![image](https://raw.githubusercontent.com/paddyfeh1976/Wortuhr/main/images/banner_klein.png)

Diese Projekt ist noch in der Entwicklung. Bitte nicht verwenden bzw. auf eigenes Risiko.

Eine Home Assistant Integration zur Steuerung der [Wortuhr](https://www.wortuhr.daniel-stingl.de/) über die HTTP-API.

## Features

- 🎯 **Texte & Events anzeigen**: Beliebige Texte mit Farben und Animationen auf der Wortuhr anzeigen
- 🎵 **Audio abspielen**: Sounddateien von der SD-Karte abspielen (Wenn Audiomodul vorhanden)
- 🎭 **Modi wechseln**: Zwischen 21 verschiedenen Display-Modi umschalten (Zeit, Wetter, Datum, etc.)
- ⚙️ **Einstellungen**: ~~Alarme~~, ~~Helligkeit~~, Farben und mehr konfigurieren
- 🔧 **Geräteverwaltung**: Reboot, WiFi-Reset, MP3-Reset

## Installation

### Über HACS (empfohlen)

1. Öffne Home Assistant → HACS
2. Klicke auf **"Custom repositories"** (drei Punkte)
3. Füge folgende URL ein: `https://github.com/pfehr/Wortuhr_HA`
4. Kategorie: **Integration**
5. Suche nach **Wortuhr** und installiere die Integration
6. Starte Home Assistant neu

### Manuell

1. Klone das Repository oder lade es herunter
2. Kopiere `custom_components/wortuhr` nach `config/custom_components/wortuhr`
3. Starte Home Assistant neu

## Konfiguration

1. Gehe zu **Einstellungen → Geräte & Services → Integrationen**
2. Klicke auf **"Integration hinzufügen"** und suche **"Wortuhr"**
3. Gib die **IP-Adresse** deiner Wortuhr ein
4. Speichere die Integration

> Die Wortuhr-IP muss sich im gleichen Netzwerk wie Home Assistant befinden.

## Unterstützte Services

Die Integration registriert folgende Services:

### `wortuhr.show_text`
Zeigt Text mit optionaler Farbe und Buzzer an.

```yaml
service: wortuhr.show_text
data:
  text: "Hallo Welt"
  color: 1           # 0-24
  buzzer: 2
```

### `wortuhr.show_event`
Zeigt ein Event mit optionalen Animationen und Audio an.

```yaml
service: wortuhr.show_event
data:
  text: "Morgen wird Gelbe Tonne geleert"
  color: 5
  audio: 750
  preani: "MUELL_GELB"
  postani: "MUELL_GELB"
```

### `wortuhr.play_audio`
Spielt eine Sounddatei von der SD-Karte ab.

```yaml
service: wortuhr.play_audio
data:
  soundfile: 819
  volume: 100
```

### `wortuhr.set_mode`
Schaltet den Display-Modus um.

```yaml
service: wortuhr.set_mode
data:
  mode: 2
  sound: true
```

### `wortuhr.reboot`
Startet die Wortuhr neu.

```yaml
service: wortuhr.reboot
```

### `wortuhr.wifi_reset`
Setzt die WiFi-Konfiguration zurück.

```yaml
service: wortuhr.wifi_reset
```

### `wortuhr.mp3_reset`
Setzt den MP3-Player zurück.

```yaml
service: wortuhr.mp3_reset
```

## Verfügbare Moduswerte

- `0` = Zeit (Uhr)
- `1` = Ansage
- `2` = Wochentag
- `3` = Datum
- `4` = Mondphase
- `5` = Temperatur
- `6` = Luftfeuchte
- `7` = Luftdruck
- `8` = Wetter
- `12` = IP-Adresse
- `13` = Testmodus
- `18` = Timer
- `20` = Aus

## Geräte-Steuerelemente

Nach der Einrichtung stehen in der Geräteansicht typische Entitäten bereit:

- `button`-Entitäten für Reboot, WiFi-Reset, MP3-Reset und Nachricht anzeigen
- `select`-Entitäten für Moduswahl, Textfarbe, LED-Farben, Hintergrundoptionen, Animationen und mehr
- `text`-Entitäten für Meldungen und ggf. Hintergrundfarbe
- `switch`-Entitäten für automatische Helligkeit, Ein/Aus-Funktionen und weitere Einstellungen
- `light`-Entitäten für die Wortuhrbeleuchtung

## Beispiele

### Automation: Erinnerung an die Gelbe Tonne

```yaml
automation:
  - alias: "Gelbe Tonne Erinnerung"
    trigger:
      platform: time
      at: "18:00:00"
    condition:
      - condition: time
        weekday:
          - wed
    action:
      - service: wortuhr.show_event
        data:
          text: "Morgen wird gelbe Tonne geleert"
          color: 5
          audio: 750
          preani: "MUELL_GELB"
          postani: "MUELL_GELB"
```

### Script: Guten Morgen

```yaml
script:
  good_morning:
    sequence:
      - service: wortuhr.show_text
        data:
          text: "Guten Morgen"
          color: 10
          buzzer: 1
      - delay:
          seconds: 3
      - service: wortuhr.set_mode
        data:
          mode: 0
          sound: false
```

## Bekannte Einschränkungen

- Die Wortuhr muss sich im gleichen Netzwerk wie Home Assistant befinden.
- Die HTTP-API unterstützt aktuell keine Authentifizierung.
- Einige Auswahlwerte und Modi können von deiner Wortuhr-Firmware abweichen.

## Fehlerbehebung

**Problem:** Integration lässt sich nicht hinzufügen
- Prüfe die eingegebene IP-Adresse
- Stelle sicher, dass die Wortuhr erreichbar ist
- Home Assistant neu starten

**Problem:** Serviceaufrufe funktionieren nicht
- Prüfe die Home Assistant-Protokolle
- Vergleiche die Serviceparameter mit den Beispielen oben

## Support

Für Bugs und Feature-Requests: [GitHub Issues](https://github.com/pfehr/Wortuhr_HA/issues)

## Lizenz

MIT License
