import math

##constants

#technically these get updated, but only once. they are used as constants for the rest of the module
SCRN_SIZE = None
SCRN_SIZE_PATH = "../data/screen_size.txt"
CENTRE = None

# the matrix which represents no transformation
IDENTITY_MATRIX = [[1,0,0],[0,1,0],[0,0,1]] 


##functions
def multmat(a,b):
    #a and b are 3x3 matrices. returns a x b
    result = [[0,0,0],[0,0,0],[0,0,0]]

    for i in range(3):
        for j in range(3): 
            for k in range(3):
                result[i][j] += a[i][k]*b[k][j]

    return result

def vector_add(a,b):
    #element-wise addition of vectors a and b
    result = [0,0,0]
    for i in range(3):
        result[i] = a[i]+b[i]
    return result

def vector_scale(s, v):
    #multiplies vector v by scalar s
    result = [0,0,0]
    for i in range(3):
        result[i] = s*v[i]
    return result

def apply_matrix(m, v):
    #m is a matrix, v is a vector (3x3 and 3x1). returns m x v
    result = [0,0,0]
    for i in range(3):
        for j in range(3):
            result[i] += v[j]*m[j][i]
    return result

def rotation_matrix(angle, axis):
    #angle is in degrees, axis is a string (x, y, or z)
    a = math.radians(angle)
    if axis == 'x':
        return [[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]]
    
    if axis == 'y':
        return [[math.cos(a),0,-math.sin(a)],[0,1,0],[math.sin(a),0,math.cos(a)]]

    if axis == 'z':
        return [[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]

def get_resolution():
    #gets the resulotion from screen_size.txt
    f = open(SCRN_SIZE_PATH, 'r')
    result = tuple(map(int, f.read().split("x")))
    f.close()
    return result

def project2d(v):
    #projects 3D coordinates onto 2 dimensions
    x = v[0]*SCRN_SIZE[0]/v[2] + CENTRE[0]
    y = v[1]*SCRN_SIZE[0]/v[2] + CENTRE[1]
    return [int(x),int(y)]

#the draw functions - these get assigned when engine is imported and they vary with each graphics module used
point_draw_function = None
line_draw_function = None

##set up screen size
SCRN_SIZE = get_resolution()
CENTRE = [SCRN_SIZE[0]//2, SCRN_SIZE[1]//2]


##classes
class Camera:
    def __init__(self, pos, rots):
        self.pos = pos
        self.spd = [0,0,0]
        self.angle = rots
        self.xrotation = None
        self.yrotation = None

    def update(self):
        #updates the self.pos, self.xrotation, and self.yrotation to be correct
        vect = apply_matrix(rotation_matrix(-self.angle[1], 'y'), self.spd)
        self.pos = vector_add(self.pos, vect)
        self.xrotation = rotation_matrix(self.angle[0], 'x')
        self.yrotation = rotation_matrix(self.angle[1], 'y')

    def rotate(self,new):
        #adds new to self.pos
        self.angle = vector_add(self.angle, vector_scale(-1,new))
        

class Graph:
    # pointlist is a 2d array like [[x1, y1, z1], [x2, y2, z2], ...]
    # colour is an rgb tuple
    def __init__(self, pointlist, colour):
        self.coords = pointlist
        
        # indicies of self.coords which make an edge
        self.edges = [] 
        
        self.colour = colour

        # a matrix used to transform the position vectors in self.coords
        self.transformation = IDENTITY_MATRIX 

    # multiplies matrix with self.transformation
    def add_transformation(self, matrix): 
        self.transformation = multmat(self.transformation, matrix)

    def get_transformation(self):
        newlist = []
        for coord in self.coords:
            newlist.append(apply_matrix(self.transformation, coord))
        return newlist

    def get_translation(self, vector):
        new = self.coords
        for i in range(len(new)):
            new[i] = vector_add(new[i], vector)
        return new

    def translate(self, vector):
        self.coords = self.get_translation(vector)

    def rotate(self, angles, centre_of_rotation):
        self.translate(vector_scale(-1, centre_of_rotation))
        self.transformation = IDENTITY_MATRIX
        self.add_transformation(rotation_matrix(angles[0], 'x'))
        self.add_transformation(rotation_matrix(angles[1], 'y'))
        self.add_transformation(rotation_matrix(angles[2], 'z'))
        self.coords = self.get_transformation()
        self.translate(centre_of_rotation)

    def scale(self, factors, centre_of_scale):
        self.translate(vector_scale(-1, centre_of_scale))
        
        self.transformation = IDENTITY_MATRIX
        self.add_transformation([[factors[0],0,0],[0,factors[1],0],[0,0,factors[2]]])
        self.coords = self.get_transformation()
        self.translate(centre_of_scale)
        
    # creates an edge between the vertices with indicies a and b in self.coords        
    def connect(self, a, b): 
        self.edges.append([a,b])
        
    # draws a 2d representation of the graph onto the surface
    def draw(self, camera, lines=True, circles=True): 
        self.transformation = IDENTITY_MATRIX
        
        #apply rotation
        self.add_transformation(camera.yrotation)
        self.add_transformation(camera.xrotation)
        
        #get set of transformed vertices, and apply translation
        transformed = self.get_transformation()
        pos = apply_matrix(self.transformation, camera.pos)
        transformed = [vector_add(pos, i) for i in transformed]
        points = []

        #project onto 2d space
        for coord in transformed:
            if (coord[2] + CENTRE[0] > 5 or coord[2] + CENTRE[0] < -5) and coord[2] > 0:
                points.append(project2d(coord))
            else:
                points.append(None)

        #draw the shapes
        if circles:
            for point in points:
                if point != None:
                    try:
                        point_draw_function(self.colour, point)
                    except:
                        pass    
        if lines:
            for edge in self.edges:
                point1 = points[edge[0]]
                point2 = points[edge[1]]
                if point1 != None and point2 != None:
                    try:
                        line_draw_function(self.colour, point1, point2)
                    except:
                        pass

class Cuboid(Graph):
    #x,y,z are the coordinates of the top-left-nearest corner
    #w,h,d are the width, height, and depth
    def __init__(self, x,y,z, w,h,d, colour):
        template = [[0,0,0],[1,0,0],[0,1,0],[0,0,1],[1,1,0],[0,1,1],[1,0,1],[1,1,1]]

        coords = []
        for i in template:#adjusts template to be the correct coordinates
            new = [x,y,z]         
            if i[0] == 1:
                new[0] += w
            if i[1] == 1:
                new[1] += h
            if i[2] == 1:
                new[2] += d
            coords.append(new)

        Graph.__init__(self, coords, colour)#initialises a graph with the correct coordinates

        #find all edges
        for i in range(8):
            a = template[i]
            for j in range(i,8):
                b = template[j]
                diff = 0
                for k in range(3):
                    if a[k] != b[k]:
                        diff += 1
                if diff == 1:
                    self.connect(i,j)
            
class Tetrahedron(Graph):
    def __init__(self, c1, c2, c3, size, colour):
        coords = []
        template = [[ math.sqrt(8/9), 0 , -1/3 ],
                    [-math.sqrt(2/9), math.sqrt(2/3), -1/3 ],
                    [-math.sqrt(2/9), -math.sqrt(2/3), -1/3 ],
                    [0 , 0 , 1 ]]
        for i in template:
            new = [size, size, size]
            for j in range(3):
                new[j] *= i[j]
            new[0] += c1
            new[1] += c2
            new[2] += c3
            coords.append(new)
        Graph.__init__(self, coords, colour)
        self.edges = [[0,1],[0,2],[0,3],[1,1],[1,2],[1,3],[2,3]]
        
class Line(Graph):
    def __init__(self, point, direction, n, colour):
        coords = []
        for l in range(n):
            coords.append([point[0]+l*direction[0],point[1]+l*direction[1],point[2]+l*direction[2]])

        Graph.__init__(self, coords, colour)
        for i in range(n-1):
            self.connect(i, i+1)
