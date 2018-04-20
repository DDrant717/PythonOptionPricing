'''
@author: Dalton Dranitsaris
@date: 2018-04-09
@summary: Defines all relevant models to run binomial pricing models for BU423 Assignment 2 Question 2
'''

from math import exp, sqrt
from abc import ABC, abstractmethod
from enum import Enum

# Abstract Classes ---------------------------------------------------------------
class Derivative(ABC):
	class OptionClass(Enum):
		EUROPEAN = 'European'
		AMERICAN = 'American'

	@abstractmethod
	def __init__(self, underlying, optionClass, term):
		self.underlying = underlying
		self.optionClass = optionClass
		self.term = term

	@abstractmethod
	def payoff(self, underlyingLevel):
		pass

class Vanilla(Derivative):
	# Parameters:
	# 	strikePrice: float
	# 	contracts: int - number of contracts purchased
	# 	costPerContract: float - price of a contract at purchase
	# 	long: boolean - True = long, False = short
	# 	unitsPerContract: int - default 100
	# 	
	@abstractmethod
	def __init__(self, underlying, optionClass, term, strikePrice, isLong, contracts=0, costPerContract=0, unitsPerContract=100):
		super().__init__(underlying, optionClass, term)
		self.strikePrice = strikePrice
		self.isLong = isLong
		self.contracts = contracts
		self.costPerContract = costPerContract
		self.unitsPerContract = unitsPerContract
# --------------------------------------------------------------------------------
class Put(Vanilla):
	underlying = None
	def __init__(self, underlying, optionClass, term, strikePrice, isLong, contracts=0, costPerContract=0, unitsPerContract=100):
		super().__init__(underlying, optionClass, term, strikePrice, isLong, contracts, costPerContract, unitsPerContract)

	# Calculates the payoff for a given level of the underlying asset (per unit)
	def payoff(self, underlyingLevel):
		putPayoff = max((self.strikePrice - underlyingLevel), 0)
		return putPayoff if self.isLong else -putPayoff

class Call(Vanilla):
	def __init__(self, underlying, optionClass, term, strikePrice, isLong, contracts=0, costPerContract=0, unitsPerContract=100):
		super().__init__(underlying, optionClass, strikePrice, isLong, contracts, costPerContract, unitsPerContract)

	# Calculates the payoff for a given level of the underlying asset
	def payoff(self, underlyingLevel):
		callPayoff = max((underlyingLevel - self.strikePrice), 0)
		return callPayoff if self.isLong else -callPayoff

class Underlying():	
	# Parameters:
	# 	startLevel: float - decimal value of the underlying (i.e. 11650 points, $1096.62/oz)
	#	volatility: float - decimal repr of annual volatility rate (i.e. 25% = 0.25)
	#	dividendYield: float - decimal repr of dividend yield, continuously compounded (i.e. 5% = 0.05)
	def __init__(self, startLevel, volatility, dividendYield):
		self.startLevel = startLevel
		self.volatility = volatility
		self.dividendYield = dividendYield

	def performanceInPercentage(self, currentLevel):
		return ((currentLevel - self.startLevel) / self.startLevel)


class NoteBarrierBooster(Derivative):
	# Typically a Barrier Boosted Return note will have a return of 0 at the Barrier Level,
	# as well as a Boost Level of 0 (i.e. where the boosted return begins).
	# Participation Level is usually == Boosted Return, Participation Rates vary but this 
	# assignment assumes 100%
	# All returns should be expressed as percentages in decimal form (i.e. 35% = 0.35)
	def __init__(self, underlying, optionClass, term, barrierLevel, boostedReturn, barrierReturn=0, \
		boostLevel = 0, participationLevel=None, participationRate=1.00):
		super().__init__(underlying, optionClass, term)
		self.barrierLevel = barrierLevel
		self.barrierReturn = barrierReturn
		self.boostLevel = boostLevel
		self.boostedReturn = boostedReturn
		self.participationLevel = self.boostedReturn if participationLevel == None else participationLevel
		self.participationRate = participationRate

	# Calculates the payoff for a given level of the underlying asset (in %age return)
	def payoff(self, underlyingLevel):
		underlyingReturn = self.underlying.performanceInPercentage(underlyingLevel)
		# Decided to make this less than (and not equal to) as this is what TD Structured Notes
		# outlines in their Investor Summary
		if underlyingReturn < self.barrierLevel:
			percReturn = underlyingReturn
		elif underlyingReturn < self.boostLevel:
			percReturn = self.barrierReturn
		elif underlyingReturn < self.participationLevel:
			percReturn = self.boostedReturn
		else:
			excessReturn = underlyingReturn - self.participationLevel
			percReturn = self.boostedReturn + (excessReturn*self.participationRate)
		return percReturn

	def __repr__(self):
		return "Barrier={}%:Booster={}%:Participation={}%" \
			.format(self.barrierLevel*100, self.boostedReturn*100, self.participationRate*100)

