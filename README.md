# Wortuhr Integration für Home Assistant

![image](https://raw.githubusercontent.com/paddyfeh1976/Wortuhr/main/images/banner_klein.png)

**Diese Projekt ist noch in der Entwicklung. Bitte nicht verwenden bzw. auf eigenes Risiko. Es erfolgt kein Support**

Eine vollständige Home Assistant Integration zur Steuerung der [Wortuhr](https://www.wortuhr.daniel-stingl.de/) über die HTTP-API.

**Version:** 1.0.0 | **Benötigt:** Home Assistant 2024.1.0+

## Features

- 🎯 **Texte & Events anzeigen**: Beliebige Texte mit Farben und Animationen auf der Wortuhr anzeigen
- 🎵 **Audio abspielen**: Sounddateien von der SD-Karte abspielen (mit Audiomodul)
- 🎭 **Modi wechseln**: Zwischen 21 verschiedenen Display-Modi umschalten (Zeit, Wetter, Datum, etc.)
- 🎨 **Umfangreiche Anpassungen**: Farben, LED-Effekte, Animationen, Hintergrundoptionen
- ⚙️ **Automatische Helligkeit**: Adaptive Helligkeitsanpassung basierend auf Lichtsensor
- 📊 **Sensor-Daten**: WLAN-Signalstärke, BSSID, Temperatur, Luftfeuchte, Luftdruck und weitere Daten
- 💡 **Light-Entity**: Native Home Assistant Light-Integration für die Wortuhr-Beleuchtung
- 🔧 **Geräteverwaltung**: Reboot, WiFi-Reset, MP3-Reset
- 🔔 **Benachrichtigungen**: Notify-Service für einfache Text-Ausgabe

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

Die Integration registriert folgende Services für erweiterte Funktionalität:

### `wortuhr.show_text`
Zeigt Text mit optionaler Farbe und Buzzer an.

```yaml
service: wortuhr.show_text
data:
  text: "Hallo Welt"
  color: 1           # 0-24 (Farbnummern)
  buzzer: 2          # 0=aus, 1=kurz, 2=lang (optional)
```

### `wortuhr.show_event`
Zeigt ein Event mit optionalen Animationen und Audio an. Ideal für Benachrichtigungen mit Effekten.

```yaml
service: wortuhr.show_event
data:
  text: "Morgen wird Gelbe Tonne geleert"
  color: 5
  audio: 750                    # Audio-Datei-Nummer (optional)
  preani: "MUELL_GELB"         # Animation vor dem Text
  postani: "MUELL_GELB"        # Animation nach dem Text
```

### `wortuhr.play_audio`
Spielt eine Sounddatei von der SD-Karte ab.

```yaml
service: wortuhr.play_audio
data:
  soundfile: 819
  volume: 100        # 0-100 (optional)
```

### `wortuhr.set_mode`
Schaltet den Display-Modus um. Mit `sound: true` wird ein Ton abgespielt.

```yaml
service: wortuhr.set_mode
data:
  mode: 2            # 0-20 (siehe Modusliste)
  sound: true        # true/false (optional)
```

### `notify.wortuhr`
Einfacher Notify-Service zum Anzeigen von Nachrichten.

```yaml
service: notify.wortuhr
data:
  message: "Hallo Welt"
```

## Verfügbare Display-Modi

| Modus-ID | Beschreibung |
|----------|-------------|
| 0 | Zeit (Uhr) |
| 1 | Ansage / Text |
| 2 | Wochentag |
| 3 | Datum |
| 4 | Mondphase |
| 5 | Temperatur |
| 6 | Luftfeuchte |
| 7 | Luftdruck |
| 8 | Wetter |
| 12 | IP-Adresse |
| 13 | Testmodus |
| 18 | Timer |
| 20 | Aus |

*Hinweis: Die verfügbaren Modi können je nach Wortuhr-Firmware unterschiedlich sein.*

## Verfügbare Entitäten

Nach der Einrichtung stehen folgende Entitäten im Home Assistant zur Verfügung:

### 🔘 Button-Entitäten
- `Wortuhr reboot` - Startet die Wortuhr neu
- `Wortuhr WiFi Reset` - Setzt die WiFi-Konfiguration zurück
- `Wortuhr MP3 Reset` - Setzt den MP3-Player zurück
- `Wortuhr Nachricht anzeigen` - Zeigt die konfigurierte Nachricht an

### 📋 Select-Entitäten
- `Wortuhr LED Farbwechsel` - Effekt für LED-Farbwechsel
- `Wortuhr Minuten LED Farbwechsel` - Effekt für Minuten-LED
- `Wortuhr Minuten LED Farbe` - Farbe der Minuten-LED
- `Wortuhr Nachricht Textfarbe` - Textfarbe für Nachrichten
- `Wortuhr Event Pre-Animation` - Animation vor Event-Anzeige
- `Wortuhr Event Post-Animation` - Animation nach Event-Anzeige
- `Wortuhr Hintergrund Option` - Hintergrundeffekt-Einstellung

### 📝 Text-Entitäten
- `Wortuhr Nachricht` - Nachrichtentext zum Anzeigen

### 🔗 Zusammenhang zwischen Select- und Light-Entitäten
Die Light-Entitäten sind eng mit den Select-Entitäten verknüpft:
- `wortuhr_minutes` wird über die Select-Entität `wortuhr_minute_led_change_select` gesteuert. Der Select entscheidet, ob die Minuten-LEDs wie Hauptfarbe, aus oder anders behandelt werden.
- `wortuhr_background_light` ist mit `wortuhr_background_option` gekoppelt. Wenn die Hintergrund-Light eingeschaltet oder farblich angepasst wird, wird der zugehörige Hintergrund-Select passend synchronisiert.

Diese Verknüpfung ist wichtig, weil die Wortuhr-API die Beleuchtung über verschiedene Settings-Parameter steuert und die Selects dabei die zugehörigen Modi und Zustände festlegen.

### 💡 Light-Entitäten
- `Wortuhr` - Haupt-Beleuchtung der Wortuhr mit Helligkeitssteuerung und Farbwahl
- `Wortuhr Minuten` - Minuten-LED-Beleuchtung als reine Farb-Light-Entity
- `Hintergrund Farbe` - Hintergrundbeleuchtung als reine Farb-Light-Entity

> Hinweis zu den Farb-Lights: Die Entitäten `Wortuhr Minuten` und `Hintergrund` unterstützen keine Helligkeitssteuerung, weil die Wortuhr-API dafür keine Funktion bereitstellt. In Home Assistant lässt sich die Helligkeitssteuerung nicht deaktivieren, sie ist also ohne Funktion.

### 🔌 Switch-Entitäten
- `Wortuhr Es ist` - "Es ist" Text anzeigen/verbergen
- `Wortuhr Automatische Helligkeit` - Adaptive Helligkeit aktivieren/deaktivieren

### 📊 Sensor-Entitäten (Diagnostik)
- WLAN-Signalstärke (RSSI)
- WLAN BSSID
- WLAN SSID
- IP-Adresse
- Temperatur
- Luftfeuchte
- Luftdruck
- Windgeschwindigkeit
- UV-Index
- Weitere Wetterdaten und Systeminformationen

### 🔔 Notify-Service
- `notify.wortuhr` - Serviceaufruf zum Anzeigen von Text-Benachrichtigungen

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

### Benachrichtigung über Notify-Service

```yaml
automation:
  - alias: "Benachrichtigung auf Wortuhr"
    trigger:
      platform: state
      entity_id: binary_sensor.backdoor
      to: "on"
    action:
      - service: notify.wortuhr
        data:
          message: "Hintertür geöffnet"
```

### Helligkeit steuern

```yaml
script:
  dim_wortuhr:
    sequence:
      - service: light.turn_on
        target:
          entity_id: light.wortuhr
        data:
          brightness: 100  # 0-255
```

### Automatische Tagesgrüße

```yaml
automation:
  - alias: "Wortuhr Tagesgrüße"
    trigger:
      platform: time
      at:
        - "07:00:00"   # Morgens
        - "12:00:00"   # Mittags
        - "19:00:00"   # Abends
    action:
      - service: wortuhr.show_text
        data:
          text: "Guten Tag!"
          color: "{{ range(0, 25) | random }}"  # Zufällige Farbe
          buzzer: 1
      - delay:
          seconds: 5
      - service: wortuhr.set_mode
        data:
          mode: 0  # Zurück zur Uhr

## Tipps & erweiterte Konfiguration

### Farben-IDs (0-24)
Die verfügbaren Farbnummern entsprechen den vordefinierten Farben der Wortuhr. Die genaue Farbzuordnung kann je nach Firmware unterschiedlich sein. Experimen Sie, um die Farben zu finden, die Ihnen gefallen!

### Texte mit Sonderzeichen
Die Integration unterstützt umlaute und Sonderzeichen. Beachten Sie jedoch:
- Maximale Textlänge: ca. 28 Zeichen (abhängig vom Display)
- Sehr lange Texte werden automatisch gekürzt
- Manche Sonderzeichen werden vom Display möglicherweise nicht unterstützt

### Performance-Tipps
1. **Zu viele Automationen**: Begrenzen Sie die Häufigkeit der Text-Ausgaben
2. **Lange Verzögerungen vermeiden**: Mehrere schnelle Requests können die Wortuhr überlasten
3. **Zeitbasierte Automationen**: Nutzen Sie `delay` oder `wait_for_trigger` um Requests zu verteilen

### Mehrere Wortuhren
Wenn Sie mehrere Wortuhren haben, können Sie diese über separate Home Assistant Integrationen hinzufügen. Jede Integration erstellt ihre eigenen Entitäten mit eindeutigem Präfix.

### Debug-Modus
Um HTTP-Requests zu debuggen, können Sie folgende Automation nutzen:

```yaml
automation:
  - alias: "Wortuhr Debug"
    trigger:
      platform: homeassistant
      event: start
    action:
      - service: logger.set_level
        data:
          wortuhr: DEBUG
```

## Fehlerbehebung

### Problem: Integration lässt sich nicht hinzufügen
- **Prüfpunkte:**
  - IP-Adresse der Wortuhr ist korrekt
  - Wortuhr ist im Netzwerk erreichbar und angeschaltet
  - Firewall blockiert keine Zugriffe auf Port 80 (HTTP)
  - Wortuhr und Home Assistant sind im gleichen Netzwerk
- **Lösungsvorschläge:**
  - Home Assistant neu starten
  - Wortuhr neu starten (Power-Reset)
  - IP-Adresse in der Netzwerk-Einstellung überprüfen

### Problem: Serviceaufrufe funktionieren nicht / HTTP-Fehler
- **Prüfpunkte:**
  - In Home Assistant Logs nach Fehlern suchen (Settings → System → Logs)
  - Wortuhr noch angeschaltet?
  - Netzwerkverbindung noch stabil?
- **Lösungsvorschläge:**
  - Serviceparameter überprüfen (siehe Beispiele oben)
  - Wortuhr ist ggf. überlastet → kurz warten
  - HTTP-Request direkt testen: `http://192.168.X.X/showText?text=Test&color=1`

### Problem: Entitäten werden nicht angezeigt
- **Lösungsvorschläge:**
  - Integration erfolgreich konfiguriert? (Geräte & Services > Integrationen)
  - Entitäten sind teilweise deaktiviert (standardmäßig deaktivierte Sensoren aktivieren)
  - Home Assistant neu starten

### Problem: Licht-Entität funktioniert nicht
- Wortuhr-Firmware muss Unterstützung für Helligkeitsregelung haben
- LED-Modul muss installiert sein
- Bei `Wortuhr Minuten` und `Hintergrund Farbe` ist die Bedienung bewusst auf Farbwahl beschränkt, weil die API keine Brightness-Unterstützung bietet

## Bekannte Einschränkungen

- Wortuhr und Home Assistant müssen sich im gleichen Netzwerk befinden
- HTTP-API unterstützt aktuell keine Authentifizierung (lokal sicher, aber nicht remote)
- Die verfügbaren Animation, Modi und Farben können je nach Wortuhr-Firmware unterschiedlich sein
- Maximale Textlänge beträgt in der Regel 28 Zeichen (abhängig von Displaygröße)

## Zusätzliche Ressourcen

### Offizielle Wortuhr Website
- [Wortuhr von Daniel Stingl](https://www.wortuhr.daniel-stingl.de/) - Offizielle Seite mit Hardware-Informationen
- [Wortuhr API Dokumentation](https://www.wortuhr.daniel-stingl.de/) - HTTP-API Dokumentation
- [Community Forum](https://www.wortuhr.daniel-stingl.de/) - Austausch mit anderen Benutzern

### Home Assistant Dokumentation
- [Home Assistant Integration Development](https://developers.home-assistant.io/docs/creating_integration_manifest/)
- [Home Assistant Services](https://www.home-assistant.io/docs/scripts/service-calls/)
- [Home Assistant Automations](https://www.home-assistant.io/docs/automation/)

## Support & Community

- 🐛 **Bug-Reports**: [GitHub Issues](https://github.com/pfehr/Wortuhr_HA/issues)
- 💡 **Feature-Requests**: [GitHub Issues](https://github.com/pfehr/Wortuhr_HA/issues)
- 💬 **Diskussionen**: [GitHub Discussions](https://github.com/pfehr/Wortuhr_HA/discussions)
- ⭐ **Gefällt dir die Integration?** Gib dem Repo einen Star auf GitHub!

## Lizenz

MIT License
