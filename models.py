import numpy as np
from math import sin, cos
from tasks import DrawLineTask

DTYPE = np.float32
MIN_ZOOM = 100
MAX_ZOOM = 100000

def getRotMatX(a):
    return np.array([
        [ 1, 0, 0 ],
        [ 0, cos(a), -sin(a) ],
        [ 0, sin(a), cos(a) ]
    ], dtype=DTYPE)
    
def getRotMatY(a):
    return np.array([
        [ cos(a), 0, sin(a)],
        [ 0, 1, 0 ],
        [ -sin(a), 0, cos(a) ]
    ], dtype=DTYPE)

def getRotMatZ(a):
    return np.array([
        [ cos(a), -sin(a), 0 ],
        [ sin(a), cos(a), 0 ],
        [ 0, 0, 1 ]
    ], dtype=DTYPE)


class Line():
    def __init__(self, x1, y1, z1, x2, y2, z2, color):
        self.start = np.array(
            [ x1, y1, z1 ],
            dtype=DTYPE)
        self.end = np.array(
            [ x2, y2, z2 ],
            dtype=DTYPE)
        self.color = color

class Cuboid():
    """
    Representation of cuboid
    """

    def __init__(self, x, y, z, a, b, c, color):
        """
        (x, y, z) - position of first vertex
        (a, b, c) - side lengths
        """

        vertices = np.array([[x, y, z]]*8, dtype=DTYPE)
        for i in range(4):
            vertices[1 + i + 2 * int(i/2)][0] += a
            vertices[2 + 2 * int(i/2) + i][1] += b
            vertices[4 + i               ][2] += c

        self.vertices = vertices
        self.color = color

    #----------------------------
    # rotations

    def rotateX(self, angle):
        mat = getRotMatX(angle)
        for i in range(len(self.vertices)):
            self.vertices[i] = np.matmul(self.vertices[i], mat)

    def rotateY(self, angle):
        mat = getRotMatY(angle)
        for i in range(len(self.vertices)):
            self.vertices[i] = np.matmul(self.vertices[i], mat)

    def rotateZ(self, angle):
        mat = getRotMatZ(angle)
        for i in range(len(self.vertices)):
            self.vertices[i] = np.matmul(self.vertices[i], mat)

    def rotate(self, xangle, yangle, zangle):
        xmat = getRotMatX(xangle)
        ymat = getRotMatY(yangle)
        zmat = getRotMatZ(zangle)
        rmat = np.matmul(xmat, np.matmul(zmat , ymat))
        for i in range(len(self.vertices)):
            self.vertices[i] = np.matmul(self.vertices[i], rmat)

    #----------------------------
    # translations

    def translateX(self, val):
        for i in range(len(self.vertices)):
            self.vertices[i][0] += val

    def translateY(self, val):
        for i in range(len(self.vertices)):
            self.vertices[i][1] += val
    
    def translateZ(self, val):
        for i in range(len(self.vertices)):
            self.vertices[i][2] += val

    def translate(self, x, y, z):
        for i in range(len(self.vertices)):
            self.vertices[i] += [x, y, z]

    #----------------------------
    # getting lines out of cuboid

    def getLines(self):
        lines = []
        for i in range(4):
            # front rect
            lines.append(
                Line(
                    self.vertices[i][0],
                    self.vertices[i][1],
                    self.vertices[i][2],
                    self.vertices[(i + 1) % 4][0],
                    self.vertices[(i + 1) % 4][1],
                    self.vertices[(i + 1) % 4][2],
                    self.color
                    )
            )

            # back rect
            lines.append(
                Line(
                    self.vertices[i % 4 + 4][0],
                    self.vertices[i % 4 + 4][1],
                    self.vertices[i % 4 + 4][2],
                    self.vertices[(i + 1) % 4 + 4][0],
                    self.vertices[(i + 1) % 4 + 4][1],
                    self.vertices[(i + 1) % 4 + 4][2],
                    self.color
                    )
            )

            # rect connections
            lines.append(
                Line(
                    self.vertices[i][0],
                    self.vertices[i][1],
                    self.vertices[i][2],
                    self.vertices[i + 4][0],
                    self.vertices[i + 4][1],
                    self.vertices[i + 4][2],
                    self.color
                    )
            )

        return lines

            
class Camera():
    """
    Reprenetation of camera and kind of scene (also holds scene entities)
    """

    zoom = 300
    cuboids = [
        Cuboid(-150, 200, 100, 100, -100, 100, (255, 255, 255)),
        Cuboid(50, 200, 100, 100, -200, 100, (255, 255, 255)),
        Cuboid(50, 200, 300, 100, -300, 100, (255, 255, 255)),
        Cuboid(-150, 200, 300, 100, -400, 100, (255, 255, 255))
    ]

    def getProjectionMatrix(self, z):
        return np.array([
            [ self.zoom/z, 0, 0 ],
            [ 0, self.zoom/z, 0 ],
            [ 0, 0, 0 ]
            ], dtype=DTYPE)

    #----------------------------
    # rotations

    def rotateX(self, angle):
        for cuboid in self.cuboids:
            cuboid.rotateX(-angle)

    def rotateY(self, angle):
        for cuboid in self.cuboids:
            cuboid.rotateY(-angle)

    def rotateZ(self, angle):
        for cuboid in self.cuboids:
            cuboid.rotateZ(-angle)

    #----------------------------
    # translations

    def translateX(self, val):
        for cuboid in self.cuboids:
            cuboid.translateX(-val)

    def translateY(self, val):
        for cuboid in self.cuboids:
            cuboid.translateY(-val)

    def translateZ(self, val):
        for cuboid in self.cuboids:
            cuboid.translateZ(-val)

    #----------------------------
    # zooming

    def changeZoom(self, val):
        self.zoom += val
        if self.zoom < MIN_ZOOM:
            self.zoom = MIN_ZOOM
        elif self.zoom > MAX_ZOOM:
            self.zoom = MAX_ZOOM

    #----------------------------
    # getting line draw tasks

    def makeTaskFromLine(self, line: Line):
        if line.start[2] <= 0 or line.end[2] <=0:
            return None
            
        mat1 = self.getProjectionMatrix(line.start[2])
        mat2 = self.getProjectionMatrix(line.end[2])

        start = np.matmul(line.start, mat1)
        end = np.matmul(line.end, mat2)

        return DrawLineTask(start, end, line.color)

    def getTasks(self):
        lines = []

        for cuboid in self.cuboids:
            for line in cuboid.getLines():
                lines.append(line)

        tasks = []

        for line in lines:
            task = self.makeTaskFromLine(line)
            if task:
                tasks.append(task)

        return tasks

    

