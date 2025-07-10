from ogum.fem_interface import create_unit_mesh

def test_unit_mesh_creation():
    mesh = create_unit_mesh(0.5)
    coords = mesh.geometry.x
    assert coords.shape[0] > 2
