"""Regenerate every image patch (run after extract.py when the game updates)."""
import os

from paths import ART

if __name__ == "__main__":
    patches = os.path.join(ART, "patches.json")
    if os.path.exists(patches):
        os.remove(patches)
    import titlescreen
    import art_billboard
    import art_maps
    titlescreen.main()
    art_billboard.main()
    art_maps.main()
