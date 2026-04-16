import os

import grass.script as gs


def run_function_with_points(scanned_elev, eventHandler, env, points=None, **kwargs):
    """Doesn't do anything, except loading points from a vector map to Python

    If *points* is provided, the function assumes it is name of an existing vector map.
    This is used during testing.
    If *points* is not provided, the function assumes it runs in Tangible Landscape.
    """
    if not points:
        # If there are no points, ask Tangible Landscape to generate points from
        # a change in the surface.
        points = "points"
        import analyses
        from activities import updateDisplay

        analyses.change_detection(
            "scan_saved",
            scanned_elev,
            points,
            height_threshold=[10, 100],
            cells_threshold=[5, 50],
            add=True,
            max_detected=5,
            debug=True,
            env=env,
        )

    point_prob = gs.read_command(
        "r.what",
        map="probabilitySurface",
        points=points,
        env=env,
    )
    print(point_prob.split("|")[-1])
    # percentage = float(point_prob.split("|")[-1]) * 100

    # the output seems to be three columns separated by |
    # coordinates and the probability
    # 2890|28689|0.15

    # update dashboard
    event = updateDisplay(value=point_prob)
    eventHandler.postEvent(receiver=eventHandler.activities_panel, event=event)
    # throw eventHandler into defining function
    # activities_panel


def main():
    env = os.environ.copy()
    env["GRASS_OVERWRITE"] = "1"
    elevation = "elev_lid792_1m"
    elev_resampled = "elev_resampled"
    gs.run_command("g.region", raster=elevation, res=4, flags="a", env=env)
    gs.run_command("r.resamp.stats", input=elevation, output=elev_resampled, env=env)

    points = "points"
    gs.write_command(
        "v.in.ascii",
        flags="t",
        input="-",
        output=points,
        separator="comma",
        stdin="638432,220382\n638621,220607",
        env=env,
    )

    run_function_with_points(scanned_elev=elev_resampled, env=env, points=points)


if __name__ == "__main__":
    main()
