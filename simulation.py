import os
import sys
import subprocess
import ROOT


def simulation_impl(distance, doubleplane, energy, neutron, physics, overwrite):
    outfile = f"output/{distance}m_{doubleplane}dp_{energy}AMeV_{neutron}n_{physics}.simu.root"
    parfile = f"output/{distance}m_{doubleplane}dp_{energy}AMeV_{neutron}n_{physics}.para.root"

    if os.path.isfile(outfile):
        if overwrite:
            os.remove(outfile)
            os.remove(parfile)
        else:
            print(f"Output {outfile} exists and overwriting is disabled")
            return

    ROOT.ROOT.EnableThreadSafety()
    ROOT.FairLogger.GetLogger().SetLogVerbosityLevel("LOW")
    ROOT.FairLogger.GetLogger().SetLogScreenLevel("ERROR")

    vmcworkdir = os.environ["VMCWORKDIR"]
    os.environ["GEOMPATH"] = vmcworkdir + "/geometry"
    os.environ["CONFIG_DIR"] = vmcworkdir + "/gconfig"
    os.environ["PHYSICSLIST"] = f"QGSP_{physics.upper()}_HP"

    # Initialize Simulation
    run = ROOT.FairRunSim()
    run.SetName("TGeant4")
    run.SetStoreTraj(False)
    run.SetMaterials("media_r3b.geo")

    # Output
    run.SetSink(ROOT.FairRootFileSink(outfile))

    if neutron > 1:
        print(f"NYI")
        return

    # Primary Generator
    generator = ROOT.FairPrimaryGenerator()
    boxGen = ROOT.FairBoxGenerator(2112)
    boxGen.SetThetaRange(0.0, 2.0)
    boxGen.SetPhiRange(0.0, 360.0)
    boxGen.SetEkinRange(energy / 1000.0, energy / 1000.0)
    boxGen.SetXYZ(0.0, 0.0, 0.0)
    generator.AddGenerator(boxGen)
    run.SetGenerator(generator)

    # Geometry
    cave = ROOT.R3BCave("Cave")
    cave.SetGeometryFileName("r3b_cave_vacuum.geo")
    run.AddModule(cave)

    run.AddModule(ROOT.R3BNeutronWindowAndSomeAir(700, distance * 100))

    neuland_position = ROOT.TGeoTranslation(0.0, 0.0, distance * 100 + doubleplane * 10.0 / 2.0)
    neuland = ROOT.R3BNeuland(doubleplane, neuland_position)
    run.AddModule(neuland)

    # Prepare to run
    run.Init()
    ROOT.TVirtualMC.GetMC().SetRandom(ROOT.TRandom3(1337))
    ROOT.TVirtualMC.GetMC().SetMaxNStep(100000)

    # Runtime Database
    rtdb = run.GetRuntimeDb()
    parout = ROOT.FairParRootFileIo(True)
    parout.open(parfile)
    rtdb.setOutput(parout)
    rtdb.saveOutput()

    # Run
    run.Run(100000)


# Ugly hack, as FairRun (FairRunSim, FairRunAna) has some undeleteable, not-quite-singleton behavior.
# As a result, the same process can't be reused after the first run.
# Here, create a fully standalone process that is fully destroyed afterwards.
# TODO: Once/If this is fixed, remove this and rename the impl function
def simulation(distance, doubleplane, energy, neutron, physics):
    logfile = f"output/{distance}m_{doubleplane}dp_{energy}AMeV_{neutron}n_{physics}.simu.log"
    d = [
        "python",
        "simulation.py",
        str(distance),
        str(doubleplane),
        str(energy),
        str(neutron),
        str(physics),
    ]
    with open(logfile, "w") as log:
        subprocess.run(d, stdout=log, stderr=log)


if __name__ == "__main__":
    distance = int(sys.argv[1])
    doubleplane = int(sys.argv[2])
    energy = int(sys.argv[3])
    neutron = int(sys.argv[4])
    physics = sys.argv[5]
    simulation_impl(distance, doubleplane, energy, neutron, physics, overwrite=False)
