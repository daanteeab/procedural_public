from math import *
from random import random, randrange
from numpy import *
from ursina import *
from ursina.shaders import lit_with_shadows_shader

def generate_uvs(verts):
    uvs = ()
    print("Generating uvs")
    for x in range(len(verts)):
        uvs += (1,0),
    return uvs

def generate_colors(verts, color_list):
    colors = ()
    for x in range(len(verts)):
        #print(x, "color")
        colors += random.choice(color_list),
    return colors


class ProceduralTree():
    def __init__(self, origin = None, generations = None, segments = None):
        '''Origin takes a tuple of 3d coordinates and is the origin of the tree.
        
        Generations specifies how many iterations of the branch functions is run, if your system is time sensitive i recommend max 5. Pass it as an integer.

        Segments specifies for how many segments a branch is propagated, assigning a random integer to this for each tree makes for some great variation,
        pass this argument as an integer.
        
        EXAMPLE! Instanciate the class as following in order to generate a tree:


        ProceduralTree(origin = (0,0,0), generations = 5, segments = 5)).generate()

        OR:

        someVarName = ProceduralTree(origin = (0,0,0), generations = 5, segments = 5))

        someVarName.generate()

        If you want to edit something in the mesh after the fact, you can get the entities created with the attributes YourclassInstance.tree_ent for the tree entity, and YourclassInstance.leafs_ent for the leaf entity.'''

        '''Origin argument passed to the class'''
        self.origin = origin
        '''This dict hold the base vertices of the tree'''
        self.branch_log = {}
        '''This dict hold the new vector, origin and index of each new generation of branches'''
        self.generation_ov = {"0":[((0,0,0),(0,1,0),(0))]}
        '''This dict holds the vertices of the mesh'''
        self.mesh_log = {}
        '''This dict is a graph representation of the tree with a one-way adjacency list to keep track of each vertice parent vertice,
        this is important for generating the triangles'''
        self.verticeGraph = {}
        if self.origin is not None:
            self.generation_ov = {"0":[(origin,(0,1,0),(0))]}

        '''Arguments passed to the class'''
        self.generations = generations
        self.segments = segments

        '''Output entities'''
        self.tree_ent = None
        self.leafs_ent = None

    def branch(self, generation, segments, branch_log, generation_ov, flag, someVerticeCounter):
        '''Setup, formatting'''
        generation = str(generation)
        branch_log[generation] = ()
        self.mesh_log[generation] = ()
        generation_ov[str(int(generation)+1)] = []
        edge_vectors = []
        edge_index = []
        for y in range(len(generation_ov[generation])):
            '''This is the current base point'''
            last_vector = generation_ov[generation][y][0]
            last_index = generation_ov[generation][y][2]
            for x in range(segments):
                '''Adding new point to branch_log'''
                branch_log[generation] += (add(last_vector,generation_ov[generation][y][1])),
                '''This scalar below is to make sure the trees preceived radius reduces per generation to finally close up in on itself for the last segment in the last generation'''
                radiusMultiplierScalar = (1-(int(generation)*(1/self.generations))-(((1/self.generations)/self.segments)*x))
                '''Generating volume points from base point, using cross product'''
                c1 = Vec3(tuple(cross(generation_ov[generation][y][1],(1,0,0)))).normalized()*radiusMultiplierScalar
                c2 = Vec3(tuple(cross(generation_ov[generation][y][1],(0,0,1)))).normalized()*radiusMultiplierScalar
                c3 = Vec3(tuple(cross(generation_ov[generation][y][1],(-1,0,0)))).normalized()*radiusMultiplierScalar
                c4 = Vec3(tuple(cross(generation_ov[generation][y][1],(0,0,-1)))).normalized()*radiusMultiplierScalar
                '''Changing base point to get correct offset origin'''
                last_vector = branch_log[generation][-1]
                '''Adding points to mesh using the new origin of offset'''
                self.mesh_log[generation] += (add(last_vector,c1)),
                self.mesh_log[generation] += (add(last_vector,c2)),
                self.mesh_log[generation] += (add(last_vector,c3)),
                self.mesh_log[generation] += (add(last_vector,c4)),
                if x == 0:
                    self.verticeGraph[str(someVerticeCounter)] = [last_index]
                if someVerticeCounter == 0:
                    self.verticeGraph[str(someVerticeCounter)] = []
                if someVerticeCounter != 0 and x != 0:
                    self.verticeGraph[str(someVerticeCounter)] = [someVerticeCounter-1]
                '''If we're on the last segment on a branch, append the point to edge_vectors so that next branch can use it'''
                if x == segments-1:
                    edge_vectors.append(last_vector)
                    edge_index.append(someVerticeCounter)
                someVerticeCounter += 1
        '''If we're on the last generation, it doesnt do this so save time. Hence the flag'''
        if flag == True:
            print("creating new branches")
            for y in range(len(edge_vectors)):
                randRange = linspace(1,2**(int(generation)+1),2**(int(generation)+1))
                randChoise = random.choice(randRange)
                for x in range(int(randChoise)):
                    generation_ov[str(int(generation)+1)].append((edge_vectors[y], Vec3(random.random()-0.5,random.random()*0.5,random.random()-0.5).normalized(), edge_index[y]))
        return someVerticeCounter

    def tree(self):
        '''Just a counter to keep track of absolute index'''
        someVerticeCounter = 0
        '''Calls the branch function for the amount of generations specified'''
        for x in range(self.generations):
            print("calculation gen:", str(x))
            flag = True
            if x == self.generations-1:
                flag = False
            someVerticeCounter = self.branch(generation = x, segments = self.segments, branch_log = self.branch_log, generation_ov = self.generation_ov, flag = flag, someVerticeCounter = someVerticeCounter)

        verts = ()
        leaf_vertices = ()
        leaf_verts = ()
        print("Exporting last generation as base vertices for leafes and reformatting base vertices from dict to tuple of tuples")
        for keys in self.branch_log:
            for x in range(len(list(self.branch_log[keys]))):
                '''Add base vertices of the tree to a tuple, this is mostly for debugging purposes'''
                verts += self.branch_log[keys][x],

                '''If we're on the last generatinon export those as leaf vertice to new tuple, generate leaf vertices and add to leaf mesh'''
                if keys == str(self.generations-1):
                    leaf_vertices += self.branch_log[(str(self.generations-1))][x],
                    randAngle = random.random()*6.14
                    point_1 = Vec3(leaf_vertices[-1][0]+cos(randAngle), leaf_vertices[-1][1]+random.random()*0.5, leaf_vertices[-1][2] + sin(randAngle))
                    point_2 = Vec3(leaf_vertices[-1][0]+cos(randAngle-0.5), leaf_vertices[-1][1]+random.random()*0.5, leaf_vertices[-1][2] + sin(randAngle-0.5))
                    point_3 = Vec3(leaf_vertices[-1][0]+cos(randAngle-0.25)*2, leaf_vertices[-1][1]+random.random()*0.5, leaf_vertices[-1][2] + sin(randAngle-0.25)*2)
                    leaf_verts += leaf_vertices[-1],point_1, point_2, point_3,

        mesh_verts = ()
        mesh_tris = ()
        normals = ()
        '''Reformatting mesh vertices from dict to tuple of tuples'''
        for keys in self.mesh_log:
            print("mesh:generating gen:", str(keys), "; ", str(len(list(self.mesh_log[keys]))), "-vertices")
            for x in range(len(list(self.mesh_log[keys]))):
                mesh_verts += self.mesh_log[keys][x],
                normals += (random.random(),random.random(),random.random()),

        '''Translating treeGraph to mesh_tris'''
        print("Reformatting mesh tris to tuples of 3 from pairs in vertice graph")
        mesh_tris = ()
        tupleofEight = ()
        for keys in self.verticeGraph:
            if keys == "0":
                continue
            i = self.verticeGraph[keys][0]
            j = int(keys)
            tupleofEight += (i*4,i*4+1,i*4+2,i*4+3,j*4,j*4+1,j*4+2,j*4+3),
            for k in range(4):
                mesh_tris += (tupleofEight[-1][0+k],tupleofEight[-1][1+k],tupleofEight[-1][4+k]),(tupleofEight[-1][0+k],tupleofEight[-1][4+k],tupleofEight[-1][3+k]),

        leaf_tris = ()
        print("Generating leaf triangels: ", str(len(list(leaf_verts))/4), "-trangles")
        for x in range(0,len(list(leaf_verts)),4):
            leaf_tris += (x,x+1,x+2),(x+1,x+2,x+3),
        print("Done!")
        return mesh_verts, mesh_tris, normals, verts, leaf_verts, leaf_tris

    def generate(self):
        tree_verts, tree_tris, tree_normals, base_verts, leaf_verts, leaf_tris = self.tree()
        uvs = generate_uvs(tree_verts)
        colors = generate_colors(tree_verts, [color.brown, color.olive])
        a_mesh = Mesh(vertices=tree_verts, triangles=tree_tris, uvs = uvs, normals = tree_normals, colors = colors)
        self.tree_ent = Entity(model=a_mesh, position = (0,-1,0), double_sided = True)
        luvs = generate_uvs(leaf_verts)
        colorsb = generate_colors(leaf_verts, [color.green, color.lime])
        b_mesh = Mesh(vertices=leaf_verts, triangles=leaf_tris, uvs = luvs, normals = tree_normals, colors = colorsb)
        self.leafs_ent = Entity(model=b_mesh, position = (0,-1,0), double_sided = True)
        '''Uncomment these and comment out self.tree_ent and self.leafs_ent to see the underlying vertices of the tree'''
        #volume_mesh = Mesh(vertices = tree_verts, mode = "point", thickness = 0.02)
        #Entity(model = volume_mesh, color = color.orange)
        #base_mesh = Mesh(vertices = base_verts, mode = "point", thickness = 0.02)
        #Entity(model = base_mesh, color = color.cyan)

app = Ursina()

EditorCamera()

pivot = Entity()
DirectionalLight(parent=pivot, y=2, z=3, shadows=True)
Entity(model = "plane", texture = "grass", scale = 20, shader = lit_with_shadows_shader)

ProceduralTree(origin = (0,0,0), generations = 5, segments = 5).generate()

app.run()

