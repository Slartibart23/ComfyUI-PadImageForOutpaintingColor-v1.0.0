# ComfyUI – Pad Image For Outpainting (Color)

**Version 1.0.0**

Wie die Standard-Node "Pad Image For Outpainting", aber die neue Fläche wird
mit einer frei wählbaren Farbe gefüllt. In der Node gibt es dafür einen
Farbpicker, daneben wird der Hex-Code angezeigt und kann auch direkt
eingetippt werden.

## Installation

### Manuell
```
cd ComfyUI/custom_nodes
git clone https://github.com/DEIN-GITHUB-NAME/ComfyUI-PadImageForOutpaintingColor
```
ComfyUI neu starten, im Browser einmal Hard-Reload (Strg+F5).

### Über ComfyUI-Manager
"Install via Git URL" → Repo-URL eintragen.

## Node
Kategorie: `image` → **Pad Image For Outpainting (Color)**

| Eingang     | Beschreibung                                  |
|-------------|-----------------------------------------------|
| image       | Eingangsbild                                   |
| left/top/right/bottom | Erweiterung in Pixeln (Schritt 8)    |
| feathering  | Weiche Kante der Maske (wie Original)          |
| color       | Füllfarbe als Hex, z. B. `#FF8800`             |

Ausgänge: `IMAGE`, `MASK`

Ungültige Hex-Werte werden in der Node rot markiert und fallen beim
Ausführen auf Grau (`#808080`) zurück.

## Lizenz
MIT
