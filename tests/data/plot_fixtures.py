# Tools to visualize manufactured datasets

import argparse
import pathlib

import numpy as np
import pyvista as pv
import vtk


def plot_cells(dataset, pl):
    n_cells = dataset.n_cells
    cells_id = np.arange(n_cells)
    
    pl.add_mesh(
        dataset,
        style="surface",
        scalars=cells_id,
        clim=[-0.5, n_cells-0.5],
        show_edges=True,
        edge_color="lightgrey",
        point_size=35,
        line_width=6,
        lighting=False,
        n_colors=n_cells,
        cmap="tab20b",
        reset_camera=True,
        show_scalar_bar=False,
    )
    
    height = n_cells/22.0
    sbar = pl.add_scalar_bar(
        title="Cell ID",
        height=height,
        position_y=0.5-height/2,
        vertical=True,
        fmt=" %.0f",
    )
    sbar.SetCustomLabels(
        pv.convert_array(cells_id, array_type=vtk.VTK_DOUBLE)
    )
    sbar.UseCustomLabelsOn()
    
    return
    

def plot_points(dataset, pl):
    points = dataset.points.copy()
    points[:,2] += 0.5
    pl.add_points(
        points,
        color="lightgrey",
        point_size=22,
        point_shape="circle",
    )

    points_id = points.copy()
    points_id[:,2] += 0.5
    pl.add_point_labels(
        points_id,
        labels=[f"{i}" for i in np.arange(len(points_id))],
        font_size=pv.global_theme.font.size-6,
        text_color="black",
        show_points=False,
        shape=None,
        justification_horizontal="center",
        justification_vertical="center",
    )
    
    return
    

def plot_grid(pl):
    pl.show_grid(
        bounds=[-2, 3, 0, 5, -1, 4],
        bold=False,
        font_size=pv.global_theme.font.size-6,
        xtitle=" ",
        ytitle=" ",
        n_xlabels=6,
        n_ylabels=6,
        use_2d=True,
        grid="back",
        location="front",
        fmt="%.1f",
    )
    
    pl.add_axes(
        viewport=(0.0, 0.0, 0.18, 0.18),
    )
    
    return 
    

def plot(file, off_screen=False):
    dataset = pv.read(file)
    pl = pv.Plotter(off_screen=off_screen)
    
    plot_cells(dataset, pl)
    plot_points(dataset, pl)
    plot_grid(pl)
    
    pl.add_title(
        file,
        font_size=pv.global_theme.font.size-8,
    )
    
    pl.enable_parallel_projection()
    pl.view_xy()
    pl.camera.zoom(1.4)

    return pl
    

def show(file):
    pl = plot(file)
    pl.enable_2d_style()
    pl.show()
    return
    

def save(file, output):
    pl = plot(file, off_screen=True)
    pl.save_graphic(output)
    return
    

def get_args():
    usage_text = (
        "Visualize the manufactured PyVista datasets. "
        "A screenshot of the rendering window can be saved as a graphic file."
    )
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, 
        description=usage_text
    )
    
    parser.add_argument(
        "files", type=str, default="", metavar="<file_in>", nargs="+",
        help="name of the file(s) to read"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-o", "--output", type=str, default="", metavar="<file_out>",
        help=(
            "name of the file to write (with extension .svg, .eps, .ps, .pdf, .tex) ; "
            "if specified, there is no graphical display"
        )
    )
    group.add_argument(
        "-f", "--format", type=str, default="", choices={"svg", "eps", "ps", "pdf", "tex"},
        help=(
            "format of the file(s) to write ; "
            "if specified, there is no graphical display"
        )
    )
 
    args = parser.parse_args()
    
    return args.files, args.output, args.format
    

def main():
    files, output, format = get_args()
    if output: # Only the first input file is rendered
        save(files[0], output)
    elif format:
        for file in files:
            output = pathlib.Path(file).with_suffix("."+format)
            save(file, output)
    else:
        for file in files:
            show(file)
    return
    

if __name__ == '__main__':
    main()
    
