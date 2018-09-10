import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

def getUserPath(user):
	return os.path.join(os.getcwd(), user)

def getExpiryPath(userPath, stock, earningsDate, expiryDate):
	return os.path.join(userPath, stock, earningsDate, expiryDate)

def getOptionPath(expiryPath, optionFileName):
	return os.path.join(expiryPath, optionFileName)

def getAllStocksFolders(userPath):
	return os.listdir(userPath)

def getAllEarningsDatesFolders(stockPath):
	return os.listdir(stockPath)

def getAllExpiryDatesFolders(earningsPath):
	return os.listdir(earningsPath)

def getAllOptionsFiles(expiryPath):
	return os.listdir(expiryPath)

def getOption(optionPath):
	return pd.read_csv(optionPath)