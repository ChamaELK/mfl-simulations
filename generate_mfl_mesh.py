

import gmsh
import sys
import math

gmsh.initialize(sys.argv)
gmsh.option.setColor("Mesh.Color.Lines", 0, 0, 0)

gmsh.option.setNumber('Mesh.Optimize', 1)
gmsh.option.setNumber('Mesh.OptimizeNetgen', 1)
gmsh.option.setNumber('Mesh.Algorithm3D', 10)

gmsh.model.add("mfl")
cascade = gmsh.model.occ
# Let's create a simple rectangular geometry:
lc = 0.2#.
plate_length= 2
cube_length =0.2

cascade.addPoint(-plate_length, -plate_length, 0, lc, 1)
cascade.addPoint(plate_length, -plate_length, 0, lc, 2)
cascade.addPoint(plate_length, plate_length, 0, lc, 3)
cascade.addPoint(-plate_length, plate_length, 0, lc, 4)
cascade.addPoint(0.2, .5, 0, lc, 5)

cascade.addLine(1, 2, 1)
cascade.addLine(2, 3, 2)
cascade.addLine(3, 4, 3)
cascade.addLine(4, 1, 4)

cascade.addCurveLoop([1, 2, 3, 4], 5)
plane_surface_tag= 6
cascade.addPlaneSurface([5], plane_surface_tag)

cascade.synchronize()
cube_tag =1 
extruded_entities = cascade.extrude([(2, 6)], 0, 0, cube_length)



cascade.synchronize()


cavity_length = 0.2
defect_length = 0.04
defect_depth = 0.8*0.2

defect_x = ( - defect_length) / 2.0
defect_y = (- defect_length) / 2.0
defect_z = cube_length 
defect = cascade.addBox(defect_x, defect_y, defect_z, defect_length, defect_length, -defect_depth,7)

cascade.synchronize()
outer_cube = cube_tag
# Subtract the defect from the outer cube
cascade.cut([(3, outer_cube)], [(3, defect)])
cascade.synchronize()


gmsh.model.mesh.field.add("Box", 6)
gmsh.model.mesh.field.setNumber(6, "VIn", lc / 15)
gmsh.model.mesh.field.setNumber(6, "VOut", lc)
gmsh.model.mesh.field.setNumber(6, "XMin", -0.25)
gmsh.model.mesh.field.setNumber(6, "XMax", 0.25)
gmsh.model.mesh.field.setNumber(6, "YMin", -0.25)
gmsh.model.mesh.field.setNumber(6, "YMax", 0.25)
gmsh.model.mesh.field.setNumber(6,"ZMax",1)
gmsh.model.mesh.field.setNumber(6,"ZMin",0)
gmsh.model.mesh.field.setNumber(6, "Thickness", 0.3)

gmsh.model.mesh.field.add("Min", 7)
gmsh.model.mesh.field.setNumbers(7, "FieldsList", [2, 3, 5, 6])

gmsh.model.mesh.field.setAsBackgroundMesh(7)
gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)


Ri = 0.2
dr= 0.05
Ra = 4
#la = 0.5
th = 0.05
nl = 30
lc = th / 4
lz =2
dy= 0.5

cascade = gmsh.model.occ
meshing = gmsh.model.mesh
gdim = 3

cascade.addPoint(Ri, -dy/2, lz, lc, 25)
cascade.addPoint(Ri+dr, -dy/2, lz, lc, 26)
cascade.addPoint(Ri+dr, dy/2, lz, lc, 27)
cascade.addPoint(Ri, dy/2, lz, lc, 28)

cascade.addLine(25, 26, 29)
cascade.addLine(26, 27, 30)
cascade.addLine(27, 28, 31)
cascade.addLine(28, 25, 32)
cascade.addCurveLoop([29, 30, 31, 32], 33)
cascade.addPlaneSurface([33], 34)

cascade.addPoint(0., -dy, lz, lc/2, 35)
cascade.addPoint(0., dy, lz, lc/2, 36)
cascade.addLine(35, 36, 37)

cascade.synchronize()



ls_1 = cascade.revolve([(gdim-1, 34)], 0, -dy, lz, 0, 1, 0, -math.pi, [nl], recombine = False)
ls_2 = cascade.revolve([(gdim-1, 34)], 0, -dy, lz, 0, 1, 0, math.pi, [nl], recombine = False)
cascade.synchronize()

ls_3 = cascade.fuse([(gdim, 2)], [(gdim, 3)], 4)
coil_tag = [4]
coil_dimtag= [(gdim,4)]



