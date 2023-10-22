from Genetic import calculator
from Greedy import greedycalc
from Config import loader, config

if __name__ == "__main__":
    gc = greedycalc.greedy_calculator(loader=loader, config=config)
    rs = gc.main()
    if rs > 1.0 and rs != 9999:
        gc2 = calculator.genetic_calculator(loader=loader, config=config)
        gc2.main()