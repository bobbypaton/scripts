"""
PyMOL Style Configuration for Paton Lab

This script provides custom PyMOL visualization functions and settings optimized
for molecular structure visualization. It includes:
- Bondi van der Waals radii for all elements
- Ball-and-stick representation functions
- Molecular orbital and spin density visualization
- Non-covalent interaction (NCI) plotting

Usage: Run this script in PyMOL or load it in your .pymolrc file
"""

from pymol import cmd
from pymol import stored

# ============================================================================
# Van der Waals Radii Settings
# ============================================================================
# Override PyMOL's default VDW radii with Bondi values (Å)
# Reference: Bondi, A. (1964). J. Phys. Chem. 68, 441-451
# These values are used for proper space-filling representations
cmd.alter("elem Ac", "vdw=2.00")
cmd.alter("elem Al", "vdw=2.00")
cmd.alter("elem Am", "vdw=2.00")
cmd.alter("elem Sb", "vdw=2.00")
cmd.alter("elem Ar", "vdw=1.88")
cmd.alter("elem As", "vdw=1.85")
cmd.alter("elem At", "vdw=2.00")
cmd.alter("elem Ba", "vdw=2.00")
cmd.alter("elem Bk", "vdw=2.00")
cmd.alter("elem Be", "vdw=2.00")
cmd.alter("elem Bi", "vdw=2.00")
cmd.alter("elem Bh", "vdw=2.00")
cmd.alter("elem B ", "vdw=2.00")
cmd.alter("elem Br", "vdw=1.85")
cmd.alter("elem Cd", "vdw=1.58")
cmd.alter("elem Cs", "vdw=2.00")
cmd.alter("elem Ca", "vdw=2.00")
cmd.alter("elem Cf", "vdw=2.00")
cmd.alter("elem C ", "vdw=1.70")
cmd.alter("elem Ce", "vdw=2.00")
cmd.alter("elem Cl", "vdw=1.75")
cmd.alter("elem Cr", "vdw=2.00")
cmd.alter("elem Co", "vdw=2.00")
cmd.alter("elem Cu", "vdw=1.40")
cmd.alter("elem Cm", "vdw=2.00")
cmd.alter("elem Ds", "vdw=2.00")
cmd.alter("elem Db", "vdw=2.00")
cmd.alter("elem Dy", "vdw=2.00")
cmd.alter("elem Es", "vdw=2.00")
cmd.alter("elem Er", "vdw=2.00")
cmd.alter("elem Eu", "vdw=2.00")
cmd.alter("elem Fm", "vdw=2.00")
cmd.alter("elem F ", "vdw=1.47")
cmd.alter("elem Fr", "vdw=2.00")
cmd.alter("elem Gd", "vdw=2.00")
cmd.alter("elem Ga", "vdw=1.87")
cmd.alter("elem Ge", "vdw=2.00")
cmd.alter("elem Au", "vdw=1.66")
cmd.alter("elem Hf", "vdw=2.00")
cmd.alter("elem Hs", "vdw=2.00")
cmd.alter("elem He", "vdw=1.40")
cmd.alter("elem Ho", "vdw=2.00")
cmd.alter("elem In", "vdw=1.93")
cmd.alter("elem I ", "vdw=1.98")
cmd.alter("elem Ir", "vdw=2.00")
cmd.alter("elem Fe", "vdw=2.00")
cmd.alter("elem Kr", "vdw=2.02")
cmd.alter("elem La", "vdw=2.00")
cmd.alter("elem Lr", "vdw=2.00")
cmd.alter("elem Pb", "vdw=2.02")
cmd.alter("elem Li", "vdw=1.82")
cmd.alter("elem Lu", "vdw=2.00")
cmd.alter("elem Mg", "vdw=1.73")
cmd.alter("elem Mn", "vdw=2.00")
cmd.alter("elem Mt", "vdw=2.00")
cmd.alter("elem Md", "vdw=2.00")
cmd.alter("elem Hg", "vdw=1.55")
cmd.alter("elem Mo", "vdw=2.00")
cmd.alter("elem Nd", "vdw=2.00")
cmd.alter("elem Ne", "vdw=1.54")
cmd.alter("elem Np", "vdw=2.00")
cmd.alter("elem Ni", "vdw=1.63")
cmd.alter("elem Nb", "vdw=2.00")
cmd.alter("elem N ", "vdw=1.55")
cmd.alter("elem No", "vdw=2.00")
cmd.alter("elem Os", "vdw=2.00")
cmd.alter("elem O ", "vdw=1.52")
cmd.alter("elem Pd", "vdw=1.63")
cmd.alter("elem P ", "vdw=1.80")
cmd.alter("elem Pt", "vdw=1.72")
cmd.alter("elem Pu", "vdw=2.00")
cmd.alter("elem Po", "vdw=2.00")
cmd.alter("elem K ", "vdw=2.75")
cmd.alter("elem Pr", "vdw=2.00")
cmd.alter("elem Pm", "vdw=2.00")
cmd.alter("elem Pa", "vdw=2.00")
cmd.alter("elem Ra", "vdw=2.00")
cmd.alter("elem Rn", "vdw=2.00")
cmd.alter("elem Re", "vdw=2.00")
cmd.alter("elem Rh", "vdw=2.00")
cmd.alter("elem Rb", "vdw=2.00")
cmd.alter("elem Ru", "vdw=2.00")
cmd.alter("elem Rf", "vdw=2.00")
cmd.alter("elem Sm", "vdw=2.00")
cmd.alter("elem Sc", "vdw=2.00")
cmd.alter("elem Sg", "vdw=2.00")
cmd.alter("elem Se", "vdw=1.90")
cmd.alter("elem Si", "vdw=2.10")
cmd.alter("elem Ag", "vdw=1.72")
cmd.alter("elem Na", "vdw=2.27")
cmd.alter("elem Sr", "vdw=2.00")
cmd.alter("elem S ", "vdw=1.80")
cmd.alter("elem Ta", "vdw=2.00")
cmd.alter("elem Tc", "vdw=2.00")
cmd.alter("elem Te", "vdw=2.06")
cmd.alter("elem Tb", "vdw=2.00")
cmd.alter("elem Tl", "vdw=1.96")
cmd.alter("elem Th", "vdw=2.00")
cmd.alter("elem Tm", "vdw=2.00")
cmd.alter("elem Sn", "vdw=2.17")
cmd.alter("elem Ti", "vdw=2.00")
cmd.alter("elem W ", "vdw=2.00")
cmd.alter("elem U ", "vdw=1.86")
cmd.alter("elem V ", "vdw=2.00")
cmd.alter("elem Xe", "vdw=2.16")
cmd.alter("elem Yb", "vdw=2.00")
cmd.alter("elem Y ", "vdw=2.00")
cmd.alter("elem Zn", "vdw=1.39")
cmd.alter("elem Zr", "vdw=2.00")
cmd.rebuild()  # Rebuild geometry with updated VDW radii

