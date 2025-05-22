import argparse as ap
import sys
from bvhTools import bvhIO, bvhManipulation, bvhSlicer, bvhVisualizerMpl

def main():
    parser = ap.ArgumentParser(description="bvhTools CLI interface")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)
    
    # subparser for centering commands
    parser_centering = subparsers.add_parser("center", help="Centering operations", description="Centers a BVH file's feet, root or the X and Z axes and writes it to a new BVH file")
    parser_centering.add_argument("--centeringOption", type=str, help="Option to execute", choices=["feet", "root", "xz"], default="feet")
    parser_centering.add_argument("--bvhFile", required=True, type=str, help="Path to the BVH file")
    parser_centering.add_argument("--outputFile", required=True, type=str, help="Path to the output BVH file")

    # subparser for rotation commands
    parser_rotation = subparsers.add_parser("rotate", help="Rotation commands", description="Rotates a BVH file in local or world space and writes it to a new BVH file")
    parser_rotation.add_argument("--rotationOption", type=str, help="Option to execute", choices=["local", "world"], default="local")
    parser_rotation.add_argument("--bvhFile", required=True, type=str, help="Path to the BVH file")
    parser_rotation.add_argument("--outputFile", required=True, type=str, help="Path to the output BVH file")
    parser_rotation.add_argument("--angles", required=True, type=float, nargs=3, help="Angles to rotate: X_value Y_value Z_value")

    # subparser for viewer commands
    parser_viewer = subparsers.add_parser("view", help="Viewer command", description="Launches matplotlib viewer. By default, it will show points, lines and labels. Disable them with --noPoints, --noLines and --noLabels")
    parser_viewer.add_argument("--bvhFile", required=True, type=str, help="Path to the BVH file")
    parser_viewer.add_argument("--noPoints", action="store_false", help="Do not draw points for joints")
    parser_viewer.add_argument("--noLines", action="store_false", help="Do not draw lines between joints")
    parser_viewer.add_argument("--noLabels", action="store_false", help="Do not draw labels")
    
    # subparser for slicing commands
    parser_slicer = subparsers.add_parser("slice", help="Slicer commands", description="Slices a BVH between two frames and writes it to a new BVH file")
    parser_slicer.add_argument("--bvhFile", required=True, type=str, help="Path to the BVH file")
    parser_slicer.add_argument("--startFrame", required=True, type=int, help="Start frame")
    parser_slicer.add_argument("--endFrame", required=True, type=int, help="End frame")
    parser_slicer.add_argument("--outputFile", required=True, type=str, help="Path to the output BVH file")

    # subparser for CSV commands
    parser_csv = subparsers.add_parser("csv", help="CSV commands", description="Exports a BVH file completely or its positions to a CSV file")
    parser_csv.add_argument("--csvOption", type=str, help="CSV export options: 'positions' for joint coordinates or 'bvh' for the whole BVH", choices=["positions", "bvh"], default="positions")
    parser_csv.add_argument("--bvhFile", required=True, type=str, help="Path to the BVH file")
    parser_csv.add_argument("--outputFile", required=True, type=str, help="Path to the output CSV file")

    args = parser.parse_args()

    commands = {
        "center": center_bvh,
        "rotate": rotate_bvh,
        "view": view_bvh,
        "slice": slice_bvh,
        "csv": csv_bvh
    }
    
    # dispatch the command
    if args.command in commands:
        commands[args.command](args)
    else:
        showHelp()
        sys.exit(1)

def showHelp():
    print("bvhTools: Command-line tools for BVH file manipulation\n")
    print("Usage:")
    print(f"  python {sys.argv[0]} <command> [options]\n")
    print("Commands:")
    print("  center     Center the skeleton (feet, root, or XZ)")
    print("  rotate     Apply rotation (local/world space)")
    print("  view       Launch a matplotlib-based BVH viewer")
    print("  slice      Extract a segment of the animation")
    print("  csv        Export joint position data or full BVH to CSV")
    print("\nUse '<command> --help' to see options for a specific command.")


def center_bvh(args):
    bvhData = bvhIO.readBvh(args.bvhFile)
    if(args.centeringOption == "feet"):
        bvhData = bvhManipulation.centerSkeletonFeet(bvhData)
    if(args.centeringOption == "root"):
        bvhData = bvhManipulation.centerSkeletonRoot(bvhData)
    if(args.centeringOption == "xz"):
        bvhData = bvhManipulation.centerSkeletonXZ(bvhData)
    bvhIO.writeBvh(bvhData, args.outputFile)

def rotate_bvh(args):
    bvhData = bvhIO.readBvh(args.bvhFile)
    if(args.rotationOption == "local"):
        bvhData = bvhManipulation.rotateSkeletonLocal(bvhData, args.angles)
    if(args.rotationOption == "world"):
        bvhData = bvhManipulation.rotateSkeletonWorld(bvhData, args.angles)
    bvhIO.writeBvh(bvhData, args.outputFile)

def view_bvh(args):
    bvhData = bvhIO.readBvh(args.bvhFile)
    bvhVisualizerMpl.showBvhAnimation(bvhData, showPoints=args.noPoints, showLines=args.noLines, showLabels=args.noLabels)

def slice_bvh(args):
    bvhData = bvhIO.readBvh(args.bvhFile)
    bvhData = bvhSlicer.getBvhSlice(bvhData, args.startFrame, args.endFrame)
    bvhIO.writeBvh(bvhData, args.outputFile)

def csv_bvh(args):
    bvhData = bvhIO.readBvh(args.bvhFile)
    if(args.csvOption == "positions"):
        bvhIO.writePositionsToCsv(bvhData, args.outputFile)
    if(args.csvOption == "bvh"):
        bvhIO.writeBvhToCsv(bvhData, args.outputFile)

if __name__ == "__main__":
    main()