# This class represents the Binomial Tree Pricing model we are using.
# Derivative passed in (inheriting from abstract derivative) provides the function 'payoff'
# which is used to calculate leaf node values
class BinomialTreePricer():
	# Parameters:
	# 	timeStep: float - time step in years (i.e. 1 month = (1/12))
	# 	numSteps: int - number of time steps left until maturity/expiration
	# 	riskFreeRate: float - decimal repr of the rate, continuously compounded (i.e. 5.25% = 0.0525)
	# 	derivative: Derivative - an object of class inheriting Derivative
	# 	underlying: Underlying - with startLevel, volatility, dividendYield
	# 	
	def __init__(self, timeStep, numSteps, riskFreeRate, derivative):
		self.timeStep = timeStep
		self.numSteps = numSteps
		self.riskFreeRate = riskFreeRate
		self.derivative = derivative
		self.u = exp(self.derivative.underlying.volatility*sqrt(self.timeStep))
		self.d = 1/self.u
		self.p = (exp(self.riskFreeRate - self.derivative.underlying.dividendYield) - self.d) / (self.u - self.d)
		self.treeCache = {}

	# DO NOT USE:
	# Parameters:
	# 	underlyingLevel: float - 
	# 	k: int - determines the number of timesteps that will be taken. Default = 0 (root node)
	# 	Between underlyingLevel and k, we can simulate the pricing from any node in the tree.
	# 	We would simply pass the underlyingLevel at that node and set k = node step
	# 
	# This function was the first (naive) iteration of the binomial pricing recursive model.
	# Does not take advantage of the fact that many nodes will be accessed multiple times, and can
	# therefore be stored in cache
	# def priceDerivative (self, underlyingLevel: float, step: int = 0) -> float:
	# 	if step >= self.numSteps:
	# 		leafPayoff = self.derivative.payoff(underlyingLevel)
	# 		print ((" "*step) + "Leaf:Level={}, Payoff={}".format(underlyingLevel, leafPayoff))
	# 		return leafPayoff
	# 	else:
	# 		PVFA = exp(-self.riskFreeRate*self.timeStep)
	# 		upLevel = underlyingLevel*self.u
	# 		downLevel = underlyingLevel*self.d

	# 		print((" "*step) + "Children:")
	# 		price = PVFA*(self.p*self.priceDerivative(upLevel, step + 1) + (1 - self.p)*(self.priceDerivative(downLevel, step + 1)))
	# 		print((" "*step) + "Level {} Price: {}".format(step, price)) 
	# 		if self.derivative.optionClass == Derivative.OptionClass.AMERICAN:
	# 			payoff = self.derivative.payoff(underlyingLevel)
	# 			print((" "*step) + "Payoff: {}, Early Exercise Optimal: {}".format(payoff, payoff>price))
	# 			return max(price, payoff)

	# 		# else OptionClass.EUROPEAN
	# 		return price


	# Parameters:
	# 	numUs: int - the number of upward movements at this step (so number downward = self.numSteps - numUs) 
	# 	k: int - determines the number of timesteps that will be taken. Default = 0 (root node)
	# 	Between underlyingLevel and k, we can simulate the pricing from any node in the tree.
	# 	We would simply pass the underlyingLevel at that node and set k = node step
	# 
	# 	Optimized to store node values in cache to avoid full binary tree recursion.
	def priceDerivativeOptimized (self, numUs: int = 0, step: int = 0) -> float:
		# Attempt to get the price for this node from the cache
		price = self.getFromCache(numUs, step)
		if price is None:
			if step >= self.numSteps:
				level = self.underlyingLevelAfterMovements(numUs, step)
				price = self.derivative.payoff(level)

				# print (("  "*step) + "Adding to cache: " + str(numUs) + ":" + str(step) + " = " + str(price))
				self.addToCache(numUs, step, price)
			else:
				level = self.underlyingLevelAfterMovements(numUs, step)
				PVFA = exp(-self.riskFreeRate*self.timeStep)
				price = PVFA*(self.p*self.priceDerivativeOptimized(numUs + 1, step + 1) \
					+ (1 - self.p)*(self.priceDerivativeOptimized(numUs, step + 1))) 
				if self.derivative.optionClass == Derivative.OptionClass.AMERICAN:
					payoff = self.derivative.payoff(level)
					price = max(price, payoff)
				# print (("  "*step) + "Adding to cache: " + str(numUs) + ":" + str(step) + " = " + str(price))
				self.addToCache(numUs, step, price)
		else:
			# print(("  "*step) + "Retrieving from cache: {}:{} = {}".format(numUs, step, price)) 
			pass
		return price

	def underlyingLevelAfterMovements (self, numUs, step):
		initialLevel = self.derivative.underlying.startLevel
		numDs = step - numUs
		growthFactor = self.u**(numUs - numDs) # numUs - numDs == 2*numUs - step
		return initialLevel*growthFactor

	def addToCache(self, numUs, step, price):
		self.treeCache[str(numUs) + ":" + str(step)] = price

	def getFromCache(self, numUs, step):
		return self.treeCache.get(str(numUs) + ":" + str(step))