# ============================================================================
# Global Workspace Settings
# ============================================================================
# Configure PyMOL rendering settings for high-quality publication figures
cmd.bg_color("white")  # White background for clean figures
cmd.set("ray_opaque_background", "off")  # Transparent background for ray-traced images
cmd.set("orthoscopic", 0)  # Use perspective projection
cmd.set("transparency", 0.5)  # Default transparency level
#cmd.set("dash_gap", 0)  # Uncomment for solid dashed lines (no gaps)
cmd.set("ray_trace_mode", 1)  # High-quality ray tracing
cmd.set("ray_texture", 2)  # Matte surface texture
cmd.set("antialias", 3)  # Maximum antialiasing for smooth edges
cmd.set("ambient", 0.5)  # Ambient lighting intensity
cmd.set("spec_count", 5)  # Number of specular highlights
cmd.set("shininess", 50)  # Surface shininess
cmd.set("specular", 1)  # Specular reflection intensity
cmd.set("reflect", .1)  # Reflection coefficient
cmd.space("cmyk")  # Use CMYK color space (better for print)
cmd.set("label_distance_digits", 2)  # Show 2 decimal places in distance labels

# ============================================================================
# Ball-and-Stick Representation
# ============================================================================
def BallnStick(arg1):
    """
    Creates a publication-quality ball-and-stick representation of a molecule.

    Args:
        arg1 (str): PyMOL selection or object name

    This function displays atoms as small spheres connected by thin sticks,
    with custom coloring (gray carbons, white hydrogens, slate nitrogens).
    """
    cmd.show("sticks", arg1)  # Show bonds as sticks
    cmd.show("spheres", arg1)  # Show atoms as spheres

    # Custom color scheme
    cmd.color("gray85", "elem C and "+arg1)  # Light gray for carbon
    cmd.color("gray98", "elem H and "+arg1)  # Nearly white for hydrogen
    cmd.color("slate", "elem N and "+arg1)   # Slate blue for nitrogen

    # Stick and sphere sizing
    cmd.set("stick_radius", 0.07, arg1)  # Thin sticks for bonds
    cmd.set("sphere_scale", 0.18, arg1)  # Small spheres for heavy atoms
    cmd.set("sphere_scale", 0.13, arg1+" and elem H")  # Even smaller for hydrogens
    cmd.set("stick_color", "black", arg1)  # Black bonds

    # Hydrogen bond dashing
    cmd.set("dash_gap", 0.01)  # Small gaps in dashed lines
    cmd.set("dash_radius", 0.035)  # Thickness of dashed lines

    # Hide unnecessary representations
    cmd.hide("nonbonded", arg1)  # Hide non-bonded atoms
    cmd.hide("lines", arg1)  # Hide line representation

    # Show valence (unpaired electrons)
    cmd.set('valence', 1, arg1)  # Enable valence display
    cmd.set('valence_size', 0.2, arg1)  # Size of valence indicators

    cmd.zoom(arg1)  # Center and zoom on the selection
    cmd.hide("labels")  # Hide all labels

