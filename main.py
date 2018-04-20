'''
@author: Dalton Dranitsaris
@date: 2018-04-09
@summary: Runs simulation cases for BU423 Assignment 2 Question 2
'''


from models import Underlying, Derivative, Put, Call, \
					NoteBarrierBooster, BinomialTreePricer, BinomialTreeQ3Pricer
import datetime

def startScenarios():
	scenarios = {}

	# CALL TEST -----------------------------------------------------------------
	# u = Underlying(20, 0, 0)
	# c = (u, Derivative.OptionClass.AMERICAN, 2, 52, True)
	# timeStep = 0.25
	# e = BinomialTreePricer(timeStep, c.term/timeStep, 0.12, c)
	# price = e.priceDerivative(c.underlying.startLevel)
	# print ("Call option price: {}", price)
	# END TEST ------------------------------------------------------------------

	# PUT TEST ------------------------------------------------------------------
	# u = Underlying(50, 0.3, 0)
	# p = Put(u, Derivative.OptionClass.AMERICAN, 2, 52, True)
	# timeStep = 1
	# e = BinomialTreePricer(timeStep, p.term//timeStep, 0.05, p)
	# # price2 = e.priceDerivative(p.underlying.startLevel)
	# # print ("Put option price: {}", price2)
	# price = e.priceDerivativeOptimized()
	# print ("Put option price: {}", price)
	# END TEST ------------------------------------------------------------------

	sptsx = Underlying(15400, 0.25, 0.012)
	term = 6
	scenarios["S1"] = NoteBarrierBooster(sptsx, Derivative.OptionClass.EUROPEAN, term, -0.3, 0.6)
	scenarios["S2"] = NoteBarrierBooster(sptsx, Derivative.OptionClass.EUROPEAN, term, -0.2, 0.5)
	scenarios["S3"] = NoteBarrierBooster(sptsx, Derivative.OptionClass.EUROPEAN, term, -0.1, 0.4)
	scenarios["S4"] = NoteBarrierBooster(sptsx, Derivative.OptionClass.EUROPEAN, term, -0.4, 0.7)
	scenarios["S5"] = NoteBarrierBooster(sptsx, Derivative.OptionClass.EUROPEAN, term, -0.5, 0.8)
	print("Successfully Created Notes")

	# NOTE TEST ------------------------------------------------------------------
	# note = scenarios["S1"]
	# print (note)
	# timeStep = 1/6
	# b = BinomialTreePricer(timeStep, note.term//timeStep, 0.035, note)
	# price = b.priceDerivativeOptimized()
	# print ("Price for: {}\n ${}".format(note, price))
	# END TEST ------------------------------------------------------------------

	outputFile = open("Q2Results.txt", mode="a")
	outputFile.write("Running at: {}\n".format(datetime.datetime.now()))
	outputFile.write("Volatility: {}\n".format(sptsx.volatility))
	print("Running at: {}\n".format(datetime.datetime.now()))
	print("Volatility: {}\n".format(sptsx.volatility))
	for key, note in scenarios.items():
		timeStep = 1
		b = BinomialTreeQ3Pricer(timeStep, note.term//timeStep, 0.035, note, -0.2)
		price = b.priceDerivativeOptimized()
		outputFile.write ("Price for {}: {}\n ${:.5} per $1\n".format(key, note, price))
		print("Price for {}: {}\n ${:.5} per $1\n".format(key, note, price))
		
	outputFile.close()



if __name__ == "__main__":
	print("Starting up")
	startScenarios()