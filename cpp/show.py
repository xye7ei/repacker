
def color(b, h):
    import math
    if b > h: c = b / h
    else:     c = - h / b
    fei = math.atan(c)
    red = int(50 * fei + 128) # c[max] ~= 100, 50*atan(c) + 128 in [50, 206]
    grn = int( 5 * fei + 128)
    blu = int( 5 * fei + 128)
    fill = "#%02X%02X%02X" % (red, grn, blu)
    return fill


def show(src):

    with open(src) as o:

        tps = eval(o.read())

        import matplotlib.pyplot as plt
        import matplotlib.patches as pch
        import io

        plt.rc('font')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for (x1, y1), (x2, y2) in tps:
            b, h = x2 - x1, y2 - y1
            p_r = pch.Rectangle((x1, y1),
                                b, h,
                                edgecolor='#101010',
                                alpha=0.9,
                                facecolor=color(b, h))
            ax.add_patch(p_r)

        ax.axis('equal')
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')

        plt.plot()
        plt.show()


def figure(fname, outname):

    from PIL import Image, ImageFont, ImageDraw

    with open(fname, 'r') as o:
        rects = eval(o.read())
    
    x_max = y_max =0
    for (x1, y1), (x2, y2) in rects:
        x_max = max(x_max, x2)
        y_max = max(y_max, y2)
        
    x_max = int(x_max * 1.02)
    y_max = int(y_max * 1.02)

    im = Image.new('RGB', (x_max, y_max), (255, 255, 255))
    dr = ImageDraw.Draw(im)

    for (x1, y1), (x2, y2) in rects:
        b = x2 - x1; h = y2 - y1
        dr.rectangle(((x1, y_max - y1),
                      x2, y_max - y2),
                     fill=color(b, h),
                     outline='black')
    im.save(outname)


# fn = 'test_rand_1.py'
# show(fn)

# fn = 'test_rand_less.py'
# show(fn)

fn = 'test_rand_more.py'
# show(fn)
figure(fn, 'test_rand_more.png')
