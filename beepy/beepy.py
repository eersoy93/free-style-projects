import pyxel

class App:
    def __init__(self):
        pyxel.init(160, 120, title="Beepy")
        pyxel.run(self.update, self.draw)

    def update(self):
        notes = [
            ("A3", 0), ("B3", 1), ("C3", 2), ("D3", 3),
            ("E3", 4), ("F3", 5), ("G3", 6)
        ]

        for note, i in notes:
            pyxel.sounds[i].set(note, "T", "7", "F", 10)

        for i in range(7):
            if pyxel.btnp(getattr(pyxel, f"KEY_{i+1}")):
                pyxel.play(0, i)

    def draw(self):
        pyxel.cls(0)
        if (pyxel.frame_count // 30) % 2 == 0:
            pyxel.text(40, 55, "Press 1 to 7 to beeps!", 7)

        if pyxel.play_pos(0) is not None:
            pyxel.cls(0)
            t = pyxel.frame_count
            for i in range(3):
                radius = 10 + i*10 + abs(pyxel.sin(t*10)) * 5
                pyxel.circb(80, 60, radius, 8 + i)
            pyxel.flip()

App()
