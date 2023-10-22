from Genetic import calculator
from Greedy import greedycalc
from Config import loader, config

if __name__ == "__main__":
    gc = greedycalc.GreedyCalculator(loader=loader, config=config)
    rs = gc.optimize_build()
    if rs > 1.0 and rs != 9999:
        gc2 = calculator.GeneticCalculator(loader=loader, config=config)
        gc2.optimize_build()