cylinder_radius= Ri
cylinder_width = 2
vertices=[]
cylinder_zpos= lz
vertices.append(gmsh.model.occ.addPoint(0, -cylinder_width/2, cylinder_zpos))
vertices.append(gmsh.model.occ.addPoint(cylinder_radius, -cylinder_width/2, cylinder_zpos))
vertices.append(gmsh.model.occ.addPoint(cylinder_radius, cylinder_width/2, cylinder_zpos))
vertices.append(gmsh.model.occ.addPoint(0, cylinder_width/2, cylinder_zpos))

# Create the edges to define the 2D square
edges = [gmsh.model.occ.addLine(vertices[i], vertices[(i + 1) % 4]) for i in range(4)]

# Create the loop for the square
square_loop = gmsh.model.occ.addCurveLoop(edges)

# Create the 2D square's surface
square_surface = gmsh.model.occ.addPlaneSurface([square_loop])
cascade = gmsh.model.occ
gdim =3
import math
nl =30
ls_1 = cascade.revolve([(gdim-1, square_surface)], 0, 0, lz, 0, 1, 0, -math.pi, [nl], recombine = False)
ls_2 = cascade.revolve([(gdim-1, square_surface)], 0, 0, lz, 0, 1, 0, math.pi, [nl], recombine = False)
cascade.synchronize()


ls_3 = cascade.fuse([(gdim, 5)], [(gdim, 6)], 7)

# Create the right cube
core_cube_dx = 2*Ri +0.2
core_cube_dy = Ri
core_cube_height = - (lz-cube_length  + Ri)
core_cube_x = -core_cube_dx/2
core_cube_y = cylinder_width/2
core_cube_z = lz + Ri
right_cube = gmsh.model.occ.addBox(core_cube_x,core_cube_y, core_cube_z,
                                   core_cube_dx , core_cube_dy, core_cube_height)

cascade.fuse([(gdim, 7)], [(gdim, 8)], 9)
cascade.synchronize()


# Create the left cube
core_cube_dx = 2*Ri +0.2
core_cube_dy = Ri
core_cube_height = - (lz-cube_length  + Ri)
core_cube_x = -core_cube_dx/2
core_cube_y = -cylinder_width/2 - core_cube_dy
core_cube_z = lz + Ri
left_cube = gmsh.model.occ.addBox(core_cube_x,core_cube_y, core_cube_z,
                                   core_cube_dx , core_cube_dy, core_cube_height)

cascade.fuse([(gdim, 9)], [(gdim, 10)], 11)
cascade.synchronize()




### TODO ( last ) boundaries : coil - air , coil - core, core - cube , air - (all)
### Equation (magnetic field) 

air_tag= [12]

cascade.fragment(gmsh.model.occ.getEntities(gdim), [])

cascade.addSphere(0, 0, 0, Ra, 12)
cascade.synchronize()

cascade.fragment([(gdim, 12)], [(3,4),(3,11),(3,1)])

cascade.synchronize()


up, down = gmsh.model.getAdjacencies(gdim, air_tag[0])
# add the core 
coilBoundary_dimtag = gmsh.model.getBoundary([(gdim, 4),(gdim,1), (gdim,11)], oriented=False)
coilBoundary_tags = [tup[1] for tup in coilBoundary_dimtag]


gmsh.model.addPhysicalGroup(gdim, [cube_tag], 1, name="Cube")
gmsh.model.addPhysicalGroup(gdim, coil_tag, 2, name="Coil")

gmsh.model.addPhysicalGroup(gdim, air_tag, 3, name="Air")
gmsh.model.addPhysicalGroup(gdim-1, [down[0]], 4, name="AirBoundary")
gmsh.model.setColor([(gdim-1, down[0])], 0, 0, 255)
gmsh.model.addPhysicalGroup(gdim-1, coilBoundary_tags, 5, name="CoilBoundary")
gmsh.model.setColor(coilBoundary_dimtag, 0, 255, 255)
gmsh.model.addPhysicalGroup(1, [6], 6, name="Axis")
gmsh.model.addPhysicalGroup(gdim, [11], 7, name="CoreTag")

meshing.removeDuplicateNodes
meshing.removeDuplicateElements

#gmsh.option.setNumber("Mesh.Algorithm", 5)
gmsh.model.mesh.generate(3)
gmsh.write("mfl.msh")

# Launch the GUI to see the results:
if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()