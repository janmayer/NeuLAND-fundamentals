import joblib
from digitization import digitization


distances = [15, 35]
doubleplanes = [12, 30]
energies = [200, 600, 1000]
neutrons = [1]
physicss = ["bert", "bic", "inclxx"]


# Parallel simulations
joblib.Parallel(n_jobs=-1, backend="loky", verbose=11)(
    joblib.delayed(digitization)(
        distance=distance,
        doubleplane=doubleplane,
        energy=energy,
        neutron=neutron,
        physics=physics,
    )
    for distance in distances
    for energy in energies
    for doubleplane in doubleplanes
    for neutron in neutrons
    for physics in physicss
)
