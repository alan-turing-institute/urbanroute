import matplotlib.pyplot as plt
import math
from shapely.geometry import Point, Polygon
import shapely.affinity
from descartes import PolygonPatch

GM = (math.sqrt(5)-1.0)/2.0
W = 8.0
H = W*GM
SIZE = (W, H)

BLUE = '#6699cc'
GRAY = '#999999'
DARKGRAY = '#333333'
YELLOW = '#ffcc33'
GREEN = '#339933'
RED = '#ff3333'
BLACK = '#000000'

COLOR_ISVALID = {
    True: BLUE,
    False: RED,
}


def plot_line(ax, ob, color=GRAY, zorder=1, linewidth=3, alpha=1):
    x, y = ob.xy
    ax.plot(x, y, color=color, linewidth=linewidth,
            solid_capstyle='round', zorder=zorder, alpha=alpha)


def plot_coords(ax, ob, color=GRAY, zorder=1, alpha=1):
    x, y = ob.xy
    ax.plot(x, y, 'o', color=color, zorder=zorder, alpha=alpha)


def color_isvalid(ob, valid=BLUE, invalid=RED):
    if ob.is_valid:
        return valid
    else:
        return invalid


def color_issimple(ob, simple=BLUE, complex=YELLOW):
    if ob.is_simple:
        return simple
    else:
        return complex


def plot_line_isvalid(ax, ob, **kwargs):
    kwargs["color"] = color_isvalid(ob)
    plot_line(ax, ob, **kwargs)


def plot_line_issimple(ax, ob, **kwargs):
    kwargs["color"] = color_issimple(ob)
    plot_line(ax, ob, **kwargs)


def plot_bounds(ax, ob, zorder=1, alpha=1):
    x, y = zip(*list((p.x, p.y) for p in ob.boundary))
    ax.plot(x, y, 'o', color=BLACK, zorder=zorder, alpha=alpha)


def add_origin(ax, geom, origin):
    x, y = xy = affinity.interpret_origin(geom, origin, 2)
    ax.plot(x, y, 'o', color=GRAY, zorder=1)
    ax.annotate(str(xy), xy=xy, ha='center',
                textcoords='offset points', xytext=(0, 8))


def set_limits(ax, x0, xN, y0, yN):
    ax.set_xlim(x0, xN)
    ax.set_xticks(range(x0, xN+1))
    ax.set_ylim(y0, yN)
    ax.set_yticks(range(y0, yN+1))
    ax.set_aspect("equal")


source = (-4.85624511894443, 85.1837967179202)
dest = (-19.85624511894443 + 1, 70.1837967179202)
theta = math.atan((dest[1]-source[1])/(dest[0]-source[0]))
tau = 1.1
distance = math.sqrt((dest[1]-source[1])**2 + (dest[0]-source[0])**2) * tau
print(distance)
b = (dest[1]+source[1])/2
a = (dest[0]+source[0])/2
A = (tau/2) * math.sqrt((dest[1] - source[1])**2 + (dest[0] - source[0])**2)
B = math.sqrt(A**2 - ((dest[1] - source[1])**2 + (dest[0] - source[0])**2)/4)
points = [Point(source[0], source[1]),
          Point(dest[0], dest[1])]
box = Polygon([(a + math.sqrt(A**2 * math.cos(theta)**2 + B ** 2 * math.sin(theta)**2),
                b + math.sqrt(A**2 * math.sin(theta)**2 + B ** 2 * math.cos(theta)**2)),
               (a + math.sqrt(A**2 * math.cos(theta)**2 + B ** 2 * math.sin(theta)**2),
                b - math.sqrt(A**2 * math.sin(theta)**2 + B ** 2 * math.cos(theta)**2)),
               (a - math.sqrt(A**2 * math.cos(theta)**2 + B ** 2 * math.sin(theta)**2),
                b - math.sqrt(A**2 * math.sin(theta)**2 + B ** 2 * math.cos(theta)**2)),
               (a - math.sqrt(A**2 * math.cos(theta)**2 + B ** 2 * math.sin(theta)**2),
                b + math.sqrt(A**2 * math.sin(theta)**2 + B ** 2 * math.cos(theta)**2))])
xs = [point.x for point in points]
ys = [point.y for point in points]

# 1st elem = center point (x,y) coordinates
# 2nd elem = the two semi-axis values (along x, along y)
# 3rd elem = angle in degrees between x-axis of the Cartesian base
#            and the corresponding semi-axis
print(theta)
ellipse = ((a, b), (B, A), math.degrees(-theta))

# Let create a circle of radius 1 around center point:
circ = shapely.geometry.Point(ellipse[0]).buffer(1)

# Let create the ellipse along x and y:
ell = shapely.affinity.scale(circ, int(ellipse[1][0]), int(ellipse[1][1]))

# Let rotate the ellipse (clockwise, x axis pointing right):
ellr = shapely.affinity.rotate(ell, ellipse[2])

# If one need to rotate it clockwise along an upward pointing x axis:
elrv = shapely.affinity.rotate(ell, 90-ellipse[2])
# According to the man, a positive value means a anti-clockwise angle,
# and a negative one a clockwise angle.
plt.scatter(xs, ys)
plt.plot(*box.exterior.xy)
ax = plt.gca()
patch = PolygonPatch(elrv, fc=GREEN, ec=GRAY, alpha=0.5, zorder=2)
ax.add_patch(patch)
#set_limits(ax, -10, 10, -10, 80)
plt.show()
