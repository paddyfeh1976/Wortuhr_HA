"""Helper class to map arbitrary RGB colors to Wortuhr COLOR_OPTIONS."""
from __future__ import annotations
import math
from .const import COLOR_OPTIONS

# Definition von ungefähren RGB-Richtwerten für deine COLOR_OPTIONS-Namen
RGB_REFERENCE = {
    "Weiß": (255, 255, 255),
    "Rot": (255, 0, 0),
    "Rot 75%": (192, 0, 0),
    "Rot 50%": (128, 0, 0),
    "Orange": (255, 165, 0),
    "Gelb": (255, 255, 0),
    "Gelb 75%": (192, 192, 0),
    "Gelb 50%": (128, 128, 0),
    "Gelb-Grün": (173, 255, 47),
    "Grün": (0, 255, 0),
    "Grün 75%": (0, 192, 0),
    "Grün 50%": (0, 128, 0),
    "Mintgrün": (152, 251, 152),
    "Cyan": (0, 255, 255),
    "Cyan 75%": (0, 192, 192),
    "Cyan 50%": (0, 128, 128),
    "Leicht Blau": (173, 216, 230),
    "Blau": (0, 0, 255),
    "Blau 75%": (0, 0, 192),
    "Blau 50%": (0, 0, 128),
    "Violett": (238, 130, 238),
    "Magenta": (255, 0, 255),
    "Magenta 75%": (192, 0, 192),
    "Magenta 50%": (128, 0, 128),
    "Pink": (255, 192, 203),
}

class WortuhrColorMapper:
    """Maps continuous RGB colors to fixed device colors."""

    @staticmethod
    def rgb_distance(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
        """Calculates the Euclidean distance between two colors."""
        return math.sqrt(
            (rgb1[0] - rgb2[0]) ** 2 +
            (rgb1[1] - rgb2[1]) ** 2 +
            (rgb1[2] - rgb2[2]) ** 2
        )

    @classmethod
    def find_closest_color(cls, target_rgb: tuple[int, int, int]) -> tuple[str, int, tuple[int, int, int]]:
        """
        Finds the closest available color option.
        Returns: (Color Name, API ID, Matched RGB Tuple)
        """
        closest_name = "Weiß"
        min_distance = float("inf")

        for name, ref_rgb in RGB_REFERENCE.items():
            # Überspringe Namen, die nicht in den echten COLOR_OPTIONS existieren
            if name not in COLOR_OPTIONS:
                continue
                
            distance = cls.rgb_distance(target_rgb, ref_rgb)
            if distance < min_distance:
                min_distance = distance
                closest_name = name

        api_id = COLOR_OPTIONS[closest_name]
        matched_rgb = RGB_REFERENCE[closest_name]
        
        return closest_name, api_id, matched_rgb