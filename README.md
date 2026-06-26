# Wortuhr Integration für Home Assistant

![image](https://raw.githubusercontent.com/paddyfeh1976/Wortuhr/main/images/icon.png)

Diese Projekt ist noch in der Entwicklung. Bitte nicht verwenden bzw. auf eigenes Risiko.

Eine Home Assistant Integration zur Steuerung der [Wortuhr](https://www.wortuhr.daniel-stingl.de/) über die HTTP-API.

## Features

- 🎯 **Texte & Events anzeigen**: Beliebige Texte mit Farben und Animationen auf der Wortuhr anzeigen
- 🎵 **Audio abspielen**: Sounddateien von der SD-Karte abspielen (Wenn Audiomodul vorhanden)
- 🎭 **Modi wechseln**: Zwischen 21 verschiedenen Display-Modi umschalten (Zeit, Wetter, Datum, etc.)
- ⚙️ **Einstellungen**: Alarme, Helligkeit, Farben und mehr konfigurieren
- 🔧 **Geräteverwaltung**: Reboot, WiFi-Reset, MP3-Reset

## Installation

### Über HACS (empfohlen)

1. Öffne Home Assistant → HACS
2. Klicke auf **"Custom repositories"** (drei Punkte)
3. Füge folgende URL ein: `https://github.com/pfehr/Wortuhr_HA`
4. Kategorie: **Integration**
5. Klicke auf "Wortuhr"
6. **Install** klicken
7. Home Assistant neu starten

### Manuell

1. Klone das Repository oder lade es herunter
2. Kopiere `custom_components/wortuhr` nach `config/custom_components/wortuhr`
3. Starte Home Assistant neu

## Konfiguration

Nach der Installation:

1. Gehe zu **Einstellungen → Geräte & Services → Integrationen**
2. Klicke auf **"Neue Integration erstellen"** und suche **"Wortuhr"**
3. Gib die **IP-Adresse** deiner Wortuhr ein
4. Die Verbindung wird getestet und gespeichert

Die Wortuhr-IP muss sich im gleichen Netz wie dein Home Assistant befinden.

## Verfügbare Services

Nach der Konfiguration stehen folgende Services zur Verfügung:

### `wortuhr.show_text`
Zeigt einen Text mit optionalen Ankündigungssounds an.

```yaml
service: wortuhr.show_text
data:
  text: "Hallo Welt"
  color: 1           # 0-24
  buzzer: 2          # Anzahl der Töne
```

### `wortuhr.show_event`
Zeigt ein Event mit Vorher- und Nachher-Animation an.

```yaml
service: wortuhr.show_event
data:
  text: "Morgen wird Gelbe Tonne geleert"
  color: 5
  audio: 750
  preani: "MUELL_GELB"
  postani: "MUELL_GELB"
```

### `wortuhr.set_mode`
Wechselt zu einem bestimmten Display-Modus.

```yaml
service: wortuhr.set_mode
data:
  mode: 2            # 0=Zeit, 2=Wochentag, 3=Datum, 8=Wetter, etc.
  sound: true        # Ankündigungstext
```

**Verfügbare Modi:**
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

### `wortuhr.play_audio`
Spielt eine Sounddatei ab.

```yaml
service: wortuhr.play_audio
data:
  soundfile: 819     # Soundnummer
  volume: 100        # 0-100 (0 = aktuelle Lautstärke)
```

### `wortuhr.reboot`
Startet die Wortuhr neu.

```yaml
service: wortuhr.reboot
```

### `wortuhr.wifi_reset`
Setzt die WiFi-Einstellungen zurück (AP-Mode).

```yaml
service: wortuhr.wifi_reset
```

### `wortuhr.mp3_reset`
Setzt den MP3-Player zurück.

```yaml
service: wortuhr.mp3_reset
```

## Beispiele

### Automation: Mülltonnen-Erinnerung

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

## Bekannte Limitierungen

- Die Wortuhr muss sich im gleichen WLAN-Netz wie Home Assistant befinden
- Einige Modi können je nach Hardware-Konfiguration verschoben sein (Ausprobieren hilft)
- Die HTTP-API hat keine Authentifizierung

## Fehlerbehebung

**Problem:** "Verbindung zur Wortuhr fehlgeschlagen"
- Stelle sicher, dass die Wortuhr im gleichen WLAN wie Home Assistant ist
- Überprüfe die IP-Adresse in der Konfiguration
- Starte die Wortuhr neu

**Problem:** Service funktioniert nicht
- Überprüfe die Heimautomation-Logs: **Einstellungen → Protokolle**
- Stelle sicher, dass alle erforderlichen Parameter angegeben sind

## Support

Für Bugs und Feature-Requests: [GitHub Issues](https://github.com/pfehr/Wortuhr_HA/issues)

## Lizenz

MIT License
