from PIL import Image
#RECORTAR PNG
image_png = Image.open("test.png")
image_png.getbbox()  # (64, 89, 278, 267)
image_png = image_png.crop(image_png.getbbox())
#CONVERTIR A JPG
image_png.load() # required for png.split()
background = Image.new("RGB", image_png.size, (255, 255, 255))
background.paste(image_png, mask=image_png.split()[3]) # 3 is the alpha channel
background.save('test_jpg.jpg', 'JPEG', quality=80)