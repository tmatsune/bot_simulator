from settings import * 

def get_image(path: str, scale: list):
    image: pg.image = pg.image.load(path)
    image = pg.transform.scale( image, (scale[0], scale[1]))
    return image

 
