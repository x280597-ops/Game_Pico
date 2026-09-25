import Module
display=Module.display()
def draw_map(tilelist,imagelist):
    draw_x=0
    draw_y=0
    scale=len(tilelist)
    for write_y in tilelist:
        draw_x=0
        size=7
        for write_x in write_y:
            display.draw_image(draw_x*scale*size,draw_y*scale*size,imagelist[write_x],size)
            draw_x+=1
        draw_y+=1
    