# ============================================================================
# Van der Waals Surface Representation
# ============================================================================
def Add_VDW(arg1):
    """
    Creates a transparent van der Waals surface representation.

    Args:
        arg1 (str): PyMOL selection or object name

    This function duplicates the object and displays it as full-sized,
    transparent spheres representing the VDW surface. Useful for visualizing
    steric effects and molecular volume.
    """
    cmd.copy(arg1+"_vdw", arg1)  # Create a copy with "_vdw" suffix
    cmd.set("sphere_scale", 1.0, arg1+"_vdw and elem H")  # Full size for hydrogens
    cmd.rebuild()  # Rebuild with new settings
    cmd.set("sphere_scale", 1, arg1+"_vdw")  # Full VDW size for all atoms

    # Show only spheres, hide other representations
    cmd.hide("nonbonded", arg1+"_vdw")
    cmd.hide("lines", arg1+"_vdw")
    cmd.hide("sticks", arg1+"_vdw")

    cmd.set("sphere_transparency", 0.7, arg1+"_vdw")  # Make transparent

# ============================================================================
# Spin Density Visualization
# ============================================================================
def Add_spin(arg1):
    """
    Visualizes spin density from a Gaussian cube file.

    Args:
        arg1 (str): Base name of the cube file (without .cube extension)

    Loads spin density data and displays it as an isosurface colored by
    density value (red = positive/alpha, blue = negative/beta spin).
    """
    cmd.load(arg1+".cube")  # Load cube file
    cmd.isosurface("spin_iso", arg1, .005)  # Create isosurface at 0.005 isovalue

    # Create color gradient from red to blue
    cmd.ramp_new("ramp", arg1, range=[-1E-30, 1E-30], color="[red, blue]")
    cmd.set("surface_color", "ramp", "spin_iso")

    # High-quality rendering settings
    cmd.set("surface_quality", 3)
    cmd.set("ray_texture", 2)
    cmd.set("antialias", 3)
    cmd.set("ambient", 0.5)
    cmd.set("spec_count", 5)
    cmd.set("shininess", 50)
    cmd.set("specular", 1)
    cmd.set("transparency", 0.5)

# ============================================================================
# Molecular Orbital Visualizations
# ============================================================================
def Add_homo(arg1):
    """
    Visualizes the Highest Occupied Molecular Orbital (HOMO) from cube file.

    Args:
        arg1 (str): Base name of the cube file (without .cube extension)

    Creates two isosurfaces representing positive (red) and negative (blue)
    phases of the HOMO wavefunction at isovalue ±0.02.
    """
    cmd.load(arg1+".cube")  # Load cube file

    # Create positive and negative isosurfaces for different orbital phases
    cmd.isosurface("homo_isoA", arg1, .02)   # Positive phase
    cmd.isosurface("homo_isoB", arg1, -.02)  # Negative phase

    # Color by phase
    cmd.color("red", "homo_isoA")   # Positive = red
    cmd.color("blue", "homo_isoB")  # Negative = blue

    # High-quality rendering settings
    cmd.set("surface_quality", 3)
    cmd.set("ray_texture", 2)
    cmd.set("antialias", 3)
    cmd.set("ambient", 0.5)
    cmd.set("spec_count", 5)
    cmd.set("shininess", 50)
    cmd.set("specular", 1)
    cmd.set("transparency", 0.5)

