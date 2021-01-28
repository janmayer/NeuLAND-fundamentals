import os
import sys
import subprocess
import ROOT


def digitization_impl(distance, doubleplane, energy, neutron, physics):
    inpfile = f"output/{distance}m_{doubleplane}dp_{energy}AMeV_{neutron}n_{physics}.simu.root"
    parfile = f"output/{distance}m_{doubleplane}dp_{energy}AMeV_{neutron}n_{physics}.para.root"
    outfile = f"output/{distance}m_{doubleplane}dp_{energy}AMeV_{neutron}n_{physics}.digi.root"

    if not os.path.isfile(inpfile):
        print(f"Input {inpfile} does not exist")
        return

    if os.path.isfile(outfile):
        os.remove(outfile)

    ROOT.ROOT.EnableThreadSafety()
    ROOT.FairLogger.GetLogger().SetLogVerbosityLevel("LOW")
    ROOT.FairLogger.GetLogger().SetLogScreenLevel("ERROR")

    run = ROOT.FairRunAna()
    run.SetSource(ROOT.FairFileSource(inpfile))
    run.SetSink(ROOT.FairRootFileSink(outfile))

    # Connect Runtime Database
    rtdb = run.GetRuntimeDb()
    pario = ROOT.FairParRootFileIo(False)
    pario.open(parfile)
    rtdb.setFirstInput(pario)

    # Digitize data to hit level and create respective histograms
    run.AddTask(ROOT.R3BNeulandDigitizer())

    # Build clusters and create respective histograms
    run.AddTask(ROOT.R3BNeulandClusterFinder())

    # Find the actual primary interaction points and their clusters
    run.AddTask(ROOT.R3BNeulandPrimaryInteractionFinder())
    run.AddTask(ROOT.R3BNeulandPrimaryClusterFinder())

    # Create spectra
    run.AddTask(ROOT.R3BNeulandMCMon())
    run.AddTask(ROOT.R3BNeulandHitMon())
    run.AddTask(ROOT.R3BNeulandHitMon("NeulandPrimaryHits", "NeulandPrimaryHitsMon"))
    run.AddTask(ROOT.R3BNeulandClusterMon())
    run.AddTask(ROOT.R3BNeulandClusterMon("NeulandPrimaryClusters", "NeulandPrimaryClusterMon"))

    run.Init()
    run.Run(0, 0)


# Ugly hack, as FairRun (FairRunSim, FairRunAna) has some undeleteable, not-quite-singleton behavior.
# As a result, the same process can't be reused after the first run.
# Here, create a fully standalone process that is fully destroyed afterwards.
# TODO: Once/If this is fixed, remove this and rename the impl function
def digitization(distance, doubleplane, energy, neutron, physics):
    logfile = f"output/{distance}m_{doubleplane}dp_{energy}AMeV_{neutron}n_{physics}.digi.log"
    d = [
        "python",
        "digitization.py",
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
    digitization_impl(distance, doubleplane, energy, neutron, physics)
