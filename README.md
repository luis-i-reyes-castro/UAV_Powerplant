# UAV Powerplant Multi-Objective Optimization

This project contains a set of Python scripts designed to model and optimize the performance of multi-rotor Unmanned Aerial Vehicles (UAVs). This tool was developed to aid in the component selection phase for the AeroMarca UAV project.

Given a database of commercially available motors, propellers, batteries, and electronic speed controllers (ESCs), the tool calculates key performance metrics for thousands of possible hardware combinations. It then performs a multi-objective optimization to identify the Pareto-optimal set of configurations, allowing a designer to select the best possible design that balances flight endurance and payload capacity for a given budget.

## How it Works

The process involves several key steps:

1.  **Modeling**: The `models.py` script defines Python classes for every major component: `Motor`, `Propeller`, `Battery`, `ElectronicSpeedController`. These classes store technical specifications and performance data. A final `VehicleConfiguration` class assembles these components into a full vehicle design.
2.  **System Assembly & Feasibility**: The `VehicleConfiguration` class programmatically checks if each hardware combination is physically feasible (e.g., mismatched voltages, currents exceeding limits). If feasible, it calculates the two primary objectives: hover flight `endurance` and payload `massbudget`.
3.  **Data Parsing**: The functions in `routines.py` read component specifications from various Excel spreadsheets (`.xlsx` files).
4.  **Brute-Force Combination & Filtering**: The main script, `vehicle_performance.py`, systematically generates all possible vehicle configurations from the parsed data. It then filters for designs that meet a set of predefined constraints (e.g., minimum endurance, minimum payload, and maximum cost).
5.  **Pareto Optimization**: For all the feasible designs, the `pareto_frontier` function in `routines.py` is called. This function implements a classic algorithm to find the Pareto front for the two objectives (endurance and mass budget). The resulting configurations are those for which you cannot improve one objective without sacrificing the other.

## File Structure

-   `vehicle_performance.py`: The main executable script to run the entire analysis.
-   `models.py`: Contains the Python classes for all UAV components and the overall vehicle configuration.
-   `routines.py`: Contains helper functions for parsing data from Excel files and the Pareto optimization algorithm.
-   `Propellers.xlsx`, `Batteries.xlsx`, `Electronic-Speed-Controllers.xlsx`: The Excel files containing the component databases.
-   `Propulsion-Systems/`: A directory containing specific motor performance data, organized by brand.
-   `Vehicle-Performance_Brand:[...].pdf`: An example of the output plot generated by the script.

## Requirements

To run this project, you will need:
-   Python 3.x
-   `pandas` library
-   `matplotlib` library

You can install the required libraries using pip:
```sh
pip install pandas matplotlib
```

## Usage

1.  Ensure all required libraries are installed.
2.  Populate the `.xlsx` data files and the `Propulsion-Systems/` directory with your component data, following the existing format.
3.  Run the main script from your terminal:
    ```sh
    python vehicle_performance.py
    ```
4.  The script will print its progress to the console. Upon completion, it will display a plot and save it as a PDF file (e.g., `Vehicle-Performance_Brand:KDE_Max-cost:5500.pdf`). It will also print the detailed specifications of the configurations that lie on the Pareto frontier to the console.