def Add_lumo(arg1):
    """
    Visualizes the Lowest Unoccupied Molecular Orbital (LUMO) from cube file.

    Args:
        arg1 (str): Base name of the cube file (without .cube extension)

    Creates two isosurfaces representing positive (red) and negative (blue)
    phases of the LUMO wavefunction at isovalue ±0.02.
    """
    cmd.load(arg1+".cube")  # Load cube file

    # Create positive and negative isosurfaces for different orbital phases
    cmd.isosurface("lumo_isoA", arg1, .02)   # Positive phase
    cmd.isosurface("lumo_isoB", arg1, -.02)  # Negative phase

    # Color by phase
    cmd.color("red", "lumo_isoA")   # Positive = red
    cmd.color("blue", "lumo_isoB")  # Negative = blue

    # High-quality rendering settings
    cmd.set("surface_quality", 3)
    cmd.set("ray_texture", 2)
    cmd.set("antialias", 3)
    cmd.set("ambient", 0.5)
    cmd.set("spec_count", 5)
    cmd.set("shininess", 50)
    cmd.set("specular", 1)
    cmd.set("transparency", 0.5)


# ============================================================================
# Register Custom Commands
# ============================================================================
# Make functions available as PyMOL commands with case-insensitive aliases
cmd.extend( "ballnstick", BallnStick );
cmd.extend( "BallnStick", BallnStick );
cmd.extend( "Add_VDW", Add_VDW );
cmd.extend( "addvdw", Add_VDW );
cmd.extend( "Add_spin", Add_spin );
cmd.extend( "Add_homo", Add_homo );
cmd.extend( "Add_lumo", Add_lumo );


# ============================================================================
# Non-Covalent Interaction (NCI) Visualization
# ============================================================================
# Based on https://github.com/rmera/ncipy/blob/master/nci.py
@cmd.extend
def nci(arg1, arg2, arg3):
    """
    Visualizes non-covalent interactions using NCI analysis.

    Args:
        arg1 (str): Base name for density and gradient cube files
        arg2 (str/int): Minimum density value for color ramp
        arg3 (str/int): Maximum density value for color ramp

    Requires two cube files: {arg1}-dens.cube and {arg1}-grad.cube
    Colors the reduced density gradient surface by electron density using
    a rainbow gradient to highlight different interaction types
    (e.g., hydrogen bonds, steric clashes, van der Waals).
    """
    densf = arg1+"-dens"  # Density cube file
    gradf = arg1+"-grad"  # Gradient cube file

    cmd.isosurface("grad", gradf, 0.5)  # Create isosurface of reduced gradient

    # Color by electron density (rainbow: blue = attractive, red = repulsive)
    cmd.ramp_new("ramp", densf, [int(arg2), int(arg3)], "rainbow")
    cmd.set("surface_color", "ramp", "grad")
    cmd.set('two_sided_lighting', value=1)  # Enable two-sided lighting


# ============================================================================
# Custom Spin Density Plot with Adjustable Isovalue
# ============================================================================
@cmd.extend
def spin_density_plot(arg1, arg2):
    """
    Creates a spin density plot with user-defined isovalue.

    Args:
        arg1 (str): Base name of the cube file (without .cube extension)
        arg2 (str/float): Isovalue threshold for the isosurface

    Similar to Add_spin() but allows custom isovalue specification.
    Creates two isosurfaces at ±isovalue, colored red (alpha/positive spin)
    and blue (beta/negative spin).
    """
    cmd.load(arg1+".cube")  # Load cube file

    # Create positive and negative spin density isosurfaces
    cmd.isosurface("spin_isoA", arg1, float(arg2))   # Positive spin (alpha)
    cmd.isosurface("spin_isoB", arg1, -float(arg2))  # Negative spin (beta)

    # Color by spin
    cmd.color("red", "spin_isoA")   # Alpha spin = red
    cmd.color("blue", "spin_isoB")  # Beta spin = blue

    # Alternative coloring method (currently commented out)
    # cmd.ramp_new("ramp", arg1, color="[red, blue]")
    # cmd.set("surface_color","ramp", "spin_iso")

    # Optional rendering settings (commented out - uses global defaults)
    #cmd.set("surface_quality",3)
    #cmd.set("ray_texture", 2)
    #cmd.set("antialias", 3)
    #cmd.set("ambient", 0.5)
    #cmd.set("spec_count", 5)
    #cmd.set("shininess", 50)
    #cmd.set("specular", 1)

    cmd.set("transparency", 0.7)  # More transparent than default