# This class represents the Binomial Tree Pricing model we are using for Question 3.
# Derivative passed in (inheriting from abstract derivative) provides the function 'payoff'
# which is used to calculate leaf node values
class BinomialTreeQ3Pricer():
	# Parameters:
	# 	timeStep: float - time step in years (i.e. 1 month = (1/12))
	# 	numSteps: int - number of time steps left until maturity/expiration
	# 	riskFreeRate: float - decimal repr of the rate, continuously compounded (i.e. 5.25% = 0.0525)
	# 	derivative: Derivative - an object of class inheriting Derivative
	# 	underlying: Underlying - with startLevel, volatility, dividendYield
	# 	
	def __init__(self, timeStep, numSteps, riskFreeRate, derivative, knockout):
		self.timeStep = timeStep
		self.numSteps = numSteps
		self.riskFreeRate = riskFreeRate
		self.derivative = derivative
		self.knockout = knockout
		self.u = exp(self.derivative.underlying.volatility*sqrt(self.timeStep))
		self.d = 1/self.u
		self.p = (exp((self.riskFreeRate - self.derivative.underlying.dividendYield)*self.timeStep) - self.d) / (self.u - self.d)
		self.treeCache = {}

	# Parameters:
	# 	numUs: int - the number of upward movements at this step (so number downward = self.numSteps - numUs) 
	# 	k: int - determines the number of timesteps that will be taken. Default = 0 (root node)
	# 	Between underlyingLevel and k, we can simulate the pricing from any node in the tree.
	# 	We would simply pass the underlyingLevel at that node and set k = node step
	# 
	# 	Optimized to store node values in cache to avoid full binary tree recursion.
	def priceDerivativeOptimized (self, numUs: int = 0, step: int = 0) -> float:
		# Check if we are in the first 3 years
		if step*self.timeStep <= 3:
			# Check if the index has dropped more than -20%
			underlyingPerformance = self.derivative.underlying.performanceInPercentage(self.underlyingLevelAfterMovements(numUs, step))
			if underlyingPerformance < self.knockout:
				return 0

		# Attempt to get the price for this node from the cache
		price = self.getFromCache(numUs, step)
		if price is None:
			if step >= self.numSteps:
				level = self.underlyingLevelAfterMovements(numUs, step)
				price = self.derivative.payoff(level)

				# print (("  "*step) + "Adding to cache: " + str(numUs) + ":" + str(step) + " = " + str(price))
				self.addToCache(numUs, step, price)
			else:
				level = self.underlyingLevelAfterMovements(numUs, step)
				PVFA = exp(-self.riskFreeRate*self.timeStep)
				price = PVFA*(self.p*self.priceDerivativeOptimized(numUs + 1, step + 1) + (1 - self.p)*(self.priceDerivativeOptimized(numUs, step + 1))) 
				if self.derivative.optionClass == Derivative.OptionClass.AMERICAN:
					payoff = self.derivative.payoff(level)
					price = max(price, payoff)
				# print (("  "*step) + "Adding to cache: " + str(numUs) + ":" + str(step) + " = " + str(price))
				self.addToCache(numUs, step, price)
		else:
			# print(("  "*step) + "Retrieving from cache: {}:{} = {}".format(numUs, step, price)) 
			pass
		return price

	def underlyingLevelAfterMovements (self, numUs, step):
		initialLevel = self.derivative.underlying.startLevel
		numDs = step - numUs
		growthFactor = self.u**(numUs - numDs) # numUs - numDs == 2*numUs - step
		return initialLevel*growthFactor

	def addToCache(self, numUs, step, price):
		self.treeCache[str(numUs) + ":" + str(step)] = price

	def getFromCache(self, numUs, step):
		return self.treeCache.get(str(numUs) + ":" + str(step))