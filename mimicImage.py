#!/usr/bin/python3
import sys
import math
import copy
from PIL import Image, ImageDraw
from random import randrange, random

'''
Class with points and color attributes for a triangle
 - points is an array that holds 3 tuples.
 	- each tuple holds 2 values i.e (x,y)
 - holds a tuple of with 4 values i.e (r,g,b,a)
'''
class triangle():
	def __init__(self, points, color):
		if len(points) == 3 and self.isValidColor(color): # Checking if provided parameters are valid
			self.points = points
			self.color = color
	'''
	Checks if color is valid
	'''
	def isValidColor(self, color):
		if len(color) == 4: # (r,g,b,a)
			for x in color:
				if x < 0 or x > 255: # value must be between 0 and 255
					return False
			return True
		return False

'''
Class that hold data for each generated image
 - width: holds image width
 - height: holds image height
 - triangles: array of triangle objects
 - outImg: PIL Image object of the instance 
'''
class image():
	def __init__(self, width, height):
		self.width = width
		self.height = height

	'''
	Generates triangles with random points and colors
	 - numTriangles: number of triangles to generate
	'''
	def generateTriangles(self, numTriangles):
		self.triangles = []
		for tri in range(0, numTriangles):
			points = []
			for _ in range(0, 3): # Generating 3 points for a triangle
				# Generating random point with in the image boundary
				x = randrange(self.width+1)
				y = randrange(self.height+1)

				# Saving generated point
				points.append((x,y))

			# Generating random color
			r = randrange(256)
			g = randrange(256)
			b = randrange(256)
			a = randrange(256)

			# Saving generated triangle
			temp = triangle(points, (r,g,b,a))
			self.triangles.append(temp)

	'''
	Generates PIL Image object of the instance
	 - background: specifies original image background
	 - Each triangle is drawn on a separate image and then placed on the original
	'''
	def generateOutputImage(self, background=(0,0,0)):
		self.outImg = Image.new('RGB', (self.width, self.height), background)
		triangle = Image.new('RGBA', (self.width, self.height))
		drawTri = ImageDraw.Draw(triangle)
		for tri in self.triangles: # Draw triangles on outImg
			drawTri.polygon(tri.points, fill=tri.color, outline=tri.color)
			self.outImg.paste(triangle, mask=triangle)

	'''
	Saves the output image to a file
	 - PIL Image functions are used to do this therefore,
	   generateOutputImage() MUST run before this
	'''
	def saveImg(self, path="out.png"):
		if self.outImg:
			self.outImg.save(path)
		else:
			print("ERROR: Image does not exist")
			print("Generate the image by calling generateOutputImage()")

'''
Returns a difference between 2 images using the L2-Norm approach
 - This difference is evaluated by calculating the difference in each pixel of the images
 - Next, the difference is squared and added on to the previous squared differences
 - The squareroot of the sum of squared differences is returned
'''
def fitness(img1, img2):
	width = img1.width
	height  = img1.height
	l2Norm = 0
	for x in range(0, width):
		for y in range(0, height):
			actual = img1.getpixel((x,y))
			generated = img2.getpixel((x,y))
			for i in range(0, 3):
				difference = abs(actual[i] - generated[i])
				l2Norm += difference * difference
	return math.sqrt(l2Norm)

'''
Creates a population of generated images
 - inputImage: PIL Image instance of the input image
 - populationSize: number of images to generate
 - numTriangles: number of triangles in each generated image
Returns a list of all the generated images
'''
def createPopulation(inputImage, populationSize, numTriangles):
	width = inputImage.width
	height  = inputImage.height
	population = []
	for _ in range(0, populationSize):
		temp = image(width, height)
		temp.generateTriangles(numTriangles)
		temp.generateOutputImage()
		temp.fitnessValue = fitness(inputImage, temp.outImg)
		population.append(temp)
	return population

