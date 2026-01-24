from PIL import Image

side = 16
image = Image.open("../res/hero.png")
image.crop((4, 4, 20, 20)).save("../res/hero_animation/default.png")
for i in range(4):
    frame = image.crop((4 * (i + 1) + 16 * i, 24, 4 * (i + 1) + 16 * i + 16, 40))
    frame.save(f"../res/hero_animation/right{i}.png")
    frame.transpose(Image.FLIP_LEFT_RIGHT).save(f"../res/hero_animation/left{i}.png")
for i in range(4):
    image.crop((4 * (i + 1) + 16 * i, 4, 4 * (i + 1) + 16 * i + 16, 20)).save(
        f"../res/hero_animation/down{i}.png"
    )
for i in range(4):
    image.crop((4 * (i + 1) + 16 * i, 84, 4 * (i + 1) + 16 * i + 16, 100)).save(
        f"../res/hero_animation/up{i}.png"
    )
ghost = Image.open("../res/ghost.png")
ghost.crop((0, 0, 16, 16)).save("../res/ghost_animation/1.png")
ghost.crop((18, 0, 34, 16)).save("../res/ghost_animation/2.png")