'''
Performs a genetic operation between two given parents
 - inputImage: PIL Image instance of the input image
 - img1: first parent
 - img2: second parent
 - mutationRate: rate at which each triangle of the children should be mutated
Creates 2 children from different halves of the parents
Return the 2 children created
'''
def geneticOperation(inputImage, img1, img2, mutationRate):
	pivot = int(len(img1.triangles)/2)
	
	# Generate child 1
	child1 = image(img1.width, img1.height)
	child1.triangles = img1.triangles[0:pivot] + img2.triangles[pivot:]
	child1 = mutation(child1, mutationRate)
	child1.generateOutputImage()
	child1.fitnessValue = fitness(inputImage, child1.outImg)

	# Generate child 2
	child2 = image(img1.width, img1.height)
	child2.triangles = img2.triangles[0:pivot] + img1.triangles[pivot:]
	child2 = mutation(child2, mutationRate)
	child2.generateOutputImage()
	child2.fitnessValue = fitness(inputImage, child2.outImg)
	return child1, child2

'''
Performs mutation in a given image
 - image: image to perform the mutation on
 - mutationRate: rate of mutation
Each mutation happens on each triangle if mutateVal <= mutationRate
There are 3 types of possible mutations:
 - colorMutation: 40% chance
 - pointsMutation: 40% chance
 - color and points mutation: 20% chance
Returns mutated image
'''
def mutation(image, mutationRate):
	img = copy.deepcopy(image)
	for tri in img.triangles: # iterate through each triangle
		mutateVal = random()
		if mutateVal <= mutationRate:
			# Determine mutation type
			selectMutation = randrange(51)

			color = randrange(4)
			colorVal = randrange(256)

			point = randrange(3)
			x = randrange(img.width+1)
			y = randrange(img.height+1)

			if selectMutation < 20:
				# mutate color
				temp = list(tri.color)
				temp[color] = colorVal
				tri.color = tuple(temp)
			elif selectMutation < 40:
				# mutate points
				tri.points[point] = (x,y)
			else:
				# mutate color and points
				temp = list(tri.color)
				temp[color] = colorVal
				tri.color = tuple(temp)

				tri.points[point] = (x,y)
	return img

'''
Selects two parents to perform genetic operation on
Images with the 2 lowest fitness values are selected
Weakest two images (highest fitnessValue) are removed from the population
 - inputImage: PIL Image instance of the input image
 - population: number of images in the sample space
 - mutationRate: rate of mutating triangles in children
 - crossoverRate: rate of genetic operations to be performed in the given population
'''
def selection(inputImage, population, mutationRate, crossoverRate):
	numCouples = int(crossoverRate * len(population))
	for _ in range(0, numCouples):
		# Get best two from current population
		parent1 = parent2 = population[0]
		for i in population:
			if i.fitnessValue < parent1.fitnessValue:
				parent1 = i
			elif i.fitnessValue < parent2.fitnessValue and i is not parent1:
				parent2 = i

		# Perform genetic operation
		child1, child2 = geneticOperation(inputImage, parent1, parent2, mutationRate)
		population.append(child1)
		population.append(child2)

		# Remove worst two from population
		for _ in range(0, 2):
			largestValue = population[0]
			for i in population:
				if i.fitnessValue > largestValue.fitnessValue:
					largestValue = i
			population.remove(largestValue)
	return population



def main():
	if len(sys.argv) != 7:
		print("Usage: imagePath numTriangles populationSize crossoverRate mutationRate generations")
		sys.exit()

	# Reading arguments
	imagePath = sys.argv[1]
	numTriangles = int(sys.argv[2])
	populationSize = int(sys.argv[3])
	crossoverRate = float(sys.argv[4])
	mutationRate = float(sys.argv[5])
	generations = int(sys.argv[6])

	# Creating PIL Image Instance of the input image
	inputImage = Image.open(imagePath)

	# Creating population
	population = createPopulation(inputImage, populationSize, numTriangles)

	saveInterval = generations//3

	# running algorithm for given number of generations
	for gen in range(0, generations):
		print("Generation: "+str(gen)) # Current generation
		population = selection(inputImage, population, mutationRate, crossoverRate)

		# Saving images in intervals
		if gen % saveInterval == 0 or gen == generations-1:
			# Finding best image from the population
			bestImage = population[0]
			for i in population:
				if i.fitnessValue < bestImage.fitnessValue:
					bestImage = i
			# Saving best image to a file
			bestImage.saveImg("gen-"+str(gen)+"_"+imagePath)
	
if __name__ == "__main__":
	main()